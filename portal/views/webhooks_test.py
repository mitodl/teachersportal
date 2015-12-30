"""
Tests for webhooks API.
"""

from __future__ import unicode_literals
from decimal import Decimal
import hashlib
import hmac
import json

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from oscar.apps.catalogue.models import Product
from oscar.apps.partner.models import Partner, StockRecord

from portal.util import (
    make_upc,
    COURSE_PRODUCT_TYPE,
    MODULE_PRODUCT_TYPE,
)
from portal.views.util import as_json


FAKE_SECRET = b'secret'


# pylint: disable=invalid-name, too-many-public-methods
@override_settings(CCXCON_WEBHOOKS_SECRET=FAKE_SECRET)
class WebhookTests(TestCase):
    """
    Tests for CCXCon webhooks.
    """

    COURSE_UUID1 = '2290f78f-10d0-4fbf-85e0-5e7a14fdc464'
    COURSE_UUID2 = 'cd29b564-e1f5-412f-a8af-dfee3df65840'
    MODULE_UUID1 = 'c3677c69-c2f8-4316-9376-41e245729808'
    MODULE_UUID2 = 'f65023cd-54f6-406b-81cf-f2fa37a10fba'

    # These characters are interrobangs to assert unicode support
    COURSE_TITLE1 = "Course's title 1\u203d"
    COURSE_TITLE2 = "Course's title 2"
    MODULE_TITLE1 = "Module's title 1\u203d"
    MODULE_TITLE2 = "Module's title 2"

    def setUp(self):
        """
        Create a user to use with django-oscar-api
        """
        self.user = User.objects.create(username='user', password='pass')
        self.client.login(username=self.user.username, password=self.user.password)

        # Create course and module
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.COURSE_TITLE1,
                'external_pk': self.COURSE_UUID1
            }
        })
        self.post_webhook({
            'action': 'update',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'title': self.MODULE_TITLE1,
                "external_pk": self.MODULE_UUID1,
                'subchapters': ["some json here"],
                'course_external_pk': self.COURSE_UUID1
            }
        })

    def post_webhook(self, data, expected_status=200, expected_errors=None):
        """
        Helper method to POST a message to webhook endpoint.
        """
        data_bytes = json.dumps(data)
        signature = hmac.new(FAKE_SECRET, data_bytes.encode('utf-8'), hashlib.sha1).hexdigest()

        # Only products marked is_available should show up in this list
        resp = self.client.get(reverse("product-list"))
        assert resp.status_code == 200, resp.content
        old_available = [product['external_pk'] for product in as_json(resp)]

        old_products = self.get_products()
        resp = self.client.post(
            reverse('webhooks-ccxcon'),
            data=data_bytes,
            content_type="application/json",
            HTTP_X_CCXCON_SIGNATURE=signature
        )
        assert resp.status_code == expected_status, resp.content

        product_api_resp = self.client.get(reverse("product-list"))
        assert product_api_resp.status_code == 200, product_api_resp.content
        available = [product['external_pk'] for product in as_json(product_api_resp)]
        # Make sure products marked as being available didn't change
        assert available == old_available

        if expected_status != 200:
            # Make sure nothing changed in case of failure
            assert old_products == self.get_products()

            # Note that this requires expected_errors to be specified if
            # expected_status is set.
            errors = json.loads(resp.content.decode('utf-8'))
            assert errors == expected_errors

    def get_products(self):  # pylint: disable=no-self-use
        """
        Returns list of products in oscar.

        Returns:
            list: List of products from database
        """
        return list(Product.objects.order_by('date_created'))

    def test_webhook_with_no_auth(self):
        """
        Test that we get a 403 if we post to the webhook endpoint without
        the right headers.
        """
        data = {
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.COURSE_TITLE2,
                'external_pk': self.COURSE_UUID2
            }
        }
        resp = self.client.post(
            reverse('webhooks-ccxcon'),
            data=json.dumps(data),
            content_type="application/json"
        )
        assert resp.status_code == 403, resp.content
        assert "Authentication credentials were not provided" in resp.content.decode('utf-8')

    def test_webhook_with_bad_auth(self):
        """
        Test that we get a 403 if we post to the webhook endpoint with invalid
        authentication.
        """
        data = {
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.COURSE_TITLE2,
                'external_pk': self.COURSE_UUID2
            }
        }
        # Signature is now for a different set of data and therefore invalid
        data_bytes = json.dumps(data) + " and something extra"
        signature = hmac.new(FAKE_SECRET, data_bytes.encode('utf-8'), hashlib.sha1).hexdigest()

        resp = self.client.post(
            reverse('webhooks-ccxcon'),
            data=json.dumps(data),
            content_type="application/json",
            HTTP_X_CCXCON_SIGNATURE=signature
        )
        assert resp.status_code == 403, resp.content
        assert "Authentication credentials were not provided" in resp.content.decode('utf-8')

    def test_add_course(self):
        """
        Test for creating a new course.
        """
        assert len(self.get_products()) == 2

        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.COURSE_TITLE2,
                'external_pk': self.COURSE_UUID2
            }
        })

        products = self.get_products()
        assert len(products) == 3
        assert products[2].title == self.COURSE_TITLE2
        assert products[2].upc == make_upc(COURSE_PRODUCT_TYPE, self.COURSE_UUID2)

    def test_update_course(self):
        """
        Test updating a course.
        """
        # Second time it should update course in place.
        new_title = "changed title"
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': new_title,
                'external_pk': self.COURSE_UUID1
            }
        })

        products = self.get_products()
        assert len(products) == 2
        assert products[0].title == new_title
        assert products[0].upc == make_upc(COURSE_PRODUCT_TYPE, self.COURSE_UUID1)

    def test_add_course_with_same_title(self):
        """Test adding a course with duplicate titles"""
        # When we change the external_pk it should create a new product.
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.COURSE_TITLE1,
                'external_pk': self.COURSE_UUID2
            }
        })

        products = self.get_products()
        assert len(products) == 3
        assert products[0].title == self.COURSE_TITLE1
        assert products[0].upc == make_upc(COURSE_PRODUCT_TYPE, self.COURSE_UUID1)
        assert products[2].title == self.COURSE_TITLE1
        assert products[2].upc == make_upc(COURSE_PRODUCT_TYPE, self.COURSE_UUID2)

    def test_create_module_with_blank_uuid(self):
        """
        Try creating a module with a blank UUID
        """
        self.post_webhook({
            'action': 'update',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'title': self.MODULE_TITLE2,
                'external_pk': '',
                'subchapters': [],
                'course_external_pk': self.COURSE_UUID1
            }
        }, expected_status=400, expected_errors=['Invalid external_pk'])

    def test_create_course_with_blank_uuid(self):
        """
        Try creating a course with a blank UUID
        """
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.COURSE_TITLE1,
                'external_pk': '',
            }
        }, expected_status=400, expected_errors=['Invalid external_pk'])

    def test_update_module_with_course_uuid(self):
        """Test update for type Module with Course UUID"""
        self.post_webhook({
            'action': 'update',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'title': self.COURSE_TITLE1,
                'external_pk': self.COURSE_UUID1,
                'course_external_pk': self.COURSE_UUID1
            }
        })

        # Since we allow UUIDs to be duplicate as long as they are of the same
        # product type, this should work fine.
        products = self.get_products()
        assert len(products) == 3
        assert products[2].upc == make_upc(MODULE_PRODUCT_TYPE, self.COURSE_UUID1)

    def test_update_course_with_module_uuid(self):
        """
        Try to update a course with a module uuid
        """
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.MODULE_TITLE1,
                'external_pk': self.MODULE_UUID1
            }
        })

        # Since we allow UUIDs to be duplicate as long as they are of the same
        # product type, this should work fine.
        products = self.get_products()
        assert len(products) == 3
        assert products[2].upc == make_upc(COURSE_PRODUCT_TYPE, self.MODULE_UUID1)

    def test_update_course_empty_title(self):
        """
        Try to set a course title to an empty string
        """
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': '',
                'external_pk': self.COURSE_UUID1
            }
        })

        products = self.get_products()
        assert len(products) == 2
        assert products[0].upc == make_upc(COURSE_PRODUCT_TYPE, self.COURSE_UUID1)
        assert products[0].title == ''

    def test_update_module_empty_title(self):
        """
        Try to set a module title to an empty string
        """
        self.post_webhook({
            'action': 'update',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'title': '',
                'external_pk': self.MODULE_UUID1,
                'course_external_pk': self.COURSE_UUID1,
                'subchapters': ""
            }
        })

        products = self.get_products()
        assert len(products) == 2
        assert products[1].upc == make_upc(MODULE_PRODUCT_TYPE, self.MODULE_UUID1)
        assert products[1].title == ''

    def test_delete_module_with_course_uuid(self):
        """
        Try to delete a module with a course uuid
        """
        self.post_webhook({
            'action': 'delete',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'external_pk': self.COURSE_UUID1
            }
        })
        # Unchanged
        assert len(self.get_products()) == 2

    def test_delete_course_with_module_uuid(self):
        """
        Try to delete a course with a module uuid
        """
        self.post_webhook({
            'action': 'delete',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'external_pk': self.MODULE_UUID1,
            }
        })
        # Unchanged
        assert len(self.get_products()) == 2

    def test_delete_course_with_missing_uuid(self):
        """
        Try deleting a course with a uuid that doesn't exist.
        """
        # Missing uuid should not cause an error but not do anything either
        self.post_webhook({
            'action': 'delete',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'external_pk': self.COURSE_UUID2
            }
        })
        assert len(self.get_products()) == 2

    def test_delete_course(self):
        """
        Test for deleting a course.
        """
        self.post_webhook({
            'action': 'delete',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'external_pk': self.COURSE_UUID1
            }
        })
        # We deleted the course which will cascade to module as well.
        assert len(self.get_products()) == 0

    def test_update_module_with_missing_course_uuid(self):
        """
        Try to update a module with missing course uuid
        """
        new_title = "new_title"
        self.post_webhook({
            'action': 'update',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'title': new_title,
                'external_pk': self.MODULE_UUID1,
                'subchapters': [],
                'course_external_pk': self.COURSE_UUID2
            }
        }, expected_status=400, expected_errors=["Invalid course_external_pk"])

    def test_update_module_with_another_course_uuid(self):
        """
        We shouldn't allow modules to change parents
        """
        self.post_webhook({
            'action': 'update',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'title': self.MODULE_TITLE1,
                'external_pk': self.MODULE_UUID1,
                'subchapters': [],
                'course_external_pk': self.COURSE_UUID2
            }
        }, expected_status=400, expected_errors=["Invalid course_external_pk"])

    def test_update_module(self):
        """
        Try updating a module (chapter).
        """
        new_title = "new title"
        self.post_webhook({
            'action': 'update',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'title': new_title,
                'external_pk': self.MODULE_UUID1,
                'subchapters': [],
                'course_external_pk': self.COURSE_UUID1
            }
        })

        # Should be one module and one course
        products = self.get_products()
        assert len(products) == 2
        assert products[1].upc == make_upc(MODULE_PRODUCT_TYPE, self.MODULE_UUID1)
        assert products[1].title == new_title

    def test_add_module(self):
        """Add a new module"""
        self.post_webhook({
            'action': 'update',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'title': self.MODULE_TITLE2,
                'external_pk': self.MODULE_UUID2,
                'subchapters': None,
                'course_external_pk': self.COURSE_UUID1
            }
        })
        products = self.get_products()
        assert len(products) == 3
        assert products[2].upc == make_upc(MODULE_PRODUCT_TYPE, self.MODULE_UUID2)
        assert products[2].title == self.MODULE_TITLE2

    def test_add_module_as_parent(self):
        """
        We shouldn't allow modules to be parents of other modules
        """
        self.post_webhook({
            'action': 'update',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'title': "title",
                'external_pk': self.MODULE_TITLE2,
                'subchapters': [],
                'course_external_pk': self.MODULE_UUID1
            }
        }, expected_status=400, expected_errors=['Invalid course_external_pk'])

    def test_child_parent(self):
        """
        Make sure course and module ownership is consistent with updates.
        """
        products = self.get_products()

        def parent_has_child(parent, child):
            """Assert parent/child relationship"""
            return (
                child.parent.upc == parent.upc and
                parent.parent is None
            )

        assert products[0].upc == make_upc(COURSE_PRODUCT_TYPE, self.COURSE_UUID1)
        assert products[1].upc == make_upc(MODULE_PRODUCT_TYPE, self.MODULE_UUID1)
        assert parent_has_child(products[0], products[1])

        # Make another course module pair
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.COURSE_TITLE2,
                'external_pk': self.COURSE_UUID2
            }
        })
        self.post_webhook({
            'action': 'update',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'title': self.MODULE_TITLE2,
                'external_pk': self.MODULE_UUID2,
                'subchapters': [],
                'course_external_pk': self.COURSE_UUID2
            }
        })

        products = self.get_products()
        assert len(products) == 4
        assert products[2].upc == make_upc(COURSE_PRODUCT_TYPE, self.COURSE_UUID2)
        assert products[3].upc == make_upc(MODULE_PRODUCT_TYPE, self.MODULE_UUID2)
        parent1, child1, parent2, child2 = products
        assert parent_has_child(parent1, child1)
        assert not parent_has_child(parent1, child2)
        assert not parent_has_child(parent2, child1)
        assert parent_has_child(parent2, child2)

    def test_course_becomes_parent(self):
        """
        Make sure Product status changes from STANDALONE to PARENT when a module is added.
        """
        # Create another course
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.COURSE_TITLE2,
                'external_pk': self.COURSE_UUID2
            }
        })
        products = self.get_products()
        assert products[2].upc == make_upc(COURSE_PRODUCT_TYPE, self.COURSE_UUID2)
        assert products[2].structure == Product.STANDALONE

        # Add module to course
        self.post_webhook({
            'action': 'update',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'title': self.MODULE_TITLE2,
                'external_pk': self.MODULE_UUID2,
                'subchapters': [],
                'course_external_pk': self.COURSE_UUID2
            }
        })
        products = self.get_products()
        assert products[2].upc == make_upc(COURSE_PRODUCT_TYPE, self.COURSE_UUID2)
        assert products[2].structure == Product.PARENT

    def test_change_parent(self):
        """
        Make sure a validation error is raised when we change the course_external_pk.
        """
        # Create another course
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.COURSE_TITLE2,
                'external_pk': self.COURSE_UUID2
            }
        })
        # Update module1 to point to course2
        self.post_webhook({
            'action': 'update',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'title': self.MODULE_TITLE1,
                'external_pk': self.MODULE_UUID1,
                'subchapters': [],
                'course_external_pk': self.COURSE_UUID2
            }
        }, expected_status=400, expected_errors=['Invalid course_external_pk'])

    def test_add_module_with_same_title(self):
        """
        Add a module with a duplicate title
        """
        self.post_webhook({
            'action': 'update',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'title': self.MODULE_TITLE1,
                'external_pk': self.MODULE_UUID2,
                'subchapters': [],
                'course_external_pk': self.COURSE_UUID1
            }
        })
        products = self.get_products()
        assert len(products) == 3
        assert products[2].upc == make_upc(MODULE_PRODUCT_TYPE, self.MODULE_UUID2)
        assert products[2].title == self.MODULE_TITLE1

    def test_delete_module_with_missing_uuid(self):
        """
        Missing uuid should not cause an error but not do anything either
        """
        self.post_webhook({
            'action': 'delete',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'external_pk': self.MODULE_UUID2,
            }
        })
        assert len(self.get_products()) == 2

    def test_delete_module(self):
        """
        Test for deleting a module.
        """
        self.post_webhook({
            'action': 'delete',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'external_pk': self.MODULE_UUID1,
            }
        })
        products = self.get_products()
        assert len(products) == 1
        assert products[0].upc == make_upc(COURSE_PRODUCT_TYPE, self.COURSE_UUID1)
        # Delete should change product type to standalone since it has no children anymore
        assert products[0].structure == Product.STANDALONE

    def test_invalid_type(self):
        """Test invalid type"""
        self.post_webhook({
            'action': 'update',
            'type': 'missing',
            'payload': {}
        }, expected_status=400, expected_errors=["No handler for type missing"])

    def test_missing_type(self):
        """Missing type"""
        self.post_webhook({
            'action': 'update',
            'payload': {
                'title': "title",
                'external_pk': "uuid"
            }
        }, expected_status=400, expected_errors=['Missing key type'])

    def test_invalid_action(self):
        """Invalid action"""
        for hook_type in (COURSE_PRODUCT_TYPE, MODULE_PRODUCT_TYPE):
            self.post_webhook({
                'action': 'missing',
                'type': hook_type,
                'payload': {
                    'title': "title",
                    'external_pk': "uuid"
                }
            }, expected_status=400, expected_errors=['Unknown action missing'])

    def test_missing_action(self):
        """Missing action"""
        for hook_type in (COURSE_PRODUCT_TYPE, MODULE_PRODUCT_TYPE):
            self.post_webhook({
                'type': hook_type,
                'payload': {
                    'title': "title",
                    'external_pk': "uuid"
                }
            }, expected_status=400, expected_errors=['Missing key action'])

    def test_payload_missing_title(self):
        """Payload missing title"""
        for hook_type in (COURSE_PRODUCT_TYPE, MODULE_PRODUCT_TYPE):
            self.post_webhook({
                'action': 'update',
                'type': hook_type,
                'payload': {
                    'external_pk': "uuid"
                }
            }, expected_status=400, expected_errors=['Missing key title'])

    def test_missing_payload(self):
        """Missing payload"""
        for hook_type in (COURSE_PRODUCT_TYPE, MODULE_PRODUCT_TYPE):
            self.post_webhook({
                'action': 'update',
                'type': hook_type
            }, expected_status=400, expected_errors=['Missing key payload'])

    def test_payload_invalid_type(self):
        """Payload is a string"""
        for hook_type in (COURSE_PRODUCT_TYPE, MODULE_PRODUCT_TYPE):
            self.post_webhook({
                'action': 'update',
                'type': hook_type,
                'payload': "{}"
            }, expected_status=400, expected_errors=['Invalid key string indices must be integers'])

    def test_missing_external_pk_on_delete(self):
        """Missing fields"""
        for hook_type in (COURSE_PRODUCT_TYPE, MODULE_PRODUCT_TYPE):
            self.post_webhook({
                'action': 'delete',
                'type': hook_type,
                'payload': {}
            }, expected_status=400, expected_errors=['Missing key external_pk'])

    def test_missing_payload_fields_for_course_update(self):
        """Missing fields for course update"""
        payload = {
            'title': self.COURSE_TITLE1,
            'external_pk': self.COURSE_UUID1
        }
        for key in payload.keys():
            payload_copy = dict(payload)
            del payload_copy[key]
            self.post_webhook({
                'action': 'update',
                'type': COURSE_PRODUCT_TYPE,
                'payload': payload_copy
            }, expected_errors=["Missing key {key}".format(key=key)], expected_status=400)

    def test_missing_payload_fields_for_module_update(self):
        """Missing fields for module update"""
        payload = {
            'title': self.COURSE_TITLE1,
            'external_pk': self.MODULE_UUID1,
            'course_external_pk': self.COURSE_UUID1
        }
        for key in payload.keys():
            payload_copy = dict(payload)
            del payload_copy[key]
            self.post_webhook({
                'action': 'update',
                'type': MODULE_PRODUCT_TYPE,
                'payload': payload_copy
            }, expected_errors=["Missing key {key}".format(key=key)], expected_status=400)

    def test_update_product_with_price(self):
        """
        Make sure we preserve price information on update.
        """
        module = Product.objects.filter(
            upc=make_upc(MODULE_PRODUCT_TYPE, self.MODULE_UUID1)
        ).first()

        # Add price
        new_price = Decimal('123.45')
        StockRecord.objects.create(
            product=module,
            partner=Partner.objects.get(name='edX'),
            partner_sku=module.upc,
            price_currency="$",
            price_excl_tax=new_price,
        )

        self.post_webhook({
            'action': 'update',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'title': self.MODULE_TITLE1,
                'external_pk': self.MODULE_UUID1,
                'subchapters': [],
                'course_external_pk': self.COURSE_UUID1
            }
        })
        assert len(self.get_products()) == 2
        assert module.stockrecords.count() == 1
        assert module.stockrecords.first().price_excl_tax == new_price
