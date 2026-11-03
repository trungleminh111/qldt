import sqlite3
import os
import config

def lay_ket_noi():
    ket_noi = sqlite3.connect(config.DATABASE_PATH, timeout=30.0)
    ket_noi.row_factory = sqlite3.Row
    ket_noi.execute("PRAGMA foreign_keys = ON")
    ket_noi.execute("PRAGMA journal_mode = DELETE")
    ket_noi.execute("PRAGMA synchronous = FULL")
    ket_noi.execute("PRAGMA busy_timeout = 30000")
    return ket_noi

def kiem_tra_da_co_du_lieu():
    if not os.path.exists(config.DATABASE_PATH):
        return False
    try:
        ket_noi = lay_ket_noi()
        con_tro = ket_noi.cursor()
        con_tro.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tai_khoan'")
        if not con_tro.fetchone():
            ket_noi.close()
            return False
        con_tro.execute("SELECT COUNT(*) FROM tai_khoan")
        so_tk = con_tro.fetchone()[0]
        con_tro.execute("SELECT COUNT(*) FROM quan_nhan")
        so_qn = con_tro.fetchone()[0]
        con_tro.execute("SELECT COUNT(*) FROM cap_bac")
        so_cb = con_tro.fetchone()[0]
        ket_noi.close()
        return (so_tk > 0 or so_qn > 0 or so_cb > 0)
    except Exception:
        return False

def lay_danh_sach_don_vi_truc_thuoc(khoa_don_vi):
    if not khoa_don_vi:
        return []
    if isinstance(khoa_don_vi, (list, tuple, set)):
        ds_ban_dau = [int(x) for x in khoa_don_vi if str(x).isdigit()]
    elif isinstance(khoa_don_vi, str) and "," in khoa_don_vi:
        ds_ban_dau = [int(x.strip()) for x in khoa_don_vi.split(",") if x.strip().isdigit()]
    else:
        try:
            ds_ban_dau = [int(khoa_don_vi)]
        except (ValueError, TypeError):
            return []

    if not ds_ban_dau:
        return []

    try:
        ket_noi = lay_ket_noi()
        con_tro = ket_noi.cursor()
        placeholders = ",".join("?" for _ in ds_ban_dau)
        con_tro.execute(f"""
            WITH RECURSIVE cay_don_vi AS (
                SELECT ma_tu_sinh FROM don_vi WHERE ma_tu_sinh IN ({placeholders})
                UNION ALL
                SELECT dv.ma_tu_sinh FROM don_vi dv
                JOIN cay_don_vi c ON dv.khoa_don_vi_cha = c.ma_tu_sinh
                WHERE dv.dang_dung = 1
            )
            SELECT DISTINCT ma_tu_sinh FROM cay_don_vi
        """, ds_ban_dau)
        ket_qua = [r[0] for r in con_tro.fetchall()]
        ket_noi.close()
        return ket_qua or ds_ban_dau
    except Exception:
        return ds_ban_dau

def tao_dieu_kien_don_vi(cot_don_vi, khoa_don_vi_gioi_han):
    if not khoa_don_vi_gioi_han:
        return "", []
    ds_id = lay_danh_sach_don_vi_truc_thuoc(khoa_don_vi_gioi_han)
    if not ds_id:
        return f" AND {cot_don_vi} = -1", []
    if len(ds_id) == 1:
        return f" AND {cot_don_vi} = ?", [ds_id[0]]
    placeholders = ",".join("?" for _ in ds_id)
    return f" AND {cot_don_vi} IN ({placeholders})", ds_id

def kiem_tra_thuoc_don_vi(khoa_don_vi, khoa_don_vi_gioi_han):
    if not khoa_don_vi_gioi_han:
        return True
    if not khoa_don_vi:
        return False
    ds_id = lay_danh_sach_don_vi_truc_thuoc(khoa_don_vi_gioi_han)
    return int(khoa_don_vi) in ds_id

def khoi_tao_co_so_du_lieu():
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS cap_bac (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_cap_bac TEXT UNIQUE NOT NULL,
        ten_cap_bac TEXT NOT NULL,
        thu_tu INTEGER DEFAULT 0,
        dang_dung INTEGER DEFAULT 1
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS cau_hinh_gio (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_cau_hinh TEXT UNIQUE NOT NULL,
        ten_cau_hinh TEXT NOT NULL,
        mo_ta TEXT,
        hieu_luc_tu TEXT NOT NULL,
        hieu_luc_den TEXT,
        dang_dung INTEGER DEFAULT 1
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS khung_gio (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        khoa_cau_hinh_gio INTEGER NOT NULL,
        thu_trong_tuan INTEGER NOT NULL,
        gio_bat_dau TEXT NOT NULL,
        gio_ket_thuc TEXT NOT NULL,
        ghi_chu TEXT,
        dang_dung INTEGER DEFAULT 1,
        FOREIGN KEY (khoa_cau_hinh_gio) REFERENCES cau_hinh_gio(ma_tu_sinh)
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS ngay_dac_biet (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        ngay TEXT NOT NULL,
        pham_vi_loai TEXT NOT NULL,
        pham_vi_khoa INTEGER,
        khoa_cau_hinh_ghi_de INTEGER,
        cam_su_dung INTEGER DEFAULT 0,
        loai_lap TEXT DEFAULT 'MOT_LAN',
        ly_do TEXT NOT NULL,
        dang_dung INTEGER DEFAULT 1,
        FOREIGN KEY (khoa_cau_hinh_ghi_de) REFERENCES cau_hinh_gio(ma_tu_sinh)
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS don_vi (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_don_vi TEXT UNIQUE NOT NULL,
        ten_don_vi TEXT NOT NULL,
        khoa_don_vi_cha INTEGER,
        thu_tu INTEGER DEFAULT 0,
        dang_dung INTEGER DEFAULT 1,
        FOREIGN KEY (khoa_don_vi_cha) REFERENCES don_vi(ma_tu_sinh)
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS chuc_vu (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_chuc_vu TEXT UNIQUE NOT NULL,
        ten_chuc_vu TEXT NOT NULL,
        khoa_cau_hinh_gio INTEGER,
        thu_tu INTEGER DEFAULT 0,
        dang_dung INTEGER DEFAULT 1,
        FOREIGN KEY (khoa_cau_hinh_gio) REFERENCES cau_hinh_gio(ma_tu_sinh)
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS quan_nhan (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_quan_nhan TEXT UNIQUE NOT NULL,
        ho_ten TEXT NOT NULL,
        ngay_sinh TEXT,
        ngay_nhap_ngu TEXT,
        khoa_cap_bac INTEGER NOT NULL,
        khoa_chuc_vu INTEGER NOT NULL,
        khoa_don_vi INTEGER NOT NULL,
        co_dien_thoai INTEGER DEFAULT 1,
        trang_thai TEXT DEFAULT 'DANG_PHUC_VU',
        ghi_chu TEXT,
        da_xoa INTEGER DEFAULT 0,
        ngay_tao TEXT DEFAULT (datetime('now', 'localtime')),
        ngay_sua TEXT,
        FOREIGN KEY (khoa_cap_bac) REFERENCES cap_bac(ma_tu_sinh),
        FOREIGN KEY (khoa_chuc_vu) REFERENCES chuc_vu(ma_tu_sinh),
        FOREIGN KEY (khoa_don_vi) REFERENCES don_vi(ma_tu_sinh)
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS dien_thoai (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_thiet_bi TEXT UNIQUE NOT NULL,
        ten_dien_thoai TEXT NOT NULL,
        hang_san_xuat TEXT,
        model TEXT,
        so_imei TEXT UNIQUE,
        so_dien_thoai TEXT,
        khoa_quan_nhan INTEGER NOT NULL,
        tinh_trang TEXT DEFAULT 'DANG_DUNG',
        ghi_chu TEXT,
        da_xoa INTEGER DEFAULT 0,
        ngay_tao TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (khoa_quan_nhan) REFERENCES quan_nhan(ma_tu_sinh)
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS tu (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_tu TEXT UNIQUE NOT NULL,
        ten_tu TEXT NOT NULL,
        vi_tri TEXT,
        so_ngan INTEGER DEFAULT 24,
        khoa_don_vi_quan_ly INTEGER,
        dang_dung INTEGER DEFAULT 1,
        FOREIGN KEY (khoa_don_vi_quan_ly) REFERENCES don_vi(ma_tu_sinh)
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS ngan (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_ngan TEXT UNIQUE NOT NULL,
        ten_ngan TEXT NOT NULL,
        khoa_tu INTEGER NOT NULL,
        khoa_quan_nhan INTEGER UNIQUE,
        dang_dung INTEGER DEFAULT 1,
        FOREIGN KEY (khoa_tu) REFERENCES tu(ma_tu_sinh),
        FOREIGN KEY (khoa_quan_nhan) REFERENCES quan_nhan(ma_tu_sinh)
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS ngoai_le (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        khoa_quan_nhan INTEGER NOT NULL,
        tu_gio TEXT NOT NULL,
        den_gio TEXT NOT NULL,
        loai_ngoai_le TEXT NOT NULL,
        ly_do TEXT NOT NULL,
        khoa_nguoi_de_nghi INTEGER NOT NULL,
        khoa_nguoi_duyet INTEGER,
        trang_thai TEXT DEFAULT 'CHO_DUYET',
        thoi_gian_duyet TEXT,
        ly_do_tu_choi TEXT,
        FOREIGN KEY (khoa_quan_nhan) REFERENCES quan_nhan(ma_tu_sinh)
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS lich_su_giao_nhan (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        khoa_quan_nhan INTEGER NOT NULL,
        khoa_dien_thoai INTEGER NOT NULL,
        khoa_ngan INTEGER,
        thoi_gian TEXT NOT NULL,
        loai TEXT NOT NULL,
        ket_qua TEXT NOT NULL,
        khoa_khung_gio INTEGER,
        khoa_cau_hinh_gio INTEGER,
        khoa_chuc_vu INTEGER,
        khoa_ngoai_le INTEGER,
        khoa_nguoi_thuc_hien INTEGER NOT NULL,
        ten_nguoi_thuc_hien TEXT,
        ma_vai_tro TEXT,
        la_ban_ghi_dieu_chinh INTEGER DEFAULT 0,
        khoa_ban_ghi_goc INTEGER,
        ghi_chu TEXT,
        FOREIGN KEY (khoa_quan_nhan) REFERENCES quan_nhan(ma_tu_sinh),
        FOREIGN KEY (khoa_dien_thoai) REFERENCES dien_thoai(ma_tu_sinh),
        FOREIGN KEY (khoa_ngan) REFERENCES ngan(ma_tu_sinh),
        FOREIGN KEY (khoa_ngoai_le) REFERENCES ngoai_le(ma_tu_sinh)
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS ca_truc (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_ca TEXT UNIQUE NOT NULL,
        ten_ca TEXT NOT NULL,
        gio_bat_dau TEXT NOT NULL,
        gio_ket_thuc TEXT NOT NULL,
        dang_dung INTEGER DEFAULT 1
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS ban_giao_ca (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        khoa_ca_truc INTEGER NOT NULL,
        ngay_truc TEXT NOT NULL,
        khoa_nguoi_ban_giao INTEGER NOT NULL,
        khoa_nguoi_nhan INTEGER NOT NULL,
        tong_thiet_bi INTEGER DEFAULT 0,
        dang_trong_tu INTEGER DEFAULT 0,
        da_lay INTEGER DEFAULT 0,
        chua_nop INTEGER DEFAULT 0,
        bat_thuong INTEGER DEFAULT 0,
        ghi_chu_ban_giao TEXT,
        thoi_gian_ban_giao TEXT DEFAULT (datetime('now', 'localtime')),
        trang_thai TEXT DEFAULT 'DA_BAN_GIAO',
        du_lieu_snapshot TEXT,
        ma_tu_snapshot TEXT,
        ten_ngan_snapshot TEXT,
        so_qua_han INTEGER DEFAULT 0,
        FOREIGN KEY (khoa_ca_truc) REFERENCES ca_truc(ma_tu_sinh)
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS tai_khoan (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        ten_dang_nhap TEXT UNIQUE NOT NULL,
        mat_khau_ma_hoa TEXT NOT NULL,
        ho_ten TEXT NOT NULL,
        khoa_quan_nhan INTEGER UNIQUE,
        loai_tai_khoan TEXT DEFAULT 'NGUOI_DUNG',
        dang_dung INTEGER DEFAULT 1,
        dang_nhap_cuoi TEXT,
        ngay_tao TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (khoa_quan_nhan) REFERENCES quan_nhan(ma_tu_sinh)
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS vai_tro (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_vai_tro TEXT UNIQUE NOT NULL,
        ten_vai_tro TEXT NOT NULL,
        mo_ta TEXT,
        la_he_thong INTEGER DEFAULT 0,
        dang_dung INTEGER DEFAULT 1
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS quyen_han (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_quyen TEXT UNIQUE NOT NULL,
        nhom TEXT NOT NULL,
        ten_quyen TEXT NOT NULL,
        mo_ta TEXT
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS vai_tro_quyen (
        khoa_vai_tro INTEGER NOT NULL,
        khoa_quyen INTEGER NOT NULL,
        PRIMARY KEY (khoa_vai_tro, khoa_quyen),
        FOREIGN KEY (khoa_vai_tro) REFERENCES vai_tro(ma_tu_sinh),
        FOREIGN KEY (khoa_quyen) REFERENCES quyen_han(ma_tu_sinh)
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS tai_khoan_vai_tro (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        khoa_tai_khoan INTEGER NOT NULL,
        khoa_vai_tro INTEGER NOT NULL,
        pham_vi_loai TEXT DEFAULT 'TOAN_BO',
        pham_vi_khoa INTEGER,
        hieu_luc_tu TEXT NOT NULL,
        hieu_luc_den TEXT,
        dang_dung INTEGER DEFAULT 1,
        FOREIGN KEY (khoa_tai_khoan) REFERENCES tai_khoan(ma_tu_sinh),
        FOREIGN KEY (khoa_vai_tro) REFERENCES vai_tro(ma_tu_sinh)
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS nhat_ky (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        thoi_gian TEXT DEFAULT (datetime('now', 'localtime')),
        khoa_tai_khoan INTEGER,
        ten_nguoi_thao_tac TEXT,
        dia_chi_ip TEXT,
        ten_bang TEXT,
        khoa_ban_ghi INTEGER,
        hanh_dong TEXT NOT NULL,
        du_lieu_cu TEXT,
        du_lieu_moi TEXT,
        ly_do TEXT
    )
    """)

    con_tro.execute("""
    CREATE TABLE IF NOT EXISTS vi_pham (
        ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
        khoa_quan_nhan INTEGER NOT NULL,
        khoa_giao_nhan INTEGER,
        loai TEXT NOT NULL,
        thoi_gian TEXT NOT NULL,
        noi_dung TEXT,
        trang_thai TEXT DEFAULT 'MOI',
        khoa_nguoi_xu_ly INTEGER,
        ket_qua_xu_ly TEXT,
        FOREIGN KEY (khoa_quan_nhan) REFERENCES quan_nhan(ma_tu_sinh),
        FOREIGN KEY (khoa_giao_nhan) REFERENCES lich_su_giao_nhan(ma_tu_sinh)
    )
    """)

    con_tro.execute("CREATE INDEX IF NOT EXISTS idx_qn_ma ON quan_nhan(ma_quan_nhan)")
    con_tro.execute("CREATE INDEX IF NOT EXISTS idx_qn_donvi ON quan_nhan(khoa_don_vi)")
    con_tro.execute("CREATE INDEX IF NOT EXISTS idx_dt_ma ON dien_thoai(ma_thiet_bi)")
    con_tro.execute("CREATE INDEX IF NOT EXISTS idx_dt_qn ON dien_thoai(khoa_quan_nhan)")
    con_tro.execute("CREATE INDEX IF NOT EXISTS idx_gn_thoigian ON lich_su_giao_nhan(thoi_gian)")
    con_tro.execute("CREATE INDEX IF NOT EXISTS idx_gn_qn ON lich_su_giao_nhan(khoa_quan_nhan)")
    con_tro.execute("CREATE INDEX IF NOT EXISTS idx_gn_dt ON lich_su_giao_nhan(khoa_dien_thoai)")

    ket_noi.commit()
    ket_noi.close()
    kiem_tra_va_nang_cap_bang_ban_giao()

def kiem_tra_va_nang_cap_bang_ban_giao():
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("PRAGMA table_info(ban_giao_ca)")
    cot_hien_co = [row["name"] for row in con_tro.fetchall()]
    if "du_lieu_snapshot" not in cot_hien_co:
        con_tro.execute("ALTER TABLE ban_giao_ca ADD COLUMN du_lieu_snapshot TEXT")
    if "ma_tu_snapshot" not in cot_hien_co:
        con_tro.execute("ALTER TABLE ban_giao_ca ADD COLUMN ma_tu_snapshot TEXT")
    if "ten_ngan_snapshot" not in cot_hien_co:
        con_tro.execute("ALTER TABLE ban_giao_ca ADD COLUMN ten_ngan_snapshot TEXT")
    if "so_qua_han" not in cot_hien_co:
        con_tro.execute("ALTER TABLE ban_giao_ca ADD COLUMN so_qua_han INTEGER DEFAULT 0")

    con_tro.execute("PRAGMA table_info(ngay_dac_biet)")
    cot_ndb = [row["name"] for row in con_tro.fetchall()]
    if cot_ndb and "loai_lap" not in cot_ndb:
        con_tro.execute("ALTER TABLE ngay_dac_biet ADD COLUMN loai_lap TEXT DEFAULT 'MOT_LAN'")

    ket_noi.commit()
    ket_noi.close()

def khoi_tao_csdl():
    khoi_tao_co_so_du_lieu()

def ghi_nhat_ky(khoa_tai_khoan=None, ten_nguoi_thao_tac=None, dia_chi_ip=None, ten_bang=None, khoa_ban_ghi=None, hanh_dong="THAO_TAC", du_lieu_cu=None, du_lieu_moi=None, ly_do=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        INSERT INTO nhat_ky (
            khoa_tai_khoan, ten_nguoi_thao_tac, dia_chi_ip, ten_bang,
            khoa_ban_ghi, hanh_dong, du_lieu_cu, du_lieu_moi, ly_do
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (khoa_tai_khoan, ten_nguoi_thao_tac, dia_chi_ip, ten_bang, khoa_ban_ghi, hanh_dong, du_lieu_cu, du_lieu_moi, ly_do))
    id_moi = con_tro.lastrowid
    ket_noi.commit()
    ket_noi.close()
    return id_moi

