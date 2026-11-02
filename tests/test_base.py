import os
import shutil
import tempfile
import unittest
import config
from app import tao_ung_dung
from models.co_so_du_lieu import khoi_tao_co_so_du_lieu, lay_ket_noi
from models.du_lieu_mau import nap_du_lieu_mau

class BaseTestCase(unittest.TestCase):
    original_db = None
    master_db_path = None
    app = None

    @classmethod
    def setUpClass(cls):
        cls.original_db = config.DATABASE_PATH
        fd, cls.master_db_path = tempfile.mkstemp(prefix="qldt_master_", suffix=".db")
        os.close(fd)
        config.DATABASE_PATH = cls.master_db_path
        khoi_tao_co_so_du_lieu()
        nap_du_lieu_mau()
        cls.app = tao_ung_dung()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False

    @classmethod
    def tearDownClass(cls):
        config.DATABASE_PATH = cls.original_db
        if cls.master_db_path and os.path.exists(cls.master_db_path):
            try:
                os.remove(cls.master_db_path)
            except Exception:
                pass

    def setUp(self):
        fd, self.test_db_path = tempfile.mkstemp(prefix="qldt_case_", suffix=".db")
        os.close(fd)
        shutil.copyfile(self.master_db_path, self.test_db_path)
        config.DATABASE_PATH = self.test_db_path
        self.client = self.app.test_client()

    def tearDown(self):
        config.DATABASE_PATH = self.master_db_path
        if hasattr(self, "test_db_path") and os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    def login(self, ten_dang_nhap, mat_khau):
        return self.client.post(
            "/dang-nhap",
            data={"ten_dang_nhap": ten_dang_nhap, "mat_khau": mat_khau},
            follow_redirects=True
        )

    def logout(self):
        return self.client.get("/dang-xuat", follow_redirects=True)

    def get_db(self):
        return lay_ket_noi()
