"""
Views for product availability listing.
"""
from __future__ import unicode_literals

from oscar.apps.catalogue.models import Product
from rest_framework.generics import ListAPIView

from portal.serializers import ProductSerializer
from portal.util import (
    get_external_pk,
    get_price_without_tax,
    get_product_type,
    is_available_to_buy,
)


class ProductListView(ListAPIView):
    """
    Lists products available for purchase
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        """A queryset for products that are available for purchase"""

        return (
            {
                "title": product.title,
                "external_pk": get_external_pk(product),
                "product_type": get_product_type(product),
                "price_without_tax": get_price_without_tax(product),
                "parent_external_pk": get_external_pk(product.parent)
            }
            for product in Product.objects.order_by("date_created")
            if is_available_to_buy(product)
        )
