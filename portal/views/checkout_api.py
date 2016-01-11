"""
API for checkout
"""

from __future__ import unicode_literals


from django.contrib.auth.decorators import login_required
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from stripe import Charge

from portal.util import create_order


@login_required
@api_view(["POST"])
def checkout_view(request):
    """
    Make a purchase of the cart.
    Args:
        request: rest_framework.request.Request
    Returns:
        rest_framework.response.Response
    """
    try:
        token = str(request.data['token'])
        cart = request.data['cart']
    except KeyError as ex:
        raise ValidationError("Missing key {}".format(ex.args[0]))
    except TypeError:
        raise ValidationError("Invalid JSON")

    if not isinstance(cart, list):
        raise ValidationError("Cart must be a list of items")
    if len(cart) == 0:
        raise ValidationError("Cannot checkout an empty cart")

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

        # At this point tell edX everything went well

    return Response(status=200)
