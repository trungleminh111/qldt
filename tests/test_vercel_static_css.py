import unittest
from api.index import app

class TestVercelStaticCSS(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_static_css_direct(self):
        res = self.client.get("/static/css/style.css")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/css", res.headers.get("Content-Type", ""))
        self.assertGreater(len(res.data), 1000)

    def test_static_js_direct(self):
        res = self.client.get("/static/js/app.js")
        self.assertEqual(res.status_code, 200)
        self.assertIn("javascript", res.headers.get("Content-Type", "").lower())
        self.assertGreater(len(res.data), 100)

    def test_static_css_via_vercel_matched_path(self):
        res = self.client.get("/api/index.py", environ_base={
            "HTTP_X_MATCHED_PATH": "/static/css/style.css"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/css", res.headers.get("Content-Type", ""))

    def test_static_css_via_vercel_with_query_string(self):
        res = self.client.get("/api/index.py", environ_base={
            "HTTP_X_MATCHED_PATH": "/static/css/style.css?v=2.0.0"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/css", res.headers.get("Content-Type", ""))

    def test_static_js_via_vercel_with_query_string(self):
        res = self.client.get("/api/index.py", environ_base={
            "HTTP_X_FORWARDED_URI": "/static/js/app.js?t=12345"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("javascript", res.headers.get("Content-Type", "").lower())

if __name__ == "__main__":
    unittest.main()
