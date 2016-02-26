"""
Tests about permissions
"""

from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth.models import User, Group, AnonymousUser

from portal.factories import CourseFactory, ModuleFactory
from portal.permissions import (
    EDIT_OWN_CONTENT,
    EDIT_OWN_LIVENESS,
    EDIT_OWN_PRICE,
    AuthorizationHelpers
)


def strip_appname(perm):
    """Helper function to remove appname from a permission"""
    app_name = "portal"
    if perm.startswith("{}.".format(app_name)):
        return perm[len(app_name) + 1:]


# pylint: disable=no-self-use
class PermissionsTests(TestCase):
    """
    Tests about permissions
    """

    def test_instructor_group(self):
        """
        Assert permissions on instructor group
        """
        user = User.objects.create_user(username="user")
        codenames = [perm.codename for perm in user.get_all_permissions()]
        assert [] == codenames
        instructors = Group.objects.get(name="Instructor")
        user.groups.add(instructors)
        user = User.objects.first()
        codenames = [strip_appname(perm) for perm in user.get_all_permissions()]
        assert sorted([
            EDIT_OWN_CONTENT[0],
            EDIT_OWN_LIVENESS[0],
            EDIT_OWN_PRICE[0]
        ]) == sorted(codenames)

    def test_get_courses(self):
        """Assert get_courses returns a list of courses available for purchase"""
        # Note that course1 is not live
        course1 = CourseFactory.create(live=False)
        ModuleFactory.create(
            price_without_tax=1,
            course=course1
        )
        course2 = CourseFactory.create(live=True)
        ModuleFactory.create(
            price_without_tax=1,
            course=course2
        )
        assert AuthorizationHelpers.get_courses() == [course2]

    def test_get_course_success(self):
        """Assert get_course returns a Course"""
        course = CourseFactory.create(live=True)
        ModuleFactory.create(
            price_without_tax=1,
            course=course
        )
        assert AuthorizationHelpers.get_course(course.uuid) == course

    def test_get_course_missing_uuid(self):
        """
        If the uuid doesn't match any course, return None.
        """
        assert AuthorizationHelpers.get_course("missing") is None

    def test_get_course_not_available(self):
        """
        If the course is not available for purchase, return None
        """
        # This course has no modules so it won't be available for purchase
        course = CourseFactory.create(live=True)
        assert AuthorizationHelpers.get_course(course.uuid) is None

    def test_is_owner(self):
        """
        Assert that is_owner returns true if a course is owned by a user, false otherwise.
        """
        user = User.objects.create_user(username="user")
        course = CourseFactory.create()
        assert not AuthorizationHelpers.is_owner(course, user)
        course.owners.add(user)
        assert AuthorizationHelpers.is_owner(course, user)

    def test_is_owner_anonymous(self):
        """
        Assert that is_owner returns false if user is anonymous.
        """
        user = AnonymousUser()
        course = CourseFactory.create()
        assert not AuthorizationHelpers.is_owner(course, user)

    def test_edit_content(self):
        """
        Assert that True is returned if user has permission to edit content for a course.
        """
        user = User.objects.create_user(username="user")
        course = CourseFactory.create()
        assert not AuthorizationHelpers.can_edit_own_content(course, user)

        # Instructor group has edit_own_content permission
        user.groups.add(Group.objects.get(name="Instructor"))
        # Need to do this to refresh user permissions
        user = User.objects.get(username="user")
        # Instructor does not own course
        assert not AuthorizationHelpers.can_edit_own_content(course, user)
        # Now that instructor is an owner this check should pass
        course.owners.add(user)
        user = User.objects.get(username="user")
        assert AuthorizationHelpers.can_edit_own_content(course, user)

    def test_edit_liveness(self):
        """
        Assert that True is returned if user has permission to edit liveness for a course.
        """
        user = User.objects.create_user(username="user")
        course = CourseFactory.create()
        assert not AuthorizationHelpers.can_edit_own_liveness(course, user)

        # Instructor group has edit_own_content permission
        user.groups.add(Group.objects.get(name="Instructor"))
        # Need to do this to refresh user permissions
        user = User.objects.get(username="user")
        # Instructor does not own course
        assert not AuthorizationHelpers.can_edit_own_liveness(course, user)
        # Now that instructor is an owner this check should pass
        course.owners.add(user)
        user = User.objects.get(username="user")
        assert AuthorizationHelpers.can_edit_own_liveness(course, user)

    def test_edit_price(self):
        """
        Assert that True is returned if user has permission to edit price for a course's module.
        """
        user = User.objects.create_user(username="user")
        course = CourseFactory.create()
        assert not AuthorizationHelpers.can_edit_own_price(course, user)

        # Instructor group has edit_own_content permission
        user.groups.add(Group.objects.get(name="Instructor"))
        # Need to do this to refresh user permissions
        user = User.objects.get(username="user")
        # Instructor does not own course
        assert not AuthorizationHelpers.can_edit_own_price(course, user)
        # Now that instructor is an owner this check should pass
        course.owners.add(user)
        user = User.objects.get(username="user")
        assert AuthorizationHelpers.can_edit_own_price(course, user)

    def test_can_purchase_course(self):
        """
        Assert behavior of AuthorizationHelpers.can_purchase_course
        """
        user = User.objects.create_user(username="user")
        course = CourseFactory.create(live=True)
        ModuleFactory.create(course=course, price_without_tax=1)
        assert AuthorizationHelpers.can_purchase_course(course, user)

    def test_cant_purchase_owned_course(self):
        """
        User can't purchase a course they own
        """
        user = User.objects.create_user(username="user")
        course = CourseFactory.create(live=True)
        ModuleFactory.create(course=course, price_without_tax=1)
        user.courses_owned.add(course)
        assert not AuthorizationHelpers.can_purchase_course(course, user)

    def test_cant_purchase(self):
        """
        User can't purchase a course that's not live
        """
        user = User.objects.create_user(username="user")
        course = CourseFactory.create(live=False)
        ModuleFactory.create(course=course, price_without_tax=1)
        assert not AuthorizationHelpers.can_purchase_course(course, user)
