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
            GROUP BY dv.ma_tu_sinh
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
            GROUP BY dv.ma_tu_sinh
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
            GROUP BY dv.ma_tu_sinh
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
            GROUP BY dv.ma_tu_sinh
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