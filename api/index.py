import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
except BaseException as e:
    import traceback
    error_msg = traceback.format_exc()
    print("WSGI STARTUP ERROR:\n", error_msg, file=sys.stderr)
    def app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        return [b"CRITICAL STARTUP ERROR:\n\n" + error_msg.encode()]

application = app
