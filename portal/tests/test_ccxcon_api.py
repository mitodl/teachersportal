"""
Tests for CCXCon API forwarding
"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.test.utils import override_settings
import requests_mock


FAKE_CCXCON_API = 'http://fakehost/api/'


@override_settings(CCXCON_API=FAKE_CCXCON_API)
class TestCCXConAPI(TestCase):
    """
    Tests for CCXCon API forwarding.
    """

    @requests_mock.mock()
    def test_forwarding(self, mock):
        """
        Test that GET requests are forwarded.
        """
        mock.get("{base}v1/".format(base=FAKE_CCXCON_API), text='success')
        resp = self.client.get("{base}v1/".format(base=reverse("ccxcon-api")))
        assert resp.status_code == 200
        assert resp.content.decode('utf-8') == 'success'

    @requests_mock.mock()
    def test_headers(self, mock):  # pylint: disable=no-self-use
        """
        Test that we don't pass headers to CCXCon in the request,
        but we pass headers coming back in the response.
        """

        def response_callback(request, context):  # pylint: disable=unused-argument
            """
            Make sure we filtered out the header we sent to the portal API.
            """
            assert 'request_header' not in request.headers
            return 'success'

        mock.get(
            "{base}v1/end/point".format(base=FAKE_CCXCON_API),
            text=response_callback,
            headers={"response_header": "response_header_value"}
        )

        client = Client(request_header_value="request_header")
        resp = client.get("{base}v1/end/point".format(base=reverse("ccxcon-api")))
        assert resp.status_code == 200
        assert resp.content.decode('utf-8') == 'success'
        assert resp['response_header'] == 'response_header_value'

    def test_post(self):
        """
        Test that POST requests are rejected.
        """
        resp = self.client.post("{base}v1/endpoint/".format(base=reverse("ccxcon-api")))
        assert resp.status_code == 405

    @requests_mock.mock()
    def test_query_params(self, mock):
        """
        Test that query parameters are forwarded.
        """

        def response_callback(request, context):  # pylint: disable=unused-argument
            """
            Make sure we pass all query parameters from the portal API.
            """
            assert request.qs['limit'] == ['4']
            assert request.qs['offset'] == ['3']
            return 'success'

        mock.get(
            "{base}v1/ccx/".format(base=FAKE_CCXCON_API),
            text=response_callback
        )

        resp = self.client.get("{base}v1/ccx/?limit=4&offset=3".format(
            base=reverse('ccxcon-api')
        ))
        assert resp.status_code == 200
        assert resp.content.decode('utf-8') == 'success'
