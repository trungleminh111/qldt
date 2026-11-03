import threading
from datetime import datetime
from models.co_so_du_lieu import lay_ket_noi, tao_dieu_kien_don_vi
from models.cau_hinh_model import lay_mo_ta_loai_lap

_khoa_giao_nhan = threading.Lock()


def chuyen_doi_thu_tieng_viet(thu_so):
    map_thu = {
        2: "Thứ Hai",
        3: "Thứ Ba",
        4: "Thứ Tư",
        5: "Thứ Năm",
        6: "Thứ Sáu",
        7: "Thứ Bảy",
        8: "Chủ Nhật"
    }
    return map_thu.get(thu_so, "")

def kiem_tra_khung_gio(khoa_quan_nhan, thoi_diem=None):
    if thoi_diem is None:
        thoi_diem = datetime.now()
    elif isinstance(thoi_diem, str):
        try:
            thoi_diem = datetime.strptime(thoi_diem, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            thoi_diem = datetime.strptime(thoi_diem, "%Y-%m-%d %H:%M")

    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()

    con_tro.execute("""
        SELECT qn.ma_tu_sinh, qn.ho_ten, cv.ten_chuc_vu, cv.khoa_cau_hinh_gio, ch.ten_cau_hinh
        FROM quan_nhan qn
        JOIN chuc_vu cv ON qn.khoa_chuc_vu = cv.ma_tu_sinh
        LEFT JOIN cau_hinh_gio ch ON cv.khoa_cau_hinh_gio = ch.ma_tu_sinh
        WHERE qn.ma_tu_sinh = ?
    """, (khoa_quan_nhan,))
    thong_tin_qn = con_tro.fetchone()

    if not thong_tin_qn:
        ket_noi.close()
        return {"hop_le": False, "ma_trang_thai": "KHONG_TON_TAI", "thong_bao": "Không tìm thấy quân nhân", "khung_gio": []}

    khoa_ch = thong_tin_qn["khoa_cau_hinh_gio"]
    ten_doi_tuong = thong_tin_qn["ten_cau_hinh"] or "Không giới hạn"

    if not khoa_ch:
        ket_noi.close()
        return {
            "hop_le": True,
            "ma_trang_thai": "DUOC_PHEP",
            "thong_bao": "Đối tượng không giới hạn khung giờ",
            "doi_tuong": ten_doi_tuong,
            "khung_gio": [{"thu": "Tất cả các ngày", "bat_dau": "00:00", "ket_thuc": "23:59"}]
        }

    ngay_str = thoi_diem.strftime("%Y-%m-%d")
    thu_so = thoi_diem.weekday() + 2
    ngay_trong_thang = thoi_diem.day
    thang_ngay_str = thoi_diem.strftime("%m-%d")

    con_tro.execute("""
        SELECT cam_su_dung, ly_do, khoa_cau_hinh_ghi_de, ngay, loai_lap
        FROM ngay_dac_biet
        WHERE dang_dung = 1
    """)
    tat_ca_ndb = [dict(row) for row in con_tro.fetchall()]

    cac_ndb_khop = []
    for ndb in tat_ca_ndb:
        loai_lap = ndb.get("loai_lap") or "MOT_LAN"
        ref_ngay = ndb.get("ngay") or ""
        khop = False

        if loai_lap == "MOT_LAN":
            khop = (ref_ngay == ngay_str)
        elif loai_lap == "HANG_NAM":
            if len(ref_ngay) >= 10:
                khop = (ref_ngay[5:10] == thang_ngay_str)
        elif loai_lap == "HANG_THANG":
            if len(ref_ngay) >= 10:
                try:
                    ref_day = int(ref_ngay.split("-")[2])
                    khop = (ngay_trong_thang == ref_day)
                except (ValueError, IndexError):
                    pass
        elif loai_lap == "HANG_TUAN":
            if len(ref_ngay) >= 10:
                try:
                    ref_dt = datetime.strptime(ref_ngay, "%Y-%m-%d")
                    ref_thu_so = ref_dt.weekday() + 2
                    khop = (thu_so == ref_thu_so)
                except (ValueError, IndexError):
                    pass

        if khop:
            cac_ndb_khop.append(ndb)

    if cac_ndb_khop:
        ndb_cam = next((r for r in cac_ndb_khop if r.get("cam_su_dung") == 1), None)
        if ndb_cam:
            ket_noi.close()
            mo_ta = lay_mo_ta_loai_lap(ndb_cam.get("loai_lap"), ndb_cam.get("ngay"))
            return {
                "hop_le": False,
                "ma_trang_thai": "CAM_SU_DUNG",
                "thong_bao": f"Ngày đặc biệt cấm sử dụng ({mo_ta}): {ndb_cam['ly_do']}",
                "doi_tuong": ten_doi_tuong,
                "khung_gio": []
            }

        ndb_ghi_de = next((r for r in cac_ndb_khop if r.get("khoa_cau_hinh_ghi_de")), None)
        if ndb_ghi_de and ndb_ghi_de["khoa_cau_hinh_ghi_de"]:
            khoa_ch = ndb_ghi_de["khoa_cau_hinh_ghi_de"]

    thu_so = thoi_diem.weekday() + 2
    gio_phut_str = thoi_diem.strftime("%H:%M")

    con_tro.execute("""
        SELECT thu_trong_tuan, gio_bat_dau, gio_ket_thuc, ghi_chu
        FROM khung_gio
        WHERE khoa_cau_hinh_gio = ? AND dang_dung = 1
        ORDER BY thu_trong_tuan ASC, gio_bat_dau ASC
    """, (khoa_ch,))
    tat_ca_khung_gio = [
        {
            "thu_so": row["thu_trong_tuan"],
            "thu": chuyen_doi_thu_tieng_viet(row["thu_trong_tuan"]),
            "bat_dau": row["gio_bat_dau"],
            "ket_thuc": row["gio_ket_thuc"],
            "ghi_chu": row["ghi_chu"]
        }
        for row in con_tro.fetchall()
    ]

    khung_gio_hom_nay = [kg for kg in tat_ca_khung_gio if kg["thu_so"] == thu_so]
    duoc_phep = False
    khung_trung_khop = None

    for kg in khung_gio_hom_nay:
        if kg["bat_dau"] <= gio_phut_str <= kg["ket_thuc"]:
            duoc_phep = True
            khung_trung_khop = kg
            break

    ket_noi.close()

    if duoc_phep:
        return {
            "hop_le": True,
            "ma_trang_thai": "DUOC_PHEP",
            "thong_bao": f"Được phép mượn ({khung_trung_khop['bat_dau']} - {khung_trung_khop['ket_thuc']})",
            "doi_tuong": ten_doi_tuong,
            "khung_gio": tat_ca_khung_gio,
            "khung_hien_tai": khung_trung_khop
        }
    else:
        return {
            "hop_le": False,
            "ma_trang_thai": "NGOAI_KHUNG_GIO",
            "thong_bao": "Ngoài khung giờ quy định",
            "doi_tuong": ten_doi_tuong,
            "khung_gio": tat_ca_khung_gio,
            "khung_hien_tai": None
        }

def thuc_hien_lay_dien_thoai(khoa_quan_nhan, khoa_nguoi_thuc_hien, ten_nguoi_thuc_hien, thoi_gian=None, la_ngoai_le=False, ly_do=None, ghi_chu=None, han_nop=None, khoa_don_vi_gioi_han=None, khoa_nguoi_duyet=None):
    if not thoi_gian:
        thoi_gian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()

    cau_lenh_qn = """
        SELECT dt.ma_tu_sinh, ng.ma_tu_sinh AS khoa_ngan, qn.khoa_chuc_vu
        FROM quan_nhan qn
        JOIN dien_thoai dt ON dt.khoa_quan_nhan = qn.ma_tu_sinh AND dt.da_xoa = 0
        LEFT JOIN ngan ng ON ng.khoa_quan_nhan = qn.ma_tu_sinh
        WHERE qn.ma_tu_sinh = ?
    """
    tham_so_qn = [khoa_quan_nhan]
    if khoa_don_vi_gioi_han:
        dieu_kien, params = tao_dieu_kien_don_vi("qn.khoa_don_vi", khoa_don_vi_gioi_han)
        cau_lenh_qn += dieu_kien
        tham_so_qn.extend(params)

    con_tro.execute(cau_lenh_qn, tham_so_qn)
    thong_tin = con_tro.fetchone()

    if not thong_tin:
        ket_noi.close()
        return False, "Quân nhân chưa được gán thiết bị điện thoại hoặc không thuộc đơn vị quản lý."

    khoa_dt = thong_tin["ma_tu_sinh"]
    khoa_ngan = thong_tin["khoa_ngan"]
    khoa_cv = thong_tin["khoa_chuc_vu"]

    con_tro.execute("""
        SELECT loai FROM lich_su_giao_nhan
        WHERE khoa_dien_thoai = ?
        ORDER BY ma_tu_sinh DESC LIMIT 1
    """, (khoa_dt,))
    trang_thai_cuoi = con_tro.fetchone()
    if trang_thai_cuoi and trang_thai_cuoi["loai"] == "LAY_RA":
        ket_noi.close()
        return False, "Thiết bị này đang ở trạng thái ĐÃ LẤY, chưa được nộp về tủ."

    khoa_nl = None
    ket_qua = "DUNG_GIO"

    if la_ngoai_le:
        ket_qua = "NGOAI_LE"
        den_gio_val = f"{thoi_gian[:10]} {han_nop}:00" if han_nop else thoi_gian
        if khoa_nguoi_duyet:
            trang_thai_nl = "DA_DUYET"
            nguoi_duyet_id = khoa_nguoi_duyet
            tg_duyet = thoi_gian
        else:
            trang_thai_nl = "CHO_DUYET"
            nguoi_duyet_id = None
            tg_duyet = None
        con_tro.execute("""
            INSERT INTO ngoai_le (khoa_quan_nhan, tu_gio, den_gio, loai_ngoai_le, ly_do, khoa_nguoi_de_nghi, khoa_nguoi_duyet, trang_thai, thoi_gian_duyet)
            VALUES (?, ?, ?, 'KHAN_CAP', ?, ?, ?, ?, ?)
        """, (khoa_quan_nhan, thoi_gian, den_gio_val, ly_do or "Mượn ngoài giờ", khoa_nguoi_thuc_hien, nguoi_duyet_id, trang_thai_nl, tg_duyet))
        khoa_nl = con_tro.lastrowid

    con_tro.execute("""
        INSERT INTO lich_su_giao_nhan (khoa_quan_nhan, khoa_dien_thoai, khoa_ngan, thoi_gian, loai, ket_qua, khoa_chuc_vu, khoa_ngoai_le, khoa_nguoi_thuc_hien, ten_nguoi_thuc_hien, ghi_chu)
        VALUES (?, ?, ?, ?, 'LAY_RA', ?, ?, ?, ?, ?, ?)
    """, (khoa_quan_nhan, khoa_dt, khoa_ngan, thoi_gian, ket_qua, khoa_cv, khoa_nl, khoa_nguoi_thuc_hien, ten_nguoi_thuc_hien, ghi_chu))

    ket_noi.commit()
    ket_noi.close()
    return True, "Đã ghi nhận giao điện thoại thành công."

def duyet_ngoai_le(khoa_ngoai_le, khoa_nguoi_duyet, thoi_gian=None):
    if not thoi_gian:
        thoi_gian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        UPDATE ngoai_le
        SET trang_thai = 'DA_DUYET', khoa_nguoi_duyet = ?, thoi_gian_duyet = ?
        WHERE ma_tu_sinh = ?
    """, (khoa_nguoi_duyet, thoi_gian, khoa_ngoai_le))
    ket_noi.commit()
    ket_noi.close()
    return True

def thuc_hien_nop_dien_thoai(khoa_quan_nhan, khoa_nguoi_thuc_hien, ten_nguoi_thuc_hien, thoi_gian=None, ghi_chu=None, khoa_don_vi_gioi_han=None):
    if not thoi_gian:
        thoi_gian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with _khoa_giao_nhan:
        ket_noi = lay_ket_noi()
        try:
            con_tro = ket_noi.cursor()

            cau_lenh_qn = """
                SELECT dt.ma_tu_sinh, ng.ma_tu_sinh AS khoa_ngan, qn.khoa_chuc_vu
                FROM quan_nhan qn
                JOIN dien_thoai dt ON dt.khoa_quan_nhan = qn.ma_tu_sinh AND dt.da_xoa = 0
                LEFT JOIN ngan ng ON ng.khoa_quan_nhan = qn.ma_tu_sinh
                WHERE qn.ma_tu_sinh = ?
            """
            tham_so_qn = [khoa_quan_nhan]
            if khoa_don_vi_gioi_han:
                dieu_kien, params = tao_dieu_kien_don_vi("qn.khoa_don_vi", khoa_don_vi_gioi_han)
                cau_lenh_qn += dieu_kien
                tham_so_qn.extend(params)

            con_tro.execute(cau_lenh_qn, tham_so_qn)
            thong_tin = con_tro.fetchone()

            if not thong_tin:
                return False, "Không tìm thấy thiết bị của quân nhân hoặc không thuộc đơn vị quản lý."

            khoa_dt = thong_tin["ma_tu_sinh"]
            khoa_ngan = thong_tin["khoa_ngan"]
            khoa_cv = thong_tin["khoa_chuc_vu"]

            con_tro.execute("""
                SELECT loai, thoi_gian FROM lich_su_giao_nhan
                WHERE khoa_dien_thoai = ?
                ORDER BY ma_tu_sinh DESC LIMIT 1
            """, (khoa_dt,))
            trang_thai_cuoi = con_tro.fetchone()
            if not trang_thai_cuoi or trang_thai_cuoi["loai"] != "LAY_RA":
                return False, "Thiết bị này đã có trong tủ, không thể nộp tiếp."

            ket_qua = "DUNG_GIO"

            con_tro.execute("""
                INSERT INTO lich_su_giao_nhan (khoa_quan_nhan, khoa_dien_thoai, khoa_ngan, thoi_gian, loai, ket_qua, khoa_chuc_vu, khoa_nguoi_thuc_hien, ten_nguoi_thuc_hien, ghi_chu)
                VALUES (?, ?, ?, ?, 'NOP_VAO', ?, ?, ?, ?, ?)
            """, (khoa_quan_nhan, khoa_dt, khoa_ngan, thoi_gian, ket_qua, khoa_cv, khoa_nguoi_thuc_hien, ten_nguoi_thuc_hien, ghi_chu))

            ket_noi.commit()
            return True, "Đã ghi nhận nộp điện thoại về tủ thành công."
        finally:
            ket_noi.close()

def danh_sach_chua_nop(khoa_don_vi_gioi_han=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    cau_lenh = """
        SELECT qn.ma_tu_sinh AS qn_id, qn.ma_quan_nhan, qn.ho_ten, cb.ten_cap_bac, cv.ten_chuc_vu, dv.ten_don_vi,
               dt.ma_tu_sinh AS dt_id, dt.ma_thiet_bi, dt.ten_dien_thoai, dt.hang_san_xuat, dt.model,
               ng.ma_ngan, ng.ten_ngan, t.ma_tu, t.ten_tu,
               gn.thoi_gian AS gio_lay, gn.ten_nguoi_thuc_hien, gn.ket_qua, gn.ghi_chu,
               nl.den_gio AS han_ngoai_le
        FROM dien_thoai dt
        JOIN quan_nhan qn ON dt.khoa_quan_nhan = qn.ma_tu_sinh
        JOIN cap_bac cb ON qn.khoa_cap_bac = cb.ma_tu_sinh
        JOIN chuc_vu cv ON qn.khoa_chuc_vu = cv.ma_tu_sinh
        JOIN don_vi dv ON qn.khoa_don_vi = dv.ma_tu_sinh
        LEFT JOIN ngan ng ON ng.khoa_quan_nhan = qn.ma_tu_sinh
        LEFT JOIN tu t ON ng.khoa_tu = t.ma_tu_sinh
        INNER JOIN (
            SELECT gn1.khoa_dien_thoai, gn1.loai, gn1.thoi_gian, gn1.ten_nguoi_thuc_hien, gn1.ket_qua, gn1.ghi_chu, gn1.khoa_ngoai_le
            FROM lich_su_giao_nhan gn1
            INNER JOIN (
                SELECT khoa_dien_thoai, MAX(ma_tu_sinh) AS max_id
                FROM lich_su_giao_nhan
                GROUP BY khoa_dien_thoai
            ) gn2 ON gn1.ma_tu_sinh = gn2.max_id
        ) gn ON gn.khoa_dien_thoai = dt.ma_tu_sinh
        LEFT JOIN ngoai_le nl ON gn.khoa_ngoai_le = nl.ma_tu_sinh
        WHERE gn.loai = 'LAY_RA' AND dt.da_xoa = 0
    """
    tham_so = []
    if khoa_don_vi_gioi_han:
        dieu_kien, params = tao_dieu_kien_don_vi("qn.khoa_don_vi", khoa_don_vi_gioi_han)
        cau_lenh += dieu_kien
        tham_so.extend(params)
    cau_lenh += " ORDER BY gn.thoi_gian ASC"
    con_tro.execute(cau_lenh, tham_so)
    danh_sach = []
    bay_gio = datetime.now()

    for row in con_tro.fetchall():
        item = dict(row)
        try:
            thoi_gian_lay = datetime.strptime(item["gio_lay"], "%Y-%m-%d %H:%M:%S")
            phut_da_qua = int((bay_gio - thoi_gian_lay).total_seconds() / 60)
            item["phut_da_qua"] = phut_da_qua

            han_ngoai_le = item.get("han_ngoai_le")
            han_dt = None
            if han_ngoai_le:
                try:
                    han_dt = datetime.strptime(han_ngoai_le, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    try:
                        han_dt = datetime.strptime(han_ngoai_le, "%Y-%m-%d %H:%M")
                    except Exception:
                        han_dt = None

            if han_dt:
                if bay_gio > han_dt:
                    phut_qh = int((bay_gio - han_dt).total_seconds() / 60)
                    item["muc_do"] = "QUA_HAN"
                    item["nhan_trang_thai"] = f"Quá hạn ngoại lệ {phut_qh} phút"
                else:
                    phut_cl = int((han_dt - bay_gio).total_seconds() / 60)
                    item["muc_do"] = "SAP_DEN_HAN" if phut_cl <= 30 else "BINH_THUONG"
                    item["nhan_trang_thai"] = f"Còn {phut_cl} phút (ngoại lệ)"
            else:
                if phut_da_qua > 120:
                    item["muc_do"] = "QUA_HAN"
                    item["nhan_trang_thai"] = f"Quá hạn {phut_da_qua - 120} phút"
                elif phut_da_qua > 90:
                    item["muc_do"] = "SAP_DEN_HAN"
                    item["nhan_trang_thai"] = f"Còn {120 - phut_da_qua} phút"
                else:
                    item["muc_do"] = "BINH_THUONG"
                    item["nhan_trang_thai"] = "Chưa nộp"
        except Exception:
            item["phut_da_qua"] = 0
            item["muc_do"] = "BINH_THUONG"
            item["nhan_trang_thai"] = "Chưa nộp"

        danh_sach.append(item)

    ket_noi.close()
    return danh_sach

def danh_sach_lich_su(tu_khoa=None, ngay=None, loai=None, limit=100, khoa_don_vi_gioi_han=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    cau_lenh = """
        SELECT gn.ma_tu_sinh, gn.thoi_gian, gn.loai, gn.ket_qua, gn.ten_nguoi_thuc_hien, gn.ghi_chu,
               qn.ma_quan_nhan, qn.ho_ten, cb.ten_cap_bac, dv.ten_don_vi,
               dt.ma_thiet_bi, dt.ten_dien_thoai,
               ng.ma_ngan, ng.ten_ngan, t.ma_tu
        FROM lich_su_giao_nhan gn
        JOIN quan_nhan qn ON gn.khoa_quan_nhan = qn.ma_tu_sinh
        JOIN cap_bac cb ON qn.khoa_cap_bac = cb.ma_tu_sinh
        JOIN don_vi dv ON qn.khoa_don_vi = dv.ma_tu_sinh
        JOIN dien_thoai dt ON gn.khoa_dien_thoai = dt.ma_tu_sinh
        LEFT JOIN ngan ng ON gn.khoa_ngan = ng.ma_tu_sinh
        LEFT JOIN tu t ON ng.khoa_tu = t.ma_tu_sinh
        WHERE 1 = 1
    """
    tham_so = []
    if khoa_don_vi_gioi_han:
        dieu_kien, params = tao_dieu_kien_don_vi("qn.khoa_don_vi", khoa_don_vi_gioi_han)
        cau_lenh += dieu_kien
        tham_so.extend(params)
    if tu_khoa:
        cau_lenh += " AND (qn.ho_ten LIKE ? OR qn.ma_quan_nhan LIKE ? OR dt.ma_thiet_bi LIKE ?)"
        tk = f"%{tu_khoa}%"
        tham_so.extend([tk, tk, tk])
    if ngay:
        cau_lenh += " AND gn.thoi_gian LIKE ?"
        tham_so.append(f"{ngay}%")
    if loai and loai != "TAT_CA":
        cau_lenh += " AND gn.loai = ?"
        tham_so.append(loai)

    cau_lenh += " ORDER BY gn.ma_tu_sinh DESC LIMIT ?"
    tham_so.append(limit)

    con_tro.execute(cau_lenh, tham_so)
    ket_qua = [dict(row) for row in con_tro.fetchall()]
    ket_noi.close()
    return ket_qua
