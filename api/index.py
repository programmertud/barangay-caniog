def app(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    return [b"HELLO WORLD FROM VERCEL! (Django is disabled for this test)"]

application = app
