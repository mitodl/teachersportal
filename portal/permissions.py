"""
Permissions classes for REST API
"""

from __future__ import unicode_literals
import hashlib
import hmac

from django.conf import settings
from django.utils.crypto import constant_time_compare
from rest_framework.permissions import BasePermission


class HmacPermission(BasePermission):
    """
    Verify hmac signature.
    """
    def has_permission(self, request, view):
        try:
            signature = request.META['HTTP_X_CCXCON_SIGNATURE']
        except KeyError:
            return False

        return constant_time_compare(
            signature,
            hmac.new(settings.CCXCON_WEBHOOKS_SECRET, request.body, hashlib.sha1).hexdigest()
        )
