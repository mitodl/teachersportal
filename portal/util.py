"""
Helper functions which may be generally useful.
"""

from __future__ import unicode_literals

from rest_framework.exceptions import ValidationError
from oscar.apps.catalogue.models import Product
from oscar.apps.partner.strategy import Selector

from portal.models import Order, OrderLine

MODULE_PRODUCT_TYPE = "Module"
COURSE_PRODUCT_TYPE = "Course"


def make_upc(product_type, external_pk):
    """
    Helper function to create unique UPC and SKU values for the database.

    Args:
        product_type (basestring):
            The name of the product type.
        external_pk (basestring):
            An identifer string, unique within the ProductClass.
    Returns:
        basestring: A unique string id.
    """
    return "{type}_{pk}".format(type=product_type, pk=external_pk)


def make_external_pk(product_type, upc):
    """
    We concatenate the product class with the UUID to store it in Product.upc
    which requires each entry to be unique (the incoming UUIDs are only guaranteed
    to be unique within product class). This chops off the product class and returns
    the UUID to be exposed via REST API.

    Args:
        product_type (basestring):
            The name of the product type.
        upc (basestring):
            The UPC used inside the database.
    Returns:
        basestring: The external_pk value used in creating this UUID
    """
    prefix = "{product_type}_".format(product_type=product_type)
    if upc.startswith(prefix):
        return upc[len(prefix):]

    # Should never happen since only the webhooks should update this listing
    raise Exception("Unexpected prefix found")


def get_external_pk(product):
    """
    Helper function to get external_pk for a product which may be None.

    Args:
        product (oscar.apps.catalogue.models.Product):
            A Product (may be None)
    Returns:
        basestring: The appropriate external pk for the Product, or None if
        product is None.
    """
    if product is None:
        return None
    if product.structure == Product.PARENT or product.structure == Product.STANDALONE:
        product_type = COURSE_PRODUCT_TYPE
    elif product.structure == Product.CHILD:
        product_type = MODULE_PRODUCT_TYPE
    else:
        raise Exception("Unexpected structure")
    return make_external_pk(product_type, product.upc)


def get_product_type(product):
    """
    Parse product type from UPC.

    Args:
        product (oscar.apps.catalogue.models.Product):
            A Product
    Returns:
        basestring: The product type
    """
    upc = product.upc
    for product_type in (COURSE_PRODUCT_TYPE, MODULE_PRODUCT_TYPE):
        if upc.startswith("{product_type}_".format(product_type=product_type)):
            return product_type
    raise Exception("Invalid product type")


# pylint: disable=too-many-branches
def validate_product(product):
    """
    Raise an exception if the product is invalid in some way, based on the rules
    we are enforcing in this app. (This may raise Exceptions for things that
    are valid by django-oscar.)
    """
    # This is not the same as the product type which is part of the UPC.
    if product.structure == Product.CHILD:
        if product.product_class is not None:
            raise Exception("Children cannot have product_class set")
        if product.parent is None:
            raise Exception("CHILD products must have a parent")
        if product.children.count() != 0:
            raise Exception("CHILD products must not have children")
        if get_product_type(product) != MODULE_PRODUCT_TYPE:
            raise Exception("Modules may only be CHILD Products")
        if product.categories.count() != 0:
            raise Exception("CHILD products can't have categories")
    elif product.structure == Product.PARENT or product.structure == Product.STANDALONE:
        if product.product_class.name != "Course":
            raise Exception("Only Course ProductClass may be set")
        if product.parent is not None:
            raise Exception("PARENT products must not have a parent")
        if get_product_type(product) != COURSE_PRODUCT_TYPE:
            raise Exception("Courses may only be PARENT Products")
        if product.structure == Product.PARENT and product.children.count() == 0:
            raise Exception("PARENT products must have children")
        if product.structure == Product.STANDALONE and product.children.count() > 0:
            raise Exception("STANDALONE products must not have children")
        if product.categories.count() == 0:
            raise Exception("STANDALONE and PARENT products must have a category")

    stockrecords = product.stockrecords.all()
    if stockrecords.count() > 0:
        if product.structure != Product.CHILD:
            raise Exception("Only CHILD products can have StockRecords")
        if stockrecords.count() > 1:
            raise Exception("More than one StockRecords for a Product")

        stockrecord = stockrecords.first()
        if stockrecord.partner_sku != product.upc:
            raise Exception("StockRecord SKU does not match Product UPC")

        if stockrecord.price_currency != "$":
            raise Exception("StockRecord price_currency must be $")


def get_price_without_tax(product):
    """
    Helper function to get price from Product's StockRecord.

    Args:
        product (oscar.apps.catalogue.models.Product):
            A Product (may be None)
    Returns:
        decimal.Decimal: If product exists and has a price, return the price
        else return None.
    """
    validate_product(product)

    stockrecord = product.stockrecords.first()
    if stockrecord is None:
        # No price information, not available to buy
        return None

    # Get default strategy
    strategy = Selector().strategy()
    info = strategy.fetch_for_product(product, stockrecord)
    return info.price.excl_tax


def is_available_to_buy(product):
    """
    Is a Product available to purchase? For our purposes this means if it has
    a price set.

    Args:
        product (oscar.apps.catalogue.models.Product):
            A Product
    Returns:
        bool: True if product is available to buy
    """
    validate_product(product)

    if product.structure == Product.PARENT:
        # Product will be available if any children are available
        return any(
            child for child in product.children.all()
            if is_available_to_buy(child)
        )
    elif product.structure == Product.STANDALONE:
        return False
    elif product.structure == Product.CHILD:
        stockrecord = product.stockrecords.first()
        if stockrecord is None:
            # No price information, not available to buy
            return False

        # Get default strategy
        strategy = Selector().strategy()
        info = strategy.fetch_for_product(product, stockrecord)
        return info.availability.is_available_to_buy
    else:
        raise Exception("Unexpected structure")


def product_as_json(product, ccxcon_info):
    """
    Serialize product to JSON
    Args:
        product (Product): A Product
        ccxcon_info (dict): Information fetched from CCXCon

    Returns:
        dict: The product as a dictionary
    """
    parent_upc = None
    if product.parent is not None:
        parent_upc = product.parent.upc
    return {
        "upc": product.upc,
        "title": product.title,
        "description": product.description,
        "external_pk": get_external_pk(product),
        "product_type": get_product_type(product),
        "price_without_tax": get_price_without_tax(product),
        "parent_upc": parent_upc,
        "info": ccxcon_info.get(product.upc),
        "children": [
            product_as_json(child, ccxcon_info)
            for child in product.children.order_by('date_created')
            if is_available_to_buy(child)
        ],
    }


def calculate_cart_subtotal(cart):
    """
    Calculate total of a cart.
    Args:
        cart (list): A list of items in cart
    Returns:
        float: Total price of cart
    """
    return sum(calculate_cart_item_total(item) for item in cart)


def calculate_cart_item_total(item):
    """
    Calculate total for a particular line.
    Args:
        item (dict): An item in the cart
    Returns:
        float: Product price times number of seats
    """
    product = Product.objects.get(upc=item['upc'])
    num_seats = int(item['seats'])
    return get_price_without_tax(product) * num_seats


def validate_cart(cart):
    """
    Validate cart contents.
    Args:
        cart (list): A list of items in cart
    """
    items_in_cart = set()

    for item in cart:
        try:
            product = Product.objects.get(upc=item['upc'])
            seats = int(item['seats'])
        except Product.DoesNotExist:
            raise ValidationError("One or more products are unavailable")
        except KeyError as ex:
            raise ValidationError("Missing key {}".format(ex.args[0]))

        if get_product_type(product) == COURSE_PRODUCT_TYPE:
            raise ValidationError("Cannot purchase a Course")
        if not is_available_to_buy(product):
            raise ValidationError("One or more products are unavailable")

        if seats == 0:
            raise ValidationError("Number of seats is zero")

        if item['upc'] in items_in_cart:
            raise ValidationError("Duplicate item in cart")

        items_in_cart.add(item['upc'])


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
        product = Product.objects.get(upc=item['upc'])
        OrderLine.objects.create(
            order=order,
            seats=int(item['seats']),
            product=product,
            price_without_tax=get_price_without_tax(product),
            line_total=calculate_cart_item_total(item)
        )
    return order
