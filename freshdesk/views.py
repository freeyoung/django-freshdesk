from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote
from django.core.exceptions import ImproperlyConfigured

import hashlib
import hmac
import time


@never_cache
@login_required
def authenticate(request):
    if not hasattr(settings, 'FRESHDESK_URL'):
        raise ImproperlyConfigured("Set the FRESHDESK_URL settings variable")
    if not hasattr(settings, 'FRESHDESK_SECRET_KEY'):
        raise ImproperlyConfigured("Set the FRESHDESK_SECRET_KEY settings variable")

    if not request.user:
        raise Http404()

    first_name = request.user.first_name
    last_name = request.user.last_name
    if not first_name and not last_name:
        first_name = "Guinea"
        last_name = "Pig"

    utctime = int(time.time())
    data = '{0} {1}{2}{3}'.format(
        first_name, last_name, request.user.email, utctime)
    generated_hash = hmac.new(
        settings.FRESHDESK_SECRET_KEY, data, hashlib.md5).hexdigest()
    url = settings.FRESHDESK_URL + "login/sso?name=" + urlquote('{0} {1}'.format(first_name, last_name)) + \
        "&email=" + urlquote(request.user.email) + "&timestamp=" + \
        str(utctime) + "&hash=" + generated_hash
    print iri_to_uri(url)

    return HttpResponseRedirect(iri_to_uri(url))
