from datetime import datetime
from models.co_so_du_lieu import lay_ket_noi, tao_dieu_kien_don_vi

def lay_tat_ca_dien_thoai(tu_khoa=None, ma_don_vi=None, khoa_don_vi_gioi_han=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    cau_lenh = """
        SELECT dt.ma_tu_sinh, dt.ma_thiet_bi, dt.ten_dien_thoai, dt.hang_san_xuat, dt.model, dt.so_imei, dt.so_dien_thoai,
               qn.ma_quan_nhan, qn.ho_ten AS ten_quan_nhan, cb.ten_cap_bac, dv.ten_don_vi,
               ng.ma_ngan, ng.ten_ngan, t.ma_tu, t.ten_tu,
               CASE
                   WHEN gn.loai = 'LAY_RA' THEN 'Đã lấy'
                   ELSE 'Trong tủ'
               END AS trang_thai_hien_tai,
               gn.thoi_gian AS lan_giao_dich_cuoi
        FROM dien_thoai dt
        JOIN quan_nhan qn ON dt.khoa_quan_nhan = qn.ma_tu_sinh
        JOIN cap_bac cb ON qn.khoa_cap_bac = cb.ma_tu_sinh
        JOIN don_vi dv ON qn.khoa_don_vi = dv.ma_tu_sinh
        LEFT JOIN ngan ng ON ng.khoa_quan_nhan = qn.ma_tu_sinh
        LEFT JOIN tu t ON ng.khoa_tu = t.ma_tu_sinh
        LEFT JOIN (
            SELECT gn1.khoa_dien_thoai, gn1.loai, gn1.thoi_gian
            FROM lich_su_giao_nhan gn1
            INNER JOIN (
                SELECT khoa_dien_thoai, MAX(ma_tu_sinh) AS max_id
                FROM lich_su_giao_nhan
                GROUP BY khoa_dien_thoai
            ) gn2 ON gn1.ma_tu_sinh = gn2.max_id
        ) gn ON gn.khoa_dien_thoai = dt.ma_tu_sinh
        WHERE dt.da_xoa = 0
    """
    tham_so = []
    if tu_khoa:
        cau_lenh += " AND (dt.ma_thiet_bi LIKE ? OR dt.ten_dien_thoai LIKE ? OR qn.ho_ten LIKE ? OR dt.so_imei LIKE ?)"
        tk = f"%{tu_khoa}%"
        tham_so.extend([tk, tk, tk, tk])
    if khoa_don_vi_gioi_han:
        dieu_kien, params = tao_dieu_kien_don_vi("qn.khoa_don_vi", khoa_don_vi_gioi_han)
        cau_lenh += dieu_kien
        tham_so.extend(params)
    elif ma_don_vi and ma_don_vi != "TAT_CA":
        cau_lenh += " AND (dv.ma_don_vi = ? OR dv.ma_tu_sinh = ?)"
        tham_so.extend([ma_don_vi, ma_don_vi])

    cau_lenh += " ORDER BY dt.ma_tu_sinh ASC"
    con_tro.execute(cau_lenh, tham_so)
    ket_qua = [dict(row) for row in con_tro.fetchall()]
    ket_noi.close()
    return ket_qua

def lay_chi_tiet_dien_thoai(ma_tu_sinh, khoa_don_vi_gioi_han=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    cau_lenh = """
        SELECT dt.*, qn.ma_quan_nhan, qn.ho_ten AS ten_quan_nhan, qn.khoa_don_vi, cb.ten_cap_bac, cv.ten_chuc_vu, dv.ten_don_vi,
               ng.ma_ngan, ng.ten_ngan, t.ma_tu, t.ten_tu,
               CASE
                   WHEN gn.loai = 'LAY_RA' THEN 'Đã lấy'
                   ELSE 'Trong tủ'
               END AS trang_thai_hien_tai
        FROM dien_thoai dt
        JOIN quan_nhan qn ON dt.khoa_quan_nhan = qn.ma_tu_sinh
        JOIN cap_bac cb ON qn.khoa_cap_bac = cb.ma_tu_sinh
        JOIN chuc_vu cv ON qn.khoa_chuc_vu = cv.ma_tu_sinh
        JOIN don_vi dv ON qn.khoa_don_vi = dv.ma_tu_sinh
        LEFT JOIN ngan ng ON ng.khoa_quan_nhan = qn.ma_tu_sinh
        LEFT JOIN tu t ON ng.khoa_tu = t.ma_tu_sinh
        LEFT JOIN (
            SELECT gn1.khoa_dien_thoai, gn1.loai
            FROM lich_su_giao_nhan gn1
            INNER JOIN (
                SELECT khoa_dien_thoai, MAX(ma_tu_sinh) AS max_id
                FROM lich_su_giao_nhan
                GROUP BY khoa_dien_thoai
            ) gn2 ON gn1.ma_tu_sinh = gn2.max_id
        ) gn ON gn.khoa_dien_thoai = dt.ma_tu_sinh
        WHERE (dt.ma_tu_sinh = ? OR dt.ma_thiet_bi = ?) AND dt.da_xoa = 0
    """
    tham_so = [ma_tu_sinh, ma_tu_sinh]
    if khoa_don_vi_gioi_han:
        dieu_kien, params = tao_dieu_kien_don_vi("qn.khoa_don_vi", khoa_don_vi_gioi_han)
        cau_lenh += dieu_kien
        tham_so.extend(params)
    con_tro.execute(cau_lenh, tham_so)
    dong = con_tro.fetchone()
    ket_qua = dict(dong) if dong else None
    ket_noi.close()
    return ket_qua

def them_dien_thoai(ma_thiet_bi, ten_dien_thoai, hang_san_xuat, model, so_imei, so_dien_thoai, khoa_quan_nhan, ma_ngan=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        INSERT INTO dien_thoai (ma_thiet_bi, ten_dien_thoai, hang_san_xuat, model, so_imei, so_dien_thoai, khoa_quan_nhan)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ma_thiet_bi, ten_dien_thoai, hang_san_xuat, model, so_imei, so_dien_thoai, khoa_quan_nhan))
    id_moi = con_tro.lastrowid

    if ma_ngan:
        con_tro.execute("UPDATE ngan SET khoa_quan_nhan = NULL WHERE khoa_quan_nhan = ?", (khoa_quan_nhan,))
        con_tro.execute("UPDATE ngan SET khoa_quan_nhan = ? WHERE ma_ngan = ?", (khoa_quan_nhan, ma_ngan))

    ket_noi.commit()
    ket_noi.close()
    return id_moi

def sua_dien_thoai(ma_tu_sinh, ten_dien_thoai, hang_san_xuat, model, so_imei, so_dien_thoai, khoa_quan_nhan, ma_ngan=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        UPDATE dien_thoai
        SET ten_dien_thoai = ?, hang_san_xuat = ?, model = ?, so_imei = ?, so_dien_thoai = ?, khoa_quan_nhan = ?
        WHERE ma_tu_sinh = ?
    """, (ten_dien_thoai, hang_san_xuat, model, so_imei, so_dien_thoai, khoa_quan_nhan, ma_tu_sinh))

    if ma_ngan:
        con_tro.execute("UPDATE ngan SET khoa_quan_nhan = NULL WHERE khoa_quan_nhan = ?", (khoa_quan_nhan,))
        con_tro.execute("UPDATE ngan SET khoa_quan_nhan = ? WHERE ma_ngan = ?", (khoa_quan_nhan, ma_ngan))

    ket_noi.commit()
    ket_noi.close()

def lay_danh_sach_tu(khoa_don_vi_gioi_han=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    cau_lenh = """
        SELECT t.ma_tu_sinh, t.ma_tu, t.ten_tu, t.vi_tri, t.so_ngan, t.khoa_don_vi_quan_ly, dv.ten_don_vi,
               COUNT(ng.ma_tu_sinh) AS tong_ngan,
               SUM(CASE WHEN ng.ma_tu_sinh IS NOT NULL AND ng.khoa_quan_nhan IS NOT NULL THEN 1 ELSE 0 END) AS so_ngan_co_chu,
               SUM(CASE WHEN ng.ma_tu_sinh IS NOT NULL AND ng.khoa_quan_nhan IS NULL THEN 1 ELSE 0 END) AS so_ngan_trong
        FROM tu t
        LEFT JOIN don_vi dv ON t.khoa_don_vi_quan_ly = dv.ma_tu_sinh
        LEFT JOIN ngan ng ON ng.khoa_tu = t.ma_tu_sinh
        WHERE t.dang_dung = 1
    """
    tham_so = []
    if khoa_don_vi_gioi_han:
        dieu_kien, params = tao_dieu_kien_don_vi("t.khoa_don_vi_quan_ly", khoa_don_vi_gioi_han)
        cau_lenh += dieu_kien
        tham_so.extend(params)
    cau_lenh += """
        GROUP BY t.ma_tu_sinh
        ORDER BY t.ma_tu ASC
    """
    con_tro.execute(cau_lenh, tham_so)
    ket_qua = [dict(row) for row in con_tro.fetchall()]
    ket_noi.close()
    return ket_qua

def lay_so_do_tu(ma_tu_code="T01", khoa_don_vi_gioi_han=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    cau_lenh = """
        SELECT ng.ma_tu_sinh, ng.ma_ngan, ng.ten_ngan, ng.khoa_quan_nhan,
               dt.ma_tu_sinh AS khoa_dien_thoai,
               qn.ma_quan_nhan, qn.ho_ten, qn.khoa_cap_bac, cb.ten_cap_bac,
               dt.ma_thiet_bi, dt.ten_dien_thoai, dt.hang_san_xuat,
               CASE
                   WHEN ng.khoa_quan_nhan IS NULL THEN 'TRONG'
                   WHEN gn.loai = 'LAY_RA' THEN 'DA_LAY'
                   ELSE 'DANG_LUU'
               END AS trang_thai_ngan,
               gn.thoi_gian AS gio_lay
        FROM ngan ng
        JOIN tu t ON ng.khoa_tu = t.ma_tu_sinh
        LEFT JOIN quan_nhan qn ON ng.khoa_quan_nhan = qn.ma_tu_sinh AND qn.da_xoa = 0
        LEFT JOIN cap_bac cb ON qn.khoa_cap_bac = cb.ma_tu_sinh
        LEFT JOIN dien_thoai dt ON dt.khoa_quan_nhan = qn.ma_tu_sinh AND dt.da_xoa = 0
        LEFT JOIN (
            SELECT gn1.khoa_dien_thoai, gn1.loai, gn1.thoi_gian
            FROM lich_su_giao_nhan gn1
            INNER JOIN (
                SELECT khoa_dien_thoai, MAX(ma_tu_sinh) AS max_id
                FROM lich_su_giao_nhan
                GROUP BY khoa_dien_thoai
            ) gn2 ON gn1.ma_tu_sinh = gn2.max_id
        ) gn ON gn.khoa_dien_thoai = dt.ma_tu_sinh
        WHERE t.ma_tu = ?
    """
    tham_so = [ma_tu_code]
    if khoa_don_vi_gioi_han:
        dieu_kien, params = tao_dieu_kien_don_vi("t.khoa_don_vi_quan_ly", khoa_don_vi_gioi_han)
        cau_lenh += dieu_kien
        tham_so.extend(params)
    cau_lenh += " ORDER BY ng.ma_ngan ASC"
    con_tro.execute(cau_lenh, tham_so)
    ket_qua = [dict(row) for row in con_tro.fetchall()]
    ket_noi.close()
    bay_gio = datetime.now()
    for item in ket_qua:
        item["qua_han"] = 0
        if item["trang_thai_ngan"] == "DA_LAY" and item.get("gio_lay"):
            try:
                thoi_gian_lay = datetime.strptime(item["gio_lay"], "%Y-%m-%d %H:%M:%S")
                phut_da_qua = int((bay_gio - thoi_gian_lay).total_seconds() / 60)
                item["phut_da_qua"] = phut_da_qua
                if phut_da_qua > 120:
                    item["qua_han"] = 1
                    item["trang_thai_ngan"] = "QUA_HAN"
            except Exception:
                pass
    return ket_qua

def lay_tat_ca_ngan_trong(khoa_don_vi_gioi_han=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    cau_lenh = """
        SELECT ng.ma_tu_sinh, ng.ma_ngan, ng.ten_ngan, t.ma_tu, t.ten_tu
        FROM ngan ng
        JOIN tu t ON ng.khoa_tu = t.ma_tu_sinh
        WHERE ng.khoa_quan_nhan IS NULL AND ng.dang_dung = 1
    """
    tham_so = []
    if khoa_don_vi_gioi_han:
        dieu_kien, params = tao_dieu_kien_don_vi("t.khoa_don_vi_quan_ly", khoa_don_vi_gioi_han)
        cau_lenh += dieu_kien
        tham_so.extend(params)
    cau_lenh += " ORDER BY ng.ma_ngan ASC"
    con_tro.execute(cau_lenh, tham_so)
    ket_qua = [dict(row) for row in con_tro.fetchall()]
    ket_noi.close()
    return ket_qua

def lay_goi_y_tu_tiep_theo():
    import re
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT ma_tu FROM tu ORDER BY ma_tu_sinh DESC")
    rows = con_tro.fetchall()
    ket_noi.close()
    max_num = 0
    for r in rows:
        m = re.search(r"(\d+)", r["ma_tu"])
        if m:
            num = int(m.group(1))
            if num > max_num:
                max_num = num
    next_num = max_num + 1 if max_num > 0 else len(rows) + 1
    ma_tu_goi_y = f"T{next_num:02d}"
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    tien_to_goi_y = letters[(next_num - 1) % len(letters)]
    return {
        "ma_tu": ma_tu_goi_y,
        "tien_to_ngan": tien_to_goi_y,
        "ten_tu": f"Tủ bảo quản {next_num}"
    }

def them_tu(ma_tu, ten_tu, vi_tri="", so_ngan=24, khoa_don_vi_quan_ly=None, tien_to_ngan=None):
    import re
    ma_tu = (ma_tu or "").strip().upper()
    ten_tu = (ten_tu or "").strip()
    vi_tri = (vi_tri or "").strip()
    so_ngan = int(so_ngan) if so_ngan else 24
    if so_ngan < 1:
        so_ngan = 1
    if so_ngan > 100:
        so_ngan = 100

    if not tien_to_ngan or not str(tien_to_ngan).strip():
        m = re.search(r"(\d+)", ma_tu)
        num = int(m.group(1)) if m else 1
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        tien_to_ngan = letters[(num - 1) % len(letters)]
    else:
        tien_to_ngan = str(tien_to_ngan).strip().upper()

    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        INSERT INTO tu (ma_tu, ten_tu, vi_tri, so_ngan, khoa_don_vi_quan_ly, dang_dung)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (ma_tu, ten_tu, vi_tri, so_ngan, khoa_don_vi_quan_ly))
    khoa_tu = con_tro.lastrowid

    for i in range(1, so_ngan + 1):
        ten_ngan = f"{tien_to_ngan}{i:02d}"
        ma_ngan = f"{ma_tu}-{ten_ngan}"
        con_tro.execute("""
            INSERT INTO ngan (ma_ngan, ten_ngan, khoa_tu, khoa_quan_nhan, dang_dung)
            VALUES (?, ?, ?, NULL, 1)
        """, (ma_ngan, ten_ngan, khoa_tu))

    ket_noi.commit()
    ket_noi.close()
    return khoa_tu

def lay_goi_y_ngan_tiep_theo(khoa_tu):
    import re
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT ma_tu FROM tu WHERE ma_tu_sinh = ?", (khoa_tu,))
    tu_row = con_tro.fetchone()
    ma_tu = tu_row["ma_tu"] if tu_row else "T01"

    con_tro.execute("SELECT ten_ngan, ma_ngan FROM ngan WHERE khoa_tu = ? ORDER BY ma_tu_sinh ASC", (khoa_tu,))
    rows = con_tro.fetchall()
    ket_noi.close()

    if not rows:
        return ("A01", f"{ma_tu}-A01")

    max_num = 0
    prefix = ""
    for r in rows:
        ten = r["ten_ngan"] or ""
        m = re.search(r"([A-Za-z]+)(\d+)", ten)
        if m:
            prefix = m.group(1)
            val = int(m.group(2))
            if val > max_num:
                max_num = val
    if not prefix:
        prefix = "N"
    next_num = max_num + 1 if max_num > 0 else len(rows) + 1
    ten_ngan_goi_y = f"{prefix}{next_num:02d}"
    ma_ngan_goi_y = f"{ma_tu}-{ten_ngan_goi_y}"
    return (ten_ngan_goi_y, ma_ngan_goi_y)

def them_ngan(khoa_tu, ten_ngan=None, ma_ngan=None, so_luong=1):
    import re
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT ma_tu FROM tu WHERE ma_tu_sinh = ?", (khoa_tu,))
    tu_row = con_tro.fetchone()
    if not tu_row:
        ket_noi.close()
        raise ValueError("Tủ bảo quản không tồn tại.")
    ma_tu = tu_row["ma_tu"]

    so_luong = int(so_luong) if so_luong else 1
    if so_luong < 1:
        so_luong = 1
    if so_luong > 50:
        so_luong = 50

    ids = []
    current_ten = (ten_ngan or "").strip()
    prefix = ""
    start_num = 1
    if current_ten:
        m = re.search(r"([A-Za-z]+)(\d+)", current_ten)
        if m:
            prefix = m.group(1).upper()
            start_num = int(m.group(2))
        else:
            prefix = current_ten.upper()
            start_num = 1
    else:
        goi_y_ten, _ = lay_goi_y_ngan_tiep_theo(khoa_tu)
        m = re.search(r"([A-Za-z]+)(\d+)", goi_y_ten)
        if m:
            prefix = m.group(1)
            start_num = int(m.group(2))
        else:
            prefix = "N"
            start_num = 1

    for offset in range(so_luong):
        num = start_num + offset
        cur_ten = f"{prefix}{num:02d}" if len(prefix) > 0 else f"{num:02d}"
        cur_ma = f"{ma_tu}-{cur_ten}"

        con_tro.execute("SELECT ma_tu_sinh FROM ngan WHERE ma_ngan = ?", (cur_ma,))
        existing = con_tro.fetchone()
        if existing:
            con_tro.execute("SELECT COUNT(*) as cnt FROM ngan WHERE ma_ngan LIKE ?", (f"{cur_ma}%",))
            dup_cnt = con_tro.fetchone()["cnt"]
            cur_ma = f"{cur_ma}-{dup_cnt + 1}"
            cur_ten = f"{cur_ten}-{dup_cnt + 1}"

        con_tro.execute("""
            INSERT INTO ngan (ma_ngan, ten_ngan, khoa_tu, khoa_quan_nhan, dang_dung)
            VALUES (?, ?, ?, NULL, 1)
        """, (cur_ma, cur_ten, khoa_tu))
        ids.append(con_tro.lastrowid)

    con_tro.execute("""
        UPDATE tu
        SET so_ngan = (SELECT COUNT(*) FROM ngan WHERE khoa_tu = ?)
        WHERE ma_tu_sinh = ?
    """, (khoa_tu, khoa_tu))

    ket_noi.commit()
    ket_noi.close()
    return ids
