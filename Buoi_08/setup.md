# HƯỚNG DẪN CHUẨN BỊ CHO BUỔI HỌC

## 1. Yêu cầu

Các em tạo thư mục **Buoi_08**, sau đó thêm file `requirements.txt` với nội dung như sau:
```txt
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=5.1.0
playwright>=1.42.0
fake-useragent>=1.5.0
pymongo>=4.6.0
pandas>=2.0.0
python-dotenv>=1.0.0
```

## 2. Thiết lập Môi trường Ảo (`.venv`) & Khởi chạy

Để tránh xung đột package giữa các dự án, khuyến nghị khởi tạo và sử dụng môi trường ảo độc lập (`.venv`).

### Bước 1: Khởi tạo & Kích hoạt Môi trường ảo (`.venv`)

Mở Terminal và điều hướng tới thư mục `Buoi_08`:

```bash
cd Buoi_08
python -m venv .venv
```

**Kích hoạt môi trường ảo tùy theo hệ điều hành:**

* **Trên Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
  *(Nếu gặp lỗi script execution policy, chạy lệnh: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

* **Trên Windows (Command Prompt - CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

* **Trên macOS / Linux:**
  ```bash
  source .venv/bin/activate
  ```

*(Khi kích hoạt thành công, đầu dòng lệnh Terminal sẽ xuất hiện tiền tố `(.venv)`)*

---

### Bước 2: Cài đặt Thư viện từ `requirements.txt`

Sau khi đã kích hoạt môi trường ảo `(.venv)`, tiến hành nâng cấp `pip` và cài đặt danh sách thư viện đã chuẩn bị sẵn:

```bash
pip install -r requirements.txt

# Cài đặt Browser Driver riêng cho Playwright (Chromium)
playwright install chromium
```

---

### Bước 3: Cài đặt & Kết nối MongoDB thông qua Extension trên IDE

> Trong buổi học này, chúng ta sẽ không dùng phần mềm rời bên ngoài, mà sẽ quản lý Database/Collection và xem trực quan các Document **thông qua Extension trực tiếp trên IDE**. Phần cài đặt này các em sẽ tự tìm hiểu và thực hiện, chưa yêu cầu phải kết nối được với MongoDB.