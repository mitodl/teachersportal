"""
Models classes needed for portal
"""
from django.db import models

from django.contrib.auth.models import User
from django.db.models.fields.related import OneToOneField
from django.db.models.fields import TextField


class UserInfo(models.Model):
    """
    Other user information.
    """
    user = OneToOneField(User, primary_key=True)
    registration_token = TextField(null=True, blank=True)
    organization = TextField()
    full_name = TextField()
