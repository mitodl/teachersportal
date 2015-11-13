"""
Views for teachersportal.
"""

from __future__ import unicode_literals

from django.shortcuts import render


def index_view(request):
    """View for index.

    Args:
        request (HttpRequest): Django request.
    Returns:
        HttpResponse
    """

    return render(request, 'portal/index.html', context={
        "host": request.get_host().split(":")[0]
    })
