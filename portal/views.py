"""
Views for teachersportal.
"""

from __future__ import unicode_literals

import json
from six.moves.urllib.parse import urlparse, urlunparse  # pylint: disable=import-error
from wsgiref.util import is_hop_by_hop  # pylint: disable=wrong-import-order

from django.conf import settings
from django.shortcuts import render, HttpResponse
from django.views.decorators.http import require_http_methods
from django.template import RequestContext
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from portal.permissions import HmacPermission
from portal.templatetags.webpack import webpack_bundle  # pylint: disable=unused-import
import portal.webhooks as webhooks


def index_view(request):
    """View for index.

    Args:
        request (HttpRequest): Django request.
    Returns:
        HttpResponse
    """
    host = request.get_host().split(":")[0]
    js_settings = {
        "host": host,
        "ccxconApi": "/ccxcon/"
    }

    return render(
        request, 'portal/index.html',
        context={
            "js_settings_json": json.dumps(js_settings)
        },
        context_instance=RequestContext(request)
    )


def forward_to_ccxcon(request):
    """
    Forwards GET traffic to CCXCon.

    Args:
        request (HttpRequest): Django request.

    Returns:
        HttpResponse
    """
    ccxcon_api = settings.CCXCON_API
    client_id = settings.CCXCON_OAUTH_CLIENT_ID
    client_secret = settings.CCXCON_OAUTH_CLIENT_SECRET

    # Get an oauth token. At some point in the future we may want to cache
    # this if it doesn't already so we don't make an unnecessary request here.
    client = BackendApplicationClient(client_id=client_id)
    oauth_ccxcon = OAuth2Session(client=client)
    token_url = urlunparse(urlparse(ccxcon_api)._replace(path="/o/token/"))
    oauth_ccxcon.fetch_token(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
    )

    path = request.path
    if path.startswith("/ccxcon/"):
        path = path[len("/ccxcon/"):]

    response = oauth_ccxcon.get(
        "{api_base}{path}".format(
            api_base=ccxcon_api,
            path=path
        ),
        params=request.GET
    )

    ccxcon_response = HttpResponse(
        status=response.status_code,
        content=response.content
    )

    for key, value in response.headers.items():
        if not is_hop_by_hop(key):
            ccxcon_response[key] = value

    return ccxcon_response


@require_http_methods(["GET"])
def ccxcon_view(request):
    """
    Forwards GET traffic to CCXCon.

    Args:
        request (HttpRequest): Django request.
    Returns:
        HttpResponse
    """
    return forward_to_ccxcon(request)


class WebhooksCCXConView(APIView):
    """
    Accepts messages from CCXCon
    """

    permission_classes = (HmacPermission, )

    def post(self, request):  # pylint: disable=no-self-use
        """
        Handle messages from CCXCon.

        Args:
            request: HttpRequest
        Returns:
            HttpResponse
        """
        # We'll probably want to move this logic out of an if statement when
        # it gets complicated.
        message = request.data
        for key in ('type', 'action', 'payload'):
            if key not in message:
                raise ValidationError("Missing key {key}".format(key=key))
        try:
            hook = getattr(webhooks, message['type'].lower())
        except AttributeError:
            raise ValidationError("No handler for type {type}".format(type=message['type']))

        hook(message['action'], message['payload'])

        # On success webhooks won't return anything since CCXCon
        # can't do anything with this information.
        return HttpResponse(status=200)
