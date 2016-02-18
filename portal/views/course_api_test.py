"""
Tests for Course API
"""

from __future__ import unicode_literals

from decimal import Decimal
import json
from mock import patch
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
import requests_mock

from portal.factories import CourseFactory, ModuleFactory
from portal.models import Course, Module
from portal.views.course_api import (
    filter_ccxcon_course_info,
    filter_ccxcon_module_info,
)
from portal.views.base import CourseTests, FAKE_CCXCON_API
from portal.views.util import as_json
from portal.util import (
    course_as_dict,
)


class CourseAPIGETTests(CourseTests):
    """
    Tests for course API, GET method
    """

    def setUp(self):
        """
        Set up the courses
        """
        super(CourseAPIGETTests, self).setUp()
        self.course.live = True
        self.course.save()

        credentials = {"username": "auser", "password": "apass"}
        self.teacher = User.objects.create_user(**credentials)
        self.client.login(**credentials)

    def validate_course_api(self, courses_from_api):  # pylint: disable=no-self-use
        """
        Helper function to verify 200 and return list of courses.
        """
        for course_from_api in courses_from_api:
            # Assert consistency between database and what API endpoint is returning.
            course = Course.objects.get(uuid=course_from_api['uuid'])
            assert course.title == course_from_api['title']
            assert course.description == course_from_api['description']

            modules_from_api = sorted(course_from_api['modules'], key=lambda x: x['uuid'])
            for module_from_api in modules_from_api:
                module = Module.objects.get(uuid=module_from_api['uuid'])
                assert module.title == module_from_api['title']

        return courses_from_api

    def test_not_live(self):
        """
        Make sure API shows no courses if none are live.
        """
        self.course.live = False
        self.course.save()

        resp = self.client.get(reverse("course-list"))
        assert resp.status_code == 200, resp.content.decode('utf-8')
        courses_from_api = as_json(resp)

        self.validate_course_api(courses_from_api)
        assert courses_from_api == []

    def test_live(self):
        """
        Make sure API returns this course since it's live.
        """
        resp = self.client.get(reverse("course-list"))
        assert resp.status_code == 200, resp.content.decode('utf-8')
        courses_from_api = as_json(resp)

        self.validate_course_api(courses_from_api)
        assert courses_from_api == [
            course_as_dict(self.course)
        ]

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_course_detail(self, mock, fetch_mock):  # pylint: disable=unused-argument
        """
        Test that course detail works properly.
        """
        course_uuid = self.course.uuid
        module_uuid = self.module.uuid

        ccxcon_course_title = "ccxcon course title"
        ccxcon_module_title = "ccxcon module title"
        ccxcon_description = "ccxcon description"
        author = "author"
        overview = "overview"
        subchapters = ["subchapter1", "subchapter2"]
        image_url = "http://youtube.com/"
        fetch_mock.get(
            "{base}v1/coursexs/{course_uuid}/".format(
                base=FAKE_CCXCON_API,
                course_uuid=course_uuid,
            ), json={
                "uuid": course_uuid,
                "title": ccxcon_course_title,
                "author_name": author,
                "overview": overview,
                "description": ccxcon_description,
                "image_url": image_url,
                "edx_instance": "http://mitx.edx.org",
                "url": "https://example.com",
                "modules": "https://example.com",
                "instructors": [],
                "course_id": "course_id"
            }
        )
        fetch_mock.get(
            "{base}v1/coursexs/{course_uuid}/modules/".format(
                base=FAKE_CCXCON_API,
                course_uuid=course_uuid
            ), json=[
                {
                    "uuid": module_uuid,
                    "title": ccxcon_module_title,
                    "subchapters": subchapters,
                    "course": "https://example.com/",
                    "url": "https://example.com/"
                }
            ]
        )

        resp = self.client.get(
            reverse("course-detail", kwargs={"uuid": self.course.uuid})
        )
        assert resp.status_code == 200
        assert json.loads(resp.content.decode('utf-8')) == {
            "info": {
                "title": ccxcon_course_title,
                "description": ccxcon_description,
                "overview": overview,
                "image_url": image_url,
                "author_name": author
            },
            "title": self.course.title,
            "description": self.course.description,
            "uuid": course_uuid,
            "modules": [
                {
                    "info": {
                        "title": ccxcon_module_title,
                        "subchapters": subchapters
                    },
                    "title": self.module.title,
                    "uuid": module_uuid,
                    "price_without_tax": float(self.module.price_without_tax)
                }
            ],
            "live": True,
        }
        assert fetch_mock.called

    def test_course_not_available(self):
        """
        Test that course detail returns a 404 if the course or module is not available.
        """
        self.course.live = False
        self.course.save()

        resp = self.client.get(
            reverse("course-detail", kwargs={"uuid": self.course.uuid})
        )
        assert resp.status_code == 404, resp.content.decode('utf-8')

        resp = self.client.get(
            reverse("course-detail", kwargs={"uuid": self.module.uuid})
        )
        assert resp.status_code == 404, resp.content.decode('utf-8')

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_course_different_logged_in(self, _, fetch_mock):
        """
        Test that a limited version of the course detail is available for anonymous users
        """
        course_uuid = self.course.uuid
        module_uuid = self.module.uuid

        ccxcon_course_title = "ccxcon course title"
        ccxcon_module_title = "ccxcon module title"
        ccxcon_description = "ccxcon description"
        author = "author"
        overview = "overview"
        subchapters = ["subchapter1", "subchapter2"]
        image_url = "http://youtube.com/"
        fetch_mock.get(
            "{base}v1/coursexs/{course_uuid}/".format(
                base=FAKE_CCXCON_API,
                course_uuid=course_uuid,
            ), json={
                "uuid": course_uuid,
                "title": ccxcon_course_title,
                "author_name": author,
                "overview": overview,
                "description": ccxcon_description,
                "image_url": image_url,
                "edx_instance": "http://mitx.edx.org",
                "url": "https://example.com",
                "modules": "https://example.com",
                "instructors": [],
                "course_id": "course_id"
            }
        )
        fetch_mock.get(
            "{base}v1/coursexs/{course_uuid}/modules/".format(
                base=FAKE_CCXCON_API,
                course_uuid=course_uuid
            ), json=[
                {
                    "uuid": module_uuid,
                    "title": ccxcon_module_title,
                    "subchapters": subchapters,
                    "course": "https://example.com/",
                    "url": "https://example.com/"
                }
            ]
        )

        resp = self.client.get(
            reverse("course-detail", kwargs={"uuid": self.course.uuid})
        )
        assert resp.status_code == 200, resp.content.decode('utf-8')
        assert 'modules' in resp.data

        self.client.logout()
        resp = self.client.get(
            reverse("course-detail", kwargs={"uuid": self.course.uuid})
        )
        assert resp.status_code == 200, resp.content.decode('utf-8')
        assert 'modules' not in resp.data

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_error_reading_courses(self, mock, fetch_mock):  # pylint: disable=unused-argument
        """
        Test that an error reading courses from CCXCon will cause an error locally.
        """
        fetch_mock.get(
            "{base}v1/coursexs/{course_uuid}/".format(
                base=FAKE_CCXCON_API,
                course_uuid=self.course.uuid,
            ),
            status_code=500,
            json={}
        )

        with self.assertRaises(Exception) as ex:
            self.client.get(
                reverse("course-detail", kwargs={"uuid": self.course.uuid})
            )
        assert "CCXCon returned a non 200 status code 500" in ex.exception.args[0]
        assert fetch_mock.called

        # Course list API does not read from CCXCon so it should be unaffected
        resp = self.client.get(reverse('course-list'))
        assert resp.status_code == 200

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_error_reading_modules(self, mock, fetch_mock):  # pylint: disable=unused-argument
        """
        Test that an error reading modules from CCXCon will cause an error locally.
        """
        fetch_mock.get(
            "{base}v1/coursexs/{course_uuid}/modules/".format(
                base=FAKE_CCXCON_API,
                course_uuid=self.course.uuid,
            ),
            status_code=500,
            json={}
        )
        fetch_mock.get(
            "{base}v1/coursexs/{course_uuid}/".format(
                base=FAKE_CCXCON_API,
                course_uuid=self.course.uuid,
            ),
            status_code=200,
            json={}
        )

        with self.assertRaises(Exception) as ex:
            self.client.get(
                reverse("course-detail", kwargs={"uuid": self.course.uuid})
            )
        assert "CCXCon returned a non 200 status code 500" in ex.exception.args[0]
        assert fetch_mock.called

        # Course list API does not read from CCXCon so it should be unaffected
        resp = self.client.get(reverse('course-list'))
        assert resp.status_code == 200

    def test_filter_course_info(self):  # pylint: disable=no-self-use
        """
        Assert what we filter from the information we got from CCXCon
        """
        filtered = filter_ccxcon_course_info({
            "uuid": "uuid",
            "title": "title",
            "author_name": "author",
            "overview": "overview",
            "description": "description",
            "image_url": "http://youtube.com/",
            "edx_instance": "http://mitx.edx.org",
            "url": "http://example.com",
            "modules": "http://example.com",
            "instructors": [],
            "course_id": "course_id"
        })
        assert set(filtered.keys()) == {
            'title', 'description', 'overview', 'image_url', 'author_name'
        }

    def test_filter_module_info(self):  # pylint: disable=no-self-use
        """
        Assert what we filter from the module information we got from CCXCon
        """
        filtered = filter_ccxcon_module_info({
            "uuid": "ed99737e-d5bf-4b95-a467-bf4ecf31f7b0",
            "title": "other course",
            "subchapters": [],
            "course": "http://example.com",
            "url": "http://example.com"
        })
        assert set(filtered.keys()) == {'title', 'subchapters'}

    def assert_course_visibility(self, visibility_pairs):
        """
        Assert course-list and course-detail visibility for courses
        """

        resp = self.client.get(reverse('course-list'))
        assert resp.status_code == 200, resp.content.decode('utf-8')
        courses = json.loads(resp.content.decode('utf-8'))

        # No not_live_course here
        assert courses == [
            course_as_dict(Course.objects.get(uuid=uuid))
            for uuid, visible in visibility_pairs
            if visible
        ]

        for uuid, visible in visibility_pairs:
            resp = self.client.get(reverse('course-detail', kwargs={'uuid': uuid}))
            if visible:
                assert resp.status_code == 200, resp.content.decode('utf-8')
            else:
                assert resp.status_code == 404, resp.content.decode('utf-8')

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_course_visibility(self, mock, fetch_mock):  # pylint: disable=unused-argument
        """
        Assert that an instructor can also see courses which are not live
        but which they own, in both course list and detail view.
        """
        # Create an instructor
        instructor = User.objects.create_user(username="instructor", password="instructor")
        instructor.groups.add(Group.objects.get(name="Instructor"))
        self.client.login(username="instructor", password="instructor")

        not_live_course = CourseFactory.create(live=False)
        ModuleFactory.create(course=not_live_course, price_without_tax=1)
        not_live_owned_course = CourseFactory.create(live=False)
        ModuleFactory.create(course=not_live_owned_course, price_without_tax=3)
        instructor.courses_owned.add(not_live_owned_course)

        visibility_pairs = [
            (self.course.uuid, True),
            (not_live_course.uuid, False),
            (not_live_owned_course.uuid, True)
        ]
        for course_uuid, _ in visibility_pairs:
            fetch_mock.get(
                "{base}v1/coursexs/{course_uuid}/".format(
                    base=FAKE_CCXCON_API,
                    course_uuid=course_uuid,
                ), json={}
            )
            fetch_mock.get(
                "{base}v1/coursexs/{course_uuid}/modules/".format(
                    base=FAKE_CCXCON_API,
                    course_uuid=course_uuid
                ), json=[]
            )
        self.assert_course_visibility(visibility_pairs)

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_see_own_courses_perm(self, mock, fetch_mock):  # pylint: disable=unused-argument
        """
        Assert that ownership isn't enough to see not live courses, you need
        the permission too.
        """

        # Create an instructor
        not_live_course = CourseFactory.create(live=False)
        ModuleFactory.create(course=not_live_course, price_without_tax=1)
        not_live_owned_course = CourseFactory.create(live=False)
        ModuleFactory.create(course=not_live_owned_course, price_without_tax=3)
        self.teacher.courses_owned.add(not_live_owned_course)

        visibility_pairs = [
            (self.course.uuid, True),
            (not_live_course.uuid, False),
            (not_live_owned_course.uuid, False)
        ]
        for course_uuid, _ in visibility_pairs:
            fetch_mock.get(
                "{base}v1/coursexs/{course_uuid}/".format(
                    base=FAKE_CCXCON_API,
                    course_uuid=course_uuid,
                ), json={}
            )
            fetch_mock.get(
                "{base}v1/coursexs/{course_uuid}/modules/".format(
                    base=FAKE_CCXCON_API,
                    course_uuid=course_uuid
                ), json=[]
            )
        self.assert_course_visibility(visibility_pairs)


# pylint: disable=too-many-public-methods
class CourseAPIPATCHTests(CourseTests):
    """
    Tests for courses detail API, PATCH method
    """
    def setUp(self):
        super(CourseAPIPATCHTests, self).setUp()
        self.course.live = True
        self.course.save()

        # Login an instructor who owns a course
        credentials = {"username": "auser", "password": "apass"}
        self.instructor = User.objects.create_user(**credentials)
        self.instructor.groups.add(Group.objects.get(name="Instructor"))
        self.client.login(**credentials)
        self.instructor.courses_owned.add(self.course)

    def test_put_not_allowed(self):
        """PUT is not supported, mostly to cut down the work we need to do here"""
        resp = self.client.put(reverse('course-detail', kwargs={"uuid": self.course.uuid}))
        assert resp.status_code == 405

    def test_invalid_json(self):
        """If user sends invalid JSON in PATCH, return a 400"""
        resp = self.client.patch(
            reverse('course-detail', kwargs={"uuid": self.course.uuid}),
            content_type="application/json",
            data="{"
        )
        assert resp.status_code == 400, resp.content.decode('utf-8')
        assert "JSON parse error" in resp.content.decode('utf-8')

    def assert_patch_validation(self, course_uuid, course_dict, error):
        """Helper method to assert course validation errors"""
        course = Course.objects.get(uuid=course_uuid)
        module = course.module_set.first()
        old_course_title = course.title
        old_course_description = course.description
        old_module_title = module.title
        old_module_price = module.price_without_tax

        resp = self.client.patch(
            reverse('course-detail', kwargs={"uuid": course_uuid}),
            content_type="application/json",
            data=json.dumps(course_dict)
        )
        assert resp.status_code == 400, resp.content.decode('utf-8')
        assert error in resp.content.decode('utf-8')

        # Assert transactionality
        course.refresh_from_db()
        module.refresh_from_db()
        assert course.title == old_course_title
        assert course.description == old_course_description
        assert module.title == old_module_title
        assert module.price_without_tax == old_module_price

    def test_missing_course(self):
        """Error if course UUID points to a missing course"""
        resp = self.client.patch(
            reverse('course-detail', kwargs={"uuid": "missing"}),
            content_type="application/json",
            data=json.dumps({})
        )
        assert resp.status_code == 404, resp.content.decode('utf-8')

    def test_bad_module_list(self):
        """Error if modules is not a list"""
        course_dict = {
            'modules': {}
        }
        self.assert_patch_validation(
            self.course.uuid,
            course_dict,
            "modules must be a list of modules"
        )

    def test_bad_module(self):
        """Error if a module is not an object"""
        course_dict = {
            'modules': [None]
        }
        self.assert_patch_validation(self.course.uuid, course_dict, "Each module must be an object")

    def test_no_module_uuid(self):
        """Error if a module does not include a uuid"""
        course_dict = {
            'modules': [{}]
        }
        self.assert_patch_validation(self.course.uuid, course_dict, "Missing key uuid")

    def test_missing_module(self):
        """Error if a module does not exist"""
        course_dict = {
            'uuid': self.course.uuid,
            'modules': [{
                'uuid': 'missing'
            }]
        }
        self.assert_patch_validation(self.course.uuid, course_dict, "Unable to find module")

    def test_module_course_mismatch(self):
        """Error if the module uuid doesn't match the course"""
        module2 = ModuleFactory.create()
        course_dict = {
            'uuid': self.course.uuid,
            'modules': [{
                'uuid': module2.uuid
            }]
        }
        self.assert_patch_validation(
            self.course.uuid,
            course_dict,
            "Unable to find module {}".format(module2.uuid)
        )

    def test_duplicate_module(self):
        """Error if the module uuid shows up twice"""
        course_dict = {
            'uuid': self.course.uuid,
            'modules': [
                {
                    'uuid': self.module.uuid,
                    "title": "title1"
                },
                {
                    'uuid': self.module.uuid,
                    "title": "title2"
                }
            ],
        }
        self.assert_patch_validation(self.course.uuid, course_dict, "Duplicate module")

    def patch_dict_for_price(self, price):
        """Make a dict we can use to patch a price"""
        return {
            'modules': [{
                'uuid': self.module.uuid,
                'price_without_tax': price
            }]
        }

    def test_price_one_module(self):
        """
        Make sure we allow patching only the modules we care about.
        """
        # Get dict when we have one module, then create a second one
        module2 = ModuleFactory.create(course=self.course)
        second_old_price = module2.price_without_tax
        new_price = '4'
        course_dict = self.patch_dict_for_price(new_price)
        assert self.module.price_without_tax != new_price

        resp = self.client.patch(
            reverse('course-detail', kwargs={"uuid": self.course.uuid}),
            content_type="application/json",
            data=json.dumps(course_dict)
        )
        assert resp.status_code == 200, resp.content.decode('utf-8')

        self.module.refresh_from_db()
        assert self.module.price_without_tax == Decimal(new_price)
        assert module2.price_without_tax == second_old_price

    def test_null_price(self):
        """
        Null prices are allowed, as this is the default state of a price. These
        modules won't be available for sale.
        """
        course_dict = self.patch_dict_for_price(None)
        resp = self.client.patch(
            reverse('course-detail', kwargs={"uuid": self.course.uuid}),
            content_type="application/json",
            data=json.dumps(course_dict)
        )
        assert resp.status_code == 200, resp.content.decode('utf-8')
        self.module.refresh_from_db()
        assert self.module.price_without_tax is None

    def test_bad_price(self):
        """Error if price is not a string"""
        course_dict = self.patch_dict_for_price(3)
        self.assert_patch_validation(
            self.course.uuid,
            course_dict,
            'price_without_tax must be a string'
        )

    def test_invalid_number_price(self):
        """Error if price can't be parsed into a Decimal"""
        course_dict = self.patch_dict_for_price("seven")
        self.assert_patch_validation(
            self.course.uuid,
            course_dict,
            'price_without_tax is not a valid number'
        )

    def test_negative_price(self):
        """Error if the price is negative"""
        course_dict = self.patch_dict_for_price('-1')
        self.assert_patch_validation(
            self.course.uuid,
            course_dict,
            'price_without_tax is not a valid number'
        )

    def test_price_to_invalid_number(self):
        """Error if the price is not a finite number"""
        for invalid_number in ('inf', '-inf', 'nan', '-nan'):
            course_dict = self.patch_dict_for_price(invalid_number)
            self.assert_patch_validation(
                self.course.uuid,
                course_dict,
                'price_without_tax is not a valid number'
            )

    def test_empty_price(self):
        """Zero prices are allowed"""
        course_dict = self.patch_dict_for_price('')
        self.assert_patch_validation(
            self.course.uuid,
            course_dict,
            "price_without_tax is not a valid number"
        )

    def test_zero_price(self):
        """Zero prices are allowed"""
        course_dict = self.patch_dict_for_price('0')
        resp = self.client.patch(
            reverse('course-detail', kwargs={"uuid": self.course.uuid}),
            content_type="application/json",
            data=json.dumps(course_dict)
        )
        assert resp.status_code == 200, resp.content.decode('utf-8')
        self.module.refresh_from_db()
        assert self.module.price_without_tax == 0

    def test_price_requires_owner(self):
        """If a user doesn't own a course, they can't set prices for its modules"""
        self.instructor.courses_owned.remove(self.course)
        course_dict = self.patch_dict_for_price('125')
        self.assert_patch_validation(
            self.course.uuid,
            course_dict,
            "User doesn\'t have permission to edit module price"
        )

    def test_price_requires_perm(self):
        """
        If a user doesn't have permissions for a course, they can't set prices for its modules
        """
        self.instructor.groups.remove(Group.objects.get(name="Instructor"))
        course_dict = self.patch_dict_for_price('125')
        self.assert_patch_validation(
            self.course.uuid,
            course_dict,
            "User doesn\'t have permission to edit module price"
        )

    def patch_dict_for_course_title(self, title):  # pylint: disable=no-self-use
        """Make a dict we can use to patch a course title"""
        return {
            'title': title
        }

    def test_course_title(self):
        """Set a course title and assert that the change was made"""
        course_dict = self.patch_dict_for_course_title("new title")
        assert course_dict['title'] != self.course.title

        resp = self.client.patch(
            reverse('course-detail', kwargs={"uuid": self.course.uuid}),
            content_type="application/json",
            data=json.dumps(course_dict)
        )
        assert resp.status_code == 200, resp.content.decode('utf-8')
        self.course.refresh_from_db()
        assert course_dict['title'] == self.course.title

    def test_bad_course_title(self):
        """Error if the course title is not a string"""
        course_dict = self.patch_dict_for_course_title(3)
        self.assert_patch_validation(
            self.course.uuid,
            course_dict,
            "title must be a non-empty string"
        )

    def test_set_empty_course_title(self):
        """Error if the course title is empty"""
        course_dict = self.patch_dict_for_course_title('')
        self.assert_patch_validation(
            self.course.uuid,
            course_dict,
            "title must be a non-empty string"
        )

    def patch_dict_for_course_description(self, description):  # pylint: disable=no-self-use, invalid-name
        """Make a dict we can use to patch a course description"""
        return {
            'description': description
        }

    def test_course_description(self):
        """Set a course description and assert that the change was made"""
        course_dict = self.patch_dict_for_course_description("new description")
        assert course_dict['description'] != self.course.description

        resp = self.client.patch(
            reverse('course-detail', kwargs={"uuid": self.course.uuid}),
            content_type="application/json",
            data=json.dumps(course_dict)
        )
        assert resp.status_code == 200, resp.content.decode('utf-8')
        self.course.refresh_from_db()
        assert course_dict['description'] == self.course.description

    def test_bad_course_description(self):
        """Set a course description that's not a string"""
        course_dict = self.patch_dict_for_course_description(None)
        self.assert_patch_validation(
            self.course.uuid,
            course_dict,
            "description must be a string"
        )

    def patch_dict_for_module_title(self, title):
        """Make a dict we can use to patch a module title"""
        return {
            'modules': [{
                'uuid': self.module.uuid,
                'title': title
            }]
        }

    def test_module_title(self):
        """Set a module title and assert that the change was made"""
        course_dict = self.patch_dict_for_module_title('new module title')
        assert course_dict['modules'][0]['title'] != self.course.title

        resp = self.client.patch(
            reverse('course-detail', kwargs={"uuid": self.course.uuid}),
            content_type="application/json",
            data=json.dumps(course_dict)
        )
        assert resp.status_code == 200, resp.content.decode('utf-8')
        self.module.refresh_from_db()
        assert course_dict['modules'][0]['title'] == self.module.title

    def test_bad_module_title(self):
        """Error if the module title is not a string"""
        course_dict = self.patch_dict_for_module_title({})
        self.assert_patch_validation(
            self.course.uuid,
            course_dict,
            "title must be a non-empty string"
        )

    def test_empty_module_title(self):
        """Error if the module title is empty"""
        course_dict = self.patch_dict_for_module_title('')
        self.assert_patch_validation(
            self.course.uuid,
            course_dict,
            "title must be a non-empty string"
        )

    def test_content_requires_owner(self):
        """Instructor must own course to edit content"""
        self.instructor.courses_owned.remove(self.course)

        for course_dict in (
                self.patch_dict_for_course_description('description'),
                self.patch_dict_for_course_title('course title'),
                self.patch_dict_for_module_title('module title')
        ):
            self.assert_patch_validation(
                self.course.uuid,
                course_dict,
                "User doesn\'t have permission to edit course descriptions or titles"
            )

    def test_content_requires_perm(self):
        """User must have instructor permissions to edit content"""
        # Remove user from instructor group, which also removes permissions
        self.instructor.groups.remove(Group.objects.get(name="Instructor"))

        for course_dict in (
                self.patch_dict_for_course_description('description'),
                self.patch_dict_for_course_title('course title'),
                self.patch_dict_for_module_title('module title')
        ):
            self.assert_patch_validation(
                self.course.uuid,
                course_dict,
                "User doesn\'t have permission to edit course descriptions or titles"
            )

    def patch_dict_for_liveness(self, live):  # pylint: disable=no-self-use
        """Make a dict we can use to patch a course liveness"""
        return {
            'live': live
        }

    def test_liveness(self):
        """
        Set the liveness of a course
        """
        course_dict = self.patch_dict_for_liveness(False)
        assert course_dict['live'] != self.course.live

        resp = self.client.patch(
            reverse('course-detail', kwargs={"uuid": self.course.uuid}),
            content_type="application/json",
            data=json.dumps(course_dict)
        )
        assert resp.status_code == 200, resp.content.decode('utf-8')
        self.course.refresh_from_db()
        assert course_dict['live'] == self.course.live

    def test_bad_liveness(self):
        """
        Error if live is not a boolean
        """
        course_dict = self.patch_dict_for_liveness(None)
        self.assert_patch_validation(self.course.uuid, course_dict, "live must be a bool")

    def test_liveness_requires_owner(self):
        """
        Error if we set live without owning course
        """
        self.instructor.courses_owned.remove(self.course)

        course_dict = self.patch_dict_for_liveness(True)
        self.assert_patch_validation(
            self.course.uuid,
            course_dict,
            "User doesn\'t have permission to edit course liveness"
        )

    def test_liveness_requires_perm(self):
        """
        Error if we set live without having permission to
        """
        self.instructor.groups.remove(Group.objects.get(name="Instructor"))

        course_dict = self.patch_dict_for_liveness(True)
        self.assert_patch_validation(
            self.course.uuid,
            course_dict,
            "User doesn\'t have permission to edit course liveness"
        )
