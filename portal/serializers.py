"""
Serializers for REST API
"""

from __future__ import unicode_literals

from rest_framework.serializers import (
    Serializer,
    CharField,
    DecimalField,
)


# pylint: disable=abstract-method
class ProductSerializer(Serializer):
    """Serializer for Product"""

    title = CharField()
    external_pk = CharField()
    product_type = CharField()
    price_without_tax = DecimalField(max_digits=20, decimal_places=2)
    parent_external_pk = CharField()
