from models.co_so_du_lieu import lay_ket_noi

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
