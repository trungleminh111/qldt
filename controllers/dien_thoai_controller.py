from flask import Blueprint, render_template, request, redirect, url_for, flash
from controllers import yeu_cau_dang_nhap, lay_don_vi_gioi_han
from models.dien_thoai_model import (
    lay_tat_ca_dien_thoai,
    lay_chi_tiet_dien_thoai,
    them_dien_thoai,
    sua_dien_thoai,
    lay_danh_sach_tu,
    lay_so_do_tu,
    lay_tat_ca_ngan_trong,
    lay_goi_y_tu_tiep_theo,
    them_tu,
    lay_goi_y_ngan_tiep_theo,
    them_ngan
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
    cac_tu = lay_danh_sach_tu(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    tu_con_trong = [t for t in cac_tu if (t.get("so_ngan_trong") or 0) > 0]

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
        tu_trong_list=tu_con_trong,
        tu_khoa=tu_khoa,
        don_vi_hien_tai=ma_don_vi,
        tong_so=tong_so,
        so_apple=so_apple,
        so_samsung=so_samsung,
        so_khac=so_khac,
        khoa_don_vi_gioi_han=khoa_don_vi_gioi_han
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
    ngan_trong = lay_tat_ca_ngan_trong(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    cac_tu = lay_danh_sach_tu(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    tu_con_trong = [t for t in cac_tu if (t.get("so_ngan_trong") or 0) > 0 or (dt.get("ma_tu") and t.get("ma_tu") == dt.get("ma_tu"))]
    return render_template(
        "dien_thoai/chi_tiet.html",
        dt=dt,
        lich_su=lich_su,
        ngan_trong_list=ngan_trong,
        tu_trong_list=tu_con_trong
    )

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

@dien_thoai_bp.route("/dien-thoai/gan-ngan/<int:id>", methods=["POST"])
@yeu_cau_dang_nhap
def gan_ngan_nhanh(id):
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    dt = lay_chi_tiet_dien_thoai(id, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    if not dt:
        flash("Không tìm thấy thiết bị hoặc đồng chí không có thẩm quyền.", "canh_bao")
        return redirect(url_for("dien_thoai.danh_sach"))

    ma_ngan = request.form.get("ma_ngan", "").strip()
    khoa_qn = dt["khoa_quan_nhan"]

    try:
        sua_dien_thoai(
            ma_tu_sinh=id,
            ten_dien_thoai=dt["ten_dien_thoai"],
            hang_san_xuat=dt["hang_san_xuat"],
            model=dt["model"] or "",
            so_imei=dt["so_imei"] or "",
            so_dien_thoai=dt["so_dien_thoai"] or "",
            khoa_quan_nhan=khoa_qn,
            ma_ngan=ma_ngan
        )
        if ma_ngan:
            flash(f"Đã gán ngăn {ma_ngan} cho thiết bị {dt['ma_thiet_bi']} thành công.", "thanh_cong")
        else:
            flash(f"Đã hủy gán vị trí ngăn tủ cho thiết bị {dt['ma_thiet_bi']}.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi khi gán vị trí ngăn tủ: {str(e)}", "nguy_hiem")

    return redirect(request.referrer or url_for("dien_thoai.danh_sach"))

@dien_thoai_bp.route("/tu-dien-thoai")
@yeu_cau_dang_nhap
def danh_sach_tu():
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    danh_sach_tu_data = lay_danh_sach_tu(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    cac_don_vi = lay_danh_sach_don_vi(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    goi_y_tu = lay_goi_y_tu_tiep_theo()
    return render_template(
        "dien_thoai/tu.html",
        tu_list=danh_sach_tu_data,
        don_vi_list=cac_don_vi,
        goi_y_tu=goi_y_tu,
        khoa_don_vi_gioi_han=khoa_don_vi_gioi_han
    )

@dien_thoai_bp.route("/tu-dien-thoai/them", methods=["POST"])
@yeu_cau_dang_nhap
def them_tu_moi():
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    ma_tu = request.form.get("ma_tu", "").strip().upper()
    ten_tu = request.form.get("ten_tu", "").strip()
    vi_tri = request.form.get("vi_tri", "").strip()
    so_ngan_raw = request.form.get("so_ngan", "24").strip()
    tien_to_ngan = request.form.get("tien_to_ngan", "").strip().upper()
    khoa_dv_raw = request.form.get("khoa_don_vi_quan_ly")

    if not ma_tu or not ten_tu:
        flash("Vui lòng nhập đầy đủ mã tủ và tên tủ bảo quản.", "canh_bao")
        return redirect(url_for("dien_thoai.danh_sach_tu"))

    try:
        so_ngan = int(so_ngan_raw) if so_ngan_raw else 24
    except ValueError:
        so_ngan = 24

    khoa_don_vi = None
    if khoa_dv_raw:
        try:
            khoa_don_vi = int(khoa_dv_raw)
        except ValueError:
            khoa_don_vi = None

    if khoa_don_vi_gioi_han:
        ds_chophep = khoa_don_vi_gioi_han if isinstance(khoa_don_vi_gioi_han, (list, tuple, set)) else [int(khoa_don_vi_gioi_han)]
        if khoa_don_vi not in ds_chophep:
            khoa_don_vi = ds_chophep[0] if ds_chophep else None

    try:
        them_tu(
            ma_tu=ma_tu,
            ten_tu=ten_tu,
            vi_tri=vi_tri,
            so_ngan=so_ngan,
            khoa_don_vi_quan_ly=khoa_don_vi,
            tien_to_ngan=tien_to_ngan
        )
        flash(f"Đã khởi tạo thành công {ten_tu} ({ma_tu}) gồm {so_ngan} ngăn bảo quản.", "thanh_cong")
        return redirect(url_for("dien_thoai.so_do_tu", ma_tu=ma_tu))
    except Exception as e:
        flash(f"Lỗi khi thêm tủ mới (có thể mã tủ đã tồn tại): {str(e)}", "nguy_hiem")

    return redirect(url_for("dien_thoai.danh_sach_tu"))

@dien_thoai_bp.route("/tu-dien-thoai/<ma_tu>")
@yeu_cau_dang_nhap
def so_do_tu(ma_tu):
    ma_tu = (ma_tu or "").strip().upper()
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    cac_tu = lay_danh_sach_tu(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    tu_hien_tai = next((t for t in cac_tu if t["ma_tu"].upper() == ma_tu), None)
    if not tu_hien_tai:
        tat_ca_tu = lay_danh_sach_tu(khoa_don_vi_gioi_han=None)
        tu_ton_tai = next((t for t in tat_ca_tu if t["ma_tu"].upper() == ma_tu), None)
        if tu_ton_tai and not khoa_don_vi_gioi_han:
            tu_hien_tai = tu_ton_tai
            cac_tu = tat_ca_tu
        elif not tu_ton_tai:
            flash("Tủ bảo quản không tồn tại hoặc đã ngừng sử dụng.", "canh_bao")
            return redirect(url_for("dien_thoai.danh_sach_tu"))
        else:
            flash("Đồng chí không có thẩm quyền truy cập tủ của đơn vị khác.", "canh_bao")
            return redirect(url_for("dien_thoai.danh_sach_tu"))
    ngan_list = lay_so_do_tu(ma_tu, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    goi_y_ngan = lay_goi_y_ngan_tiep_theo(tu_hien_tai["ma_tu_sinh"])
    cac_don_vi = lay_danh_sach_don_vi(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    goi_y_tu = lay_goi_y_tu_tiep_theo()
    return render_template(
        "dien_thoai/so_do_tu.html",
        tu_list=cac_tu,
        tu_hien_tai=tu_hien_tai,
        ngan_list=ngan_list,
        ma_tu_hien_tai=ma_tu,
        goi_y_ngan=goi_y_ngan,
        don_vi_list=cac_don_vi,
        goi_y_tu=goi_y_tu
    )

@dien_thoai_bp.route("/ngan-tu/them", methods=["POST"])
@yeu_cau_dang_nhap
def them_ngan_moi():
    khoa_tu_raw = request.form.get("khoa_tu")
    ma_tu = request.form.get("ma_tu", "").strip()
    ten_ngan = request.form.get("ten_ngan", "").strip()
    so_luong_raw = request.form.get("so_luong", "1").strip()

    if not khoa_tu_raw:
        flash("Không xác định được tủ bảo quản.", "nguy_hiem")
        return redirect(url_for("dien_thoai.danh_sach_tu"))

    try:
        khoa_tu = int(khoa_tu_raw)
        so_luong = int(so_luong_raw) if so_luong_raw else 1
    except ValueError:
        flash("Dữ liệu nhập không hợp lệ.", "canh_bao")
        return redirect(url_for("dien_thoai.danh_sach_tu"))

    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    if khoa_don_vi_gioi_han:
        cac_tu = lay_danh_sach_tu(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
        co_quyen = any(t["ma_tu_sinh"] == khoa_tu for t in cac_tu)
        if not co_quyen:
            flash("Đồng chí không có quyền thao tác trên tủ của đơn vị khác.", "canh_bao")
            return redirect(url_for("dien_thoai.danh_sach_tu"))

    try:
        them_ngan(khoa_tu=khoa_tu, ten_ngan=ten_ngan, so_luong=so_luong)
        flash(f"Đã thêm thành công {so_luong} ngăn mới vào tủ.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi khi thêm ngăn tủ: {str(e)}", "nguy_hiem")

    if ma_tu:
        return redirect(url_for("dien_thoai.so_do_tu", ma_tu=ma_tu))
    return redirect(url_for("dien_thoai.danh_sach_tu"))
