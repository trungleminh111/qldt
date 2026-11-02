from flask import Blueprint, render_template
from controllers import yeu_cau_dang_nhap, lay_don_vi_gioi_han
from models.bao_cao_model import lay_thong_ke_tong_quan
from models.giao_nhan_model import danh_sach_lich_su, danh_sach_chua_nop

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@dashboard_bp.route("/tong-quan")
@yeu_cau_dang_nhap
def tong_quan():
    khoa_don_vi_gioi_han = lay_don_vi_gioi_han()
    thong_ke = lay_thong_ke_tong_quan(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    hoat_dong_gan_day = danh_sach_lich_su(limit=5, khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)
    ds_chua_nop = danh_sach_chua_nop(khoa_don_vi_gioi_han=khoa_don_vi_gioi_han)[:4]
    return render_template(
        "dashboard/index.html",
        thong_ke=thong_ke,
        hoat_dong=hoat_dong_gan_day,
        chua_nop=ds_chua_nop
    )
