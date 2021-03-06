"""
Webpack handlers.
"""

from __future__ import unicode_literals

import json
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.shortcuts import render
from django.template import RequestContext


def index_view(request):
    """View for index.

    Args:
        request (HttpRequest): Django request.
    Returns:
        HttpResponse
    """
    host = request.get_host().split(":")[0]

    # AnonymousUser doesn't have an email address
    email = ""
    # Incorrectly built/anonymous users lack a userinfo property.
    name = ""
    if not request.user.is_anonymous():
        email = request.user.email

        try:
            name = request.user.userinfo.full_name
        except (ObjectDoesNotExist,):
            pass

    js_settings = {
        "host": host,
        "email": email,
        "name": name,
        "isAuthenticated": request.user.is_authenticated(),
        "stripePublishableKey": settings.STRIPE_PUBLISHABLE_KEY,
        "gaTrackingID": settings.GA_TRACKING_ID,
        "reactGaDebug": settings.REACT_GA_DEBUG
    }

    bundle = "index_page.js"
    if settings.DEBUG and settings.USE_WEBPACK_DEV_SERVER:
        host = request.get_host().split(":")[0]

        src = "{host_url}/{bundle}".format(
            host_url=settings.WEBPACK_SERVER_URL.format(host=host),
            bundle=bundle
        )
    else:
        src = static("bundles/{bundle}".format(bundle=bundle))

    return render(
        request, 'portal/index.html',
        context={
            "js_settings_json": json.dumps(js_settings),
            "src": src
        },
        context_instance=RequestContext(request)
    )
