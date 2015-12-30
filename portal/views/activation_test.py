"""
Activation tests
"""
from __future__ import unicode_literals

import json

from django.core.urlresolvers import reverse

from portal.views.base import AuthenticationTestCase


class ActivationTests(AuthenticationTestCase):
    """
    Tests for user activation
    """

    def test_activate(self):
        """
        Test that a user can activate their account by POSTing to endpoint.
        """
        resp = self.client.post(
            reverse('activate'),
            json.dumps({
                "token": self.inactive_user.userinfo.registration_token
            }),
            content_type="application/json"
        )
        assert resp.status_code == 200, resp.content
        self.inactive_user.refresh_from_db()
        assert self.inactive_user.is_active
        # User is not logged in automatically just by clicking the link
        assert not self.is_authenticated(self.inactive_user)

    def test_already_activated(self):
        """
        Test that user can activate twice and it has the same effect as if
        they only did it once.
        """
        # Activate token again
        resp = self.client.post(
            reverse('activate'),
            json.dumps({
                "token": self.user.userinfo.registration_token
            }),
            content_type="application/json"
        )
        assert resp.status_code == 200, resp.content
        assert self.user.is_active
        assert not self.is_authenticated(self.user)

    def test_logged_in(self):
        """
        Test that we block access if a user is logged in
        """
        self.client.login(username=self.USERNAME, password=self.PASSWORD)

        resp = self.client.post(
            reverse('activate'),
            json.dumps({
                "token": self.user.userinfo.registration_token
            }),
            content_type="application/json"
        )
        assert resp.status_code == 403, resp.content

    def test_invalid_json(self):
        """
        Test that a 400 is returned on invalid JSON.
        """
        resp = self.client.post(
            reverse('activate'),
            "{",
            content_type="application/json"
        )
        assert resp.status_code == 400, resp.content
        assert "JSON parse error" in resp.content.decode('utf-8')

    def test_missing_token(self):
        """
        Test that a 400 is returned missing token.
        """
        resp = self.client.post(
            reverse('activate'),
            json.dumps({
            }),
            content_type="application/json"
        )
        assert resp.status_code == 400, resp.content
        assert "Missing key token" in resp.content.decode('utf-8')

    def test_empty_token(self):
        """
        Test that a 400 is returned for empty tokens. Empty tokens shouldn't
        match anything anyway but just in case we'll error on this input.
        """
        resp = self.client.post(
            reverse('activate'),
            json.dumps({
                "token": ""
            }),
            content_type="application/json"
        )
        assert resp.status_code == 400, resp.content
        assert "token is empty" in resp.content.decode('utf-8')
