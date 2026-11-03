import os
import mimetypes
from flask import Flask, request
import config
from models.co_so_du_lieu import khoi_tao_co_so_du_lieu, kiem_tra_da_co_du_lieu
from models.du_lieu_mau import nap_du_lieu_mau
from controllers.auth_controller import auth_bp
from controllers.dashboard_controller import dashboard_bp
from controllers.giao_nhan_controller import giao_nhan_bp
from controllers.quan_nhan_controller import quan_nhan_bp
from controllers.dien_thoai_controller import dien_thoai_bp
from controllers.cau_hinh_controller import cau_hinh_bp
from controllers.bao_cao_controller import bao_cao_bp

mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")

def tao_ung_dung():
    templates_path = os.path.join(config.RESOURCE_DIR, "templates")
    static_path = os.path.join(config.RESOURCE_DIR, "static")
    app = Flask(__name__, template_folder=templates_path, static_folder=static_path)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER

    khoi_tao_co_so_du_lieu()
    if not kiem_tra_da_co_du_lieu():
        nap_du_lieu_mau()

    @app.after_request
    def xu_ly_phan_hoi(phan_hoi):
        if request.path.endswith(".css"):
            phan_hoi.headers["Content-Type"] = "text/css; charset=utf-8"
        elif request.path.endswith(".js"):
            phan_hoi.headers["Content-Type"] = "application/javascript; charset=utf-8"
        if not request.path.startswith("/static/"):
            phan_hoi.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
            phan_hoi.headers["Pragma"] = "no-cache"
            phan_hoi.headers["Expires"] = "0"
        return phan_hoi

    @app.context_processor
    def tiem_thong_tin_don_vi():
        from models.cau_hinh_model import lay_thong_tin_don_vi
        try:
            return {"thong_tin_don_vi": lay_thong_tin_don_vi()}
        except Exception:
            return {
                "thong_tin_don_vi": {
                    "don_vi_cap_tren": "TIỂU ĐOÀN 3",
                    "ten_don_vi": "ĐẠI ĐỘI 11",
                    "dia_diem": "Đà Nẵng",
                    "can_cu_quy_dinh": "Quy định số 763/QyĐ-SĐ ngày 12/3/2026 của Sư đoàn về việc quản lý, sử dụng thiết bị điện tử trong đơn vị",
                    "chuc_danh_chi_huy": "CHỈ HUY ĐẠI ĐỘI",
                    "noi_nhan": "- CH/d (để theo dõi);\n- Lưu: c."
                }
            }

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(giao_nhan_bp)
    app.register_blueprint(quan_nhan_bp)
    app.register_blueprint(dien_thoai_bp)
    app.register_blueprint(cau_hinh_bp)
    app.register_blueprint(bao_cao_bp)

    return app

app = tao_ung_dung()

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
