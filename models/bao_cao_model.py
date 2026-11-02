from models.co_so_du_lieu import lay_ket_noi

def lay_thong_ke_tong_quan(khoa_don_vi_gioi_han=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()

    if khoa_don_vi_gioi_han:
        con_tro.execute("SELECT COUNT(*) FROM quan_nhan WHERE da_xoa = 0 AND khoa_don_vi = ?", (khoa_don_vi_gioi_han,))
        tong_quan_nhan = con_tro.fetchone()[0]

        con_tro.execute("""
            SELECT COUNT(*)
            FROM dien_thoai dt
            JOIN quan_nhan qn ON dt.khoa_quan_nhan = qn.ma_tu_sinh
            WHERE dt.da_xoa = 0 AND qn.khoa_don_vi = ?
        """, (khoa_don_vi_gioi_han,))
        tong_dien_thoai = con_tro.fetchone()[0]

        con_tro.execute("""
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
            WHERE gn.loai = 'LAY_RA' AND dt.da_xoa = 0 AND qn.khoa_don_vi = ?
        """, (khoa_don_vi_gioi_han,))
        da_lay = con_tro.fetchone()[0]
        dang_trong_tu = tong_dien_thoai - da_lay

        con_tro.execute("""
            SELECT COUNT(*)
            FROM lich_su_giao_nhan gn
            JOIN quan_nhan qn ON gn.khoa_quan_nhan = qn.ma_tu_sinh
            WHERE gn.ket_qua = 'NGOAI_LE' AND qn.khoa_don_vi = ?
        """, (khoa_don_vi_gioi_han,))
        so_ngoai_le = con_tro.fetchone()[0]

        con_tro.execute("""
            SELECT dv.ten_don_vi, COUNT(qn.ma_tu_sinh) AS so_quan_nhan
            FROM don_vi dv
            LEFT JOIN quan_nhan qn ON qn.khoa_don_vi = dv.ma_tu_sinh AND qn.da_xoa = 0
            WHERE dv.ma_tu_sinh = ? AND dv.dang_dung = 1
            GROUP BY dv.ma_tu_sinh
        """, (khoa_don_vi_gioi_han,))
        quan_so_theo_don_vi = [dict(row) for row in con_tro.fetchall()]

        con_tro.execute("""
            SELECT dt.hang_san_xuat, COUNT(dt.ma_tu_sinh) AS so_luong
            FROM dien_thoai dt
            JOIN quan_nhan qn ON dt.khoa_quan_nhan = qn.ma_tu_sinh
            WHERE dt.da_xoa = 0 AND qn.khoa_don_vi = ?
            GROUP BY dt.hang_san_xuat
            ORDER BY so_luong DESC
        """, (khoa_don_vi_gioi_han,))
        co_cau_hang = [dict(row) for row in con_tro.fetchall()]

        con_tro.execute("""
            SELECT dv.ten_don_vi,
                   COUNT(qn.ma_tu_sinh) AS quan_so,
                   COUNT(dt.ma_tu_sinh) AS so_may,
                   SUM(CASE WHEN gn.loai = 'LAY_RA' THEN 1 ELSE 0 END) AS da_lay,
                   SUM(CASE WHEN gn.loai = 'NOP_VAO' OR gn.loai IS NULL THEN 1 ELSE 0 END) AS trong_tu
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
            WHERE dv.ma_tu_sinh = ? AND dv.dang_dung = 1
            GROUP BY dv.ma_tu_sinh
        """, (khoa_don_vi_gioi_han,))
        thong_ke_don_vi = [dict(row) for row in con_tro.fetchall()]

        con_tro.execute("""
            SELECT date(gn.thoi_gian) AS ngay,
                   SUM(CASE WHEN gn.loai = 'LAY_RA' THEN 1 ELSE 0 END) AS so_lay,
                   SUM(CASE WHEN gn.loai = 'NOP_VAO' THEN 1 ELSE 0 END) AS so_nop
            FROM lich_su_giao_nhan gn
            JOIN quan_nhan qn ON gn.khoa_quan_nhan = qn.ma_tu_sinh
            WHERE qn.khoa_don_vi = ?
            GROUP BY date(gn.thoi_gian)
            ORDER BY ngay DESC
            LIMIT 7
        """, (khoa_don_vi_gioi_han,))
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
                   SUM(CASE WHEN gn.loai = 'LAY_RA' THEN 1 ELSE 0 END) AS da_lay,
                   SUM(CASE WHEN gn.loai = 'NOP_VAO' OR gn.loai IS NULL THEN 1 ELSE 0 END) AS trong_tu
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