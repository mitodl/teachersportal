"""
Tests for checkout API
"""

from __future__ import unicode_literals
import json

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from mock import patch
from oscar.apps.partner.models import Partner, StockRecord
from stripe import Charge

from portal.models import Order, OrderLine
from portal.views.base import ProductTests
from portal.util import calculate_cart_subtotal, calculate_cart_item_total


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
        User.objects.create_user(**credentials)
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
                "token": "token"
            })
        )
        assert resp.status_code == 400, resp.content
        assert "Cannot checkout an empty cart" in resp.content.decode('utf-8')

    def test_missing_keys(self):
        """
        Assert that missing keys cause a 400.
        """
        for key in ('cart', 'token'):
            payload = {
                "cart": [],
                "token": ""
            }
            del payload[key]
            resp = self.client.post(
                reverse('checkout'),
                content_type='application/json',
                data=json.dumps(payload)
            )
            assert resp.status_code == 400, resp.content
            assert "Missing key {}".format(key) in resp.content.decode('utf-8')

    def test_cart_without_price(self):
        """
        Assert that if the total of a cart is zero, checkout still works.
        """
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
                "token": ""
            })
        )
        assert resp.status_code == 200, resp.content

    def test_cart_with_price(self):
        """
        Assert that if the total of a cart is not zero, checkout works.
        """
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
                    "token": "token"
                })
            )
            assert resp.status_code == 200, resp.content

            assert mocked_kwargs['source'] == 'token'
            assert mocked_kwargs['amount'] == int(total * 100)
            assert mocked_kwargs['currency'] == 'usd'
            assert 'order_id' in mocked_kwargs['metadata']

            order = Order.objects.get(id=mocked_kwargs['metadata']['order_id'])
            assert order.orderline_set.count() == 1
            order_line = order.orderline_set.first()
            assert calculate_cart_item_total(cart_item) == order_line.line_total

    def test_cart_fails_to_checkout(self):
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
                        "token": "token"
                    })
                )
            assert ex.exception.args[0] == 'test exception'

            assert Order.objects.count() == 0
            assert OrderLine.objects.count() == 0
