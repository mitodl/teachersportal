"""
Tests for checkout API
"""
# pylint: disable=no-self-use,invalid-name
from __future__ import unicode_literals
import json

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from mock import patch
from oscar.apps.catalogue.models import Product
from oscar.apps.partner.models import Partner, StockRecord
from stripe import Charge

from portal.factories import OrderFactory, OrderLineFactory, ProductFactory
from portal.models import Order, OrderLine, UserInfo
from portal.views.base import ProductTests
from portal.util import (
    calculate_cart_subtotal, calculate_cart_item_total, make_upc, MODULE_PRODUCT_TYPE
)

from .checkout_api import CheckoutView


class CheckoutAPITests(ProductTests):
    """
    Tests for checkout
    """
    def setUp(self):
        super(CheckoutAPITests, self).setUp()
        partner = Partner.objects.first()
        self.price = 123
        StockRecord.objects.create(
            product=self.child,
            partner=partner,
            partner_sku=self.child.upc,
            price_currency="$",
            price_excl_tax=self.price,
        )

        credentials = {"username": "auser", "password": "apass"}
        UserInfo.objects.create(
            user=User.objects.create_user(**credentials),
            full_name='Test User')
        self.client.login(**credentials)

    def test_empty_cart(self):
        """
        Assert that an empty cart causes a 400.
        """
        resp = self.client.post(
            reverse('checkout'),
            content_type='application/json',
            data=json.dumps({
                "cart": [],
                "token": "token",
                "total": 0
            })
        )
        assert resp.status_code == 400, resp.content.decode('utf-8')
        assert "Cannot checkout an empty cart" in resp.content.decode('utf-8')

    def test_missing_keys(self):
        """
        Assert that missing keys cause a 400.
        """
        for key in ('cart', 'token', 'total'):
            payload = {
                "cart": [],
                "token": "",
                "total": 0
            }
            del payload[key]
            resp = self.client.post(
                reverse('checkout'),
                content_type='application/json',
                data=json.dumps(payload)
            )
            assert resp.status_code == 400, resp.content.decode('utf-8')
            assert "Missing key {}".format(key) in resp.content.decode('utf-8')

    @patch('portal.views.checkout_api.ccxcon_request')
    def test_cart_without_price(self, mock_ccxcon):
        """
        Assert that if the total of a cart is zero, checkout still works.
        """
        mock_ccxcon.return_value.post.return_value.status_code = 200
        stockrecord = StockRecord.objects.first()
        stockrecord.price_excl_tax = 0
        stockrecord.save()

        resp = self.client.post(
            reverse('checkout'),
            content_type='application/json',
            data=json.dumps({
                "cart": [{
                    "upc": self.child.upc,
                    "seats": 5
                }],
                "token": "",
                "total": 0
            })
        )
        assert resp.status_code == 200, resp.content.decode('utf-8')
        assert mock_ccxcon.return_value.post.called

    @patch('portal.views.checkout_api.ccxcon_request')
    def test_cart_with_price(self, mock_ccxcon):
        """
        Assert that if the total of a cart is not zero, checkout works.
        """
        mock_ccxcon.return_value.post.return_value.status_code = 200
        cart_item = {
            "upc": self.child.upc,
            "seats": 5
        }
        cart = [cart_item]
        total = calculate_cart_subtotal(cart)
        # Note: autospec intentionally not used, we need an unbound method here
        with patch.object(Charge, 'create') as create_mock:
            mocked_kwargs = {}

            def _create_mock(**kwargs):
                """Side effect function to capture kwargs for assert"""
                # Note: not just assigning to mocked_kwargs because of scope differences.
                for key, value in kwargs.items():
                    mocked_kwargs[key] = value
            create_mock.side_effect = _create_mock

            resp = self.client.post(
                reverse('checkout'),
                content_type='application/json',
                data=json.dumps({
                    "cart": cart,
                    "token": "token",
                    "total": float(total)
                })
            )
            assert resp.status_code == 200, resp.content.decode('utf-8')

            assert mocked_kwargs['source'] == 'token'
            assert mocked_kwargs['amount'] == int(total * 100)
            assert mocked_kwargs['currency'] == 'usd'
            assert 'order_id' in mocked_kwargs['metadata']
            assert mock_ccxcon.return_value.post.called

            order = Order.objects.get(id=mocked_kwargs['metadata']['order_id'])
            assert order.orderline_set.count() == 1
            order_line = order.orderline_set.first()
            assert calculate_cart_item_total(cart_item) == order_line.line_total

    def test_cart_with_price_not_matching_total(self):
        """
        Assert that if the total of a cart doesn't match the calculated price,
        we raise a ValidationError.
        """
        cart_item = {
            "upc": self.child.upc,
            "seats": 5
        }
        cart = [cart_item]

        resp = self.client.post(
            reverse('checkout'),
            content_type='application/json',
            data=json.dumps({
                "cart": cart,
                "token": "token",
                "total": 0
            })
        )
        assert resp.status_code == 400, resp.content.decode('utf-8')
        assert "Cart total doesn't match expected value" in resp.content.decode('utf-8')

    @patch('portal.views.checkout_api.ccxcon_request')
    def test_cart_fails_to_checkout(self, ccxcon_request):
        """
        Assert that we clean up everything if checkout failed.
        """
        cart_item = {
            "upc": self.child.upc,
            "seats": 5
        }
        cart = [cart_item]
        # Note: autospec intentionally not used, we need an unbound method here
        with patch.object(Charge, 'create') as create_mock:
            def _create_mock(**kwargs):  # pylint: disable=unused-argument
                """Side effect function to raise an exception"""
                raise Exception("test exception")
            create_mock.side_effect = _create_mock

            with self.assertRaises(Exception) as ex:
                self.client.post(
                    reverse('checkout'),
                    content_type='application/json',
                    data=json.dumps({
                        "cart": cart,
                        "token": "token",
                        "total": float(calculate_cart_subtotal(cart))
                    })
                )
            assert ex.exception.args[0] == 'test exception'

            assert Order.objects.count() == 0
            assert OrderLine.objects.count() == 0
            assert not ccxcon_request.called

    @patch('portal.views.checkout_api.ccxcon_request')
    def test_failed_api_try_all(self, requester):
        """
        If the post fails, it should try again for the second orderline.
        """
        requester.return_value.post.side_effect = AttributeError()
        order = OrderFactory.create()
        OrderLineFactory.create_batch(2, order=order)

        CheckoutView().notify_external_services(order, order.purchaser)

        assert requester.return_value.post.call_count == 2

    @patch('portal.views.checkout_api.ccxcon_request')
    def test_failed_post_makes_orders(self, requester):
        """
        If the post fails, orders are still created
        """
        start = Order.objects.count()
        start_ol = OrderLine.objects.count()
        requester.return_value.post.side_effect = AttributeError()
        cart_item = {
            "upc": self.child.upc,
            "seats": 5
        }
        cart = [cart_item]

        with patch.object(Charge, 'create'):
            self.client.post(
                reverse('checkout'),
                content_type='application/json',
                data=json.dumps({
                    "cart": cart,
                    "token": "token",
                    "total": float(calculate_cart_subtotal(cart))
                })
            )

        assert Order.objects.count() - start == 1
        assert OrderLine.objects.count() - start_ol == 1

    @patch('portal.views.checkout_api.ccxcon_request')
    def test_errors_propagate_to_response(self, requester):
        """
        If there are errors on checkout, they make it to the response.
        """
        child2 = ProductFactory.create(
            upc=make_upc(MODULE_PRODUCT_TYPE, 'abcdef2'),
            parent=self.parent,
            title='test',
            product_class=None,
            structure=Product.CHILD
        )
        StockRecord.objects.create(
            product=child2,
            partner=Partner.objects.first(),
            partner_sku=child2.upc,
            price_currency="$",
            price_excl_tax=100,
        )
        requester.return_value.post.side_effect = [
            AttributeError("Example Error"),
            AttributeError("Another Error"),
        ]
        cart = [{
            "upc": self.child.upc,
            "seats": 5
        }, {
            "upc": child2.upc,
            "seats": 4
        }]

        with patch.object(Charge, 'create'):
            resp = self.client.post(
                reverse('checkout'),
                content_type='application/json',
                data=json.dumps({
                    "cart": cart,
                    "token": "token",
                    "total": float(calculate_cart_subtotal(cart))
                })
            )

        assert "Example Error" in resp.content.decode('utf-8')
        assert "Another Error" in resp.content.decode('utf-8')

    def test_not_logged_in(self):
        """
        Assert that the user must be logged in to checkout.
        """
        self.client.logout()

        cart_item = {
            "upc": self.child.upc,
            "seats": 5
        }
        cart = [cart_item]
        resp = self.client.post(
            reverse('checkout'),
            content_type='application/json',
            data=json.dumps({
                "cart": cart,
                "token": "token"
            })
        )
        assert resp.status_code == 403
