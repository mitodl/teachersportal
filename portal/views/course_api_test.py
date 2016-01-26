"""
Tests for Course API
"""

from __future__ import unicode_literals

import json
from mock import patch
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import requests_mock

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


class CourseAPITests(CourseTests):
    """
    Tests for course API
    """

    def setUp(self):
        """
        Set up the courses
        """
        super(CourseAPITests, self).setUp()
        self.course.live = True
        self.course.save()

        credentials = {"username": "auser", "password": "apass"}
        User.objects.create_user(**credentials)
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

    def test_not_logged_in(self):
        """
        Test that course detail are only available to logged in users.
        """
        self.client.logout()
        resp = self.client.get(
            reverse("course-detail", kwargs={"uuid": self.module.uuid})
        )
        assert resp.status_code == 403, resp.content.decode('utf-8')

        # Course list is available to users not logged in
        resp = self.client.get(reverse("course-list"))
        assert resp.status_code == 200, resp.content.decode('utf-8')

    @patch('requests_oauthlib.oauth2_session.OAuth2Session.fetch_token', autospec=True)
    @requests_mock.mock()
    def test_ccxcon_connection_broken(self, mock, fetch_mock):  # pylint: disable=unused-argument
        """
        Test that if the CCXCon connection is broken an exception is raised
        (producing a 500 error).
        """
        fetch_mock.get(
            "{base}v1/coursexs/{course_uuid}/modules/".format(
                base=FAKE_CCXCON_API,
                course_uuid=self.course.uuid,
            ),
            status_code=200,
            json={}
        )
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
