import os
import openpyxl
from io import BytesIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
import config
from controllers import yeu_cau_dang_nhap, lay_don_vi_gioi_han
from models.quan_nhan_model import (
    lay_tat_ca_quan_nhan,
    lay_chi_tiet_quan_nhan,
    them_quan_nhan,
    sua_quan_nhan,
    xoa_quan_nhan,
    import_quan_nhan_excel,
    lay_danh_sach_don_vi,
    lay_danh_sach_cap_bac,
    lay_danh_sach_chuc_vu
)
from models.giao_nhan_model import danh_sach_lich_su

quan_nhan_bp = Blueprint("quan_nhan", __name__)

@quan_nhan_bp.route("/quan-nhan")
@yeu_cau_dang_nhap
def danh_sach():
    tu_khoa = request.args.get("tu_khoa", "")
    ma_don_vi = request.args.get("don_vi", "TAT_CA")
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()

    danh_sach_qn = lay_tat_ca_quan_nhan(tu_khoa=tu_khoa, ma_don_vi=ma_don_vi, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    cac_don_vi = lay_danh_sach_don_vi(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    cac_cap_bac = lay_danh_sach_cap_bac()
    cac_chuc_vu = lay_danh_sach_chuc_vu()

    tong_so = len(danh_sach_qn)
    so_da_nop = sum(1 for qn in danh_sach_qn if qn.get("trang_thai_may") in ["Đã nộp", "Trong tủ"])
    so_da_lay = sum(1 for qn in danh_sach_qn if qn.get("trang_thai_may") == "Đã lấy")

    return render_template(
        "quan_nhan/index.html",
        danh_sach=danh_sach_qn,
        don_vi_list=cac_don_vi,
        cap_bac_list=cac_cap_bac,
        chuc_vu_list=cac_chuc_vu,
        tu_khoa=tu_khoa,
        don_vi_hien_tai=ma_don_vi,
        tong_so=tong_so,
        so_da_nop=so_da_nop,
        so_da_lay=so_da_lay
    )

@quan_nhan_bp.route("/quan-nhan/chi-tiet/<int:id>")
@yeu_cau_dang_nhap
def chi_tiet(id):
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    qn = lay_chi_tiet_quan_nhan(id, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    if not qn:
        flash("Không tìm thấy quân nhân hoặc đồng chí không có quyền truy cập.", "canh_bao")
        return redirect(url_for("quan_nhan.danh_sach"))

    cac_don_vi = lay_danh_sach_don_vi(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    cac_cap_bac = lay_danh_sach_cap_bac()
    cac_chuc_vu = lay_danh_sach_chuc_vu()
    lich_su = danh_sach_lich_su(tu_khoa=qn["ma_quan_nhan"], limit=10, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    return render_template(
        "quan_nhan/chi_tiet.html",
        qn=qn,
        lich_su=lich_su,
        don_vi_list=cac_don_vi,
        cap_bac_list=cac_cap_bac,
        chuc_vu_list=cac_chuc_vu
    )

@quan_nhan_bp.route("/quan-nhan/them", methods=["POST"])
@yeu_cau_dang_nhap
def them():
    ma_qn = request.form.get("ma_quan_nhan", "").strip()
    ho_ten = request.form.get("ho_ten", "").strip()
    khoa_cb = request.form.get("khoa_cap_bac")
    khoa_cv = request.form.get("khoa_chuc_vu")
    khoa_dv = request.form.get("khoa_don_vi")
    ngay_sinh = request.form.get("ngay_sinh")
    ngay_nhap_ngu = request.form.get("ngay_nhap_ngu")
    ghi_chu = request.form.get("ghi_chu", "").strip()

    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    if khoa_don_vi_gioi_han:
        khoa_dv = khoa_don_vi_gioi_han

    if not ma_qn or not ho_ten or not khoa_cb or not khoa_cv or not khoa_dv:
        flash("Vui lòng điền đầy đủ các thông tin bắt buộc.", "canh_bao")
        return redirect(url_for("quan_nhan.danh_sach"))

    try:
        them_quan_nhan(
            ma_quan_nhan=ma_qn,
            ho_ten=ho_ten,
            khoa_cap_bac=khoa_cb,
            khoa_chuc_vu=khoa_cv,
            khoa_don_vi=khoa_dv,
            ngay_sinh=ngay_sinh,
            ngay_nhap_ngu=ngay_nhap_ngu,
            ghi_chu=ghi_chu
        )
        flash(f"Đã thêm quân nhân {ho_ten} thành công.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi khi thêm quân nhân (có thể mã quân nhân đã tồn tại): {str(e)}", "nguy_hiem")

    return redirect(url_for("quan_nhan.danh_sach"))

@quan_nhan_bp.route("/quan-nhan/sua/<int:id>", methods=["POST"])
@yeu_cau_dang_nhap
def sua(id):
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    qn_kiem_tra = lay_chi_tiet_quan_nhan(id, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    if not qn_kiem_tra:
        flash("Đồng chí không có thẩm quyền sửa quân nhân này.", "nguy_hiem")
        return redirect(url_for("quan_nhan.danh_sach"))

    ho_ten = request.form.get("ho_ten", "").strip()
    if not ho_ten:
        flash("Họ và tên quân nhân không được để trống.", "canh_bao")
        return redirect(url_for("quan_nhan.chi_tiet", id=id))
    khoa_cb = request.form.get("khoa_cap_bac")
    khoa_cv = request.form.get("khoa_chuc_vu")
    khoa_dv = request.form.get("khoa_don_vi")
    ngay_sinh = request.form.get("ngay_sinh")
    ngay_nhap_ngu = request.form.get("ngay_nhap_ngu")
    ghi_chu = request.form.get("ghi_chu", "").strip()

    if khoa_don_vi_gioi_han:
        khoa_dv = khoa_don_vi_gioi_han

    try:
        sua_quan_nhan(
            ma_tu_sinh=id,
            ho_ten=ho_ten,
            khoa_cap_bac=khoa_cb,
            khoa_chuc_vu=khoa_cv,
            khoa_don_vi=khoa_dv,
            ngay_sinh=ngay_sinh,
            ngay_nhap_ngu=ngay_nhap_ngu,
            ghi_chu=ghi_chu
        )
        flash("Đã cập nhật hồ sơ quân nhân thành công.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi cập nhật: {str(e)}", "nguy_hiem")

    return redirect(url_for("quan_nhan.chi_tiet", id=id))

@quan_nhan_bp.route("/quan-nhan/xoa/<int:id>", methods=["POST"])
@yeu_cau_dang_nhap
def xoa(id):
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    qn_kiem_tra = lay_chi_tiet_quan_nhan(id, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    if not qn_kiem_tra:
        flash("Đồng chí không có thẩm quyền xóa quân nhân này.", "nguy_hiem")
        return redirect(url_for("quan_nhan.danh_sach"))

    try:
        xoa_quan_nhan(id)
        flash("Đã xóa quân nhân khỏi danh sách đơn vị.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi khi xóa: {str(e)}", "nguy_hiem")

    return redirect(url_for("quan_nhan.danh_sach"))

@quan_nhan_bp.route("/quan-nhan/import-excel", methods=["POST"])
@yeu_cau_dang_nhap
def import_excel():
    tep_tin = request.files.get("file_excel")
    if not tep_tin or tep_tin.filename == "":
        flash("Vui lòng chọn tệp tin Excel (.xlsx).", "canh_bao")
        return redirect(url_for("quan_nhan.danh_sach"))

    duong_dan_luu = os.path.join(config.UPLOAD_FOLDER, tep_tin.filename)
    tep_tin.save(duong_dan_luu)

    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    try:
        so_luong = import_quan_nhan_excel(duong_dan_luu, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
        flash(f"Đã import thành công {so_luong} quân nhân từ tệp Excel.", "thanh_cong")
    except Exception as e:
        flash(f"Lỗi khi đọc tệp Excel: {str(e)}", "nguy_hiem")
    finally:
        if os.path.exists(duong_dan_luu):
            os.remove(duong_dan_luu)

    return redirect(url_for("quan_nhan.danh_sach"))

@quan_nhan_bp.route("/quan-nhan/mau-excel")
@yeu_cau_dang_nhap
def tai_mau_excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "DanhSachQuanNhan"
    tieu_de = ["Mã quân nhân", "Họ và tên", "Cấp bậc", "Chức vụ", "Đơn vị"]
    ws.append(tieu_de)
    ws.append(["QN015", "Nguyễn Văn Mẫu", "Binh nhì", "Chiến sĩ", "Trung đội 1"])
    ws.append(["QN016", "Trần Văn Mẫu", "Hạ sĩ", "Tiểu đội trưởng", "Trung đội 2"])

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    return send_file(
        stream,
        as_attachment=True,
        download_name="Mau_Import_Quan_Nhan.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
