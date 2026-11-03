import unittest
from models.co_so_du_lieu import PostgresRow, PostgresCursorWrapper, nen_dung_postgres
import config

class MockRawCursor:
    def __init__(self):
        self.description = [("ma_tu_sinh",), ("ho_ten",), ("dang_dung",)]
        self.rowcount = 1

    def execute(self, q, p):
        pass

    def fetchone(self):
        return (1, "Nguyễn Minh Quân 1", 1)

    def fetchall(self):
        return [(1, "Nguyễn Minh Quân 1", 1)]

    def close(self):
        pass

class TestPostgresAdapter(unittest.TestCase):
    def test_postgres_row_dict_and_index_access(self):
        desc = [("ma_tu_sinh",), ("ho_ten",), ("dang_dung",)]
        vals = (10, "Trần Văn Bình", 1)
        row = PostgresRow(desc, vals)
        self.assertEqual(row[0], 10)
        self.assertEqual(row["ma_tu_sinh"], 10)
        self.assertEqual(row["ho_ten"], "Trần Văn Bình")
        self.assertEqual(row.get("dang_dung"), 1)
        self.assertEqual(row.get("khong_co", "mac_dinh"), "mac_dinh")
        self.assertTrue("ho_ten" in row)
        self.assertEqual(len(row), 3)
        as_dict = dict(row)
        self.assertEqual(as_dict, {"ma_tu_sinh": 10, "ho_ten": "Trần Văn Bình", "dang_dung": 1})

    def test_cursor_query_transformation(self):
        raw = MockRawCursor()
        wrapper = PostgresCursorWrapper(raw)

        q1 = "CREATE TABLE test (id INTEGER PRIMARY KEY AUTOINCREMENT, ngay TEXT DEFAULT (datetime('now', 'localtime')))"
        t1, p1, r1 = wrapper._transform_query(q1)
        self.assertIn("SERIAL PRIMARY KEY", t1)
        self.assertIn("TO_CHAR(NOW() AT TIME ZONE 'Asia/Bangkok'", t1)
        self.assertFalse(r1)

        q2 = "SELECT * FROM quan_nhan WHERE ma_tu_sinh = ? AND dang_dung = ?"
        t2, p2, r2 = wrapper._transform_query(q2)
        self.assertIn("%s", t2)
        self.assertNotIn("?", t2)

        q3 = "INSERT INTO cap_bac (ma_cap_bac, ten_cap_bac) VALUES (?, ?)"
        t3, p3, r3 = wrapper._transform_query(q3)
        self.assertTrue(r3)
        self.assertTrue(t3.endswith("RETURNING ma_tu_sinh"))

        q4 = "PRAGMA table_info(lich_su_giao_nhan)"
        t4, p4, r4 = wrapper._transform_query(q4)
        self.assertIn("information_schema.columns", t4)
        self.assertEqual(p4, ["lich_su_giao_nhan"])

    def test_db_backend_toggle(self):
        import sys
        orig_backend = getattr(config, "DB_BACKEND", "auto")
        orig_url = getattr(config, "DATABASE_URL", None)
        saved_argv = list(sys.argv)
        saved_testing = getattr(config, "TESTING", False)
        saved_db_path = config.DATABASE_PATH
        try:
            config.DB_BACKEND = "sqlite"
            config.DATABASE_URL = "postgresql://user:pass@localhost:5432/db"
            self.assertFalse(nen_dung_postgres())

            sys.argv = ["app.py"]
            config.TESTING = False
            config.DATABASE_PATH = "/tmp/real_prod.db"

            config.DB_BACKEND = "postgres"
            config.DATABASE_URL = None
            with self.assertRaises(ValueError):
                nen_dung_postgres()

            config.DATABASE_URL = "postgresql://user:pass@localhost:5432/db"
            self.assertTrue(nen_dung_postgres())

            config.DB_BACKEND = "auto"
            self.assertTrue(nen_dung_postgres())

            config.DATABASE_URL = None
            self.assertFalse(nen_dung_postgres())
        finally:
            config.DB_BACKEND = orig_backend
            config.DATABASE_URL = orig_url
            sys.argv = saved_argv
            config.TESTING = saved_testing
            config.DATABASE_PATH = saved_db_path

    def test_live_postgres_connection_if_configured(self):
        if not getattr(config, "DATABASE_URL", None):
            self.skipTest("DATABASE_URL not configured")
        import pg8000.dbapi
        import ssl
        from urllib.parse import urlparse, unquote
        p = urlparse(config.DATABASE_URL)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        pw = unquote(p.password) if p.password else ""
        raw = pg8000.dbapi.connect(
            user=p.username,
            password=pw,
            host=p.hostname,
            port=p.port or 5432,
            database=p.path.lstrip("/"),
            ssl_context=ctx
        )
        cur = raw.cursor()
        cur.execute("SELECT COUNT(*) FROM tai_khoan")
        cnt = cur.fetchone()[0]
        self.assertGreaterEqual(cnt, 1)
        raw.close()

if __name__ == "__main__":
    unittest.main()
