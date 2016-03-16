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
from portal.permissions import AuthorizationHelpers

log = logging.getLogger(__name__)


def course_as_dict(course, course_info=None, modules_info=None):
    """
    Serialize course to dict, ready for JSON serialization
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
        module_as_dict(module, modules_info.get(module.uuid))
        for module in course.module_set.order_by('created_at')
        ]
    return {
        "title": course.title,
        "description": course.description,
        "uuid": course.uuid,
        "info": course_info,
        "modules": modules,
        "live": course.live
    }


def module_as_dict(module, ccxcon_module_info=None):
    """
    Serialize module to dict, ready for JSON serialization
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
    total = Decimal()
    for item in cart:
        for uuid in item['uuids']:
            total += calculate_orderline_total(uuid, item['seats'])
    return total


def calculate_orderline_total(uuid, seats):
    """
    Calculate total for a particular item.
    Args:
        uuid (str): A UUID
        seats (int): A number of seats
    Returns:
        Decimal: Product price times number of seats
    """
    module = Module.objects.get(uuid=uuid)
    return module.price_without_tax * seats


# pylint: disable=too-many-branches
def validate_cart(cart, user):
    """
    Validate cart contents.
    Args:
        cart (list): A list of items in cart
        user (django.contrib.auth.models.User): A user
    """
    modules_in_cart = set()
    courses_in_cart = set()

    for item in cart:
        try:
            uuids = item['uuids']
            seats = item['seats']
            course_uuid = item['course_uuid']
        except KeyError as ex:
            raise ValidationError("Missing key {}".format(ex.args[0]))

        if not isinstance(seats, int):
            # Hopefully we're never entering long territory here
            raise ValidationError("Seats must be an integer")

        if seats == 0:
            raise ValidationError("Number of seats is zero")

        if not isinstance(uuids, list):
            raise ValidationError("uuids must be a list")

        if len(uuids) == 0:
            raise ValidationError("uuids must not be empty")

        if course_uuid in courses_in_cart:
            log.debug("Duplicate course %s in cart", course_uuid)
            raise ValidationError("Duplicate course in cart")
        course = AuthorizationHelpers.get_course(course_uuid, user)
        if course is None:
            raise ValidationError("One or more courses are unavailable")

        if not AuthorizationHelpers.can_purchase_course(course, user):
            raise ValidationError("User cannot purchase this course")

        courses_in_cart.add(course_uuid)

        for uuid in uuids:
            try:
                module = Module.objects.get(uuid=uuid)
            except Module.DoesNotExist:
                log.debug('Could not find module with uuid %s', uuid)
                raise ValidationError("One or more modules are unavailable")

            if module.course != course:
                log.debug(
                    'Course with uuid %s does not match up with module with uuid %s',
                    course_uuid,
                    uuid
                )
                raise ValidationError("Course does not match up with module")

            if not module.is_available_for_purchase:
                raise ValidationError("One or more modules are unavailable")

            if uuid in modules_in_cart:
                log.debug("Duplicate module uuid %s", uuid)
                raise ValidationError("Duplicate module in cart")

            modules_in_cart.add(uuid)


def create_order(cart, user):
    """
    Create an order given a cart's contents.
    Args:
        cart: (list): A list of items in cart.
        user: (django.contrib.auth.models.User): A user
    Returns:
        Order: A newly created order
    """
    validate_cart(cart, user)

    subtotal = calculate_cart_subtotal(cart)
    order = Order.objects.create(
        purchaser=user,
        subtotal=subtotal,
        total_paid=subtotal,
    )
    for item in cart:
        seats = item['seats']
        uuids = item['uuids']
        for uuid in uuids:
            module = Module.objects.get(uuid=uuid)
            OrderLine.objects.create(
                order=order,
                seats=seats,
                module=module,
                price_without_tax=module.price_without_tax,
                line_total=calculate_orderline_total(uuid, seats)
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
