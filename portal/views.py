"""
Views for teachersportal.
"""

from __future__ import unicode_literals

import json
import uuid
from six.moves.urllib.parse import urlparse, urlunparse, quote_plus  # pylint: disable=import-error
from wsgiref.util import is_hop_by_hop  # pylint: disable=wrong-import-order

from django.conf import settings
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, HttpResponse
from django.template import RequestContext
from django.views.decorators.http import require_http_methods
from oauthlib.oauth2 import BackendApplicationClient
from oscar.apps.catalogue.models import Product
from requests_oauthlib import OAuth2Session
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from portal.models import UserInfo
from portal.permissions import HmacPermission
from portal.templatetags.webpack import webpack_bundle  # pylint: disable=unused-import
from portal.serializers import ProductSerializer
from portal.util import (
    get_external_pk,
    get_price_without_tax,
    get_product_type,
    is_available_to_buy,
)
import portal.webhooks as webhooks


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


class WebhooksCCXConView(APIView):
    """
    Accepts messages from CCXCon
    """

    # Note that this does not include IsAuthenticated. We use only hmac
    # signatures to verify authentication for this API.
    permission_classes = (HmacPermission, )

    def post(self, request):  # pylint: disable=no-self-use
        """
        Handle messages from CCXCon.

        Args:
            request (HttpRequest)
        Returns:
            HttpResponse
        """
        # We'll probably want to move this logic out of an if statement when
        # it gets complicated.
        message = request.data
        for key in ('type', 'action', 'payload'):
            if key not in message:
                raise ValidationError("Missing key {key}".format(key=key))
        try:
            hook = getattr(webhooks, message['type'].lower())
        except AttributeError:
            raise ValidationError("No handler for type {type}".format(type=message['type']))

        hook(message['action'], message['payload'])

        # On success webhooks won't return anything since CCXCon
        # can't do anything with this information.
        return HttpResponse(status=200)


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


class ProductListView(ListAPIView):
    """
    Lists products available for purchase
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        """A queryset for products that are available for purchase"""

        return (
            {
                "title": product.title,
                "external_pk": get_external_pk(product),
                "product_type": get_product_type(product),
                "price_without_tax": get_price_without_tax(product),
                "parent_external_pk": get_external_pk(product.parent)
            }
            for product in Product.objects.order_by("date_created")
            if is_available_to_buy(product)
        )


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


@api_view(["POST"])
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
        return Response(status=403)

    user = userinfo.user
    user.is_active = True
    user.save()
    return Response(status=200)
