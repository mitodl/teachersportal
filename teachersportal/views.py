"""
Views for teachersportal.
"""

from __future__ import unicode_literals

import json

from django.shortcuts import render
from django.conf import settings


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
        "ccxconApi": settings.CCXCON_API
    }

    return render(request, 'portal/index.html', context={
        "host": host,
        "js_settings_json": json.dumps(js_settings)
    })
