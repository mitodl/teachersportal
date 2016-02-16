"""
Views for course availability listing.
"""
from __future__ import unicode_literals

import logging
import json
from six.moves.urllib.parse import urlparse, urlunparse  # pylint: disable=import-error

from django.conf import settings
from django.http.response import Http404
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.status import HTTP_200_OK

from portal.permissions import AuthorizationHelpers
from portal.serializers import (
    CourseSerializer,
    CourseSerializerReduced,
)
from portal.util import (
    course_as_dict,
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


def filter_ccxcon_course_info(course_info):
    """
    Filter course info
    Args:
        course_info (dict): CCXCon course info

    Returns:
        The CCXCon course info with only allowed fields
    """
    allowed_course_keys = ('title', 'description', 'overview', 'image_url', 'author_name')
    return {
        k: v for k, v in course_info.items()
        if k in allowed_course_keys
    }


def filter_ccxcon_module_info(module_info):
    """
    Filter module info

    Args:
        module_info (dict): CCXCon module info

    Returns:
        The CCXCon module info with only allowed fields
    """
    allowed_module_keys = ('title', 'subchapters')
    return {
        k: v for k, v in module_info.items()
        if k in allowed_module_keys
    }


def fetch_ccxcon_info(uuid):
    """
    Fetch information from CCXCon about a course and its modules. Note that
    this list is not filtered by availability to buy, that will be done in view.
    Args:
        uuid (str): The course uuid
    Returns:
        tuple:
            (dict, dict) where
            Item one is information from CCXCon for a course,
            Item two is the information for each module for that course
    """
    oauth_ccxcon = ccxcon_request()
    ccxcon_api = settings.CCXCON_API

    course_url = "{api_base}v1/coursexs/{course_uuid}/".format(
        api_base=ccxcon_api,
        course_uuid=uuid
    )
    response = oauth_ccxcon.get(course_url)
    if response.status_code != HTTP_200_OK:
        log.info(
            "Unable to fetch course from CCXCon: url: %s, code: %s, content: %s",
            course_url,
            response.status_code,
            response.content.decode('utf-8')
        )
        raise Exception("CCXCon returned a non 200 status code {code}: {content}".format(
            code=response.status_code,
            content=response.content,
        ))
    course_info = json.loads(response.content.decode('utf-8'))
    # Whitelist of allowed keys to pass through

    # Add module information to list
    modules_url = "{api_base}v1/coursexs/{course_uuid}/modules/".format(
        api_base=ccxcon_api,
        course_uuid=uuid
    )
    response = oauth_ccxcon.get(modules_url)
    if response.status_code != HTTP_200_OK:
        log.info(
            "Unable to fetch modules from CCXCon: url: %s, code: %s, content: %s",
            modules_url,
            response.status_code,
            response.content.decode('utf-8')
        )
        raise Exception("CCXCon returned a non 200 status code {code}: {content}".format(
            code=response.status_code,
            content=response.content,
        ))
    data = json.loads(response.content.decode('utf-8'))
    modules_info = {}
    for module_info in data:
        uuid = module_info['uuid']
        modules_info[uuid] = module_info

    return course_info, modules_info


class CourseListView(ListAPIView):
    """
    Lists courses available for purchase
    """
    serializer_class = CourseSerializer
    # No authentication for course list, we want the public to see this
    permission_classes = ()

    def get_queryset(self):
        """A queryset for courses that are available for purchase"""

        return [
            course_as_dict(course)
            for course in AuthorizationHelpers.get_courses(self.request.user)
        ]


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

        course_info, modules_info = fetch_ccxcon_info(uuid)

        return course_as_dict(
            course,
            filter_ccxcon_course_info(course_info),
            {
                uuid: filter_ccxcon_module_info(module)
                for uuid, module in modules_info.items()
            }
        )
