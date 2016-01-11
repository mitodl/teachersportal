"""
Tests for Product API
"""

from __future__ import unicode_literals

import json
from mock import patch
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from oscar.apps.catalogue.models import Product, ProductClass
from oscar.apps.partner.models import Partner, StockRecord
import requests_mock

from portal.views.base import ProductTests
from portal.views.util import as_json
from portal.util import (
    product_as_json,
    get_external_pk,
    COURSE_PRODUCT_TYPE,
    MODULE_PRODUCT_TYPE,
)


FAKE_CCXCON_API = 'https://fakehost/api/'


@override_settings(CCXCON_API=FAKE_CCXCON_API)
class ProductAPITests(ProductTests):
    """
    Tests for product API
    """

    def setUp(self):
        """
        Set up the products and also add a StockRecord to make it available to purchase.
        """
        super(ProductAPITests, self).setUp()
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

    def validate_product_api(self, products_from_api):  # pylint: disable=no-self-use
        """
        Helper function to verify 200 and return list of products.
        """
        for product_from_api in products_from_api:
            # Assert consistency between database and what API endpoint is returning.
            product_from_db = Product.objects.get(
                upc=product_from_api['upc']
            )
            assert product_from_db.title == product_from_api['title']
            assert product_from_db.upc == product_from_api['upc']

            parent = product_from_db.parent
            if parent is None:
                assert product_from_api['parent_upc'] is None
                if product_from_db.children.count() == 0:
                    assert product_from_db.structure == Product.STANDALONE
                else:
                    assert product_from_db.structure == Product.PARENT

                assert product_from_db.product_class == ProductClass.objects.get(name="Course")
            else:
                assert product_from_db.product_class is None
                assert product_from_api['parent_upc'] == parent.upc
                assert product_from_db.structure == Product.CHILD

                # Make sure there's one StockRecord and SKU matches UPC
                assert product_from_db.stockrecords.count() == 1
                assert product_from_db.upc == product_from_db.stockrecords.first().partner_sku
        return products_from_api

    def test_no_stockrecord(self):
        """
        Make sure API shows no products if none have StockRecords.
        """
        StockRecord.objects.all().delete()

        resp = self.client.get(reverse("product-list"))
        assert resp.status_code == 200, resp.content.decode('utf-8')
        products_from_api = as_json(resp)

        self.validate_product_api(products_from_api)
        assert products_from_api == []

    def test_one_stockrecord(self):
        """
        Make sure API returns this product since it has a StockRecord.
        """
        # API only shows products with StockRecords
        resp = self.client.get(reverse("product-list"))
        assert resp.status_code == 200, resp.content.decode('utf-8')
        products_from_api = as_json(resp)

        self.validate_product_api(products_from_api)
        assert products_from_api == [
            product_as_json(self.parent, {}),
            product_as_json(self.child, {}),
        ]

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_product_detail_for_module(self, mock, fetch_mock):  # pylint: disable=unused-argument
        """
        Test that product detail for modules works properly.
        """
        module_uuid = get_external_pk(self.child)
        ccxcon_title = "ccxcon title"
        subchapters = ["subchapter1", "subchapter2"]
        fetch_mock.get("{base}v1/coursexs/{course_uuid}/modules/{module_uuid}/".format(
            base=FAKE_CCXCON_API,
            course_uuid=get_external_pk(self.child.parent),
            module_uuid=module_uuid,
        ), text=json.dumps(
            {
                "uuid": module_uuid,
                "title": ccxcon_title,
                "subchapters": subchapters,
                "course": "https://example.com/",
                "url": "https://example.com/"
            }
        ))
        resp = self.client.get(
            reverse("product-detail", kwargs={"uuid": self.child.upc})
        )
        assert resp.status_code == 200
        assert json.loads(resp.content.decode('utf-8')) == {
            "info": {
                "title": ccxcon_title,
                "subchapters": subchapters
            },
            "parent_upc": self.parent.upc,
            "product_type": MODULE_PRODUCT_TYPE,
            "title": self.child.title,
            "description": self.child.description,
            "external_pk": get_external_pk(self.child),
            "children": [],
            "upc": self.child.upc,
            "price_without_tax": self.price
        }

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_product_detail_for_course(self, mock, fetch_mock):  # pylint: disable=unused-argument
        """
        Test that product detail for courses works properly.
        """
        course_uuid = get_external_pk(self.parent)
        module_uuid = get_external_pk(self.child)

        ccxcon_course_title = "ccxcon course title"
        ccxcon_module_title = "ccxcon module title"
        ccxcon_description = "ccxcon description"
        author = "author"
        overview = "overview"
        subchapters = ["subchapter1", "subchapter2"]
        image_url = "http://youtube.com/"
        fetch_mock.get("{base}v1/coursexs/{course_uuid}/".format(
            base=FAKE_CCXCON_API,
            course_uuid=course_uuid,
        ), text=json.dumps(
            {
                "uuid": course_uuid,
                "title": ccxcon_course_title,
                "author_name": author,
                "overview": overview,
                "description": ccxcon_description,
                "image_url": image_url,
                "edx_instance": "http://mitx.edx.org",
                "url": "https://example.com",
                "modules": "https://example.com",
                "instructors": [],
                "course_id": "course_id"
            }
        ))
        fetch_mock.get("{base}v1/coursexs/{course_uuid}/modules/".format(
            base=FAKE_CCXCON_API,
            course_uuid=course_uuid
        ), text=json.dumps([
            {
                "uuid": module_uuid,
                "title": ccxcon_module_title,
                "subchapters": subchapters,
                "course": "https://example.com/",
                "url": "https://example.com/"
            }
        ]))

        resp = self.client.get(
            reverse("product-detail", kwargs={"uuid": self.parent.upc})
        )
        assert resp.status_code == 200
        assert json.loads(resp.content.decode('utf-8')) == {
            "info": {
                "title": ccxcon_course_title,
                "description": ccxcon_description,
                "overview": overview,
                "image_url": image_url,
                "author_name": author
            },
            "parent_upc": None,
            "product_type": COURSE_PRODUCT_TYPE,
            "title": self.parent.title,
            "description": self.parent.description,
            "external_pk": course_uuid,
            "children": [
                {
                    "info": {
                        "title": ccxcon_module_title,
                        "subchapters": subchapters
                    },
                    "parent_upc": self.parent.upc,
                    "product_type": MODULE_PRODUCT_TYPE,
                    "title": self.child.title,
                    "description": self.child.description,
                    "external_pk": module_uuid,
                    "children": [],
                    "upc": self.child.upc,
                    "price_without_tax": self.price
                }
            ],
            "upc": self.parent.upc,
            "price_without_tax": None
        }

    def test_product_not_available(self):
        """
        Test that product detail returns a 404 if the product is not available.
        """
        # Make child unavailable for purchase
        StockRecord.objects.all().delete()

        resp = self.client.get(
            reverse("product-detail", kwargs={"uuid": self.child.upc})
        )
        assert resp.status_code == 404, resp.content.decode('utf-8')

    def test_not_logged_in(self):
        """
        Test that product list and detail are only available to logged in users.
        """
        self.client.logout()
        resp = self.client.get(
            reverse("product-detail", kwargs={"uuid": self.child.upc})
        )
        assert resp.status_code == 403, resp.content.decode('utf-8')

        resp = self.client.get(reverse("product-list"))
        assert resp.status_code == 403, resp.content.decode('utf-8')

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_ccxcon_connection_broken(self, mock, fetch_mock):  # pylint: disable=unused-argument
        """
        Test that if the CCXCon connection is broken an exception is raised
        (producing a 500 error).
        """
        module_uuid = get_external_pk(self.child)
        fetch_mock.get("{base}v1/coursexs/{course_uuid}/modules/{module_uuid}/".format(
            base=FAKE_CCXCON_API,
            course_uuid=get_external_pk(self.child.parent),
            module_uuid=module_uuid,
        ), status_code=500, text="{}")

        with self.assertRaises(Exception) as ex:
            self.client.get(
                reverse("product-detail", kwargs={"uuid": self.child.upc})
            )
        assert "CCXCon returned a non 200 status code 500" in ex.exception.args[0]

        # Product list API does not read from CCXCon so it should be unaffected
        resp = self.client.get(reverse('product-list'))
        assert resp.status_code == 200
