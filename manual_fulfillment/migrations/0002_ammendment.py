# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manual_fulfillment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ammendment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('new_seat_count', models.PositiveIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('original_purchase_order', models.ForeignKey(to='manual_fulfillment.PurchaseOrder')),
            ],
        ),
    ]
