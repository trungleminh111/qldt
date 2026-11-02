import os
import sys
import mimetypes

mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class VercelPathFixMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        matched = (
            environ.get("HTTP_X_MATCHED_PATH") or
            environ.get("HTTP_X_FORWARDED_URI") or
            environ.get("REQUEST_URI") or
            environ.get("PATH_INFO", "")
        )
        if matched.startswith("http://") or matched.startswith("https://"):
            from urllib.parse import urlparse
            matched = urlparse(matched).path
        if "?" in matched:
            path_part, query_part = matched.split("?", 1)
            matched = path_part
            if not environ.get("QUERY_STRING"):
                environ["QUERY_STRING"] = query_part
        for prefix in ["/api/index.py", "api/index.py", "/api/index", "api/index"]:
            if matched.startswith(prefix):
                matched = matched[len(prefix):]
                break
        if not matched or not matched.startswith("/"):
            matched = "/" + matched.lstrip("/")
        environ["PATH_INFO"] = matched
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)
