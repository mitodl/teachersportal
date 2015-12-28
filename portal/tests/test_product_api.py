"""
Tests for Product API
"""

from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from oscar.apps.catalogue.models import Product, ProductClass
from oscar.apps.partner.models import Partner, StockRecord

from portal.tests.util import as_json
from portal.util import (
    make_external_pk,
    make_upc,
    COURSE_PRODUCT_TYPE,
    MODULE_PRODUCT_TYPE,
)


class ProductAPITests(TestCase):
    """
    Tests for product API
    """

    def setUp(self):
        """
        Create parent and child Products with no StockRecords to start with.
        """
        product_class = ProductClass.objects.get(name="Course")
        self.parent_external_pk = "uuid"
        parent_upc = make_upc(COURSE_PRODUCT_TYPE, self.parent_external_pk)
        parent_title = "parent's title"
        self.parent = Product.objects.create(
            upc=parent_upc,
            product_class=product_class,
            structure=Product.PARENT,
            parent=None,
            title=parent_title
        )

        self.child_external_pk = "uuid"
        child_upc = make_upc(MODULE_PRODUCT_TYPE, self.child_external_pk)
        child_title = "child's title"
        self.child = Product.objects.create(
            upc=child_upc,
            product_class=None,
            structure=Product.CHILD,
            parent=self.parent,
            title=child_title
        )

    def get_products(self):
        """
        Helper function to verify 200 and return list of products.
        """
        resp = self.client.get(reverse("product-list"))
        assert resp.status_code == 200, resp.content
        products_from_api = as_json(resp)

        for product_from_api in products_from_api:
            # Assert consistency between database and what API endpoint is returning.
            product_from_db = Product.objects.get(
                upc=make_upc(
                    product_from_api['product_type'],
                    product_from_api['external_pk']
                )
            )
            assert product_from_db.title == product_from_api['title']
            assert product_from_db.upc == make_upc(
                product_from_api['product_type'],
                product_from_api['external_pk'],
            )

            parent = product_from_db.parent
            if parent is None:
                assert product_from_api['parent_external_pk'] is None
                if product_from_db.children.count() == 0:
                    assert product_from_db.structure == Product.STANDALONE
                else:
                    assert product_from_db.structure == Product.PARENT

                assert product_from_db.product_class == ProductClass.objects.get(name="Course")
            else:
                assert product_from_db.product_class is None
                assert product_from_api['parent_external_pk'] == make_external_pk(
                    str(parent.product_class),
                    parent.upc
                )
                assert product_from_db.structure == Product.CHILD

                # Make sure there's one StockRecord and SKU matches UPC
                assert product_from_db.stockrecords.count() == 1
                assert product_from_db.upc == product_from_db.stockrecords.first().partner_sku
        return products_from_api

    def test_no_stockrecord(self):
        """
        Make sure API shows no products if none have StockRecords.
        """
        assert self.get_products() == []

    def test_one_stockrecord(self):
        """
        Make sure API returns this product since it has a StockRecord.
        """
        partner = Partner.objects.first()
        StockRecord.objects.create(
            product=self.child,
            partner=partner,
            partner_sku=self.child.upc,
            price_currency="$",
            price_excl_tax=123,
        )

        # API only shows products with StockRecords
        assert self.get_products() == [
            {
                'external_pk': self.parent_external_pk,
                'parent_external_pk': None,
                'price_without_tax': None,
                'product_type': COURSE_PRODUCT_TYPE,
                'title': self.parent.title
            },
            {
                'external_pk': self.child_external_pk,
                'parent_external_pk': self.parent_external_pk,
                'price_without_tax': '123.00',
                'product_type': MODULE_PRODUCT_TYPE,
                'title': self.child.title
            },
        ]

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
            self.get_products()
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
            self.get_products()
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
            self.get_products()
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
            self.get_products()
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
            self.get_products()
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
            self.get_products()
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
            product_class=self.parent.product_class,
            structure=Product.CHILD,
            parent=parent,
            title="child"
        )
        with self.assertRaises(Exception) as ex:
            self.get_products()
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
            self.get_products()
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
            self.get_products()
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
            self.get_products()
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
            self.get_products()
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
            self.get_products()
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
            self.get_products()
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
