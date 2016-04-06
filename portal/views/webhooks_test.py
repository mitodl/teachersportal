"""
Tests for webhooks API.
"""
# pylint: disable=no-self-use,unused-argument
from __future__ import unicode_literals
from copy import deepcopy
import hashlib
import hmac
import json
from mock import patch

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework.exceptions import ValidationError
from portal.factories import UserFactory
from portal.models import Course


FAKE_SECRET = b'secret'


@patch('portal.views.webhooks.webhooks', autospec=True)
@override_settings(CCXCON_WEBHOOKS_SECRET=FAKE_SECRET)
class WebhookViewTests(TestCase):
    """
    Tests for the webhook views
    """
    def setUp(self):
        credentials = {"username": 'user', "password": 'pass'}
        self.user = User.objects.create_user(**credentials)
        self.client.login(**credentials)

    def _sign_send_payload(self, data, signature=None):
        data_bytes = json.dumps(data)
        if not signature:
            signature = hmac.new(
                FAKE_SECRET,
                data_bytes.encode('utf-8'),
                hashlib.sha1
            ).hexdigest()

        return self.client.post(
            reverse('webhooks-ccxcon'),
            data=data_bytes,
            content_type="application/json",
            HTTP_X_CCXCON_SIGNATURE=signature,
        )

    def test_checks_hmac_validity(self, wh_mock):
        """Test HMAC validity"""
        data = {
            'action': 'update',
            'type': 'course',
            'payload': {}
        }
        resp = self._sign_send_payload(data, signature='asdf')
        assert resp.status_code == 403

    def test_proper_payload_structure(self, wh_mock):
        """Errors on invalid payload"""
        data = {
            'action': 'update',
            'type': 'course',
            'payload': {}
        }
        for key in data.keys():
            dupe_data = deepcopy(data)
            del dupe_data[key]
            resp = self._sign_send_payload(dupe_data)
            assert resp.status_code == 400

    def test_errors_on_invalid_action(self, wh_mock):
        """Error on invalid action"""
        data = {
            'action': 'update',
            'type': 'blammo',
            'payload': {}
        }
        resp = self._sign_send_payload(data)
        assert resp.status_code == 400

    def test_200_status_on_success(self, wh_mock):
        """200 on success"""
        data = {
            'action': 'update',
            'type': 'course',
            'payload': {}
        }
        resp = self._sign_send_payload(data)
        assert resp.status_code == 200, resp.content.decode('utf-8')

    def test_calls_hook_on_success(self, wh_mock):
        """Calls hooks with proper args."""
        hook = wh_mock.course
        data = {
            'action': 'update',
            'type': 'course',
            'payload': {'a': 1},
        }
        self._sign_send_payload(data)
        assert hook.called
        hook.assert_called_with('update', {'a': 1})

    def test_validation_error_raises(self, wh_mock):
        """
        If there's a validation error, the error message is in the response
        """
        wh_mock.course.side_effect = ValidationError("Message Here")
        data = {
            'action': 'update',
            'type': 'course',
            'payload': {'a': 1},
        }
        resp = self._sign_send_payload(data)

        assert resp.status_code == 400
        assert 'Message Here' in resp.content.decode('utf-8')


@patch('portal.views.webhooks.module_population', autospec=True)
class EdxWebhooksTest(TestCase):
    """Tests for Edx webhook"""
    def setUp(self):
        self.user = UserFactory.create(profile__edx_instance__instance_url='https://example.org/')
        self.client.force_login(self.user)

    def test_happy_case(self, mod_pop):
        """Everything went according to plan"""
        self.client.post(reverse('webhooks-edx'), {
            "title": "title1",
            "author_name": "author1",
            "overview": "overview1",
            "description": "description1",
            "course_id": 'some-course-id',
            "image_url": "/234.jpg",
        })
        course = Course.objects.all()[0]
        assert course.title == 'title1'
        assert course.author_name == 'author1'
        assert course.overview == 'overview1'
        assert course.description == 'description1'
        assert course.edx_course_id == 'some-course-id'
        assert course.image_url == 'https://example.org/234.jpg'

    def test_calls_module_population(self, mod_pop):
        """
        Ensure we're calling out module population task.
        """
        resp = self.client.post(reverse('webhooks-edx'), {
            "title": "title1",
            "author_name": "author1",
            "overview": "overview1",
            "description": "description1",
            "course_id": 'some-course-id',
            "image_url": "/234.jpg",
        })
        assert resp.status_code == 201
        resp = self.client.post(reverse('webhooks-edx'), {
            "title": "title1",
            "author_name": "author1",
            "overview": "overview1",
            "description": "description1",
            "course_id": 'some-course-id',
            "image_url": "/2345.jpg",  # different
        })

        assert mod_pop.delay.call_count == 2
        call1, call2 = mod_pop.delay.call_args_list
        assert call1[0] == call2[0] == ('some-course-id',)
        assert resp.status_code == 200

    def test_user_has_instance(self, mod_pop):
        """User must have a backing edx instance"""
        user = UserFactory.create(profile__edx_instance=None)
        self.client.force_login(user)

        resp = self.client.post(reverse('webhooks-edx'), {
            "title": "title1",
            "author_name": "author1",
            "overview": "overview1",
            "description": "description1",
            "course_id": 'some-course-id',
            # NOTE: Specifically excluded the edx_instance key
            "instructors": [
                "861e87a0803e436b989cb62d5e672c5f",
                "961e87a0803e436b989cb62d5e672c5f"
            ]
        })

        content = resp.content.decode('utf-8')
        assert resp.status_code == 400, content
        assert 'associated edx_instance' in content

    def test_image_required(self, mod_pop):
        """Image is required"""
        resp = self.client.post(reverse('webhooks-edx'), {
            "title": "title1",
            "author_name": "author1",
            "overview": "overview1",
            "description": "description1",
            "course_id": 'some-course-id',
            # "edx_instance": "",
            "instructors": [
                "861e87a0803e436b989cb62d5e672c5f",
                "961e87a0803e436b989cb62d5e672c5f"
            ]
        })

        content = resp.content.decode('utf-8')
        assert resp.status_code == 400, content
        assert 'specify an image_url' in content

    def test_edx_instance_applied(self, mod_pop):
        """
        edx_instance applied automatically.
        """
        resp = self.client.post(reverse('webhooks-edx'), {
            "title": "title1",
            "author_name": "author1",
            "overview": "overview1",
            "description": "description1",
            "image_url": "http://example.com/1.jpg",
            "course_id": 'some-course-id',
            # "edx_instance": "",
            "instructors": [
                "861e87a0803e436b989cb62d5e672c5f",
                "961e87a0803e436b989cb62d5e672c5f"
            ]
        })
        assert resp.status_code == 201, resp.content.decode('utf-8')
        assert Course.objects.all()[0].instance.instance_url == 'https://example.org/'

    def test_duplicate_post_updates(self, mod_pop):
        """
        If we post twice with the same course_id, it should trigger an update.
        """
        resp = self.client.post(reverse('webhooks-edx'), {
            "title": "title1",
            "author_name": "author1",
            "overview": "overview1",
            "description": "description1",
            "course_id": 'some-course-id',
            "image_url": "/234.jpg",
        })
        self.assertEqual(resp.status_code, 201, resp.content)
        resp = self.client.post(reverse('webhooks-edx'), {
            "title": "title1",
            "author_name": "author1",
            "overview": "overview1",
            "description": "description1",
            "course_id": 'some-course-id',
            "image_url": "/2345.jpg",  # different
        })
        self.assertEqual(resp.status_code, 200, resp.content)
        assert Course.objects.count() == 1
        assert Course.objects.all()[0].image_url == 'https://example.org/2345.jpg'
