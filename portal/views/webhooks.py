"""
Webhook handlers.
"""
from __future__ import unicode_literals

from django.shortcuts import HttpResponse
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from portal.permissions import HmacPermission
import portal.webhooks as webhooks


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
            raise ValidationError("No handler for type {type}".format(
                type=message['type']))

        hook(message['action'], message['payload'])

        # On success webhooks won't return anything since CCXCon
        # can't do anything with this information.
        return HttpResponse(status=200)
