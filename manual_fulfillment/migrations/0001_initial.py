# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0009_no_null_for_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('coach_email', models.EmailField(max_length=254)),
                ('seat_count', models.PositiveSmallIntegerField()),
                ('title', models.CharField(help_text=b'Title of the ccx in edX.', max_length=255)),
                ('ccx_id', models.IntegerField(help_text=b"This will be filled in by the system when it's saved.", null=True, blank=True)),
                ('info', models.TextField(help_text=b'Information like purchase order number, etc', null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(to='portal.Course')),
            ],
        ),
    ]
