# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

# pylint: skip-file


def add_instructor_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(
        name='Instructor'
    )

def remove_instructor_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name='Instructor').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0003_unique_instance'),
    ]

    operations = [
        migrations.RunPython(add_instructor_group, remove_instructor_group),
    ]
