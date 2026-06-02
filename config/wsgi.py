"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import traceback

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    _application = get_wsgi_application()
except Exception:
    import traceback
    error_msg = traceback.format_exc()
    print("WSGI STARTUP ERROR:\n", error_msg)

    def _application(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        return [b"STARTUP ERROR:\n\n" + error_msg.encode()]

application = _application
