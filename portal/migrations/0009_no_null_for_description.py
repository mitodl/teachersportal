# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

# pylint: skip-file

def remove_none(apps, schema_editor):
    Course = apps.get_model("portal", "Course")
    for course in Course.objects.filter(description=None).all():
        course.description = ""
        course.save()


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0008_see_own_not_live'),
    ]

    operations = [
        # Reverse migration does nothing here
        migrations.RunPython(remove_none, lambda *args: None),
        migrations.AlterField(
            model_name='course',
            name='description',
            field=models.TextField(default=None, blank=True),
            preserve_default=False,
        ),
    ]
