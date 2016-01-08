"""
Status check API

Notes:

* Useful messages are logged, but NO_CONFIG is returned whether
  settings are missing or invalid, to prevent information leakage.
* Different services provide different information, but all should return
  UP, DOWN, or NO_CONFIG for the "status" key.
"""

from __future__ import unicode_literals

from datetime import datetime
import logging

from django.conf import settings
from django.http import JsonResponse, Http404
from psycopg2 import connect, OperationalError

log = logging.getLogger(__name__)

UP = "up"
DOWN = "down"
NO_CONFIG = "no config found"
HTTP_OK = 200
SERVICE_UNAVAILABLE = 503
TIMEOUT_SECONDS = 5


def get_pg_info():
    """Check PostgreSQL connection."""
    log.debug("entered get_pg_info")
    try:
        conf = settings.DATABASES['default']
        database = conf["NAME"]
        user = conf["USER"]
        host = conf["HOST"]
        port = conf["PORT"]
        password = conf["PASSWORD"]
    except (AttributeError, KeyError):
        log.error("No PostgreSQL connection info found in settings.")
        return {"status": NO_CONFIG}
    except TypeError:
        return {"status": DOWN}
    log.debug("got past getting conf")
    try:
        start = datetime.now()
        connection = connect(
            database=database, user=user, host=host,
            port=port, password=password, connect_timeout=TIMEOUT_SECONDS,
        )
        log.debug("at end of context manager")
        micro = (datetime.now() - start).microseconds
        connection.close()
    except (OperationalError, KeyError):
        log.error("Invalid PostgreSQL connection info in settings: %s", conf)
        return {"status": DOWN}
    log.debug("got to end of postgres check successfully")
    return {"status": UP, "response_microseconds": micro}


def status(request):  # pylint: disable=unused-argument
    """Status"""
    token = request.GET.get("token", "")
    if token != settings.STATUS_TOKEN or settings.STATUS_TOKEN == "":
        raise Http404()
    info = {}
    log.debug("getting info on postgres")
    info["postgresql"] = get_pg_info()
    code = HTTP_OK
    for key in info:
        if info[key]["status"] == "down":
            code = SERVICE_UNAVAILABLE
            break
    resp = JsonResponse(info)
    resp.status_code = code
    return resp
