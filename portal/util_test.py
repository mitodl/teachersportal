"""
Tests for product serializer functions.
"""

from __future__ import unicode_literals
from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

from portal.models import Order, OrderLine
from portal.views.base import CourseTests
from portal.factories import (
    CourseFactory,
    ModuleFactory,
)
from portal.util import (
    calculate_cart_subtotal,
    calculate_orderline_total,
    create_order,
    get_cents,
    course_as_dict,
    module_as_dict,
    validate_cart,
)


class CourseUtilTests(CourseTests):
    """
    Test for utility functions.
    """

    def test_course_module_json(self):
        """
        Test functionality of course_as_json and module_as_json
        """

        expected_module = {
            "title": self.module.title,
            "uuid": self.module.uuid,
            "price_without_tax": float(self.module.price_without_tax),
            "info": {
                "type": "module"
            }
        }
        course_info = {"type": "course"}
        modules_info = {
            self.module.uuid: {
                "type": "module"
            }
        }
        assert module_as_dict(self.module, modules_info[self.module.uuid]) == expected_module
        assert course_as_dict(self.course, course_info, modules_info) == {
            "title": self.course.title,
            "description": self.course.description,
            "uuid": self.course.uuid,
            "info": {
                "type": "course"
            },
            "modules": [expected_module]
        }

    def test_live_availability(self):
        """Assert that live boolean affects availability for purchase"""
        assert not self.course.is_available_for_purchase
        assert not self.module.is_available_for_purchase
        self.course.live = True
        self.course.save()
        assert self.course.is_available_for_purchase
        assert self.module.is_available_for_purchase

    def test_missing_price(self):
        """Assert that a missing price means module is unavailable for purchase"""
        self.course.live = True
        self.course.save()
        self.module.price_without_tax = None
        self.module.save()

        assert not self.course.is_available_for_purchase
        assert not self.module.is_available_for_purchase

    def test_zero_price(self):
        """Assert that a module is available for purchase even with a $0 price"""
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


class CheckoutValidationTests(CourseTests):
    """
    Tests for checkout validation
    """

    def setUp(self):
        super(CheckoutValidationTests, self).setUp()
        self.course.live = True
        self.course.save()

    def test_cart_with_zero_price(self):
        """
        Assert that we support carts with zero priced modules
        """
        self.module.price_without_tax = 0
        self.module.save()

        assert calculate_cart_subtotal([
            {
                "uuids": [self.module.uuid],
                "seats": 10,
                "course_uuid": self.course.uuid
            }
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
        module2 = ModuleFactory.create(
            course=self.course,
        )
        seats = 10
        assert calculate_cart_subtotal([
            {
                "uuids": [self.module.uuid, module2.uuid],
                "seats": seats,
                "course_uuid": self.course.uuid
            }
        ]) == (
            self.module.price_without_tax * seats +
            module2.price_without_tax * seats
        )

    def test_empty_line_total(self):
        """
        Assert that an line with a module with price $0 has a total of $0
        """
        self.module.price_without_tax = 0
        self.module.save()

        assert calculate_orderline_total(self.module.uuid, 10) == 0

    def test_line_total(self):
        """
        Assert that a line total is the price times quantity.
        """
        assert calculate_orderline_total(self.module.uuid, 10) == self.module.price_without_tax * 10

    def test_validation(self):
        """
        Assert that a valid cart will pass validation.
        """
        validate_cart([
            {
                "uuids": [self.module.uuid],
                "seats": 10,
                "course_uuid": self.course.uuid
            }
        ])

    def test_no_seats(self):
        """
        Assert that a cart item cannot have zero seats.
        """
        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {
                    "uuids": [self.module.uuid],
                    "seats": 0,
                    "course_uuid": self.course.uuid
                }
            ])
        assert ex.exception.detail[0] == "Number of seats is zero"

    def test_unavailable_items(self):
        """
        Assert that any references to items not for sale will cause a validation error.
        """
        self.course.live = False
        self.course.save()

        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {
                    "uuids": [self.module.uuid],
                    "seats": 10,
                    "course_uuid": self.course.uuid
                }
            ])
        assert ex.exception.detail[0] == "One or more modules are unavailable"

        self.course.live = True
        self.course.save()
        self.module.price_without_tax = None
        self.module.save()

        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {
                    "uuids": [self.module.uuid],
                    "seats": 10,
                    "course_uuid": self.course.uuid
                }
            ])
        assert ex.exception.detail[0] == "One or more modules are unavailable"

    def test_missing_module(self):
        """
        Assert that references to modules that are missing will cause a validation error.
        """
        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {
                    "uuids": ["missing"],
                    "seats": 10,
                    "course_uuid": self.course.uuid
                }
            ])
        assert ex.exception.detail[0] == "One or more modules are unavailable"

    def test_missing_courses(self):
        """
        Assert that references to courses that are missing will cause a validation error.
        """
        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {
                    "uuids": [self.module.uuid],
                    "seats": 10,
                    "course_uuid": "missing"
                }
            ])
        assert ex.exception.detail[0] == "One or more courses are unavailable"

    def test_missing_keys(self):
        """
        Assert that missing keys cause a ValidationError.
        """
        item = {
            "uuids": [self.module.uuid],
            "seats": 10,
            "course_uuid": self.course.uuid
        }
        for key in ('uuids', 'seats', 'course_uuid'):
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
            item = {
                "uuids": [self.module.uuid],
                "seats": seats,
                "course_uuid": self.course.uuid
            }
            with self.assertRaises(ValidationError) as ex:
                validate_cart([item])
            assert ex.exception.detail[0] == "Seats must be an integer"

    def test_duplicate_modules(self):
        """
        Assert that we don't allow duplicate modules in cart
        """
        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {
                    "uuids": [self.module.uuid, self.module.uuid],
                    "seats": 10,
                    "course_uuid": self.course.uuid
                }
            ])
        assert ex.exception.detail[0] == "Duplicate module in cart"

    def test_duplicate_courses(self):
        """
        Assert that we don't allow duplicate courses in cart
        """
        module2 = ModuleFactory.create(
            course=self.course
        )
        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {
                    "uuids": [self.module.uuid],
                    "seats": 10,
                    "course_uuid": self.course.uuid
                },
                {
                    "uuids": [module2.uuid],
                    "seats": 15,
                    "course_uuid": self.course.uuid
                }
            ])
        assert ex.exception.detail[0] == "Duplicate course in cart"

    def test_course_module_mismatch(self):
        """
        Assert that we don't allow duplicate items in cart
        """
        # Also creates a new course
        module2 = ModuleFactory.create()
        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {
                    "uuids": [self.module.uuid],
                    "seats": 10,
                    "course_uuid": module2.course.uuid
                }
            ])
        assert ex.exception.detail[0] == "Course does not match up with module"

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
                {
                    'uuids': [self.module.uuid],
                    'seats': 5,
                    'course_uuid': self.course.uuid
                },
            ])

        assert ex.exception.detail[0] == 'You must purchase all modules for a course.'

    def test_dont_allow_empty_uuids(self):
        """
        Raise a ValidationError if uuids list is empty
        """
        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {
                    'uuids': [],
                    'seats': 5,
                    'course_uuid': self.course.uuid
                },
            ])

        assert ex.exception.detail[0] == 'uuids must not be empty'


class CheckoutOrderTests(CourseTests):
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
        # Create second module to test cart with multiple items
        title = "other product title"
        second_price = 345
        second_course = CourseFactory.create(
            live=True
        )
        second_module = ModuleFactory.create(
            course=second_course,
            title=title,
            price_without_tax=second_price
        )

        first_seats = 5
        second_seats = 10
        order = create_order([
            {
                "uuids": [self.module.uuid],
                "seats": first_seats,
                "course_uuid": self.course.uuid
            },
            {
                "uuids": [second_module.uuid],
                "seats": second_seats,
                "course_uuid": second_module.course.uuid
            },
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
