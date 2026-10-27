"""The local web UI: pages, generate, corrections, and the guards around them (training itself is covered by training/evaluate.py)."""
import http.client
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

import webui
from corecraft import feedback


class UI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.old = (feedback.PATH, webui.OUT)
        feedback.PATH = Path(cls.tmp.name) / "feedback.json"
        webui.OUT = Path(cls.tmp.name) / "ui"
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), webui.Handler)
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        feedback.PATH, webui.OUT = cls.old
        cls.tmp.cleanup()

    def call(self, method, path, body=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        c.request(method, path, body=json.dumps(body) if isinstance(body, dict) else body)
        r = c.getresponse()
        raw = r.read()
        c.close()
        return r.status, raw

    def test_page_loads(self):
        code, raw = self.call("GET", "/")
        self.assertEqual(code, 200)
        self.assertIn(b"Core-Craft AI", raw)

    def test_generate_returns_report_and_preview(self):
        code, raw = self.call("POST", "/api/generate", {"prompt": "dental clinic in Pune, braces, implants", "facts": {"name": "Smile Hub", "phone": ""}})
        d = json.loads(raw)
        self.assertEqual((code, d["brand"], d["detected"], d["location"]), (200, "Smile Hub", "dental", "Pune"))
        self.assertEqual(d["services"], ["braces", "implants"])
        code, page = self.call("GET", d["preview"])
        self.assertEqual(code, 200)
        self.assertIn(b"Smile Hub", page)

    def test_bad_requests_are_clean_errors(self):
        self.assertEqual(self.call("POST", "/api/generate", "{bad")[0], 400)
        self.assertEqual(self.call("POST", "/api/generate", {"prompt": ""})[0], 400)
        self.assertEqual(self.call("POST", "/api/generate", "[1]")[0], 400)
        self.assertEqual(self.call("POST", "/api/feedback", {"prompt": "x", "type": "nonsense"})[0], 400)
        self.assertEqual(self.call("POST", "/nope", {})[0], 404)

    def test_files_outside_the_site_folder_are_not_served(self):
        for p in ("/site/../../main.py", "/site/..%2F..%2Fmain.py", "/site/%2e%2e/%2e%2e/main.py"):
            self.assertEqual(self.call("GET", p)[0], 404, p)

    def test_corrections_are_saved_and_removed(self):
        self.assertEqual(json.loads(self.call("POST", "/api/feedback", {"prompt": "mera bike showroom hai Jaipur mein", "type": "autosales"})[1])["count"], 1)
        self.assertEqual(feedback.pairs(), [("mera bike showroom hai Jaipur mein", "autosales")])
        self.assertEqual(json.loads(self.call("POST", "/api/feedback/remove", {"prompt": "mera bike showroom hai Jaipur mein"})[1])["count"], 0)

    def test_oversized_body_is_refused(self):
        self.assertEqual(self.call("POST", "/api/generate", "x" * 300000)[0], 413)


if __name__ == "__main__":
    unittest.main()
