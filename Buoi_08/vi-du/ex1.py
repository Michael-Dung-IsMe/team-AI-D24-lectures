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