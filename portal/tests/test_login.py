"""
Tests for login and logout views
"""

from __future__ import unicode_literals
import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase


class LoginTests(TestCase):
    """
    Tests for login and logout views.
    """

    USERNAME = "user"
    PASSWORD = "pass"
    OTHER_USERNAME = "other_user"
    OTHER_PASSWORD = "other_pass"

    def is_authenticated(self, user):
        """Is user authenticated in self.client.session?"""
        # http://stackoverflow.com/questions/5660952/test-that-user-was-logged-in-successfully
        return (
            '_auth_user_id' in self.client.session and
            user.pk == int(self.client.session['_auth_user_id'])
        )

    def setUp(self):
        """Common test setup"""
        super(LoginTests, self).setUp()

        self.user = User.objects.create_user(
            username=self.USERNAME,
            password=self.PASSWORD,
        )
        self.other_user = User.objects.create_user(
            username=self.OTHER_USERNAME,
            password=self.OTHER_PASSWORD,
        )
        assert not self.is_authenticated(self.user)
        assert not self.is_authenticated(self.other_user)

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
