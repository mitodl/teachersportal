"""
Migration to remove a product class we don't use
"""

from __future__ import unicode_literals

from django.db import migrations
from oscar.core.loading import get_model

# pylint: skip-file


def remove_module_product_class(apps, schema_editor):
    """
    Add base information for creating Products.
    """
    # IMPORTANT: we should be using apps.get_model but then we won't have
    # access to the overridden models.
    ProductClass = get_model("catalogue", "ProductClass")
    ProductClass.objects.filter(name="Module").delete()


class Migration(migrations.Migration):
    """
    Migration to populate oscar models.
    """
    dependencies = [("portal", "0002_userinfo")]

    operations = [
        migrations.RunPython(remove_module_product_class)
    ]
