"""
Views to proxy requests back to CCXCon
"""
from __future__ import unicode_literals

from wsgiref.util import is_hop_by_hop  # pylint: disable=wrong-import-order
from six.moves.urllib.parse import urlparse, urlunparse  # pylint: disable=import-error

from django.conf import settings
from django.shortcuts import HttpResponse
from django.views.decorators.http import require_http_methods
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


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
