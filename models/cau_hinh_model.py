import time
from models.co_so_du_lieu import lay_ket_noi

_cache_thong_tin_don_vi = None
_cache_thong_tin_don_vi_time = 0

def lay_tat_ca_cau_hinh_gio():
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT * FROM cau_hinh_gio WHERE dang_dung = 1 ORDER BY ma_tu_sinh ASC")
    ket_qua = [dict(row) for row in con_tro.fetchall()]
    ket_noi.close()
    return ket_qua

def lay_khung_gio_theo_cau_hinh(khoa_cau_hinh=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    cau_lenh = """
        SELECT kg.*, ch.ten_cau_hinh, ch.ma_cau_hinh
        FROM khung_gio kg
        JOIN cau_hinh_gio ch ON kg.khoa_cau_hinh_gio = ch.ma_tu_sinh
        WHERE kg.dang_dung = 1
    """
    tham_so = []
    if khoa_cau_hinh:
        cau_lenh += " AND kg.khoa_cau_hinh_gio = ?"
        tham_so.append(khoa_cau_hinh)

    cau_lenh += " ORDER BY kg.khoa_cau_hinh_gio ASC, kg.thu_trong_tuan ASC, kg.gio_bat_dau ASC"
    con_tro.execute(cau_lenh, tham_so)
    map_thu = {2: "Thứ Hai", 3: "Thứ Ba", 4: "Thứ Tư", 5: "Thứ Năm", 6: "Thứ Sáu", 7: "Thứ Bảy", 8: "Chủ Nhật"}
    danh_sach = []
    for row in con_tro.fetchall():
        d = dict(row)
        d["ten_thu"] = map_thu.get(d["thu_trong_tuan"], "")
        danh_sach.append(d)

    ket_noi.close()
    return danh_sach

def lay_chi_tiet_khung_gio(ma_tu_sinh):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT * FROM khung_gio WHERE ma_tu_sinh = ?", (ma_tu_sinh,))
    row = con_tro.fetchone()
    ket_qua = dict(row) if row else None
    ket_noi.close()
    return ket_qua

def them_cau_hinh_gio(ma_cau_hinh, ten_cau_hinh, mo_ta=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        INSERT INTO cau_hinh_gio (ma_cau_hinh, ten_cau_hinh, mo_ta, hieu_luc_tu)
        VALUES (?, ?, ?, date('now'))
    """, (ma_cau_hinh, ten_cau_hinh, mo_ta))
    id_moi = con_tro.lastrowid
    ket_noi.commit()
    ket_noi.close()
    return id_moi

def them_khung_gio(khoa_cau_hinh_gio, thu_trong_tuan, gio_bat_dau, gio_ket_thuc, ghi_chu=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        INSERT INTO khung_gio (khoa_cau_hinh_gio, thu_trong_tuan, gio_bat_dau, gio_ket_thuc, ghi_chu)
        VALUES (?, ?, ?, ?, ?)
    """, (khoa_cau_hinh_gio, thu_trong_tuan, gio_bat_dau, gio_ket_thuc, ghi_chu))
    id_moi = con_tro.lastrowid
    ket_noi.commit()
    ket_noi.close()
    return id_moi

def sua_khung_gio(ma_tu_sinh, khoa_cau_hinh_gio, thu_trong_tuan, gio_bat_dau, gio_ket_thuc, ghi_chu=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        UPDATE khung_gio
        SET khoa_cau_hinh_gio = ?, thu_trong_tuan = ?, gio_bat_dau = ?, gio_ket_thuc = ?, ghi_chu = ?
        WHERE ma_tu_sinh = ?
    """, (khoa_cau_hinh_gio, thu_trong_tuan, gio_bat_dau, gio_ket_thuc, ghi_chu, ma_tu_sinh))
    ket_noi.commit()
    ket_noi.close()

def xoa_khung_gio(ma_tu_sinh):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("DELETE FROM khung_gio WHERE ma_tu_sinh = ?", (ma_tu_sinh,))
    ket_noi.commit()
    ket_noi.close()

def lay_mo_ta_loai_lap(loai_lap, ngay_str):
    if not loai_lap or loai_lap == "MOT_LAN":
        return "Một lần"
    try:
        from datetime import datetime
        dt = datetime.strptime(ngay_str, "%Y-%m-%d")
        if loai_lap == "HANG_NAM":
            return f"Hàng năm ({dt.strftime('%d/%m')})"
        elif loai_lap == "HANG_THANG":
            return f"Hàng tháng (Ngày {dt.strftime('%d')})"
        elif loai_lap == "HANG_TUAN":
            thu_so = dt.weekday() + 2
            ten_thu = "Chủ Nhật" if thu_so == 8 else f"Thứ {thu_so}"
            return f"Hàng tuần ({ten_thu})"
    except Exception:
        pass
    return loai_lap

def lay_danh_sach_ngay_dac_biet():
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        SELECT ndb.*, ch.ten_cau_hinh AS ten_cau_hinh_ghi_de
        FROM ngay_dac_biet ndb
        LEFT JOIN cau_hinh_gio ch ON ndb.khoa_cau_hinh_ghi_de = ch.ma_tu_sinh
        WHERE ndb.dang_dung = 1
        ORDER BY ndb.ngay DESC
    """)
    ket_qua = [dict(row) for row in con_tro.fetchall()]
    for item in ket_qua:
        item["mo_ta_loai_lap"] = lay_mo_ta_loai_lap(item.get("loai_lap"), item["ngay"])
    ket_noi.close()
    return ket_qua

def them_ngay_dac_biet(ngay, ly_do, cam_su_dung=0, khoa_cau_hinh_ghi_de=None, loai_lap="MOT_LAN"):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        INSERT INTO ngay_dac_biet (ngay, pham_vi_loai, cam_su_dung, ly_do, khoa_cau_hinh_ghi_de, loai_lap)
        VALUES (?, 'TOAN_BO', ?, ?, ?, ?)
    """, (ngay, cam_su_dung, ly_do, khoa_cau_hinh_ghi_de, loai_lap or "MOT_LAN"))
    id_moi = con_tro.lastrowid
    ket_noi.commit()
    ket_noi.close()
    return id_moi

def sua_ngay_dac_biet(ma_tu_sinh, ngay, ly_do, cam_su_dung=0, khoa_cau_hinh_ghi_de=None, loai_lap="MOT_LAN"):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        UPDATE ngay_dac_biet
        SET ngay = ?, ly_do = ?, cam_su_dung = ?, khoa_cau_hinh_ghi_de = ?, loai_lap = ?
        WHERE ma_tu_sinh = ?
    """, (ngay, ly_do, cam_su_dung, khoa_cau_hinh_ghi_de, loai_lap or "MOT_LAN", ma_tu_sinh))
    ket_noi.commit()
    ket_noi.close()

def xoa_ngay_dac_biet(ma_tu_sinh):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("DELETE FROM ngay_dac_biet WHERE ma_tu_sinh = ?", (ma_tu_sinh,))
    ket_noi.commit()
    ket_noi.close()

def lay_thong_tin_don_vi(force_refresh=False):
    global _cache_thong_tin_don_vi, _cache_thong_tin_don_vi_time
    now = time.time()
    if not force_refresh and _cache_thong_tin_don_vi and (now - _cache_thong_tin_don_vi_time < 300.0):
        return dict(_cache_thong_tin_don_vi)

    gia_tri_mac_dinh = {
        "don_vi_cap_tren": "TIỂU ĐOÀN 3",
        "ten_don_vi": "ĐẠI ĐỘI 11",
        "dia_diem": "Đà Nẵng",
        "can_cu_quy_dinh": "Quy định số 763/QyĐ-SĐ ngày 12/3/2026 của Sư đoàn về việc quản lý, sử dụng thiết bị điện tử trong đơn vị",
        "chuc_danh_chi_huy": "CHỈ HUY ĐẠI ĐỘI",
        "noi_nhan": "- CH/d (để theo dõi);\n- Lưu: c."
    }
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    try:
        con_tro.execute("SELECT khoa_thiet_lap, gia_tri FROM thong_tin_don_vi")
        rows = con_tro.fetchall()
        for row in rows:
            if isinstance(row, dict):
                k = row.get("khoa_thiet_lap")
                v = row.get("gia_tri")
            elif hasattr(row, "keys"):
                k = row["khoa_thiet_lap"]
                v = row["gia_tri"]
            else:
                k = row[0]
                v = row[1]
            if k in gia_tri_mac_dinh and v is not None and str(v).strip():
                gia_tri_mac_dinh[k] = str(v).strip()
    except Exception:
        pass
    finally:
        ket_noi.close()

    _cache_thong_tin_don_vi = dict(gia_tri_mac_dinh)
    _cache_thong_tin_don_vi_time = now
    return gia_tri_mac_dinh

def cap_nhat_thong_tin_don_vi(du_lieu):
    global _cache_thong_tin_don_vi
    _cache_thong_tin_don_vi = None
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        CREATE TABLE IF NOT EXISTS thong_tin_don_vi (
            khoa_thiet_lap TEXT PRIMARY KEY,
            gia_tri TEXT
        )
    """)
    for k, v in du_lieu.items():
        val = str(v).strip() if v is not None else ""
        con_tro.execute("SELECT COUNT(*) FROM thong_tin_don_vi WHERE khoa_thiet_lap = ?", (k,))
        ton_tai = con_tro.fetchone()[0] > 0
        if ton_tai:
            con_tro.execute("UPDATE thong_tin_don_vi SET gia_tri = ? WHERE khoa_thiet_lap = ?", (val, k))
        else:
            con_tro.execute("INSERT INTO thong_tin_don_vi (khoa_thiet_lap, gia_tri) VALUES (?, ?)", (k, val))
    ket_noi.commit()
    ket_noi.close()
