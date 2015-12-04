"""
Views for teachersportal.
"""

from __future__ import unicode_literals

import json

from django.conf import settings
from django.shortcuts import render, HttpResponse
from django.views.decorators.http import require_http_methods
import requests


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

    return render(request, 'portal/index.html', context={
        "host": host,
        "js_settings_json": json.dumps(js_settings)
    })


def forward_to_ccxcon(request):
    """
    Forwards GET traffic to CCXCon.

    Args:
        request (HttpRequest): Django request.

    Returns:
        HttpResponse
    """
    ccxcon_api = settings.CCXCON_API

    path = request.path
    if path.startswith("/ccxcon/"):
        path = path[len("/ccxcon/"):]

    response = requests.get(
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
