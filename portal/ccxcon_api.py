"""
Script to create a CCX using the CCXCon REST APIs
"""
import argparse
import sys

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

HTTP_201_CREATED = 201
CCXCON_TOKEN_URL = '/o/token/'
CCXCON_CREATE_CCX = '/api/v1/ccx/'


# pylint: disable=too-few-public-methods
class CCXConAPI(object):
    """
    An API client for CCXCon
    """
    # pylint: disable=too-many-arguments
    def __init__(self, ccxcon_url, client_id, client_secret, cert_verify=True,
                 oauth_client=None):
        """
        Args:
            ccxcon_url (str): URL of CCXCon
            client_id (str): OAuth client id
            client_secret (str): OAuth client secret
            cert_verify (bool): whether to validate TLS certificate
            oauth_client (reqeusts_oauthlib.OAuth2Session): Override for the
                lazy-loaded oauth client.
        """
        self.ccxcon_url = ccxcon_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.cert_verify = cert_verify
        self.oauth_client = oauth_client

    @staticmethod
    def _get_oauth_client(ccxcon_url, client_id, client_secret, cert_verify):
        """
        Function that creates an oauth client and fetches a token.
        """
        client = BackendApplicationClient(client_id=client_id)
        oauth_ccxcon = OAuth2Session(client=client)
        oauth_ccxcon.fetch_token(
            token_url=urljoin(ccxcon_url, CCXCON_TOKEN_URL),
            client_id=client_id,
            client_secret=client_secret,
            verify=cert_verify
        )
        return oauth_ccxcon

    def request(self, method, *args, **kwargs):
        """
        Generic interface for calling http methods on the oauth_client.
        """
        if self.oauth_client is None:
            self.oauth_client = self._get_oauth_client(
                self.ccxcon_url, self.client_id, self.client_secret,
                self.cert_verify)
        return getattr(self.oauth_client, method)(*args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Shortcut for making POSTs via the oauth_client.
        """
        return self.request('post', *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Shortcut for making GETs via the oauth_client.
        """
        return self.request('get', *args, **kwargs)

    # pylint: disable=too-many-arguments
    def create_ccx(self, master_course_uuid, user_email, seats, ccx_title,
                   course_modules=None):
        """
        Creates a CCX using the CCXCon

        Args:
            master_course_uuid (str): UUID of the master course.
            user_email (str): email of the coach on edX
            seats (int): Number of seats the CCX has access to
            ccx_title (str): Title of the CCX
            course_modules (list): List of module UUIDs to give the course
                access to.

        Returns:
           tuple: success (bool), status_code (int), json (dict)
        """
        payload = {
            'master_course_id': master_course_uuid,
            'user_email': user_email,
            'total_seats': seats,
            'display_name': ccx_title,
        }
        if course_modules is not None:
            payload['course_modules'] = course_modules
        headers = {'content-type': 'application/json'}

        # make the POST request
        resp = self.post(
            url=urljoin(self.ccxcon_url, CCXCON_CREATE_CCX),
            json=payload,
            headers=headers,
            verify=self.cert_verify
        )

        return (
            resp.status_code == HTTP_201_CREATED,
            resp.status_code,
            resp.json()
        )


def parse_arguments():
    """
    Parsing arguments necessary to create the CCX
    """
    parser = argparse.ArgumentParser(description="Create a CCX using CCXCon")
    # Parameters for CCXCon information
    parser.add_argument('--ccxcon-url', dest='ccxconurl',
                        help="The CCXCon URL to be used", required=True)
    parser.add_argument('--client-id', dest='clientid',
                        help="The user's OAUTH ID", required=True)
    parser.add_argument('--client-secret', dest='clientsecret',
                        help="The user's OAUTH SECRET", required=True)
    # Parameters for creating the CCX
    parser.add_argument('--master-course', dest='mastercourse',
                        help="The master course UUID", required=True)
    parser.add_argument('--user-email', dest='useremail',
                        help="The coach email", required=True)
    parser.add_argument('--seats', type=int, dest='seats',
                        help="The number of seats for the CCX", required=True)
    parser.add_argument('--ccx-title', dest='ccxtitle',
                        help="The title for the CCX", required=True)
    parser.add_argument('--modules', dest='modules', nargs="*",
                        help="Course modules")
    # Parameters for the script
    parser.add_argument('--no-cert-verify', dest='certverify',
                        action='store_false', default=True,
                        help="No SSL certificate verification")
    return parser.parse_args()


def main():
    """
    Entry point for the script
    """
    args = parse_arguments()

    api = CCXConAPI(
        args.ccxconurl,
        args.clientid,
        args.clientsecret,
        args.certverify)

    worked, status, content = api.create_ccx(
        args.mastercourse,
        args.useremail,
        args.seats,
        args.ccxtitle,
        args.modules,
    )

    # pylint: disable=superfluous-parens
    if not worked:
        print('Server returned unexpected status code {}'.format(status))
        sys.exit(1)
    else:
        print('CCX successfully created. \nServer output: {}'.format(content))


if __name__ == '__main__':
    main()
