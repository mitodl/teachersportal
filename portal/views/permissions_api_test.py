"""
Permissions API tests
"""

from __future__ import unicode_literals
import json
from itertools import product
from mock import patch
from six import get_function_code

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from portal.factories import CourseFactory, ModuleFactory
from portal.permissions import (
    EDIT_OWN_CONTENT,
    EDIT_OWN_LIVENESS,
    EDIT_OWN_PRICE,
    AuthorizationHelpers as Helpers,
)


class PermissionsAPITests(TestCase):
    """
    Permission API tests
    """

    def test_permissions(self):
        """
        Test all possible combinations of permissions.
        """
        User.objects.create_user(username="user", password="pass")
        self.client.login(username="user", password="pass")

        course = CourseFactory.create(live=True)
        ModuleFactory.create(price_without_tax=3, course=course)
        assert course.is_available_for_purchase

        def assert_permissions(edit_content, edit_liveness, edit_price, is_owner):
            """Mock and assert these set of permissions"""

            @patch.object(Helpers, 'is_owner', return_value=is_owner)
            @patch.object(Helpers, 'can_edit_own_content', return_value=edit_content)
            @patch.object(Helpers, 'can_edit_own_liveness', return_value=edit_liveness)
            @patch.object(Helpers, 'can_edit_own_price', return_value=edit_price)
            def run_assert_permissions(*args):  # pylint: disable=unused-argument
                """Something to attach our patch objects to so we don't indent each time"""
                resp = self.client.get(
                    reverse('course-permissions', kwargs={"uuid": course.uuid})
                )
                assert resp.status_code == 200, resp.content.decode('utf-8')
                result = json.loads(resp.content.decode('utf-8'))
                assert result == {
                    "is_owner": is_owner,
                    EDIT_OWN_CONTENT[0]: edit_content,
                    EDIT_OWN_PRICE[0]: edit_price,
                    EDIT_OWN_LIVENESS[0]: edit_liveness,
                }
            run_assert_permissions()

        num_args = get_function_code(assert_permissions).co_argcount  # pylint: disable=no-member
        args = [(True, False)] * num_args
        for tup in product(*args):
            assert_permissions(*tup)

    def test_no_course(self):
        """
        If course is missing we should return a 404.
        """
        User.objects.create_user(username="user", password="pass")
        self.client.login(username="user", password="pass")

        resp = self.client.get(reverse('course-permissions', kwargs={'uuid': 'missing'}))
        assert resp.status_code == 404, resp.content.decode('utf-8')

    def test_not_logged_in(self):
        """
        If the user is not logged in, return a 403.
        """
        course = CourseFactory.create(live=True)
        ModuleFactory.create(price_without_tax=3, course=course)
        assert course.is_available_for_purchase

        resp = self.client.get(reverse('course-permissions', kwargs={'uuid': course.uuid}))
        assert resp.status_code == 403, resp.content.decode('utf-8')
