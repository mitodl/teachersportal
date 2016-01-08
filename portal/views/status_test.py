"""
Tests for the status API
"""
from __future__ import unicode_literals

from copy import deepcopy
import json
import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import Client
from django.test.testcases import TestCase
from django.test.utils import override_settings

log = logging.getLogger(__name__)

HTTP_OK = 200
NOT_FOUND = 404
SERVICE_UNAVAILABLE = 503


@override_settings(STATUS_TOKEN="xyz")
class StatusTests(TestCase):
    """Test output of status page."""

    def setUp(self):
        """
        Set up client and remember settings for PostgreSQL, Redis,
        and Elasticsearch. Changes made to django.conf.settings during
        tests persist beyond the test scope, so if they are changed
        we need to restore them.
        """

        # Create test client.
        self.client = Client()
        self.url = reverse("status")
        super(StatusTests, self).setUp()

    def get(self, expected_status=HTTP_OK):
        """Get the page."""
        resp = self.client.get(self.url, data={"token": settings.STATUS_TOKEN})
        assert resp.status_code == expected_status
        if expected_status != NOT_FOUND:
            return json.loads(resp.content.decode('utf-8'))

    def test_view(self):
        """Get normally."""
        resp = self.get()
        assert resp["postgresql"]["status"] == "up"

    def test_no_settings(self):
        """Missing settings."""
        databases = settings.DATABASES
        try:
            del settings.DATABASES
            resp = self.get()
            assert resp['postgresql']['status'] == "no config found"
        finally:
            settings.DATABASES = databases

    def test_broken_settings(self):
        """Settings that couldn't possibly work."""
        junk = " not a chance "
        databases = deepcopy(settings.DATABASES)
        databases['default'] = junk
        with self.settings(
            DATABASES=databases,
        ):
            resp = self.get(expected_status=SERVICE_UNAVAILABLE)
            assert resp['postgresql']["status"] == "down"

    def test_invalid_settings(self):
        """
        Settings that look right, but aren't (if service is actually down).
        """
        databases = deepcopy(settings.DATABASES)
        databases["default"]["HOST"] = "monkey"
        with self.settings(
            DATABASES=databases,
        ):
            resp = self.get(expected_status=SERVICE_UNAVAILABLE)
            assert resp["postgresql"]['status'] == 'down'

    def test_token(self):
        """
        Caller must have correct token, or no dice. Having a good token
        is tested in all the other tests.
        """

        # No token.
        resp = self.client.get(self.url)
        assert resp.status_code == 404

        # Invalid token.
        resp = self.client.get(self.url, {"token": "gibberish"})
        assert resp.status_code == 404

    def test_empty_token(self):
        """
        If configuration left the token empty, we should return a 404.
        """
        with self.settings(STATUS_TOKEN=""):
            self.get(expected_status=NOT_FOUND)
