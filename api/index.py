import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class VercelPathFixMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if path == "/api/index" or path == "/api/index.py":
            environ["PATH_INFO"] = "/"
        elif path.startswith("/api/index/"):
            environ["PATH_INFO"] = path[len("/api/index"):]
        elif path.startswith("/api/index.py/"):
            environ["PATH_INFO"] = path[len("/api/index.py"):]
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)
