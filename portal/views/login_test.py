"""
Tests for login and logout views
"""

from __future__ import unicode_literals
import json

from django.core.urlresolvers import reverse

from portal.views.base import AuthenticationTestCase


class LoginTests(AuthenticationTestCase):
    """
    Tests for login and logout views.
    """

    def test_login_get(self):
        """Make sure that GET is not allowed"""
        resp = self.client.get(reverse('login'))
        assert resp.status_code == 405

    def test_login_success(self):
        """
        Verify login endpoint can successfully authenticate users.
        """
        resp = self.client.post(
            reverse('login'),
            json.dumps({
                "username": self.USERNAME,
                "password": self.PASSWORD,
            }),
            content_type="application/json"
        )
        assert resp.status_code == 200, resp.content
        assert self.is_authenticated(self.user)
        assert not self.is_authenticated(self.other_user)

    def test_login_with_bad_password(self):
        """
        Verify authentication fails if password doesn't match.
        """
        resp = self.client.post(
            reverse('login'),
            json.dumps({
                "username": self.USERNAME,
                "password": "",
            }),
            content_type="application/json"
        )
        assert resp.status_code == 403, resp.content
        assert not self.is_authenticated(self.user)

    def test_login_with_bad_username(self):
        """
        Verify authentication fails if username doesn't match.
        """
        resp = self.client.post(
            reverse('login'),
            json.dumps({
                "username": "",
                "password": self.PASSWORD,
            }),
            content_type="application/json"
        )
        assert resp.status_code == 403, resp.content
        assert not self.is_authenticated(self.user)

    def test_login_missing_username(self):
        """
        Make sure we return a 400 for a missing username instead of a KeyError.
        """
        resp = self.client.post(
            reverse('login'),
            json.dumps({
                "password": "pass",
            }),
            content_type="application/json"
        )
        assert resp.status_code == 400, resp.content
        assert not self.is_authenticated(self.user)

    def test_login_missing_password(self):
        """
        Make sure we return a 400 for a missing password instead of a KeyError.
        """
        resp = self.client.post(
            reverse('login'),
            json.dumps({
                "password": "pass",
            }),
            content_type="application/json"
        )
        assert resp.status_code == 400, resp.content
        assert not self.is_authenticated(self.user)

    def test_login_not_an_object(self):
        """
        Make sure we return a 400 for invalid JSON instead of a TypeError.
        """
        resp = self.client.post(
            reverse('login'),
            "{",
            content_type="application/json"
        )
        assert resp.status_code == 400, resp.content
        assert not self.is_authenticated(self.user)

    def test_logout(self):
        """
        Assert that logout works correctly.
        """
        assert not self.is_authenticated(self.user)
        resp = self.client.post(
            reverse('login'),
            json.dumps({
                "username": self.USERNAME,
                "password": self.PASSWORD,
            }),
            content_type="application/json"
        )
        assert resp.status_code == 200, resp.content
        assert self.is_authenticated(self.user)
        assert not self.is_authenticated(self.other_user)

        # Now logout the logged in user.
        resp = self.client.post(reverse('logout'))
        assert resp.status_code == 200, resp.content
        assert not self.is_authenticated(self.user)
        assert not self.is_authenticated(self.other_user)

    def test_anonymous_logout(self):
        """
        If the user logs out when not logged in, endpoint should not do anything
        and return a 200.
        """
        resp = self.client.post(reverse('logout'))
        assert resp.status_code == 200, resp.content
        assert not self.is_authenticated(self.user)
        assert not self.is_authenticated(self.other_user)
