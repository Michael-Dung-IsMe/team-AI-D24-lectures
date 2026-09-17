# Tổng kết & Homework Buổi 8: Data Crawling & MongoDB Pipeline

## 1. Tổng kết kiến thức buổi 8

### 1.1 Các công cụ thu thập dữ liệu
```
                   [Lựa Chọn Chiến Lược Crawl Dữ Liệu]
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
   [Static Scraping]        [Dynamic Scraping]       [API Sniffing]
    requests + bs4               playwright        F12 DevTools + requests
  HTML tĩnh từ Server         SPA / Render JS         Internal JSON API
  (Mô hình Server-Side)    (Client-Side Rendering)    (Dữ liệu thô từ Backend)
  Nhanh, nhẹ, ổn định      Mô phỏng trình duyệt     Tốc độ cực hạn (20-50x),
                           Auto-wait, tốn RAM        data JSON sạch nhất
```

- **Option 1 — Static Scraping (`requests` + `BeautifulSoup4`):** Ưu tiên hàng đầu cho các trang Server-Side Rendering (SSR). Dữ liệu có sẵn trong HTML trả về. Sử dụng parser engine `lxml` cho tốc độ xử lý nhanh nhất.
- **Option 2 — Dynamic Scraping (`playwright`):** Bắt buộc khi gặp Single Page Application (React/Vue/Angular), nội dung cuộn vô hạn (Infinite Scroll) hoặc yêu cầu tương tác giao diện (click, gõ phím, xử lý auth). Cơ chế *Auto-waiting* và kiến trúc 3 tầng (*Browser $\rightarrow$ BrowserContext $\rightarrow$ Page*) giúp tiết kiệm RAM và loại bỏ lỗi `ElementNotInteractable`.
- **Option 3 — Network API Sniffing (Kỹ thuật tối thượng):** Mở Chrome DevTools (`F12`) $\rightarrow$ tab **Network** $\rightarrow$ lọc **Fetch/XHR** để tìm trực tiếp endpoint JSON ngầm. Bỏ qua hoàn toàn bước render và bóc tách DOM, đưa thẳng dữ liệu vào Python Dict/List.

---

### 1.2 Bảng Tra Cứu Nhanh Các Package & Hàm Cốt Lõi (Cheatsheet)

| Thư viện | Cú pháp / Hàm cốt lõi | Ý nghĩa & Ứng dụng thực chiến |
| :--- | :--- | :--- |
| **`requests`** | `requests.get(url, headers=..., timeout=10)` | Gửi HTTP GET, bắt buộc giả lập `User-Agent` và thiết lập timeout tránh treo script. |
| | `response.content` | **Quan trọng:** Lấy raw bytes để parser tự giải mã UTF-8 từ thẻ `<meta>`, tránh lỗi giải mã Latin-1 (`Â£`). |
| | `response.raise_for_status()` | Bắt lỗi tự động và ném Exception nếu HTTP code thuộc nhóm 4xx/5xx. |
| | `requests.Session()` | Duy trì kết nối TCP (Keep-Alive) tăng tốc độ mạng 2-3 lần và tự động quản lý Cookie qua các trang. |
| **`bs4`** | `BeautifulSoup(response.content, 'lxml')` | Dựng cây DOM bằng bộ phân tích cú pháp C (`lxml`) siêu tốc và ổn định. |
| | `soup.select(css_selector)` | Tìm kiếm danh sách phần tử bằng cú pháp CSS Selector (`article.product_pod`, `div.quote`). |
| | `card.select_one("h3 > a")` | Tìm phần tử con trực tiếp đầu tiên khớp với bộ chọn. |
| | `tag.get_text(strip=True)` | Trích xuất văn bản bên trong thẻ, tự động xóa khoảng trắng và dòng thừa ở 2 đầu. |
| | `tag.get('attr_name')` | Lấy giá trị thuộc tính HTML (`href`, `title`, `src`). Tránh crash lỗi nếu thuộc tính không tồn tại. |
| **`urllib.parse`** | `urljoin(base_url, rel_link)` | Chuẩn hóa đường dẫn tương đối (như `../page-2.html`) thành URL tuyệt đối hợp lệ. |
| **`re`** | `re.search(r"[\d.]+", price_str)` | Bóc tách số thực từ chuỗi chứa ký tự tiền tệ phục vụ lưu trữ số liệu AI (`float`). |
| **`playwright`** | `p.chromium.launch(headless=True)` | Khởi chạy Chromium ngầm (không giao diện) tiết kiệm tối đa CPU/RAM. |
| | `page.goto(url, wait_until="networkidle")` | Điều hướng tới URL và chờ tới khi mạng ổn định (không còn request ngầm trong 500ms). |
| | `page.evaluate("window.scrollTo(0, document.body.scrollHeight);")` | Thực thi mã JavaScript trực tiếp trên trang để cuộn xuống đáy (Infinite Scroll). |
| | `page.locator(selector).all()` | Bắt danh sách các phần tử theo locator có hỗ trợ cơ chế auto-waiting. |
| **`pymongo`** | `MongoClient("mongodb://localhost:27017/")` | Khởi tạo kết nối tới Database MongoDB Server. |
| | `col.create_index([("key", 1)], unique=True)` | Tạo chỉ mục Unique B-Tree ngăn chặn hoàn toàn việc chèn trùng lặp dữ liệu. |
| | `col.insert_many(list_of_dicts)` | Chèn hàng loạt document vào collection với hiệu năng cao. |
| | `col.update_one(filter, {"$set": ...}, upsert=True)` | **Kỹ thuật Upsert:** Cập nhật nếu đã có bản ghi, chèn mới nếu chưa tồn tại. |
| | `col.find(filter, {"_id": 0})` | Truy vấn dữ liệu kết hợp Projection loại bỏ trường `_id` để tương thích định dạng JSON/Pandas. |
| **`pandas`** | `pd.DataFrame(list(col.find({}, {"_id": 0})))` | **Cầu nối AI:** Đưa toàn bộ cursor dữ liệu MongoDB vào DataFrame để phục vụ huấn luyện mô hình. |

---

### 1.3 Những Bẫy Kỹ Thuật (Pitfalls) & Nguyên Tắc Vàng Cần Ghi Nhớ
1. **Bẫy giải mã Encoding (`response.text` vs `response.content`):**
   - Không nên dùng `response.text` khi website không khai báo `charset=utf-8` trên HTTP Header, vì `requests` sẽ mặc định về `ISO-8859-1`, biến `£51.77` thành `Â51.77` gây lỗi crash hàm `float()`.
   - **Nguyên tắc:** Luôn truyền `response.content` vào `BeautifulSoup(response.content, 'lxml')` và dùng Regex `re.search(r"[\d.]+", text)` để trích xuất số.
2. **Hiểm họa URL tương đối:**
   - Tránh việc ghép chuỗi thủ công `base_url + href`. Luôn dùng `urljoin(base_url, href)` để tự xử lý đúng các trường hợp link con (`/catalogue/...`, `../page-2.html`).
3. **Phòng thủ `NoneType` khi bóc tách thẻ HTML:**
   - Cấu trúc website thực tế không đồng nhất (có sản phẩm không có giá cũ, không có tag). Luôn kiểm tra điều kiện tồn tại trước khi gọi thuộc tính:
     ```python
     title = title_tag.get("title", title_tag.get_text(strip=True)) if title_tag else "Unknown"
     ```
4. **Văn hóa cào lịch sự & Chiến lược Anti-blocking:**
   - Luôn thiết lập `User-Agent` ngẫu nhiên qua `fake-useragent`.
   - Thêm khoảng nghỉ ngẫu nhiên `time.sleep(random.uniform(1.0, 2.5))` giữa các trang.
   - Khi gặp mã lỗi `429 Too Many Requests` hoặc `503`, áp dụng ngay **Exponential Backoff + Random Jitter** thay vì spam request.
5. **Chống rò rỉ bộ nhớ (Memory Leak):**
   - Với Playwright, luôn bọc trong khối `with sync_playwright() as p:` hoặc đảm bảo gọi `browser.close()` trong `finally`.

---

## 2. Đề Bài & Yêu Cầu Bài Tập Về Nhà (Homework)

> 💡 **Mục tiêu bài tập:** Xây dựng hoàn chỉnh một **Data Pipeline chuẩn của Kỹ sư AI**: Thu thập dữ liệu từ Web $\rightarrow$ Lưu trữ & Lập chỉ mục trong MongoDB $\rightarrow$ Truy vấn trích xuất dữ liệu $\rightarrow$ Chuyển đổi sang cấu trúc bảng Pandas DataFrame.  
> Trang web thực hành chuẩn: **`http://quotes.toscrape.com/`**

```
                     Quy Trình Data Pipeline Cần Thực Hiện:
             ┌──────────────────────────────────────────────────┐
             │         Trang web quotes.toscrape.com            │
             └─────────────────────────┬────────────────────────┘
                                       │
                                       ▼  Task 1: requests + BeautifulSoup4
             ┌──────────────────────────────────────────────────┐
             │       Danh sách 10 Quotes dạng Python Dict       │
             └─────────────────────────┬────────────────────────┘
                                       │
                                       ▼  Task 2: pymongo insert_many
             ┌──────────────────────────────────────────────────┐
             │      MongoDB Database: d24_buoi8 -> quotes       │
             └─────────────────────────┬────────────────────────┘
                                       │
                                       ▼  Task 3: find + projection
             ┌──────────────────────────────────────────────────┐
             │     Lọc danh sách Quote của "Albert Einstein"    │
             └─────────────────────────┬────────────────────────┘
                                       │
                                       ▼  Task 4: pd.DataFrame
             ┌──────────────────────────────────────────────────┐
             │    Pandas DataFrame hiển thị sẵn sàng cho AI     │
             └──────────────────────────────────────────────────┘
```

---

### 2.1 PHẦN 1: CỐT LÕI (BẮT BUỘC)

Các em tạo file `homework_buoi8.py` (hoặc `homework_buoi8.ipynb`) và hoàn thiện tuần tự 4 tasks:

#### Task 1: Web Scraping với BeautifulSoup
- **Mục tiêu:** Cào dữ liệu trang 1 của `http://quotes.toscrape.com/`.
- **Yêu cầu kỹ thuật:**
  1. Thiết lập Header giả lập trình duyệt và kiểm tra trạng thái kết nối.
  2. Truyền `response.content` vào `BeautifulSoup(...)` để dựng cây DOM an toàn không lỗi font/encoding.
  3. Lọc tất cả các khối thẻ `<div class="quote">`.
  4. Bóc tách chính xác 3 trường thông tin cho mỗi trích dẫn:
     - `text` (chuỗi văn bản câu nói, ví dụ: `"The world as we have created it..."`).
     - `author` (tên tác giả, ví dụ: `"Albert Einstein"`).
     - `tags` (danh sách các thẻ chủ đề dạng `list[str]`, ví dụ: `["change", "deep-thoughts", "thinking"]`).

#### Task 2: Lưu trữ vào MongoDB với `pymongo`
- **Mục tiêu:** Lưu trữ 10 bản ghi vừa cào vào cơ sở dữ liệu MongoDB.
- **Yêu cầu kỹ thuật:**
  1. Kết nối tới MongoDB Local `mongodb://localhost:27017/` (hoặc chuỗi kết nối MongoDB Atlas).
  2. Truy cập Database `d24_buoi8` và Collection `quotes`.
  3. Xóa sạch dữ liệu cũ trong collection (nếu có) để đảm bảo kết quả kiểm thử nhất quán.
  4. Chèn toàn bộ danh sách bản ghi vào collection.

#### Task 3: Truy vấn Dữ liệu Nâng cao
- **Mục tiêu:** Thực hành thao tác truy vấn có điều kiện và sử dụng Projection trong MongoDB.
- **Yêu cầu kỹ thuật:**
  1. Viết câu lệnh để tìm tất cả các câu trích dẫn có tác giả chính xác là `"Albert Einstein"`.
  2. Áp dụng kỹ thuật Projection để ẩn trường `_id` khỏi kết quả.
  3. Duyệt con trỏ (Cursor) và in các câu trích dẫn tìm được ra màn hình terminal.

#### Task 4: Chuyển đổi sang Pandas DataFrame cho AI
- **Mục tiêu:** Xây dựng cầu nối chuyển đổi dữ liệu từ MongoDB sang DataFrame phục vụ tiền xử lý và huấn luyện mô hình.
- **Yêu cầu kỹ thuật:**
  1. Truy vấn toàn bộ dữ liệu từ collection `quotes`, loại bỏ trường `_id`.
  2. Ép kiểu kết quả trả về thành danh sách Python và khởi tạo `pd.DataFrame(list(...))`.
  3. In thông tin tóm tắt cấu trúc bảng và in ra 5 dòng đầu tiên.

---

### 2.2 PHẦN 2: THỬ THÁCH MỞ RỘNG (KHUYẾN KHÍCH)

Học viên chọn làm thêm các thử thách sau để nâng cao kỹ năng xử lý dữ liệu quy mô lớn:

* **Thử thách A — Phân trang tự động (Pagination):**
  - Không dừng lại ở trang 1, hãy viết vòng lặp tự động tìm thẻ nút Next `<li class="next"> > a` ở chân trang để lấy link trang kế tiếp.
  - Tìm cách để chuẩn hóa đường dẫn và tiếp tục cào sang trang 2, trang 3 (thu thập tổng cộng 30 câu trích dẫn).
  - Có thiết lập khoảng nghỉ ngẫu nhiên giữa các lượt tải trang.

* **Thử thách B — Kỹ thuật Upsert Chống trùng lặp (Data Deduplication):**
  - Thiết lập `Unique Index` trên trường nội dung: `collection.create_index([("text", 1)], unique=True)`.
  - Thay vì xóa sạch collection rồi `insert_many()`, hãy sử dụng vòng lặp kết hợp kỹ thuật Upsert:
    ```python
    collection.update_one(
        {"text": item["text"]},
        {"$set": item},
        upsert=True
    )
    ```
  - Kiểm chứng: Khi chạy lại script nhiều lần liên tiếp, tổng số bản ghi trong Database vẫn giữ nguyên, không bị trùng lặp dữ liệu.

---

## 3. Đầu Ra Mẫu Mong Đợi (Expected Outputs)

### 3.1 Dữ liệu BSON Document mẫu trên Extension IDE
Khi mở Extension MongoDB trên IDE (hoặc MongoDB Compass / `mongosh`) tại Database `d24_buoi8`, Collection `quotes`, dữ liệu hiển thị chuẩn cấu trúc:
```json
{
  "_id": {"$oid": "6644f1e582a9..."},
  "text": "“The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.”",
  "author": "Albert Einstein",
  "tags": ["change", "deep-thoughts", "thinking", "world"]
}
```

### 3.2 Đầu ra Terminal hiển thị mẫu (Tham khảo)
```text
=== KẾT QUẢ CHẠY BÀI TẬP VỀ NHÀ BUỔI 8 ===
[*] Đang kết nối tới trang: http://quotes.toscrape.com/
[OK] Đã cào thành công 10 câu trích dẫn từ trang web!
[OK] Kết nối MongoDB thành công tới Database 'd24_buoi8'!
[OK] Đã lưu 10 bản ghi vào collection 'quotes'.

[*] Danh sách trích dẫn tìm được của Albert Einstein:
 - "The world as we have created it is a process of our thinking..." (Tác giả: Albert Einstein)
 - "There are only two ways to live your life. One is as though nothing is a miracle..." (Tác giả: Albert Einstein)
 - "Try not to become a man of success. Rather become a man of value." (Tác giả: Albert Einstein)

--- DATAFRAME NGHIỆM THU (5 DÒNG ĐẦU) ---
                                                text            author                                                tags
0  “The world as we have created it is a process ...   Albert Einstein            [change, deep-thoughts, thinking, world]
1  “It is our choices, Harry, that show what we t...      J.K. Rowling                                [abilities, choices]
2  “There are only two ways to live your life. On...   Albert Einstein      [inspirational, life, live, miracle, miracles]
3  “The person, be it gentleman or lady, who has ...       Jane Austen                                  [aliteracy, books]
4  “Imperfection is beauty, madness is genius and...    Marilyn Monroe                        [be-yourself, inspirational]

[OK] Kích thước DataFrame: (10, 3)
[OK] Hoàn thành toàn bộ pipeline xuất sắc!
```

---

## 4. Tiêu Chí Đánh Giá & Nghiệm Thu (Evaluation Checklist)

| Tiêu chí | Mức độ | Yêu cầu nghiệm thu kỹ thuật |
| :--- | :---: | :--- |
| **Crawl dữ liệu chính xác** | Bắt buộc | Cào đủ 10 quotes, bóc tách đầy đủ 3 trường `text`, `author`, `tags` (trường `tags` phải là kiểu `list[str]`). Có thiết lập giả lập `User-Agent`. |
| **Thao tác MongoDB chuẩn quy chuẩn** | Bắt buộc | Kết nối thành công, tạo đúng Database `d24_buoi8` và Collection `quotes`. Sử dụng đúng lệnh `insert_many()`. |
| **Truy vấn & Projection** | Bắt buộc | Viết đúng cú pháp query tìm kiếm tác giả `"Albert Einstein"`. Sử dụng Projection để ẩn trường `_id`. |
| **Chuyển đổi DataFrame** | Bắt buộc | Tạo DataFrame từ kết quả truy vấn MongoDB thành công, hiển thị đủ các cột mà không phát sinh lỗi serialize `ObjectId`. |
| **Clean Code & Robustness** | Bắt buộc | Mã nguồn rõ ràng, có chia hàm mạch lạc, có khối `try...except` bắt ngoại lệ kết nối mạng và đóng kết nối MongoDB khi kết thúc. |
| **Phân trang tự động (Pagination)** | Điểm cộng | Tự động lần theo thẻ `<li class="next"> > a` và dùng `urljoin` để cào đủ 30 quotes qua 3 trang kèm delay hợp lý. |
| **Chống trùng lặp (Unique Upsert)** | Điểm cộng | Khởi tạo `Unique Index` cho trường `text` và áp dụng thành công `update_one(..., upsert=True)`. Chạy lại script nhiều lần không tăng thêm document rác. |

---

## 5. Hướng Dẫn nộp bài

1. **Yêu cầu:**: Tạo file tên `[ten]_homework_buoi8.ipynb`(Ví dụ: `DungPM_homework_buoi8.ipynb`), bao gồm:
  - Mã nguồn kèm giải thích.
  - Các ảnh màn hình hiển thị:
    - Dữ liệu đã lưu hiển thị trực quan trên **Extension MongoDB trên IDE** (hoặc MongoDB Compass / `mongosh`).
    - Terminal chạy script in ra kết quả truy vấn và bảng DataFrame thành công.
2. **Hình thức nộp:**
  - Tạo thư mục theo cấu trúc và đẩy lên thư mục `Buoi_08/BTVN` trên repo.
3. **Hạn chót (Deadline):** Trước buổi học tiếp theo.
