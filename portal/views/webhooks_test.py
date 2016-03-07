"""
Tests for webhooks API.
"""

from __future__ import unicode_literals
import hashlib
import hmac
import json

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from portal.models import Course, Module
from portal.views.util import as_json


FAKE_SECRET = b'secret'
MODULE_PRODUCT_TYPE = "Module"
COURSE_PRODUCT_TYPE = "Course"


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

    INSTANCE = "http://example.com/1/"

    def setUp(self):
        """
        Create a user to use with these tests
        """
        credentials = {"username": 'user', "password": 'pass'}
        self.user = User.objects.create_user(**credentials)
        self.client.login(**credentials)

        # Create course and module
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.COURSE_TITLE1,
                'external_pk': self.COURSE_UUID1,
                'instance': self.INSTANCE,
                'course_id': 'course_id',
                'author_name': 'author_name',
                'overview': 'overview',
                'description': 'description',
                'image_url': 'image_url',
                'instructors': ['one', 'two', 'three'],
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

        # Only courses marked as available should show up in this list
        resp = self.client.get(reverse("course-list"))
        assert resp.status_code == 200, resp.content.decode('utf-8')
        old_available = [course['external_pk'] for course in as_json(resp)]

        old_courses = self.get_courses()
        old_modules = self.get_modules()
        resp = self.client.post(
            reverse('webhooks-ccxcon'),
            data=data_bytes,
            content_type="application/json",
            HTTP_X_CCXCON_SIGNATURE=signature
        )
        assert resp.status_code == expected_status, resp.content.decode('utf-8')

        course_api_resp = self.client.get(reverse("course-list"))
        assert course_api_resp.status_code == 200, course_api_resp.content
        available = [course['external_pk'] for course in as_json(course_api_resp)]
        # Make sure we didn't mark anything new as being live
        assert available == old_available

        if expected_status != 200:
            # Make sure nothing changed in case of failure
            assert old_courses == self.get_courses()
            assert old_modules == self.get_modules()

            # Note that this requires expected_errors to be specified if
            # expected_status is set.
            errors = json.loads(resp.content.decode('utf-8'))
            assert errors == expected_errors

    def get_courses(self):  # pylint: disable=no-self-use
        """
        Returns list of courses in order of creation date.

        Returns:
            list: List of courses from database
        """
        return list(Course.objects.all())

    def get_modules(self):  # pylint: disable=no-self-use
        """
        Returns list of modules in order of creation date.

        Returns:
            list: List of courses from database
        """
        return list(Module.objects.all())

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
                'external_pk': self.COURSE_UUID2,
                'instance': self.INSTANCE,
                'course_id': 'course_id',
                'author_name': 'author_name',
                'overview': 'overview',
                'description': 'description',
                'image_url': 'image_url',
                'instructors': ['one', 'two', 'three'],
            }
        }
        resp = self.client.post(
            reverse('webhooks-ccxcon'),
            data=json.dumps(data),
            content_type="application/json"
        )
        assert resp.status_code == 403, resp.content.decode('utf-8')
        assert "You do not have permission to perform this action." in resp.content.decode('utf-8')

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
                'external_pk': self.COURSE_UUID2,
                'instance': self.INSTANCE,
                'course_id': 'course_id',
                'author_name': 'author_name',
                'overview': 'overview',
                'description': 'description',
                'image_url': 'image_url',
                'instructors': ['one', 'two', 'three'],
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
        assert resp.status_code == 403, resp.content.decode('utf-8')
        assert "You do not have permission to perform this action." in resp.content.decode('utf-8')

    def test_add_course(self):
        """
        Test for creating a new course.
        """
        course_count = len(self.get_courses())
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.COURSE_TITLE2,
                'external_pk': self.COURSE_UUID2,
                'instance': self.INSTANCE,
                'course_id': 'course_id',
                'author_name': 'author_name',
                'overview': 'overview',
                'description': 'description',
                'image_url': 'image_url',
                'instructors': ['one', 'two', 'three'],
            }
        })

        courses = self.get_courses()
        assert len(courses) == course_count + 1
        course = courses[-1]
        assert course.title == self.COURSE_TITLE2
        assert course.uuid == self.COURSE_UUID2
        assert course.instance.instance_url == self.INSTANCE
        assert course.course_id == 'course_id'
        assert course.author_name == 'author_name'
        assert course.overview == 'overview'
        assert course.description == 'description'
        assert course.image_url == 'image_url'
        assert course.instructors == ['one', 'two', 'three']

    def test_update_course(self):
        """
        Test updating a course.
        """
        course_count = len(self.get_courses())
        # Second time it should update course in place.
        new_title = "changed title"
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': new_title,
                'external_pk': self.COURSE_UUID1,
                'instance': self.INSTANCE,
                'course_id': 'new course_id',
                'author_name': 'new author_name',
                'overview': 'new overview',
                'description': 'new description',
                'image_url': 'new image_url',
                'instructors': ['four'],
            }
        })

        courses = self.get_courses()
        assert len(courses) == course_count
        course = courses[0]
        assert course.title == new_title
        assert course.uuid == self.COURSE_UUID1
        assert course.instance.instance_url == self.INSTANCE
        assert course.course_id == 'new course_id'
        assert course.author_name == 'new author_name'
        assert course.overview == 'new overview'
        assert course.description == 'new description'
        assert course.image_url == 'new image_url'
        assert course.instructors == ['four']

    def test_update_course_null(self):
        """
        Test updating a course with null values.
        """
        course_count = len(self.get_courses())
        # Second time it should update course in place.
        new_title = "changed title"
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': new_title,
                'external_pk': self.COURSE_UUID1,
                'instance': self.INSTANCE,
                'course_id': None,
                'author_name': None,
                'overview': None,
                'description': None,
                'image_url': None,
                'instructors': None,
            }
        })

        courses = self.get_courses()
        assert len(courses) == course_count
        course = courses[0]
        assert course.title == new_title
        assert course.uuid == self.COURSE_UUID1
        assert course.instance.instance_url == self.INSTANCE
        assert course.course_id is None
        assert course.author_name is None
        assert course.overview is None
        assert course.description is None
        assert course.image_url is None
        assert course.instructors is None

    def test_add_course_with_same_title(self):
        """Test adding a course with duplicate titles"""
        course_count = len(self.get_courses())
        # When we change the external_pk it should create a new course.
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.COURSE_TITLE1,
                'external_pk': self.COURSE_UUID2,
                'instance': self.INSTANCE,
                'course_id': 'course_id',
                'author_name': 'author_name',
                'overview': 'overview',
                'description': 'description',
                'image_url': 'image_url',
                'instructors': ['one', 'two', 'three'],
            }
        })

        courses = self.get_courses()
        assert len(courses) == course_count + 1
        assert courses[-1].title == self.COURSE_TITLE1
        assert courses[-1].uuid == self.COURSE_UUID2

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
                'instance': self.INSTANCE,
                'course_id': 'course_id',
                'author_name': 'author_name',
                'overview': 'overview',
                'description': 'description',
                'image_url': 'image_url',
                'instructors': ['one', 'two', 'three'],
            }
        }, expected_status=400, expected_errors=['Invalid external_pk'])

    def test_update_module_with_course_uuid(self):
        """Test update for type Module with Course UUID"""
        module_count = len(self.get_modules())
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
        modules = self.get_modules()
        assert len(modules) == module_count + 1
        assert modules[-1].uuid == self.COURSE_UUID1

    def test_update_course_with_module_uuid(self):
        """
        Try to update a course with a module uuid
        """
        course_count = len(self.get_courses())
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.MODULE_TITLE1,
                'external_pk': self.MODULE_UUID1,
                'instance': self.INSTANCE,
                'course_id': 'course_id',
                'author_name': 'author_name',
                'overview': 'overview',
                'description': 'description',
                'image_url': 'image_url',
                'instructors': ['one', 'two', 'three'],
            }
        })

        # Since we allow UUIDs to be duplicate as long as they are of the same
        # product type, this should work fine.
        courses = self.get_courses()
        assert len(courses) == course_count + 1
        assert courses[-1].uuid == self.MODULE_UUID1

    def test_update_course_empty_title(self):
        """
        Try to set a course title to an empty string
        """
        course_count = len(self.get_courses())
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': '',
                'external_pk': self.COURSE_UUID1,
                'instance': self.INSTANCE,
                'course_id': 'course_id',
                'author_name': 'author_name',
                'overview': 'overview',
                'description': 'description',
                'image_url': 'image_url',
                'instructors': ['one', 'two', 'three'],
            }
        })

        courses = self.get_courses()
        assert len(courses) == course_count
        assert courses[0].uuid == self.COURSE_UUID1
        assert courses[0].title == ''

    def test_update_module_empty_title(self):
        """
        Try to set a module title to an empty string
        """
        module_count = len(self.get_modules())
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

        modules = self.get_modules()
        assert len(modules) == module_count
        assert modules[0].uuid == self.MODULE_UUID1
        assert modules[0].title == ''

    def test_delete_module_with_course_uuid(self):
        """
        Try to delete a module with a course uuid
        """
        module_count = len(self.get_modules())
        self.post_webhook({
            'action': 'delete',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'external_pk': self.COURSE_UUID1,
            }
        })
        # Unchanged
        assert len(self.get_modules()) == module_count

    def test_delete_course_with_module_uuid(self):
        """
        Try to delete a course with a module uuid
        """
        course_count = len(self.get_courses())
        self.post_webhook({
            'action': 'delete',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'external_pk': self.MODULE_UUID1,
            }
        })
        # Unchanged
        assert len(self.get_courses()) == course_count

    def test_delete_course_with_missing_uuid(self):
        """
        Try deleting a course with a uuid that doesn't exist.
        """
        course_count = len(self.get_courses())
        # Missing uuid should not cause an error but not do anything either
        self.post_webhook({
            'action': 'delete',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'external_pk': self.COURSE_UUID2
            }
        })
        assert len(self.get_courses()) == course_count

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
        assert len(self.get_courses()) == 0
        assert len(self.get_modules()) == 0

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
        modules = self.get_modules()
        module_count = len(modules)
        price_without_tax = modules[0].price_without_tax
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

        modules = self.get_modules()
        assert len(modules) == module_count
        assert modules[0].uuid == self.MODULE_UUID1
        assert modules[0].title == new_title

        # Price was not affected by update
        assert modules[0].price_without_tax == price_without_tax

    def test_add_module(self):
        """Add a new module"""
        module_count = len(self.get_modules())
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
        modules = self.get_modules()
        assert len(modules) == module_count + 1
        assert modules[-1].uuid == self.MODULE_UUID2
        assert modules[-1].title == self.MODULE_TITLE2

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
        courses = self.get_courses()
        modules = self.get_modules()

        assert courses[0].uuid == self.COURSE_UUID1
        assert modules[0].uuid == self.MODULE_UUID1
        assert courses[0] == modules[0].course

        course_count = len(courses)
        module_count = len(modules)

        # Make another course module pair
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.COURSE_TITLE2,
                'external_pk': self.COURSE_UUID2,
                'instance': self.INSTANCE,
                'course_id': 'course_id',
                'author_name': 'author_name',
                'overview': 'overview',
                'description': 'description',
                'image_url': 'image_url',
                'instructors': ['one', 'two', 'three'],
            }
        })
        courses = self.get_courses()
        assert len(courses) == course_count + 1

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
        modules = self.get_modules()
        assert len(modules) == module_count + 1

        assert courses[-1].uuid == self.COURSE_UUID2
        assert modules[-1].uuid == self.MODULE_UUID2
        course1, course2 = courses
        module1, module2 = modules
        assert module1.course == course1
        assert module2.course != course1
        assert module1.course != course2
        assert module2.course == course2

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
                'external_pk': self.COURSE_UUID2,
                'instance': self.INSTANCE,
                'course_id': 'course_id',
                'author_name': 'author_name',
                'overview': 'overview',
                'description': 'description',
                'image_url': 'image_url',
                'instructors': ['one', 'two', 'three'],
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
        module_count = len(self.get_modules())
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
        modules = self.get_modules()
        assert len(modules) == module_count + 1
        assert modules[-1].uuid == self.MODULE_UUID2
        assert modules[-1].title == self.MODULE_TITLE1

    def test_delete_module_with_missing_uuid(self):
        """
        Missing uuid should not cause an error but not do anything either
        """
        module_count = len(self.get_modules())
        self.post_webhook({
            'action': 'delete',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'external_pk': self.MODULE_UUID2,
            }
        })
        assert len(self.get_modules()) == module_count

    def test_delete_module(self):
        """
        Test for deleting a module.
        """
        course_count = len(self.get_courses())
        self.post_webhook({
            'action': 'delete',
            'type': MODULE_PRODUCT_TYPE,
            'payload': {
                'external_pk': self.MODULE_UUID1,
            }
        })
        courses = self.get_courses()
        modules = self.get_modules()
        # Courses are not affected
        assert len(courses) == course_count
        assert len(modules) == 0

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
                'external_pk': "uuid",
                'instance': self.INSTANCE
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
                    'external_pk': "uuid",
                    'instance': self.INSTANCE
                }
            }, expected_status=400, expected_errors=['Unknown action missing'])

    def test_missing_action(self):
        """Missing action"""
        for hook_type in (COURSE_PRODUCT_TYPE, MODULE_PRODUCT_TYPE):
            self.post_webhook({
                'type': hook_type,
                'payload': {
                    'title': "title",
                    'external_pk': "uuid",
                    'instance': self.INSTANCE
                }
            }, expected_status=400, expected_errors=['Missing key action'])

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

    def test_invalid_json_for_delete(self):
        """Invalid json for delete"""
        for hook_type in (COURSE_PRODUCT_TYPE, MODULE_PRODUCT_TYPE):
            self.post_webhook({
                'action': 'delete',
                'type': hook_type,
                'payload': None
            }, expected_errors=["Invalid value for payload"], expected_status=400)

    def test_missing_payload_fields_for_course_update(self):
        """Missing fields for course update"""
        payload = {
            'title': self.COURSE_TITLE1,
            'external_pk': self.COURSE_UUID1,
            'instance': self.INSTANCE,
            'course_id': 'course_id',
            'author_name': 'author_name',
            'overview': 'overview',
            'description': 'description',
            'image_url': 'image_url',
            'instructors': ['one', 'two', 'three'],
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

    def test_course_instance_cant_change(self):
        """Assert that instance can't change"""
        self.post_webhook({
            'action': 'update',
            'type': COURSE_PRODUCT_TYPE,
            'payload': {
                'title': self.COURSE_TITLE1,
                'external_pk': self.COURSE_UUID1,
                'instance': '{}/update'.format(self.INSTANCE),
                'course_id': 'course_id',
                'author_name': 'author_name',
                'overview': 'overview',
                'description': 'description',
                'image_url': 'image_url',
                'instructors': ['one', 'two', 'three'],
            }
        }, expected_status=400, expected_errors=['Instance cannot be changed'])

    def test_invalid_instance_type(self):
        """Assert that instance must be a non-empty string"""
        for instance in ('', None, 3, [], {}):
            self.post_webhook(
                {
                    'action': 'update',
                    'type': COURSE_PRODUCT_TYPE,
                    'payload': {
                        'title': self.COURSE_TITLE1,
                        'external_pk': self.COURSE_UUID1,
                        'instance': instance,
                        'course_id': 'course_id',
                        'author_name': 'author_name',
                        'overview': 'overview',
                        'description': 'description',
                        'image_url': 'image_url',
                        'instructors': ['one', 'two', 'three'],
                    }
                },
                expected_status=400,
                expected_errors=['Instance must be a non-empty string']
            )
