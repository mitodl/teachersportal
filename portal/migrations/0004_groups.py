# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

# pylint: skip-file


def populate_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.create(
        name='Instructor'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0003_unique_instance'),
    ]

    operations = [
        migrations.RunPython(populate_groups),
    ]
