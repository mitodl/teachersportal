"""
Migration to populate oscar models.
"""
from __future__ import unicode_literals

from django.db import migrations
from django.utils.text import slugify

from oscar.core.loading import get_model

# pylint: skip-file

def populate_oscar_models(apps, schema_editor):
    """
    Add base information for creating Products.
    """
    # IMPORTANT: we should be using apps.get_model but then we won't have
    # access to the overridden models.
    ProductClass = get_model("catalogue", "ProductClass")
    Category = get_model("catalogue", "Category")
    Partner = get_model("partner", "Partner")

    for name in ('Course', 'Module'):
        ProductClass.objects.create(
            name=name,
            requires_shipping=False,
            track_stock=False,
        )

    category_name = "Course"
    Category.add_root(name=category_name, slug=slugify(category_name))
    Partner.objects.create(name='edX')


class Migration(migrations.Migration):
    """
    Migration to populate oscar models.
    """
    dependencies = [("catalogue", "0001_initial")]

    operations = [
        migrations.RunPython(populate_oscar_models)
    ]
