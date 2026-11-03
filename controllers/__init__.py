from functools import wraps
from flask import session, redirect, url_for, flash, request

def yeu_cau_dang_nhap(f):
    @wraps(f)
    def ham_trang_tri(*args, **kwargs):
        if "nguoi_dung" not in session:
            flash("Vui lòng đăng nhập để tiếp tục.", "canh_bao")
            return redirect(url_for("auth.dang_nhap"))
        return f(*args, **kwargs)
    return ham_trang_tri

def yeu_cau_quyen(*quyen_hop_le):
    def decorator(f):
        @wraps(f)
        def ham_trang_tri(*args, **kwargs):
            if "nguoi_dung" not in session:
                flash("Vui lòng đăng nhập để tiếp tục.", "canh_bao")
                return redirect(url_for("auth.dang_nhap"))

            nguoi_dung = session.get("nguoi_dung", {})
            danh_sach_quyen = nguoi_dung.get("danh_sach_quyen") or nguoi_dung.get("cac_quyen") or []
            ma_vai_tro = nguoi_dung.get("ma_vai_tro")
            ten_dang_nhap = nguoi_dung.get("ten_dang_nhap")

            la_admin = (ten_dang_nhap == "admin") or (ma_vai_tro == "QUAN_TRI")
            co_quyen = la_admin or (ma_vai_tro in quyen_hop_le) or any(q in danh_sach_quyen for q in quyen_hop_le)

            if not co_quyen and ma_vai_tro in ["CHI_HUY", "CAN_BO"]:
                if any(".XEM" in str(q) or q in ["GIAONHAN.XEM", "QUANNHAN.XEM", "DIENTHOAI.XEM", "BAOCAO.XEM", "CATRUC.BANGIAO"] for q in quyen_hop_le):
                    co_quyen = True

            if not co_quyen and not danh_sach_quyen and ma_vai_tro:
                from models.co_so_du_lieu import lay_ket_noi
                try:
                    ket_noi = lay_ket_noi()
                    con_tro = ket_noi.cursor()
                    con_tro.execute("""
                        SELECT qh.ma_quyen
                        FROM quyen_han qh
                        JOIN vai_tro_quyen vtq ON qh.ma_tu_sinh = vtq.khoa_quyen
                        JOIN vai_tro vt ON vt.ma_tu_sinh = vtq.khoa_vai_tro
                        WHERE vt.ma_vai_tro = ?
                    """, (ma_vai_tro,))
                    db_quyen = [r[0] for r in con_tro.fetchall()]
                    ket_noi.close()
                    co_quyen = any(q in db_quyen for q in quyen_hop_le)
                except Exception:
                    pass

            if not co_quyen:
                if request.path.startswith("/api/") or request.is_json:
                    return {"hop_le": False, "thong_bao": "Đồng chí không có thẩm quyền truy cập nội dung này."}, 403
                flash("Đồng chí không có thẩm quyền truy cập nội dung này.", "nguy_hiem")
                return redirect(url_for("dashboard.tong_quan"))

            return f(*args, **kwargs)
        return ham_trang_tri
    return decorator

from models.co_so_du_lieu import kiem_tra_thuoc_don_vi

def lay_don_vi_gioi_han():
    nguoi_dung = session.get("nguoi_dung")
    if not nguoi_dung:
        return None
    ten_dang_nhap = nguoi_dung.get("ten_dang_nhap")
    ma_vai_tro = nguoi_dung.get("ma_vai_tro")
    if ten_dang_nhap == "admin" or ma_vai_tro == "QUAN_TRI":
        return None
    if nguoi_dung.get("pham_vi_loai") == "DON_VI":
        pv_khoa = nguoi_dung.get("khoa_don_vi") or nguoi_dung.get("pham_vi_khoa")
        if not pv_khoa:
            return None
        if isinstance(pv_khoa, str) and "," in pv_khoa:
            return [int(x.strip()) for x in pv_khoa.split(",") if x.strip().isdigit()]
        if isinstance(pv_khoa, (list, tuple, set)):
            return [int(x) for x in pv_khoa if str(x).isdigit()]
        try:
            return int(pv_khoa)
        except (ValueError, TypeError):
            return None
    if nguoi_dung.get("pham_vi_loai") == "TU":
        pv_khoa = nguoi_dung.get("pham_vi_khoa")
        if pv_khoa:
            try:
                tu_id = int(pv_khoa)
                from models.co_so_du_lieu import lay_ket_noi
                ket_noi = lay_ket_noi()
                con_tro = ket_noi.cursor()
                con_tro.execute("SELECT khoa_don_vi_quan_ly FROM tu WHERE ma_tu_sinh = ?", (tu_id,))
                row = con_tro.fetchone()
                ket_noi.close()
                if row and row["khoa_don_vi_quan_ly"]:
                    return int(row["khoa_don_vi_quan_ly"])
            except Exception:
                pass
        return -1
    return None

def lay_tu_gioi_han():
    nguoi_dung = session.get("nguoi_dung")
    if not nguoi_dung:
        return None
    ten_dang_nhap = nguoi_dung.get("ten_dang_nhap")
    ma_vai_tro = nguoi_dung.get("ma_vai_tro")
    if ten_dang_nhap == "admin" or ma_vai_tro == "QUAN_TRI":
        return None
    if nguoi_dung.get("pham_vi_loai") == "TU":
        pv_khoa = nguoi_dung.get("pham_vi_khoa")
        if pv_khoa:
            try:
                return int(pv_khoa)
            except (ValueError, TypeError):
                return -1
        return -1
    return None
