# TÀI LIỆU HƯỚNG DẪN SỬ DỤNG HỆ THỐNG QUẢN LÝ ĐIỆN THOẠI ĐẠI ĐỘI (QLDT)

---

## I. TỔNG QUAN HỆ THỐNG

Hệ thống **Quản lý điện thoại đại đội (QLDT)** được xây dựng nhằm chuẩn hóa, số hóa và tự động hóa toàn diện công tác quản lý, giao nhận, giám sát thời lượng sử dụng và bàn giao ca gác thiết bị liên lạc trong đơn vị quân đội.

### 1. Các mục tiêu chính:
* **Quản lý trực quan:** Sơ đồ tủ đồ điện tử, phân loại trạng thái theo màu sắc thời gian thực.
* **Kiểm soát chặt chẽ:** Quy định khung giờ sử dụng theo từng nhóm đối tượng (Chiến sĩ mới, Hạ sĩ quan - Binh sĩ, Sĩ quan).
* **Bàn giao ca trực thông suốt:** Quy trình Wizard 3 bước, cảnh báo thiết bị quá hạn/chưa nộp, hỗ trợ thu hồi nhanh và xuất biên bản in chuẩn A4.
* **Lưu vết và kiểm toán:** Chụp snapshot dữ liệu khi đổi ca, nhật ký giao nhận không thể sửa đổi trái phép.

---

## II. DANH SÁCH TÀI KHOẢN VÀ PHÂN QUYỀN TRUY CẬP

Hệ thống phân định quyền hạn theo vai trò (RBAC) nghiêm ngặt:

| Tên đăng nhập | Mật khẩu mặc định | Cán bộ / Quân nhân | Vai trò | Quyền hạn chính |
| :--- | :--- | :--- | :--- | :--- |
| **`admin`** | `admin123` | Nguyễn Minh Quân | **Quản trị viên** | Toàn quyền cấu hình, phân quyền, quản lý danh mục, xem toàn bộ dữ liệu. |
| **`tuananh`** | `12345678` | Phạm Tuấn Anh | **Người trực (Trực ban)** | Ghi giao nhận điện thoại, duyệt mượn nhanh, thực hiện bàn giao ca trực toàn đơn vị. |
| **`levanson`** | `12345678` | Lê Văn Sơn | **Chỉ huy đại đội** | Phê duyệt đề nghị sử dụng ngoài giờ, xem và xuất các loại báo cáo, phê duyệt biên bản ca trực. |
| **`vanbinh`** | `12345678` | Trần Văn Bình | **Trực ban phân đội** | Quản lý giao nhận và bàn giao ca trong phạm vi đơn vị phụ trách. |

---

## III. HƯỚNG DẪN KHỞI CHẠY ỨNG DỤNG TẠI CHỖ

### Cách 1: Khởi chạy dạng Desktop App (Khuyên dùng)
* Nhấp đúp chuột vào tệp `chay_desktop.bat` (hoặc mở Terminal gõ `python desktop_app.py`).
* Hệ thống sẽ tự động khởi động máy chủ nội bộ và mở cửa sổ ứng dụng riêng biệt (App Mode) trên màn hình.

### Cách 2: Khởi chạy nền Web
* Chạy tệp `chay_web.bat` (hoặc mở Terminal gõ `python app.py`).
* Mở trình duyệt web bất kỳ (Chrome, Edge, Cốc Cốc, Firefox) và truy cập đường dẫn:
  ```
  http://127.0.0.1:5000
  ```

---

## IV. HƯỚNG DẪN CÁC TÍNH NĂNG CHI TIẾT

### 1. Đăng nhập & Đăng xuất
1. Truy cập màn hình đăng nhập, điền **Tên đăng nhập** và **Mật khẩu**.
2. Nhấn **Đăng nhập**. Hệ thống sẽ chuyển hướng trực tiếp vào màn hình Dashboard phù hợp với quyền của tài khoản.
3. Để đăng xuất, nhấn vào nút **Đăng xuất** màu đỏ độc lập trên thanh menu trên cùng (Topbar).

---

### 2. Trang Tổng quan (Dashboard)
* **Thẻ thống kê nhanh:** Hiển thị tổng số quân nhân, tổng điện thoại, số máy đang lưu trong tủ, số máy đang lấy ra và số máy quá hạn.
* **Cảnh báo khẩn cấp:** Khung màu đỏ hiển thị các trường hợp quá hạn quy định chưa trả máy.
* **Tỷ lệ trả máy theo đơn vị:** Thanh biểu đồ trực quan tiến độ nộp máy của từng trung đội/phân đội.

---

### 3. Sơ đồ tủ đồ (Quản lý trực quan)
* **Hiển thị trực quan theo ô tủ:** Mỗi ngăn tủ tương ứng với một quân nhân và thiết bị đăng ký.
* **Quy ước màu sắc chuẩn:**
  * **Màu xanh lá:** Máy đang nằm trong tủ (an toàn/đúng vị trí).
  * **Màu vàng/cam:** Máy đang được lấy ra sử dụng hợp lệ.
  * **Màu đỏ:** Máy đang lấy ra nhưng đã **QUÁ HẠN** so với khung giờ cho phép.
  * **Màu xám:** Ngăn tủ trống chưa gán máy hoặc quân nhân.
* **Thao tác nhanh:** Nhấp vào từng ô để xem thông tin chi tiết của quân nhân, thiết bị và lịch sử giao nhận gần nhất.

---

### 4. Giao nhận điện thoại (Lấy ra & Nộp vào)
* **Lấy điện thoại ra:**
  1. Chọn quân nhân cần lấy máy từ danh sách hoặc quét mã.
  2. Hệ thống tự động đối chiếu với khung giờ hiện tại:
     * Nếu trong khung giờ cho phép: Chấp thuận giao máy ngay.
     * Nếu ngoài khung giờ: Yêu cầu chọn lý do ngoại lệ hoặc chỉ huy phê duyệt.
  3. Nhấn **Xác nhận lấy máy**.
* **Nộp điện thoại vào tủ:**
  1. Chọn quân nhân nộp máy.
  2. Xác nhận tình trạng thiết bị và ngăn tủ cất giữ.
  3. Nhấn **Xác nhận nộp máy**. Trạng thái ngăn tủ tự động chuyển sang màu xanh.

---

### 5. Luồng Bàn giao ca trực (Quy trình Wizard 3 bước mới)

Đây là chức năng trọng tâm giúp trực ban cũ và trực ban mới bàn giao quân số thiết bị nhanh chóng, chính xác và không sợ sót lọt:

```
[Bước 1: Kiểm đếm & Xử lý nợ]  ──>  [Bước 2: Thông tin nhận ca]  ──>  [Bước 3: Xác nhận & In biên bản]
```

#### Bước 1: Kiểm đếm số lượng & Xử lý nhanh
* Hệ thống tự động tổng hợp số liệu: Tổng máy, Trong tủ, Đang mượn, Quá hạn.
* Danh sách thiết bị chưa nộp được phân nhóm màu:
  * **Nhãn đỏ (Quá hạn):** Quân nhân giữ máy quá giờ quy định.
  * **Nhãn vàng (Đang mượn):** Quân nhân đang sử dụng máy hợp lệ.
* **Nút "⚡ Thu hồi nhanh":** 
  * Cho phép trực ban thu hồi máy của quân nhân ngay tại bảng kiểm kê mà không phải chuyển sang màn hình khác.
  * Cơ chế khóa an toàn chống trùng lặp dữ liệu.
* Nhấn **Tiếp tục: Bàn giao >>** để sang Bước 2.

#### Bước 2: Thông tin nhận ca & Dặn dò
* Chọn **Cán bộ nhận ca** từ danh sách (chỉ hiện các quân nhân có thẩm quyền trực ban).
* Chọn **Ca trực tiếp theo** (Sáng, Chiều, Tối hoặc ca đặc biệt).
* Nhập nội dung **Dặn dò / Lưu ý nghiệp vụ** cho ca sau (ví dụ: máy hỏng, quân nhân đi viện mang theo máy,...).
* Nhấn **Tiếp tục: Xác nhận >>** để sang Bước 3.

#### Bước 3: Xác nhận & Hoàn tất
* Xem lại bản tóm tắt tình trạng bàn giao.
* Tích chọn cam kết: *"Tôi đã kiểm tra đối chiếu thực tế và xác nhận các thông tin trên là chính xác"*.
* Nhấn **Hoàn tất bàn giao ca**.
* Hệ thống sẽ tự động đóng băng và chụp ảnh **Snapshot JSON** toàn bộ dữ liệu lúc bàn giao vào cơ sở dữ liệu.

#### In Biên bản bàn giao chuẩn A4:
* Sau khi hoàn tất hoặc tại danh sách lịch sử bàn giao, nhấn nút **In biên bản**.
* Mẫu in được định dạng trang trọng theo chuẩn văn bản quân đội:
  * Quốc hiệu, Tiêu ngữ.
  * Thông tin ca trực, thời gian, người giao, người nhận.
  * Bảng kiểm đếm số lượng thực tế.
  * Bảng chi tiết danh sách thiết bị chưa thu hồi kèm lý do.
  * 3 khung chữ ký: **Người bàn giao**, **Người nhận ca**, **Chỉ huy phê duyệt**.

---

### 6. Quản lý quân nhân & Điện thoại
* **Quân nhân:** Thêm mới quân nhân, cập nhật cấp bậc, chức vụ, đơn vị, gán ngăn tủ cố định.
* **Điện thoại:** Khai báo số IMEI, hãng sản xuất, model máy, số điện thoại liên lạc của quân nhân. Có modal chỉnh sửa trực tiếp.

---

### 7. Báo cáo thống kê
* **Báo cáo tổng hợp:** Xem biểu đồ tỷ lệ chấp hành thời gian nộp máy theo ngày/tuần/tháng.
* **Báo cáo vi phạm:** Danh sách các trường hợp chậm nộp máy, sử dụng sai quy định để đại đội xử lý kỷ luật hoặc nhắc nhở.
* **Xuất Excel:** Nhấn **Xuất dữ liệu** để tải về file Excel tổng hợp phục vụ lưu trữ và báo cáo cấp trên.

---

### 8. Cấu hình hệ thống (Dành cho Quản trị viên)
* **Khung giờ sử dụng:** Cài đặt giờ mở tủ và giờ thu máy cho từng thứ trong tuần và từng nhóm quân nhân.
* **Cơ cấu tổ chức:** Cấu hình danh mục đại đội, trung đội, tiểu đội.
* **Tủ & Ngăn tủ:** Cấu hình số lượng tủ, số hàng, số cột và mã ngăn tủ.
