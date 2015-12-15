"""
Test end to end django views.
"""

from __future__ import unicode_literals

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse


class TestViews(TestCase):
    """
    Test that the views work as expected.
    """
    def setUp(self):
        """Common test setup"""
        super(TestViews, self).setUp()
        self.client = Client()

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
