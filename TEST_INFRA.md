# Kiến trúc và Hạ tầng Kiểm thử Tự động E2E (TEST_INFRA)

## 1. Triết lý Kiểm thử (Test Philosophy)

Hệ thống kiểm thử cho phần mềm Quản lý điện thoại đại đội (QLDT) được xây dựng theo nguyên tắc kiểm thử hộp đen mờ (opaque-box testing), độc lập hoàn toàn với cấu trúc cài đặt nội bộ và bám sát trực tiếp các yêu cầu quân sự thực tế tại `ORIGINAL_REQUEST.md` và `PROJECT.md`.

### 1.1. Bốn tầng kiểm thử (4-Tier Architecture)
1. **Tier 1 - Feature Coverage (Bao phủ chức năng cơ bản, >= 5 ca kiểm thử mỗi nhóm chức năng)**:
   - Xác thực đăng nhập/đăng xuất và quản lý phiên.
   - Quản lý hồ sơ quân nhân (CRUD, tra cứu, xóa mềm an toàn).
   - Quản lý thiết bị điện thoại và sơ đồ tủ 24 ngăn.
   - Giao nhận máy hàng ngày, kiểm tra khung giờ và danh sách chưa nộp.
   - Quản lý ca trực, bàn giao ca và xuất báo cáo (Excel, biểu mẫu in A4).
2. **Tier 2 - Boundary & Corner Cases (Biên giới hạn và tình huống góc cạnh, >= 5 ca kiểm thử mỗi nhóm)**:
   - Giá trị rỗng ở các trường bắt buộc.
   - Giá trị cực đại và độ dài chuỗi biên (tên 200+ ký tự, model cực dài).
   - Ràng buộc trùng lặp dữ liệu (trùng IMEI, trùng mã quân nhân, trùng tên đăng nhập).
   - Định danh không tồn tại trên đường dẫn URL (ID 999999).
   - Biên thời gian khung giờ (giờ bắt đầu lớn hơn hoặc bằng giờ kết thúc).
   - Ký tự đặc biệt, dấu nháy, mã HTML/JS, payload SQL/XSS bảo đảm an toàn dữ liệu.
3. **Tier 3 - Security & Cross-Role Combinations (Bảo mật, phân quyền chéo và cô lập phạm vi)**:
   - Chặn truy cập trái phép khi chưa xác thực (Unauthenticated redirect).
   - Chống tấn công cố định phiên (Session Fixation Prevention qua `session.clear()`).
   - Kiểm soát quyền RBAC: người trực/quân nhân bị chặn khi truy cập trang cấu hình và tài khoản.
   - Bất khả xâm phạm tài khoản Quản trị tối cao (`admin`): cấp dưới không thể xóa hoặc đổi mật khẩu.
   - Cô lập dữ liệu ngang (`pham_vi_loai == 'DON_VI'`): Cán bộ trung đội không thể xem dữ liệu trung đội khác.
   - Xác thực băm mật khẩu có muối (Salted Hash - scrypt/pbkdf2), chống dò ngược bằng bảng băm (Rainbow Table Resistance).
4. **Tier 4 - Real-World Military Personas (Kịch bản thực chiến theo 4 vai trò quân nhân)**:
   - **Persona 1: Trực ban nội vụ**: Tra cứu siêu tốc dưới 5 giây (<5s SLA), hoàn tất chu trình bàn giao/thu hồi máy, cảnh báo rõ ràng khi bàn giao ca mà còn chiến sĩ chưa nộp.
   - **Persona 2: Cán bộ Trung đội**: Giới hạn dữ liệu quân nhân thuộc trung đội mình, trực quan hóa sơ đồ tủ 24 ngăn (A01 - A24), bị chặn khi can thiệp tủ trung đội khác.
   - **Persona 3: Chỉ huy Đại đội**: Bảng điều khiển toàn diện với danh sách vi phạm quá hạn, nút in trực tiếp biểu mẫu A4 một chạm và định dạng CSS ẩn thanh điều hướng khi in.
   - **Persona 4: Chiến sĩ / Người tò mò**: Giả lập hành vi cố ý truy cập trái phép vào cấu hình giờ, tài khoản quản trị hoặc đổi mật khẩu quản trị và bị từ chối triệt để.

### 1.2. Tính Độc lập và Tự Cô lập (Test Independence & Isolation)
- Mỗi test case khi khởi chạy đều được cấp một bản sao cơ sở dữ liệu SQLite cô lập hoàn toàn (`qldt_case_*.db`) từ master test fixture.
- Tuyệt đối không ghi đè hay làm sai lệch dữ liệu sản xuất tại `qldt.db`.
- Tự động dọn dẹp các tệp tạm sau khi hoàn tất phiên kiểm thử.

### 1.3. Quy tắc Mã Nguồn Sạch (Clean Code - Zero Comments)
Toàn bộ mã kiểm thử trong thư mục `tests/` tuân thủ nghiêm ngặt quy tắc: 100% không chứa chú thích code (`#`, `//`, `/*`, `<!--`), bảo đảm tính trong sáng và chuyên nghiệp cao nhất.

---

## 2. Bản đồ Bao phủ Tính năng (Feature Inventory & Mapping)

| Mã tính năng | Tên tính năng | Tầng kiểm thử | Tệp kiểm thử phụ trách | Trạng thái xác minh |
|---|---|---|---|---|
| F1 | Salted Password Hashing | Tier 3 | `test_tier3_security.py` | ĐẠT (Werkzeug scrypt/pbkdf2) |
| F2 | Session Hardening | Tier 3 | `test_tier3_security.py` | ĐẠT (session.clear on login) |
| F3 | RBAC Enforcement Decorator | Tier 3, 4 | `test_tier3_security.py`, `test_tier4_personas.py` | ĐẠT (Chặn 403 / redirect) |
| F4 | Super Admin Protection | Tier 3, 4 | `test_tier3_security.py`, `test_tier4_personas.py` | ĐẠT (Bảo vệ tuyệt đối tài khoản admin) |
| F5 | UI Sidebar Menu Scoping | Tier 3, 4 | `test_tier3_security.py`, `test_tier4_personas.py` | ĐẠT |
| F6 | Data Scoping (`pham_vi_loai`) | Tier 3, 4 | `test_tier3_security.py`, `test_tier4_personas.py` | CHỜ THỰC HIỆN (M2 Worker) |
| F7 | Trực ban Quick Search (<5s) | Tier 4 | `test_tier4_personas.py` | ĐẠT (< 0.2s thực tế) |
| F8 | A4 Report 1-Click Print | Tier 4 | `test_tier4_personas.py` | CHỜ THỰC HIỆN (M3 Worker) |
| F9 | Shift Handover Warning | Tier 4 | `test_tier4_personas.py` | ĐẠT (Cảnh báo chưa nộp) |
| F10 | Dashboard Overdue List | Tier 4 | `test_tier4_personas.py` | ĐẠT (Danh sách chưa nộp) |
| F11 | Zero Comments Clean Code | Toàn bộ | Toàn bộ các tệp trong `tests/` | ĐẠT (0 comment) |
| F12 | Military Persona E2E Tests | Tier 4 | `test_tier4_personas.py` | ĐẠT cấu trúc |

---

## 3. Cấu trúc Thư mục Kiểm thử (Directory Layout)

```
tests/
├── __init__.py                (Gói kiểm thử)
├── test_base.py               (Lớp cơ sở BaseTestCase, quản lý DB fixture cô lập)
├── test_tier1_features.py     (Tier 1: 25 test cases bao phủ chức năng cơ bản)
├── test_tier2_boundaries.py   (Tier 2: 25 test cases biên và trường hợp dị biệt)
├── test_tier3_security.py     (Tier 3: 10 test cases bảo mật, RBAC, hash mật khẩu)
├── test_tier4_personas.py     (Tier 4: 11 test cases kịch bản 4 vai trò quân nhân)
└── run_all_tests.py           (Bộ chạy kiểm thử thống nhất, phân tầng kết quả)
```

---

## 4. Hướng dẫn Thực thi Kiểm thử (Execution Instructions)

### 4.1. Lệnh thực thi toàn bộ Suite
Sử dụng môi trường Python 3.12:
```powershell
py -3.12 tests/run_all_tests.py
```

### 4.2. Lệnh thực thi từng tầng riêng biệt
```powershell
py -3.12 -m unittest -v tests/test_tier1_features.py
py -3.12 -m unittest -v tests/test_tier2_boundaries.py
py -3.12 -m unittest -v tests/test_tier3_security.py
py -3.12 -m unittest -v tests/test_tier4_personas.py
```

### 4.3. Ý nghĩa Mã Thoát (Exit Codes)
- `0`: Toàn bộ 71 test cases đều vượt qua thành công (All Passed).
- `1`: Có ít nhất 1 test case thất bại (phát hiện lỗi triển khai hoặc tính năng của milestone sau chưa hoàn thành).
