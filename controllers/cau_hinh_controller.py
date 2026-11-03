from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from controllers import yeu_cau_dang_nhap, yeu_cau_quyen
from models.cau_hinh_model import (
    lay_tat_ca_cau_hinh_gio,
    lay_khung_gio_theo_cau_hinh,
    them_khung_gio,
    sua_khung_gio,
    xoa_khung_gio,
    them_cau_hinh_gio,
    lay_danh_sach_ngay_dac_biet,
    them_ngay_dac_biet,
    sua_ngay_dac_biet,
    xoa_ngay_dac_biet,
    lay_thong_tin_don_vi,
    cap_nhat_thong_tin_don_vi
)
from models.phan_quyen_model import (
    lay_tat_ca_tai_khoan,
    lay_chi_tiet_tai_khoan,
    lay_danh_sach_vai_tro,
    lay_danh_sach_quyen,
    them_tai_khoan,
    sua_tai_khoan,
    xoa_tai_khoan,
    cap_nhat_quyen_vai_tro,
    BAC_VAI_TRO
)
from models.quan_nhan_model import (
    lay_tat_ca_quan_nhan,
    lay_danh_sach_don_vi,
    lay_tat_ca_don_vi,
    lay_chi_tiet_don_vi,
    lay_goi_y_phan_doi_tiep_theo,
    them_don_vi,
    sua_don_vi,
    xoa_don_vi
)
from models.dien_thoai_model import lay_danh_sach_tu

cau_hinh_bp = Blueprint("cau_hinh", __name__)

@cau_hinh_bp.route("/khung-gio")
@cau_hinh_bp.route("/cau-hinh-gio")
@yeu_cau_quyen("CAUHINH.GIO")
def khung_gio():
    cau_hinh_list = lay_tat_ca_cau_hinh_gio()
    khung_gio_list = lay_khung_gio_theo_cau_hinh()
    ngay_dac_biet_list = lay_danh_sach_ngay_dac_biet()

    return render_template(
        "cau_hinh/khung_gio.html",
        cau_hinh_list=cau_hinh_list,
        khung_gio_list=khung_gio_list,
        ngay_dac_biet_list=ngay_dac_biet_list
    )

@cau_hinh_bp.route("/cau-hinh-gio/them", methods=["POST"])
@yeu_cau_quyen("CAUHINH.GIO")
def them_khung():
    khoa_ch = request.form.get("khoa_cau_hinh_gio")
    thu = int(request.form.get("thu_trong_tuan", 2))
    bat_dau = request.form.get("gio_bat_dau")
    ket_thuc = request.form.get("gio_ket_thuc")
    ghi_chu = request.form.get("ghi_chu", "")

    if not bat_dau or not ket_thuc or bat_dau >= ket_thuc:
        flash("Khung giờ không hợp lệ (Giờ bắt đầu phải nhỏ hơn giờ kết thúc).", "canh_bao")
        return redirect(url_for("cau_hinh.khung_gio"))

    try:
        them_khung_gio(khoa_ch, thu, bat_dau, ket_thuc, ghi_chu)
        flash("Đã thêm khung giờ mới thành công.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi thêm khung giờ: {str(e)}", "nguy_hiem")

    return redirect(url_for("cau_hinh.khung_gio"))

@cau_hinh_bp.route("/cau-hinh-gio/sua/<int:id>", methods=["POST"])
@yeu_cau_quyen("CAUHINH.GIO")
def sua_khung(id):
    khoa_ch = request.form.get("khoa_cau_hinh_gio")
    thu = int(request.form.get("thu_trong_tuan", 2))
    bat_dau = request.form.get("gio_bat_dau")
    ket_thuc = request.form.get("gio_ket_thuc")
    ghi_chu = request.form.get("ghi_chu", "")

    if not bat_dau or not ket_thuc or bat_dau >= ket_thuc:
        flash("Khung giờ không hợp lệ (Giờ bắt đầu phải nhỏ hơn giờ kết thúc).", "canh_bao")
        return redirect(url_for("cau_hinh.khung_gio"))

    try:
        sua_khung_gio(id, khoa_ch, thu, bat_dau, ket_thuc, ghi_chu)
        flash("Đã cập nhật khung giờ thành công.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi cập nhật: {str(e)}", "nguy_hiem")

    return redirect(url_for("cau_hinh.khung_gio"))

@cau_hinh_bp.route("/cau-hinh-gio/xoa/<int:id>", methods=["POST"])
@yeu_cau_quyen("CAUHINH.GIO")
def xoa_khung(id):
    try:
        xoa_khung_gio(id)
        flash("Đã xóa khung giờ thành công.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi khi xóa: {str(e)}", "nguy_hiem")

    return redirect(url_for("cau_hinh.khung_gio"))

@cau_hinh_bp.route("/ngay-dac-biet/them", methods=["POST"])
@yeu_cau_quyen("CAUHINH.GIO")
def them_ngay():
    ngay = request.form.get("ngay")
    ly_do = request.form.get("ly_do")
    cam_su_dung = 1 if request.form.get("cam_su_dung") == "1" else 0
    khoa_ghi_de = request.form.get("khoa_cau_hinh_ghi_de") or None
    loai_lap = request.form.get("loai_lap", "MOT_LAN")

    if not ngay or not ly_do:
        flash("Vui lòng nhập ngày và lý do áp dụng.", "canh_bao")
        return redirect(url_for("cau_hinh.khung_gio"))

    try:
        them_ngay_dac_biet(ngay, ly_do, cam_su_dung, khoa_ghi_de, loai_lap)
        flash("Đã cấu hình ngày đặc biệt thành công.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi cấu hình: {str(e)}", "nguy_hiem")

    return redirect(url_for("cau_hinh.khung_gio"))

@cau_hinh_bp.route("/ngay-dac-biet/sua/<int:id>", methods=["POST"])
@yeu_cau_quyen("CAUHINH.GIO")
def sua_ngay(id):
    ngay = request.form.get("ngay")
    ly_do = request.form.get("ly_do")
    cam_su_dung = 1 if request.form.get("cam_su_dung") == "1" else 0
    khoa_ghi_de = request.form.get("khoa_cau_hinh_ghi_de") or None
    loai_lap = request.form.get("loai_lap", "MOT_LAN")

    if not ngay or not ly_do:
        flash("Vui lòng nhập ngày và lý do áp dụng.", "canh_bao")
        return redirect(url_for("cau_hinh.khung_gio"))

    try:
        sua_ngay_dac_biet(id, ngay, ly_do, cam_su_dung, khoa_ghi_de, loai_lap)
        flash("Đã cập nhật ngày đặc biệt thành công.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi cập nhật: {str(e)}", "nguy_hiem")

    return redirect(url_for("cau_hinh.khung_gio"))

@cau_hinh_bp.route("/ngay-dac-biet/xoa/<int:id>", methods=["POST"])
@yeu_cau_quyen("CAUHINH.GIO")
def xoa_ngay(id):
    try:
        xoa_ngay_dac_biet(id)
        flash("Đã xóa ngày đặc biệt.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi xóa: {str(e)}", "nguy_hiem")

    return redirect(url_for("cau_hinh.khung_gio"))

@cau_hinh_bp.route("/tai-khoan-phan-quyen")
@yeu_cau_quyen("QUANTRI.TAIKHOAN")
def phan_quyen():
    user = session.get("nguoi_dung", {})
    user_ten_dn = user.get("ten_dang_nhap")
    user_bac = 100 if user_ten_dn == "admin" else BAC_VAI_TRO.get(user.get("ma_vai_tro"), 10)

    tai_khoan_list = lay_tat_ca_tai_khoan(bac_nguoi_xem=user_bac)
    vai_tro_list_tat_ca = lay_danh_sach_vai_tro()
    if user_ten_dn == "admin":
        vai_tro_list = vai_tro_list_tat_ca
    else:
        vai_tro_list = [vt for vt in vai_tro_list_tat_ca if BAC_VAI_TRO.get(vt["ma_vai_tro"], 10) <= user_bac]

    quyen_list = lay_danh_sach_quyen()
    quan_nhan_list = lay_tat_ca_quan_nhan()
    don_vi_list = lay_danh_sach_don_vi()
    tu_list = lay_danh_sach_tu()

    thong_tin_don_vi = lay_thong_tin_don_vi()

    return render_template(
        "cau_hinh/phan_quyen.html",
        tai_khoan_list=tai_khoan_list,
        vai_tro_list=vai_tro_list,
        quyen_list=quyen_list,
        quan_nhan_list=quan_nhan_list,
        don_vi_list=don_vi_list,
        tu_list=tu_list,
        thong_tin_don_vi=thong_tin_don_vi
    )

@cau_hinh_bp.route("/cau-hinh/thong-tin-don-vi", methods=["POST"])
@yeu_cau_quyen("QUANTRI.TAIKHOAN")
def cap_nhat_tt_don_vi():
    don_vi_cap_tren = request.form.get("don_vi_cap_tren", "").strip() or "TIỂU ĐOÀN 3"
    ten_don_vi = request.form.get("ten_don_vi", "").strip() or "ĐẠI ĐỘI 11"
    dia_diem = request.form.get("dia_diem", "").strip() or "Đà Nẵng"
    can_cu_quy_dinh = request.form.get("can_cu_quy_dinh", "").strip() or "Quy định số 763/QyĐ-SĐ ngày 12/3/2026 của Sư đoàn về việc quản lý, sử dụng thiết bị điện tử trong đơn vị"
    chuc_danh_chi_huy = request.form.get("chuc_danh_chi_huy", "").strip() or "CHỈ HUY ĐẠI ĐỘI"
    noi_nhan = request.form.get("noi_nhan", "").strip() or "- CH/d (để theo dõi);\n- Lưu: c."

    try:
        cap_nhat_thong_tin_don_vi({
            "don_vi_cap_tren": don_vi_cap_tren,
            "ten_don_vi": ten_don_vi,
            "dia_diem": dia_diem,
            "can_cu_quy_dinh": can_cu_quy_dinh,
            "chuc_danh_chi_huy": chuc_danh_chi_huy,
            "noi_nhan": noi_nhan
        })
        try:
            from models.co_so_du_lieu import lay_ket_noi
            kn = lay_ket_noi()
            ct = kn.cursor()
            ct.execute("UPDATE don_vi SET ten_don_vi = ? WHERE khoa_don_vi_cha IS NULL", (ten_don_vi,))
            kn.commit()
            kn.close()
        except Exception:
            pass
        flash("Đã cập nhật thông tin đơn vị và tiêu đề biểu mẫu báo cáo thành công.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi cập nhật thông tin đơn vị: {str(e)}", "nguy_hiem")

    return redirect(url_for("cau_hinh.phan_quyen"))

@cau_hinh_bp.route("/tai-khoan/them", methods=["POST"])
@yeu_cau_quyen("QUANTRI.TAIKHOAN")
def them_tk():
    user = session.get("nguoi_dung", {})
    user_ten_dn = user.get("ten_dang_nhap")
    user_bac = 100 if user_ten_dn == "admin" else BAC_VAI_TRO.get(user.get("ma_vai_tro"), 10)

    ten_dang_nhap = request.form.get("ten_dang_nhap", "").strip()
    mat_khau = request.form.get("mat_khau", "").strip()
    ho_ten = request.form.get("ho_ten", "").strip()
    khoa_vt = request.form.get("khoa_vai_tro")
    khoa_qn = request.form.get("khoa_quan_nhan") or None
    pham_vi_chon = request.form.get("pham_vi_chon", "").strip()
    pham_vi = request.form.get("pham_vi_loai", "TOAN_BO")
    pham_vi_khoa = None

    if pham_vi_chon:
        if ":" in pham_vi_chon:
            p_loai, p_id = pham_vi_chon.split(":", 1)
            pham_vi = p_loai
            try:
                pham_vi_khoa = int(p_id) if p_id and p_id != "0" else None
            except ValueError:
                pham_vi_khoa = None
        else:
            pham_vi = pham_vi_chon
            pham_vi_khoa = None
    elif pham_vi == "DON_VI":
        pv_list = request.form.getlist("pham_vi_khoa_don_vi")
        if pv_list:
            clean_list = [str(x).strip() for x in pv_list if str(x).strip().isdigit()]
            if clean_list:
                pham_vi_khoa = ",".join(clean_list)
        if not pham_vi_khoa:
            pv_val = request.form.get("pham_vi_khoa_don_vi")
            if pv_val:
                pham_vi_khoa = str(pv_val).strip()
    elif pham_vi == "TU":
        pv_val = request.form.get("pham_vi_khoa_tu")
        if pv_val:
            try:
                pham_vi_khoa = int(pv_val)
            except ValueError:
                pass

    if not ten_dang_nhap or not mat_khau or not ho_ten or not khoa_vt:
        flash("Vui lòng điền đầy đủ các thông tin tài khoản bắt buộc.", "canh_bao")
        return redirect(url_for("cau_hinh.phan_quyen"))

    if user_ten_dn != "admin":
        vai_tro_list = lay_danh_sach_vai_tro()
        target_role = next((vt for vt in vai_tro_list if str(vt["ma_tu_sinh"]) == str(khoa_vt)), None)
        if target_role and BAC_VAI_TRO.get(target_role["ma_vai_tro"], 10) > user_bac:
            flash("Đồng chí không thể gán vai trò cao hơn cấp bậc của mình.", "nguy_hiem")
            return redirect(url_for("cau_hinh.phan_quyen"))

    try:
        them_tai_khoan(ten_dang_nhap, mat_khau, ho_ten, khoa_vt, khoa_qn, pham_vi, pham_vi_khoa)
        flash(f"Đã tạo tài khoản {ten_dang_nhap} thành công.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi tạo tài khoản (có thể tên đăng nhập đã tồn tại): {str(e)}", "nguy_hiem")

    return redirect(url_for("cau_hinh.phan_quyen"))

@cau_hinh_bp.route("/tai-khoan/sua/<int:id>", methods=["POST"])
@yeu_cau_quyen("QUANTRI.TAIKHOAN")
def sua_tk(id):
    user = session.get("nguoi_dung", {})
    user_ten_dn = user.get("ten_dang_nhap")
    user_bac = 100 if user_ten_dn == "admin" else BAC_VAI_TRO.get(user.get("ma_vai_tro"), 10)

    target_user = lay_chi_tiet_tai_khoan(id)
    if not target_user:
        flash("Tài khoản này không tồn tại hoặc đã được xóa trước đó.", "thong_tin")
        return redirect(url_for("cau_hinh.phan_quyen"))

    target_ten_dn = target_user.get("ten_dang_nhap")
    target_bac = 100 if target_ten_dn == "admin" else BAC_VAI_TRO.get(target_user.get("ma_vai_tro"), 10)

    if target_ten_dn == "admin" and user_ten_dn != "admin":
        flash("Chỉ quản trị viên tối cao (admin) mới có quyền chỉnh sửa tài khoản admin.", "nguy_hiem")
        return redirect(url_for("cau_hinh.phan_quyen"))

    if user_ten_dn != "admin" and target_bac > user_bac:
        flash("Đồng chí không có thẩm quyền chỉnh sửa tài khoản cấp trên.", "nguy_hiem")
        return redirect(url_for("cau_hinh.phan_quyen"))

    ten_dang_nhap = request.form.get("ten_dang_nhap", "").strip()
    ho_ten = request.form.get("ho_ten", "").strip()
    mat_khau_moi = request.form.get("mat_khau_moi", "").strip()
    khoa_vt = request.form.get("khoa_vai_tro")
    pham_vi_chon = request.form.get("pham_vi_chon", "").strip()
    pham_vi = request.form.get("pham_vi_loai", "TOAN_BO")
    dang_dung = 1 if request.form.get("dang_dung") == "1" else 0

    pham_vi_khoa = None
    if pham_vi_chon:
        if ":" in pham_vi_chon:
            p_loai, p_id = pham_vi_chon.split(":", 1)
            pham_vi = p_loai
            try:
                pham_vi_khoa = int(p_id) if p_id and p_id != "0" else None
            except ValueError:
                pham_vi_khoa = None
        else:
            pham_vi = pham_vi_chon
            pham_vi_khoa = None
    elif pham_vi == "DON_VI":
        pv_list = request.form.getlist("pham_vi_khoa_don_vi")
        if pv_list:
            clean_list = [str(x).strip() for x in pv_list if str(x).strip().isdigit()]
            if clean_list:
                pham_vi_khoa = ",".join(clean_list)
        if not pham_vi_khoa:
            pv_val = request.form.get("pham_vi_khoa_don_vi")
            if pv_val:
                pham_vi_khoa = str(pv_val).strip()
    elif pham_vi == "TU":
        pv_val = request.form.get("pham_vi_khoa_tu")
        if pv_val:
            try:
                pham_vi_khoa = int(pv_val)
            except ValueError:
                pass

    if not ho_ten or not khoa_vt:
        flash("Vui lòng điền đủ họ tên và vai trò cán bộ.", "canh_bao")
        return redirect(url_for("cau_hinh.phan_quyen"))

    if user_ten_dn != "admin":
        vai_tro_list = lay_danh_sach_vai_tro()
        target_role = next((vt for vt in vai_tro_list if str(vt["ma_tu_sinh"]) == str(khoa_vt)), None)
        if target_role and BAC_VAI_TRO.get(target_role["ma_vai_tro"], 10) > user_bac:
            flash("Đồng chí không thể gán vai trò cao hơn cấp bậc của mình.", "nguy_hiem")
            return redirect(url_for("cau_hinh.phan_quyen"))

    if target_ten_dn != "admin" and not ten_dang_nhap:
        ten_dang_nhap = target_ten_dn

    try:
        ten_dn_cap_nhat = sua_tai_khoan(id, ho_ten, mat_khau_moi, khoa_vt, pham_vi, dang_dung, nguoi_thuc_hien=user_ten_dn, pham_vi_khoa=pham_vi_khoa, ten_dang_nhap=ten_dang_nhap)
        if user_ten_dn == target_ten_dn:
            user["ten_dang_nhap"] = ten_dn_cap_nhat
            user["ho_ten"] = ho_ten
            session["nguoi_dung"] = user
            session.modified = True
        flash("Đã cập nhật thông tin tài khoản thành công.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi cập nhật tài khoản: {str(e)}", "nguy_hiem")

    return redirect(url_for("cau_hinh.phan_quyen"))

@cau_hinh_bp.route("/tai-khoan/xoa/<int:id>", methods=["POST"])
@yeu_cau_quyen("QUANTRI.TAIKHOAN")
def xoa_tk(id):
    user = session.get("nguoi_dung", {})
    user_ten_dn = user.get("ten_dang_nhap")
    user_bac = 100 if user_ten_dn == "admin" else BAC_VAI_TRO.get(user.get("ma_vai_tro"), 10)

    target_user = lay_chi_tiet_tai_khoan(id)
    if not target_user:
        flash("Tài khoản này không tồn tại hoặc đã được xóa trước đó.", "thong_tin")
        return redirect(url_for("cau_hinh.phan_quyen"))

    target_ten_dn = target_user.get("ten_dang_nhap")
    if target_ten_dn == "admin" or id == 1:
        flash("Tuyệt đối không được phép xóa tài khoản quản trị tối cao (admin).", "nguy_hiem")
        return redirect(url_for("cau_hinh.phan_quyen"))

    target_bac = BAC_VAI_TRO.get(target_user.get("ma_vai_tro"), 10)
    if user_ten_dn != "admin" and target_bac > user_bac:
        flash("Đồng chí không có thẩm quyền xóa tài khoản cấp trên.", "nguy_hiem")
        return redirect(url_for("cau_hinh.phan_quyen"))

    try:
        xoa_tai_khoan(id)
        flash("Đã xóa tài khoản cán bộ.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi khi xóa tài khoản: {str(e)}", "nguy_hiem")

    return redirect(url_for("cau_hinh.phan_quyen"))

@cau_hinh_bp.route("/vai-tro/cap-nhat-quyen/<int:id>", methods=["POST"])
@yeu_cau_quyen("QUANTRI.TAIKHOAN")
def cap_nhat_quyen(id):
    user = session.get("nguoi_dung", {})
    user_ten_dn = user.get("ten_dang_nhap")
    user_bac = 100 if user_ten_dn == "admin" else BAC_VAI_TRO.get(user.get("ma_vai_tro"), 10)

    vai_tro_list = lay_danh_sach_vai_tro()
    target_role = next((vt for vt in vai_tro_list if vt["ma_tu_sinh"] == id), None)
    if not target_role:
        flash("Không tìm thấy vai trò chỉ định.", "nguy_hiem")
        return redirect(url_for("cau_hinh.phan_quyen"))

    target_role_bac = BAC_VAI_TRO.get(target_role["ma_vai_tro"], 10)
    if user_ten_dn != "admin" and target_role_bac > user_bac:
        flash("Đồng chí không có thẩm quyền điều chỉnh quyền của vai trò cấp trên.", "nguy_hiem")
        return redirect(url_for("cau_hinh.phan_quyen"))

    if target_role["ma_vai_tro"] == "QUAN_TRI" and user_ten_dn != "admin" and user.get("ma_vai_tro") != "QUAN_TRI":
        flash("Chỉ quản trị viên tối cao mới có quyền cấu hình vai trò Quản trị hệ thống.", "nguy_hiem")
        return redirect(url_for("cau_hinh.phan_quyen"))

    danh_sach_quyen = request.form.getlist("quyen_ids")
    danh_sach_khoa = [int(q) for q in danh_sach_quyen if q.isdigit()]

    try:
        cap_nhat_quyen_vai_tro(id, danh_sach_khoa)
        if user.get("khoa_vai_tro") == id:
            vai_tro_list_moi = lay_danh_sach_vai_tro()
            role_moi = next((vt for vt in vai_tro_list_moi if vt["ma_tu_sinh"] == id), None)
            if role_moi:
                user["cac_quyen"] = role_moi.get("ds_ma_quyen", [])
                user["danh_sach_quyen"] = role_moi.get("ds_ma_quyen", [])
                session["nguoi_dung"] = user
                session.modified = True
        flash(f"Đã cập nhật phân quyền cho vai trò {target_role['ten_vai_tro']} thành công.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi cập nhật quyền: {str(e)}", "nguy_hiem")

    return redirect(url_for("cau_hinh.phan_quyen"))
@cau_hinh_bp.route("/phan-doi")
@yeu_cau_quyen("QUANTRI.HETHONG", "CAUHINH.QUANNHAN")
def danh_sach_phan_doi():
    don_vi_list = lay_tat_ca_don_vi()
    goi_y = lay_goi_y_phan_doi_tiep_theo()
    return render_template(
        "cau_hinh/phan_doi.html",
        don_vi_list=don_vi_list,
        goi_y=goi_y
    )

@cau_hinh_bp.route("/phan-doi/them", methods=["POST"])
@yeu_cau_quyen("QUANTRI.HETHONG", "CAUHINH.QUANNHAN")
def them_phan_doi():
    ma_dv = request.form.get("ma_don_vi", "").strip().upper()
    ten_dv = request.form.get("ten_don_vi", "").strip()
    thu_tu = request.form.get("thu_tu", "").strip()
    thu_tu_val = int(thu_tu) if thu_tu and thu_tu.isdigit() else None

    if not ma_dv or not ten_dv:
        flash("Vui lòng điền đầy đủ mã và tên phân đội.", "canh_bao")
        return redirect(url_for("cau_hinh.danh_sach_phan_doi"))

    khoa_cha = request.form.get("khoa_don_vi_cha")
    khoa_cha_val = int(khoa_cha) if khoa_cha and khoa_cha.isdigit() else 1

    try:
        them_don_vi(ma_dv, ten_dv, khoa_don_vi_cha=khoa_cha_val, thu_tu=thu_tu_val)
        flash(f"Đã thêm phân đội {ten_dv} ({ma_dv}) thành công.", "thanh_cong")
    except ValueError as e:
        flash(str(e), "nguy_hiem")
    except Exception as e:
        flash(f"Lỗi thêm phân đội: {str(e)}", "nguy_hiem")

    return redirect(url_for("cau_hinh.danh_sach_phan_doi"))

@cau_hinh_bp.route("/phan-doi/sua/<int:id>", methods=["POST"])
@yeu_cau_quyen("QUANTRI.HETHONG", "CAUHINH.QUANNHAN")
def sua_phan_doi(id):
    ma_dv = request.form.get("ma_don_vi", "").strip().upper()
    ten_dv = request.form.get("ten_don_vi", "").strip()
    thu_tu = request.form.get("thu_tu", "").strip()
    dang_dung = 1 if request.form.get("dang_dung") == "1" else 0
    thu_tu_val = int(thu_tu) if thu_tu and thu_tu.isdigit() else None
    khoa_cha = request.form.get("khoa_don_vi_cha")
    khoa_cha_val = int(khoa_cha) if khoa_cha and khoa_cha.isdigit() else None

    if not ma_dv or not ten_dv:
        flash("Vui lòng điền đầy đủ mã và tên phân đội.", "canh_bao")
        return redirect(url_for("cau_hinh.danh_sach_phan_doi"))

    try:
        sua_don_vi(id, ma_dv, ten_dv, thu_tu=thu_tu_val, dang_dung=dang_dung, khoa_don_vi_cha=khoa_cha_val)
        flash(f"Đã cập nhật thông tin phân đội {ten_dv} thành công.", "thanh_cong")
    except ValueError as e:
        flash(str(e), "nguy_hiem")
    except Exception as e:
        flash(f"Lỗi cập nhật phân đội: {str(e)}", "nguy_hiem")

    return redirect(url_for("cau_hinh.danh_sach_phan_doi"))

@cau_hinh_bp.route("/phan-doi/xoa/<int:id>", methods=["POST"])
@yeu_cau_quyen("QUANTRI.HETHONG", "CAUHINH.QUANNHAN")
def xoa_phan_doi(id):
    try:
        xoa_don_vi(id)
        flash("Đã xóa phân đội thành công.", "thanh_cong")
    except ValueError as e:
        flash(str(e), "nguy_hiem")
    except Exception as e:
        flash(f"Lỗi xóa phân đội: {str(e)}", "nguy_hiem")

    return redirect(url_for("cau_hinh.danh_sach_phan_doi"))
