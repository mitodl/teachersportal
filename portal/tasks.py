"""
Course Tasks
"""
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

import requests
from requests.exceptions import RequestException

from teachersportal.celery import async
from portal.models import Course, Module
from portal.oauth import get_access_token


def get_subchapters(module_id, blocks):
    """
    Fetches nested subchapters for a module.
    """
    return [blocks[x]['display_name'] for x in blocks[module_id]['children']]


def get_backoff(retries=0):
    """
    Returns exponential backoff for retry limits. Given 5 retries:

    0: 2 min
    1: 5 min
    2: 10 min
    3: 17 min
    4: 26 min
    """
    return (retries + 1) ** 2 * 60 + 60


# pylint: disable=too-many-locals
@async.task(bind=True, max_retries=5)
def module_population(self, course_id):
    """
    Gets and persists a list of modules for a given course.
    """
    try:
        course = Course.objects.get(edx_course_id=course_id)
    except Course.DoesNotExist:
        return  # delete case.

    access_token = get_access_token(course.instance)

    try:
        resp = requests.get(
            urljoin(course.instance.instance_url, '/api/courses/v1/blocks/'),
            params={
                "depth": "all",
                "username": course.instance.username,
                "course_id": course.edx_course_id,
                "requested_fields": "children,display_name,id,type,visible_to_staff_only",
            }, headers={
                'Authorization': 'Bearer {}'.format(access_token)
            })
    except RequestException as exc:
        self.retry(exc=exc, countdown=get_backoff(self.request.retries))

    if resp.status_code >= 300:
        self.retry(countdown=get_backoff(self.request.retries))

    j_resp = resp.json()
    blocks = j_resp['blocks']
    locations = blocks[j_resp['root']]['children']
    chapters = [blocks[location] for location in locations]
    visible_course_ids = {
        chapter['id'] for chapter in chapters
        if not chapter.get('visible_to_staff_only')
    }

    # Delete happens first so we don't have duplicate `order` entries.
    for module in course.modules.exclude(locator_id__in=visible_course_ids):
        module.delete()

    for num, payload in enumerate(chapters):
        locator_id = payload['id']
        if locator_id not in visible_course_ids:
            continue

        try:
            module = Module.objects.get(course=course, locator_id=locator_id)
        except Module.DoesNotExist:
            module = Module(course=course, locator_id=locator_id)
        module.title = payload['display_name']
        module.order = num
        module.subchapters = get_subchapters(module.locator_id, blocks)
        module.save()
