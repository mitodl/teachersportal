"""
Models classes needed for portal
"""
from __future__ import unicode_literals
from datetime import timedelta, datetime
from django.db import models

from django.contrib.auth.models import User
from django.db.models.fields.related import (
    ForeignKey,
    OneToOneField,
    ManyToManyField,
)
from django.db.models.fields import (
    BooleanField,
    DecimalField,
    IntegerField,
    TextField,
    DateTimeField,
)
from django.utils.timezone import make_aware, now
from django.utils.encoding import python_2_unicode_compatible
from jsonfield import JSONField

from portal.permissions import (
    EDIT_OWN_CONTENT,
    EDIT_OWN_LIVENESS,
    EDIT_OWN_PRICE,
    SEE_OWN_NOT_LIVE,
)


@python_2_unicode_compatible
class BackingInstance(models.Model):
    """
    The instance of edX where the course lives.
    """
    instance_url = TextField(unique=True)
    oauth_client_id = models.CharField(max_length=128, blank=True, null=True)
    oauth_client_secret = models.CharField(
        max_length=255, blank=True, null=True)
    username = models.CharField(
        max_length=30, blank=True, null=True,
        help_text="Username the backing oauth user is attached to. This is"
        " used to request course structure and MUST be a staff member of the"
        " course.")
    grant_token = models.CharField(max_length=128, blank=True, null=True)
    refresh_token = models.CharField(max_length=128, null=True, blank=True)
    access_token = models.CharField(max_length=128, null=True, blank=True)
    access_token_expiration = models.DateTimeField(
        default=make_aware(datetime(1970, 1, 1)))

    def __str__(self):
        """String representation to show in Django Admin console"""
        return self.instance_url

    @property
    def is_expired(self):
        """
        Returns whether the access token is expired
        """
        if not self.access_token_expiration:  # pre-persistence
            return True
        return self.access_token_expiration <= now() + timedelta(hours=2)


@python_2_unicode_compatible
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
    owners = ManyToManyField(to=User, related_name="courses_owned", blank=True)
    course_id = TextField(blank=True, null=True)
    author_name = TextField(blank=True, null=True)
    overview = TextField(blank=True, null=True)
    image_url = TextField(blank=True, null=True)
    instructors = JSONField(blank=True, null=True)

    @property
    def is_available_for_purchase(self):
        """
        Does the course have any modules available for purchase?
        """
        if self.modules.count() == 0:
            return False
        return all(module.is_available_for_purchase for module in self.modules.all())

    def __str__(self):
        """String representation to show in Django Admin console"""
        return "{title} ({uuid})".format(title=self.title, uuid=self.uuid)

    class Meta:  # pylint: disable=missing-docstring, no-init, old-style-class, too-few-public-methods
        ordering = ('created_at', )
        permissions = (
            EDIT_OWN_CONTENT,
            EDIT_OWN_LIVENESS,
            SEE_OWN_NOT_LIVE,
        )


@python_2_unicode_compatible
class Module(models.Model):
    """
    A chapter in a CCX course
    """
    uuid = TextField()
    course = ForeignKey(Course, related_name="modules")
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

    def __str__(self):
        """String representation to show in Django Admin console"""
        return "{title} ({uuid})".format(title=self.title, uuid=self.uuid)

    class Meta:  # pylint: disable=missing-docstring, no-init, old-style-class, too-few-public-methods
        ordering = ('created_at', )
        permissions = (
            EDIT_OWN_PRICE,
        )


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
    A module which is purchased.
    """
    order = ForeignKey(Order)
    seats = IntegerField()
    module = ForeignKey(Module)
    price_without_tax = DecimalField(decimal_places=2, max_digits=20)
    line_total = DecimalField(decimal_places=2, max_digits=20)
    created_at = DateTimeField(auto_now_add=True, blank=True)
    modified_at = DateTimeField(auto_now=True, blank=True)
