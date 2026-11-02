# QUY TẮC DỰ ÁN QUẢN LÝ ĐIỆN THOẠI ĐẠI ĐỘI

Dự án này phục vụ công tác quản lý vũ khí, trang bị, thiết bị thông tin (điện thoại) trong môi trường quân đội (cấp Đại đội). Mọi lập trình viên hoặc AI khi tiếp tục phát triển hệ thống bắt buộc phải đọc và tuân thủ tuyệt đối các nguyên tắc dưới đây.

---

## 1. NGUYÊN TẮC BẮT BUỘC: KHÔNG COMMENT CODE

- **TUYỆT ĐỐI KHÔNG VIẾT COMMENT TRONG MÃ NGUỒN**:
  - Không dùng `# ...` trong Python.
  - Không dùng `// ...` hoặc `/* ... */` trong JavaScript, CSS.
  - Không dùng `<!-- ... -->` trong HTML template.
- **Lý do**: Mã nguồn phải được thiết kế rõ ràng, tên hàm, tên biến và tên class tự diễn giải nghĩa (self-explanatory), chuẩn hóa tiếng Việt hoặc tiếng Anh mạch lạc, loại bỏ mọi rác chú thích để code tinh gọn, dễ đọc, dễ in ấn và kiểm duyệt an ninh thông tin trong quân đội.
- Mọi tài liệu hóa, giải thích quy trình hay hướng dẫn vận hành đều được ghi lại trong file markdown này hoặc tài liệu hướng dẫn sử dụng riêng, không đưa vào file code.

---

## 2. KIẾN TRÚC MÔ HÌNH MVC (MODEL - VIEW - CONTROLLER)

Hệ thống được tổ chức mạch lạc theo mô hình MVC để các đồng chí quân nhân dễ dàng tiếp cận, bảo trì và phát triển tính năng mới:

### Cấu trúc thư mục:
- `models/`: Chứa định nghĩa cấu trúc dữ liệu, kết nối cơ sở dữ liệu (SQLite/PostgreSQL) và các hàm truy vấn SQL nghiệp vụ.
- `views/`: Chứa giao diện người dùng bằng template HTML (Jinja2), CSS và JavaScript giao diện.
- `controllers/`: Chứa logic điều hướng (routing), kiểm tra quyền hạn, xác thực dữ liệu đầu vào và gọi Model để trả dữ liệu cho View.
- `static/`: Chứa file tĩnh (css, js, hình ảnh, icon SVG).
- `config.py`: File cấu hình chung cho hệ thống (đường dẫn DB, secret key, cổng chạy).
- `app.py`: File khởi chạy ứng dụng web.

---

## 3. NGUYÊN TẮC THIẾT KẾ GIAO DIỆN VÀ TRẢI NGHIỆM

1. **Phục vụ quân nhân không rành công nghệ**:
   - Thao tác một chạm (1-click action): Giao nhận, nộp máy chỉ cần 1 thao tác bấm nút to rõ.
   - Màu sắc nhận diện nghiệp vụ chuẩn quân đội:
     - Xanh lá (`#168452` / `#167b4b`): Đang lưu trong tủ, đúng giờ, an toàn.
     - Vàng cam (`#bd791c` / `#b7791e`): Đã lấy sử dụng, trường hợp ngoại lệ.
     - Đỏ (`#c34444`): Chưa nộp, quá hạn, vi phạm quy định.
     - Xanh hải quân (`#173653` / `#1e3a5f`): Màu chủ đạo bảng điều khiển đại đội.
   - Font chữ to, dễ đọc trên mọi màn hình máy tính bàn, laptop hoặc máy tính bảng.
   - Có phím tắt nhanh và hỗ trợ in ấn biểu mẫu A4 chuẩn theo quy định bàn giao, báo cáo.

---

## 4. QUY TẮC CƠ SỞ DỮ LIỆU VÀ NGHIỆP VỤ

1. **Chuẩn hóa tên gọi tiếng Việt không dấu (`snake_case`)**:
   - Tên bảng: `quan_nhan`, `dien_thoai`, `tu`, `ngan`, `lich_su_giao_nhan`, `cau_hinh_gio`, `khung_gio`, `tai_khoan`, `vai_tro`, `quyen_han`, `ca_truc`, `ban_giao_ca`.
   - Khóa chính: `ma_tu_sinh` (INTEGER PRIMARY KEY AUTOINCREMENT).
   - Khóa ngoại: `khoa_<tên_bang>` (VD: `khoa_quan_nhan`, `khoa_tu`).
2. **Khung giờ thông minh & linh hoạt**:
   - Không fix cứng khung giờ trong code. Tất cả được lưu trong bảng `cau_hinh_gio` và `khung_gio`.
   - Có thể điều chỉnh trực tiếp trên giao diện: khung giờ theo ngày trong tuần, theo nhóm đối tượng (Chiến sĩ mới; HSQ, BS năm thứ nhất; HSQ, BS năm thứ hai; Sĩ quan).
   - Hỗ trợ ngày đặc biệt (Lễ, Tết, trực sẵn sàng chiến đấu, diễn tập) có thể cấm sử dụng hoặc ghi đè khung giờ.
   - Khi giao nhận, hệ thống tự động kiểm tra giờ server với khung giờ quy định:
     - Đúng khung giờ: Cho phép lấy máy ngay.
     - Ngoài khung giờ: Bắt buộc chọn quy trình ngoại lệ (lý do khẩn cấp, cán bộ phụ trách, hạn phải nộp lại).
3. **Phân quyền động**:
   - Hệ thống quyền hạn chia theo nhóm chức năng (`GIAONHAN`, `QUANNHAN`, `DIENTHOAI`, `CAUHINH`, `BAOCAO`, `QUANTRI`).
   - Vai trò động: Người quản trị có thể tạo thêm vai trò mới và tích chọn quyền trực tiếp trên giao diện.
   - Tài khoản có thể gán vai trò theo thời hạn (theo ca trực) hoặc vĩnh viễn, phạm vi toàn đại đội hoặc theo từng trung đội/tủ.
4. **Không xóa cứng dữ liệu giao nhận**:
   - Mọi lượt giao nhận được ghi nhận liên tục vào `lich_su_giao_nhan` với timestamp server chuẩn xác.
   - Trạng thái hiện tại của máy (trong tủ hay đã lấy) được suy ra từ giao dịch mới nhất, chống sai lệch dữ liệu.

---

## 5. HƯỚNG DẪN MỞ RỘNG VÀ ĐÓNG GÓI SANG WINDOWS APP (.EXE)

1. **Chế độ Web hiện tại**:
   - Chạy bằng lệnh: `python app.py` (truy cập `http://localhost:5000` trên trình duyệt máy trạm hoặc mạng nội bộ đại đội).
2. **Khi chuyển sang Windows App (.exe)**:
   - Dùng thư viện `pywebview` để hiển thị cửa sổ ứng dụng desktop độc lập (không cần mở trình duyệt ngoài).
   - Dùng `pyinstaller --noconsole --onefile --add-data "templates;templates" --add-data "static;static" app.py` để tạo file `.exe` duy nhất.
   - Cơ sở dữ liệu SQLite tự động tạo file `qldt.db` cùng thư mục với file `.exe`, không cần cài thêm bất kỳ phần mềm hay cơ sở dữ liệu nào khác trên máy tính của đơn vị.
