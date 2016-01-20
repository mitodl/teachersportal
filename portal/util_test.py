"""
Tests for product serializer functions.
"""

from __future__ import unicode_literals
from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

from portal.exceptions import ProductException
from portal.models import Order, OrderLine
from portal.views.base import ProductTests
from portal.factories import ModuleFactory
from portal.util import (
    calculate_cart_subtotal,
    calculate_cart_item_total,
    create_order,
    get_cents,
    make_qualified_id,
    make_external_pk,
    get_product_type,
    course_as_product_json,
    module_as_product_json,
    validate_cart,
    COURSE_PRODUCT_TYPE,
    MODULE_PRODUCT_TYPE,
)


class ProductUtilTests(ProductTests):
    """
    Test for Product utility functions.
    """

    def test_product_json(self):
        """
        Test functionality of course_as_product_json and module_as_product_json
        """

        expected_module = {
            "upc": self.module.qualified_id,
            "title": self.module.title,
            "description": "",
            "external_pk": self.module.uuid,
            "product_type": MODULE_PRODUCT_TYPE,
            "price_without_tax": float(self.module.price_without_tax),
            "parent_upc": self.course.qualified_id,
            "info": None,
            "children": []
        }
        assert module_as_product_json(self.module, {}) == expected_module

        ccxcon_title = "a title"
        assert course_as_product_json(self.course, {
            self.course.qualified_id: {
                "title": ccxcon_title
            }
        }) == {
            "upc": self.course.qualified_id,
            "title": self.course.title,
            "description": self.course.description,
            "external_pk": self.course.uuid,
            "product_type": COURSE_PRODUCT_TYPE,
            "price_without_tax": None,
            "parent_upc": None,
            "info": {
                "title": ccxcon_title
            },
            "children": [expected_module]
        }

    def test_make_qualified_id(self):  # pylint: disable=no-self-use
        """Assert make_qualified_id behavior"""
        assert make_qualified_id("product_type", "external_pk") == "product_type_external_pk"

    def test_make_external_pk(self):
        """Assert make_external_pk behavior"""
        assert make_external_pk("type", "type_upc") == "upc"

        with self.assertRaises(ProductException) as ex:
            make_external_pk("type", "other_prefix_upc")
        assert ex.exception.args[0] == "Unexpected prefix found"

    def test_get_product_type(self):
        """Assert get_product_type behavior"""
        assert get_product_type(self.module.qualified_id) == MODULE_PRODUCT_TYPE
        assert get_product_type(self.course.qualified_id) == COURSE_PRODUCT_TYPE
        assert get_product_type("invalid") is None

    def test_live_availability(self):
        """Assert that live boolean affects availability for purchase"""
        assert not self.course.is_available_for_purchase
        assert not self.module.is_available_for_purchase
        self.course.live = True
        self.course.save()
        assert self.course.is_available_for_purchase
        assert self.module.is_available_for_purchase

    def test_missing_price(self):
        """Assert that a missing price means product is unavailable for purchase"""
        self.course.live = True
        self.course.save()
        self.module.price_without_tax = None
        self.module.save()

        assert not self.course.is_available_for_purchase
        assert not self.module.is_available_for_purchase

    def test_zero_price(self):
        """Assert that a $0 price means product is available for purchase"""
        self.course.live = True
        self.course.save()
        self.module.price_without_tax = 0
        self.module.save()

        assert self.course.is_available_for_purchase
        assert self.module.is_available_for_purchase

    def test_no_modules(self):
        """
        If a course has no modules, it is not available for purchase.
        """
        self.course.live = True
        self.course.save()
        self.module.delete()

        assert not self.course.is_available_for_purchase

    def test_get_cents(self):  # pylint: disable=no-self-use
        """
        Test behavior of get_cents
        """
        # 5114.15 is actually something like 5114.149999...
        dec = Decimal(5114.15)
        assert get_cents(dec) == 511415


class CheckoutValidationTests(ProductTests):
    """
    Tests for checkout validation
    """

    def setUp(self):
        super(CheckoutValidationTests, self).setUp()
        self.course.live = True
        self.course.save()

    def test_cart_with_zero_price(self):
        """
        Assert that we support carts with zero priced products
        """
        self.module.price_without_tax = 0
        self.module.save()

        assert calculate_cart_subtotal([
            {"upc": self.module.qualified_id, "seats": 10}
        ]) == 0

    def test_empty_cart_total(self):  # pylint: disable=no-self-use
        """
        Assert that an empty cart has a total of $0
        """
        assert calculate_cart_subtotal([]) == 0

    def test_cart_total(self):
        """
        Assert that the cart total is calculated correctly (seats * price)
        """
        assert calculate_cart_subtotal([
            {"upc": self.module.qualified_id, "seats": 10}
        ]) == self.module.price_without_tax * 10

    def test_empty_line_total(self):
        """
        Assert that an empty line has a total of 0
        """
        self.module.price_without_tax = 0
        self.module.save()

        assert calculate_cart_item_total({
            "upc": self.module.qualified_id,
            "seats": 10
        }) == 0

    def test_line_total(self):
        """
        Assert that a line total is the price times quantity.
        """
        assert calculate_cart_item_total({
            "upc": self.module.qualified_id,
            "seats": 10
        }) == self.module.price_without_tax * 10

    def test_validation(self):
        """
        Assert that a valid cart will pass validation.
        """
        validate_cart([
            {"upc": self.module.qualified_id, "seats": 10}
        ])

    def test_no_seats(self):
        """
        Assert that a valid cart will pass validation.
        """
        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {"upc": self.module.qualified_id, "seats": 0}
            ])
        assert ex.exception.detail[0] == "Number of seats is zero"

    def test_purchase_of_course(self):
        """
        Assert that we don't allow purchases of courses, just individual modules.
        """
        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {"upc": self.course.qualified_id, "seats": 10}
            ])
        assert ex.exception.detail[0] == "Can only purchase Modules"

    def test_unavailable_items(self):
        """
        Assert that any references to items not for sale will cause a validation error.
        """
        self.course.live = False
        self.course.save()

        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {"upc": self.module.qualified_id, "seats": 10}
            ])
        assert ex.exception.detail[0] == "One or more products are unavailable"

    def test_missing_items(self):
        """
        Assert that references to items that are missing will cause a validation error.
        """
        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {"upc": make_qualified_id(MODULE_PRODUCT_TYPE, "missing"), "seats": 10}
            ])
        assert ex.exception.detail[0] == "One or more products are unavailable"

    def test_missing_keys(self):
        """
        Assert that missing keys cause a ValidationError.
        """
        item = {"upc": self.module.qualified_id, "seats": 10}
        for key in ('upc', 'seats'):
            with self.assertRaises(ValidationError) as ex:
                item_copy = dict(item)
                del item_copy[key]
                validate_cart([item_copy])
            assert ex.exception.detail[0] == "Missing key {}".format(key)

    def test_int_seats(self):
        """
        Assert that non-int keys for number of seats are rejected.
        """
        for seats in ('6.5', 6.5, None, [], {}):
            item = {"upc": self.module.qualified_id, "seats": seats}
            with self.assertRaises(ValidationError) as ex:
                validate_cart([item])
            assert ex.exception.detail[0] == "Seats must be an integer"

    def test_duplicate_order(self):
        """
        Assert that we don't allow duplicate items in cart
        """
        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {"upc": self.module.qualified_id, "seats": 10},
                {"upc": self.module.qualified_id, "seats": 5}
            ])
        assert ex.exception.detail[0] == "Duplicate item in cart"

    def test_must_have_all_children_in_cart(self):  # pylint: disable=invalid-name
        """
        If user tries to buy a subset of a course, raise a validation error.

        Note: It's expected that this will be removed when we support buying
        modules.
        """
        # Create second module so we need to pass both modules to the API to purchase
        ModuleFactory.create(
            course=self.course,
            title='test',
            price_without_tax=100
        )

        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {'upc': self.module.qualified_id, 'seats': 5},
            ])

        assert ex.exception.detail[0] == 'You must purchase all modules for a course.'


class CheckoutOrderTests(ProductTests):
    """
    Tests for creating an order
    """

    def setUp(self):
        super(CheckoutOrderTests, self).setUp()
        self.course.live = True
        self.course.save()

        credentials = {"username": "auser", "password": "apass"}
        self.user = User.objects.create_user(**credentials)
        self.client.login(**credentials)

    def test_empty_cart_total(self):
        """
        Assert an empty order
        """
        order = create_order([], self.user)
        assert order.purchaser == self.user
        assert order.total_paid == 0
        assert order.subtotal == 0
        assert Order.objects.count() == 1
        assert OrderLine.objects.count() == 0

    def test_order_course(self):
        """
        Assert that an order is created in the database
        """
        # Create second product to test cart with multiple items
        title = "other product title"
        second_price = 345
        second_module = ModuleFactory.create(
            course=self.course,
            title=title,
            price_without_tax=second_price
        )

        first_seats = 5
        second_seats = 10
        order = create_order([
            {"upc": self.module.qualified_id, "seats": first_seats},
            {"upc": second_module.qualified_id, "seats": second_seats},
        ], self.user)
        first_line_total = self.module.price_without_tax * first_seats
        second_line_total = second_price * second_seats

        total = first_line_total + second_line_total
        assert order.purchaser == self.user
        assert order.total_paid == total
        assert order.subtotal == total
        assert order.orderline_set.count() == 2

        first_line = order.orderline_set.get(module=self.module)
        assert first_line.line_total == first_line_total
        assert first_line.price_without_tax == self.module.price_without_tax
        assert first_line.seats == first_seats

        second_line = order.orderline_set.get(module=second_module)
        assert second_line.line_total == second_line_total
        assert second_line.price_without_tax == second_price
        assert second_line.seats == second_seats
