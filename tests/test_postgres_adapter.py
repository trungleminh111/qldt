import unittest
from models.co_so_du_lieu import PostgresRow, PostgresCursorWrapper, lay_ket_noi
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

        q4 = "PRAGMA table_info(ban_giao_ca)"
        t4, p4, r4 = wrapper._transform_query(q4)
        self.assertIn("information_schema.columns", t4)
        self.assertEqual(p4, ["ban_giao_ca"])

    def test_live_postgres_connection_if_configured(self):
        if not getattr(config, "DATABASE_URL", None):
            self.skipTest("DATABASE_URL not configured")
        import pg8000.dbapi
        import ssl
        from urllib.parse import urlparse
        p = urlparse(config.DATABASE_URL)
        ctx = ssl.create_default_context()
        raw = pg8000.dbapi.connect(
            user=p.username,
            password=p.password,
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
