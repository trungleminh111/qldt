import json
from datetime import datetime
from models.co_so_du_lieu import lay_ket_noi

def lay_danh_sach_ca_truc():
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT * FROM ca_truc WHERE dang_dung = 1 ORDER BY gio_bat_dau ASC")
    ket_qua = [dict(row) for row in con_tro.fetchall()]
    ket_noi.close()
    return ket_qua

def lay_ca_hien_tai():
    cac_ca = lay_danh_sach_ca_truc()
    gio_hien_tai = datetime.now().strftime("%H:%M")
    ca_phu_hop = None

    for ca in cac_ca:
        bat_dau = ca["gio_bat_dau"]
        ket_thuc = ca["gio_ket_thuc"]
        if bat_dau <= ket_thuc:
            if bat_dau <= gio_hien_tai <= ket_thuc:
                ca_phu_hop = ca
                break
        else:
            if gio_hien_tai >= bat_dau or gio_hien_tai <= ket_thuc:
                ca_phu_hop = ca
                break

    if not ca_phu_hop and cac_ca:
        ca_phu_hop = cac_ca[-1]

    return ca_phu_hop

def lay_so_lieu_kiem_ke(khoa_don_vi_gioi_han=None):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()

    if khoa_don_vi_gioi_han:
        con_tro.execute("""
            SELECT COUNT(*)
            FROM dien_thoai dt
            JOIN quan_nhan qn ON dt.khoa_quan_nhan = qn.ma_tu_sinh
            WHERE dt.da_xoa = 0 AND qn.khoa_don_vi = ?
        """, (khoa_don_vi_gioi_han,))
        tong_thiet_bi = con_tro.fetchone()[0]

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

        con_tro.execute("""
            SELECT gn.thoi_gian
            FROM dien_thoai dt
            JOIN quan_nhan qn ON dt.khoa_quan_nhan = qn.ma_tu_sinh
            INNER JOIN (
                SELECT gn1.khoa_dien_thoai, gn1.loai, gn1.thoi_gian
                FROM lich_su_giao_nhan gn1
                INNER JOIN (
                    SELECT khoa_dien_thoai, MAX(ma_tu_sinh) AS max_id
                    FROM lich_su_giao_nhan
                    GROUP BY khoa_dien_thoai
                ) gn2 ON gn1.ma_tu_sinh = gn2.max_id
            ) gn ON gn.khoa_dien_thoai = dt.ma_tu_sinh
            WHERE gn.loai = 'LAY_RA' AND dt.da_xoa = 0 AND qn.khoa_don_vi = ?
        """, (khoa_don_vi_gioi_han,))
        rows = con_tro.fetchall()
    else:
        con_tro.execute("SELECT COUNT(*) FROM dien_thoai WHERE da_xoa = 0")
        tong_thiet_bi = con_tro.fetchone()[0]

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

        con_tro.execute("""
            SELECT gn.thoi_gian
            FROM dien_thoai dt
            INNER JOIN (
                SELECT gn1.khoa_dien_thoai, gn1.loai, gn1.thoi_gian
                FROM lich_su_giao_nhan gn1
                INNER JOIN (
                    SELECT khoa_dien_thoai, MAX(ma_tu_sinh) AS max_id
                    FROM lich_su_giao_nhan
                    GROUP BY khoa_dien_thoai
                ) gn2 ON gn1.ma_tu_sinh = gn2.max_id
            ) gn ON gn.khoa_dien_thoai = dt.ma_tu_sinh
            WHERE gn.loai = 'LAY_RA' AND dt.da_xoa = 0
        """)
        rows = con_tro.fetchall()

    dang_trong_tu = tong_thiet_bi - da_lay
    chua_nop = da_lay

    so_qua_han = 0
    bay_gio = datetime.now()
    for r in rows:
        tg_str = r[0] if isinstance(r, (tuple, list)) else r["thoi_gian"]
        try:
            tg = datetime.strptime(tg_str, "%Y-%m-%d %H:%M:%S")
            if (bay_gio - tg).total_seconds() > 120 * 60:
                so_qua_han += 1
        except Exception:
            pass

    ket_noi.close()
    return {
        "tong_thiet_bi": tong_thiet_bi,
        "dang_trong_tu": dang_trong_tu,
        "da_lay": da_lay,
        "chua_nop": chua_nop,
        "so_qua_han": so_qua_han,
        "bat_thuong": 0
    }

def thuc_hien_ban_giao_ca(khoa_ca, khoa_nguoi_ban_giao, khoa_nguoi_nhan, ghi_chu=None, du_lieu_snapshot=None, so_qua_han=0, khoa_don_vi_gioi_han=None, ma_tu_snapshot=None, ten_ngan_snapshot=None):
    so_lieu = lay_so_lieu_kiem_ke(khoa_don_vi_gioi_han)
    ngay_truc = datetime.now().strftime("%Y-%m-%d")

    snapshot_str = None
    if du_lieu_snapshot is not None:
        if isinstance(du_lieu_snapshot, dict):
            if not so_qua_han and "so_qua_han" in du_lieu_snapshot:
                so_qua_han = du_lieu_snapshot["so_qua_han"]
            elif not so_qua_han and "so_lieu" in du_lieu_snapshot and isinstance(du_lieu_snapshot["so_lieu"], dict):
                so_qua_han = du_lieu_snapshot["so_lieu"].get("so_qua_han", 0)
            if not ma_tu_snapshot and "ma_tu_snapshot" in du_lieu_snapshot:
                ma_tu_snapshot = du_lieu_snapshot["ma_tu_snapshot"]
            if not ten_ngan_snapshot and "ten_ngan_snapshot" in du_lieu_snapshot:
                ten_ngan_snapshot = du_lieu_snapshot["ten_ngan_snapshot"]
            snapshot_str = json.dumps(du_lieu_snapshot, ensure_ascii=False)
        elif isinstance(du_lieu_snapshot, str):
            snapshot_str = du_lieu_snapshot
            try:
                parsed = json.loads(du_lieu_snapshot)
                if isinstance(parsed, dict):
                    if not so_qua_han and "so_qua_han" in parsed:
                        so_qua_han = parsed["so_qua_han"]
                    elif not so_qua_han and "so_lieu" in parsed and isinstance(parsed["so_lieu"], dict):
                        so_qua_han = parsed["so_lieu"].get("so_qua_han", 0)
                    if not ma_tu_snapshot and "ma_tu_snapshot" in parsed:
                        ma_tu_snapshot = parsed["ma_tu_snapshot"]
                    if not ten_ngan_snapshot and "ten_ngan_snapshot" in parsed:
                        ten_ngan_snapshot = parsed["ten_ngan_snapshot"]
            except Exception:
                pass

    if not so_qua_han:
        so_qua_han = so_lieu.get("so_qua_han", 0)

    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        INSERT INTO ban_giao_ca (
            khoa_ca_truc, ngay_truc, khoa_nguoi_ban_giao, khoa_nguoi_nhan,
            tong_thiet_bi, dang_trong_tu, da_lay, chua_nop, bat_thuong, ghi_chu_ban_giao,
            du_lieu_snapshot, ma_tu_snapshot, ten_ngan_snapshot, so_qua_han
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        khoa_ca, ngay_truc, khoa_nguoi_ban_giao, khoa_nguoi_nhan,
        so_lieu["tong_thiet_bi"], so_lieu["dang_trong_tu"], so_lieu["da_lay"],
        so_lieu["chua_nop"], so_lieu["bat_thuong"], ghi_chu,
        snapshot_str, ma_tu_snapshot, ten_ngan_snapshot, so_qua_han
    ))
    id_moi = con_tro.lastrowid
    ket_noi.commit()
    ket_noi.close()
    return id_moi

def lay_chi_tiet_ban_giao(ma_bg):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        SELECT bg.*, ct.ten_ca, ct.gio_bat_dau, ct.gio_ket_thuc,
               tk1.ho_ten AS ten_nguoi_ban_giao,
               tk2.ho_ten AS ten_nguoi_nhan
        FROM ban_giao_ca bg
        JOIN ca_truc ct ON bg.khoa_ca_truc = ct.ma_tu_sinh
        JOIN tai_khoan tk1 ON bg.khoa_nguoi_ban_giao = tk1.ma_tu_sinh
        JOIN tai_khoan tk2 ON bg.khoa_nguoi_nhan = tk2.ma_tu_sinh
        WHERE bg.ma_tu_sinh = ?
    """, (ma_bg,))
    hang = con_tro.fetchone()
    ket_noi.close()
    if not hang:
        return None
    ban_giao = dict(hang)
    snapshot_raw = ban_giao.get("du_lieu_snapshot")
    if snapshot_raw:
        try:
            ban_giao["snapshot"] = json.loads(snapshot_raw)
        except Exception:
            ban_giao["snapshot"] = {}
    else:
        ban_giao["snapshot"] = {}
    return ban_giao

def lay_lich_su_ban_giao_ca(limit=10):
    ket_noi = lay_ket_noi()
    con_tro = ket_noi.cursor()
    con_tro.execute("""
        SELECT bg.*, ct.ten_ca, ct.gio_bat_dau, ct.gio_ket_thuc,
               tk1.ho_ten AS ten_nguoi_ban_giao,
               tk2.ho_ten AS ten_nguoi_nhan
        FROM ban_giao_ca bg
        JOIN ca_truc ct ON bg.khoa_ca_truc = ct.ma_tu_sinh
        JOIN tai_khoan tk1 ON bg.khoa_nguoi_ban_giao = tk1.ma_tu_sinh
        JOIN tai_khoan tk2 ON bg.khoa_nguoi_nhan = tk2.ma_tu_sinh
        ORDER BY bg.ma_tu_sinh DESC LIMIT ?
    """, (limit,))
    ket_qua = []
    for row in con_tro.fetchall():
        d = dict(row)
        snap_raw = d.get("du_lieu_snapshot")
        if snap_raw:
            try:
                d["snapshot"] = json.loads(snap_raw)
            except Exception:
                d["snapshot"] = {}
        else:
            d["snapshot"] = {}
        ket_qua.append(d)
    ket_noi.close()
    return ket_qua
