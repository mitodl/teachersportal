"""
Tests for webhooks API.
"""
# pylint: disable=no-self-use,unused-argument
from __future__ import unicode_literals
import hashlib
import hmac
import json
from copy import deepcopy

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from mock import patch
from rest_framework.exceptions import ValidationError


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
