"""
Handlers for CCXCon webhooks
"""

from __future__ import unicode_literals

from django.db import transaction
from oscar.apps.catalogue.models import (
    Product,
    ProductCategory,
    ProductClass,
    Category,
)
from oscar.apps.partner.models import StockRecord, Partner
from rest_framework.exceptions import ValidationError

from portal.util import make_upc

# Note: reflection used for names below so be careful not to rename functions.


def course(action, payload):
    """
    Handle a CCXCon request regarding courses.

    Args:
        action: Action to take for course
        payload: Data for action
    Returns:
        HttpResponse
    """
    product_class = ProductClass.objects.get(name="Course")
    category = Category.objects.get(name="Course")
    partner = Partner.objects.get(name='edX')

    if action == 'update':
        try:
            title = payload['title']
            external_pk = payload['external_pk']
        except KeyError as ex:
            raise ValidationError("Missing key {key}".format(key=ex.args[0]))
        except TypeError as ex:
            raise ValidationError("Invalid key {key}".format(key=ex.args[0]))

        if not external_pk:
            raise ValidationError('Invalid external_pk')

        upc = make_upc(product_class.name, external_pk)
        with transaction.atomic():
            try:
                product = Product.objects.get(
                    upc=upc,
                    product_class=product_class,
                )
                product.title = title
                product.save()
            except Product.DoesNotExist:
                product = Product.objects.create(
                    upc=upc,
                    product_class=product_class,
                    structure=Product.PARENT,
                    title=title
                )

            # Link product to category.
            ProductCategory.objects.get_or_create(
                category=category,
                product=product,
            )
            # Link product to partner (note that prices will be empty).
            StockRecord.objects.get_or_create(
                product=product,
                partner=partner,
                partner_sku=upc,
                price_currency="$",
                price_excl_tax=0,
                price_retail=0,
                cost_price=0,
            )
    elif action == 'delete':
        try:
            upc = make_upc(product_class.name, payload['external_pk'])
        except KeyError as ex:
            raise ValidationError("Missing key {key}".format(key=ex.args[0]))
        except TypeError as ex:
            raise ValidationError("Invalid key {key}".format(key=ex.args[0]))
        Product.objects.filter(upc=upc, product_class=product_class).delete()
    else:
        raise ValidationError("Unknown action {action}".format(action=action))


def module(action, payload):
    """
    Handle a CCXCon request regarding modules.

    Args:
        action: Action to take for module
        payload: Data for action
    Returns:
        HttpResponse
    """
    course_product_class = ProductClass.objects.get(name="Course")
    module_product_class = ProductClass.objects.get(name="Module")
    category = Category.objects.get(name="Course")
    partner = Partner.objects.get(name='edX')

    if action == 'update':
        try:
            title = payload['title']
            external_pk = payload['external_pk']
            course_external_pk = payload['course_external_pk']
        except KeyError as ex:
            raise ValidationError("Missing key {key}".format(key=ex.args[0]))
        except TypeError as ex:
            raise ValidationError("Invalid key {key}".format(key=ex.args[0]))

        if not external_pk:
            raise ValidationError("Invalid external_pk")

        module_upc = make_upc(module_product_class.name, external_pk)
        course_upc = make_upc(course_product_class.name, course_external_pk)
        with transaction.atomic():
            try:
                parent = Product.objects.get(
                    upc=course_upc,
                    product_class=course_product_class,
                )
            except Product.DoesNotExist:
                raise ValidationError("Invalid course_external_pk")

            try:
                product = Product.objects.get(
                    upc=module_upc,
                    product_class=module_product_class,
                )

                if parent != product.parent:
                    raise ValidationError("Invalid course_external_pk")
                product.title = title
                product.save()
            except Product.DoesNotExist:
                product = Product.objects.create(
                    upc=module_upc,
                    product_class=module_product_class,
                    structure=Product.CHILD,
                    parent=parent,
                    title=title
                )

            # Link product to category.
            ProductCategory.objects.get_or_create(
                category=category,
                product=product,
            )
            # Link product to partner (note that prices will be empty).
            StockRecord.objects.get_or_create(
                product=product,
                partner=partner,
                partner_sku=module_upc,
                price_currency="$",
                price_excl_tax=0,
                price_retail=0,
                cost_price=0,
            )

    elif action == 'delete':
        try:
            upc = make_upc(module_product_class.name, payload['external_pk'])
        except KeyError as ex:
            raise ValidationError("Missing key {key}".format(key=ex.args[0]))
        except TypeError as ex:
            raise ValidationError("Invalid key {key}".format(key=ex.args[0]))
        Product.objects.filter(upc=upc, product_class=module_product_class).delete()
    else:
        raise ValidationError("Unknown action {action}".format(action=action))
