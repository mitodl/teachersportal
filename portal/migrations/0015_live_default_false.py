# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-04 19:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0014_userinfo_edx_instance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='live',
            field=models.BooleanField(default=False),
        ),
    ]
