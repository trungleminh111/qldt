from models.co_so_du_lieu import lay_ket_noi, tao_dieu_kien_don_vi

def lay_thong_ke_tong_quan(khoa_don_vi_gioi_han=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()

    dieu_kien_qn, params_qn = tao_dieu_kien_don_vi("qn.khoa_don_vi", khoa_don_vi_gioi_han)
    dieu_kien_dv, params_dv = tao_dieu_kien_don_vi("dv.ma_tu_sinh", khoa_don_vi_gioi_han)
    dieu_kien_raw, params_raw = tao_dieu_kien_don_vi("khoa_don_vi", khoa_don_vi_gioi_han)
    if dieu_kien_qn:
        con_tro.execute(f"SELECT COUNT(*) FROM quan_nhan WHERE da_xoa = 0 {dieu_kien_raw}", params_raw)
        tong_quan_nhan = con_tro.fetchone()[0]

        con_tro.execute(f"""
            SELECT COUNT(*)
            FROM dien_thoai dt
            JOIN quan_nhan qn ON dt.khoa_quan_nhan = qn.ma_tu_sinh
            WHERE dt.da_xoa = 0 {dieu_kien_qn}
        """, params_qn)
        tong_dien_thoai = con_tro.fetchone()[0]

        con_tro.execute(f"""
            SELECT COUNT(*)
            FROM dien_thoai dt
            JOIN quan_nhan qn ON dt.khoa_quan_nhan = qn.ma_tu_sinh
            INNER JOIN (
                SELECT gn1.khoa_dien_thoai, gn1.loai
                FROM lich_su_giao_nhan gn1
                INNER JOIN (
                    SELECT khoa_dien_thoai, MAX(ma_tu_sinh) AS max_id
                    FROM lich_su_giao_nhan
                    GROUP BY khoa_dien_thoai
                ) gn2 ON gn1.ma_tu_sinh = gn2.max_id
            ) gn ON gn.khoa_dien_thoai = dt.ma_tu_sinh
            WHERE gn.loai = 'LAY_RA' AND dt.da_xoa = 0 {dieu_kien_qn}
        """, params_qn)
        da_lay = con_tro.fetchone()[0]
        dang_trong_tu = tong_dien_thoai - da_lay

        con_tro.execute(f"""
            SELECT COUNT(*)
            FROM lich_su_giao_nhan gn
            JOIN quan_nhan qn ON gn.khoa_quan_nhan = qn.ma_tu_sinh
            WHERE gn.ket_qua = 'NGOAI_LE' {dieu_kien_qn}
        """, params_qn)
        so_ngoai_le = con_tro.fetchone()[0]

        con_tro.execute(f"""
            SELECT dv.ten_don_vi, COUNT(qn.ma_tu_sinh) AS so_quan_nhan
            FROM don_vi dv
            LEFT JOIN quan_nhan qn ON qn.khoa_don_vi = dv.ma_tu_sinh AND qn.da_xoa = 0
            WHERE dv.dang_dung = 1 {dieu_kien_dv}
            GROUP BY dv.ma_tu_sinh, dv.ten_don_vi
        """, params_dv)
        quan_so_theo_don_vi = [dict(row) for row in con_tro.fetchall()]

        con_tro.execute(f"""
            SELECT dt.hang_san_xuat, COUNT(dt.ma_tu_sinh) AS so_luong
            FROM dien_thoai dt
            JOIN quan_nhan qn ON dt.khoa_quan_nhan = qn.ma_tu_sinh
            WHERE dt.da_xoa = 0 {dieu_kien_qn}
            GROUP BY dt.hang_san_xuat
            ORDER BY so_luong DESC
        """, params_qn)
        co_cau_hang = [dict(row) for row in con_tro.fetchall()]

        con_tro.execute(f"""
            SELECT dv.ten_don_vi,
                   COUNT(qn.ma_tu_sinh) AS quan_so,
                   COUNT(dt.ma_tu_sinh) AS so_may,
                   SUM(CASE WHEN dt.ma_tu_sinh IS NOT NULL AND gn.loai = 'LAY_RA' THEN 1 ELSE 0 END) AS da_lay,
                   SUM(CASE WHEN dt.ma_tu_sinh IS NOT NULL AND (gn.loai = 'NOP_VAO' OR gn.loai IS NULL) THEN 1 ELSE 0 END) AS trong_tu
            FROM don_vi dv
            LEFT JOIN quan_nhan qn ON qn.khoa_don_vi = dv.ma_tu_sinh AND qn.da_xoa = 0
            LEFT JOIN dien_thoai dt ON dt.khoa_quan_nhan = qn.ma_tu_sinh AND dt.da_xoa = 0
            LEFT JOIN (
                SELECT gn1.khoa_dien_thoai, gn1.loai
                FROM lich_su_giao_nhan gn1
                INNER JOIN (
                    SELECT khoa_dien_thoai, MAX(ma_tu_sinh) AS max_id
                    FROM lich_su_giao_nhan
                    GROUP BY khoa_dien_thoai
                ) gn2 ON gn1.ma_tu_sinh = gn2.max_id
            ) gn ON gn.khoa_dien_thoai = dt.ma_tu_sinh
            WHERE dv.dang_dung = 1 {dieu_kien_dv}
            GROUP BY dv.ma_tu_sinh, dv.ten_don_vi
        """, params_dv)
        thong_ke_don_vi = [dict(row) for row in con_tro.fetchall()]

        con_tro.execute(f"""
            SELECT date(gn.thoi_gian) AS ngay,
                   SUM(CASE WHEN gn.loai = 'LAY_RA' THEN 1 ELSE 0 END) AS so_lay,
                   SUM(CASE WHEN gn.loai = 'NOP_VAO' THEN 1 ELSE 0 END) AS so_nop
            FROM lich_su_giao_nhan gn
            JOIN quan_nhan qn ON gn.khoa_quan_nhan = qn.ma_tu_sinh
            WHERE 1 = 1 {dieu_kien_qn}
            GROUP BY date(gn.thoi_gian)
            ORDER BY ngay DESC
            LIMIT 7
        """, params_qn)
        thong_ke_theo_ngay = [dict(row) for row in con_tro.fetchall()]
        thong_ke_theo_ngay.reverse()
    else:
        con_tro.execute("SELECT COUNT(*) FROM quan_nhan WHERE da_xoa = 0")
        tong_quan_nhan = con_tro.fetchone()[0]

        con_tro.execute("SELECT COUNT(*) FROM dien_thoai WHERE da_xoa = 0")
        tong_dien_thoai = con_tro.fetchone()[0]

        con_tro.execute("""
            SELECT COUNT(*)
            FROM dien_thoai dt
            INNER JOIN (
                SELECT gn1.khoa_dien_thoai, gn1.loai
                FROM lich_su_giao_nhan gn1
                INNER JOIN (
                    SELECT khoa_dien_thoai, MAX(ma_tu_sinh) AS max_id
                    FROM lich_su_giao_nhan
                    GROUP BY khoa_dien_thoai
                ) gn2 ON gn1.ma_tu_sinh = gn2.max_id
            ) gn ON gn.khoa_dien_thoai = dt.ma_tu_sinh
            WHERE gn.loai = 'LAY_RA' AND dt.da_xoa = 0
        """)
        da_lay = con_tro.fetchone()[0]
        dang_trong_tu = tong_dien_thoai - da_lay

        con_tro.execute("SELECT COUNT(*) FROM lich_su_giao_nhan WHERE ket_qua = 'NGOAI_LE'")
        so_ngoai_le = con_tro.fetchone()[0]

        con_tro.execute("""
            SELECT dv.ten_don_vi, COUNT(qn.ma_tu_sinh) AS so_quan_nhan
            FROM don_vi dv
            LEFT JOIN quan_nhan qn ON qn.khoa_don_vi = dv.ma_tu_sinh AND qn.da_xoa = 0
            WHERE dv.khoa_don_vi_cha IS NOT NULL AND dv.dang_dung = 1
            GROUP BY dv.ma_tu_sinh, dv.ten_don_vi, dv.thu_tu
            ORDER BY dv.thu_tu ASC
        """)
        quan_so_theo_don_vi = [dict(row) for row in con_tro.fetchall()]

        con_tro.execute("""
            SELECT dt.hang_san_xuat, COUNT(dt.ma_tu_sinh) AS so_luong
            FROM dien_thoai dt
            WHERE dt.da_xoa = 0
            GROUP BY dt.hang_san_xuat
            ORDER BY so_luong DESC
        """)
        co_cau_hang = [dict(row) for row in con_tro.fetchall()]

        con_tro.execute("""
            SELECT dv.ten_don_vi,
                   COUNT(qn.ma_tu_sinh) AS quan_so,
                   COUNT(dt.ma_tu_sinh) AS so_may,
                   SUM(CASE WHEN dt.ma_tu_sinh IS NOT NULL AND gn.loai = 'LAY_RA' THEN 1 ELSE 0 END) AS da_lay,
                   SUM(CASE WHEN dt.ma_tu_sinh IS NOT NULL AND (gn.loai = 'NOP_VAO' OR gn.loai IS NULL) THEN 1 ELSE 0 END) AS trong_tu
            FROM don_vi dv
            LEFT JOIN quan_nhan qn ON qn.khoa_don_vi = dv.ma_tu_sinh AND qn.da_xoa = 0
            LEFT JOIN dien_thoai dt ON dt.khoa_quan_nhan = qn.ma_tu_sinh AND dt.da_xoa = 0
            LEFT JOIN (
                SELECT gn1.khoa_dien_thoai, gn1.loai
                FROM lich_su_giao_nhan gn1
                INNER JOIN (
                    SELECT khoa_dien_thoai, MAX(ma_tu_sinh) AS max_id
                    FROM lich_su_giao_nhan
                    GROUP BY khoa_dien_thoai
                ) gn2 ON gn1.ma_tu_sinh = gn2.max_id
            ) gn ON gn.khoa_dien_thoai = dt.ma_tu_sinh
            WHERE dv.khoa_don_vi_cha IS NOT NULL AND dv.dang_dung = 1
            GROUP BY dv.ma_tu_sinh, dv.ten_don_vi, dv.thu_tu
            ORDER BY dv.thu_tu ASC
        """)
        thong_ke_don_vi = [dict(row) for row in con_tro.fetchall()]

        con_tro.execute("""
            SELECT date(thoi_gian) AS ngay,
                   SUM(CASE WHEN loai = 'LAY_RA' THEN 1 ELSE 0 END) AS so_lay,
                   SUM(CASE WHEN loai = 'NOP_VAO' THEN 1 ELSE 0 END) AS so_nop
            FROM lich_su_giao_nhan
            GROUP BY date(thoi_gian)
            ORDER BY ngay DESC
            LIMIT 7
        """)
        thong_ke_theo_ngay = [dict(row) for row in con_tro.fetchall()]
        thong_ke_theo_ngay.reverse()

    ket_noi.close()

    return {
        "tong_quan_nhan": tong_quan_nhan,
        "tong_dien_thoai": tong_dien_thoai,
        "dang_trong_tu": dang_trong_tu,
        "da_lay": da_lay,
        "chua_nop": da_lay,
        "so_ngoai_le": so_ngoai_le,
        "quan_so_theo_don_vi": quan_so_theo_don_vi,
        "co_cau_hang": co_cau_hang,
        "thong_ke_don_vi": thong_ke_don_vi,
        "thong_ke_theo_ngay": thong_ke_theo_ngay
    }

def lay_bao_cao_dang_ky_trong_ngay(ngay=None, khoa_don_vi_gioi_han=None):
    if not ngay:
        from datetime import datetime
        ngay = datetime.now().strftime("%Y-%m-%d")

    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()

    dieu_kien_qn, params_qn = tao_dieu_kien_don_vi("qn.khoa_don_vi", khoa_don_vi_gioi_han)

    cau_lenh = f"""
        SELECT gn.ma_tu_sinh, gn.thoi_gian, gn.loai, gn.ket_qua, gn.ghi_chu,
               qn.ma_tu_sinh AS qn_id, qn.ma_quan_nhan, qn.ho_ten,
               cb.ten_cap_bac, cv.ten_chuc_vu, dv.ten_don_vi,
               dt.ma_tu_sinh AS dt_id, dt.ma_thiet_bi, dt.ten_dien_thoai, dt.so_imei,
               ng.ma_ngan, ng.ten_ngan, t.ma_tu, t.ten_tu,
               gn.ten_nguoi_thuc_hien,
               nl.den_gio AS han_ngoai_le, nl.ly_do AS ly_do_ngoai_le
        FROM lich_su_giao_nhan gn
        JOIN quan_nhan qn ON gn.khoa_quan_nhan = qn.ma_tu_sinh
        LEFT JOIN cap_bac cb ON qn.khoa_cap_bac = cb.ma_tu_sinh
        LEFT JOIN chuc_vu cv ON qn.khoa_chuc_vu = cv.ma_tu_sinh
        LEFT JOIN don_vi dv ON qn.khoa_don_vi = dv.ma_tu_sinh
        JOIN dien_thoai dt ON gn.khoa_dien_thoai = dt.ma_tu_sinh
        LEFT JOIN ngan ng ON ng.khoa_quan_nhan = qn.ma_tu_sinh
        LEFT JOIN tu t ON ng.khoa_tu = t.ma_tu_sinh
        LEFT JOIN ngoai_le nl ON gn.khoa_ngoai_le = nl.ma_tu_sinh
        WHERE SUBSTR(gn.thoi_gian, 1, 10) = ? {dieu_kien_qn}
        ORDER BY gn.thoi_gian ASC, gn.ma_tu_sinh ASC
    """
    tham_so = [ngay] + params_qn
    con_tro.execute(cau_lenh, tham_so)
    cac_dong = [dict(r) for r in con_tro.fetchall()]

    danh_sach_phien = []
    cac_lay_ra = [d for d in cac_dong if d["loai"] == "LAY_RA"]
    cac_nop_vao = [d for d in cac_dong if d["loai"] == "NOP_VAO"]

    nop_da_dung = set()

    stt = 1
    for lr in cac_lay_ra:
        matching_nop = None
        for nv in cac_nop_vao:
            if nv["ma_tu_sinh"] not in nop_da_dung and nv["dt_id"] == lr["dt_id"] and nv["thoi_gian"] >= lr["thoi_gian"]:
                matching_nop = nv
                nop_da_dung.add(nv["ma_tu_sinh"])
                break

        gio_lay = lr["thoi_gian"][11:16] if len(lr["thoi_gian"]) >= 16 else lr["thoi_gian"]
        gio_nop = matching_nop["thoi_gian"][11:16] if matching_nop and len(matching_nop["thoi_gian"]) >= 16 else (matching_nop["thoi_gian"] if matching_nop else None)

        da_nop = matching_nop is not None
        trang_thai = "DA_NOP" if da_nop else "DANG_SU_DUNG"

        vi_tri_ngan = ""
        if lr.get("ma_tu") and (lr.get("ten_ngan") or lr.get("ma_ngan")):
            vi_tri_ngan = f"{lr['ma_tu']} - Ngăn {lr.get('ten_ngan') or lr.get('ma_ngan')}"

        danh_sach_phien.append({
            "stt": stt,
            "ma_tu_sinh": lr["ma_tu_sinh"],
            "qn_id": lr["qn_id"],
            "ma_quan_nhan": lr["ma_quan_nhan"],
            "ho_ten": lr["ho_ten"],
            "ten_cap_bac": lr.get("ten_cap_bac") or "-",
            "ten_chuc_vu": lr.get("ten_chuc_vu") or "-",
            "ten_don_vi": lr.get("ten_don_vi") or "-",
            "dt_id": lr["dt_id"],
            "ma_thiet_bi": lr["ma_thiet_bi"],
            "ten_dien_thoai": lr["ten_dien_thoai"],
            "so_imei": lr.get("so_imei") or "-",
            "vi_tri_ngan": vi_tri_ngan or "Chưa phân ngăn",
            "thoi_gian_lay": lr["thoi_gian"],
            "gio_lay": gio_lay,
            "thoi_gian_nop": matching_nop["thoi_gian"] if matching_nop else None,
            "gio_nop": gio_nop or "Chưa nộp",
            "da_nop": da_nop,
            "trang_thai": trang_thai,
            "phan_loai": lr.get("ket_qua") or "DUNG_GIO",
            "ly_do_ngoai_le": lr.get("ly_do_ngoai_le") or "",
            "han_ngoai_le": lr.get("han_ngoai_le") or "",
            "nguoi_thuc_hien": lr.get("ten_nguoi_thuc_hien") or "-",
            "ghi_chu": lr.get("ghi_chu") or (matching_nop.get("ghi_chu") if matching_nop else "")
        })
        stt += 1

    for nv in cac_nop_vao:
        if nv["ma_tu_sinh"] not in nop_da_dung:
            gio_nop = nv["thoi_gian"][11:16] if len(nv["thoi_gian"]) >= 16 else nv["thoi_gian"]
            vi_tri_ngan = ""
            if nv.get("ma_tu") and (nv.get("ten_ngan") or nv.get("ma_ngan")):
                vi_tri_ngan = f"{nv['ma_tu']} - Ngăn {nv.get('ten_ngan') or nv.get('ma_ngan')}"

            danh_sach_phien.append({
                "stt": stt,
                "ma_tu_sinh": nv["ma_tu_sinh"],
                "qn_id": nv["qn_id"],
                "ma_quan_nhan": nv["ma_quan_nhan"],
                "ho_ten": nv["ho_ten"],
                "ten_cap_bac": nv.get("ten_cap_bac") or "-",
                "ten_chuc_vu": nv.get("ten_chuc_vu") or "-",
                "ten_don_vi": nv.get("ten_don_vi") or "-",
                "dt_id": nv["dt_id"],
                "ma_thiet_bi": nv["ma_thiet_bi"],
                "ten_dien_thoai": nv["ten_dien_thoai"],
                "so_imei": nv.get("so_imei") or "-",
                "vi_tri_ngan": vi_tri_ngan or "Chưa phân ngăn",
                "thoi_gian_lay": "-",
                "gio_lay": "Trước đó",
                "thoi_gian_nop": nv["thoi_gian"],
                "gio_nop": gio_nop,
                "da_nop": True,
                "trang_thai": "DA_NOP",
                "phan_loai": nv.get("ket_qua") or "DUNG_GIO",
                "ly_do_ngoai_le": "",
                "han_ngoai_le": "",
                "nguoi_thuc_hien": nv.get("ten_nguoi_thuc_hien") or "-",
                "ghi_chu": nv.get("ghi_chu") or ""
            })
            stt += 1

    ket_noi.close()

    tong_so = len(danh_sach_phien)
    so_da_nop = sum(1 for p in danh_sach_phien if p["da_nop"])
    so_dang_su_dung = tong_so - so_da_nop
    so_ngoai_le = sum(1 for p in danh_sach_phien if p["phan_loai"] == "NGOAI_LE")

    return {
        "ngay": ngay,
        "danh_sach": danh_sach_phien,
        "tong_so": tong_so,
        "so_da_nop": so_da_nop,
        "so_dang_su_dung": so_dang_su_dung,
        "so_ngoai_le": so_ngoai_le
    }
