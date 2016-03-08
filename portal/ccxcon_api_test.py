"""
Tests for CCXConAPI
"""
# pylint: disable=no-self-use
from unittest import TestCase
from requests import Session
import mock

from .ccxcon_api import CCXConAPI


class CCXConAPITest(TestCase):
    """
    Tests for CCXConAPI
    """
    def setUp(self):
        self.session = Session()

    def test_creates_ccx(self):
        """
        If the requests to ccxcon are successful, we should report it as such.
        """
        mock_oauth_client = mock.Mock()
        response = mock_oauth_client.post.return_value
        response.status_code = 201
        response.json.return_value = {
            'ccx_id': 2
        }

        api = CCXConAPI(
            'url',
            'id',
            'secret',
            oauth_client=mock_oauth_client,
        )

        works, status, json_result = api.create_ccx(
            '1934ebc3-33e5-4833-814e-72043620f453',
            'abrahms@mit.edu',
            20,
            'Test CCX Title',
            course_modules=[
                'dd5e27ca-3795-4efc-ae8f-e51659f41a22',
                '381c3a81-8c42-4998-b619-5c810bfc72ee',
                'd39e1434-c7bf-4156-b69b-803e0df4eae0',
            ]
        )

        assert works
        assert status == 201
        assert 'ccx_id' in json_result
        mock_oauth_client.post.assert_called_once_with(
            url=mock.ANY,
            json={
                'master_course_id': '1934ebc3-33e5-4833-814e-72043620f453',
                'user_email': 'abrahms@mit.edu',
                'total_seats': 20,
                'display_name': 'Test CCX Title',
                'course_modules': [
                    'dd5e27ca-3795-4efc-ae8f-e51659f41a22',
                    '381c3a81-8c42-4998-b619-5c810bfc72ee',
                    'd39e1434-c7bf-4156-b69b-803e0df4eae0'
                ],
            },
            headers=mock.ANY,
            verify=mock.ANY,
        )

    def test_failure_bubbles(self):
        """
        Errors on the ccx request should be reflected in status.
        """
        mock_oauth_client = mock.Mock()
        response = mock_oauth_client.post.return_value
        response.status_code = 400
        response.json.return_value = {}

        api = CCXConAPI(
            'url',
            'id',
            'secret',
            oauth_client=mock_oauth_client,
        )

        works, status, _ = api.create_ccx(
            '1934ebc3-33e5-4833-814e-72043620f453',
            'abrahms@mit.edu',
            20,
            'Test CCX Title',
            course_modules=[
                'dd5e27ca-3795-4efc-ae8f-e51659f41a22',
                '381c3a81-8c42-4998-b619-5c810bfc72ee',
                'd39e1434-c7bf-4156-b69b-803e0df4eae0',
            ]
        )

        assert not works
        assert status != 201
