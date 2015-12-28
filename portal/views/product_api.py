"""
Views for product availability listing.
"""
from __future__ import unicode_literals

import json
from six.moves.urllib.parse import urlparse, urlunparse  # pylint: disable=import-error

from django.conf import settings
from django.http.response import Http404
from oauthlib.oauth2 import BackendApplicationClient
from oscar.apps.catalogue.models import Product
from requests_oauthlib import OAuth2Session
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from portal.serializers import ProductSerializer
from portal.util import (
    get_external_pk,
    get_product_type,
    make_upc,
    is_available_to_buy,
    product_as_json,
    COURSE_PRODUCT_TYPE,
    MODULE_PRODUCT_TYPE,
)


def fetch_ccxcon_info(product):
    """
    Fetch information from CCXCon about a product and its children. Note that
    this list is not filtered by availability to buy, that will be done in view.
    Args:
        product (Product): The product to get course or module information for.
    Returns:
        OrderedDict: Information from CCXCon, for either a module or course.
    """
    ccxcon_api = settings.CCXCON_API
    client_id = settings.CCXCON_OAUTH_CLIENT_ID
    client_secret = settings.CCXCON_OAUTH_CLIENT_SECRET
    allowed_module_keys = ('title', 'subchapters')
    allowed_course_keys = ('title', 'description', 'overview', 'image_url', 'author_name')

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

    product_type = get_product_type(product)
    if product_type == COURSE_PRODUCT_TYPE:
        response = oauth_ccxcon.get(
            "{api_base}v1/coursexs/{course_uuid}/".format(
                api_base=ccxcon_api,
                course_uuid=get_external_pk(product)
            )
        )
        data = json.loads(response.content.decode('utf-8'))
        # Whitelist of allowed keys to pass through
        ret = {
            product.upc: {
                k: v for k, v in data.items()
                if k in allowed_course_keys
            }
        }

        # Add module information to list
        response = oauth_ccxcon.get(
            "{api_base}v1/coursexs/{course_uuid}/modules/".format(
                api_base=ccxcon_api,
                course_uuid=get_external_pk(product)
            )
        )
        data = json.loads(response.content.decode('utf-8'))
        for module_info in data:
            ret[make_upc(MODULE_PRODUCT_TYPE, module_info['uuid'])] = {
                k: v for k, v in module_info.items()
                if k in allowed_module_keys
            }
        return ret
    elif product_type == MODULE_PRODUCT_TYPE:
        response = oauth_ccxcon.get(
            "{api_base}v1/coursexs/{course_uuid}/modules/{module_uuid}/".format(
                api_base=ccxcon_api,
                course_uuid=get_external_pk(product.parent),
                module_uuid=get_external_pk(product),
            )
        )
        if response.status_code != 200:
            raise Exception("CCXCon returned a non 200 status code {code}: {content}".format(
                code=response.status_code,
                content=response.content,
            ))
        data = json.loads(response.content.decode('utf-8'))
        return {
            product.upc: {k: v for k, v in data.items() if k in allowed_module_keys}
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

        return (
            product_as_json(product, {})
            for product in Product.objects.order_by("date_created")
            if is_available_to_buy(product)
        )


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
        product_uuid = self.kwargs['uuid']
        try:
            product = Product.objects.get(
                upc=product_uuid
            )
        except Product.DoesNotExist:
            raise Http404

        if not is_available_to_buy(product):
            raise Http404

        info = fetch_ccxcon_info(product)

        return product_as_json(product, info)
