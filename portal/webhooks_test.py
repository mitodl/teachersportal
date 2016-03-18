"""
Tests for webhook handlers
"""
# pylint: disable=no-self-use
from __future__ import unicode_literals
from copy import deepcopy

from django.test import TestCase
from django.contrib.auth.models import User
import pytest
from rest_framework.exceptions import ValidationError

from portal.models import Course, Module

from .factories import CourseFactory, ModuleFactory
from .webhooks import course as course_webhook, module as module_webhook


class CourseWebhookTests(TestCase):
    """
    Test for the Course incoming webhook
    """
    valid_data = {
        'title': 'title',
        'external_pk': 'uuid',
        'edx_course_id': 'course-v1:ColumbiaX+DS101X+3T2015',
        'instance': 'instance',
        'course_id': 'course_id',
        'author_name': 'author_name',
        'overview': 'overview',
        'description': 'description',
        'image_url': 'image_url',
        'instructors': ['one', 'two', 'three'],
    }

    def test_unknown_action_errors(self):
        """Unknown actions error"""
        with pytest.raises(ValidationError) as exc:
            course_webhook('zammie', {})
        assert 'Unknown action zammie' in str(exc.value)

    def test_delete_deletes_record(self):
        """Delete should properly delete"""
        course = CourseFactory.create()
        course_webhook('delete', {'external_pk': course.uuid})

        assert not Course.objects.filter(pk=course.pk).exists()

    def test_delete_nonexistent_silence(self):
        """Deleting non-existent records are silent"""
        # Should pass without Exception.
        course_webhook('delete', {'external_pk': 'asdf'})

    def test_delete_bad_format_errors(self):
        """Deleting with bad payload errors"""
        with pytest.raises(ValidationError) as exc:
            course_webhook('delete', None)
        assert 'Invalid value for payload' in str(exc.value)

    def test_update_creates_if_dne(self):
        """Update creates if it doesn't exist"""
        course_webhook('update', self.valid_data)
        course = Course.objects.get(uuid='uuid')
        assert course.title == 'title'
        assert course.uuid == 'uuid'
        assert course.instance.instance_url == 'instance'
        assert course.course_id == 'course_id'
        assert course.author_name == 'author_name'
        assert course.overview == 'overview'
        assert course.description == 'description'
        assert course.image_url == 'image_url'
        assert course.instructors == ['one', 'two', 'three']
        assert course.edx_course_id == 'course-v1:ColumbiaX+DS101X+3T2015'
        assert not course.live
        assert not course.owners.exists()

    def test_update_updates_if_exists(self):
        """Update updates if it exists"""
        course = CourseFactory.create(
            uuid=self.valid_data['external_pk'],
            title='test',
            live=True,
            instance__instance_url=self.valid_data['instance'],
        )
        user = User.objects.create(username='asdf')
        course.owners.add(user)

        course_webhook('update', self.valid_data)

        course = Course.objects.get(uuid='uuid')
        assert course.title == 'title'
        assert course.uuid == 'uuid'
        assert course.instance.instance_url == 'instance'
        assert course.course_id == 'course_id'
        assert course.author_name == 'author_name'
        assert course.overview == 'overview'
        assert course.description == 'description'
        assert course.image_url == 'image_url'
        assert course.instructors == ['one', 'two', 'three']
        assert course.owners.count() == 1
        assert course.owners.all()[0].id == user.id
        assert course.live

    def test_errors_changing_instance(self):
        """Update errors if changing backinginstance"""
        CourseFactory.create(
            uuid=self.valid_data['external_pk'],
            instance__instance_url='zammie',
        )

        with pytest.raises(ValidationError) as exc:
            course_webhook('update', self.valid_data)
        assert 'Instance cannot be changed' in str(exc.value)

    def test_update_errors_bad_payload(self):
        """Update errors when payload invalid"""
        with pytest.raises(ValidationError) as exc:
            course_webhook('update', None)
        assert 'Invalid payload' in str(exc.value)

    def test_errors_keys_required(self):
        """If there's no external_pk, error"""
        with pytest.raises(ValidationError) as exc:
            course_webhook('update', {})
        assert "Missing key" in str(exc.value)

    def test_update_instance_mandatory(self):
        """Instance must be present"""
        params = deepcopy(self.valid_data)
        params['instance'] = ''
        with pytest.raises(ValidationError) as exc:
            course_webhook('update', params)
        assert "Instance must be a non-empty string" in str(exc.value)

    def test_update_uuid_required(self):
        """Errors if missing the uuid"""
        params = deepcopy(self.valid_data)
        params['external_pk'] = ''
        with pytest.raises(ValidationError) as exc:
            course_webhook('update', params)
        assert 'Invalid external_pk' in str(exc.value)


class ModuleWebhookTests(TestCase):
    """
    Test for the Module incoming webhook
    """
    valid_payload = {
        'title': 'module_title',
        "external_pk": 'uuid',
        'course_external_pk': 'course-uuid',
        'locator_id': 'testing',
    }

    def test_unknown_action_errors(self):
        """Unknown action errors"""
        with pytest.raises(ValidationError) as exc:
            module_webhook('nope', {})
        assert 'Unknown action' in str(exc.value)

    def test_delete_invalid_payload(self):
        """Valid payload required for delete"""
        with pytest.raises(ValidationError) as exc:
            module_webhook('delete', None)
        assert 'Invalid value for payload' in str(exc.value)

    def test_delete_require_external_pk(self):
        """Delete must have external pk"""
        with pytest.raises(ValidationError) as exc:
            module_webhook('delete', {})
        assert 'Missing key' in str(exc.value)

    def test_delete_deletes_record(self):
        """Delete happy path"""
        module = ModuleFactory.create(uuid='uuid')
        module_webhook('delete', {'external_pk': 'uuid'})
        assert not Module.objects.filter(pk=module.pk).exists()

    def test_update_non_dict(self):
        """Update: payload must be dict"""
        with pytest.raises(ValidationError) as exc:
            module_webhook('update', None)
        assert 'Invalid key' in str(exc.value)

    def test_update_must_have_uuid(self):
        """Update requires uuid"""
        no_uuid = deepcopy(self.valid_payload)
        no_uuid['external_pk'] = ''
        with pytest.raises(ValidationError) as exc:
            module_webhook('update', no_uuid)
        assert 'Invalid external_pk' in str(exc.value)

    def test_update_creates_module(self):
        """Update creates if not exists"""
        CourseFactory.create(uuid='course-uuid')
        module_webhook('update', self.valid_payload)
        assert Module.objects.count() == 1
        module = Module.objects.all()[0]
        assert module.title == self.valid_payload['title']
        assert module.uuid == self.valid_payload['external_pk']
        assert module.course.uuid == self.valid_payload['course_external_pk']
        assert module.locator_id == self.valid_payload['locator_id']
        assert module.price_without_tax is None

    def test_update_wont_change_course(self):
        """Update wont change course"""
        CourseFactory.create(uuid='course-uuid')
        ModuleFactory.create(
            uuid='uuid', course__uuid='different-uuid')
        with pytest.raises(ValidationError) as exc:
            module_webhook('update', self.valid_payload)
        assert 'Invalid course_external_pk' in str(exc.value)

    def test_update_updates_module(self):
        """Update updates the module if it exists"""
        module = ModuleFactory.create(
            uuid='uuid',
            course__uuid='course-uuid',
            title='different',
            price_without_tax=0,
        )
        module_webhook('update', self.valid_payload)
        assert Module.objects.filter(
            pk=module.pk, title=self.valid_payload['title']
        ).exists()
        assert Module.objects.count() == 1
        assert Module.objects.all()[0].price_without_tax == 0

    def test_update_valid_course(self):
        """Update requires valid course"""
        ModuleFactory.create(
            uuid='uuid', course__uuid='course-uuid', title='different')
        wrong_course = deepcopy(self.valid_payload)
        wrong_course['course_external_pk'] = 'wrong course here'
        with pytest.raises(ValidationError) as exc:
            module_webhook('update', wrong_course)
        assert 'Invalid course_external_pk' in str(exc.value)
