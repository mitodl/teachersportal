# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields

# pylint: skip-file

class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0009_no_null_for_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='author_name',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='course',
            name='course_id',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='course',
            name='image_url',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='course',
            name='instructors',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='course',
            name='overview',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='course',
            field=models.ForeignKey(related_name='modules', to='portal.Course'),
        ),
    ]
