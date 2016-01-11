"""
Models classes needed for portal
"""
from django.db import models

from django.contrib.auth.models import User
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.db.models.fields import (
    DecimalField,
    IntegerField,
    TextField,
    DateTimeField,
)
from oscar.apps.catalogue.models import Product


class UserInfo(models.Model):
    """
    Other user information.
    """
    user = OneToOneField(User, primary_key=True)
    registration_token = TextField(null=True, blank=True)
    organization = TextField()
    full_name = TextField()


class Order(models.Model):
    """
    An order that has been placed after purchasing courses.
    """
    subtotal = DecimalField(decimal_places=2, max_digits=20)
    total_paid = DecimalField(decimal_places=2, max_digits=20)
    purchaser = ForeignKey(User)
    created_at = DateTimeField(auto_now_add=True, blank=True)
    modified_at = DateTimeField(auto_now=True, blank=True)


class OrderLine(models.Model):
    """
    An item purchased
    """
    order = ForeignKey(Order)
    seats = IntegerField()
    product = ForeignKey(Product)
    price_without_tax = DecimalField(decimal_places=2, max_digits=20)
    line_total = DecimalField(decimal_places=2, max_digits=20)
    created_at = DateTimeField(auto_now_add=True, blank=True)
    modified_at = DateTimeField(auto_now=True, blank=True)
