# Buổi 8 — Data Crawling & Lưu Trữ với MongoDB

> **Đối tượng:** Team AI ProPTIT D24  
> **Thời lượng dự kiến:** 120 phút  
> **Tài liệu đồng hành:** [Dàn ý bài giảng (lesson_08_plan.md)](lesson_08_plan.md) | [Danh mục tài liệu đọc (reading_list.md)](reading_list.md)  
> **Định hướng chuyên môn:** Kỹ năng kỹ thuật dữ liệu thực chiến dành cho Kỹ sư AI (Data Engineering for AI Engineers) — ưu tiên bản chất mã nguồn, phân tích chuyên sâu các packages/hàm và kiến trúc luồng dữ liệu End-to-End.

---

### Bảng Phân Bổ Thời Gian Chi Tiết (Lecture Timeline - 120 phút)

| Phần | Nội dung chính | Thời lượng | Trọng tâm sư phạm & Kỹ thuật |
| :--- | :--- | :---: | :--- |
| **Phần 1** | Khởi động & Kiến trúc Thu thập Dữ liệu cho AI | **15 phút** | Tư duy Data-Centric AI, vòng đời dữ liệu, phân tích và so sánh 3 chiến lược crawl, đạo đức thu thập (`robots.txt`). |
| **Phần 2** | Kỹ thuật Crawl Thực chiến (3 Options) | **45 phút** | • Option 1: Static Scraping (`requests` + `bs4`) (15')<br>• Option 2: Dynamic Scraping (`playwright`) (15')<br>• Option 3: Network API Sniffing / Reverse Engineering (10')<br>• Kỹ thuật chống bị chặn (Anti-bot, Header Spoofing, Backoff) (5') |
| **Phần 3** | Lưu trữ Bán cấu trúc với MongoDB & `pymongo` | **40 phút** | • Bản chất NoSQL Document vs RDBMS cho AI Data (10')<br>• Thực hành `pymongo` CRUD, Query Operators, Kỹ thuật Upsert (20')<br>• Indexing & Aggregation Pipeline phân tích dữ liệu (10') |
| **Phần 4** | Xây dựng End-to-End Pipeline & Cầu nối AI | **10 phút** | Ghép nối luồng: Crawl $\rightarrow$ Ingest MongoDB $\rightarrow$ Query ra Pandas DataFrame phục vụ Model Training / RAG. |
| **Phần 5** | Tổng kết, Q&A & Giao Bài tập Thực tế | **10 phút** | Đúc kết sai lầm thường gặp (Pitfalls) và hướng dẫn bài tập về nhà. |

---

## 1. Khởi động — Tại sao kỹ sư AI phải biết cào dữ liệu? (15')

> 💡 **Ví dụ mở đầu:** "Giả sử bạn muốn xây một hệ thống phân tích cảm xúc đánh giá sản phẩm trên Shopee, hoặc một mô hình LLM trả lời câu hỏi luật giao thông Việt Nam — dữ liệu lấy từ đâu?"
>
> **Trình bày:** Trong môi trường công nghiệp thực tế, 80% thời gian của một kỹ sư AI dành cho việc thu thập, làm sạch và chuẩn bị dữ liệu (tư duy Data-Centric AI), chứ không chỉ là ngồi viết code mô hình hay tuning siêu tham số. AI không có dữ liệu tốt thì cũng giống như siêu xe không có xăng.

### 1.1 Data Crawling nằm ở đâu trong pipeline AI?

Một hệ thống AI hiện đại vận hành giống như một *chuỗi cung ứng dữ liệu khép kín*. Hãy nhìn vào bức tranh tổng thể dưới đây:

```text
[Web / App / API bên ngoài]
         │
         ▼  (Data Crawling / Thu thập)
[Dữ liệu thô — HTML, JSON, Text]
         │
         ▼  (Đẩy vào NoSQL — MongoDB)
[Data Lake / Kho dữ liệu thô]
         │
         ▼  (Lọc rác, loại trùng, chuẩn hoá)
[Dữ liệu sạch — Pandas DataFrame]
         │
         ├───► Feature Store / Tokenization ──► Huấn luyện Model (ML/DL)
         └───► Embedding Model ────────────────► Vector DB / RAG System
```

**Giải thích chi tiết luồng dữ liệu (Pipeline):**
1. **Thu thập (Crawling):** Chúng ta kéo dữ liệu từ các nguồn bên ngoài (Web, App) về. Lúc này, dữ liệu là "thô" và hỗn độn: HTML chứa đầy thẻ div, JSON thừa/thiếu trường, text lẫn nhiều ký tự lạ.
2. **Lưu trữ thô (Data Lake):** Ta không đẩy ngay dữ liệu này vào CSDL quan hệ (SQL) vì cấu trúc chưa ổn định. Ta dùng **MongoDB (NoSQL)** làm "hồ chứa" vì nó chấp nhận mọi cấu trúc linh hoạt (Dynamic Schema).
3. **Tiền xử lý & Chuẩn hóa:** Kỹ sư AI sẽ kéo dữ liệu từ MongoDB ra, sử dụng Pandas để làm sạch, xử lý missing values, loại bỏ nhiễu và định dạng lại cấu trúc.
4. **Đầu ra cho AI:** Lúc này, dữ liệu sạch (Pandas DataFrame) mới được đưa vào các khâu tiếp theo:
   - Đưa vào ML/DL Model để phân tích, dự đoán.
   - Hoặc biến thành vector đưa vào Vector Database cho hệ thống RAG (Chatbot LLM).

**Nhấn mạnh:** Định lý kinh điển của AI là **"Garbage In, Garbage Out"** (Rác vào thì Rác ra). Nếu dữ liệu đầu vào sai lệch hoặc trùng lặp, toàn bộ mô hình toán học phía sau sẽ sụp đổ. Do đó, kỹ năng cào dữ liệu chuẩn xác và chống trùng lặp là vũ khí sống còn.

### 1.2 Ba chiến lược tiếp cận crawl dữ liệu

Tùy vào cấu trúc của trang web, chúng ta có 3 "vũ khí" khác nhau:

| Tiêu chí | **Option 1:** Static Scraping | **Option 2:** Dynamic Scraping | **Option 3:** API Sniffing |
| :--- | :--- | :--- | :--- |
| **Công cụ chính** | `requests`, `BeautifulSoup4`, `lxml` | `playwright`, `selenium` | Browser DevTools (F12), `requests` |
| **Cơ chế hoạt động** | Tải mã HTML tĩnh từ server và parse cây DOM | Khởi chạy trình duyệt thật (Headless), thực thi mã JS | Bắt trực tiếp Endpoint API trả về JSON ngầm |
| **Tốc độ thực thi** | **Rất nhanh** (~0.1s - 0.5s / request) | **Chậm** (~1s - 5s / trang do render JS) | **Siêu tốc** (~0.05s - 0.2s / request) |
| **Tiêu tốn tài nguyên** | Cực thấp (Chỉ cần CPU & Network nhẹ) | Rất cao (Tốn RAM, CPU do chạy Chrome/Chromium) | Cực thấp (Chỉ gửi HTTP Request thuần) |
| **Độ phức tạp bóc tách** | Trung bình (Viết CSS Selector / XPath) | Trung bình (Tương tác nút, cuộn trang, selector) | **Dễ nhất** (Dữ liệu trả về sẵn kiểu Dictionary/List) |
| **Trường hợp áp dụng** | Trang tin tức, blog, tài liệu HTML tĩnh | Trang web SPA (React, Vue, Angular), cuộn vô hạn | Bất kỳ web nào nạp data qua AJAX/Fetch XHR |

### 1.3 Đạo đức và Pháp lý khi Thu thập Dữ liệu (Polite Crawling)

#### 1.3.1 Bản Chất: Tại Sao Cần "Polite Crawling"?
Khi viết mã nguồn cào dữ liệu bằng Python (`requests`, `playwright`), tốc độ xử lý của máy tính vượt xa hành vi của người dùng thông thường:
- Một vòng lặp `for` không kiểm soát có thể bắn **hàng chục đến hàng trăm request mỗi giây** vào máy chủ mục tiêu.
- Nếu không có cơ chế hãm tốc, hành động này sẽ vô tình trở thành một cuộc **tấn công từ chối dịch vụ (DoS - Denial of Service)**, làm cạn kiệt băng thông, CPU, RAM và kết nối cơ sở dữ liệu của đối tác, khiến website bị sập hoặc ngừng phục vụ người dùng thật.

Do đó, **Polite Crawling (Cào dữ liệu lịch sự / văn minh)** là bộ quy tắc đạo đức, kỹ thuật và pháp lý mà mọi kỹ sư AI chuyên nghiệp bắt buộc phải tuân thủ nhằm:
1. **Bảo vệ hệ thống đối tác:** Giữ lưu lượng ở mức an toàn, không gây ảnh hưởng đến hiệu năng máy chủ.
2. **Bảo vệ crawler của chính mình:** Tránh bị hệ thống tường lửa ứng dụng web (WAF như Cloudflare, Akamai) kích hoạt cơ chế phòng thủ: trả về mã lỗi `429 Too Many Requests`, thử thách Captcha hoặc đưa IP vào danh sách đen (IP Blacklist) vĩnh viễn.
3. **Đảm bảo tính pháp lý & đạo đức dữ liệu AI:** Thu thập dữ liệu minh bạch, tôn trọng điều khoản dịch vụ (Terms of Service - ToS) và bản quyền dữ liệu khi huấn luyện mô hình.

#### 1.3.2 Ba Nguyên Tắc Cốt Lõi Của Polite Crawling

##### ① Đọc và Tôn Trọng File `robots.txt`
Trước khi viết bất kỳ dòng mã cào nào trên một domain mới, bước đầu tiên của kỹ sư là truy cập vào `https://<domain>/robots.txt` (Robots Exclusion Protocol):
```txt
# Ví dụ cấu trúc file https://domain.com/robots.txt
User-agent: *
Disallow: /api/private/
Disallow: /checkout/
Disallow: /admin/
Allow: /catalog/
Crawl-delay: 2
```

- **`User-agent: *`**: Quy tắc áp dụng cho mọi bot/crawler (trừ khi có khai báo riêng cho `Googlebot`, `Bingbot`...).
- **`Disallow: /checkout/`**: Đường dẫn **nghiêm cấm** thu thập (thường là dữ liệu nhạy cảm, giỏ hàng, trang thanh toán, thông tin cá nhân).
- **`Allow: /catalog/`**: Khu vực công khai cho phép lập chỉ mục hoặc thu thập.
- **`Crawl-delay: 2`**: Yêu cầu giãn cách tối thiểu giữa 2 request liên tiếp gửi lên máy chủ là **2 giây**.

> 💡 **Kỹ thuật thực chiến:** Trong Python, ta có thể dùng module có sẵn `urllib.robotparser` để tự động kiểm tra xem một URL có được phép cào hay không:
> ```python
> import urllib.robotparser
> 
> rp = urllib.robotparser.RobotFileParser()
> rp.set_url("https://books.toscrape.com/robots.txt")
> rp.read()
> 
> # Kiểm tra quyền cào URL chỉ định
> can_fetch = rp.can_fetch("MyAICrawler/1.0", "https://books.toscrape.com/catalogue/page-1.html")
> print(f"Được phép cào URL: {can_fetch}")
> ```

##### ② Thêm Độ Trễ Ngẫu Nhiên Giữa Các Request (Random Delay / Jitter)
Nếu gửi request với khoảng thời gian cố định lặp lại đều đặn (VD: `time.sleep(1.0)` chính xác từng mili-giây), các thuật toán nhận diện bot của WAF sẽ phát hiện ngay mẫu hành vi máy móc (Mechanical Pattern).

**Giải pháp chuẩn công nghiệp:** Kết hợp độ trễ tối thiểu với một biến thiên ngẫu nhiên (Random Jitter):
```python
import time
import random

# Giãn cách ngẫu nhiên từ 1.0 đến 3.0 giây giữa mỗi trang
delay_time = random.uniform(1.0, 3.0)
print(f"[*] Nghỉ lịch sự {delay_time:.2f}s trước request tiếp theo...")
time.sleep(delay_time)
```
Kỹ thuật này vừa giúp máy chủ có thời gian giải phóng tài nguyên (Connection Pool), vừa tạo luồng truy cập tự nhiên giống hệt hành vi người dùng thật đang đọc nội dung.

##### ③ Định Danh Rõ Ràng Qua Header `User-Agent`
Mặc định thư viện Python `requests` gửi header nhận diện:
```http
User-Agent: python-requests/2.31.0
```
Phần lớn các web server hiện đại tự động chặn thẳng tay mã lỗi `403 Forbidden` đối với header này vì xếp nó vào diện bot quét lỗ hổng bảo mật.

Kỹ sư cào dữ liệu cần chủ động thiết lập `User-Agent` hợp lệ (giả lập trình duyệt chuẩn) hoặc định danh bot học thuật rõ ràng:
```python
headers = {
    # Giả lập trình duyệt chuẩn của người dùng thật
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
}
```
*(Nếu là bot thu thập cho tổ chức học thuật/nghiên cứu, có thể định danh: `User-Agent: ProPTIT_AI_Research_Bot/1.0 (+https://proptit.com/bot-info)` để webmaster có thể liên hệ khi cần).*

---

## 2. Kỹ thuật Crawl Thực chiến dành cho AI Engineer (45 phút)

Sau khi nắm vững kiến trúc dữ liệu và các nguyên tắc lịch sự, chúng ta sẽ đi sâu vào **3 chiến lược thu thập dữ liệu thực chiến** tương ứng với 3 cấp độ phức tạp của thế giới Web, cùng các kỹ thuật phòng vệ chống bị chặn (Anti-blocking) chuẩn công nghiệp.

---

### 2.1 Option 1 — Static Scraping với `requests` & `BeautifulSoup4`

Đây là giải pháp ưu tiên hàng đầu cho các website áp dụng mô hình **Server-Side Rendering (SSR)** truyền thống (báo chí, blog, tài liệu, web thương mại điện tử đơn giản). Toàn bộ nội dung văn bản đã được server nhúng sẵn vào mã HTML trả về.

#### 2.1.1 Bản Chất Cây DOM & So Sánh Các Bộ Parser
Trình duyệt hiển thị trang web bằng cách chuyển mã HTML thô thành cấu trúc cây phân cấp gọi là **DOM (Document Object Model)**:
```
                     <html>
                    /      \
               <head>      <body>
                 |         /     \
              <title>   <header> <main>
                                 /    \
                           <article>  <article>
```
Khi dùng `BeautifulSoup`, ta cần chọn một "động cơ" (Parser Engine) để dựng cây DOM này:

| Bộ Parser | Cú pháp khởi tạo | Tốc độ | Khả năng tự sửa lỗi HTML hỏng | Thư viện nền tảng | Đánh giá & Khuyến nghị |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **`lxml`** | `BeautifulSoup(html, 'lxml')` | **Siêu tốc** (~0.05s) | Cực tốt (Linh hoạt) | C / `libxml2` | **Khuyến nghị số 1:** Luôn dùng cho AI Crawler quy mô lớn. |
| **`html.parser`** | `BeautifulSoup(html, 'html.parser')` | Trung bình (~0.2s) | Khá tốt | Python built-in | Tiện lợi khi không thể cài thêm C-extensions, nhưng chậm hơn. |
| **`html5lib`** | `BeautifulSoup(html, 'html5lib')` | Rất chậm (~0.8s) | Hoàn hảo (Chuẩn W3C) | Python thuần | Chỉ dùng khi HTML quá nát, các parser khác đều vỡ cây DOM. |

#### 2.1.2 Làm Chủ CSS Selector Nâng Cao & Kỹ Thuật XPath

Để trích xuất dữ liệu chính xác, kỹ sư cần làm chủ 2 công cụ định vị: **CSS Selector** (tiện lợi, ngắn gọn) và **XPath** (mạnh mẽ, định vị hai chiều).

##### Bảng Tra Cứu CSS Selector Thực Chiến:
- **Chọn theo thẻ, class, id:** `article`, `.product_pod`, `#main-content`
- **Con trực tiếp (`>`):** `div.product_price > p.price_color` (chỉ chọn thẻ `p` là con cấp 1 của `div`).
- **Hậu duệ bất kỳ (khoảng trắng):** `article.product_pod a` (chọn mọi thẻ `a` nằm bên trong `article`).
- **Lọc theo thuộc tính HTML:**
  - Khớp chính xác: `a[target="_blank"]`
  - Bắt đầu bằng: `a[href^="http"]` (chỉ lấy link tuyệt đối)
  - Kết thúc bằng: `img[src$=".jpg"]` (chỉ lấy ảnh đuôi jpg)
  - Chứa chuỗi con: `article[class*="product"]`
- **Pseudo-classes (Bộ chọn vị trí):**
  - `table tr:first-child` (hàng đầu tiên)
  - `ul.nav > li:nth-of-type(3)` (phần tử thứ 3 trong danh sách)

##### Khi Nào Bắt Buộc Phải Dùng XPath Thay Vì CSS Selector?
CSS Selector chỉ cho phép duyệt **từ cha xuống con (một chiều)**. Khi gặp các trường hợp sau, ta bắt buộc phải dùng XPath (thông qua `lxml.etree` hoặc `playwright.locator`):
1. **Tìm phần tử dựa vào nội dung chữ (Text Content):**  
   VD: Tìm thẻ nút bấm có chữ "Thêm vào giỏ": `//button[contains(text(), 'Thêm vào giỏ')]`
2. **Đi ngược lên phần tử cha hoặc tổ tiên (Axis Traversal):**  
   VD: Từ thẻ tiêu đề `<h3>`, đi ngược lên thẻ bao bọc ngoài cùng: `//h3/ancestor::div[@class='card']`
3. **Tìm phần tử anh em đứng trước:** `//td[text()='Giá bán']/preceding-sibling::td`

#### 2.1.3 Kỹ Thuật Xử Lý Phân Trang (Pagination) & Chuẩn Hóa URL
Website thực tế thường chia dữ liệu ra hàng chục đến hàng trăm trang. Có 2 mô hình phân trang chính:

1. **Phân trang tham số (Predictable Pattern):** URL có quy luật cố định (VD: `page-1.html`, `?page=2`). Ta dùng vòng lặp `for page in range(1, max_pages + 1)`.
2. **Phân trang bám theo nút "Next" (Dynamic Next Pointer):** Khi không biết trước tổng số trang, crawler sẽ tìm link của nút Next (`a[rel="next"]` hoặc thẻ `li.next > a`) để cào trang tiếp theo cho đến khi không còn nút Next thì dừng vòng lặp `while True`.

> [!WARNING]
> **Hiểm họa URL tương đối:** Thẻ HTML thường chứa link tương đối như `href="category/books_1/index.html"` hoặc `href="../page-2.html"`. Nếu dùng phép cộng chuỗi thông thường `base_url + href`, crawler sẽ sinh ra link rác bị lỗi 404.  
> **Giải pháp chuẩn:** Luôn dùng `urllib.parse.urljoin(base_url, rel_link)` để tự động chuẩn hóa URL tuyệt đối hợp lệ.

#### 2.1.4 Mã Nguồn Triển Khai Thực Tế (Ngắn Gọn & Đầy Đủ Hàm Cốt Lõi)
Ví dụ bóc tách dữ liệu từ `books.toscrape.com` bao quát toàn bộ quy trình:

```python
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time, random
import re

base_url = "http://books.toscrape.com/catalogue/page-1.html"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"}

# 1. Gửi HTTP GET và kiểm tra trạng thái phản hồi
response = requests.get(base_url, headers=headers, timeout=10)
response.raise_for_status()

# 2. Dựng cây phân tích cú pháp DOM bằng lxml engine
# Chú ý: Truyền response.content (dạng bytes) để BeautifulSoup tự giải mã chuẩn UTF-8 từ thẻ <meta>
soup = BeautifulSoup(response.content, "lxml")
books = []

# 3. Duyệt qua danh sách thẻ sản phẩm và bóc tách
for card in soup.select("article.product_pod"):
    # Lấy thuộc tính title và chuẩn hóa URL tuyệt đối
    title_tag = card.select_one("h3 > a")
    title = title_tag.get("title", title_tag.get_text(strip=True)) if title_tag else "Unknown"
    full_url = urljoin(base_url, title_tag.get("href", "")) if title_tag else ""
    
    # Trích xuất số thực: dùng Regex tách số để tránh lỗi ký tự tiền tệ hoặc lỗi encoding
    price_str = card.select_one("p.price_color").get_text(strip=True)
    price_match = re.search(r"[\d.]+", price_str)
    price = float(price_match.group()) if price_match else 0.0
    
    books.append({"title": title, "price": price, "url": full_url})

# 4. Polite delay ngẫu nhiên giữa các trang
time.sleep(random.uniform(1.0, 2.0))
print(f"[OK] Thu thập thành công {len(books)} cuốn sách. Bản ghi đầu:", books[0])
```

#### 2.1.5 Các Sai Lầm Phổ Biến (Pitfalls) Khi Dùng BS4
1. **Lỗi `AttributeError: 'NoneType' object has no attribute 'get_text'`:** Do thẻ HTML không tồn tại trên trang (ví dụ sản phẩm không có giảm giá nên không có thẻ `.old-price`).  
   $\rightarrow$ **Khắc phục:** Luôn kiểm tra `tag is not None` trước khi truy cập hoặc viết hàm bóc tách phòng vệ như ví dụ trên.
2. **Nhầm lẫn giữa `.get_text()` và thuộc tính `tag['href']`:** `.get_text()` lấy chữ hiển thị nằm giữa thẻ mở và thẻ đóng (`<a>Nội dung chữ</a>`), còn `['href']` hoặc `.get('href')` lấy giá trị thuộc tính nằm trong thẻ mở (`<a href="link.html">`).
3. **Bẫy giải mã Encoding (`response.text` vs `response.content`) & Ký tự tiền tệ (`Â51.77`):**  
   - Khi server không khai báo `charset=utf-8` trong HTTP Header, thư viện `requests` sẽ mặc định giải mã theo chuẩn `ISO-8859-1`. Ký tự `£` (UTF-8 bytes `\xc2\xa3`) bị giải mã sai thành `Â£`! Nếu chỉ dùng `.replace("£", "")`, chuỗi còn lại là `'Â51.77'` và ép kiểu `float()` sẽ gây ra lỗi `ValueError`.  
   $\rightarrow$ **Khắc phục:** Truyền thẳng `response.content` (dạng byte thô) vào `BeautifulSoup(response.content, "lxml")` để parser tự đọc đúng encoding UTF-8 từ thẻ `<meta>`, đồng thời dùng `re.search(r"[\d.]+", text)` để bóc tách số thực an toàn tuyệt đối.

---

### 2.2 Option 2 — Dynamic Scraping với `playwright`

Khi gặp các website dạng **Single Page Application (SPA)** viết bằng React, Vue, Angular, nội dung hoàn toàn không có trong mã HTML tải về lần đầu. Trình duyệt bắt buộc phải chạy JavaScript để gọi API ngầm rồi mới vẽ dữ liệu lên màn hình. Đây là lúc ta cần tới **Playwright**.

#### 2.2.1 Kiến Trúc 3 Tầng Siêu Nhẹ: Browser $\rightarrow$ BrowserContext $\rightarrow$ Page
Khác với Selenium khởi chạy mỗi cửa sổ Chrome là một tiến trình nặng nề độc lập, Playwright phân chia thành 3 lớp phân cấp:

```
[Browser Instance] (Chỉ mở 1 tiến trình Chromium ngầm duy nhất)
   ├── [BrowserContext 1] (Phiên ẩn danh 1: Cookie, Cache, Session riêng) ──► [Page (Tab 1)]
   └── [BrowserContext 2] (Phiên ẩn danh 2: IP Proxy, User-Agent riêng)   ──► [Page (Tab 2)]
```
- **Lợi ích:** Tiết kiệm tới **80% bộ nhớ RAM** khi cào đa luồng song song, vì hàng chục `BrowserContext` có thể dùng chung một binary Chromium bên dưới.

#### 2.2.2 Cơ Chế Auto-waiting & Actionability Checks
Một trong những nguyên nhân khiến script Selenium hay gãy là lỗi `ElementNotInteractableException` (phần tử đã có trong HTML nhưng chưa hiển thị hoặc đang bị animation làm mờ).  
Playwright tự động kiểm tra **5 điều kiện hành động (Actionability Checks)** trước khi thực hiện click/fill:
1. **Attached:** Phần tử đã được gắn vào DOM tree.
2. **Visible:** Phần tử có kích thước khác 0 và không bị ẩn bởi CSS (`display: none`, `visibility: hidden`).
3. **Stable:** Phần tử đã đứng yên, không còn chạy hiệu ứng animation CSS.
4. **Receives Events:** Phần tử không bị các modal/overlay khác che khuất lên trên.
5. **Enabled:** Phần tử không bị vô hiệu hóa bởi thuộc tính `disabled`.

#### 2.2.3 Tương Tác SPA: Cuộn Vô Hạn, Form Input & Click Nút
Dưới đây là các câu lệnh điều khiển cốt lõi:
- `page.fill("input[name='search']", "Machine Learning")`: Xóa nội dung cũ và gõ chuỗi mới vào ô tìm kiếm.
- `page.click("button[type='submit']")`: Click chuột vào nút submit.
- `page.keyboard.press("Enter")`: Nhấn phím Enter bàn phím.
- `page.wait_for_selector(".result-card", timeout=5000)`: Chờ tối đa 5 giây cho đến khi kết quả xuất hiện.
- `page.evaluate("window.scrollTo(0, document.body.scrollHeight);")`: Ra lệnh cho browser cuộn chuột xuống tận đáy trang.

#### 2.2.4 Tuyệt Kỹ Tăng Tốc: Chặn Tài Nguyên Thừa (Resource Blocking)
Khi cào dữ liệu cho AI, ta chỉ cần văn bản và số liệu, **hoàn toàn không cần tải ảnh, font chữ hay các script quảng cáo**. Việc tải ảnh khiến tốc độ chậm đi 3-5 lần và tốn hàng gigabyte băng thông.

Playwright cho phép ta chặn (abort) các request không cần thiết bằng cơ chế định tuyến mạng:

```python
# Chặn toàn bộ ảnh, media, font và stylesheet nặng
def block_unnecessary_resources(route):
    if route.request.resource_type in ["image", "media", "font", "stylesheet"]:
        route.abort()
    else:
        route.continue_()

# Kích hoạt trên page
page.route("**/*", block_unnecessary_resources)
```

#### 2.2.5 Mã Nguồn Triển Khai Thực Tế (Ngắn Gọn & Đầy Đủ Hàm Cốt Lõi)
Ví dụ cào các câu danh ngôn kết xuất bằng JavaScript từ `https://quotes.toscrape.com/scroll`:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 1. Khởi chạy browser ngầm (headless) và mở tab mới
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 2. Điều hướng tới trang web và chờ mạng nạp xong (networkidle)
    page.goto("https://quotes.toscrape.com/scroll", wait_until="networkidle")
    
    # 3. Cuộn trang 2 lần để kích hoạt nạp thêm dữ liệu (Infinite Scroll)
    for _ in range(2):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        page.wait_for_timeout(1500)
        
    # 4. Trích xuất danh sách phần tử qua locator
    quotes = []
    for item in page.locator("div.quote").all():
        quotes.append({
            "text": item.locator("span.text").inner_text().strip("“”\""),
            "author": item.locator("small.author").inner_text().strip()
        })
        
    browser.close()
    print(f"[✓] Lấy thành công {len(quotes)} câu trích dẫn. Bản ghi đầu:", quotes[0])
```

---

### 2.3 Option 3 — Network API Sniffing (Reverse Engineering - "Tuyệt Chiêu Tối Thượng")

Đây là kỹ năng phân loại giữa một người cào web "nghiệp dư" và một **Kỹ sư Dữ liệu AI chuyên nghiệp**.  
Thay vì khởi chạy cả trình duyệt Chromium nặng nề để render HTML rồi parse cây DOM, ta đi thẳng vào nguồn: **Bắt trộm chính API ngầm mà trang web dùng để nạp dữ liệu cho giao diện.**

```
[Trình duyệt Web] ──(Fetch / XHR ngầm)──► [Backend Internal API] ──(JSON sạch)──► [Trình duyệt Web]
       ▲                                               │
       │                                               ▼
       └────────────── (Crawler giả lập Request) ───────┘
```

#### 2.3.1 Tại Sao API Sniffing Luôn Là Lựa Chọn Số 1?
1. **Tốc độ cực hạn:** Nhanh gấp **20 - 50 lần** so với Playwright (chỉ mất ~0.05s / request).
2. **Không tiêu tốn tài nguyên:** Không cần mở trình duyệt, tiêu thụ RAM dưới 15MB.
3. **Dữ liệu sạch hoàn hảo:** Server trả về sẵn định dạng JSON (Dictionary / List), có sẵn kiểu số nguyên, số thực, mảng lồng nhau; không cần viết CSS Selector bóc tách thẻ HTML.
4. **Bền vững trước thay đổi UI:** Khi công ty đổi giao diện, đổi class CSS thì code bóc tách DOM sẽ gãy hoàn toàn. Nhưng Backend API của họ vẫn giữ nguyên cấu trúc JSON để phục vụ ứng dụng mobile/web.

#### 2.3.2 Quy Trình 6 Bước "Dịch Ngược" API Bằng Chrome DevTools
1. Mở trình duyệt Chrome, vào trang web cần cào.
2. Nhấn phím `F12` (hoặc `Ctrl + Shift + I`) để mở **DevTools** $\rightarrow$ Chuyển qua tab **Network**.
3. Bấm vào bộ lọc **Fetch/XHR** để loại bỏ các request tải ảnh, css, js tĩnh.
4. Thao tác trên trang web (bấm nút "Xem thêm", chuyển trang 2, gõ tìm kiếm).
5. Quan sát danh sách request xuất hiện: Nhấp vào từng request, xem tab **Preview** hoặc **Response**. Khi thấy dữ liệu dạng JSON chứa thông tin bài viết/sản phẩm bạn cần $\rightarrow$ Bạn đã tìm trúng "mỏ vàng"!
6. Chuột phải vào tên request đó $\rightarrow$ Chọn **Copy** $\rightarrow$ **Copy as cURL (bash)** hoặc sao chép **Request URL**, **Headers** và **Payload**.

#### 2.3.3 Mã Nguồn Triển Khai Thực Tế (Ngắn Gọn & Đầy Đủ Hàm Cốt Lõi)
Ví dụ gọi một REST API ngầm trả về danh sách các loại cà phê:

```python
import requests
import pandas as pd

api_url = "https://api.sampleapis.com/coffee/hot"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0",
    "Accept": "application/json"
}

# 1. Gọi trực tiếp API Endpoint ngầm
response = requests.get(api_url, headers=headers, timeout=10)
response.raise_for_status()

# 2. Nhận dữ liệu JSON (không cần BeautifulSoup bóc tách DOM!)
data = response.json()

# 3. Làm phẳng mảng JSON lồng nhau thành Pandas DataFrame cho AI
df = pd.json_normalize(data)
print(f"[✓] Lấy thành công {len(df)} bản ghi JSON. Xem trước:\n", df[["title", "ingredients"]].head(2))
```

#### 2.3.4 Thách Thức Khi Sniff API & Cách Khắc Phục
- **Request Payload phức tạp (POST JSON / GraphQL):** Nhiều web dùng `POST` kèm GraphQL Query. Ta chỉ cần sao chép nguyên khối JSON trong tab **Payload** của DevTools và truyền vào `requests.post(url, json=payload)`.
- **Dynamic Signature / Token:** Một số trang (như TikTok, Shopee) tạo một chuỗi băm `signature` ngẫu nhiên trong header qua mã WebAssembly/JS obfuscated. Khi gặp rào cản mã hóa này, ta chuyển sang kết hợp **Playwright để lấy Token phiên làm việc trước**, sau đó mới gọi API, hoặc fallback về Option 2.

---

### 2.4 Chiến Lược Phòng Chống Bị Chặn (Anti-Blocking Best Practices)

Khi triển khai thu thập dữ liệu ở quy mô hàng trăm ngàn bản ghi, bạn sẽ đối đầu trực tiếp với các hệ thống tường lửa ứng dụng web hiện đại như **Cloudflare**, **Akamai**, **AWS WAF** hoặc **Datadome**. Dưới đây là bộ giải pháp phòng thủ toàn diện:

#### 2.4.1 Xoay Vòng User-Agent (User-Agent Rotation)
Không bao giờ dùng một User-Agent đơn lẻ cho toàn bộ 100.000 request. Sử dụng thư viện `fake-useragent` để mỗi request giả lập một thiết bị, hệ điều hành (Windows, macOS, Ubuntu) và trình duyệt khác nhau:

```python
from fake_useragent import UserAgent

ua = UserAgent(browsers=['chrome', 'edge', 'firefox'])

def get_random_headers():
    return {
        "User-Agent": ua.random,
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1" # Do Not Track header
    }
```

- Mỗi lần bạn gọi thuộc tính `ua.random`, nó sẽ tự động bốc ngẫu nhiên một danh tính theo các trình duyệt trong `ua`.
> Tại sao không chỉ gửi mỗi User-Agent, mà phải có các dòng khác?
- 
 

#### 2.4.2 Cơ Chế Thử Lại Với Exponential Backoff & Random Jitter
Khi gặp mã lỗi `429 Too Many Requests` (quá tải rate limit) hoặc `503 Service Unavailable`, hành vi spam request liên tục sẽ khiến IP của bạn bị đưa vào Blacklist vĩnh viễn.  
Kỹ sư phải lùi bước và chờ đợi theo hàm số mũ tăng dần kết hợp biến thiên ngẫu nhiên (**Full Jitter**):

$$\text{Wait Time} = t_{\text{base}} \times 2^{\text{attempt}} + \text{jitter}$$

*Trong đó:*
- $t_{\text{base}}$: Thời gian cơ sở (thường chọn từ $1.0\text{s}$ đến $2.0\text{s}$).
- $\text{attempt}$: Số lần đã thử lại thất bại ($0, 1, 2, 3...$).
- $\text{jitter}$: Khoảng trễ ngẫu nhiên ngắt nhịp (random float từ $0.1\text{s}$ đến $1.0\text{s}$), ngăn chặn việc hàng ngàn request retry cùng một thời điểm.

```python
import requests, time, random

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"})

def fetch_with_backoff(url: str, max_retries: int = 3, t_base: float = 1.5):
    for attempt in range(max_retries):
        response = session.get(url, timeout=10)
        
        # 200 OK thành công
        if response.status_code == 200:
            return response
            
        # Gặp giới hạn request 429 hoặc quá tải 503 -> Lùi bước theo hàm số mũ
        if response.status_code in [429, 503]:
            wait = t_base * (2 ** attempt) + random.uniform(0.1, 0.5)
            print(f"[!] HTTP {response.status_code}. Chờ {wait:.2f}s trước khi thử lại lần {attempt + 1}...")
            time.sleep(wait)
            
    print(f"[X] Thất bại sau {max_retries} lần thử: {url}")
    return None
```

#### 2.4.3 Duy Trì Phiên Làm Việc (`requests.Session`)
Luôn khởi tạo đối tượng `requests.Session()` khi cào một chuỗi các trang liên quan.  
- **Ưu điểm 1:** Tự động giữ Cookie xuyên suốt (giúp vượt qua các bài kiểm tra session hợp lệ).
- **Ưu điểm 2:** Tận dụng **TCP Connection Pooling (HTTP Keep-Alive)**: Không phải thực hiện lại quá trình bắt tay 3 bước TCP và bắt tay SSL/TLS cho từng request, giúp tăng tốc độ mạng lên **200% - 300%** và tăng chỉ số tin cậy (Trust Score) trong mắt server.

#### 2.4.4 Xoay Vòng Địa Chỉ IP Qua Proxy (Proxy Rotation)
Dù bạn có đổi User-Agent hay lùi bước bao nhiêu, nếu gửi 50.000 request từ một địa chỉ IP duy nhất, WAF vẫn sẽ khóa cổng IP đó. Do đó, cào quy mô lớn đòi hỏi phải xoay vòng IP qua mạng lưới **Proxy**:
- **Datacenter Proxy:** Giá rẻ, tốc độ cao, nhưng dễ bị Cloudflare nhận diện dải IP trung tâm dữ liệu (AWS, DigitalOcean) và chặn.
- **Residential Proxy (Proxy Dân Cư):** Địa chỉ IP xuất phát từ các nhà mạng viễn thông thực tế (Viettel, VNPT, Comcast). Tỷ lệ vượt rào thành công lên tới **99%**.

*Cấu hình Proxy trong Python `requests`:*
```python
proxies = {
    "http": "http://username:password@proxy-server.com:8080",
    "https": "http://username:password@proxy-server.com:8080"
}
response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
```

#### 2.4.5 Che Giấu Dấu Vết Trình Duyệt Tự Động (Playwright Stealth)
Mặc định khi Playwright khởi chạy trình duyệt, biến JavaScript toàn cục `navigator.webdriver` sẽ có giá trị `true`. Các hệ thống chống bot chỉ cần một dòng lệnh JS để phát hiện và chặn đứng:
```js
if (navigator.webdriver) { blockRequest(); }
```
**Cách phòng thủ:**
1. Vô hiệu hóa cờ automation khi khởi tạo Playwright:
   ```python
   browser = p.chromium.launch(
       headless=True,
       args=["--disable-blink-features=AutomationControlled"]
   )
   ```
2. Sử dụng thư viện chuyên dụng `playwright-stealth` để xóa sạch toàn bộ dấu vết vân tay tự động (che giấu WebGL Vendor, Audio Fingerprint, Chrome runtime).

#### 2.4.6 Bảng Tổng Hợp Ma Trận Phòng Thủ (Troubleshooting Anti-Bot Matrix)

| Triệu chứng / Mã lỗi | Nguyên nhân gốc rễ | Biện pháp xử lý ngay lập tức |
| :--- | :--- | :--- |
| **HTTP 403 Forbidden** | User-Agent mặc định bị chặn hoặc thiếu Header bảo mật | Giả lập User-Agent trình duyệt thật; bổ sung thêm Header `Referer` và `Accept-Language`. |
| **HTTP 429 Too Many Requests** | Vượt ngưỡng tần suất gửi request (Rate Limit) | Áp dụng thuật toán **Exponential Backoff + Jitter**; tăng thời gian `time.sleep()`. |
| **Trang trắng (Empty DOM / No Data)** | Trang web render dữ liệu ngầm bằng JavaScript | Chuyển từ `bs4` sang **Playwright** (Option 2) hoặc bắt **API ngầm XHR** (Option 3). |
| **Gặp màn hình Captcha / Cloudflare Turnstile** | Hành vi bot bị phát hiện qua IP hoặc vân tay `navigator.webdriver` | Bật chế độ Stealth trong Playwright; xoay vòng địa chỉ IP qua **Residential Proxy**. |
| **Timeout / Connection Reset liên tục** | Server đối tác ngắt kết nối hoặc IP bị đưa vào Blacklist tạm thời | Dừng cào 15-30 phút; kiểm tra lại `robots.txt`; cấu hình lại proxy xoay vòng. |

---

## 3. Lưu trữ Dữ liệu Bán cấu trúc với MongoDB & `pymongo` (40 phút)

> 💡 **Gợi ý giảng dạy:** Đặt vấn đề so sánh trực quan: *"Dữ liệu chúng ta vừa cào được từ các trang web khác nhau: trang thì có thuộc tính `author`, trang thì không có; trang thì có danh sách ảnh `['img1.jpg', 'img2.jpg']`, trang thì chỉ có một ảnh đơn. Nếu dùng MySQL hoặc PostgreSQL, chúng ta phải `ALTER TABLE` liên tục hoặc để rất nhiều cột mang giá trị `NULL`. Làm sao để giải quyết?"* $\rightarrow$ Dẫn dắt sang MongoDB.

### 3.1 Bản Chất NoSQL Document Store vs RDBMS trong Khoa Học Dữ Liệu
Trong RDBMS (SQL), dữ liệu bị ép buộc vào một Schema cứng nhắc (Fixed Schema) với các hàng và cột phẳng. Mọi bản ghi đều phải tuân thủ nghiêm ngặt cấu trúc bảng.

Ngược lại, **MongoDB** lưu trữ dữ liệu dưới dạng **Document BSON (Binary JSON)**. Mỗi document là một cấu trúc dữ liệu dạng cây tự miêu tả (Self-describing) cho phép:
- **Dynamic Schema (Schema linh hoạt):** Hai document trong cùng một collection có thể có các trường (fields) hoàn toàn khác nhau.
- **Nested Structures (Cấu trúc lồng nhau):** Lưu trữ danh sách mảng (Arrays) hoặc Document con (Sub-documents) một cách tự nhiên mà không cần tạo bảng phụ và thực hiện phép `JOIN` tốn kém tài nguyên.

```
       Bảng Thuật Ngữ Đối Ứng:
┌───────────────────────────┬───────────────────────────┐
│     RDBMS (SQL Cổ Điển)   │     MongoDB (NoSQL BSON)  │
├───────────────────────────┼───────────────────────────┤
│ Database                  │ Database                  │
│ Table (Bảng)              │ Collection (Bộ sưu tập)   │
│ Row / Record (Hàng)       │ Document (Tài liệu BSON)  │
│ Column (Cột)              │ Field (Trường)            │
│ Primary Key (Khóa chính)  │ Khóa mặc định `_id`       │
│ JOIN                      │ Embedding / `$lookup`     │
└───────────────────────────┴───────────────────────────┘
```

---

### 3.2 Làm Chủ Thư Viện `pymongo`

> 💡 **Gợi ý công cụ:** Yêu cầu học viên cài Extension MongoDB trên VS Code / Cursor / Antigravity để xem dữ liệu ngay trong IDE, bỏ qua các GUI cồng kềnh như MongoDB Compass.

---

### 3.2 Làm chủ thư viện `pymongo` (Giải thích chi tiết)

#### Kết nối và Khởi tạo
```python
from pymongo import MongoClient
# Kết nối an toàn với timeout 5 giây
client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)

# Tự động tạo DB và Collection nếu chưa có
db = client["proptit_crawler"]
collection = db["books"]

# Kiểm tra kết nối thành công
try:
    client.admin.command('ping')
    print("[✓] Kết nối thành công tới MongoDB Server!")
except Exception as e:
    print(f"[!] Kết nối thất bại: {e}")
```

#### Truy vấn dữ liệu (Các toán tử bắt buộc nhớ)

- `collection.insert_one(document)`: Chèn một bản ghi duy nhất. Trả về đối tượng `InsertOneResult` chứa thuộc tính `inserted_id`.
- `collection.insert_many([doc1, doc2, ...])`: Chèn hàng loạt bản ghi (Batch Insert) — tối ưu hiệu năng vượt trội cho crawler.

Các toán tử của MongoDB có cú pháp bọc trong `$`.
- So sánh: `$eq` (=), `$gt` (>), `$lt` (<).
- Danh sách: `$in` (chứa trong).
- Chữ: `$regex` (khớp chuỗi).

```python
sample_book = {
    "title": "A Light in the Attic",
    "price": 51.77,
    "rating": 3,
    "in_stock": True,
    "url": "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    "tags": ["poetry", "children", "bestseller"]
}

# Chèn một document
result = collection.insert_one(sample_book)
print(f"[+] Đã chèn 1 bản ghi với _id tự sinh: {result.inserted_id}")
```

#### 3.2.3 Thao Tác Read & Các Toán Tử Truy Vấn (Query Operators)
- `collection.find_one(filter, projection)`: Trả về 1 document đầu tiên khớp điều kiện.
- `collection.find(filter, projection)`: Trả về một **Cursor** (con trỏ lặp) chứa các document thỏa mãn.

**Bảng Các Toán Tử Truy Vấn Cốt Lõi:**
- `$eq`: Bằng (`{"price": {"$eq": 20}}`)
- `$gt`, `$gte`: Lớn hơn, lớn hơn hoặc bằng (`{"price": {"$gt": 30}}`)
- `$lt`, `$lte`: Nhỏ hơn, nhỏ hơn hoặc bằng
- `$in`, `$nin`: Nằm trong / không nằm trong danh sách (`{"rating": {"$in": [4, 5]}}`)
- `$regex`: Tìm kiếm theo biểu thức chính quy (Pattern Matching) (`{"title": {"$regex": "^The", "$options": "i"}}`)
- `$exists`: Kiểm tra sự tồn tại của một trường (`{"tags": {"$exists": True}}`)

```python
# Ví dụ: Tìm các sách có giá > 40 và đánh giá 5 sao
# Projection: Bỏ trường _id (0), chỉ lấy title (1) và price (1)
query_filter = {
    "price": {"$gt": 40.0},
    "rating": 5
}
projection = {"_id": 0, "title": 1, "price": 1, "rating": 1}

cursor = collection.find(query_filter, projection)
for item in cursor:
    print(f"- Sách 5 sao giá cao: {item['title']} - {item['price']} GBP")
```

#### 3.2.4 Thao Tác Update & "Vũ Khí Sống Còn" Upsert trong Crawling
Trong thực tế, khi chạy một crawler định kỳ (ví dụ mỗi ngày cào 1 lần):
- Nếu dùng `insert_one()`, dữ liệu ngày hôm sau sẽ chèn đè bản ghi cũ dẫn đến trùng lặp dữ liệu khổng lồ.
- Ta cần kỹ thuật: **Nếu URL đã có trong DB $\rightarrow$ Cập nhật thông tin mới nhất (Giá, Tồn kho); nếu URL chưa có $\rightarrow$ Chèn mới.** Đó chính là **Upsert** (`update + insert`).

```python
# Cú pháp: collection.update_one(filter, update_doc, upsert=True)
updated_data = {
    "title": "A Light in the Attic",
    "price": 49.99,            # Giá giảm
    "in_stock": False,          # Hết hàng
    "last_updated": time.time()
}

res = collection.update_one(
    {"url": "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"},
    {"$set": updated_data},
    upsert=True
)

if res.matched_count > 0:
    print("[*] Đã tìm thấy bản ghi cũ và cập nhật thông tin thành công.")
elif res.upserted_id is not None:
    print(f"[+] Chưa có bản ghi, đã chèn mới với ID: {res.upserted_id}")
```

#### 3.2.5 Thao Tác Delete (Xóa Dữ Liệu)
```python
# Xóa các sách đã hết hàng và có giá dưới 10
delete_result = collection.delete_many({"in_stock": False, "price": {"$lt": 10.0}})
print(f"[-] Đã xóa {delete_result.deleted_count} bản ghi cũ.")
```

---

### 3.3 Tối Ưu Hóa & Xử Lý Nâng Cao

#### 3.3.1 Indexing (Chỉ Mục) trong MongoDB
Nếu một collection có 1.000.000 bản ghi, việc truy vấn không có Index sẽ dẫn đến **COLLSCAN** (Collection Scan - duyệt tuần tự từng file trên ổ cứng từ đầu đến cuối), thời gian truy vấn có thể mất hàng chục giây.

Khi tạo Index trên trường `url` (dùng cấu trúc cây B-Tree), MongoDB chỉ mất dưới **1 mili-giây** để tìm ra document:

```python
# Bắt buộc: Đánh Unique Index lên trường URL. Nó vừa giúp tìm cực nhanh, vừa làm hàng rào cuối cùng từ chối lưu trùng lặp.
collection.create_index([("url", 1)], unique=True)
print("[✓] Đã tạo Unique Index thành công trên trường 'url'!")

# Tạo Compound Index phục vụ tìm kiếm theo nhiều điều kiện kết hợp
collection.create_index([("price", 1), ("rating", -1)])
```

#### 3.3.2 MongoDB Aggregation Pipeline (Đường Ống Xử Lý Dữ Liệu)
Aggregation Pipeline là cơ chế xử lý dữ liệu mạnh mẽ của MongoDB, hoạt động tương tự như các thao tác `GROUP BY`, `SUM`, `AVG`, `HAVING` trong SQL hoặc `df.groupby()` trong Pandas nhưng được tính toán trực tiếp với hiệu năng C++ bên trong Database Engine:

```
[Documents] ──► [$match: Lọc] ──► [$group: Nhóm & Thống kê] ──► [$sort: Sắp xếp] ──► [Kết quả]
```

**Mã nguồn phân tích thống kê giá sách theo từng số sao đánh giá:**

```python
pipeline = [
    # Stage 1: Chỉ lọc những cuốn sách còn hàng trong kho
    {"$match": {"in_stock": True}},
    
    # Stage 2: Nhóm theo số sao (rating) và tính giá trung bình, đếm số lượng
    {
        "$group": {
        "_id": "$rating", 
            "average_price": {"$avg": "$price"},
            "min_price": {"$min": "$price"},
            "max_price": {"$max": "$price"},
            "total_books": {"$sum": 1}
        }
    },
    
    # Stage 3: Sắp xếp theo số sao giảm dần (5 -> 1)
    {"$sort": {"_id": -1}}
]

stats = list(collection.aggregate(pipeline))
print("\n--- Báo Cáo Thống Kê Phân Tích từ MongoDB Aggregation ---")
for s in stats:
    print(f"Đánh giá: {s['_id']} sao | Số lượng: {s['total_books']} cuốn | "
          f"Giá TB: {s['average_price']:.2f} GBP | Khoảng giá: [{s['min_price']} - {s['max_price']}] GBP")
```

---

## 4. Tích hợp End-to-End & Cầu nối AI (10')

### 4.1 Cầu Nối MongoDB $\longleftrightarrow$ Pandas DataFrame
Kỹ sư AI không huấn luyện mô hình trực tiếp trên cursor MongoDB, mà sẽ chuyển đổi các document đã được lọc và chuẩn hóa ra **Pandas DataFrame** để tiếp tục đưa vào Tokenizer, Sklearn, hoặc PyTorch Dataset.

```python
import pandas as pd
from pymongo import MongoClient

def export_mongodb_to_ai_dataframe(mongo_uri: str, db_name: str, coll_name: str) -> pd.DataFrame:
    """
    Truy vấn dữ liệu từ MongoDB và chuyển đổi trực tiếp thành Pandas DataFrame.
    Loại bỏ trường _id kiểu ObjectId để tránh lỗi Serialization.
    """
    client = MongoClient(mongo_uri)
    col = client[db_name][coll_name]
    
    # Lấy data (bỏ _id vì _id của Mongo là kiểu ObjectId, pandas/json hay báo lỗi)
    cursor = col.find({}, {"_id": 0})
    
    # Chuyển đổi cursor thành danh sách dictionary và khởi tạo DataFrame
    df = pd.DataFrame(list(cursor))
    
    client.close()
    return df

# Kiểm thử trích xuất dữ liệu
df_books = export_mongodb_to_ai_dataframe(
    mongo_uri="mongodb://localhost:27017/",
    db_name="proptit_ai_crawler",
    coll_name="crawled_books"
)

print("Kích thước DataFrame:", df_books.shape)
print(df_books.head(3))
```

### 4.2 Toàn Bộ Kiến Trúc Pipeline Khép Kín (Full Code Script)
Dưới đây là một script hoàn chỉnh kết nối trọn vẹn quy trình: **Crawl $\rightarrow$ Validate $\rightarrow$ Ingest MongoDB $\rightarrow$ Read to Pandas**:

```python
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient, UpdateOne
import pandas as pd
import time

def run_end_to_end_pipeline():
    # 1. Khởi tạo kết nối DB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["ai_production_db"]
    collection = db["ecommerce_catalog"]
    
    # Đảm bảo Unique Index chống trùng
    collection.create_index([("url", 1)], unique=True)
    
    # 2. Thu thập dữ liệu
    url = "http://books.toscrape.com/catalogue/category/books/science_22/index.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    
    cards = soup.select("article.product_pod")
    operations = []
    
    for card in cards:
        title = card.select_one("h3 > a")["title"]
        rel_link = card.select_one("h3 > a")["href"]
        full_url = f"http://books.toscrape.com/catalogue/{rel_link.replace('../', '')}"
        price = float(card.select_one("p.price_color").get_text(strip=True).replace("£", ""))
        
        doc = {
            "title": title,
            "url": full_url,
            "price": price,
            "category": "Science",
            "updated_at": time.time()
        }
        
        # Tạo thao tác Bulk Upsert cực nhanh
        operations.append(
            UpdateOne({"url": full_url}, {"$set": doc}, upsert=True)
        )
        
    # 3. Thực thi chèn/cập nhật hàng loạt (Bulk Write)
    if operations:
        result = collection.bulk_write(operations)
        print(f"[+] Bulk write hoàn tất: Chèn mới {result.upserted_count}, Cập nhật {result.modified_count}")
        
    # 4. Trích xuất ra DataFrame phục vụ huấn luyện mô hình
    df = pd.DataFrame(list(collection.find({"category": "Science"}, {"_id": 0})))
    print("\n--- Dữ liệu sẵn sàng cho AI Model Training ---")
    print(df.info())
    print(df.describe())
    
    client.close()

if __name__ == "__main__":
    run_end_to_end_pipeline()
```

---

## 5. Các lỗi thường gặp & Điểm Mấu Chốt (10')

### 5.1 Các lỗi "vỡ đầu" cần tránh (Pitfalls)

1. ❌ **Lỗi: `TypeError: Object of type ObjectId is not JSON serializable`**
   - **Nguyên nhân:** Khi dùng `pymongo`, trường `_id` mặc định có kiểu `bson.objectid.ObjectId`. Khi bạn dùng `json.dumps()` hoặc trả về response qua FastAPI, Python sẽ báo lỗi sập server vì JSON tiêu chuẩn không có kiểu dữ liệu này.
   - ✅ **Khắc phục:**
     - Cách 1: Sử dụng projection bỏ trường `_id` khi query: `collection.find({}, {"_id": 0})`.
     - Cách 2: Ép kiểu string trước khi serialize: `doc["_id"] = str(doc["_id"])`.
2. ❌ **Lỗi: Nhận mã lỗi HTTP `429 Too Many Requests` hoặc `403 Forbidden`**
   - **Nguyên nhân:** Gửi request liên tục với tốc độ máy móc hoặc thiếu Header `User-Agent`.
   - ✅ **Khắc phục:** Thêm `headers={"User-Agent": ...}`, gắn `time.sleep(random.uniform(1.0, 3.0))` và luân chuyển IP bằng Rotating Proxies nếu cào số lượng lớn.
3. ❌ **Lỗi: Memory Leak khi sử dụng Playwright / Selenium**
   - **Nguyên nhân:** Quên gọi `browser.close()` hoặc `context.close()` khi gặp exception giữa chừng.
   - ✅ **Khắc phục:** Luôn sử dụng context manager `with sync_playwright() as p:` hoặc đặt trong khối `finally:`.
4. ❌ **Lỗi: Hiệu năng MongoDB truy vấn chậm chạp khi dữ liệu lớn**
   - **Nguyên nhân:** Quên đánh Index trên các trường thường xuyên xuất hiện trong điều kiện lọc (`find()`) hoặc sắp xếp (`sort()`).
   - ✅ **Khắc phục:** Luôn chủ động tạo Index cho các trường tra cứu chính (`collection.create_index([("url", 1)])`).

### 5.2 Câu Hỏi Phỏng Vấn Kỹ Sư AI Thường Gặp
- **Q1: Khi nào bạn nên bóc tách HTML và khi nào nên tìm kiếm API ngầm (Reverse Engineering)?**
  - *Gợi ý trả lời:* Luôn ưu tiên mở DevTools kiểm tra tab Network trước. Nếu website giao tiếp bằng REST API/GraphQL trả về JSON, ta bắt trực tiếp API để có tốc độ cao nhất và dữ liệu sạch. Chỉ khi website mã hóa payload hoặc không có API lộ ra ngoài thì mới dùng bóc tách HTML tĩnh (`bs4`) hoặc động (`playwright`).
- **Q2: Tại sao không dùng Postgres để lưu toàn bộ dữ liệu cào ban đầu?**
  - *Gợi ý trả lời:* Dữ liệu thu thập từ Internet thường có tính dị thể cao (các trang web khác nhau có schema khác nhau, cấu trúc trường biến đổi liên tục). MongoDB với mô hình Document BSON linh hoạt cho phép lưu trữ nguyên vẹn dữ liệu thô mà không cần chạy migration bảng liên tục. Khi dữ liệu đã được làm sạch và chuẩn hóa sang dạng bảng phân tích, ta hoàn toàn có thể trích xuất sang Postgres hoặc Parquet sau.

---

## 6. Tổng Kết & Điểm Mấu Chốt (Key Takeaways)

1. **Tam Giác Vũ Khí Crawl:**
   - Dữ liệu HTML tĩnh $\rightarrow$ `requests` + `BeautifulSoup4`.
   - Trang tương tác động, SPA, cuộn chuột $\rightarrow$ `playwright`.
   - Website có backend AJAX $\rightarrow$ DevTools API Sniffing (Tối ưu nhất).
2. **Nguyên Tắc Dữ Liệu Sống Còn:**
   - Không crawl bừa bãi $\rightarrow$ Kiểm tra `robots.txt` và áp dụng delay ngẫu nhiên.
   - Không chèn mù quáng $\rightarrow$ Sử dụng kỹ thuật `Upsert` kèm `Unique Index` để đảm bảo cơ sở dữ liệu không bao giờ bị nhân bản rác.
3. **Sức Mạnh của MongoDB trong AI:**
   - Cung cấp kho chứa linh hoạt cho dữ liệu bán cấu trúc (Semi-structured data).
   - Tích hợp liền mạch với Python qua `pymongo` và chuyển đổi sang `pandas.DataFrame` chỉ với một dòng code.

---

## 6. Hướng dẫn Bài tập về nhà (Starter Code)

> 💡 **Lưu ý Giảng viên:** Để học viên bắt đầu nhẹ nhàng, bài tập dùng web luyện tập `http://quotes.toscrape.com/`. Web này không có Cloudflare chặn, cấu trúc DOM rõ ràng. Cung cấp file khung (boilerplate) cho các bạn điền vào `# TODO`.

### 7.1 Đề bài Phân tầng (Tiered Homework)

#### 📌 Phần 1: Cốt lõi (Bắt buộc)
1. **Thu thập dữ liệu:** Cào 10 câu trích dẫn từ trang 1 của `http://quotes.toscrape.com/`. Mỗi bản ghi gồm: `text` (nội dung câu nói), `author` (tác giả), `tags` (danh sách các chủ đề dạng list).
2. **Lưu trữ MongoDB:** Dùng `pymongo` kết nối tới MongoDB Local, lưu toàn bộ 10 bản ghi vào Database `d24_buoi8`, Collection `quotes` bằng lệnh `insert_many()`.
3. **Truy vấn & Pandas:**
   - Dùng `collection.find()` lọc ra các câu nói của tác giả `"Albert Einstein"`.
   - Chuyển toàn bộ dữ liệu trong collection thành `pandas.DataFrame` và hiển thị ra màn hình.

#### 🌟 Phần 2: Thử thách Nâng cao (Tùy chọn - Điểm cộng)
- **Thử thách A:** Tự động bắt đường link nút `Next →` ở chân trang để cào thêm trang 2 và trang 3.
- **Thử thách B:** Thay vì `insert_many()` làm trùng dữ liệu khi chạy lại, hãy dùng vòng lặp với `collection.update_one({"text": item["text"]}, {"$set": item}, upsert=True)`.

---

### 7.2 Khung Code Mẫu Hướng Dẫn (Starter Template)

```python
"""
BÀI TẬP VỀ NHÀ BUỔI 8 - TEAM AI PROPTIT D24
Hoàn thiện các vị trí đánh dấu # TODO bên dưới.
"""

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import pandas as pd
from typing import List, Dict, Any

# -------------------------------------------------------------
# PHẦN 1: THU THẬP DỮ LIỆU TỪ TRANG QUOTES.TOSCRAPE.COM
# -------------------------------------------------------------
def crawl_quotes_page_1() -> List[Dict[str, Any]]:
    target_url = "http://quotes.toscrape.com/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    print(f"[*] Đang tải trang web: {target_url}")
    response = requests.get(target_url, headers=headers)
    
    # Kiểm tra mã trạng thái HTTP (phải là 200 OK)
    if response.status_code != 200:
        print(f"[!] Lỗi kết nối, status code: {response.status_code}")
        return []
        
    soup = BeautifulSoup(response.text, "lxml")
    quotes_list: List[Dict[str, Any]] = []
    
    # Mỗi khối quote nằm trong thẻ <div class="quote">
    quote_blocks = soup.select("div.quote")
    
    for block in quote_blocks:
        # TODO 1: Lấy nội dung câu trích dẫn từ thẻ <span class="text">
        # Gợi ý: block.select_one("span.text").get_text(strip=True)
        text = block.select_one("span.text").get_text(strip=True)
        
        # TODO 2: Lấy tên tác giả từ thẻ <small class="author">
        author = block.select_one("small.author").get_text(strip=True)
        
        # TODO 3: Lấy danh sách tags từ các thẻ <a class="tag">
        # Gợi ý: Duyệt qua block.select("a.tag") và lấy text của từng tag
        tags = [tag.get_text(strip=True) for tag in block.select("a.tag")]
        
        quotes_list.append({
            "text": text,
            "author": author,
            "tags": tags
        })
        
    print(f"[✓] Đã cào thành công {len(quotes_list)} câu trích dẫn!")
    return quotes_list

# -------------------------------------------------------------
# PHẦN 2: LƯU TRỮ VÀO MONGODB & TRUY VẤN DỮ LIỆU
# -------------------------------------------------------------
def save_and_query_mongodb(data: List[Dict[str, Any]]):
    # TODO 4: Kết nối tới MongoDB Server (mặc định localhost:27017)
    client = MongoClient("mongodb://localhost:27017/")
    
    # Chọn Database 'd24_buoi8' và Collection 'quotes'
    db = client["d24_buoi8"]
    collection = db["quotes"]
    
    # Xóa dữ liệu mẫu cũ nếu có để tránh trùng khi test (tuỳ chọn)
    collection.delete_many({})
    
    # TODO 5: Chèn danh sách 10 quotes vào collection bằng insert_many()
    if data:
        insert_result = collection.insert_many(data)
        print(f"[✓] Đã chèn {len(insert_result.inserted_ids)} documents vào MongoDB!")
        
    # TODO 6: Viết câu truy vấn tìm các quote của tác giả "Albert Einstein"
    query = {"author": "Albert Einstein"}
    print("\n[*] Kết quả tìm kiếm quote của Albert Einstein:")
    einstein_quotes = collection.find(query, {"_id": 0, "text": 1, "author": 1})
    for q in einstein_quotes:
        print(f" - {q['text']} (Tác giả: {q['author']})")
        
    # TODO 7: Đọc toàn bộ collection ra Pandas DataFrame (bỏ cột _id)
    cursor_all = collection.find({}, {"_id": 0})
    df = pd.DataFrame(list(cursor_all))
    
    print("\n--- DataFrame Nghiệm Thu Kết Quả ---")
    print(df.head())
    print(f"Tổng số dòng: {len(df)}")
    
    client.close()
    
if __name__ == "__main__":
    crawled_data = crawl_quotes_page_1()
    save_and_query_mongodb(crawled_data)
```

---

## 8. Tài Liệu Tham Khảo (Citations & Reading List)
- [1] [PyMongo Driver Official Tutorial](https://pymongo.readthedocs.io/en/stable/tutorial.html) - MongoDB Documentation.
- [2] [Beautiful Soup 4 Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - Leonard Richardson.
- [3] [Playwright for Python Official Guide](https://playwright.dev/python/docs/intro) - Microsoft.
- [4] [Requests: HTTP for Humans Documentation](https://requests.readthedocs.io/en/latest/) - Kenneth Reitz.
- [5] [MongoDB Aggregation Framework Manual](https://www.mongodb.com/docs/manual/aggregation/) - MongoDB Docs.
- [6] [YouTube: Web Scraping with Python & Beautiful Soup Crash Course](https://www.youtube.com/watch?v=XVv6mJpFOb0) - freeCodeCamp.org.
- [7] [YouTube: Python MongoDB Tutorial using PyMongo](https://www.youtube.com/watch?v=rE_bJl2GAY8) - Tech With Tim.
