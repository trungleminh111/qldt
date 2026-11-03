import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from controllers import yeu_cau_dang_nhap, yeu_cau_quyen, lay_don_vi_gioi_han
from models.ca_truc_model import (
    lay_danh_sach_ca_truc,
    lay_ca_hien_tai,
    lay_so_lieu_kiem_ke,
    thuc_hien_ban_giao_ca,
    lay_lich_su_ban_giao_ca,
    lay_chi_tiet_ban_giao
)
from models.phan_quyen_model import lay_tat_ca_tai_khoan, lay_chi_tiet_tai_khoan
from models.giao_nhan_model import danh_sach_chua_nop, thuc_hien_nop_dien_thoai
from models.co_so_du_lieu import ghi_nhat_ky

ca_truc_bp = Blueprint("ca_truc", __name__)

@ca_truc_bp.route("/ban-giao-ca")
@ca_truc_bp.route("/ca-truc")
@yeu_cau_dang_nhap
@yeu_cau_quyen("CATRUC.BANGIAO")
def ban_giao():
    don_vi_gioi_han = lay_don_vi_gioi_han()
    ca_hien_tai = lay_ca_hien_tai()
    cac_ca = lay_danh_sach_ca_truc()
    so_lieu = lay_so_lieu_kiem_ke(khoa_don_vi_gioi_han=don_vi_gioi_han)
    lich_su = lay_lich_su_ban_giao_ca()
    all_tk = lay_tat_ca_tai_khoan()
    tai_khoan_list = [tk for tk in all_tk if tk.get("dang_dung") == 1]
    chua_nop_list = danh_sach_chua_nop(khoa_don_vi_gioi_han=don_vi_gioi_han)
    nguoi_dung_hien_tai = session.get("nguoi_dung", {})
    vua_ban_giao_id = session.pop("vua_ban_giao_id", None)

    return render_template(
        "ca_truc/index.html",
        ca_hien_tai=ca_hien_tai,
        cac_ca=cac_ca,
        so_lieu=so_lieu,
        lich_su=lich_su,
        tai_khoan_list=tai_khoan_list,
        nguoi_dung=nguoi_dung_hien_tai,
        chua_nop_list=chua_nop_list,
        vua_ban_giao_id=vua_ban_giao_id
    )

@ca_truc_bp.route("/ca-truc/xac-nhan", methods=["POST"])
@yeu_cau_dang_nhap
@yeu_cau_quyen("CATRUC.BANGIAO")
def xac_nhan_ban_giao():
    khoa_ca = request.form.get("khoa_ca")
    khoa_nguoi_nhan = request.form.get("khoa_nguoi_nhan")
    ghi_chu = request.form.get("ghi_chu", "").strip()

    nguoi_dung = session.get("nguoi_dung", {})
    khoa_nguoi_ban_giao = nguoi_dung.get("ma_tu_sinh", 1)

    if not khoa_ca or not khoa_nguoi_nhan:
        flash("Vui lòng chọn ca trực và cán bộ nhận ca.", "canh_bao")
        return redirect(url_for("ca_truc.ban_giao"))

    don_vi_gioi_han = lay_don_vi_gioi_han()
    so_lieu = lay_so_lieu_kiem_ke(khoa_don_vi_gioi_han=don_vi_gioi_han)
    chua_nop_list = danh_sach_chua_nop(khoa_don_vi_gioi_han=don_vi_gioi_han)
    cac_ca = lay_danh_sach_ca_truc()
    ca_chon = next((c for c in cac_ca if str(c.get("ma_tu_sinh")) == str(khoa_ca)), None)
    tk_nhan = lay_chi_tiet_tai_khoan(khoa_nguoi_nhan)

    so_qua_han = sum(1 for x in chua_nop_list if x.get("muc_do") == "QUA_HAN")
    ma_tu_set = sorted(list(set(x.get("ma_tu") for x in chua_nop_list if x.get("ma_tu"))))
    ma_tu_snapshot = ", ".join(ma_tu_set) if ma_tu_set else "T01"
    ten_ngan_set = sorted(list(set(x.get("ten_ngan") for x in chua_nop_list if x.get("ten_ngan"))))
    ten_ngan_snapshot = ", ".join(ten_ngan_set) if ten_ngan_set else ""

    snapshot_dict = {
        "thoi_diem_ban_giao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ca_truc": {
            "ma_tu_sinh": ca_chon.get("ma_tu_sinh") if ca_chon else khoa_ca,
            "ma_ca": ca_chon.get("ma_ca", "") if ca_chon else "",
            "ten_ca": ca_chon.get("ten_ca", "") if ca_chon else "",
            "gio_bat_dau": ca_chon.get("gio_bat_dau", "") if ca_chon else "",
            "gio_ket_thuc": ca_chon.get("gio_ket_thuc", "") if ca_chon else ""
        },
        "can_bo_ban_giao": {
            "ma_tai_khoan": nguoi_dung.get("ma_tu_sinh"),
            "ho_ten": nguoi_dung.get("ho_ten"),
            "ten_vai_tro": nguoi_dung.get("ten_vai_tro") or nguoi_dung.get("ma_vai_tro")
        },
        "can_bo_tiep_nhan": {
            "ma_tai_khoan": tk_nhan.get("ma_tu_sinh") if tk_nhan else khoa_nguoi_nhan,
            "ho_ten": tk_nhan.get("ho_ten", "") if tk_nhan else "",
            "ten_vai_tro": tk_nhan.get("ten_vai_tro", "") if tk_nhan else ""
        },
        "so_lieu": {
            "tong_thiet_bi": so_lieu.get("tong_thiet_bi", 0),
            "dang_trong_tu": so_lieu.get("dang_trong_tu", 0),
            "da_lay": so_lieu.get("da_lay", 0),
            "chua_nop": so_lieu.get("chua_nop", 0),
            "so_qua_han": so_qua_han,
            "bat_thuong": int(request.form.get("bat_thuong", 0) or 0)
        },
        "danh_sach_chua_nop": [
            {
                "ma_quan_nhan": item.get("ma_quan_nhan", ""),
                "ho_ten": item.get("ho_ten", ""),
                "ten_cap_bac": item.get("ten_cap_bac", ""),
                "ten_chuc_vu": item.get("ten_chuc_vu", ""),
                "ten_don_vi": item.get("ten_don_vi", ""),
                "ma_thiet_bi": item.get("ma_thiet_bi", ""),
                "ten_dien_thoai": item.get("ten_dien_thoai", ""),
                "model": item.get("model", ""),
                "ma_ngan": item.get("ma_ngan", ""),
                "ten_ngan": item.get("ten_ngan", ""),
                "ma_tu": item.get("ma_tu", ""),
                "ten_tu": item.get("ten_tu", ""),
                "vi_tri_ngan": item.get("ten_ngan") or item.get("ma_ngan", ""),
                "gio_lay": item.get("gio_lay", ""),
                "phut_da_qua": item.get("phut_da_qua", 0),
                "muc_do": item.get("muc_do", "BINH_THUONG"),
                "nhan_trang_thai": item.get("nhan_trang_thai", "")
            }
            for item in chua_nop_list
        ],
        "kiem_tra_thuc_te": {
            "da_kiem_dem_tu": True,
            "da_kiem_tra_khoa_niemphong": True,
            "da_giao_chia_khoa": True
        },
        "ghi_chu": ghi_chu
    }

    snapshot_json = json.dumps(snapshot_dict, ensure_ascii=False)

    try:
        id_moi = thuc_hien_ban_giao_ca(
            khoa_ca=khoa_ca,
            khoa_nguoi_ban_giao=khoa_nguoi_ban_giao,
            khoa_nguoi_nhan=khoa_nguoi_nhan,
            ghi_chu=ghi_chu,
            du_lieu_snapshot=snapshot_json,
            so_qua_han=so_qua_han,
            khoa_don_vi_gioi_han=don_vi_gioi_han,
            ma_tu_snapshot=ma_tu_snapshot,
            ten_ngan_snapshot=ten_ngan_snapshot,
            bat_thuong=int(request.form.get("bat_thuong", 0) or 0)
        )
        ghi_nhat_ky(
            khoa_tai_khoan=nguoi_dung.get("ma_tu_sinh"),
            ten_nguoi_thao_tac=nguoi_dung.get("ho_ten"),
            dia_chi_ip=request.remote_addr,
            ten_bang="ban_giao_ca",
            khoa_ban_ghi=id_moi,
            hanh_dong="BAN_GIAO_CA",
            du_lieu_moi=snapshot_json,
            ly_do=ghi_chu
        )
        session["vua_ban_giao_id"] = id_moi
        flash("Đã hoàn tất bàn giao ca trực và khóa số liệu thành công.", "thanh_cong")
        if request.form.get("in_bien_ban") == "1":
            return redirect(url_for("ca_truc.bien_ban", id=id_moi))
    except Exception as e:
        flash(f"Lỗi khi bàn giao ca: {str(e)}", "nguy_hiem")

    return redirect(url_for("ca_truc.ban_giao"))

@ca_truc_bp.route("/ca-truc/bien-ban/<int:id>")
@yeu_cau_dang_nhap
@yeu_cau_quyen("CATRUC.BANGIAO")
def bien_ban(id):
    ban_giao = lay_chi_tiet_ban_giao(id)
    if not ban_giao:
        flash("Không tìm thấy biên bản bàn giao ca trực.", "canh_bao")
        return redirect(url_for("ca_truc.ban_giao"))
    snapshot = ban_giao.get("snapshot") or {}
    return render_template("ca_truc/bien_ban.html", ban_giao=ban_giao, snapshot=snapshot)

@ca_truc_bp.route("/ca-truc/api/chi-tiet/<int:id>")
@yeu_cau_dang_nhap
@yeu_cau_quyen("CATRUC.BANGIAO")
def api_chi_tiet(id):
    ban_giao = lay_chi_tiet_ban_giao(id)
    if not ban_giao:
        return jsonify({"thanh_cong": False, "thong_bao": "Không tìm thấy biên bản bàn giao."}), 404
    return jsonify({"thanh_cong": True, "ban_giao": ban_giao, "snapshot": ban_giao.get("snapshot", {})})

@ca_truc_bp.route("/ca-truc/thu-hoi-nhanh", methods=["POST"])
@ca_truc_bp.route("/api/ca-truc/thu-hoi-nhanh", methods=["POST"])
@yeu_cau_dang_nhap
@yeu_cau_quyen("CATRUC.BANGIAO")
def thu_hoi_nhanh():
    if request.is_json:
        data = request.get_json() or {}
        khoa_qn = data.get("khoa_quan_nhan") or data.get("khoa_qn")
        ghi_chu = data.get("ghi_chu", "Thu hồi nhanh trong ca trực")
    else:
        khoa_qn = request.form.get("khoa_quan_nhan") or request.form.get("khoa_qn")
        ghi_chu = request.form.get("ghi_chu", "Thu hồi nhanh trong ca trực")

    if not khoa_qn:
        if request.is_json:
            return jsonify({"thanh_cong": False, "thong_bao": "Vui lòng chọn quân nhân cần thu hồi máy."}), 400
        flash("Vui lòng chọn quân nhân cần thu hồi máy.", "canh_bao")
        return redirect(url_for("ca_truc.ban_giao"))

    don_vi_gioi_han = lay_don_vi_gioi_han()
    nguoi_dung = session.get("nguoi_dung", {})
    khoa_nguoi_thuc_hien = nguoi_dung.get("ma_tu_sinh", 1)
    ten_nguoi_thuc_hien = nguoi_dung.get("ho_ten", "Cán bộ trực ca")

    thanh_cong, thong_bao = thuc_hien_nop_dien_thoai(
        khoa_quan_nhan=khoa_qn,
        khoa_nguoi_thuc_hien=khoa_nguoi_thuc_hien,
        ten_nguoi_thuc_hien=ten_nguoi_thuc_hien,
        ghi_chu=ghi_chu,
        khoa_don_vi_gioi_han=don_vi_gioi_han
    )

    if request.is_json:
        return jsonify({"thanh_cong": thanh_cong, "thong_bao": thong_bao}), (200 if thanh_cong else 400)

    flash(thong_bao, "thanh_cong" if thanh_cong else "nguy_hiem")
    return redirect(url_for("ca_truc.ban_giao"))
