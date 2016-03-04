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


# Note that the codename for each permission is exposed in our REST API, in order
# to tell the UI what changes to make based on user permissions.
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
SEE_OWN_NOT_LIVE = (
    'see_own_not_live',
    'Can see courses which are not live'
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

    @classmethod
    def _is_visible(cls, course, user):
        """
        Helper method to contain course visibility logic.
        """
        return course.is_available_for_purchase or (
            cls.is_owner(course, user) and cls.can_see_own_not_live(course, user)
        )

    @classmethod
    def get_courses(cls, user):
        """
        Returns a list of courses accessible by user.

        Args:
            user (django.contrib.auth.models.User): Logged in user

        Returns:
            list: A list of courses
        """
        from portal.models import Course
        return [
            course for course in Course.objects.all()
            if cls._is_visible(course, user)
        ]

    @classmethod
    def get_course(cls, course_uuid, user):
        """
        Returns a course, or None if no course exists or is not available for purchase.

        Args:
            course_uuid (str): A course UUID
            user (django.contrib.auth.models.User): Logged in user
        Returns:
            Course: A course, or None if course is not accessible to the user
        """
        from portal.models import Course
        try:
            course = Course.objects.get(uuid=course_uuid)
        except Course.DoesNotExist:
            log.debug("Couldn't find a course with uuid %s in the portal", course_uuid)
            return None

        if not cls._is_visible(course, user):
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
        return course.owners.filter(id=user.id).exists()

    @classmethod
    def can_edit_own_price(cls, course, user):
        """
        Does user have permission to edit their own course's price?

        Args:
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
    def can_edit_own_content(cls, course, user):
        """
        Does user have permission to edit their own course's descriptive content?

        Args:
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
    def can_edit_own_liveness(cls, course, user):
        """
        Does user have permission to edit their own course's live flag?

        Args:
            course (Course): A course
            user (django.contrib.auth.models.User): A User

        Returns:
            bool: True if user has this permission for this course.
        """
        return (
            user.has_perm("portal.{}".format(EDIT_OWN_LIVENESS[0])) and
            cls.is_owner(course, user)
        )

    @classmethod
    def can_purchase_course(cls, course, user):
        """
        Does user have the ability to purchase a course?

        Args:
            course (Course): A course
            user (django.contrib.auth.models.User): A User

        Returns:
            bool: True if user has permission to buy a course
        """
        return not cls.is_owner(course, user) and course.is_available_for_purchase

    @classmethod
    def can_see_own_not_live(cls, course, user):
        """
        Does user have permission to see their own courses which aren't live?

        Args:
            course (Course): A course
            user (django.contrib.auth.models.User): A User

        Returns:
            bool: True if user has this permission for this course.
        """
        return (
            user.has_perm("portal.{}".format(SEE_OWN_NOT_LIVE[0])) and
            cls.is_owner(course, user)
        )
