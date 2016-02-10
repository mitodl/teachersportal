"""
REST API for getting permissions
"""

from __future__ import unicode_literals

from django.http.response import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from portal.permissions import (
    AuthorizationHelpers,
    EDIT_OWN_PRICE,
    EDIT_OWN_CONTENT,
    EDIT_OWN_LIVENESS,
)


@api_view(["GET"])
def course_permissions_view(request, uuid):
    """
    Returns a list of permissions and other information to adjust UI in client.

    Args:
        request (rest_framework.request.Request): The REST request
        uuid (str): The course UUID
    Returns:
        rest_framework.request.Response: The REST response
    """
    course = AuthorizationHelpers.get_course(uuid)
    if course is None:
        raise Http404

    return Response(data={
        EDIT_OWN_PRICE[0]: AuthorizationHelpers.has_edit_own_price_perm(
            course, request.user
        ),
        EDIT_OWN_CONTENT[0]: AuthorizationHelpers.has_edit_own_content_perm(
            course, request.user
        ),
        EDIT_OWN_LIVENESS[0]: AuthorizationHelpers.has_edit_own_liveness_perm(
            course, request.user
        ),
        "is_owner": AuthorizationHelpers.is_owner(course, request.user)
    })
