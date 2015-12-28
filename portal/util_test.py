"""
Tests for product serializer functions.
"""

from __future__ import unicode_literals

from mock import patch
from oscar.apps.catalogue.models import Product
from oscar.apps.partner.models import Partner, StockRecord

from portal.views.base import ProductTests
from portal.util import (
    product_as_json,
    make_upc,
    make_external_pk,
    get_external_pk,
    get_price_without_tax,
    get_product_type,
    is_available_to_buy,
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

        with self.assertRaises(Exception) as ex:
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

        with self.assertRaises(Exception) as ex:
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

        with self.assertRaises(Exception) as ex:
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

        with self.assertRaises(Exception) as ex:
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

        with self.assertRaises(Exception) as ex:
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
        with self.assertRaises(Exception) as ex:
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
        with self.assertRaises(Exception) as ex:
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
        with self.assertRaises(Exception) as ex:
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
        with self.assertRaises(Exception) as ex:
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
        with self.assertRaises(Exception) as ex:
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
        with self.assertRaises(Exception) as ex:
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
        with self.assertRaises(Exception) as ex:
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
        with self.assertRaises(Exception) as ex:
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
        with self.assertRaises(Exception) as ex:
            self.validate_products()
        assert ex.exception.args[0] == "Children cannot have product_class set"

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
