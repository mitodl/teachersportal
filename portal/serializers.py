"""
Serializers for REST API
"""

from __future__ import unicode_literals

from rest_framework.serializers import (
    FloatField,
    ModelSerializer,
    SerializerMethodField,
    StringRelatedField,
)

from portal.models import Course, Module


# pylint: disable=abstract-method,no-init,old-style-class
class ModuleSerializer(ModelSerializer):
    """Serializer for Module"""
    # price_without_tax is a Decimal which renders to a string by default
    price_without_tax = FloatField()

    class Meta:  # pylint: disable=missing-docstring, too-few-public-methods
        model = Module
        fields = ('uuid', 'title', 'price_without_tax')


class CourseSerializer(ModelSerializer):
    """Serializer for Course"""

    modules = ModuleSerializer(many=True, read_only=True)
    edx_instance = StringRelatedField(source="instance")
    instructors = SerializerMethodField()

    class Meta:  # pylint: disable=missing-docstring, too-few-public-methods
        model = Course
        fields = (
            'title',
            'description',
            'uuid',
            'live',
            'modules',
            'course_id',
            'author_name',
            'overview',
            'image_url',
            'instructors',
            'edx_instance',
        )

    def get_instructors(self, obj):  # pylint: disable=no-self-use
        """Output the instructor JSON without escaping it"""
        return obj.instructors


class CourseSerializerReduced(ModelSerializer):
    """
    Serializer for Course with reduced information
    """

    class Meta:  # pylint: disable=missing-docstring, too-few-public-methods
        model = Course
        fields = (
            'title',
            'description',
            'uuid',
            'image_url',
        )
