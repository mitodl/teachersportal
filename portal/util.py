"""
Helper functions which may be generally useful.
"""

from __future__ import unicode_literals
from decimal import Decimal, ROUND_HALF_EVEN
import logging

from rest_framework.exceptions import ValidationError

from portal.models import (
    Module,
    Order,
    OrderLine,
)

log = logging.getLogger(__name__)


def course_as_json(course, course_info=None, modules_info=None):
    """
    Serialize course to JSON
    Args:
        course (Course): A Course
        course_info (dict): Information fetched from CCXCon about the course
        modules_info (dict): Information about each module, in fetched order

    Returns:
        dict: The course as a dictionary
    """
    if modules_info is None:
        modules_info = {}

    modules = [
        module_as_json(module, modules_info.get(module.uuid))
        for module in course.module_set.order_by('created_at')
    ]
    return {
        "title": course.title,
        "description": course.description,
        "uuid": course.uuid,
        "info": course_info,
        "modules": modules,
    }


def module_as_json(module, ccxcon_module_info=None):
    """
    Serialize module to JSON
    Args:
        module (Module): A Module
        ccxcon_module_info (dict): Information fetched from CCXCon

    Returns:
        dict: The module as a dictionary
    """
    price_without_tax = None
    if module.price_without_tax is not None:
        price_without_tax = float(module.price_without_tax)
    return {
        "title": module.title,
        "uuid": module.uuid,
        "price_without_tax": price_without_tax,
        "info": ccxcon_module_info,
    }


def calculate_cart_subtotal(cart):
    """
    Calculate total of a cart.
    Args:
        cart (list): A list of items in cart
    Returns:
        Decimal: Total price of cart
    """
    return sum(calculate_cart_item_total(item) for item in cart)


def calculate_cart_item_total(item):
    """
    Calculate total for a particular line.
    Args:
        item (dict): An item in the cart
    Returns:
        Decimal: Product price times number of seats
    """
    uuid = item['uuid']
    module = Module.objects.get(uuid=uuid)
    num_seats = int(item['seats'])
    return module.price_without_tax * num_seats


def validate_cart(cart):
    """
    Validate cart contents.
    Args:
        cart (list): A list of items in cart
    """
    items_in_cart = set()

    for item in cart:
        try:
            uuid = item['uuid']
            seats = item['seats']
        except KeyError as ex:
            raise ValidationError("Missing key {}".format(ex.args[0]))

        if not isinstance(seats, int):
            # Hopefully we're never entering long territory here
            raise ValidationError("Seats must be an integer")

        try:
            module = Module.objects.get(uuid=uuid)
        except Module.DoesNotExist:
            log.debug('Could not find module with uuid %s', uuid)
            raise ValidationError("One or more products are unavailable")

        if not module.course.live:
            raise ValidationError("One or more products are unavailable")

        if seats == 0:
            raise ValidationError("Number of seats is zero")

        if uuid in items_in_cart:
            raise ValidationError("Duplicate item in cart")

        items_in_cart.add(uuid)

    for module_uuid in items_in_cart:
        module = Module.objects.get(uuid=module_uuid)
        uuids = module.course.module_set.values_list('uuid', flat=True)
        if not items_in_cart.issuperset(uuids):
            raise ValidationError("You must purchase all modules for a course.")


def create_order(cart, user):
    """
    Create an order given a cart's contents.
    Args:
        cart: (list): A list of items in cart.
        user: (django.contrib.auth.models.User): A user
    Returns:
        Order: A newly created order
    """
    validate_cart(cart)

    subtotal = calculate_cart_subtotal(cart)
    order = Order.objects.create(
        purchaser=user,
        subtotal=subtotal,
        total_paid=subtotal,
    )
    for item in cart:
        uuid = item['uuid']
        module = Module.objects.get(uuid=uuid)
        OrderLine.objects.create(
            order=order,
            seats=int(item['seats']),
            module=module,
            price_without_tax=module.price_without_tax,
            line_total=calculate_cart_item_total(item)
        )
    return order


def get_cents(dec):
    """
    Helper function to get an integer cents value from a Decimal.
    Args:
        dec (Decimal): A decimal
    Returns:
        int: Number of cents, rounded down
    """
    return int(
        dec.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN) * 100
    )
