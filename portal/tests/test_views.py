"""
Test end to end django views.
"""

from __future__ import unicode_literals

from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.core.urlresolvers import reverse


class TestViews(TestCase):
    """
    Test that the views work as expected.
    """
    def setUp(self):
        """Common test setup"""
        super(TestViews, self).setUp()
        self.client = Client()

    def test_index_view(self):
        """Verify the index view is as expected"""
        response = self.client.get(reverse('portal-index'))
        self.assertContains(
            response,
            "8076/index_page.js",
            status_code=200
        )

    def test_oscar_view(self):
        """
        Verify that oscar is present
        """
        response = self.client.get("/oscar/")
        assert "oscar" in response.content.decode('utf-8')
        assert response.status_code == 200

        with override_settings(DEBUG=False):
            response = self.client.get("/oscar/")
            assert "oscar" not in response.content.decode('utf-8')
            assert response.status_code == 200
