"""
Serializers for REST API
"""

from __future__ import unicode_literals

from rest_framework.serializers import (
    Serializer,
    CharField,
    FloatField,
    DictField,
    ListField,
)


# pylint: disable=abstract-method
class ProductSerializer(Serializer):
    """Serializer for Product"""

    upc = CharField()
    title = CharField()
    description = CharField()
    external_pk = CharField()
    product_type = CharField()
    price_without_tax = FloatField()
    parent_upc = CharField()
    info = DictField()
    children = ListField()
