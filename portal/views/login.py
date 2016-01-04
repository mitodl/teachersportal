"""
Views for login/logout.
"""
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError


class LoginView(APIView):
    """
    View to authenticate and login user.
    """
    # This tuple intentionally left blank
    permission_classes = ()

    def post(self, request):  # pylint: disable=no-self-use
        """
        View to authenticate and login user.

        Args:
            request (rest_framework.request.Request)
        Returns:
            rest_framework.response.Response
        """
        # Adapted from https://docs.djangoproject.com/en/1.9/topics/auth/default/#auth-web-requests
        try:
            username = request.data['username']
            password = request.data['password']
        except KeyError:
            raise ValidationError("Missing key")
        except TypeError:
            raise ValidationError("Invalid data")

        user = authenticate(
            username=username,
            password=password,
        )
        if user is not None:
            if user.is_active:
                login(request, user)
                return Response(status=200)
            else:
                return Response(status=403)
        else:
            return Response(status=403)


@api_view(["POST"])
def logout_view(request):
    """
    View to logout user.

    Args:
        request (rest_framework.request.Request)
    Returns:
        rest_framework.response.Response
    """
    logout(request)
    return Response(status=200)
