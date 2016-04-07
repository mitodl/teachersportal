"""
Webhook handlers.
"""
from __future__ import unicode_literals
from six.moves.urllib import parse
import logging

from django.shortcuts import HttpResponse
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.mixins import (
    CreateModelMixin,
)

from portal.permissions import HmacPermission
from portal.models import Course
from portal.oauth2_auth import OAuth2Authentication
from portal.tasks import module_population
from portal.serializers import EdxCourseSerializer
import portal.webhooks as webhooks

log = logging.getLogger(__name__)


class EdxWebhookView(CreateModelMixin, viewsets.GenericViewSet):
    """
    Webhook incoming from edx, which happens on course create or update.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = EdxCourseSerializer
    authentication_classes = (OAuth2Authentication,)

    def post(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Incoming call from edX.

        Because edX won't know if they've sent the information already or not,
        this handles the update and create case.

        It also does a bit of data preparation, setting the edx_instance from
        the authenticated user and prefixing image paths with this
        edx_instance.
        """
        user = request.user
        data = request.data.copy()
        if not user.userinfo.edx_instance:
            log.info("User %s didn't have an associated edx_instance", request.user)
            raise ValidationError("User must have an associated edx_instance.")
        data['instance'] = user.userinfo.edx_instance_id

        if not data.get('image_url'):
            log.info("Didn't specify an image_url")
            raise ValidationError("You must specify an image_url")
        data['image_url'] = parse.urljoin(
            user.userinfo.edx_instance.instance_url, data['image_url'])
        data['edx_course_id'] = data.get('course_id')
        del data['course_id']

        # These two if blocks are majoritively copied directly from the source's
        # underlying mixins. It allows us to overwrite how we get the instance
        # to update without making a complex `get_object` override. Beyond that,
        # it allows us to not mutate the request.data object.
        if Course.objects.filter(edx_course_id=data['edx_course_id']).exists():
            # Mostly duped from rest_framework.mixins.UpdateModelMixin
            partial = kwargs.pop('partial', False)
            instance = Course.objects.get(edx_course_id=data['edx_course_id'])
            serializer = self.get_serializer(
                instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            module_population.delay(serializer.instance.edx_course_id)
            return Response(serializer.data)
        else:
            # Duped from rest_framework.mixins.CreateModelMixin for clarity.
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            module_population.delay(serializer.instance.edx_course_id)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class WebhooksCCXConView(APIView):
    """
    Accepts messages from CCXCon
    """

    # Note that this does not include IsAuthenticated. We use only hmac
    # signatures to verify authentication for this API.
    permission_classes = (HmacPermission, )

    def post(self, request):  # pylint: disable=no-self-use
        """
        Handle messages from CCXCon.

        Args:
            request (HttpRequest)
        Returns:
            HttpResponse
        """
        # We'll probably want to move this logic out of an if statement when
        # it gets complicated.
        message = request.data
        for key in ('type', 'action', 'payload'):
            if key not in message:
                raise ValidationError("Missing key {key}".format(key=key))
        try:
            hook = getattr(webhooks, message['type'].lower())
        except AttributeError:
            raise ValidationError("No handler for type {type}".format(
                type=message['type']))

        hook(message['action'], message['payload'])

        # On success webhooks won't return anything since CCXCon
        # can't do anything with this information.
        return HttpResponse(status=200)
