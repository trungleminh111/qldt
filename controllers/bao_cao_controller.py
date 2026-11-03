from datetime import datetime
from io import BytesIO
import openpyxl
from flask import Blueprint, render_template, request, send_file
from controllers import yeu_cau_dang_nhap, yeu_cau_quyen, lay_don_vi_gioi_han
from models.bao_cao_model import lay_thong_ke_tong_quan, lay_bao_cao_dang_ky_trong_ngay
from models.giao_nhan_model import danh_sach_lich_su

bao_cao_bp = Blueprint("bao_cao", __name__)

@bao_cao_bp.route("/bao-cao")
@yeu_cau_dang_nhap
@yeu_cau_quyen("BAOCAO.XEM")
def index():
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    thong_ke = lay_thong_ke_tong_quan(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    lich_su = danh_sach_lich_su(limit=50, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    ngay_chon = request.args.get("ngay") or datetime.now().strftime("%Y-%m-%d")
    bao_cao_ngay = lay_bao_cao_dang_ky_trong_ngay(ngay=ngay_chon, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    return render_template(
        "bao_cao/index.html",
        thong_ke=thong_ke,
        lich_su=lich_su,
        bao_cao_ngay=bao_cao_ngay,
        ngay_chon=ngay_chon
    )

@bao_cao_bp.route("/bao-cao/xuat-excel")
@yeu_cau_dang_nhap
@yeu_cau_quyen("BAOCAO.XUAT", "BAOCAO.XEM")
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
@yeu_cau_quyen("BAOCAO.XEM", "BAOCAO.XUAT")
def in_a4():
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    thong_ke = lay_thong_ke_tong_quan(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    lich_su = danh_sach_lich_su(limit=100, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    ngay_in = datetime.now().strftime("%d/%m/%Y %H:%M")
    return render_template("bao_cao/in_a4.html", thong_ke=thong_ke, lich_su=lich_su, ngay_in=ngay_in)

@bao_cao_bp.route("/bao-cao/in-ngay")
@yeu_cau_dang_nhap
@yeu_cau_quyen("BAOCAO.XEM", "BAOCAO.XUAT")
def in_ngay():
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    ngay_chon = request.args.get("ngay") or datetime.now().strftime("%Y-%m-%d")
    bao_cao_ngay = lay_bao_cao_dang_ky_trong_ngay(ngay=ngay_chon, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    try:
        dt_obj = datetime.strptime(ngay_chon, "%Y-%m-%d")
        ngay_in_chu = f"ngày {dt_obj.day:02d} tháng {dt_obj.month:02d} năm {dt_obj.year}"
    except Exception:
        ngay_in_chu = f"ngày {ngay_chon}"
    thoi_diem_in = datetime.now().strftime("%d/%m/%Y %H:%M")
    return render_template(
        "bao_cao/in_ngay_a4.html",
        bao_cao=bao_cao_ngay,
        ngay_chon=ngay_chon,
        ngay_in_chu=ngay_in_chu,
        thoi_diem_in=thoi_diem_in
    )

@bao_cao_bp.route("/bao-cao/xuat-excel-ngay")
@yeu_cau_dang_nhap
@yeu_cau_quyen("BAOCAO.XUAT", "BAOCAO.XEM")
def xuat_excel_ngay():
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    ngay_chon = request.args.get("ngay") or datetime.now().strftime("%Y-%m-%d")
    bao_cao_ngay = lay_bao_cao_dang_ky_trong_ngay(ngay=ngay_chon, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "BaoCaoNgay"

    ws.append([f"BÁO CÁO TỔNG HỢP ĐĂNG KÝ SỬ DỤNG ĐIỆN THOẠI TRONG NGÀY {ngay_chon}"])
    ws.append([])
    ws.append([
        "Tổng lượt đăng ký", bao_cao_ngay["tong_so"],
        "Đã hoàn trả tủ", bao_cao_ngay["so_da_nop"],
        "Đang giữ sử dụng", bao_cao_ngay["so_dang_su_dung"],
        "Mượn ngoại lệ", bao_cao_ngay["so_ngoai_le"]
    ])
    ws.append([])

    tieu_de = [
        "STT", "Họ và tên", "Mã quân nhân", "Cấp bậc", "Chức vụ", "Đơn vị",
        "Mã thiết bị", "Tên máy", "Số IMEI", "Tủ / Ngăn",
        "Giờ lấy", "Giờ nộp", "Phân loại", "Trạng thái",
        "Cán bộ trực ca", "Ghi chú"
    ]
    ws.append(tieu_de)

    for p in bao_cao_ngay["danh_sach"]:
        ws.append([
            p["stt"],
            p["ho_ten"],
            p["ma_quan_nhan"],
            p["ten_cap_bac"],
            p["ten_chuc_vu"],
            p["ten_don_vi"],
            p["ma_thiet_bi"],
            p["ten_dien_thoai"],
            p["so_imei"],
            p["vi_tri_ngan"],
            p["gio_lay"],
            p["gio_nop"],
            "Đúng giờ" if p["phan_loai"] == "DUNG_GIO" else "Ngoại lệ",
            "Đã nộp" if p["da_nop"] else "Đang sử dụng",
            p["nguoi_thuc_hien"],
            p["ghi_chu"]
        ])

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    return send_file(
        stream,
        as_attachment=True,
        download_name=f"Bao_Cao_Dang_Ky_Su_Dung_Dien_Thoai_{ngay_chon}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
