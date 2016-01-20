"""
Views for product availability listing.
"""
from __future__ import unicode_literals

import logging
import json
from six.moves.urllib.parse import urlparse, urlunparse  # pylint: disable=import-error

from django.conf import settings
from django.http.response import Http404
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from portal.models import Course, Module
from portal.serializers import ProductSerializer
from portal.util import (
    get_product_type,
    make_qualified_id,
    make_external_pk,
    course_as_product_json,
    module_as_product_json,
    COURSE_PRODUCT_TYPE,
    MODULE_PRODUCT_TYPE,
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


def fetch_ccxcon_info(qualified_id):
    """
    Fetch information from CCXCon about a product and its children. Note that
    this list is not filtered by availability to buy, that will be done in view.
    Args:
        qualified_id (str): The qualified_id
    Returns:
        dict: Information from CCXCon, for either a module or course.
    """
    allowed_module_keys = ('title', 'subchapters')
    allowed_course_keys = ('title', 'description', 'overview', 'image_url', 'author_name')
    oauth_ccxcon = ccxcon_request()
    ccxcon_api = settings.CCXCON_API

    product_type = get_product_type(qualified_id)
    uuid = make_external_pk(product_type, qualified_id)
    if product_type == COURSE_PRODUCT_TYPE:
        response = oauth_ccxcon.get(
            "{api_base}v1/coursexs/{course_uuid}/".format(
                api_base=ccxcon_api,
                course_uuid=uuid
            )
        )
        data = json.loads(response.content.decode('utf-8'))
        # Whitelist of allowed keys to pass through
        ret = {
            qualified_id: {
                k: v for k, v in data.items()
                if k in allowed_course_keys
            }
        }

        # Add module information to list
        response = oauth_ccxcon.get(
            "{api_base}v1/coursexs/{course_uuid}/modules/".format(
                api_base=ccxcon_api,
                course_uuid=uuid
            )
        )
        data = json.loads(response.content.decode('utf-8'))
        for module_info in data:
            ret[make_qualified_id(MODULE_PRODUCT_TYPE, module_info['uuid'])] = {
                k: v for k, v in module_info.items()
                if k in allowed_module_keys
            }
        return ret
    elif product_type == MODULE_PRODUCT_TYPE:
        module = Module.objects.get(uuid=uuid)

        response = oauth_ccxcon.get(
            "{api_base}v1/coursexs/{course_uuid}/modules/{module_uuid}/".format(
                api_base=ccxcon_api,
                course_uuid=module.course.uuid,
                module_uuid=uuid,
            )
        )
        if response.status_code != 200:
            raise Exception("CCXCon returned a non 200 status code {code}: {content}".format(
                code=response.status_code,
                content=response.content,
            ))
        data = json.loads(response.content.decode('utf-8'))
        return {
            qualified_id: {k: v for k, v in data.items() if k in allowed_module_keys}
        }
    else:
        raise Exception("Unexpected product type")


class ProductListView(ListAPIView):
    """
    Lists products available for purchase
    """
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """A queryset for products that are available for purchase"""

        pairs = [
            (course_as_product_json(course, {}), course.created_at)
            for course in Course.objects.order_by("created_at")
            if course.is_available_for_purchase
        ] + [
            (module_as_product_json(module, {}), module.created_at)
            for module in Module.objects.order_by("created_at")
            if module.is_available_for_purchase
        ]

        pairs = sorted(pairs, key=lambda x: x[1])
        return [pair[0] for pair in pairs]


class ProductDetailView(RetrieveAPIView):
    """
    Detail view for a product.
    """
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """
        Looks up information for product from CCXCon and Product model.
        """
        qualified_id = self.kwargs['qualified_id']
        product_type = get_product_type(qualified_id)
        if product_type is None:
            log.debug("Invalid product type")
            raise Http404
        uuid = make_external_pk(product_type, qualified_id)
        if product_type == COURSE_PRODUCT_TYPE:
            try:
                course = Course.objects.get(uuid=uuid)
            except Course.DoesNotExist:
                log.debug("Couldn't find a course with uuid %s in the portal", uuid)
                raise Http404

            if not course.is_available_for_purchase:
                log.debug("Course %s isn't available for sale.", course)
                raise Http404

            info = fetch_ccxcon_info(qualified_id)

            return course_as_product_json(course, info)
        elif product_type == MODULE_PRODUCT_TYPE:
            try:
                module = Module.objects.get(uuid=uuid)
            except Module.DoesNotExist:
                log.debug("Couldn't find a module with uuid %s in the portal", uuid)
                raise Http404

            if not module.is_available_for_purchase:
                log.debug("Module %s isn't available for sale.", uuid)
                raise Http404

            info = fetch_ccxcon_info(qualified_id)

            return module_as_product_json(module, info)
        else:
            raise ValidationError("Unexpected product type")
