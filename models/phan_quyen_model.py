import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from models.co_so_du_lieu import lay_ket_noi

BAC_VAI_TRO = {
    "QUAN_TRI": 100,
    "CHI_HUY": 80,
    "NGUOI_TRUC": 50,
    "QUAN_NHAN": 10
}

def lay_bac_vai_tro(ma_vai_tro):
    return BAC_VAI_TRO.get(ma_vai_tro, 10)

def ma_hoa_mat_khau(mat_khau):
    return generate_password_hash(mat_khau)

def la_hash_cu(hash_chuoi):
    if not hash_chuoi:
        return False
    if len(hash_chuoi) == 64 and all(c in "0123456789abcdefABCDEF" for c in hash_chuoi):
        return True
    return False

def xac_thuc_mat_khau(mat_khau_nhap, mat_khau_db):
    if not mat_khau_db or not mat_khau_nhap:
        return False
    if la_hash_cu(mat_khau_db):
        return hashlib.sha256(mat_khau_nhap.encode("utf-8")).hexdigest().lower() == mat_khau_db.lower()
    try:
        return check_password_hash(mat_khau_db, mat_khau_nhap)
    except Exception:
        return False

def xac_thuc_dang_nhap(ten_dang_nhap, mat_khau):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()

    con_tro.execute("""
        SELECT tk.ma_tu_sinh, tk.ten_dang_nhap, tk.mat_khau_ma_hoa, tk.ho_ten, tk.khoa_quan_nhan,
               COALESCE(tkv.pham_vi_khoa, qn.khoa_don_vi) AS khoa_don_vi,
               vt.ma_tu_sinh AS khoa_vai_tro, vt.ma_vai_tro, vt.ten_vai_tro,
               tkv.pham_vi_loai,
               COALESCE(tkv.pham_vi_khoa, qn.khoa_don_vi) AS pham_vi_khoa
        FROM tai_khoan tk
        LEFT JOIN quan_nhan qn ON tk.khoa_quan_nhan = qn.ma_tu_sinh
        LEFT JOIN tai_khoan_vai_tro tkv ON tkv.khoa_tai_khoan = tk.ma_tu_sinh AND tkv.dang_dung = 1
        LEFT JOIN vai_tro vt ON tkv.khoa_vai_tro = vt.ma_tu_sinh
        WHERE tk.ten_dang_nhap = ? AND tk.dang_dung = 1
        ORDER BY tkv.ma_tu_sinh ASC LIMIT 1
    """, (ten_dang_nhap,))

    tai_khoan = con_tro.fetchone()
    if not tai_khoan:
        ket_noi.close()
        return None

    mk_db = tai_khoan["mat_khau_ma_hoa"]
    if not xac_thuc_mat_khau(mat_khau, mk_db):
        ket_noi.close()
        return None

    ket_qua = dict(tai_khoan)
    ket_qua.pop("mat_khau_ma_hoa", None)

    if la_hash_cu(mk_db):
        mk_moi = ma_hoa_mat_khau(mat_khau)
        con_tro.execute("""
            UPDATE tai_khoan
            SET mat_khau_ma_hoa = ?
            WHERE ma_tu_sinh = ?
        """, (mk_moi, ket_qua["ma_tu_sinh"]))

    con_tro.execute("""
        UPDATE tai_khoan
        SET dang_nhap_cuoi = datetime('now', 'localtime')
        WHERE ma_tu_sinh = ?
    """, (ket_qua["ma_tu_sinh"],))
    ket_noi.commit()

    con_tro.execute("""
        SELECT DISTINCT qh.ma_quyen
        FROM tai_khoan_vai_tro tkv
        JOIN vai_tro_quyen vq ON tkv.khoa_vai_tro = vq.khoa_vai_tro
        JOIN quyen_han qh ON vq.khoa_quyen = qh.ma_tu_sinh
        WHERE tkv.khoa_tai_khoan = ? AND tkv.dang_dung = 1
    """, (ket_qua["ma_tu_sinh"],))

    cac_quyen = [row[0] for row in con_tro.fetchall()]
    ket_qua["cac_quyen"] = cac_quyen
    ket_qua["danh_sach_quyen"] = cac_quyen
    ket_noi.close()
    return ket_qua

def lay_tat_ca_tai_khoan(bac_nguoi_xem=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        SELECT tk.ma_tu_sinh, tk.ten_dang_nhap, tk.ho_ten, tk.dang_dung, tk.dang_nhap_cuoi,
               vt.ma_tu_sinh AS khoa_vai_tro, vt.ten_vai_tro, vt.ma_vai_tro,
               tkv.pham_vi_loai,
               COALESCE(tkv.pham_vi_khoa, qn.khoa_don_vi) AS pham_vi_khoa,
               COALESCE(dv.ten_don_vi, dv_qn.ten_don_vi) AS ten_don_vi_pham_vi,
               t.ten_tu AS ten_tu_pham_vi
        FROM tai_khoan tk
        LEFT JOIN quan_nhan qn ON tk.khoa_quan_nhan = qn.ma_tu_sinh
        LEFT JOIN don_vi dv_qn ON qn.khoa_don_vi = dv_qn.ma_tu_sinh
        LEFT JOIN tai_khoan_vai_tro tkv ON tkv.khoa_tai_khoan = tk.ma_tu_sinh AND tkv.dang_dung = 1
        LEFT JOIN vai_tro vt ON tkv.khoa_vai_tro = vt.ma_tu_sinh
        LEFT JOIN don_vi dv ON (tkv.pham_vi_loai = 'DON_VI' AND tkv.pham_vi_khoa = dv.ma_tu_sinh)
        LEFT JOIN tu t ON (tkv.pham_vi_loai = 'TU' AND tkv.pham_vi_khoa = t.ma_tu_sinh)
        GROUP BY tk.ma_tu_sinh
        ORDER BY tk.ma_tu_sinh ASC
    """)
    danh_sach = [dict(row) for row in con_tro.fetchall()]
    con_tro.execute("SELECT ma_tu_sinh, ten_don_vi FROM don_vi")
    ban_do_don_vi = {row["ma_tu_sinh"]: row["ten_don_vi"] for row in con_tro.fetchall()}
    for tk in danh_sach:
        if tk.get("pham_vi_loai") == "DON_VI" and tk.get("pham_vi_khoa"):
            pv_raw = str(tk["pham_vi_khoa"]).strip()
            if "," in pv_raw:
                ds_id = [int(x.strip()) for x in pv_raw.split(",") if x.strip().isdigit()]
                ten_ds = [ban_do_don_vi.get(i) for i in ds_id if ban_do_don_vi.get(i)]
                if ten_ds:
                    tk["ten_don_vi_pham_vi"] = ", ".join(ten_ds)
            elif pv_raw.isdigit():
                i = int(pv_raw)
                if ban_do_don_vi.get(i):
                    tk["ten_don_vi_pham_vi"] = ban_do_don_vi.get(i)
    ket_noi.close()
    if bac_nguoi_xem is None:
        return danh_sach
    return [tk for tk in danh_sach if BAC_VAI_TRO.get(tk.get("ma_vai_tro"), 10) <= bac_nguoi_xem]

def lay_chi_tiet_tai_khoan(ma_tu_sinh):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        SELECT tk.ma_tu_sinh, tk.ten_dang_nhap, tk.ho_ten, tk.dang_dung,
               tkv.khoa_vai_tro, vt.ma_vai_tro, vt.ten_vai_tro,
               tkv.pham_vi_loai,
               COALESCE(tkv.pham_vi_khoa, qn.khoa_don_vi) AS pham_vi_khoa
        FROM tai_khoan tk
        LEFT JOIN quan_nhan qn ON tk.khoa_quan_nhan = qn.ma_tu_sinh
        LEFT JOIN tai_khoan_vai_tro tkv ON tkv.khoa_tai_khoan = tk.ma_tu_sinh AND tkv.dang_dung = 1
        LEFT JOIN vai_tro vt ON tkv.khoa_vai_tro = vt.ma_tu_sinh
        WHERE tk.ma_tu_sinh = ?
    """, (ma_tu_sinh,))
    row = con_tro.fetchone()
    ket_qua = dict(row) if row else None
    ket_noi.close()
    return ket_qua

def lay_danh_sach_vai_tro():
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT * FROM vai_tro WHERE dang_dung = 1 ORDER BY ma_tu_sinh ASC")
    vai_tro_list = [dict(row) for row in con_tro.fetchall()]

    for vt in vai_tro_list:
        con_tro.execute("""
            SELECT qh.ma_tu_sinh, qh.ten_quyen, qh.ma_quyen, qh.nhom
            FROM vai_tro_quyen vq
            JOIN quyen_han qh ON vq.khoa_quyen = qh.ma_tu_sinh
            WHERE vq.khoa_vai_tro = ?
        """, (vt["ma_tu_sinh"],))
        vt["cac_quyen"] = [dict(r) for r in con_tro.fetchall()]
        vt["ds_ma_quyen"] = [r["ma_quyen"] for r in vt["cac_quyen"]]
        vt["cac_quyen_ids"] = [r["ma_tu_sinh"] for r in vt["cac_quyen"]]

    ket_noi.close()
    return vai_tro_list

def lay_danh_sach_quyen():
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT * FROM quyen_han ORDER BY nhom ASC, ma_tu_sinh ASC")
    ket_qua = [dict(row) for row in con_tro.fetchall()]
    ket_noi.close()
    return ket_qua

def them_tai_khoan(ten_dang_nhap, mat_khau, ho_ten, khoa_vai_tro, khoa_quan_nhan=None, pham_vi_loai="TOAN_BO", pham_vi_khoa=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    mk_ma_hoa = ma_hoa_mat_khau(mat_khau)

    con_tro.execute("""
        INSERT INTO tai_khoan (ten_dang_nhap, mat_khau_ma_hoa, ho_ten, khoa_quan_nhan)
        VALUES (?, ?, ?, ?)
    """, (ten_dang_nhap, mk_ma_hoa, ho_ten, khoa_quan_nhan))
    tk_id = con_tro.lastrowid

    con_tro.execute("""
        INSERT INTO tai_khoan_vai_tro (khoa_tai_khoan, khoa_vai_tro, pham_vi_loai, pham_vi_khoa, hieu_luc_tu)
        VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
    """, (tk_id, khoa_vai_tro, pham_vi_loai, pham_vi_khoa))

    ket_noi.commit()
    ket_noi.close()
    return tk_id

def sua_tai_khoan(ma_tu_sinh, ho_ten, mat_khau_moi=None, khoa_vai_tro=None, pham_vi_loai="TOAN_BO", dang_dung=1, nguoi_thuc_hien=None, pham_vi_khoa=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()

    con_tro.execute("SELECT ma_tu_sinh, ten_dang_nhap FROM tai_khoan WHERE ma_tu_sinh = ?", (ma_tu_sinh,))
    tk_target = con_tro.fetchone()
    if not tk_target:
        ket_noi.close()
        raise ValueError("Tài khoản không tồn tại.")

    is_admin = (tk_target["ten_dang_nhap"] == "admin") or (ma_tu_sinh == 1)
    if is_admin:
        if nguoi_thuc_hien != "admin":
            ket_noi.close()
            raise PermissionError("Chỉ có tài khoản admin mới có quyền chỉnh sửa tài khoản admin.")
        dang_dung = 1

    if mat_khau_moi and mat_khau_moi.strip():
        mk_ma_hoa = ma_hoa_mat_khau(mat_khau_moi.strip())
        con_tro.execute("""
            UPDATE tai_khoan
            SET ho_ten = ?, mat_khau_ma_hoa = ?, dang_dung = ?
            WHERE ma_tu_sinh = ?
        """, (ho_ten, mk_ma_hoa, dang_dung, ma_tu_sinh))
    else:
        con_tro.execute("""
            UPDATE tai_khoan
            SET ho_ten = ?, dang_dung = ?
            WHERE ma_tu_sinh = ?
        """, (ho_ten, dang_dung, ma_tu_sinh))

    if khoa_vai_tro:
        if is_admin:
            con_tro.execute("""
                SELECT ma_tu_sinh FROM vai_tro WHERE ma_vai_tro = 'QUAN_TRI'
            """)
            admin_vt = con_tro.fetchone()
            if admin_vt:
                khoa_vai_tro = admin_vt["ma_tu_sinh"]

        con_tro.execute("""
            UPDATE tai_khoan_vai_tro
            SET khoa_vai_tro = ?, pham_vi_loai = ?, pham_vi_khoa = ?
            WHERE khoa_tai_khoan = ?
        """, (khoa_vai_tro, pham_vi_loai, pham_vi_khoa, ma_tu_sinh))
        if con_tro.rowcount == 0:
            con_tro.execute("""
                INSERT INTO tai_khoan_vai_tro (khoa_tai_khoan, khoa_vai_tro, pham_vi_loai, pham_vi_khoa, hieu_luc_tu)
                VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
            """, (ma_tu_sinh, khoa_vai_tro, pham_vi_loai, pham_vi_khoa))

    ket_noi.commit()
    ket_noi.close()

def xoa_tai_khoan(ma_tu_sinh):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT ten_dang_nhap FROM tai_khoan WHERE ma_tu_sinh = ?", (ma_tu_sinh,))
    tk = con_tro.fetchone()
    if not tk:
        ket_noi.close()
        return False

    if tk["ten_dang_nhap"] == "admin" or ma_tu_sinh == 1:
        ket_noi.close()
        raise PermissionError("Tuyệt đối không được phép xóa tài khoản quản trị tối cao (admin).")

    con_tro.execute("DELETE FROM tai_khoan_vai_tro WHERE khoa_tai_khoan = ?", (ma_tu_sinh,))
    con_tro.execute("DELETE FROM nhat_ky WHERE khoa_tai_khoan = ?", (ma_tu_sinh,))
    con_tro.execute("DELETE FROM tai_khoan WHERE ma_tu_sinh = ?", (ma_tu_sinh,))
    ket_noi.commit()
    ket_noi.close()
    return True

def cap_nhat_quyen_vai_tro(khoa_vai_tro, danh_sach_khoa_quyen):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("DELETE FROM vai_tro_quyen WHERE khoa_vai_tro = ?", (khoa_vai_tro,))
    for kq in danh_sach_khoa_quyen:
        con_tro.execute("INSERT INTO vai_tro_quyen (khoa_vai_tro, khoa_quyen) VALUES (?, ?)", (khoa_vai_tro, kq))
    ket_noi.commit()
    ket_noi.close()

