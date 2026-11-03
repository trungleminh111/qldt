import re
import openpyxl
from models.co_so_du_lieu import lay_ket_noi, tao_dieu_kien_don_vi, kiem_tra_thuoc_don_vi

def lay_danh_sach_don_vi(khoa_don_vi_gioi_han=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    cau_lenh = "SELECT ma_tu_sinh, ma_don_vi, ten_don_vi, khoa_don_vi_cha FROM don_vi WHERE dang_dung = 1"
    dieu_kien, tham_so = tao_dieu_kien_don_vi("ma_tu_sinh", khoa_don_vi_gioi_han)
    cau_lenh += dieu_kien + " ORDER BY thu_tu ASC, ma_tu_sinh ASC"
    con_tro.execute(cau_lenh, tham_so)
    ket_qua = [dict(row) for row in con_tro.fetchall()]
    ket_noi.close()
    return ket_qua

def lay_danh_sach_cap_bac():
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT ma_tu_sinh, ma_cap_bac, ten_cap_bac FROM cap_bac WHERE dang_dung = 1 ORDER BY thu_tu ASC")
    ket_qua = [dict(row) for row in con_tro.fetchall()]
    ket_noi.close()
    return ket_qua

def lay_danh_sach_chuc_vu():
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        SELECT cv.ma_tu_sinh, cv.ma_chuc_vu, cv.ten_chuc_vu, cv.khoa_cau_hinh_gio, ch.ten_cau_hinh
        FROM chuc_vu cv
        LEFT JOIN cau_hinh_gio ch ON cv.khoa_cau_hinh_gio = ch.ma_tu_sinh
        WHERE cv.dang_dung = 1
        ORDER BY cv.thu_tu ASC
    """)
    ket_qua = [dict(row) for row in con_tro.fetchall()]
    ket_noi.close()
    return ket_qua

def lay_tat_ca_quan_nhan(tu_khoa=None, ma_don_vi=None, trang_thai=None, khoa_don_vi_gioi_han=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()

    cau_lenh = """
        SELECT qn.ma_tu_sinh, qn.ma_quan_nhan, qn.ho_ten, qn.ngay_sinh, qn.ngay_nhap_ngu, qn.khoa_don_vi,
               cb.ten_cap_bac, cv.ten_chuc_vu, dv.ten_don_vi, dv.ma_don_vi,
               ch.ten_cau_hinh AS nhom_doi_tuong,
               dt.ma_thiet_bi, dt.ten_dien_thoai, dt.hang_san_xuat, dt.model,
               ng.ma_ngan, ng.ten_ngan, t.ma_tu, t.ten_tu,
               CASE
                   WHEN gn.loai = 'LAY_RA' THEN 'Đã lấy'
                   WHEN gn.loai = 'NOP_VAO' THEN 'Đã nộp'
                   WHEN dt.ma_tu_sinh IS NOT NULL THEN 'Trong tủ'
                   ELSE 'Chưa có thiết bị'
               END AS trang_thai_may,
               gn.thoi_gian AS thoi_gian_giao_dich_cuoi
        FROM quan_nhan qn
        JOIN cap_bac cb ON qn.khoa_cap_bac = cb.ma_tu_sinh
        JOIN chuc_vu cv ON qn.khoa_chuc_vu = cv.ma_tu_sinh
        LEFT JOIN cau_hinh_gio ch ON cv.khoa_cau_hinh_gio = ch.ma_tu_sinh
        JOIN don_vi dv ON qn.khoa_don_vi = dv.ma_tu_sinh
        LEFT JOIN dien_thoai dt ON dt.khoa_quan_nhan = qn.ma_tu_sinh AND dt.da_xoa = 0
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
        WHERE qn.da_xoa = 0
    """
    tham_so = []

    if tu_khoa:
        cau_lenh += " AND (qn.ma_quan_nhan LIKE ? OR qn.ho_ten LIKE ? OR dt.ma_thiet_bi LIKE ?)"
        tk = f"%{tu_khoa}%"
        tham_so.extend([tk, tk, tk])

    if khoa_don_vi_gioi_han:
        dieu_kien_dv, tham_so_dv = tao_dieu_kien_don_vi("qn.khoa_don_vi", khoa_don_vi_gioi_han)
        cau_lenh += dieu_kien_dv
        tham_so.extend(tham_so_dv)
    elif ma_don_vi and ma_don_vi != "TAT_CA":
        cau_lenh += " AND (dv.ma_don_vi = ? OR dv.ma_tu_sinh = ?)"
        tham_so.extend([ma_don_vi, ma_don_vi])

    cau_lenh += " ORDER BY qn.ma_tu_sinh ASC"
    con_tro.execute(cau_lenh, tham_so)
    ket_qua = [dict(row) for row in con_tro.fetchall()]
    ket_noi.close()
    return ket_qua

def lay_chi_tiet_quan_nhan(ma_tu_sinh, khoa_don_vi_gioi_han=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    cau_lenh = """
        SELECT qn.*, cb.ten_cap_bac, cv.ten_chuc_vu, dv.ten_don_vi, ch.ten_cau_hinh AS nhom_doi_tuong,
               dt.ma_tu_sinh AS dt_id, dt.ma_thiet_bi, dt.ten_dien_thoai, dt.hang_san_xuat, dt.model, dt.so_imei,
               ng.ma_ngan, ng.ten_ngan, t.ten_tu, t.ma_tu,
               CASE
                   WHEN gn.loai = 'LAY_RA' THEN 'Đã lấy'
                   WHEN gn.loai = 'NOP_VAO' THEN 'Đã nộp'
                   WHEN dt.ma_tu_sinh IS NOT NULL THEN 'Trong tủ'
                   ELSE 'Chưa có thiết bị'
               END AS trang_thai_may
        FROM quan_nhan qn
        JOIN cap_bac cb ON qn.khoa_cap_bac = cb.ma_tu_sinh
        JOIN chuc_vu cv ON qn.khoa_chuc_vu = cv.ma_tu_sinh
        LEFT JOIN cau_hinh_gio ch ON cv.khoa_cau_hinh_gio = ch.ma_tu_sinh
        JOIN don_vi dv ON qn.khoa_don_vi = dv.ma_tu_sinh
        LEFT JOIN dien_thoai dt ON dt.khoa_quan_nhan = qn.ma_tu_sinh AND dt.da_xoa = 0
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
        WHERE (qn.ma_tu_sinh = ? OR qn.ma_quan_nhan = ?) AND qn.da_xoa = 0
    """
    tham_so = [ma_tu_sinh, ma_tu_sinh]
    if khoa_don_vi_gioi_han:
        dieu_kien_dv, tham_so_dv = tao_dieu_kien_don_vi("qn.khoa_don_vi", khoa_don_vi_gioi_han)
        cau_lenh += dieu_kien_dv
        tham_so.extend(tham_so_dv)
    con_tro.execute(cau_lenh, tham_so)
    dong = con_tro.fetchone()
    ket_qua = dict(dong) if dong else None
    ket_noi.close()
    return ket_qua

def them_quan_nhan(ma_quan_nhan, ho_ten, khoa_cap_bac, khoa_chuc_vu, khoa_don_vi, ngay_sinh=None, ngay_nhap_ngu=None, ghi_chu=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        INSERT INTO quan_nhan (ma_quan_nhan, ho_ten, khoa_cap_bac, khoa_chuc_vu, khoa_don_vi, ngay_sinh, ngay_nhap_ngu, ghi_chu)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (ma_quan_nhan, ho_ten, khoa_cap_bac, khoa_chuc_vu, khoa_don_vi, ngay_sinh, ngay_nhap_ngu, ghi_chu))
    id_moi = con_tro.lastrowid
    ket_noi.commit()
    ket_noi.close()
    return id_moi

def sua_quan_nhan(ma_tu_sinh, ho_ten, khoa_cap_bac, khoa_chuc_vu, khoa_don_vi, ngay_sinh=None, ngay_nhap_ngu=None, ghi_chu=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT khoa_don_vi FROM quan_nhan WHERE ma_tu_sinh = ?", (ma_tu_sinh,))
    old_row = con_tro.fetchone()
    if old_row and str(old_row["khoa_don_vi"]) != str(khoa_don_vi):
        con_tro.execute("""
            UPDATE ngan
            SET khoa_quan_nhan = NULL
            WHERE khoa_quan_nhan = ?
              AND khoa_tu IN (
                  SELECT ma_tu_sinh FROM tu WHERE khoa_don_vi_quan_ly != ?
              )
        """, (ma_tu_sinh, khoa_don_vi))
    con_tro.execute("""
        UPDATE quan_nhan
        SET ho_ten = ?, khoa_cap_bac = ?, khoa_chuc_vu = ?, khoa_don_vi = ?, ngay_sinh = ?, ngay_nhap_ngu = ?, ghi_chu = ?, ngay_sua = datetime('now', 'localtime')
        WHERE ma_tu_sinh = ?
    """, (ho_ten, khoa_cap_bac, khoa_chuc_vu, khoa_don_vi, ngay_sinh, ngay_nhap_ngu, ghi_chu, ma_tu_sinh))
    ket_noi.commit()
    ket_noi.close()

def xoa_quan_nhan(ma_tu_sinh):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        SELECT COUNT(dt.ma_tu_sinh) AS dang_giu
        FROM dien_thoai dt
        JOIN (
            SELECT gn1.khoa_dien_thoai, gn1.loai
            FROM lich_su_giao_nhan gn1
            INNER JOIN (
                SELECT khoa_dien_thoai, MAX(ma_tu_sinh) AS max_id
                FROM lich_su_giao_nhan
                GROUP BY khoa_dien_thoai
            ) gn2 ON gn1.ma_tu_sinh = gn2.max_id
        ) gn ON gn.khoa_dien_thoai = dt.ma_tu_sinh
        WHERE dt.khoa_quan_nhan = ? AND dt.da_xoa = 0 AND gn.loai = 'LAY_RA'
    """, (ma_tu_sinh,))
    row = con_tro.fetchone()
    if row and row["dang_giu"] > 0:
        ket_noi.close()
        raise ValueError("Quân nhân đang giữ thiết bị ngoài tủ. Vui lòng thu hồi thiết bị trước khi xóa hồ sơ.")

    con_tro.execute("UPDATE quan_nhan SET da_xoa = 1 WHERE ma_tu_sinh = ?", (ma_tu_sinh,))
    con_tro.execute("UPDATE ngan SET khoa_quan_nhan = NULL WHERE khoa_quan_nhan = ?", (ma_tu_sinh,))
    con_tro.execute("UPDATE dien_thoai SET da_xoa = 1 WHERE khoa_quan_nhan = ?", (ma_tu_sinh,))
    con_tro.execute("UPDATE tai_khoan SET dang_dung = 0 WHERE khoa_quan_nhan = ?", (ma_tu_sinh,))
    ket_noi.commit()
    ket_noi.close()

def import_quan_nhan_excel(file_path, khoa_don_vi_gioi_han=None):
    wb = openpyxl.load_workbook(file_path)
    sheet = wb.active
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()

    con_tro.execute("SELECT ma_tu_sinh, ten_cap_bac, ma_cap_bac FROM cap_bac")
    cap_bac_dict = {row[1].lower(): row[0] for row in con_tro.fetchall()}
    con_tro.execute("SELECT ma_tu_sinh, ten_chuc_vu, ma_chuc_vu FROM chuc_vu")
    chuc_vu_dict = {row[1].lower(): row[0] for row in con_tro.fetchall()}
    con_tro.execute("SELECT ma_tu_sinh, ten_don_vi, ma_don_vi FROM don_vi")
    don_vi_dict = {row[1].lower(): row[0] for row in con_tro.fetchall()}

    so_dong_thanh_cong = 0
    hang_bat_dau = 2
    for r in range(hang_bat_dau, sheet.max_row + 1):
        ma_qn = sheet.cell(row=r, column=1).value
        ho_ten = sheet.cell(row=r, column=2).value
        ten_cb = str(sheet.cell(row=r, column=3).value or "").strip().lower()
        ten_cv = str(sheet.cell(row=r, column=4).value or "").strip().lower()
        ten_dv = str(sheet.cell(row=r, column=5).value or "").strip().lower()

        if not ma_qn or not ho_ten:
            continue

        ma_qn = str(ma_qn).strip()
        ho_ten = str(ho_ten).strip()

        k_cb = cap_bac_dict.get(ten_cb, list(cap_bac_dict.values())[0])
        k_cv = chuc_vu_dict.get(ten_cv, list(chuc_vu_dict.values())[0])
        k_dv = don_vi_dict.get(ten_dv, list(don_vi_dict.values())[0])

        if khoa_don_vi_gioi_han and not kiem_tra_thuoc_don_vi(k_dv, khoa_don_vi_gioi_han):
            continue

        con_tro.execute("SELECT ma_tu_sinh FROM quan_nhan WHERE ma_quan_nhan = ?", (ma_qn,))
        ton_tai = con_tro.fetchone()
        if ton_tai:
            con_tro.execute("""
                UPDATE quan_nhan
                SET ho_ten = ?, khoa_cap_bac = ?, khoa_chuc_vu = ?, khoa_don_vi = ?, da_xoa = 0
                WHERE ma_tu_sinh = ?
            """, (ho_ten, k_cb, k_cv, k_dv, ton_tai[0]))
        else:
            con_tro.execute("""
                INSERT INTO quan_nhan (ma_quan_nhan, ho_ten, khoa_cap_bac, khoa_chuc_vu, khoa_don_vi)
                VALUES (?, ?, ?, ?, ?)
            """, (ma_qn, ho_ten, k_cb, k_cv, k_dv))
        so_dong_thanh_cong += 1

    ket_noi.commit()
    ket_noi.close()
    return so_dong_thanh_cong

def lay_tat_ca_don_vi():
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        SELECT dv.ma_tu_sinh, dv.ma_don_vi, dv.ten_don_vi, dv.khoa_don_vi_cha, dv.thu_tu, dv.dang_dung,
               cha.ten_don_vi AS ten_don_vi_cha,
               COUNT(DISTINCT qn.ma_tu_sinh) AS so_quan_nhan,
               COUNT(DISTINCT t.ma_tu_sinh) AS so_tu
        FROM don_vi dv
        LEFT JOIN don_vi cha ON dv.khoa_don_vi_cha = cha.ma_tu_sinh
        LEFT JOIN quan_nhan qn ON qn.khoa_don_vi = dv.ma_tu_sinh AND qn.da_xoa = 0
        LEFT JOIN tu t ON t.khoa_don_vi_quan_ly = dv.ma_tu_sinh AND t.dang_dung = 1
        GROUP BY dv.ma_tu_sinh, dv.ma_don_vi, dv.ten_don_vi, dv.khoa_don_vi_cha, dv.thu_tu, dv.dang_dung, cha.ten_don_vi
        ORDER BY dv.thu_tu ASC, dv.ma_tu_sinh ASC
    """)
    ket_qua = [dict(row) for row in con_tro.fetchall()]
    ket_noi.close()
    return ket_qua

def lay_chi_tiet_don_vi(ma_tu_sinh):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        SELECT dv.ma_tu_sinh, dv.ma_don_vi, dv.ten_don_vi, dv.khoa_don_vi_cha, dv.thu_tu, dv.dang_dung
        FROM don_vi dv
        WHERE dv.ma_tu_sinh = ?
    """, (ma_tu_sinh,))
    row = con_tro.fetchone()
    ket_qua = dict(row) if row else None
    ket_noi.close()
    return ket_qua

def lay_goi_y_phan_doi_tiep_theo():
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT ma_don_vi, ten_don_vi FROM don_vi WHERE khoa_don_vi_cha IS NOT NULL")
    rows = con_tro.fetchall()
    ket_noi.close()
    max_num = 0
    for r in rows:
        m = re.search(r"(\d+)", r["ma_don_vi"] or "")
        if m:
            val = int(m.group(1))
            if val > max_num:
                max_num = val
    next_num = max_num + 1 if max_num > 0 else len(rows) + 1
    return {
        "ma_don_vi": f"TD{next_num}",
        "ten_don_vi": f"Trung đội {next_num}",
        "thu_tu": next_num
    }

def them_don_vi(ma_don_vi, ten_don_vi, khoa_don_vi_cha=1, thu_tu=None):
    ma_don_vi = (ma_don_vi or "").strip().upper()
    ten_don_vi = (ten_don_vi or "").strip()
    if not ma_don_vi or not ten_don_vi:
        raise ValueError("Vui lòng điền đầy đủ mã và tên phân đội.")

    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()

    con_tro.execute("SELECT ma_tu_sinh FROM don_vi WHERE ma_don_vi = ?", (ma_don_vi,))
    if con_tro.fetchone():
        ket_noi.close()
        raise ValueError(f"Mã phân đội '{ma_don_vi}' đã tồn tại trong hệ thống.")

    if thu_tu is None or str(thu_tu).strip() == "":
        con_tro.execute("SELECT MAX(thu_tu) as max_tt FROM don_vi WHERE khoa_don_vi_cha IS NOT NULL")
        max_tt = con_tro.fetchone()["max_tt"] or 0
        thu_tu = max_tt + 1
    else:
        thu_tu = int(thu_tu)

    con_tro.execute("""
        INSERT INTO don_vi (ma_don_vi, ten_don_vi, khoa_don_vi_cha, thu_tu, dang_dung)
        VALUES (?, ?, ?, ?, 1)
    """, (ma_don_vi, ten_don_vi, khoa_don_vi_cha, thu_tu))
    id_moi = con_tro.lastrowid
    ket_noi.commit()
    ket_noi.close()
    return id_moi

def sua_don_vi(ma_tu_sinh, ma_don_vi, ten_don_vi, thu_tu=None, dang_dung=1, khoa_don_vi_cha=None):
    ma_don_vi = (ma_don_vi or "").strip().upper()
    ten_don_vi = (ten_don_vi or "").strip()
    if not ma_don_vi or not ten_don_vi:
        raise ValueError("Vui lòng điền đầy đủ mã và tên phân đội.")

    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()

    con_tro.execute("SELECT ma_tu_sinh FROM don_vi WHERE ma_don_vi = ? AND ma_tu_sinh != ?", (ma_don_vi, ma_tu_sinh))
    if con_tro.fetchone():
        ket_noi.close()
        raise ValueError(f"Mã phân đội '{ma_don_vi}' đã được sử dụng bởi phân đội khác.")

    if thu_tu is None or str(thu_tu).strip() == "":
        thu_tu = 0
    else:
        thu_tu = int(thu_tu)

    cha_id = None
    if khoa_don_vi_cha is not None and str(khoa_don_vi_cha).strip() != "":
        try:
            val = int(khoa_don_vi_cha)
            if val != int(ma_tu_sinh):
                cha_id = val
        except (ValueError, TypeError):
            cha_id = None

    con_tro.execute("""
        UPDATE don_vi
        SET ma_don_vi = ?, ten_don_vi = ?, thu_tu = ?, dang_dung = ?, khoa_don_vi_cha = ?
        WHERE ma_tu_sinh = ?
    """, (ma_don_vi, ten_don_vi, thu_tu, dang_dung, cha_id, ma_tu_sinh))

    if cha_id is None:
        try:
            con_tro.execute("UPDATE thong_tin_don_vi SET gia_tri = ? WHERE khoa_thiet_lap = 'ten_don_vi'", (ten_don_vi,))
        except Exception:
            pass

    ket_noi.commit()
    ket_noi.close()
    return True

def xoa_don_vi(ma_tu_sinh):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT COUNT(*) as cnt FROM quan_nhan WHERE khoa_don_vi = ? AND da_xoa = 0", (ma_tu_sinh,))
    so_qn = con_tro.fetchone()["cnt"]
    if so_qn > 0:
        ket_noi.close()
        raise ValueError(f"Không thể xóa phân đội này vì đang có {so_qn} quân nhân trực thuộc. Vui lòng chuyển quân nhân sang phân đội khác trước.")

    con_tro.execute("SELECT COUNT(*) as cnt FROM tu WHERE khoa_don_vi_quan_ly = ? AND dang_dung = 1", (ma_tu_sinh,))
    so_tu = con_tro.fetchone()["cnt"]
    if so_tu > 0:
        ket_noi.close()
        raise ValueError(f"Không thể xóa phân đội này vì đang có {so_tu} tủ bảo quản phụ trách.")

    con_tro.execute("DELETE FROM don_vi WHERE ma_tu_sinh = ?", (ma_tu_sinh,))
    ket_noi.commit()
    ket_noi.close()
    return True
