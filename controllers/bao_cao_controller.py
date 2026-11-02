from datetime import datetime
from io import BytesIO
import openpyxl
from flask import Blueprint, render_template, send_file
from controllers import yeu_cau_dang_nhap, lay_don_vi_gioi_han
from models.bao_cao_model import lay_thong_ke_tong_quan
from models.giao_nhan_model import danh_sach_lich_su

bao_cao_bp = Blueprint("bao_cao", __name__)

@bao_cao_bp.route("/bao-cao")
@yeu_cau_dang_nhap
def index():
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    thong_ke = lay_thong_ke_tong_quan(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    lich_su = danh_sach_lich_su(limit=50, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    return render_template("bao_cao/index.html", thong_ke=thong_ke, lich_su=lich_su)

@bao_cao_bp.route("/bao-cao/xuat-excel")
@yeu_cau_dang_nhap
def xuat_excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "BaoCaoGiaoNhan"

    tieu_de = [
        "Mã giao dịch", "Thời gian", "Quân nhân", "Cấp bậc", "Đơn vị",
        "Mã thiết bị", "Tên máy", "Tủ / Ngăn", "Loại giao dịch",
        "Kết quả", "Người thực hiện", "Ghi chú"
    ]
    ws.append(tieu_de)

    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    lich_su = danh_sach_lich_su(limit=500, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    for h in lich_su:
        ws.append([
            h["ma_tu_sinh"],
            h["thoi_gian"],
            h["ho_ten"],
            h["ten_cap_bac"],
            h["ten_don_vi"],
            h["ma_thiet_bi"],
            h["ten_dien_thoai"],
            f"{h.get('ma_tu') or ''} - Ngăn {h.get('ten_ngan') or h.get('ma_ngan') or ''}",
            "Lấy ra" if h["loai"] == "LAY_RA" else "Nộp vào",
            h["ket_qua"],
            h["ten_nguoi_thuc_hien"],
            h.get("ghi_chu") or ""
        ])

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    return send_file(
        stream,
        as_attachment=True,
        download_name="Bao_Cao_Giao_Nhan_Dien_Thoai.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@bao_cao_bp.route("/bao-cao/in-a4")
@yeu_cau_dang_nhap
def in_a4():
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    thong_ke = lay_thong_ke_tong_quan(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    lich_su = danh_sach_lich_su(limit=100, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    ngay_in = datetime.now().strftime("%d/%m/%Y %H:%M")
    return render_template("bao_cao/in_a4.html", thong_ke=thong_ke, lich_su=lich_su, ngay_in=ngay_in)
