"""
Base classes for test cases
"""

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.test import TestCase
from oscar.apps.catalogue.models import Product, ProductClass

from portal.models import UserInfo
from portal.util import (
    make_upc,
    COURSE_PRODUCT_TYPE,
    MODULE_PRODUCT_TYPE,
)


class AuthenticationTestCase(TestCase):
    """
    Provide functions useful for authentication tests.
    """

    USERNAME = "user"
    PASSWORD = "pass"
    OTHER_USERNAME = "other_user"
    OTHER_PASSWORD = "other_pass"
    INACTIVE_USERNAME = "inactive_user"
    INACTIVE_PASSWORD = "inactive_pass"

    def setUp(self):
        """Common test setup"""
        super(AuthenticationTestCase, self).setUp()

        self.user = User.objects.create_user(
            username=self.USERNAME,
            password=self.PASSWORD,
        )
        UserInfo.objects.create(
            organization="org for user 1",
            full_name="user 1",
            registration_token="first token with spaces",
            user=self.user
        )

        self.other_user = User.objects.create_user(
            username=self.OTHER_USERNAME,
            password=self.OTHER_PASSWORD,
        )
        UserInfo.objects.create(
            organization="org for user 2",
            full_name="user 2",
            registration_token="second token with spaces",
            user=self.other_user
        )

        self.inactive_user = User.objects.create_user(
            username=self.INACTIVE_USERNAME,
            password=self.INACTIVE_PASSWORD,
        )
        self.inactive_user.is_active = False
        self.inactive_user.save()
        UserInfo.objects.create(
            organization="org for inactive users",
            full_name="inactive user",
            registration_token="inactive user token",
            user=self.inactive_user
        )

    def is_authenticated(self, user):
        """Is user authenticated in self.client.session?"""
        # http://stackoverflow.com/questions/5660952/test-that-user-was-logged-in-successfully
        return (
            '_auth_user_id' in self.client.session and
            user.pk == int(self.client.session['_auth_user_id'])
        )


class ProductTests(TestCase):
    """
    Base class for tests dealing with products
    """
    def setUp(self):
        """
        Create parent and child Products with no StockRecords to start with.
        """
        product_class = ProductClass.objects.get(name="Course")
        parent_upc = make_upc(COURSE_PRODUCT_TYPE, "parent-uuid")
        parent_title = "parent's title"
        self.parent = Product.objects.create(
            upc=parent_upc,
            description="Parent description",
            product_class=product_class,
            structure=Product.PARENT,
            parent=None,
            title=parent_title
        )

        child_upc = make_upc(MODULE_PRODUCT_TYPE, "child-uuid")
        child_title = "child's title"
        self.child = Product.objects.create(
            upc=child_upc,
            description="Child description",
            product_class=None,
            structure=Product.CHILD,
            parent=self.parent,
            title=child_title
        )
