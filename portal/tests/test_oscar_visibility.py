"""
Test oscar site visibility
"""

from __future__ import unicode_literals

from six.moves import reload_module

from django.test import TestCase, override_settings
import portal.urls


class OscarVisibilityTest(TestCase):
    """Test oscar site visibility"""

    @override_settings(PORTAL_OSCAR_VISIBLE=False)
    def test_invisible(self):
        """If OSCAR_VISIBLE is false we shouldn't see the site"""
        reload_module(portal.urls)
        resp = self.client.get("/oscar/")
        assert resp.status_code == 200
        assert "static/oscar" not in resp.content.decode('utf-8')

    @override_settings(PORTAL_OSCAR_VISIBLE=True)
    def test_visible(self):
        """If OSCAR_VISIBLE is true we should see the site"""
        reload_module(portal.urls)
        resp = self.client.get("/oscar/")
        assert resp.status_code == 200
        assert "static/oscar" in resp.content.decode('utf-8')

    def tearDown(self):
        """
        Make sure we reset portal.urls for other tests
        """
        reload_module(portal.urls)
