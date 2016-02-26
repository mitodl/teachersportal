# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

# pylint: skip-file


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0002_add_instance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backinginstance',
            name='instance_url',
            field=models.TextField(unique=True),
        ),
    ]
