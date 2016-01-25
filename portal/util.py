"""
Helper functions which may be generally useful.
"""

from __future__ import unicode_literals
from decimal import Decimal, ROUND_HALF_EVEN
import logging

from rest_framework.exceptions import ValidationError

from portal.exceptions import ProductException
from portal.models import (
    Module,
    Order,
    OrderLine,
)

MODULE_PRODUCT_TYPE = "Module"
COURSE_PRODUCT_TYPE = "Course"
log = logging.getLogger(__name__)


def make_qualified_id(product_type, external_pk):
    """
    Helper function to create unique id for use in the client.

    Args:
        product_type (basestring):
            The product_type (either Course or Module).
        external_pk (basestring):
            An identifier string, unique to the product_type
    Returns:
        basestring: A unique string id.
    """
    return "{type}_{pk}".format(type=product_type, pk=external_pk)


def make_external_pk(product_type, qualified_id):
    """
    We concatenate the product type with the UUID to guarantee uniqueness because
    the incoming UUIDs are only guaranteed to be unique within the product type.
    This chops off the product type and returns the UUID to be exposed via REST API.

    Args:
        product_type (basestring):
            The name of the product type.
        qualified_id (basestring):
            The qualified_id used inside the database.
    Returns:
        basestring: The external_pk value used in creating this UUID
    """
    prefix = "{product_type}_".format(product_type=product_type)
    if qualified_id.startswith(prefix):
        return qualified_id[len(prefix):]

    # Should never happen since only the webhooks should update this listing
    raise ProductException("Unexpected prefix found")


def get_product_type(qualified_id):
    """
    Parse product type from qualified_id.

    Args:
        qualified_id (basestring):
            A string used in the product API to uniquely identify a course or module
    Returns:
        basestring: The product type, or None if the product type is invalid
    """
    for product_type in (COURSE_PRODUCT_TYPE, MODULE_PRODUCT_TYPE):
        if qualified_id.startswith("{product_type}_".format(product_type=product_type)):
            return product_type
    return None


def course_as_product_json(course, ccxcon_info):
    """
    Serialize course to product API JSON
    Args:
        course (Course): A Course
        ccxcon_info (dict): Information fetched from CCXCon

    Returns:
        dict: The product as a dictionary
    """
    uuid = course.uuid
    return {
        "upc": course.qualified_id,
        "title": course.title,
        "description": course.description,
        "external_pk": uuid,
        "product_type": COURSE_PRODUCT_TYPE,
        "price_without_tax": None,
        "parent_upc": None,
        "info": ccxcon_info.get(course.qualified_id),
        "children": [
            module_as_product_json(child, ccxcon_info)
            for child in course.module_set.order_by('created_at')
        ],
    }


def module_as_product_json(module, ccxcon_info):
    """
    Serialize module to product API JSON
    Args:
        module (Module): A Module
        ccxcon_info (dict): Information fetched from CCXCon

    Returns:
        dict: The product as a dictionary
    """
    price_without_tax = None
    if module.price_without_tax is not None:
        price_without_tax = float(module.price_without_tax)
    return {
        "upc": module.qualified_id,
        "title": module.title,
        "description": "",
        "external_pk": module.uuid,
        "product_type": MODULE_PRODUCT_TYPE,
        "price_without_tax": price_without_tax,
        "parent_upc": module.course.qualified_id,
        "info": ccxcon_info.get(module.qualified_id),
        "children": [],
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
    uuid = make_external_pk(MODULE_PRODUCT_TYPE, item['upc'])
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
            qualified_id = item['upc']
            seats = item['seats']
        except KeyError as ex:
            raise ValidationError("Missing key {}".format(ex.args[0]))

        if not isinstance(seats, int):
            # Hopefully we're never entering long territory here
            raise ValidationError("Seats must be an integer")

        product_type = get_product_type(qualified_id)
        if product_type is None:
            raise ValidationError("Invalid product type")

        uuid = make_external_pk(product_type, qualified_id)
        if product_type != MODULE_PRODUCT_TYPE:
            raise ValidationError("Can only purchase Modules")

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
        children_qualified_ids = module.course.module_set.values_list('uuid', flat=True)
        if not items_in_cart.issuperset(children_qualified_ids):
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
        uuid = make_external_pk(MODULE_PRODUCT_TYPE, item['upc'])
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
