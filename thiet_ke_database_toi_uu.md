# THIẾT KẾ CƠ SỞ DỮ LIỆU TỐI ƯU – HỆ THỐNG QUẢN LÝ ĐIỆN THOẠI ĐẠI ĐỘI

Phiên bản: 2.0 (Tối ưu hóa cho Web Flask và Windows App .EXE)

---

## 1. MỤC TIÊU VÀ ĐIỂM TỐI ƯU SO VỚI BẢN 1.1

1. **Khả năng chạy độc lập (Self-Contained) & Đóng gói .EXE**:
   - Sử dụng SQLite làm động cơ lưu trữ chính, sẵn sàng đóng gói thành file `.exe` duy nhất không cần cài đặt thêm phần mềm máy chủ cơ sở dữ liệu.
   - Định dạng truy vấn SQL chuẩn ANSI, có thể chuyển sang PostgreSQL chỉ bằng việc thay chuỗi kết nối.
2. **Cấu hình thời gian động thông minh**:
   - Tách biệt rõ ràng: Nhóm cấu hình giờ (`cau_hinh_gio`), chi tiết các khung giờ theo thứ trong tuần (`khung_gio`), và ngày ngoại lệ đặc biệt (`ngay_dac_biet`).
   - Hàm kiểm tra giờ tự động tính toán theo chức vụ quân nhân, ngày đặc biệt, và giờ thực tế server.
3. **Phân quyền động và ca trực**:
   - Hỗ trợ gán vai trò theo thời hạn (theo ca trực) hoặc vô thời hạn.
   - Bổ sung bảng `ca_truc` và `ban_giao_ca` để hỗ trợ quy trình bàn giao số liệu giữa các ca trực theo thực tế quân đội.
4. **Hiệu năng và tính toàn vẹn**:
   - Trạng thái hiện tại của thiết bị được tính toán từ giao dịch mới nhất, ngăn ngừa lệch dữ liệu.
   - Đánh chỉ mục (Index) trên các trường tra cứu tần suất cao: mã quân nhân, mã thiết bị, thời gian giao nhận, mã tủ.

---

## 2. BẢNG TỔNG HỢP CÁC BẢNG TRONG CƠ SỞ DỮ LIỆU

| Nhóm | Tên bảng | Chức năng |
|---|---|---|
| Danh mục | `cap_bac` | Danh mục cấp bậc quân hàm (Binh nhì đến Thượng tá...) |
| Danh mục | `chuc_vu` | Danh mục chức vụ (Tiểu đội trưởng, Chiến sĩ...) gắn với cấu hình giờ |
| Danh mục | `don_vi` | Phân cấp đơn vị (Đại đội, Trung đội 1, 2, 3, Tiểu đội hỏa lực) |
| Cấu hình giờ | `cau_hinh_gio` | Tên bộ cấu hình giờ sử dụng theo nhóm đối tượng |
| Cấu hình giờ | `khung_gio` | Chi tiết giờ bắt đầu, kết thúc theo từng thứ trong tuần |
| Cấu hình giờ | `ngay_dac_biet` | Ngày lễ, Tết, cấm sử dụng hoặc ghi đè giờ |
| Quân nhân | `quan_nhan` | Hồ sơ quân nhân trong đơn vị |
| Quân nhân | `lich_su_chuc_vu`| Lịch sử điều động chức vụ của quân nhân |
| Thiết bị | `dien_thoai` | Thông tin máy, hãng, model, số IMEI, quân nhân sở hữu |
| Thiết bị | `lich_su_so_huu` | Lịch sử đổi máy, chuyển giao thiết bị |
| Tủ & Ngăn | `tu` | Danh sách tủ điện thoại (T01, T02, T03, T04) |
| Tủ & Ngăn | `ngan` | Danh sách ngăn tủ (A01..A24) gắn cố định hoặc linh hoạt với quân nhân |
| Tủ & Ngăn | `lich_su_gan_ngan`| Lịch sử phân ngăn cho quân nhân |
| Giao nhận | `lich_su_giao_nhan`| Nhật ký lấy ra, nộp vào kèm chụp lại chức vụ, khung giờ, kết quả |
| Giao nhận | `ngoai_le` | Đơn và phê duyệt mượn ngoài giờ, khẩn cấp |
| Phân quyền | `tai_khoan` | Tài khoản đăng nhập hệ thống gắn với quân nhân |
| Phân quyền | `vai_tro` | Danh mục vai trò động (Quản trị, Chỉ huy, Người trực, Quân nhân) |
| Phân quyền | `quyen_han` | Bảng các quyền hạn nguyên tử |
| Phân quyền | `vai_tro_quyen` | Bảng liên kết quyền cho từng vai trò |
| Phân quyền | `tai_khoan_vai_tro`| Gán vai trò cho tài khoản có phạm vi và thời hạn |
| Ca trực | `ca_truc` | Danh mục các ca trực trong ngày (Sáng, Chiều, Tối) |
| Ca trực | `ban_giao_ca` | Biên bản bàn giao số liệu giữa hai ca trực |
| Giám sát | `nhat_ky` | Nhật ký thao tác hệ thống (Audit log) |
| Giám sát | `vi_pham` | Ghi nhận các trường hợp quá hạn, trễ giờ, mang trái quy định |

---

## 3. THIẾT KẾ CHI TIẾT CÁC BẢNG SQL

### 3.1. Danh mục và Cấu hình giờ

```sql
CREATE TABLE cap_bac (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_cap_bac TEXT UNIQUE NOT NULL,
    ten_cap_bac TEXT NOT NULL,
    thu_tu INTEGER DEFAULT 0,
    dang_dung INTEGER DEFAULT 1
);

CREATE TABLE chuc_vu (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_chuc_vu TEXT UNIQUE NOT NULL,
    ten_chuc_vu TEXT NOT NULL,
    khoa_cau_hinh_gio INTEGER,
    thu_tu INTEGER DEFAULT 0,
    dang_dung INTEGER DEFAULT 1,
    FOREIGN KEY (khoa_cau_hinh_gio) REFERENCES cau_hinh_gio(ma_tu_sinh)
);

CREATE TABLE don_vi (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_don_vi TEXT UNIQUE NOT NULL,
    ten_don_vi TEXT NOT NULL,
    khoa_don_vi_cha INTEGER,
    thu_tu INTEGER DEFAULT 0,
    dang_dung INTEGER DEFAULT 1,
    FOREIGN KEY (khoa_don_vi_cha) REFERENCES don_vi(ma_tu_sinh)
);

CREATE TABLE cau_hinh_gio (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_cau_hinh TEXT UNIQUE NOT NULL,
    ten_cau_hinh TEXT NOT NULL,
    mo_ta TEXT,
    hieu_luc_tu TEXT NOT NULL,
    hieu_luc_den TEXT,
    dang_dung INTEGER DEFAULT 1
);

CREATE TABLE khung_gio (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    khoa_cau_hinh_gio INTEGER NOT NULL,
    thu_trong_tuan INTEGER NOT NULL,
    gio_bat_dau TEXT NOT NULL,
    gio_ket_thuc TEXT NOT NULL,
    ghi_chu TEXT,
    dang_dung INTEGER DEFAULT 1,
    FOREIGN KEY (khoa_cau_hinh_gio) REFERENCES cau_hinh_gio(ma_tu_sinh)
);

CREATE TABLE ngay_dac_biet (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    ngay TEXT NOT NULL,
    pham_vi_loai TEXT NOT NULL,
    pham_vi_khoa INTEGER,
    khoa_cau_hinh_ghi_de INTEGER,
    cam_su_dung INTEGER DEFAULT 0,
    ly_do TEXT NOT NULL,
    dang_dung INTEGER DEFAULT 1,
    FOREIGN KEY (khoa_cau_hinh_ghi_de) REFERENCES cau_hinh_gio(ma_tu_sinh)
);
```

### 3.2. Quân nhân và Thiết bị

```sql
CREATE TABLE quan_nhan (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_quan_nhan TEXT UNIQUE NOT NULL,
    ho_ten TEXT NOT NULL,
    ngay_sinh TEXT,
    ngay_nhap_ngu TEXT,
    khoa_cap_bac INTEGER NOT NULL,
    khoa_chuc_vu INTEGER NOT NULL,
    khoa_don_vi INTEGER NOT NULL,
    co_dien_thoai INTEGER DEFAULT 1,
    trang_thai TEXT DEFAULT 'DANG_PHUC_VU',
    ghi_chu TEXT,
    da_xoa INTEGER DEFAULT 0,
    ngay_tao TEXT DEFAULT (datetime('now','localtime')),
    ngay_sua TEXT,
    FOREIGN KEY (khoa_cap_bac) REFERENCES cap_bac(ma_tu_sinh),
    FOREIGN KEY (khoa_chuc_vu) REFERENCES chuc_vu(ma_tu_sinh),
    FOREIGN KEY (khoa_don_vi) REFERENCES don_vi(ma_tu_sinh)
);

CREATE TABLE dien_thoai (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_thiet_bi TEXT UNIQUE NOT NULL,
    ten_dien_thoai TEXT NOT NULL,
    hang_san_xuat TEXT,
    model TEXT,
    so_imei TEXT UNIQUE,
    so_dien_thoai TEXT,
    khoa_quan_nhan INTEGER NOT NULL,
    tinh_trang TEXT DEFAULT 'DANG_DUNG',
    ghi_chu TEXT,
    da_xoa INTEGER DEFAULT 0,
    ngay_tao TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (khoa_quan_nhan) REFERENCES quan_nhan(ma_tu_sinh)
);

CREATE TABLE tu (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_tu TEXT UNIQUE NOT NULL,
    ten_tu TEXT NOT NULL,
    vi_tri TEXT,
    so_ngan INTEGER DEFAULT 24,
    khoa_don_vi_quan_ly INTEGER,
    dang_dung INTEGER DEFAULT 1,
    FOREIGN KEY (khoa_don_vi_quan_ly) REFERENCES don_vi(ma_tu_sinh)
);

CREATE TABLE ngan (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_ngan TEXT UNIQUE NOT NULL,
    ten_ngan TEXT NOT NULL,
    khoa_tu INTEGER NOT NULL,
    khoa_quan_nhan INTEGER UNIQUE,
    dang_dung INTEGER DEFAULT 1,
    FOREIGN KEY (khoa_tu) REFERENCES tu(ma_tu_sinh),
    FOREIGN KEY (khoa_quan_nhan) REFERENCES quan_nhan(ma_tu_sinh)
);
```

### 3.3. Giao nhận và Ca trực

```sql
CREATE TABLE lich_su_giao_nhan (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    khoa_quan_nhan INTEGER NOT NULL,
    khoa_dien_thoai INTEGER NOT NULL,
    khoa_ngan INTEGER,
    thoi_gian TEXT NOT NULL,
    loai TEXT NOT NULL,
    ket_qua TEXT NOT NULL,
    khoa_khung_gio INTEGER,
    khoa_cau_hinh_gio INTEGER,
    khoa_chuc_vu INTEGER,
    khoa_ngoai_le INTEGER,
    khoa_nguoi_thuc_hien INTEGER NOT NULL,
    ten_nguoi_thuc_hien TEXT,
    ma_vai_tro TEXT,
    la_ban_ghi_dieu_chinh INTEGER DEFAULT 0,
    khoa_ban_ghi_goc INTEGER,
    ghi_chu TEXT,
    FOREIGN KEY (khoa_quan_nhan) REFERENCES quan_nhan(ma_tu_sinh),
    FOREIGN KEY (khoa_dien_thoai) REFERENCES dien_thoai(ma_tu_sinh),
    FOREIGN KEY (khoa_ngan) REFERENCES ngan(ma_tu_sinh),
    FOREIGN KEY (khoa_ngoai_le) REFERENCES ngoai_le(ma_tu_sinh)
);

CREATE TABLE ngoai_le (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    khoa_quan_nhan INTEGER NOT NULL,
    tu_gio TEXT NOT NULL,
    den_gio TEXT NOT NULL,
    loai_ngoai_le TEXT NOT NULL,
    ly_do TEXT NOT NULL,
    khoa_nguoi_de_nghi INTEGER NOT NULL,
    khoa_nguoi_duyet INTEGER,
    trang_thai TEXT DEFAULT 'CHO_DUYET',
    thoi_gian_duyet TEXT,
    ly_do_tu_choi TEXT,
    FOREIGN KEY (khoa_quan_nhan) REFERENCES quan_nhan(ma_tu_sinh)
);

CREATE TABLE ca_truc (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_ca TEXT UNIQUE NOT NULL,
    ten_ca TEXT NOT NULL,
    gio_bat_dau TEXT NOT NULL,
    gio_ket_thuc TEXT NOT NULL,
    dang_dung INTEGER DEFAULT 1
);

CREATE TABLE ban_giao_ca (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    khoa_ca_truc INTEGER NOT NULL,
    ngay_truc TEXT NOT NULL,
    khoa_nguoi_ban_giao INTEGER NOT NULL,
    khoa_nguoi_nhan INTEGER NOT NULL,
    tong_thiet_bi INTEGER DEFAULT 0,
    dang_trong_tu INTEGER DEFAULT 0,
    da_lay INTEGER DEFAULT 0,
    chua_nop INTEGER DEFAULT 0,
    bat_thuong INTEGER DEFAULT 0,
    ghi_chu_ban_giao TEXT,
    thoi_gian_ban_giao TEXT DEFAULT (datetime('now','localtime')),
    trang_thai TEXT DEFAULT 'DA_BAN_GIAO',
    FOREIGN KEY (khoa_ca_truc) REFERENCES ca_truc(ma_tu_sinh)
);
```

### 3.4. Phân quyền và Giám sát

```sql
CREATE TABLE tai_khoan (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_dang_nhap TEXT UNIQUE NOT NULL,
    mat_khau_ma_hoa TEXT NOT NULL,
    ho_ten TEXT NOT NULL,
    khoa_quan_nhan INTEGER UNIQUE,
    loai_tai_khoan TEXT DEFAULT 'NGUOI_DUNG',
    dang_dung INTEGER DEFAULT 1,
    dang_nhap_cuoi TEXT,
    ngay_tao TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (khoa_quan_nhan) REFERENCES quan_nhan(ma_tu_sinh)
);

CREATE TABLE vai_tro (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_vai_tro TEXT UNIQUE NOT NULL,
    ten_vai_tro TEXT NOT NULL,
    mo_ta TEXT,
    la_he_thong INTEGER DEFAULT 0,
    dang_dung INTEGER DEFAULT 1
);

CREATE TABLE quyen_han (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_quyen TEXT UNIQUE NOT NULL,
    nhom TEXT NOT NULL,
    ten_quyen TEXT NOT NULL,
    mo_ta TEXT
);

CREATE TABLE vai_tro_quyen (
    khoa_vai_tro INTEGER NOT NULL,
    khoa_quyen INTEGER NOT NULL,
    PRIMARY KEY (khoa_vai_tro, khoa_quyen),
    FOREIGN KEY (khoa_vai_tro) REFERENCES vai_tro(ma_tu_sinh),
    FOREIGN KEY (khoa_quyen) REFERENCES quyen_han(ma_tu_sinh)
);

CREATE TABLE tai_khoan_vai_tro (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    khoa_tai_khoan INTEGER NOT NULL,
    khoa_vai_tro INTEGER NOT NULL,
    pham_vi_loai TEXT DEFAULT 'TOAN_BO',
    pham_vi_khoa INTEGER,
    hieu_luc_tu TEXT NOT NULL,
    hieu_luc_den TEXT,
    dang_dung INTEGER DEFAULT 1,
    FOREIGN KEY (khoa_tai_khoan) REFERENCES tai_khoan(ma_tu_sinh),
    FOREIGN KEY (khoa_vai_tro) REFERENCES vai_tro(ma_tu_sinh)
);

CREATE TABLE nhat_ky (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    thoi_gian TEXT DEFAULT (datetime('now','localtime')),
    khoa_tai_khoan INTEGER,
    ten_nguoi_thao_tac TEXT,
    dia_chi_ip TEXT,
    ten_bang TEXT,
    khoa_ban_ghi INTEGER,
    hanh_dong TEXT NOT NULL,
    du_lieu_cu TEXT,
    du_lieu_moi TEXT,
    ly_do TEXT
);

CREATE TABLE vi_pham (
    ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
    khoa_quan_nhan INTEGER NOT NULL,
    khoa_giao_nhan INTEGER,
    loai TEXT NOT NULL,
    thoi_gian TEXT NOT NULL,
    noi_dung TEXT,
    trang_thai TEXT DEFAULT 'MOI',
    khoa_nguoi_xu_ly INTEGER,
    ket_qua_xu_ly TEXT,
    FOREIGN KEY (khoa_quan_nhan) REFERENCES quan_nhan(ma_tu_sinh),
    FOREIGN KEY (khoa_giao_nhan) REFERENCES lich_su_giao_nhan(ma_tu_sinh)
);
```
