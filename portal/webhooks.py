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
from rest_framework.exceptions import ValidationError

from portal.util import (
    make_upc,
    MODULE_PRODUCT_TYPE,
    COURSE_PRODUCT_TYPE,
)

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

        upc = make_upc(COURSE_PRODUCT_TYPE, external_pk)
        with transaction.atomic():
            try:
                product = Product.objects.get(upc=upc)
                product.title = title
                product.save()
            except Product.DoesNotExist:
                product = Product.objects.create(
                    upc=upc,
                    product_class=product_class,
                    structure=Product.STANDALONE,
                    title=title
                )

            # Link product to category.
            ProductCategory.objects.get_or_create(
                category=category,
                product=product,
            )
    elif action == 'delete':
        try:
            upc = make_upc(COURSE_PRODUCT_TYPE, payload['external_pk'])
        except KeyError as ex:
            raise ValidationError("Missing key {key}".format(key=ex.args[0]))
        except TypeError as ex:
            raise ValidationError("Invalid key {key}".format(key=ex.args[0]))
        Product.objects.filter(upc=upc).delete()
    else:
        raise ValidationError("Unknown action {action}".format(action=action))


# pylint: disable=too-many-branches,too-many-statements
def module(action, payload):
    """
    Handle a CCXCon request regarding modules.

    Args:
        action: Action to take for module
        payload: Data for action
    Returns:
        HttpResponse
    """
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

        module_upc = make_upc(MODULE_PRODUCT_TYPE, external_pk)
        course_upc = make_upc(COURSE_PRODUCT_TYPE, course_external_pk)
        with transaction.atomic():
            try:
                parent = Product.objects.get(upc=course_upc)
            except Product.DoesNotExist:
                raise ValidationError("Invalid course_external_pk")

            if parent.structure == Product.STANDALONE:
                # There will be at least one child.
                parent.structure = Product.PARENT
                parent.save()

            try:
                product = Product.objects.get(upc=module_upc)

                if parent != product.parent:
                    raise ValidationError("Invalid course_external_pk")
                product.title = title
                product.save()
            except Product.DoesNotExist:
                product = Product.objects.create(
                    upc=module_upc,
                    product_class=None,
                    structure=Product.CHILD,
                    parent=parent,
                    title=title
                )

    elif action == 'delete':
        try:
            upc = make_upc(MODULE_PRODUCT_TYPE, payload['external_pk'])
        except KeyError as ex:
            raise ValidationError("Missing key {key}".format(key=ex.args[0]))
        except TypeError as ex:
            raise ValidationError("Invalid key {key}".format(key=ex.args[0]))
        with transaction.atomic():
            try:
                product = Product.objects.get(upc=upc)
                parent = product.parent
                if parent.children.count() == 1:
                    parent.structure = Product.STANDALONE
                    parent.save()
            except Product.DoesNotExist:
                pass

            Product.objects.filter(upc=upc).delete()
    else:
        raise ValidationError("Unknown action {action}".format(action=action))
