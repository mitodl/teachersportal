"""
Tests for registration REST endpoints
"""

from __future__ import unicode_literals
import json

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from six.moves.urllib.parse import quote_plus  # pylint: disable=import-error

from portal.tests.base import AuthenticationTestCase


class RegistrationTests(AuthenticationTestCase):
    """
    Tests for registration REST endpoints
    """

    def test_registration(self):
        """
        Test that an anonymous user can register successfully.
        """
        # No emails sent yet
        assert len(mail.outbox) == 0

        email = "testuser@mit.edu"
        redirect = "redirect with spaces"
        resp = self.client.post(
            reverse('register'),
            json.dumps({
                "full_name": "user",
                "password": "pass",
                "organization": "MIT",
                "email": email,
                "redirect": redirect
            }),
            content_type="application/json"
        )
        assert resp.status_code == 200, resp.content
        assert resp.content.decode('utf-8') == ""

        user = User.objects.get(email=email)
        assert not user.is_active

        # One registration email sent containing the token
        assert len(mail.outbox) == 1
        outbox = mail.outbox[0]
        url = "/activate/?token={token}&redirect={redirect}".format(
            token=quote_plus(user.userinfo.registration_token),
            redirect=quote_plus(redirect)
        )
        assert url in outbox.body
        assert len(outbox.to) == 1
        assert email in outbox.to
        assert settings.DEFAULT_FROM_EMAIL == outbox.from_email
        assert "Registration" in outbox.subject

    def test_missing_key(self):
        """
        Test that a missing key causes a 400 error.
        """
        for key in ("full_name", "password", "organization", "email"):
            data = {
                "full_name": "user",
                "password": "pass",
                "organization": "MIT",
                "email": "email",
                "redirect": "redirect",
            }
            del data[key]
            resp = self.client.post(
                reverse('register'),
                json.dumps(data),
                content_type="application/json"
            )
            assert resp.status_code == 400, resp.content
            assert "Missing key {key}".format(key=key) in resp.content.decode('utf-8')

    def test_empty_key(self):
        """
        Test that an empty key causes a 400 error.
        """
        for key in ("full_name", "password", "organization", "email"):
            data = {
                "full_name": "user",
                "password": "pass",
                "organization": "MIT",
                "email": "email",
                "redirect": "redirect",
            }
            data[key] = ""
            resp = self.client.post(
                reverse('register'),
                json.dumps(data),
                content_type="application/json"
            )
            assert resp.status_code == 400, resp.content
            assert "Empty value for {key}".format(key=key) in resp.content.decode('utf-8')

    def test_invalid_data(self):
        """
        Test that invalid data causes a 400 error.
        """
        resp = self.client.post(
            reverse('register'),
            "{",
            content_type="application/json"
        )
        assert resp.status_code == 400, resp.content
        assert "JSON parse error" in resp.content.decode('utf-8')

    def test_duplicate_email(self):
        """
        Test that a duplicate email causes a 400 error.
        """
        email = "testuser@mit.edu"
        resp = self.client.post(
            reverse('register'),
            json.dumps({
                "full_name": "first",
                "password": "first",
                "organization": "first",
                "email": email,
                "redirect": "first",
            }),
            content_type="application/json"
        )
        assert resp.status_code == 200, resp.content

        resp = self.client.post(
            reverse('register'),
            json.dumps({
                "full_name": "second",
                "password": "second",
                "organization": "second",
                "email": email,
                "redirect": "second",
            }),
            content_type="application/json"
        )
        assert resp.status_code == 400, resp.content
        assert "Email testuser@mit.edu is already in use" in resp.content.decode('utf-8')

    def test_user_already_exists(self):
        """
        Test that we can't reregister an existing user.
        """
        email = "testuser@mit.edu"
        User.objects.create_user(
            username=email,
            email=email,
            password="password"
        )
        email = "testuser@mit.edu"
        resp = self.client.post(
            reverse('register'),
            json.dumps({
                "full_name": "first",
                "password": "first",
                "organization": "first",
                "email": email,
                "redirect": "redirect",
            }),
            content_type="application/json"
        )
        assert resp.status_code == 400, resp.content
        assert "Email testuser@mit.edu is already in use" in resp.content.decode('utf-8')

    def test_user_logged_in(self):
        """
        Test that we block access if a user is logged in.
        """
        email = "other@email.com"
        User.objects.create_user(
            username=email,
            email=email,
            password="password"
        )
        self.client.login(username=email, password="password")

        email = "testuser@mit.edu"
        resp = self.client.post(
            reverse('register'),
            json.dumps({
                "full_name": "name",
                "password": "pass",
                "organization": "org",
                "email": email,
                "redirect": "redirect",
            }),
            content_type="application/json"
        )
        assert resp.status_code == 403, resp.content
