"""
Test end to end django views.
"""

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from portal.models import UserInfo


class TestViews(TestCase):
    """
    Test that the views work as expected.
    """
    def test_webpack_url(self):
        """Verify that webpack tag behaves correctly in production"""
        for debug, expected_url in [
                (True, "foo_server/index_page.js"),
                (False, "bundles/index_page.js")
        ]:
            with self.settings(
                DEBUG=debug,
                USE_WEBPACK_DEV_SERVER=True,
                WEBPACK_SERVER_URL="foo_server"
            ):
                response = self.client.get(reverse('portal-index'))
                self.assertContains(
                    response,
                    expected_url,
                    status_code=200
                )

    def test_no_userinfo_still_email(self):
        """
        If there is no userinfo object, it should still show the email.
        """
        User.objects.create_user(
            username='user',
            password='pass',
            email='darth@vad.er',
        )
        assert self.client.login(username='user', password='pass')

        response = self.client.get(reverse('portal-index'))
        self.assertContains(
            response,
            '''email": "darth@vad.er"''',
            msg_prefix=response.content.decode('utf-8')
        )

    def test_empty_name_no_user(self):
        """
        If there is no userinfo object, it should still render the homepage
        appropriately.
        """
        user = User.objects.create(username='test')
        user.set_password('asdf')
        self.client.login(username=user.username, password='asdf')

        response = self.client.get(reverse('portal-index'))
        self.assertContains(
            response,
            '''name": ""'''
        )

    def test_name_read_properly(self):
        """
        The name should show up in the javascript embedded in the HTML.
        """
        user = User.objects.create_user(username='test', password='asdf')
        UserInfo.objects.create(user=user, full_name="userinfoname")
        self.client.login(username=user.username, password='asdf')
        response = self.client.get(reverse('portal-index'))
        self.assertContains(
            response,
            '''name": "userinfoname"'''
        )
