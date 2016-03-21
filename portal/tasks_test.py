"""
Module Population Tests
"""
# pylint: disable=no-self-use,no-value-for-parameter
from copy import deepcopy
import json
import os

import mock
import pytest
from requests.exceptions import RequestException
from django.test import TestCase
from celery.exceptions import Retry

from .tasks import module_population, get_backoff
from .factories import CourseFactory, ModuleFactory
from .models import Module


@pytest.mark.parametrize("retries,backoff", [
    (0, 2 * 60),
    (1, 5 * 60),
    (2, 10 * 60),
    (3, 17 * 60),
    (4, 26 * 60),
])
def test_get_backoff(retries, backoff):
    """
    Validate backoff calculates timeouts correctly.
    """
    assert get_backoff(retries) == backoff


class ModulePopulationTests(TestCase):
    """
    Module Population Tests
    """
    def setUp(self):
        # create course
        filename = os.path.join(
            os.path.dirname(__file__), 'fixtures/course_structure.json')
        with open(filename) as file_obj:
            self.structure_response = json.loads(file_obj.read())

    def test_course_delete_silent(self):
        """
        Course delete should return silently.
        """
        try:
            module_population('doesnt_exist')
        except Exception as exc:  # pylint: disable=broad-except
            self.fail(
                "Should not error on missing course [aka delete]. "
                "Error: {}".format(exc))

    def test_request_error_exceptions(self):
        """
        Errors doing request should surface the exception.
        """
        course = CourseFactory.create()
        with mock.patch('portal.tasks.requests', autospec=True) as m_req:
            m_req.get.side_effect = RequestException()

            with pytest.raises(RequestException):
                module_population(course.course_id)

    @mock.patch('portal.tasks.get_access_token', autospec=True)
    @mock.patch('portal.tasks.requests', autospec=True)
    def test_request_non_200_exceptions(self, m_req, m_gat):
        """
        non 200 status codes should throw exception and retry.
        """
        course = CourseFactory.create()
        m_gat.return_value = 'asdf'
        m_req.get.return_value.status_code = 400

        with pytest.raises(Retry):
            module_population(course.course_id)

    @mock.patch('portal.tasks.get_access_token', autospec=True)
    @mock.patch('portal.tasks.requests', autospec=True)
    def test_modules_created(self, m_req, m_gat):
        """
        Modules are created.
        """
        m_gat.return_value = 'asdf'
        course = CourseFactory.create()
        m_req.get.return_value.status_code = 200
        m_req.get.return_value.json = lambda: self.structure_response

        module_population(course.course_id)

        assert Module.objects.count() == 6

    @mock.patch('portal.tasks.get_access_token', autospec=True)
    @mock.patch('portal.tasks.requests', autospec=True)
    def test_deleted_modules_removed(self, m_req, m_gat):
        """
        If module isn't in payload, it should be deleted.
        """
        course = CourseFactory.create()
        ModuleFactory.create(course=course)
        m_gat.return_value = 'asdf'
        m_req.get.return_value.status_code = 200
        m_req.get.return_value.json = lambda: {
            'blocks': {'test': {'children': []}}, 'root': 'test'
        }

        module_population(course.course_id)

        assert Module.objects.count() == 0

    @mock.patch('portal.tasks.get_access_token', autospec=True)
    @mock.patch('portal.tasks.requests', autospec=True)
    def test_module_ordering(self, m_req, m_gat):
        """
        Modules should be ordered based on position in the payload.
        """
        m_gat.return_value = 'asdf'
        course = CourseFactory.create()
        m_req.get.return_value.status_code = 200
        m_req.get.return_value.json = lambda: self.structure_response

        module_population(course.course_id)

        modules = course.modules.all().order_by('order')
        actual = [x.title for x in modules]
        expected = ["Introduction",
                    "Example Week 1: Getting Started",
                    "Example Week 2: Get Interactive",
                    "Example Week 3: Be Social",
                    "About Exams and Certificates",
                    "holding section"]
        assert actual == expected

    @mock.patch('portal.tasks.get_access_token', autospec=True)
    @mock.patch('portal.tasks.requests', autospec=True)
    def test_module_reordering(self, m_req, m_gat):
        """
        If modules change order, the db should update accordingly.
        """
        course = CourseFactory.create()
        m_gat.return_value = 'asdf'
        m_req.get.return_value.status_code = 200
        m_req.get.return_value.json = lambda: self.structure_response

        # initial population. Known to work via `test_module_ordering`
        module_population(course.course_id)

        m_req.get.return_value.status_code = 200
        resp = self.structure_response.copy()
        resp['blocks'][resp['root']]['children'].sort()
        m_req.get.return_value.json = lambda: resp

        module_population(course.course_id)

        modules = course.modules.all().order_by('order')
        actual = [x.title for x in modules]
        expected = [
            "About Exams and Certificates",
            "holding section",
            "Introduction",
            "Example Week 2: Get Interactive",
            "Example Week 1: Getting Started",
            "Example Week 3: Be Social",
        ]
        assert actual == expected

    @mock.patch('portal.tasks.get_access_token', autospec=True)
    @mock.patch('portal.tasks.requests', autospec=True)
    def test_dont_populate_hidden(self, m_req, m_gat):
        """
        If some modules are marked as hidden, don't populate them.
        """
        # Find a chapter block
        first_module_locator_id = None
        first_module_title = None
        for block in self.structure_response['blocks'].values():
            if block['type'] == 'chapter':
                first_module_locator_id = block['id']
                first_module_title = block['display_name']
                break

        response_with_hidden = deepcopy(self.structure_response)
        response_with_hidden['blocks'][first_module_locator_id][
            'visible_to_staff_only'] = True

        course = CourseFactory.create()
        m_req.get.return_value.status_code = 200
        m_req.get.return_value.json = lambda: response_with_hidden
        m_gat.return_value = 'asdf'

        # initial population. Known to work via `test_module_ordering`
        module_population(course.course_id)

        # Expect that the hidden module's title is not present
        titles = {module.title for module in course.modules.all()}
        assert first_module_title not in titles

    @mock.patch('portal.tasks.get_access_token', autospec=True)
    @mock.patch('portal.tasks.requests', autospec=True)
    def test_delete_existing_hidden(self, m_req, m_gat):
        """
        If some modules are newly marked as hidden, delete them.
        """
        course = CourseFactory.create()
        m_gat.return_value = 'asdf'
        m_req.get.return_value.status_code = 200
        m_req.get.return_value.json = lambda: self.structure_response

        # initial population. Known to work via `test_module_ordering`
        module_population(course.course_id)

        # Change a chapter to be hidden instead
        first_module = Module.objects.first()
        first_module_locator_id = first_module.locator_id
        first_module_title = first_module.title
        response_with_hidden = deepcopy(self.structure_response)
        response_with_hidden['blocks'][first_module_locator_id][
            'visible_to_staff_only'] = True

        m_req.get.return_value.status_code = 200
        m_req.get.return_value.json = lambda: response_with_hidden

        # initial population. Known to work via `test_module_ordering`
        module_population(course.course_id)

        # Expect that the hidden module's title is not present
        titles = {module.title for module in course.modules.all()}
        assert first_module_title not in titles
