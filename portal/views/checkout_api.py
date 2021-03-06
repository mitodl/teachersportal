"""
API for checkout
"""

from __future__ import unicode_literals
import logging
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from stripe import Charge

from portal.util import (
    calculate_cart_subtotal,
    create_order,
    get_cents,
    validate_cart,
)
from ..models import OrderLine
from ..ccxcon_api import CCXConAPI

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
        courses_and_seats = {}

        try:
            user.userinfo
        except ObjectDoesNotExist:
            raise ValidationError("You must have a user profile to check out.")

        # OrderLine stores a reference to a module and the number of seats
        # for each module. This number of seats should always be the same for each module
        # in a course.
        for line in OrderLine.objects.filter(order=order):
            course_uuid = line.module.course.uuid
            if course_uuid not in courses_and_seats:
                courses_and_seats[line.module.course.uuid] = (line.module.course, line.seats)

        ccxcon = CCXConAPI(
            settings.CCXCON_API,
            settings.CCXCON_OAUTH_CLIENT_ID,
            settings.CCXCON_OAUTH_CLIENT_SECRET,
        )
        for course, seats in courses_and_seats.values():
            try:
                _, status_code, response_json = ccxcon.create_ccx(
                    course.uuid, user.email, seats, course.title,
                    course_modules=[
                        orderline.module.uuid
                        for orderline in order.orderline_set.all()
                    ])
            except Exception as e:  # pylint: disable=broad-except,invalid-name
                log.error("Couldn't connect to ccxcon. Reason: %s", e)
                errors.add(str(e))
                continue

            if status_code >= 300:
                errors.add('Unable to post to ccxcon. Error: {} -- {}'.format(
                    status_code, response_json))
                log.error(
                    "Couldn't connect to ccxcon. Reason: %s", response_json)
        return errors

    def validate_data(self):
        """
        Validates incoming request data.

        Returns:
            (string, dict): stripe token and cart information.
        """
        data = self.request.data
        try:
            token = str(data['token'])
            cart = data['cart']
            estimated_total = Decimal(float(data['total']))
        except KeyError as ex:
            raise ValidationError("Missing key {}".format(ex.args[0]))
        except (TypeError, ValueError):
            raise ValidationError("Invalid float")

        if not isinstance(cart, list):
            raise ValidationError("Cart must be a list of items")
        if len(cart) == 0:
            raise ValidationError("Cannot checkout an empty cart")
        validate_cart(cart, self.request.user)

        total = calculate_cart_subtotal(cart)
        if get_cents(total) != get_cents(estimated_total):
            log.error(
                "Cart total doesn't match expected value. "
                "Total from client: %f but actual total is: %f",
                estimated_total,
                total
            )
            raise ValidationError("Cart total doesn't match expected value")

        return token, cart

    def post(self, request):
        """
        Make a purchase of the cart.
        Args:
            request: rest_framework.request.Request
        Returns:
            rest_framework.response.Response
        """
        token, cart = self.validate_data()

        with transaction.atomic():
            order = create_order(cart, request.user)

            amount_in_cents = get_cents(order.total_paid)
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
            }, status=500)

        return Response(status=200)
