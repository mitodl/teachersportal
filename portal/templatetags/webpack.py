"""
A template tag for resolving webpack bundle URLs.
"""

from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template import Library


register = Library()  # pylint: disable=invalid-name


@register.simple_tag(takes_context=True)
def webpack_bundle(context, bundle):
    """A Django template tag that resolves the URL of a given static webpack JavaScript bundle.

    Args:
        context (Context): The template context.
        bundle (String): The name of the bundle to resolve (including the extension).
    Returns:
        String
    """
    if settings.DEBUG and settings.USE_WEBPACK_DEV_SERVER:
        request = context['request']
        host = request.get_host().split(":")[0]

        return "{host_url}/{bundle}".format(
            host_url=settings.WEBPACK_SERVER_URL.format(host=host),
            bundle=bundle
        )

    return static("bundles/{bundle}".format(bundle=bundle))
