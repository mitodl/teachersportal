"""
Migration to remove a product class we don't use
"""

from __future__ import unicode_literals

from django.db import migrations
from portal.util import get_product_type, MODULE_PRODUCT_TYPE
from oscar.core.loading import get_model

# pylint: skip-file


def remove_module_category(apps, schema_editor):
    """
    Remove categories from modules, which are invalid according to django-oscar.
    """
    # IMPORTANT: we should be using apps.get_model but then we won't have
    # access to the overridden models.
    Product = get_model("catalogue", "Product")
    ProductCategory = get_model("catalogue", "ProductCategory")
    module_product_ids = [
        product.id for product in Product.objects.all()
        if get_product_type(product) == MODULE_PRODUCT_TYPE
    ]
    ProductCategory.objects.filter(product_id__in=module_product_ids).delete()


class Migration(migrations.Migration):
    """
    Migration to remove categories from module.
    """
    dependencies = [("portal", "0004_order_orderline")]

    operations = [
        migrations.RunPython(remove_module_category)
    ]
