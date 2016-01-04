"""
Webpack handlers.
"""

from __future__ import unicode_literals

import json
from django.shortcuts import render
from django.template import RequestContext
from portal.templatetags.webpack import webpack_bundle  # pylint: disable=unused-import


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
        "ccxconApi": "/ccxcon/",
        "isAuthenticated": request.user.is_authenticated()
    }

    return render(
        request, 'portal/index.html',
        context={
            "js_settings_json": json.dumps(js_settings)
        },
        context_instance=RequestContext(request)
    )
