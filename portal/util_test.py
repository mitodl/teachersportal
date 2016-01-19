"""
Tests for product serializer functions.
"""

from __future__ import unicode_literals

from django.contrib.auth.models import User
from mock import patch
from oscar.apps.catalogue.models import Category, Product, ProductCategory
from oscar.apps.partner.models import Partner, StockRecord
from rest_framework.exceptions import ValidationError

from portal.exceptions import ProductException
from portal.models import Order, OrderLine
from portal.views.base import ProductTests
from portal.factories import ProductFactory
from portal.util import (
    calculate_cart_subtotal,
    calculate_cart_item_total,
    create_order,
    make_upc,
    make_external_pk,
    get_external_pk,
    get_price_without_tax,
    get_product_type,
    is_available_to_buy,
    product_as_json,
    validate_cart,
    validate_product,
    COURSE_PRODUCT_TYPE,
    MODULE_PRODUCT_TYPE,
)


class ProductUtilTests(ProductTests):
    """
    Test for Product utility functions.
    """

    def test_product_as_json(self):
        """
        Test functionality of product_as_json
        """

        with patch('portal.util.get_price_without_tax', autospec=True) as price_mock:
            with patch('portal.util.is_available_to_buy', autospec=True) as available_mock:
                price = 123.45

                def _get_price_without_tax(product):
                    """Mocked price function"""
                    if product.upc == self.child.upc:
                        return price
                    return None
                price_mock.side_effect = _get_price_without_tax

                def _is_available_to_buy(product):
                    """Mocked availability function"""
                    if product.upc == self.child.upc:
                        return True
                    return False
                available_mock.side_effect = _is_available_to_buy

                expected_child = {
                    "upc": self.child.upc,
                    "title": self.child.title,
                    "description": self.child.description,
                    "external_pk": make_external_pk(MODULE_PRODUCT_TYPE, self.child.upc),
                    "product_type": MODULE_PRODUCT_TYPE,
                    "price_without_tax": price,
                    "parent_upc": self.parent.upc,
                    "info": None,
                    "children": []
                }
                assert product_as_json(self.child, {}) == expected_child

                ccxcon_title = "a title"
                assert product_as_json(self.parent, {
                    self.parent.upc: {
                        "title": ccxcon_title
                    }
                }) == {
                    "upc": self.parent.upc,
                    "title": self.parent.title,
                    "description": self.parent.description,
                    "external_pk": make_external_pk(COURSE_PRODUCT_TYPE, self.parent.upc),
                    "product_type": COURSE_PRODUCT_TYPE,
                    "price_without_tax": None,
                    "parent_upc": None,
                    "info": {
                        "title": ccxcon_title
                    },
                    "children": [expected_child]
                }

    def test_make_upc(self):  # pylint: disable=no-self-use
        """Assert make_upc behavior"""
        assert make_upc("product_type", "external_pk") == "product_type_external_pk"

    def test_make_external_pk(self):
        """Assert make_external_pk behavior"""
        assert make_external_pk("type", "type_upc") == "upc"

        with self.assertRaises(ProductException) as ex:
            make_external_pk("type", "other_prefix_upc")
        assert ex.exception.args[0] == "Unexpected prefix found"

    def test_get_external_pk(self):
        """Assert get_external_pk behavior"""
        assert get_external_pk(self.child) == self.child.upc[len(MODULE_PRODUCT_TYPE) + 1:]
        assert get_external_pk(self.parent) == self.parent.upc[len(COURSE_PRODUCT_TYPE) + 1:]

    def test_get_upc(self):
        """Assert """
        assert get_product_type(self.child) == MODULE_PRODUCT_TYPE
        assert get_product_type(self.parent) == COURSE_PRODUCT_TYPE

    def test_price_and_availability(self):
        """Assert get_price_without_tax behavior"""
        assert get_price_without_tax(self.parent) is None
        assert not is_available_to_buy(self.parent)
        assert get_price_without_tax(self.child) is None
        assert not is_available_to_buy(self.child)

        # Adding a stockrecord should make it available
        partner = Partner.objects.first()
        StockRecord.objects.create(
            product=self.child,
            partner=partner,
            partner_sku=self.child.upc,
            price_currency="$",
            price_excl_tax=123,
        )
        assert get_price_without_tax(self.parent) is None
        assert is_available_to_buy(self.parent)
        assert get_price_without_tax(self.child) == 123
        assert is_available_to_buy(self.child)


class ProductValidationTests(ProductTests):
    """
    Product validation tests.
    """
    def validate_products(self):  # pylint: disable=no-self-use
        """
        Run validate_product on all products in database.
        """
        for product in Product.objects.all():
            validate_product(product)

    def test_parent_cant_have_price(self):
        """
        Make sure parent can't have a price.
        """
        partner = Partner.objects.first()
        StockRecord.objects.create(
            product=self.parent,
            partner=partner,
            partner_sku=self.parent.upc,
            price_currency="$",
            price_excl_tax=123,
        )

        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "Only CHILD products can have StockRecords"

    def test_invalid_partner_sku(self):
        """
        Access API when a StockRecord's partner_sku doesn't match Product.upc.
        """
        price = 123
        partner = Partner.objects.first()
        StockRecord.objects.create(
            product=self.child,
            partner=partner,
            partner_sku=make_upc(MODULE_PRODUCT_TYPE, "mismatched sku"),
            price_currency="$",
            price_excl_tax=price,
        )

        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "StockRecord SKU does not match Product UPC"

    def test_invalid_currency(self):
        """
        Make sure currency == "$".
        """
        price = 123
        partner = Partner.objects.first()
        StockRecord.objects.create(
            product=self.child,
            partner=partner,
            partner_sku=self.child.upc,
            price_currency="GBP",
            price_excl_tax=price,
        )

        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "StockRecord price_currency must be $"

    def test_two_stockrecords(self):
        """
        Try creating a product with two StockRecords.
        """
        other_sku = make_upc(MODULE_PRODUCT_TYPE, "other sku")

        price1, price2 = 123, 345
        partner = Partner.objects.first()
        StockRecord.objects.create(
            product=self.child,
            partner=partner,
            partner_sku=other_sku,
            price_currency="$",
            price_excl_tax=price1,
        )
        StockRecord.objects.create(
            product=self.child,
            partner=partner,
            partner_sku=self.child.upc,
            price_currency="$",
            price_excl_tax=price2,
        )

        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "More than one StockRecords for a Product"

    def test_child_without_parent(self):
        """
        Children must have parents.
        """
        with self.assertRaises(AttributeError) as ex:
            Product.objects.create(
                upc=make_upc(MODULE_PRODUCT_TYPE, "child"),
                product_class=None,
                structure=Product.CHILD,
                parent=None,
                title=self.child.title
            )
        assert ex.exception.args[0] == "'NoneType' object has no attribute 'product_class'"

    def test_child_has_no_children(self):
        """
        Children must not have children.
        """
        child = Product.objects.create(
            upc=make_upc(MODULE_PRODUCT_TYPE, "parent child"),
            product_class=self.parent.product_class,
            structure=Product.CHILD,
            parent=self.parent,
            title="child of parent"
        )
        Product.objects.create(
            upc=make_upc(MODULE_PRODUCT_TYPE, "child"),
            product_class=self.parent.product_class,
            structure=Product.CHILD,
            parent=child,
            title="child of child"
        )
        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "Children cannot have product_class set"

    def test_parent_has_children(self):
        """
        Parents must have children.
        """
        Product.objects.create(
            upc=make_upc(COURSE_PRODUCT_TYPE, "parent"),
            product_class=self.parent.product_class,
            structure=Product.PARENT,
            parent=None,
            title=self.parent.title
        )
        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "PARENT products must have children"

    def test_standalone_has_no_children(self):
        """
        Standalone products must not have children.
        """
        parent = Product.objects.create(
            upc=make_upc(COURSE_PRODUCT_TYPE, "parent"),
            product_class=self.parent.product_class,
            structure=Product.STANDALONE,
            parent=None,
            title=self.parent.title
        )
        Product.objects.create(
            upc=make_upc(MODULE_PRODUCT_TYPE, "child"),
            product_class=self.child.product_class,
            structure=Product.CHILD,
            parent=parent,
            title="child"
        )
        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "STANDALONE products must not have children"

    def test_parent_with_parent(self):
        """
        Parents must not have a parent.
        """
        Product.objects.create(
            upc=make_upc(COURSE_PRODUCT_TYPE, "parent"),
            product_class=self.parent.product_class,
            structure=Product.PARENT,
            parent=self.parent,
            title=self.parent.title
        )
        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "PARENT products must not have a parent"

    def test_child_is_not_module(self):
        """
        Only modules can be children.
        """
        Product.objects.create(
            upc=make_upc(COURSE_PRODUCT_TYPE, "child"),
            product_class=None,
            structure=Product.CHILD,
            parent=self.parent,
            title=self.child.title
        )
        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "Modules may only be CHILD Products"

    def test_parent_is_not_course(self):
        """
        Only courses can be parents.
        """
        Product.objects.create(
            upc=make_upc(MODULE_PRODUCT_TYPE, "child"),
            product_class=self.parent.product_class,
            structure=Product.PARENT,
            parent=None,
            title=self.parent.title
        )
        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "Courses may only be PARENT Products"

    def test_standalone_is_not_course(self):
        """
        Only courses can be standalone.
        """
        Product.objects.create(
            upc=make_upc(MODULE_PRODUCT_TYPE, "child"),
            product_class=self.parent.product_class,
            structure=Product.STANDALONE,
            parent=None,
            title=self.parent.title
        )
        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "Courses may only be PARENT Products"

    def test_invalid_upc(self):
        """
        UPC must be prefixed with product type
        """
        Product.objects.create(
            upc=make_upc("other", "child"),
            product_class=None,
            structure=Product.CHILD,
            parent=self.parent,
            title=self.child.title
        )
        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "Invalid product type"

    def test_child_with_product_class(self):
        """
        Children can't have product_class set (it inherits from parent)
        """
        Product.objects.create(
            upc=make_upc(MODULE_PRODUCT_TYPE, "child"),
            product_class=self.parent.product_class,
            structure=Product.CHILD,
            parent=self.parent,
            title=self.child.title
        )
        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "Children cannot have product_class set"

    def test_parent_has_category(self):
        """
        Parent must have category which is assigned to "Course"
        """
        parent = Product.objects.create(
            upc=make_upc(COURSE_PRODUCT_TYPE, "parent2"),
            product_class=self.parent.product_class,
            structure=Product.PARENT,
            parent=None,
            title=self.parent.title
        )
        Product.objects.create(
            upc=make_upc(MODULE_PRODUCT_TYPE, "child2"),
            structure=Product.CHILD,
            parent=parent,
            title="child"
        )
        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "STANDALONE and PARENT products must have a category"

    def test_standalone_has_category(self):
        """
        Standalone product has category which is assigned to "Course"
        """
        Product.objects.create(
            upc=make_upc(COURSE_PRODUCT_TYPE, "standalone"),
            product_class=self.parent.product_class,
            structure=Product.STANDALONE,
            parent=None,
            title="standalone"
        )
        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "STANDALONE and PARENT products must have a category"

    def test_child_has_category(self):
        """
        Child must not have category which is assigned to "Course"
        """
        product = Product.objects.create(
            upc=make_upc(MODULE_PRODUCT_TYPE, "child"),
            structure=Product.CHILD,
            parent=self.parent,
            title=self.child.title
        )
        ProductCategory.objects.create(
            product=product,
            category=Category.objects.get(name="Course")
        )

        with self.assertRaises(ProductException) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "CHILD products can't have categories"

    def test_parent_product_class(self):
        """
        Parent product class must be set to Course.
        """
        with self.assertRaises(AttributeError) as ex:
            Product.objects.create(
                upc=make_upc(COURSE_PRODUCT_TYPE, "parent"),
                product_class=None,
                structure=Product.PARENT,
                parent=None,
                title=self.parent.title
            )
        assert ex.exception.args[0] == "'NoneType' object has no attribute 'attributes'"

    def test_standalone_product_class(self):
        """
        Standalone product class must be set to Course.
        """
        with self.assertRaises(AttributeError) as ex:
            Product.objects.create(
                upc=make_upc(COURSE_PRODUCT_TYPE, "parent"),
                product_class=None,
                structure=Product.STANDALONE,
                parent=None,
                title=self.parent.title
            )
        assert ex.exception.args[0] == "'NoneType' object has no attribute 'attributes'"


class CheckoutValidationTests(ProductTests):
    """
    Tests for checkout validation
    """

    def setUp(self):
        super(CheckoutValidationTests, self).setUp()
        partner = Partner.objects.first()
        self.price = 123
        StockRecord.objects.create(
            product=self.child,
            partner=partner,
            partner_sku=self.child.upc,
            price_currency="$",
            price_excl_tax=self.price,
        )

    def test_cart_with_zero_price(self):
        """
        Assert that we support carts with zero priced products
        """
        stockrecord = StockRecord.objects.first()
        stockrecord.price_excl_tax = 0
        stockrecord.save()

        assert calculate_cart_subtotal([
            {"upc": self.child.upc, "seats": 10}
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
            {"upc": self.child.upc, "seats": 10}
        ]) == self.price * 10

    def test_empty_line_total(self):
        """
        Assert that an empty line has a total of 0
        """
        stockrecord = StockRecord.objects.first()
        stockrecord.price_excl_tax = 0
        stockrecord.save()

        assert calculate_cart_item_total({
            "upc": self.child.upc,
            "seats": 10
        }) == 0

    def test_line_total(self):
        """
        Assert that a line total is the price times quantity.
        """
        assert calculate_cart_item_total({
            "upc": self.child.upc,
            "seats": 10
        }) == self.price * 10

    def test_validation(self):
        """
        Assert that a valid cart will pass validation.
        """
        validate_cart([
            {"upc": self.child.upc, "seats": 10}
        ])

    def test_no_seats(self):
        """
        Assert that a valid cart will pass validation.
        """
        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {"upc": self.child.upc, "seats": 0}
            ])
        assert ex.exception.detail[0] == "Number of seats is zero"

    def test_purchase_of_course(self):
        """
        Assert that we don't allow purchases of courses, just individual modules.
        """
        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {"upc": self.parent.upc, "seats": 10}
            ])
        assert ex.exception.detail[0] == "Cannot purchase a Course"

    def test_unavailable_items(self):
        """
        Assert that any references to items not for sale will cause a validation error.
        """
        # Make all products unavailable for purchase
        StockRecord.objects.all().delete()

        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {"upc": self.child.upc, "seats": 10}
            ])
        assert ex.exception.detail[0] == "One or more products are unavailable"

    def test_missing_items(self):
        """
        Assert that references to items that are missing will cause a validation error.
        """
        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {"upc": "missing", "seats": 10}
            ])
        assert ex.exception.detail[0] == "One or more products are unavailable"

    def test_missing_keys(self):
        """
        Assert that missing keys cause a ValidationError.
        """
        item = {"upc": self.child.upc, "seats": 10}
        for key in ('upc', 'seats'):
            with self.assertRaises(ValidationError) as ex:
                item_copy = dict(item)
                del item_copy[key]
                validate_cart([item_copy])
            assert ex.exception.detail[0] == "Missing key {}".format(key)

    def test_duplicate_order(self):
        """
        Assert that we don't allow duplicate items in cart
        """
        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {"upc": self.child.upc, "seats": 10},
                {"upc": self.child.upc, "seats": 5}
            ])
        assert ex.exception.detail[0] == "Duplicate item in cart"

    def test_must_have_all_children_in_cart(self):  # pylint: disable=invalid-name
        """
        If user tries to buy a subset of a course, raise a validation error.

        Note: It's expected that this will be removed when we support buying
        modules.
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

        with self.assertRaises(ValidationError) as ex:
            validate_cart([
                {'upc': self.child.upc, 'seats': 5},
            ])

        assert ex.exception.detail[0] == 'You must purchase all modules for a course.'


class CheckoutOrderTests(ProductTests):
    """
    Tests for creating an order
    """

    def setUp(self):
        super(CheckoutOrderTests, self).setUp()
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
        partner = Partner.objects.first()
        upc = make_upc(MODULE_PRODUCT_TYPE, "child-uuid-2")
        title = "other product title"
        second_price = 345
        second_product = Product.objects.create(
            upc=upc,
            description="Product description duplicate",
            product_class=None,
            structure=Product.CHILD,
            parent=self.parent,
            title=title
        )
        StockRecord.objects.create(
            product=second_product,
            partner=partner,
            partner_sku=second_product.upc,
            price_currency="$",
            price_excl_tax=second_price,
        )

        first_seats = 5
        second_seats = 10
        order = create_order([
            {"upc": self.child.upc, "seats": first_seats},
            {"upc": second_product.upc, "seats": second_seats},
        ], self.user)
        first_line_total = self.price * first_seats
        second_line_total = second_price * second_seats

        total = first_line_total + second_line_total
        assert order.purchaser == self.user
        assert order.total_paid == total
        assert order.subtotal == total
        assert order.orderline_set.count() == 2

        first_line = order.orderline_set.get(product=self.child)
        assert first_line.line_total == first_line_total
        assert first_line.price_without_tax == self.price
        assert first_line.seats == first_seats

        second_line = order.orderline_set.get(product=second_product)
        assert second_line.line_total == second_line_total
        assert second_line.price_without_tax == second_price
        assert second_line.seats == second_seats
