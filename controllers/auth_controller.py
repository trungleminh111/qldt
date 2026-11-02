from datetime import timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import config
from models.phan_quyen_model import xac_thuc_dang_nhap

auth_bp = Blueprint("auth", __name__)

@auth_bp.record_once
def thiet_lap_session(state):
    app = state.app
    app.config["SESSION_COOKIE_HTTPONLY"] = getattr(config, "SESSION_COOKIE_HTTPONLY", True)
    app.config["SESSION_COOKIE_SAMESITE"] = getattr(config, "SESSION_COOKIE_SAMESITE", "Lax")
    app.config["PERMANENT_SESSION_LIFETIME"] = getattr(config, "PERMANENT_SESSION_LIFETIME", timedelta(hours=8))

@auth_bp.route("/dang-nhap", methods=["GET", "POST"])
def dang_nhap():
    if "nguoi_dung" in session:
        return redirect(url_for("dashboard.tong_quan"))

    if request.method == "POST":
        ten_dang_nhap = request.form.get("ten_dang_nhap", "").strip()
        mat_khau = request.form.get("mat_khau", "").strip()

        nguoi_dung = xac_thuc_dang_nhap(ten_dang_nhap, mat_khau)
        if nguoi_dung:
            session.clear()
            session.permanent = True
            session["nguoi_dung"] = nguoi_dung
            flash(f"Đăng nhập thành công. Chào mừng {nguoi_dung['ho_ten']}.", "thanh_cong")
            return redirect(url_for("dashboard.tong_quan"))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không chính xác.", "nguy_hiem")

    return render_template("auth/login.html")

@auth_bp.route("/dang-xuat")
def dang_xuat():
    session.clear()
    flash("Đã đăng xuất khỏi hệ thống.", "thong_tin")
    return redirect(url_for("auth.dang_nhap"))

