from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from models.co_so_du_lieu import lay_ket_noi, kiem_tra_da_co_du_lieu

def ma_hoa_mat_khau(mat_khau):
    return generate_password_hash(mat_khau)


def nap_du_lieu_mau(ep_buoc=False):
    if not ep_buoc and kiem_tra_da_co_du_lieu():
        return False

    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()

    if not ep_buoc:
        con_tro.execute("SELECT COUNT(*) FROM tai_khoan")
        if con_tro.fetchone()[0] > 0:
            ket_noi.close()
            return False
        con_tro.execute("SELECT COUNT(*) FROM cap_bac")
        if con_tro.fetchone()[0] > 0:
            ket_noi.close()
            return False

    cac_cap_bac = [
        ("B2", "Binh nhì", 1),
        ("B1", "Binh nhất", 2),
        ("HS", "Hạ sĩ", 3),
        ("TS", "Trung sĩ", 4),
        ("THS", "Thượng sĩ", 5),
        ("TU", "Thiếu úy", 6),
        ("TRU", "Trung úy", 7),
        ("THU", "Thượng úy", 8),
        ("DU", "Đại úy", 9),
        ("TT", "Thiếu tá", 10),
    ]
    con_tro.executemany("INSERT INTO cap_bac (ma_cap_bac, ten_cap_bac, thu_tu) VALUES (?, ?, ?)", cac_cap_bac)

    cac_cau_hinh_gio = [
        ("GIO_CSM", "Chiến sĩ mới", "Áp dụng cho chiến sĩ mới nhập ngũ", "2026-01-01", None),
        ("GIO_HSQ_BS_N12", "HSQ, BS năm thứ nhất, năm thứ hai", "Áp dụng cho hạ sĩ quan và binh sĩ", "2026-01-01", None),
        ("GIO_SI_QUAN", "Sĩ quan, cán bộ chỉ huy", "Không giới hạn theo quy định riêng", "2026-01-01", None),
    ]
    con_tro.executemany("INSERT INTO cau_hinh_gio (ma_cau_hinh, ten_cau_hinh, mo_ta, hieu_luc_tu, hieu_luc_den) VALUES (?, ?, ?, ?, ?)", cac_cau_hinh_gio)

    con_tro.execute("SELECT ma_tu_sinh, ma_cau_hinh FROM cau_hinh_gio")
    map_ch = {row[1]: row[0] for row in con_tro.fetchall()}

    cac_khung_gio = [
        (map_ch["GIO_CSM"], 6, "20:00", "21:30", "Tối thứ Sáu"),
        (map_ch["GIO_CSM"], 7, "20:00", "21:30", "Tối thứ Bảy"),
        (map_ch["GIO_CSM"], 8, "09:00", "11:00", "Sáng Chủ Nhật"),
        (map_ch["GIO_CSM"], 8, "13:30", "15:30", "Chiều Chủ Nhật"),
        (map_ch["GIO_HSQ_BS_N12"], 6, "20:00", "21:30", "Tối thứ Sáu"),
        (map_ch["GIO_HSQ_BS_N12"], 7, "09:00", "11:00", "Sáng thứ Bảy"),
        (map_ch["GIO_HSQ_BS_N12"], 7, "13:30", "15:30", "Chiều thứ Bảy"),
        (map_ch["GIO_HSQ_BS_N12"], 7, "20:00", "21:30", "Tối thứ Bảy"),
        (map_ch["GIO_HSQ_BS_N12"], 8, "09:00", "11:00", "Sáng Chủ Nhật"),
        (map_ch["GIO_HSQ_BS_N12"], 8, "13:30", "15:30", "Chiều Chủ Nhật"),
        (map_ch["GIO_SI_QUAN"], 2, "06:00", "22:00", "Thứ Hai"),
        (map_ch["GIO_SI_QUAN"], 3, "06:00", "22:00", "Thứ Ba"),
        (map_ch["GIO_SI_QUAN"], 4, "06:00", "22:00", "Thứ Tư"),
        (map_ch["GIO_SI_QUAN"], 5, "06:00", "22:00", "Thứ Năm"),
        (map_ch["GIO_SI_QUAN"], 6, "06:00", "22:00", "Thứ Sáu"),
        (map_ch["GIO_SI_QUAN"], 7, "06:00", "22:00", "Thứ Bảy"),
        (map_ch["GIO_SI_QUAN"], 8, "06:00", "22:00", "Chủ Nhật"),
    ]
    con_tro.executemany("INSERT INTO khung_gio (khoa_cau_hinh_gio, thu_trong_tuan, gio_bat_dau, gio_ket_thuc, ghi_chu) VALUES (?, ?, ?, ?, ?)", cac_khung_gio)

    con_tro.execute("INSERT INTO don_vi (ma_don_vi, ten_don_vi, khoa_don_vi_cha, thu_tu) VALUES ('C1', 'Đại đội 1', NULL, 1)")
    ma_c1 = con_tro.lastrowid

    cac_don_vi_con = [
        ("TD1", "Trung đội 1", ma_c1, 1),
        ("TD2", "Trung đội 2", ma_c1, 2),
        ("TD3", "Trung đội 3", ma_c1, 3),
        ("HL", "Tiểu đội hỏa lực", ma_c1, 4),
    ]
    con_tro.executemany("INSERT INTO don_vi (ma_don_vi, ten_don_vi, khoa_don_vi_cha, thu_tu) VALUES (?, ?, ?, ?)", cac_don_vi_con)

    cac_chuc_vu = [
        ("DDT", "Đại đội trưởng", map_ch["GIO_SI_QUAN"], 1),
        ("CTV", "Chính trị viên", map_ch["GIO_SI_QUAN"], 2),
        ("TDT", "Trung đội trưởng", map_ch["GIO_SI_QUAN"], 3),
        ("TDT_PHO", "Phó Trung đội trưởng", map_ch["GIO_HSQ_BS_N12"], 4),
        ("TIEU_DT", "Tiểu đội trưởng", map_ch["GIO_HSQ_BS_N12"], 5),
        ("KHAU_DT", "Khẩu đội trưởng", map_ch["GIO_HSQ_BS_N12"], 6),
        ("CHIEN_SI", "Chiến sĩ", map_ch["GIO_HSQ_BS_N12"], 7),
        ("CHIEN_SI_MOI", "Chiến sĩ mới", map_ch["GIO_CSM"], 8),
        ("LIEN_LAC", "Chiến sĩ liên lạc", map_ch["GIO_HSQ_BS_N12"], 9),
    ]
    con_tro.executemany("INSERT INTO chuc_vu (ma_chuc_vu, ten_chuc_vu, khoa_cau_hinh_gio, thu_tu) VALUES (?, ?, ?, ?)", cac_chuc_vu)

    con_tro.execute("SELECT ma_tu_sinh, ma_cap_bac FROM cap_bac")
    map_cb = {row[1]: row[0] for row in con_tro.fetchall()}
    con_tro.execute("SELECT ma_tu_sinh, ma_chuc_vu FROM chuc_vu")
    map_cv = {row[1]: row[0] for row in con_tro.fetchall()}
    con_tro.execute("SELECT ma_tu_sinh, ma_don_vi FROM don_vi")
    map_dv = {row[1]: row[0] for row in con_tro.fetchall()}

    cac_tu = [
        ("T01", "Tủ Trung đội 1", "Phòng sinh hoạt Trung đội 1", 24, map_dv["TD1"]),
        ("T02", "Tủ Trung đội 2", "Phòng sinh hoạt Trung đội 2", 24, map_dv["TD2"]),
        ("T03", "Tủ Trung đội 3", "Phòng sinh hoạt Trung đội 3", 24, map_dv["TD3"]),
        ("T04", "Tủ Tiểu đội hỏa lực", "Phòng sinh hoạt Tiểu đội hỏa lực", 24, map_dv["HL"]),
    ]
    con_tro.executemany("INSERT INTO tu (ma_tu, ten_tu, vi_tri, so_ngan, khoa_don_vi_quan_ly) VALUES (?, ?, ?, ?, ?)", cac_tu)

    con_tro.execute("SELECT ma_tu_sinh, ma_tu FROM tu")
    map_tu = {row[1]: row[0] for row in con_tro.fetchall()}

    cac_ngan = []
    tien_to = {"T01": "A", "T02": "B", "T03": "C", "T04": "D"}
    for ma_tu_code, khoa_tu in map_tu.items():
        ky_tu = tien_to[ma_tu_code]
        for i in range(1, 25):
            ten_ngan = f"{ky_tu}{i:02d}"
            ma_ngan = f"{ma_tu_code}-{ten_ngan}"
            cac_ngan.append((ma_ngan, ten_ngan, khoa_tu, None))
    con_tro.executemany("INSERT INTO ngan (ma_ngan, ten_ngan, khoa_tu, khoa_quan_nhan) VALUES (?, ?, ?, ?)", cac_ngan)

    danh_sach_qn = [
        ("QN001", "Nguyễn Văn Hùng", "2001-08-12", "2021-02-08", map_cb["TS"], map_cv["TIEU_DT"], map_dv["TD1"], "Hồ sơ chính quy"),
        ("QN002", "Trần Minh Đức", "2003-05-14", "2023-02-15", map_cb["HS"], map_cv["CHIEN_SI"], map_dv["TD1"], "HSQ năm hai"),
        ("QN003", "Lê Hoàng Nam", "2004-11-20", "2024-02-10", map_cb["B1"], map_cv["CHIEN_SI"], map_dv["TD2"], "Chiến sĩ năm nhất"),
        ("QN004", "Phạm Quốc Bảo", "2004-03-08", "2024-02-10", map_cb["B1"], map_cv["CHIEN_SI"], map_dv["TD2"], "Chiến sĩ năm nhất"),
        ("QN005", "Vũ Đức Anh", "2002-09-17", "2022-02-18", map_cb["TS"], map_cv["KHAU_DT"], map_dv["HL"], "Khẩu đội trưởng cối"),
        ("QN006", "Đỗ Quang Huy", "2003-07-25", "2023-02-15", map_cb["HS"], map_cv["CHIEN_SI"], map_dv["TD3"], "Chiến sĩ trinh sát"),
        ("QN007", "Nguyễn Minh Quân", "1998-04-10", "2018-09-01", map_cb["TRU"], map_cv["TDT_PHO"], map_dv["TD1"], "Cán bộ quản lý ca trực"),
        ("QN008", "Phạm Tuấn Anh", "1999-12-05", "2019-09-01", map_cb["TU"], map_cv["TDT"], map_dv["TD2"], "Cán bộ trực ca"),
        ("QN009", "Trần Văn Bình", "1997-06-18", "2017-09-01", map_cb["THU"], map_cv["TDT"], map_dv["TD1"], "Trung đội trưởng TD1"),
        ("QN010", "Lê Văn Sơn", "1994-01-22", "2014-09-01", map_cb["DU"], map_cv["DDT"], map_dv["C1"], "Đại đội trưởng C1"),
        ("QN011", "Hoàng Văn Tuấn", "2005-02-10", "2026-02-20", map_cb["B2"], map_cv["CHIEN_SI_MOI"], map_dv["TD1"], "Chiến sĩ mới 2026"),
        ("QN012", "Nguyễn Tiến Đạt", "2003-10-30", "2023-02-15", map_cb["HS"], map_cv["CHIEN_SI"], map_dv["TD3"], "Chiến sĩ"),
    ]
    con_tro.executemany("INSERT INTO quan_nhan (ma_quan_nhan, ho_ten, ngay_sinh, ngay_nhap_ngu, khoa_cap_bac, khoa_chuc_vu, khoa_don_vi, ghi_chu) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", danh_sach_qn)

    con_tro.execute("SELECT ma_tu_sinh, ma_quan_nhan FROM quan_nhan")
    map_qn = {row[1]: row[0] for row in con_tro.fetchall()}

    gan_ngan = [
        ("T01-A01", map_qn["QN001"]),
        ("T01-A02", map_qn["QN002"]),
        ("T02-B01", map_qn["QN003"]),
        ("T02-B02", map_qn["QN004"]),
        ("T04-D01", map_qn["QN005"]),
        ("T03-C01", map_qn["QN006"]),
        ("T01-A04", map_qn["QN007"]),
        ("T02-B03", map_qn["QN008"]),
        ("T01-A05", map_qn["QN009"]),
        ("T01-A06", map_qn["QN010"]),
        ("T01-A03", map_qn["QN011"]),
        ("T03-C02", map_qn["QN012"]),
    ]
    for ma_ngan_code, khoa_qn in gan_ngan:
        con_tro.execute("UPDATE ngan SET khoa_quan_nhan = ? WHERE ma_ngan = ?", (khoa_qn, ma_ngan_code))

    danh_sach_dt = [
        ("DT001", "iPhone 13", "Apple", "iPhone 13 128GB", "356871102814829", "0981234561", map_qn["QN001"]),
        ("DT002", "Galaxy A54", "Samsung", "Galaxy A54 5G", "356921104981127", "0981234562", map_qn["QN002"]),
        ("DT003", "Reno8", "OPPO", "OPPO Reno8 Z", "864128059124018", "0981234563", map_qn["QN003"]),
        ("DT004", "Xiaomi 12", "Xiaomi", "Xiaomi 12 Pro", "867140058194012", "0981234564", map_qn["QN004"]),
        ("DT005", "iPhone 11", "Apple", "iPhone 11 64GB", "354912104819401", "0981234565", map_qn["QN005"]),
        ("DT006", "Vivo V27", "Vivo", "Vivo V27e", "862910058194025", "0981234566", map_qn["QN006"]),
        ("DT007", "iPhone 14 Pro", "Apple", "iPhone 14 Pro 256GB", "358912104819407", "0981234567", map_qn["QN007"]),
        ("DT008", "Galaxy S23", "Samsung", "Galaxy S23", "357912104819408", "0981234568", map_qn["QN008"]),
        ("DT009", "iPhone 12", "Apple", "iPhone 12", "353912104819409", "0981234569", map_qn["QN009"]),
        ("DT010", "iPhone 15 Pro", "Apple", "iPhone 15 Pro Max", "359912104819410", "0981234570", map_qn["QN010"]),
        ("DT011", "Redmi Note 13", "Xiaomi", "Redmi Note 13", "869140058194011", "0981234571", map_qn["QN011"]),
        ("DT012", "iPhone XR", "Apple", "iPhone XR 64GB", "351912104819412", "0981234572", map_qn["QN012"]),
    ]
    con_tro.executemany("INSERT INTO dien_thoai (ma_thiet_bi, ten_dien_thoai, hang_san_xuat, model, so_imei, so_dien_thoai, khoa_quan_nhan) VALUES (?, ?, ?, ?, ?, ?, ?)", danh_sach_dt)

    cac_quyen = [
        ("GIAONHAN.GHI", "GIAONHAN", "Ghi giao nhận điện thoại", "Cho phép lấy ra và nộp vào"),
        ("GIAONHAN.XEM", "GIAONHAN", "Xem lịch sử giao nhận", "Xem danh sách và nhật ký"),
        ("GIAONHAN.DIEUCHINH", "GIAONHAN", "Điều chỉnh giao nhận", "Tạo bản ghi điều chỉnh khi ghi nhầm"),
        ("NGOAILE.TAO", "NGOAILE", "Tạo đề nghị ngoại lệ", "Đăng ký sử dụng ngoài giờ"),
        ("NGOAILE.DUYET", "NGOAILE", "Duyệt đề nghị ngoại lệ", "Phê duyệt mượn khẩn cấp"),
        ("QUANNHAN.XEM", "QUANNHAN", "Xem danh sách quân nhân", "Tra cứu hồ sơ"),
        ("QUANNHAN.SUA", "QUANNHAN", "Thêm/sửa quân nhân", "Quản lý hồ sơ và Import"),
        ("DIENTHOAI.XEM", "DIENTHOAI", "Xem danh sách điện thoại", "Tra cứu thiết bị và sơ đồ tủ"),
        ("DIENTHOAI.SUA", "DIENTHOAI", "Thêm/sửa điện thoại", "Cập nhật thiết bị và gán ngăn"),
        ("CAUHINH.GIO", "CAUHINH", "Cấu hình khung giờ", "Điều chỉnh giờ sử dụng theo đối tượng"),
        ("CAUHINH.DANHMUC", "CAUHINH", "Quản lý danh mục", "Cơ cấu đơn vị, chức vụ, cấp bậc"),
        ("BAOCAO.XEM", "BAOCAO", "Xem báo cáo thống kê", "Xem số liệu tổng hợp"),
        ("BAOCAO.XUAT", "BAOCAO", "Xuất file báo cáo", "Xuất Excel và in A4"),
        ("QUANTRI.TAIKHOAN", "QUANTRI", "Quản lý tài khoản", "Tạo và phân quyền người dùng"),
    ]
    con_tro.executemany("INSERT INTO quyen_han (ma_quyen, nhom, ten_quyen, mo_ta) VALUES (?, ?, ?, ?)", cac_quyen)

    cac_vai_tro = [
        ("QUAN_TRI", "Quản trị hệ thống", "Toàn quyền quản trị phần mềm", 1),
        ("CHI_HUY", "Chỉ huy đại đội", "Theo dõi tổng thể, duyệt ngoại lệ, xem báo cáo", 1),
        ("NGUOI_TRUC", "Cán bộ trực ca", "Ghi nhận giao nhận, kiểm tủ", 1),
        ("QUAN_NHAN", "Quân nhân", "Tự xem thông tin và lịch sử của bản thân", 1),
    ]
    con_tro.executemany("INSERT INTO vai_tro (ma_vai_tro, ten_vai_tro, mo_ta, la_he_thong) VALUES (?, ?, ?, ?)", cac_vai_tro)

    con_tro.execute("SELECT ma_tu_sinh, ma_vai_tro FROM vai_tro")
    map_vt = {row[1]: row[0] for row in con_tro.fetchall()}
    con_tro.execute("SELECT ma_tu_sinh, ma_quyen FROM quyen_han")
    map_qh = {row[1]: row[0] for row in con_tro.fetchall()}

    for k_qh in map_qh.values():
        con_tro.execute("INSERT INTO vai_tro_quyen (khoa_vai_tro, khoa_quyen) VALUES (?, ?)", (map_vt["QUAN_TRI"], k_qh))

    quyen_chi_huy = ["GIAONHAN.XEM", "NGOAILE.DUYET", "QUANNHAN.XEM", "DIENTHOAI.XEM", "BAOCAO.XEM", "BAOCAO.XUAT"]
    for q in quyen_chi_huy:
        con_tro.execute("INSERT INTO vai_tro_quyen (khoa_vai_tro, khoa_quyen) VALUES (?, ?)", (map_vt["CHI_HUY"], map_qh[q]))

    quyen_nguoi_truc = ["GIAONHAN.GHI", "GIAONHAN.XEM", "NGOAILE.TAO", "QUANNHAN.XEM", "DIENTHOAI.XEM", "BAOCAO.XEM"]
    for q in quyen_nguoi_truc:
        con_tro.execute("INSERT INTO vai_tro_quyen (khoa_vai_tro, khoa_quyen) VALUES (?, ?)", (map_vt["NGUOI_TRUC"], map_qh[q]))

    cac_tai_khoan = [
        ("admin", ma_hoa_mat_khau("admin123"), "Nguyễn Minh Quân", map_qn["QN007"]),
        ("tuananh", ma_hoa_mat_khau("12345678"), "Phạm Tuấn Anh", map_qn["QN008"]),
        ("vanbinh", ma_hoa_mat_khau("12345678"), "Trần Văn Bình", map_qn["QN009"]),
        ("levanson", ma_hoa_mat_khau("12345678"), "Lê Văn Sơn", map_qn["QN010"]),
    ]
    con_tro.executemany("INSERT INTO tai_khoan (ten_dang_nhap, mat_khau_ma_hoa, ho_ten, khoa_quan_nhan) VALUES (?, ?, ?, ?)", cac_tai_khoan)

    con_tro.execute("SELECT ma_tu_sinh, ten_dang_nhap FROM tai_khoan")
    map_tk = {row[1]: row[0] for row in con_tro.fetchall()}

    con_tro.execute("INSERT INTO tai_khoan_vai_tro (khoa_tai_khoan, khoa_vai_tro, pham_vi_loai, hieu_luc_tu) VALUES (?, ?, 'TOAN_BO', '2026-01-01')", (map_tk["admin"], map_vt["QUAN_TRI"]))
    con_tro.execute("INSERT INTO tai_khoan_vai_tro (khoa_tai_khoan, khoa_vai_tro, pham_vi_loai, hieu_luc_tu) VALUES (?, ?, 'TOAN_BO', '2026-01-01')", (map_tk["levanson"], map_vt["CHI_HUY"]))
    con_tro.execute("INSERT INTO tai_khoan_vai_tro (khoa_tai_khoan, khoa_vai_tro, pham_vi_loai, hieu_luc_tu) VALUES (?, ?, 'TOAN_BO', '2026-01-01')", (map_tk["tuananh"], map_vt["NGUOI_TRUC"]))
    con_tro.execute("INSERT INTO tai_khoan_vai_tro (khoa_tai_khoan, khoa_vai_tro, pham_vi_loai, hieu_luc_tu) VALUES (?, ?, 'DON_VI', '2026-01-01')", (map_tk["vanbinh"], map_vt["NGUOI_TRUC"]))

    con_tro.execute("SELECT ma_tu_sinh, ma_thiet_bi FROM dien_thoai")
    map_dt = {row[1]: row[0] for row in con_tro.fetchall()}
    con_tro.execute("SELECT ma_tu_sinh, ma_ngan FROM ngan")
    map_ng = {row[1]: row[0] for row in con_tro.fetchall()}

    bay_gio = datetime.now()
    thoi_diem_qua = (bay_gio - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
    thoi_diem_trua = (bay_gio - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
    thoi_diem_qua_han = (bay_gio - timedelta(hours=2, minutes=35)).strftime("%Y-%m-%d %H:%M:%S")

    cac_giao_dich_ban_dau = [
        (map_qn["QN001"], map_dt["DT001"], map_ng.get("T01-A01"), thoi_diem_trua, "NOP_VAO", "DUNG_GIO", map_tk["admin"], "Nguyễn Minh Quân", "Lưu tủ đúng vị trí"),
        (map_qn["QN003"], map_dt["DT003"], map_ng.get("T02-B01"), thoi_diem_trua, "NOP_VAO", "DUNG_GIO", map_tk["admin"], "Nguyễn Minh Quân", "Lưu tủ đúng vị trí"),
        (map_qn["QN005"], map_dt["DT005"], map_ng.get("T04-D01"), thoi_diem_trua, "NOP_VAO", "DUNG_GIO", map_tk["admin"], "Nguyễn Minh Quân", "Lưu tủ đúng vị trí"),
        (map_qn["QN007"], map_dt["DT007"], map_ng.get("T01-A04"), thoi_diem_trua, "NOP_VAO", "DUNG_GIO", map_tk["admin"], "Nguyễn Minh Quân", "Lưu tủ đúng vị trí"),
        (map_qn["QN008"], map_dt["DT008"], map_ng.get("T02-B03"), thoi_diem_trua, "NOP_VAO", "DUNG_GIO", map_tk["admin"], "Nguyễn Minh Quân", "Lưu tủ đúng vị trí"),
        (map_qn["QN009"], map_dt["DT009"], map_ng.get("T01-A05"), thoi_diem_trua, "NOP_VAO", "DUNG_GIO", map_tk["admin"], "Nguyễn Minh Quân", "Lưu tủ đúng vị trí"),
        (map_qn["QN010"], map_dt["DT010"], map_ng.get("T01-A06"), thoi_diem_trua, "NOP_VAO", "DUNG_GIO", map_tk["admin"], "Nguyễn Minh Quân", "Lưu tủ đúng vị trí"),
        (map_qn["QN011"], map_dt["DT011"], map_ng.get("T01-A03"), thoi_diem_trua, "NOP_VAO", "DUNG_GIO", map_tk["admin"], "Nguyễn Minh Quân", "Lưu tủ đúng vị trí"),
        (map_qn["QN002"], map_dt["DT002"], map_ng.get("T01-A02"), thoi_diem_qua_han, "LAY_RA", "DUNG_GIO", map_tk["tuananh"], "Phạm Tuấn Anh", "Lấy điện thoại theo khung giờ"),
        (map_qn["QN004"], map_dt["DT004"], map_ng.get("T02-B02"), thoi_diem_qua_han, "LAY_RA", "DUNG_GIO", map_tk["tuananh"], "Phạm Tuấn Anh", "Lấy điện thoại theo khung giờ"),
        (map_qn["QN006"], map_dt["DT006"], map_ng.get("T03-C01"), thoi_diem_qua, "LAY_RA", "DUNG_GIO", map_tk["vanbinh"], "Trần Văn Bình", "Lấy điện thoại liên lạc"),
        (map_qn["QN012"], map_dt["DT012"], map_ng.get("T03-C02"), thoi_diem_qua, "LAY_RA", "DUNG_GIO", map_tk["vanbinh"], "Trần Văn Bình", "Lấy điện thoại"),
    ]
    con_tro.executemany("INSERT INTO lich_su_giao_nhan (khoa_quan_nhan, khoa_dien_thoai, khoa_ngan, thoi_gian, loai, ket_qua, khoa_nguoi_thuc_hien, ten_nguoi_thuc_hien, ghi_chu) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", cac_giao_dich_ban_dau)

    ket_noi.commit()
    ket_noi.close()
    return True
