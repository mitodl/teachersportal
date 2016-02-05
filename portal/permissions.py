"""
Permissions classes for REST API
"""

from __future__ import unicode_literals
import hashlib
import hmac
import logging

from django.conf import settings
from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes
from rest_framework.permissions import BasePermission
# Due to circular dependency issues we import portal.models in each function below


log = logging.getLogger(__name__)


EDIT_OWN_CONTENT = (
    'edit_own_content',
    'Can edit descriptive content for a course and related modules'
)
EDIT_OWN_LIVENESS = (
    'edit_own_liveness',
    'Can mark a course live or not live'
)
EDIT_OWN_PRICE = (
    'edit_own_price',
    'Can edit the price of a module'
)


class HmacPermission(BasePermission):
    """
    Verify hmac signature.
    """
    def has_permission(self, request, view):
        try:
            signature = request.META['HTTP_X_CCXCON_SIGNATURE']
        except KeyError:
            log.info("Request did not have the necessary X-CCXCON-SIGNATURE header")
            return False

        computed = hmac.new(
            force_bytes(settings.CCXCON_WEBHOOKS_SECRET),
            force_bytes(request.body.decode('utf-8')),
            hashlib.sha1).hexdigest()
        is_valid = constant_time_compare(signature, computed)
        if not is_valid:
            log.debug("Request did not have a valid hmac signature. %s != %s", signature, computed)

        return is_valid


class AuthorizationHelpers(object):
    """
    Functions used to ensure permissions are applied.
    """

    @staticmethod
    def get_courses():
        """
        Returns a list of courses accessible by user.

        Returns:
            list: A list of courses
        """
        from portal.models import Course
        return [
            course for course in Course.objects.all()
            if course.is_available_for_purchase
        ]

    @staticmethod
    def get_course(course_uuid):
        """
        Returns a course, or None if no course exists or is not available for purchase.

        Args:
            course_uuid (str): A course
        Returns:
            Course: A course, or None if course is not accessible to the user
        """
        from portal.models import Course
        try:
            course = Course.objects.get(uuid=course_uuid)
        except Course.DoesNotExist:
            log.debug("Couldn't find a course with uuid %s in the portal", course_uuid)
            return None

        if not course.is_available_for_purchase:
            log.debug("Course %s isn't available for sale.", course)
            return None
        return course

    @staticmethod
    def is_owner(course, user):
        """
        Returns True if user owns the course.
        Args:
            course (Course): A course
            user (django.contrib.auth.models.User): A User

        Returns:
            bool: True if the user owns the course
        """
        return user.courses_owned.filter(id=course.id).exists()

    @classmethod
    def has_edit_own_price_perm(cls, course, user):
        """
        Does user have permission to edit their own course's price?

        Args:
            cls (AuthorizationHelpers): This class
            course (Course): A course
            user (django.contrib.auth.models.User): A User

        Returns:
            bool: True if user has this permission for this course.
        """
        return (
            user.has_perm("portal.{}".format(EDIT_OWN_PRICE[0])) and
            cls.is_owner(course, user)
        )

    @classmethod
    def has_edit_own_content_perm(cls, course, user):
        """
        Does user have permission to edit their own course's descriptive content?

        Args:
            cls (AuthorizationHelpers): This class
            course (Course): A course
            user (django.contrib.auth.models.User): A User

        Returns:
            bool: True if user has this permission for this course.
        """
        return (
            user.has_perm("portal.{}".format(EDIT_OWN_CONTENT[0])) and
            cls.is_owner(course, user)
        )

    @classmethod
    def has_edit_own_liveness_perm(cls, course, user):
        """
        Does user have permission to edit their own course's live flag?

        Args:
            cls (AuthorizationHelpers): This class
            course (Course): A course
            user (django.contrib.auth.models.User): A User

        Returns:
            bool: True if user has this permission for this course.
        """
        return (
            user.has_perm("portal.{}".format(EDIT_OWN_LIVENESS[0])) and
            cls.is_owner(course, user)
        )
