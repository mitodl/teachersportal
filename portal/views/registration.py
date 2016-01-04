"""
User registration
"""
from __future__ import unicode_literals

import uuid
from six.moves.urllib.parse import quote_plus  # pylint: disable=import-error

from django.conf import settings
from django.db import transaction
from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from portal.models import UserInfo


@api_view(["POST"])
def register_view(request):
    """
    Register a new user.

    Args:
        request (rest_framework.request.Request)
    Returns:
        rest_framework.response.Response
    """
    if request.user.is_authenticated():
        return Response(status=403)

    try:
        for key in ('full_name', 'organization', 'email', 'password', 'redirect'):
            if str(request.data[key]) == '':
                raise ValidationError("Empty value for {key}".format(key=key))

        full_name = str(request.data['full_name'])
        organization = str(request.data['organization'])
        email = str(request.data['email'])
        password = str(request.data['password'])
        redirect = str(request.data['redirect'])
    except KeyError as ex:
        raise ValidationError("Missing key {}".format(ex.args[0]))
    except TypeError:
        raise ValidationError("Invalid JSON")

    if User.objects.filter(username=email).exists():
        raise ValidationError("Email {email} is already in use".format(
            email=email
        ))

    token = str(uuid.uuid4())

    # Send email before creating user so that on error we don't have inconsistent data
    send_mail(
        "Teacher's Portal Registration",
        "Click here to activate your account: "
        "{scheme}://{host}/activate/?token={token}&redirect={redirect}".format(
            scheme=request.scheme,
            host=request.get_host(),
            token=quote_plus(token),
            redirect=quote_plus(redirect)
        ),
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )
    with transaction.atomic():
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        user.is_active = False
        user.save()
        UserInfo.objects.create(
            user=user,
            organization=organization,
            full_name=full_name,
            registration_token=token,
        )

    return Response(status=200)
