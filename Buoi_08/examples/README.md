# Thư viện Code Mẫu Thực chiến - Buổi 8: MongoDB & Data Crawling

Thư mục này chứa toàn bộ các script mẫu độc lập, minh họa từng công nghệ và kỹ thuật đã được học trong **Buổi 8: Data Crawling & NoSQL Database với MongoDB** dành cho Team AI ProPTIT D24.

---

## Danh mục các Code Ví dụ

| File | Công nghệ chính | Nội dung & Kỹ thuật trọng tâm |
| :--- | :--- | :--- |
| **`01_static_scraping_bs4.py`** | `requests`, `BeautifulSoup4`, `lxml` | Cào HTML tĩnh từ `books.toscrape.com`, bóc tách bằng CSS Selector, xử lý User-Agent, ép kiểu dữ liệu và thực hiện delay lịch sự (Polite Crawling). |
| **`02_dynamic_scraping_playwright.py`** | `playwright.sync_api` | Khởi chạy trình duyệt Chromium Headless, giả lập cuộn trang vô hạn (Infinite Scroll) bằng mã JavaScript `evaluate()`, auto-wait và trích xuất dữ liệu web động. |
| **`03_api_sniffing_requests.py`** | `requests.Session` | Bắt và gọi trực tiếp Endpoint API ngầm từ tab DevTools Network, nhận dữ liệu JSON sạch với tốc độ cao, xử lý Retry với Exponential Backoff. |
| **`04_mongodb_crud_operations.py`** | `pymongo` | Kết nối `MongoClient`, thao tác CRUD (`insert_one`, `insert_many`, `find`, `delete`), thiết lập `Unique Index` và áp dụng kỹ thuật **`upsert=True`** chống trùng lặp. |
| **`05_mongodb_aggregation_pipeline.py`** | `pymongo.aggregate` | Xây dựng chuỗi xử lý Pipeline đa tầng (`$match` $\rightarrow$ `$group` $\rightarrow$ `$project` $\rightarrow$ `$sort`) để phân tích, thống kê dữ liệu trực tiếp trong Database Engine. |
| **`06_end_to_end_crawler_to_ai.py`** | `requests` + `bs4` + `pymongo` + `pandas` | Chuỗi giá trị dữ liệu khép kín: Cào web $\rightarrow$ Lưu MongoDB bằng Bulk Write Upsert $\rightarrow$ Chuyển đổi thành Pandas DataFrame sẵn sàng cho AI Model Training / RAG. |

---

## Hướng dẫn Thiết lập Môi trường Ảo (`.venv`) & Khởi chạy

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

> Trong buổi học này, chúng ta sẽ không dùng phần mềm rời bên ngoài, mà sẽ quản lý Database/Collection và xem trực quan các Document **thông qua Extension trực tiếp trên IDE**.
>
> *Phần cài đặt này các em sẽ tự tìm hiểu và thực hiện*

---

### Bước 4: Thực thi từng kịch bản code mẫu

Di chuyển vào thư mục `examples` để chạy thử nghiệm các script:

```bash
cd examples
```
```bash
# Test cào web tĩnh
python 01_static_scraping_bs4.py

# Test cào web động cuộn vô hạn
python 02_dynamic_scraping_playwright.py

# Test gọi trực tiếp API ngầm
python 03_api_sniffing_requests.py

# Test CRUD & Upsert MongoDB
python 04_mongodb_crud_operations.py

# Test Aggregation Pipeline
python 05_mongodb_aggregation_pipeline.py

# Test toàn bộ Pipeline End-to-End
python 06_end_to_end_crawler_to_ai.py
```
