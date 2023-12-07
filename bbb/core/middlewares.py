import logging

from django.utils.deprecation import MiddlewareMixin

try:
    import uwsgi
    import uwsgidecorators  # NOQA: F401 Ensure uwsgi is missing

    in_uwsgi = True
except (ImportError, AttributeError):
    in_uwsgi = False


logger = logging.getLogger(__name__)


class UwsgiLogMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not in_uwsgi:
            return response

        # Extract & settings log
        try:
            # resolver path
            if request.resolver_match:
                uwsgi.set_logvar("re_path", request.resolver_match.route)
        except Exception:
            logger.exception("uwsgi logging error")

        return response
