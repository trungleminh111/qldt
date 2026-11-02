import os
from flask import Flask
import config
from models.co_so_du_lieu import khoi_tao_co_so_du_lieu
from models.du_lieu_mau import nap_du_lieu_mau
from controllers.auth_controller import auth_bp
from controllers.dashboard_controller import dashboard_bp
from controllers.giao_nhan_controller import giao_nhan_bp
from controllers.quan_nhan_controller import quan_nhan_bp
from controllers.dien_thoai_controller import dien_thoai_bp
from controllers.ca_truc_controller import ca_truc_bp
from controllers.cau_hinh_controller import cau_hinh_bp
from controllers.bao_cao_controller import bao_cao_bp

def tao_ung_dung():
    templates_path = os.path.join(config.BASE_DIR, "templates")
    static_path = os.path.join(config.BASE_DIR, "static")
    app = Flask(__name__, template_folder=templates_path, static_folder=static_path)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER

    khoi_tao_co_so_du_lieu()
    nap_du_lieu_mau()

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(giao_nhan_bp)
    app.register_blueprint(quan_nhan_bp)
    app.register_blueprint(dien_thoai_bp)
    app.register_blueprint(ca_truc_bp)
    app.register_blueprint(cau_hinh_bp)
    app.register_blueprint(bao_cao_bp)

    return app

app = tao_ung_dung()

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
