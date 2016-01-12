"""
API for checkout
"""

from __future__ import unicode_literals
import logging

from django.conf import settings
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from stripe import Charge

from portal.util import create_order, get_external_pk, get_product_type, COURSE_PRODUCT_TYPE
from ..models import OrderLine
from .product_api import ccxcon_request

log = logging.getLogger(__name__)


class CheckoutView(APIView):
    """
    Handles checkout for courses and modules.
    """
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def notify_external_services(order, user):
        """
        Notify external services (ie CCXCon) about purchases.

        Args:
          order (portal.models.Order): The user's order.
          user (django.contrib.auth.models.User): User for the request.

        Returns:
          errors (set): A set of errors resulting from notification
        """
        errors = set()
        for line in OrderLine.objects.filter(order=order):
            if get_product_type(line.product) == COURSE_PRODUCT_TYPE:
                title = line.product.title
                course_id = get_external_pk(line.product)
            else:
                title = line.product.parent.title
                course_id = get_external_pk(line.product.parent)
            ccxcon = ccxcon_request()
            api_base = settings.CCXCON_API
            try:
                result = ccxcon.post(
                    '{api_base}v1/ccx/'.format(api_base=api_base),
                    data={
                        'master_course_id': course_id,
                        'user_email': user.email,
                        'total_seats': line.seats,
                        'display_name': '{} for {}'.format(title, user.userinfo.full_name),
                    }
                )
            except Exception as e:  # pylint: disable=broad-except,invalid-name
                log.error("Couldn't connect to ccxcon. Reason: %s", e)
                errors.add(str(e))
                continue

            if result.status_code >= 300:
                errors.add('Unable to post to ccxcon. Error: {} -- {}'.format(
                    result.status_code, result.content))
                log.error("Couldn't connect to ccxcon. Reason: %s", result.content)
        return errors

    @staticmethod
    def validate_data(data):
        """
        Validates incoming request data.

        Args:
            request.data: Data from incoming request.

        Returns:
            (string, dict): stripe token and cart information.
        """
        try:
            token = str(data['token'])
            cart = data['cart']
        except KeyError as ex:
            raise ValidationError("Missing key {}".format(ex.args[0]))
        except TypeError:
            raise ValidationError("Invalid JSON")

        if not isinstance(cart, list):
            raise ValidationError("Cart must be a list of items")
        if len(cart) == 0:
            raise ValidationError("Cannot checkout an empty cart")

        return token, cart

    def post(self, request):
        """
        Make a purchase of the cart.
        Args:
            request: rest_framework.request.Request
        Returns:
            rest_framework.response.Response
        """
        token, cart = self.validate_data(request.data)

        with transaction.atomic():
            order = create_order(cart, request.user)

            amount_in_cents = int(order.total_paid * 100)
            if amount_in_cents != 0:
                Charge.create(
                    amount=amount_in_cents,
                    currency="usd",
                    source=token,
                    description="Course purchase for MIT Teacher's Portal",
                    metadata={
                        "order_id": order.id
                    }
                )

        errors = self.notify_external_services(order, request.user)

        if len(errors):
            return Response({
                'error': "Unable to post to CCXCon",
                'error_list': errors,
            }, status=400)

        return Response(status=200)
