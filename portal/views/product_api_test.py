"""
Tests for Product API
"""

from __future__ import unicode_literals

import json
from mock import patch
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import requests_mock

from portal.models import Course, Module
from portal.views.base import ProductTests, FAKE_CCXCON_API
from portal.views.util import as_json
from portal.util import (
    course_as_product_json,
    module_as_product_json,
    COURSE_PRODUCT_TYPE,
    MODULE_PRODUCT_TYPE,
    get_product_type,
    make_external_pk,
)


class ProductAPITests(ProductTests):
    """
    Tests for product API
    """

    def setUp(self):
        """
        Set up the products and also add a StockRecord to make it available to purchase.
        """
        super(ProductAPITests, self).setUp()
        self.course.live = True
        self.course.save()

        credentials = {"username": "auser", "password": "apass"}
        User.objects.create_user(**credentials)
        self.client.login(**credentials)

    def validate_product_api(self, products_from_api):  # pylint: disable=no-self-use
        """
        Helper function to verify 200 and return list of products.
        """
        for product_from_api in products_from_api:
            # Assert consistency between database and what API endpoint is returning.
            qualified_id = product_from_api['upc']
            product_type = get_product_type(qualified_id)
            uuid = make_external_pk(product_type, qualified_id)
            if product_type == COURSE_PRODUCT_TYPE:
                course = Course.objects.get(uuid=uuid)
                assert course.title == product_from_api['title']
                assert course.description == product_from_api['description']
                assert product_from_api['price_without_tax'] is None
            elif product_type == MODULE_PRODUCT_TYPE:
                module = Module.objects.get(uuid=uuid)
                assert module.title == product_from_api['title']
                assert float(module.price_without_tax) == product_from_api['price_without_tax']
            else:
                raise Exception("Unexpected product type")

        return products_from_api

    def test_not_live(self):
        """
        Make sure API shows no products if none are live.
        """
        self.course.live = False
        self.course.save()

        resp = self.client.get(reverse("product-list"))
        assert resp.status_code == 200, resp.content.decode('utf-8')
        products_from_api = as_json(resp)

        self.validate_product_api(products_from_api)
        assert products_from_api == []

    def test_live(self):
        """
        Make sure API returns this product since it's live.
        """
        # API only shows products with StockRecords
        resp = self.client.get(reverse("product-list"))
        assert resp.status_code == 200, resp.content.decode('utf-8')
        products_from_api = as_json(resp)

        self.validate_product_api(products_from_api)
        assert products_from_api == [
            course_as_product_json(self.course, {}),
            module_as_product_json(self.module, {}),
        ]

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_product_detail_for_module(self, mock, fetch_mock):  # pylint: disable=unused-argument
        """
        Test that product detail for modules works properly.
        """
        module_uuid = self.module.uuid
        ccxcon_title = "ccxcon title"
        subchapters = ["subchapter1", "subchapter2"]
        fetch_mock.get("{base}v1/coursexs/{course_uuid}/modules/{module_uuid}/".format(
            base=FAKE_CCXCON_API,
            course_uuid=self.module.course.uuid,
            module_uuid=module_uuid,
        ), json={
            "uuid": module_uuid,
            "title": ccxcon_title,
            "subchapters": subchapters,
            "course": "https://example.com/",
            "url": "https://example.com/"
        })
        resp = self.client.get(
            reverse("product-detail", kwargs={"qualified_id": self.module.qualified_id})
        )
        assert resp.status_code == 200
        assert json.loads(resp.content.decode('utf-8')) == {
            "info": {
                "title": ccxcon_title,
                "subchapters": subchapters
            },
            "parent_upc": self.course.qualified_id,
            "product_type": MODULE_PRODUCT_TYPE,
            "title": self.module.title,
            "description": "",
            "external_pk": self.module.uuid,
            "children": [],
            "upc": self.module.qualified_id,
            "price_without_tax": float(self.module.price_without_tax)
        }
        assert fetch_mock.called

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_product_detail_for_course(self, mock, fetch_mock):  # pylint: disable=unused-argument
        """
        Test that product detail for courses works properly.
        """
        course_uuid = self.course.uuid
        module_uuid = self.module.uuid

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
        ), json={
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
        })
        fetch_mock.get("{base}v1/coursexs/{course_uuid}/modules/".format(
            base=FAKE_CCXCON_API,
            course_uuid=course_uuid
        ), json=[
            {
                "uuid": module_uuid,
                "title": ccxcon_module_title,
                "subchapters": subchapters,
                "course": "https://example.com/",
                "url": "https://example.com/"
            }
        ])

        resp = self.client.get(
            reverse("product-detail", kwargs={"qualified_id": self.course.qualified_id})
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
            "title": self.course.title,
            "description": self.course.description,
            "external_pk": course_uuid,
            "children": [
                {
                    "info": {
                        "title": ccxcon_module_title,
                        "subchapters": subchapters
                    },
                    "parent_upc": self.course.qualified_id,
                    "product_type": MODULE_PRODUCT_TYPE,
                    "title": self.module.title,
                    "description": "",
                    "external_pk": module_uuid,
                    "children": [],
                    "upc": self.module.qualified_id,
                    "price_without_tax": float(self.module.price_without_tax)
                }
            ],
            "upc": self.course.qualified_id,
            "price_without_tax": None
        }
        assert fetch_mock.called

    def test_product_not_available(self):
        """
        Test that product detail returns a 404 if the product is not available.
        """
        self.course.live = False
        self.course.save()

        resp = self.client.get(
            reverse("product-detail", kwargs={"qualified_id": self.course.qualified_id})
        )
        assert resp.status_code == 404, resp.content.decode('utf-8')

        resp = self.client.get(
            reverse("product-detail", kwargs={"qualified_id": self.module.qualified_id})
        )
        assert resp.status_code == 404, resp.content.decode('utf-8')

    def test_not_logged_in(self):
        """
        Test that product list and detail are only available to logged in users.
        """
        self.client.logout()
        resp = self.client.get(
            reverse("product-detail", kwargs={"qualified_id": self.module.qualified_id})
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
        module_uuid = self.module.uuid
        fetch_mock.get("{base}v1/coursexs/{course_uuid}/modules/{module_uuid}/".format(
            base=FAKE_CCXCON_API,
            course_uuid=self.course.uuid,
            module_uuid=module_uuid,
        ), status_code=500, json={})

        with self.assertRaises(Exception) as ex:
            self.client.get(
                reverse("product-detail", kwargs={"qualified_id": self.module.qualified_id})
            )
        assert "CCXCon returned a non 200 status code 500" in ex.exception.args[0]
        assert fetch_mock.called

        # Product list API does not read from CCXCon so it should be unaffected
        resp = self.client.get(reverse('product-list'))
        assert resp.status_code == 200
