from flask import Blueprint, render_template, request, redirect, url_for, flash
from controllers import yeu_cau_dang_nhap, lay_don_vi_gioi_han
from models.dien_thoai_model import (
    lay_tat_ca_dien_thoai,
    lay_chi_tiet_dien_thoai,
    them_dien_thoai,
    sua_dien_thoai,
    lay_danh_sach_tu,
    lay_so_do_tu,
    lay_tat_ca_ngan_trong
)
from models.quan_nhan_model import lay_tat_ca_quan_nhan, lay_chi_tiet_quan_nhan, lay_danh_sach_don_vi
from models.giao_nhan_model import danh_sach_lich_su

dien_thoai_bp = Blueprint("dien_thoai", __name__)

@dien_thoai_bp.route("/dien-thoai")
@yeu_cau_dang_nhap
def danh_sach():
    tu_khoa = request.args.get("tu_khoa", "")
    ma_don_vi = request.args.get("don_vi", "TAT_CA")
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()

    danh_sach_dt = lay_tat_ca_dien_thoai(tu_khoa=tu_khoa, ma_don_vi=ma_don_vi, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    cac_don_vi = lay_danh_sach_don_vi(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    danh_sach_qn = lay_tat_ca_quan_nhan(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    ngan_trong = lay_tat_ca_ngan_trong(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)

    tong_so = len(danh_sach_dt)
    so_apple = sum(1 for dt in danh_sach_dt if (dt.get("hang_san_xuat") or "").lower() == "apple")
    so_samsung = sum(1 for dt in danh_sach_dt if (dt.get("hang_san_xuat") or "").lower() == "samsung")
    so_khac = tong_so - so_apple - so_samsung

    return render_template(
        "dien_thoai/index.html",
        danh_sach=danh_sach_dt,
        don_vi_list=cac_don_vi,
        quan_nhan_list=danh_sach_qn,
        ngan_trong_list=ngan_trong,
        tu_khoa=tu_khoa,
        don_vi_hien_tai=ma_don_vi,
        tong_so=tong_so,
        so_apple=so_apple,
        so_samsung=so_samsung,
        so_khac=so_khac
    )

@dien_thoai_bp.route("/dien-thoai/chi-tiet/<int:id>")
@yeu_cau_dang_nhap
def chi_tiet(id):
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    dt = lay_chi_tiet_dien_thoai(id, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    if not dt:
        flash("Không tìm thấy thiết bị hoặc đồng chí không có thẩm quyền truy cập.", "canh_bao")
        return redirect(url_for("dien_thoai.danh_sach"))

    lich_su = danh_sach_lich_su(tu_khoa=dt["ma_thiet_bi"], limit=10, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    return render_template("dien_thoai/chi_tiet.html", dt=dt, lich_su=lich_su)

@dien_thoai_bp.route("/dien-thoai/them", methods=["POST"])
@yeu_cau_dang_nhap
def them():
    ma_tb = request.form.get("ma_thiet_bi", "").strip()
    ten_dt = request.form.get("ten_dien_thoai", "").strip()
    hang = request.form.get("hang_san_xuat", "").strip()
    model = request.form.get("model", "").strip()
    imei = request.form.get("so_imei", "").strip() or None
    sdt = request.form.get("so_dien_thoai", "").strip() or None
    khoa_qn = request.form.get("khoa_quan_nhan")
    ma_ngan = request.form.get("ma_ngan", "") or None

    if not ma_tb or not ten_dt or not khoa_qn:
        flash("Vui lòng nhập đầy đủ mã thiết bị, tên máy và chọn quân nhân sở hữu.", "canh_bao")
        return redirect(url_for("dien_thoai.danh_sach"))

    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    if khoa_don_vi_gioi_han:
        qn_kiem_tra = lay_chi_tiet_quan_nhan(khoa_qn, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
        if not qn_kiem_tra:
            flash("Đồng chí không có quyền gán thiết bị cho quân nhân ngoài đơn vị.", "nguy_hiem")
            return redirect(url_for("dien_thoai.danh_sach"))

    try:
        them_dien_thoai(
            ma_thiet_bi=ma_tb,
            ten_dien_thoai=ten_dt,
            hang_san_xuat=hang,
            model=model,
            so_imei=imei,
            so_dien_thoai=sdt,
            khoa_quan_nhan=khoa_qn,
            ma_ngan=ma_ngan
        )
        flash(f"Đã thêm thiết bị {ma_tb} thành công.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi khi thêm thiết bị (mã thiết bị hoặc IMEI có thể đã tồn tại): {str(e)}", "nguy_hiem")

    return redirect(url_for("dien_thoai.danh_sach"))

@dien_thoai_bp.route("/dien-thoai/sua/<int:id>", methods=["POST"])
@yeu_cau_dang_nhap
def sua(id):
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    if khoa_don_vi_gioi_han:
        dt_kiem_tra = lay_chi_tiet_dien_thoai(id, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
        if not dt_kiem_tra:
            flash("Đồng chí không có thẩm quyền sửa thiết bị này.", "nguy_hiem")
            return redirect(url_for("dien_thoai.danh_sach"))

    ten_dt = request.form.get("ten_dien_thoai", "").strip()
    hang = request.form.get("hang_san_xuat", "").strip()
    model = request.form.get("model", "").strip()
    imei = request.form.get("so_imei", "").strip() or None
    sdt = request.form.get("so_dien_thoai", "").strip() or None
    khoa_qn = request.form.get("khoa_quan_nhan")
    ma_ngan = request.form.get("ma_ngan", "") or None

    if khoa_don_vi_gioi_han and khoa_qn:
        qn_kiem_tra = lay_chi_tiet_quan_nhan(khoa_qn, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
        if not qn_kiem_tra:
            flash("Đồng chí không có quyền gán thiết bị cho quân nhân ngoài đơn vị.", "nguy_hiem")
            return redirect(url_for("dien_thoai.danh_sach"))

    try:
        sua_dien_thoai(
            ma_tu_sinh=id,
            ten_dien_thoai=ten_dt,
            hang_san_xuat=hang,
            model=model,
            so_imei=imei,
            so_dien_thoai=sdt,
            khoa_quan_nhan=khoa_qn,
            ma_ngan=ma_ngan
        )
        flash("Đã cập nhật thông tin thiết bị thành công.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi cập nhật: {str(e)}", "nguy_hiem")

    return redirect(url_for("dien_thoai.danh_sach"))

@dien_thoai_bp.route("/tu-dien-thoai")
@yeu_cau_dang_nhap
def danh_sach_tu():
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    danh_sach_tu_data = lay_danh_sach_tu(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    return render_template("dien_thoai/tu.html", tu_list=danh_sach_tu_data)

@dien_thoai_bp.route("/tu-dien-thoai/<ma_tu>")
@yeu_cau_dang_nhap
def so_do_tu(ma_tu):
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    cac_tu = lay_danh_sach_tu(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    tu_hien_tai = next((t for t in cac_tu if t["ma_tu"] == ma_tu), None)
    if not tu_hien_tai:
        flash("Đồng chí không có thẩm quyền truy cập tủ của đơn vị khác.", "canh_bao")
        return redirect(url_for("dien_thoai.danh_sach_tu"))
    ngan_list = lay_so_do_tu(ma_tu, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    return render_template(
        "dien_thoai/so_do_tu.html",
        tu_list=cac_tu,
        tu_hien_tai=tu_hien_tai,
        ngan_list=ngan_list,
        ma_tu_hien_tai=ma_tu
    )
