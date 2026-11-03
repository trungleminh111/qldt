from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from controllers import yeu_cau_dang_nhap, yeu_cau_quyen, lay_don_vi_gioi_han
from models.quan_nhan_model import lay_tat_ca_quan_nhan, lay_chi_tiet_quan_nhan, lay_danh_sach_don_vi
from models.giao_nhan_model import (
    kiem_tra_khung_gio,
    thuc_hien_lay_dien_thoai,
    thuc_hien_nop_dien_thoai,
    duyet_ngoai_le,
    danh_sach_chua_nop,
    danh_sach_lich_su
)

giao_nhan_bp = Blueprint("giao_nhan", __name__)

@giao_nhan_bp.route("/giao-nhan")
@yeu_cau_dang_nhap
@yeu_cau_quyen("GIAONHAN.XEM", "GIAONHAN.GHI")
def giao_nhan():
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    danh_sach_qn = lay_tat_ca_quan_nhan(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    cac_don_vi = lay_danh_sach_don_vi(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    ma_qn_chon = request.args.get("ma_qn")

    qn_hien_tai = None
    if ma_qn_chon:
        for qn in danh_sach_qn:
            if str(qn["ma_tu_sinh"]) == str(ma_qn_chon) or qn["ma_quan_nhan"] == ma_qn_chon:
                qn_hien_tai = qn
                break
    if not qn_hien_tai and danh_sach_qn:
        qn_hien_tai = danh_sach_qn[0]

    ket_qua_kiem_tra = None
    if qn_hien_tai:
        ket_qua_kiem_tra = kiem_tra_khung_gio(qn_hien_tai["ma_tu_sinh"])

    bay_gio = datetime.now()
    ngay_hien_tai = bay_gio.strftime("%Y-%m-%d")
    gio_hien_tai = bay_gio.strftime("%H:%M")

    return render_template(
        "giao_nhan/index.html",
        danh_sach_qn=danh_sach_qn,
        qn_hien_tai=qn_hien_tai,
        kiem_tra=ket_qua_kiem_tra,
        ngay_hien_tai=ngay_hien_tai,
        gio_hien_tai=gio_hien_tai,
        don_vi_list=cac_don_vi,
        khoa_don_vi_gioi_han=khoa_don_vi_gioi_han
    )

@giao_nhan_bp.route("/api/kiem-tra-gio")
@yeu_cau_dang_nhap
@yeu_cau_quyen("GIAONHAN.XEM", "GIAONHAN.GHI")
def api_kiem_tra_gio():
    khoa_qn = request.args.get("khoa_qn")
    ngay = request.args.get("ngay")
    gio = request.args.get("gio")

    if not khoa_qn:
        return jsonify({"hop_le": False, "thong_bao": "Chưa chọn quân nhân"})

    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    if khoa_don_vi_gioi_han:
        qn_kiem_tra = lay_chi_tiet_quan_nhan(khoa_qn, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
        if not qn_kiem_tra:
            return jsonify({"hop_le": False, "thong_bao": "Quân nhân không thuộc đơn vị quản lý"})

    thoi_diem = None
    if ngay and gio:
        thoi_diem = f"{ngay} {gio}:00"

    ket_qua = kiem_tra_khung_gio(khoa_qn, thoi_diem)
    return jsonify(ket_qua)

@giao_nhan_bp.route("/giao-nhan/lay", methods=["POST"])
@yeu_cau_dang_nhap
@yeu_cau_quyen("GIAONHAN.GHI", "GIAONHAN.XEM")
def lay_may():
    khoa_qn = request.form.get("khoa_quan_nhan")
    ngay = request.form.get("ngay")
    gio = request.form.get("gio")
    la_ngoai_le = request.form.get("la_ngoai_le") == "1"
    ly_do = request.form.get("ly_do", "")
    ghi_chu = request.form.get("ghi_chu", "")
    han_nop = request.form.get("han_nop", "")

    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    if khoa_don_vi_gioi_han:
        qn_kiem_tra = lay_chi_tiet_quan_nhan(khoa_qn, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
        if not qn_kiem_tra:
            flash("Đồng chí không có thẩm quyền thao tác với quân nhân ngoài đơn vị.", "nguy_hiem")
            return redirect(url_for("giao_nhan.giao_nhan"))

    thoi_gian = f"{ngay} {gio}:00" if ngay and gio else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    nguoi_dung = session.get("nguoi_dung", {})
    khoa_nguoi_thuc_hien = nguoi_dung.get("ma_tu_sinh", 1)
    ten_nguoi_thuc_hien = nguoi_dung.get("ho_ten", "Cán bộ trực ca")

    co_duyet = ("NGOAILE.DUYET" in (nguoi_dung.get("danh_sach_quyen") or [])) or (nguoi_dung.get("ma_vai_tro") in ("ADMIN", "CHI_HUY"))
    khoa_nguoi_duyet = khoa_nguoi_thuc_hien if co_duyet else None

    thanh_cong, thong_bao = thuc_hien_lay_dien_thoai(
        khoa_quan_nhan=khoa_qn,
        khoa_nguoi_thuc_hien=khoa_nguoi_thuc_hien,
        ten_nguoi_thuc_hien=ten_nguoi_thuc_hien,
        thoi_gian=thoi_gian,
        la_ngoai_le=la_ngoai_le,
        ly_do=ly_do,
        ghi_chu=ghi_chu,
        han_nop=han_nop,
        khoa_don_vi_gioi_han=khoa_don_vi_gioi_han,
        khoa_nguoi_duyet=khoa_nguoi_duyet
    )

    if thanh_cong:
        flash(thong_bao, "thanh_cong")
    else:
        flash(thong_bao, "nguy_hiem")

    return redirect(url_for("giao_nhan.giao_nhan", ma_qn=khoa_qn))

@giao_nhan_bp.route("/giao-nhan/nop", methods=["POST"])
@yeu_cau_dang_nhap
@yeu_cau_quyen("GIAONHAN.GHI", "GIAONHAN.XEM")
def nop_may():
    khoa_qn = request.form.get("khoa_quan_nhan")
    ghi_chu = request.form.get("ghi_chu", "")
    ngay = request.form.get("ngay")
    gio = request.form.get("gio")

    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    if khoa_don_vi_gioi_han:
        qn_kiem_tra = lay_chi_tiet_quan_nhan(khoa_qn, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
        if not qn_kiem_tra:
            flash("Đồng chí không có thẩm quyền thao tác với quân nhân ngoài đơn vị.", "nguy_hiem")
            return redirect(url_for("giao_nhan.giao_nhan"))

    thoi_gian = f"{ngay} {gio}:00" if ngay and gio else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    nguoi_dung = session.get("nguoi_dung", {})
    khoa_nguoi_thuc_hien = nguoi_dung.get("ma_tu_sinh", 1)
    ten_nguoi_thuc_hien = nguoi_dung.get("ho_ten", "Cán bộ trực ca")

    thanh_cong, thong_bao = thuc_hien_nop_dien_thoai(
        khoa_quan_nhan=khoa_qn,
        khoa_nguoi_thuc_hien=khoa_nguoi_thuc_hien,
        ten_nguoi_thuc_hien=ten_nguoi_thuc_hien,
        thoi_gian=thoi_gian,
        ghi_chu=ghi_chu,
        khoa_don_vi_gioi_han=khoa_don_vi_gioi_han
    )

    if thanh_cong:
        flash(thong_bao, "thanh_cong")
    else:
        flash(thong_bao, "nguy_hiem")

    url_chuyen_huong = request.form.get("url_chuyen_huong")
    if url_chuyen_huong:
        return redirect(url_chuyen_huong)
    return redirect(url_for("giao_nhan.giao_nhan", ma_qn=khoa_qn))

@giao_nhan_bp.route("/chua-nop")
@yeu_cau_dang_nhap
@yeu_cau_quyen("GIAONHAN.XEM", "GIAONHAN.GHI")
def chua_nop():
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    danh_sach = danh_sach_chua_nop(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    return render_template("chua_nop/index.html", danh_sach=danh_sach)

@giao_nhan_bp.route("/lich-su")
@yeu_cau_dang_nhap
@yeu_cau_quyen("GIAONHAN.XEM", "GIAONHAN.GHI")
def lich_su():
    tu_khoa = request.args.get("tu_khoa", "")
    ngay = request.args.get("ngay", "")
    loai = request.args.get("loai", "TAT_CA")
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()

    danh_sach = danh_sach_lich_su(tu_khoa=tu_khoa, ngay=ngay, loai=loai, limit=200, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    return render_template(
        "giao_nhan/lich_su.html",
        danh_sach=danh_sach,
        tu_khoa=tu_khoa,
        ngay=ngay,
        loai=loai
    )

@giao_nhan_bp.route("/duyet-ngoai-le/<int:id>", methods=["POST"])
@yeu_cau_dang_nhap
@yeu_cau_quyen("NGOAILE.DUYET")
def duyet_don_ngoai_le(id):
    nguoi_dung = session.get("nguoi_dung", {})
    khoa_nguoi_duyet = nguoi_dung.get("ma_tu_sinh", 1)
    duyet_ngoai_le(id, khoa_nguoi_duyet)
    flash("Đã phê duyệt đề nghị sử dụng điện thoại ngoại lệ thành công.", "thanh_cong")
    return redirect(request.referrer or url_for("giao_nhan.giao_nhan"))
