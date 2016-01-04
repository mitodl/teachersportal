"""
Tests for CCXCon API forwarding
"""

from __future__ import unicode_literals
from six.moves.urllib.parse import urlparse, urlunparse  # pylint: disable=import-error

from mock import patch
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.test.utils import override_settings
import requests_mock


FAKE_CCXCON_API = 'https://fakehost/api/'


@override_settings(CCXCON_API=FAKE_CCXCON_API)
class TestCCXConAPI(TestCase):
    """
    Tests for CCXCon API forwarding.
    """

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_forwarding(self, fetch_mock, mock):  # pylint: disable=unused-argument
        """
        Test that GET requests are forwarded.
        """
        mock.get("{base}v1/".format(base=FAKE_CCXCON_API), text='success')
        resp = self.client.get("{base}v1/".format(base=reverse("ccxcon-api")))
        assert resp.status_code == 200
        assert resp.content.decode('utf-8') == 'success'

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_headers(self, fetch_mock, mock):  # pylint: disable=no-self-use, unused-argument
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

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_hop_by_hop(self, fetch_mock, mock):  # pylint: disable=unused-argument
        """Test that Keep-Alive and other hop-by-hop headers are filtered out"""

        mock.get(
            "{base}v1/end/point".format(base=FAKE_CCXCON_API),
            text="success",
            headers={"Connection": "Keep-Alive"}
        )

        resp = self.client.get("{base}v1/end/point".format(base=reverse("ccxcon-api")))
        assert resp.status_code == 200
        assert resp.content.decode('utf-8') == 'success'
        assert 'Connection' not in resp

    def test_post(self):
        """
        Test that POST requests are rejected.
        """
        resp = self.client.post("{base}v1/endpoint/".format(base=reverse("ccxcon-api")))
        assert resp.status_code == 405

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_query_params(self, fetch_mock, mock):  # pylint: disable=unused-argument
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

    @requests_mock.mock()
    def test_oauth(self, mock):
        """
        Test that OAuth header exists
        """

        def response_callback(request, context):  # pylint: disable=unused-argument
            """
            Assert that OAuth headers exist and start with 'Bearer' which indicates
            OAuth 2.
            """
            assert request.headers["Authorization"].startswith("Bearer")
            return 'success'

        oauth_endpoint = urlunparse(urlparse(FAKE_CCXCON_API)._replace(path="/o/token/"))

        mock.get(
            "{base}v1/".format(base=FAKE_CCXCON_API),
            text=response_callback
        )
        mock.post(
            oauth_endpoint,
            text='{"token_type":"bearer","access_token":"AAAA%2FAAA%3DAAAAAAAA"}'
        )

        resp = self.client.get("{base}v1/".format(
            base=reverse('ccxcon-api')
        ))
        assert resp.status_code == 200
        assert resp.content.decode('utf-8') == 'success'
