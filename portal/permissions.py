"""
Permissions classes for REST API
"""

from __future__ import unicode_literals
import hashlib
import hmac
import logging

from django.conf import settings
from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes
from rest_framework.permissions import BasePermission


log = logging.getLogger(__name__)


class HmacPermission(BasePermission):
    """
    Verify hmac signature.
    """
    def has_permission(self, request, view):
        try:
            signature = request.META['HTTP_X_CCXCON_SIGNATURE']
        except KeyError:
            log.info("Request did not have the necessary X-CCXCON-SIGNATURE header")
            return False

        computed = hmac.new(
            force_bytes(settings.CCXCON_WEBHOOKS_SECRET),
            force_bytes(request.body.decode('utf-8')),
            hashlib.sha1).hexdigest()
        is_valid = constant_time_compare(signature, computed)
        if not is_valid:
            log.debug("Request did not have a valid hmac signature. %s != %s", signature, computed)

        return is_valid
