"""
View for account activation.
"""
from __future__ import unicode_literals

from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import permission_classes
from rest_framework.response import Response

from portal.models import UserInfo


@api_view(["POST"])
@permission_classes([])
def activate_view(request):
    """
    Register token to activate user

    Args:
        request (rest_framework.request.Request)
    Returns:
        rest_framework.response.Response
    """
    if request.user.is_authenticated():
        return Response(status=403)

    try:
        token = str(request.data['token'])
    except KeyError as ex:
        raise ValidationError("Missing key {}".format(ex.args[0]))
    except TypeError:
        raise ValidationError("Invalid JSON")

    if token == "":
        raise ValidationError("token is empty")

    try:
        userinfo = UserInfo.objects.get(registration_token=token)
    except UserInfo.DoesNotExist:
        return Response("Could not find registration token.", status=403)

    user = userinfo.user
    user.is_active = True
    user.save()
    return Response(status=200)
