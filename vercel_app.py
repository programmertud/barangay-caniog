import os
import sys

# Ensure the root directory is in the Python path
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
except Exception:
    import traceback
    error_msg = traceback.format_exc()
    print("WSGI STARTUP ERROR:\n", error_msg, file=sys.stderr)

    def app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        return [b"STARTUP ERROR:\n\n" + error_msg.encode()]

# Vercel needs exactly 'app' or 'application'
application = app
