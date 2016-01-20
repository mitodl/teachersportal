"""
Models classes needed for portal
"""
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.db.models.fields import (
    BooleanField,
    DecimalField,
    IntegerField,
    TextField,
    DateTimeField,
)


class BackingInstance(models.Model):
    """
    The instance of edX where the course lives.
    """
    instance_url = TextField(unique=True)


class Course(models.Model):
    """
    A CCX course
    """
    uuid = TextField()
    title = TextField()
    description = TextField(blank=True, null=True)
    live = BooleanField()
    created_at = DateTimeField(auto_now_add=True, blank=True)
    modified_at = DateTimeField(auto_now=True, blank=True)
    instance = ForeignKey(BackingInstance)

    @property
    def is_available_for_purchase(self):
        """
        Does the course have any modules available for purchase?
        """
        if self.module_set.count() == 0:
            return False
        return all(module.is_available_for_purchase for module in self.module_set.all())

    class Meta:  # pylint: disable=missing-docstring, no-init, old-style-class, too-few-public-methods
        ordering = ('created_at', )


class Module(models.Model):
    """
    A chapter in a CCX course
    """
    uuid = TextField()
    course = ForeignKey(Course)
    title = TextField()
    price_without_tax = DecimalField(decimal_places=2, max_digits=20, blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True, blank=True)
    modified_at = DateTimeField(auto_now=True, blank=True)

    @property
    def is_available_for_purchase(self):
        """
        Is the module available for purchase?
        """
        return self.course.live and self.price_without_tax is not None  # pylint: disable=no-member

    class Meta:  # pylint: disable=missing-docstring, no-init, old-style-class, too-few-public-methods
        ordering = ('created_at', )


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
    module = ForeignKey(Module)
    price_without_tax = DecimalField(decimal_places=2, max_digits=20)
    line_total = DecimalField(decimal_places=2, max_digits=20)
    created_at = DateTimeField(auto_now_add=True, blank=True)
    modified_at = DateTimeField(auto_now=True, blank=True)
