# HƯỚNG DẪN DEPLOY DỰ ÁN QUẢN LÝ ĐIỆN THOẠI (QLDT) LÊN VERCEL

---

## I. TỔNG QUAN VỀ TRIỂN KHAI TRÊN VERCEL

[Vercel](https://vercel.com) là nền tảng điện toán đám mây tối ưu cho web, cung cấp hạ tầng CDN toàn cầu và Serverless Functions. Dự án **QLDT** (Python Flask) được đóng gói để chạy mượt mà trên môi trường Serverless của Vercel thông qua runtime `@vercel/python`.

### 1. Cơ chế hoạt động của Cơ sở dữ liệu (SQLite) trên Vercel
* Hệ thống máy chủ Serverless của Vercel có hệ thống tệp **chỉ đọc (read-only)**, ngoại trừ thư mục tạm `/tmp`.
* **Cơ chế đã được cấu hình tự động trong mã nguồn (`config.py`):**
  * Khi phát hiện môi trường Vercel (`os.environ.get("VERCEL")`), hệ thống sẽ tự động sao chép tệp cơ sở dữ liệu mẫu `qldt.db` vào thư mục `/tmp/qldt.db`.
  * Nhờ đó, ứng dụng trên Vercel có thể đọc/ghi dữ liệu, đăng nhập, nộp/lấy máy và bàn giao ca gác bình thường mà không bị lỗi cấp quyền tệp.
* **Lưu ý quan trọng về tính chất Serverless:**
  * Dữ liệu trong `/tmp` sẽ tồn tại trong suốt vòng đời của container Serverless và có thể được làm mới (reset về dữ liệu gốc) khi Vercel tắt container không dùng đến (cold-start).
  * **Phù hợp nhất:** Dùng cho Demo trực tuyến, thuyết trình đồ án, kiểm thử giao diện và luồng nghiệp vụ.
  * **Nếu muốn lưu dữ liệu vĩnh viễn trên Cloud:** Bạn chỉ cần chuyển kết nối sang CSDL Cloud như **Turso (LibSQL/SQLite Cloud)**, **Supabase** hoặc **Neon (PostgreSQL)**.

---

## II. CÁC TỆP CẤU HÌNH ĐÃ ĐƯỢC CHUẨN BỊ SẴN

Trong thư mục dự án, tất cả các tệp cần thiết cho Vercel đã được tạo sẵn:

1. **`vercel.json`**: Định tuyến toàn bộ yêu cầu web (bao gồm cả static files và routes) về hàm Serverless tại `api/index.py` theo cơ chế `rewrites` chuẩn của Vercel.
2. **`api/index.py`**: Điểm vào (Entrypoint) khởi tạo ứng dụng Flask WSGI cho runtime của Vercel.
3. **`requirements.txt`**: Danh sách thư viện Python cần thiết (`Flask`, `Werkzeug`, `openpyxl`, `Jinja2`).
4. **`.vercelignore`**: Loại trừ các tệp kiểm thử tự động, cache, nhật ký để quá trình build và tải lên diễn ra nhanh nhất.
5. **`config.py`**: Tự động nhận diện biến môi trường `VERCEL` để trỏ đường dẫn CSDL và thư mục tải lên vào `/tmp`.

---

## III. CÁCH 1: DEPLOY BẰNG VERCEL CLI (NHANH NHẤT)

Nếu máy tính của bạn đã cài đặt [Node.js](https://nodejs.org/), đây là cách nhanh và thuận tiện nhất:

### Bước 1: Cài đặt Vercel CLI (nếu chưa có)
Mở PowerShell hoặc Command Prompt và chạy:
```powershell
npm install -g vercel
```

### Bước 2: Đăng nhập tài khoản Vercel
```powershell
vercel login
```
Trình duyệt sẽ mở ra, bạn chỉ cần chọn đăng nhập bằng GitHub hoặc Email của bạn.

### Bước 3: Triển khai dự án
Tại thư mục gốc dự án `d:\QLDT`, chạy lệnh:
```powershell
vercel
```

Vercel sẽ hỏi một vài câu hỏi ngắn để xác nhận, bạn chọn theo gợi ý sau:
* *Set up and deploy “d:\QLDT”?* ➔ Gõ **`y`** rồi nhấn Enter.
* *Which scope do you want to deploy to?* ➔ Chọn tài khoản của bạn.
* *Link to existing project?* ➔ Gõ **`n`** (tạo mới).
* *What’s your project’s name?* ➔ Nhấn Enter (để mặc định `qldt` hoặc đặt tên bạn muốn, ví dụ: `qldt-dai-doi`).
* *In which directory is your code located?* ➔ Nhấn Enter (để mặc định `./`).
* *Want to modify settings?* ➔ Gõ **`n`**.

Quá trình tải mã nguồn và build sẽ diễn ra trong khoảng 1-2 phút.

### Bước 4: Triển khai lên Production (Chính thức)
Sau khi kiểm tra bản Preview thành công, chạy lệnh sau để phát hành đường dẫn chính thức:
```powershell
vercel --prod
```
Vercel sẽ cung cấp cho bạn một đường dẫn URL công khai có dạng:
```
https://qldt-dai-doi.vercel.app
```

---

## IV. CÁCH 2: DEPLOY QUA GIAO DIỆN WEB VERCEL & GITHUB

Nếu bạn quản lý mã nguồn qua GitHub/GitLab:

### Bước 1: Đẩy mã nguồn lên GitHub
Khởi tạo Git và đẩy toàn bộ thư mục `d:\QLDT` lên một Repository cá nhân trên GitHub:
```powershell
git init
git add .
git commit -m "Khoi tao du an QLDT va cau hinh Vercel"
git branch -M main
git remote add origin https://github.com/<tai-khoan-cua-ban>/qldt.git
git push -u origin main
```

### Bước 2: Kết nối và Deploy trên Vercel Dashboard
1. Truy cập [https://vercel.com](https://vercel.com) và đăng nhập.
2. Tại trang tổng quan (Dashboard), nhấp vào nút **"Add New..."** ➔ Chọn **"Project"**.
3. Tại danh sách **"Import Git Repository"**, tìm và nhấn **"Import"** bên cạnh repository `qldt` bạn vừa đẩy lên.
4. Tại phần **"Configure Project"**:
   * **Project Name:** Đặt tên dự án (ví dụ: `qldt-dai-doi`).
   * **Framework Preset:** Để nguyên **Other**.
   * **Root Directory:** Để `./`.
   * **Environment Variables (Tùy chọn):** Bạn có thể thêm:
     * Key: `SECRET_KEY` | Value: `chuoi-khoa-bao-mat-tuy-y-2026`
5. Nhấn nút **"Deploy"**.
6. Đợi khoảng 1-2 phút để Vercel cài đặt thư viện và khởi chạy. Khi màn hình hiện pháo hoa chúc mừng, bạn có thể nhấp vào nút **"Visit"** để sử dụng ứng dụng ngay!

---

## V. KIỂM TRA SAU KHI DEPLOY VÀ TÀI KHOẢN ĐĂNG NHẬP

Khi truy cập vào đường dẫn trang web trên Vercel, bạn sử dụng các tài khoản có sẵn trong CSDL mẫu để trải nghiệm:

| Tài khoản | Mật khẩu | Quyền hạn |
| :--- | :--- | :--- |
| **`admin`** | `admin123` | Quản trị viên (Toàn quyền hệ thống) |
| **`tuananh`** | `12345678` | Trực ban (Bàn giao ca, giao nhận máy) |
| **`levanson`** | `12345678` | Chỉ huy đơn vị (Duyệt mượn, xem báo cáo) |
| **`vanbinh`** | `12345678` | Trực ban phân đội |

---

## VI. MỘT SỐ LƯU Ý KHI GẶP VẤN ĐỀ (TROUBLESHOOTING)

1. **Lỗi mất CSS / Giao diện vỡ (404 Not Found trên tệp `/static/...`):**
   * **Nguyên nhân:** Vercel mặc định chặn các đường dẫn static trước khi request đến Flask nếu cấu hình routes tĩnh không khớp.
   * **Cách xử lý:** Hệ thống đã được chuyển sang cơ chế `rewrites` chuẩn tại `vercel.json` và cố định đường dẫn tuyệt đối cho `static_folder` trong `app.py`. Bạn chỉ cần đẩy lại mã nguồn (`git push` hoặc `vercel --prod`) và chọn **Redeploy** trên Vercel.
2. **Lỗi 500 FUNCTION_INVOCATION_TIMEOUT:**
   * Do Serverless Function khởi động lạnh quá thời gian quy định. Vercel gói miễn phí mặc định timeout là 10 giây. Với cấu hình tối ưu của QLDT, thời gian khởi động chỉ mất dưới 1.5 giây.
2. **Lỗi Read-only File System:**
   * Mã nguồn `config.py` đã tự động chuyển sang ghi tại `/tmp/qldt.db` và `/tmp/uploads`. Nếu bạn tự thêm tính năng ghi tệp mới, luôn đảm bảo đường dẫn lưu tệp bắt đầu bằng `/tmp/`.
3. **Cập nhật mã nguồn mới:**
   * Nếu dùng **Cách 1 (Vercel CLI):** Chỉ cần chạy lại `vercel --prod` tại thư mục dự án.
   * Nếu dùng **Cách 2 (GitHub):** Mỗi khi bạn `git push` lên nhánh `main`, Vercel sẽ tự động build và cập nhật phiên bản mới nhất ngay lập tức (CI/CD tự động).
