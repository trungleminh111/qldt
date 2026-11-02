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
            co_quyen = la_admin or any(q in danh_sach_quyen for q in quyen_hop_le)

            if not co_quyen:
                if request.path.startswith("/api/") or request.is_json:
                    return {"hop_le": False, "thong_bao": "Đồng chí không có thẩm quyền truy cập nội dung này."}, 403
                flash("Đồng chí không có thẩm quyền truy cập nội dung này.", "nguy_hiem")
                return redirect(url_for("dashboard.tong_quan"))

            return f(*args, **kwargs)
        return ham_trang_tri
    return decorator

def lay_don_vi_gioi_han():
    nguoi_dung = session.get("nguoi_dung")
    if not nguoi_dung:
        return None
    if nguoi_dung.get("pham_vi_loai") == "DON_VI":
        return nguoi_dung.get("khoa_don_vi")
    return None

