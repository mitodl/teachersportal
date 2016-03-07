"""
Views for course availability listing.
"""
from __future__ import unicode_literals

from decimal import Decimal, DecimalException
import logging
from six.moves.urllib.parse import (  # pylint: disable=import-error
    urlparse,
    urlunparse,
)
from six import string_types

from django.conf import settings
from django.http.response import Http404
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from portal.models import Module
from portal.permissions import AuthorizationHelpers
from portal.serializers import (
    CourseSerializer,
    CourseSerializerReduced,
)


log = logging.getLogger(__name__)


def ccxcon_request():
    """
    Returns an object to make requests to CCXcon

    Returns:
        conn_info (requests_oauthlib.OAuth2Session): You can use this to make
            authenticated requests to the backing instance.
    """
    ccxcon_api = settings.CCXCON_API
    client_id = settings.CCXCON_OAUTH_CLIENT_ID
    client_secret = settings.CCXCON_OAUTH_CLIENT_SECRET

    # Get an oauth token. At some point in the future we may want to cache
    # this if it doesn't already so we don't make an unnecessary request here.
    client = BackendApplicationClient(client_id=client_id)
    oauth_ccxcon = OAuth2Session(client=client)
    token_url = urlunparse(urlparse(ccxcon_api)._replace(path="/o/token/"))
    oauth_ccxcon.fetch_token(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
    )

    return oauth_ccxcon


class CourseListView(ListAPIView):
    """
    Lists courses available for purchase
    """
    serializer_class = CourseSerializer
    # No authentication for course list, we want the public to see this
    permission_classes = ()

    def get_queryset(self):
        """A queryset for courses that are available for purchase"""

        return AuthorizationHelpers.get_courses(self.request.user)


class CourseDetailView(RetrieveAPIView):
    """
    Detail view for a course.
    """
    serializer_class = CourseSerializer
    serializer_class_anonymous = CourseSerializerReduced
    permission_classes = ()

    def get_serializer_class(self):
        """
        Overridden method to deal with different serializers in case of anonymous user
        """
        if self.request.user.is_anonymous():
            return self.serializer_class_anonymous
        return self.serializer_class

    def get_object(self):
        """
        Looks up information for a course from CCXCon and Course model.
        """
        uuid = self.kwargs['uuid']
        course = AuthorizationHelpers.get_course(uuid, self.request.user)
        if course is None:
            raise Http404

        return course

    # This method is a mammoth due to how much per-field validation we need to do
    # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    def patch(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Take PATCH requests, check permissions, and alter state based on them.
        """
        uuid = self.kwargs['uuid']
        data = request.data
        user = request.user
        # We shouldn't save any data until all validation checks out
        course_modified = False
        course = AuthorizationHelpers.get_course(uuid, user)
        if course is None:
            raise Http404

        if "live" in data:
            live = data['live']
            if not isinstance(live, bool):
                raise ValidationError("live must be a bool")
            if not AuthorizationHelpers.can_edit_own_liveness(course, user):
                raise ValidationError("User doesn't have permission to edit course liveness")

            course.live = live
            course_modified = True

        if "title" in data:
            title = data['title']
            if not isinstance(title, string_types) or title == '':
                raise ValidationError("title must be a non-empty string")
            if not AuthorizationHelpers.can_edit_own_content(course, user):
                raise ValidationError(
                    "User doesn't have permission to edit course descriptions or titles"
                )

            course.title = title
            course_modified = True

        if "description" in data:
            description = data['description']
            if not isinstance(description, string_types):
                raise ValidationError("description must be a string")
            if not AuthorizationHelpers.can_edit_own_content(course, user):
                raise ValidationError(
                    "User doesn't have permission to edit course descriptions or titles"
                )

            course.description = description
            course_modified = True

        modules_to_save = {}
        if "modules" in data:
            if not isinstance(data['modules'], list):
                raise ValidationError("modules must be a list of modules")

            for module_data in data['modules']:
                if not isinstance(module_data, dict):
                    raise ValidationError("Each module must be an object")
                if 'uuid' not in module_data:
                    raise ValidationError("Missing key uuid")
                if module_data['uuid'] in modules_to_save:
                    raise ValidationError("Duplicate module")

                try:
                    # We've already checked permissions for course above
                    # so this is a simple object lookup
                    module = Module.objects.get(
                        uuid=module_data['uuid'],
                        course=course
                    )
                except Module.DoesNotExist:
                    raise ValidationError(
                        "Unable to find module {uuid}".format(uuid=module_data['uuid'])
                    )

                if 'title' in module_data:
                    title = module_data['title']
                    if not isinstance(title, string_types) or title == '':
                        raise ValidationError("title must be a non-empty string")
                    if not AuthorizationHelpers.can_edit_own_content(course, user):
                        raise ValidationError(
                            "User doesn't have permission to edit course descriptions or titles"
                        )

                    module.title = title
                    modules_to_save[module.uuid] = module

                if 'price_without_tax' in module_data:
                    price_without_tax = module_data['price_without_tax']
                    if price_without_tax is not None:
                        if not isinstance(price_without_tax, string_types):
                            raise ValidationError('price_without_tax must be a string')
                        try:
                            price_without_tax = Decimal(price_without_tax)
                        except DecimalException:
                            raise ValidationError('price_without_tax is not a valid number')
                        if not price_without_tax.is_finite():
                            raise ValidationError('price_without_tax is not a valid number')
                        if price_without_tax < 0:
                            raise ValidationError('price_without_tax is not a valid number')

                    if not AuthorizationHelpers.can_edit_own_price(course, user):
                        raise ValidationError("User doesn't have permission to edit module price")

                    module.price_without_tax = price_without_tax
                    modules_to_save[module.uuid] = module

        if course_modified:
            course.save()
        for module in modules_to_save.values():
            module.save()
        return Response(status=200)
