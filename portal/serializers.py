"""
Serializers for REST API
"""

from __future__ import unicode_literals

from rest_framework.serializers import (
    Serializer,
    BooleanField,
    CharField,
    DictField,
    ListField,
)


# pylint: disable=abstract-method
class CourseSerializer(Serializer):
    """Serializer for Course"""

    title = CharField()
    description = CharField()
    uuid = CharField()
    info = DictField()
    live = BooleanField()
    modules = ListField()


class CourseSerializerReduced(Serializer):
    """
    Serializer for Course with reduced information
    """

    title = CharField()
    description = CharField()
    info = DictField()
    uuid = CharField()
