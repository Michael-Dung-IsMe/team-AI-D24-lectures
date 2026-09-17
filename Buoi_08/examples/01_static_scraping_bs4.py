"""
VÍ DỤ 1: STATIC WEB SCRAPING VỚI REQUESTS & BEAUTIFUL SOUP 4
Mục đích: Hướng dẫn cào dữ liệu từ các trang web HTML tĩnh tiêu chuẩn.
Trang mục tiêu: http://books.toscrape.com (Kho sách mẫu chuẩn quốc tế)
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Any


def scrape_books_catalog(max_pages: int = 2) -> List[Dict[str, Any]]:
    """
    Cào danh mục sách phân trang bằng requests và BeautifulSoup.
    
    Args:
        max_pages: Số trang tối đa cần cào.
        
    Returns:
        Danh sách các dictionary chứa thông tin từng cuốn sách.
    """
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
    }
    
    books_data: List[Dict[str, Any]] = []
    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    for page in range(1, max_pages + 1):
        target_url = base_url.format(page)
        print(f"[*] Đang cào trang {page}/{max_pages}: {target_url}")

        try:
            # Gửi HTTP GET request có thiết lập timeout tránh treo chương trình
            response = requests.get(target_url, headers=headers, timeout=10)
            response.raise_for_status()  # Ném lỗi nếu gặp HTTP 4xx hoặc 5xx
        except requests.exceptions.RequestException as e:
            print(f"[!] Lỗi kết nối khi tải trang {page}: {e}")
            break

        # Khởi tạo cây DOM bằng parser 'lxml' (tốc độ cao)
        soup = BeautifulSoup(response.text, "lxml")

        # Mỗi khối sản phẩm nằm trong thẻ: <article class="product_pod">
        product_cards = soup.select("article.product_pod")

        for card in product_cards:
            # 1. Trích xuất Tiêu đề và URL
            title_node = card.select_one("h3 > a")
            title = title_node["title"] if title_node and title_node.has_attr("title") else "Unknown Title"
            relative_url = title_node["href"] if title_node else ""
            full_url = f"http://books.toscrape.com/catalogue/{relative_url}"

            # 2. Trích xuất Giá bán và ép kiểu về float
            price_node = card.select_one("div.product_price > p.price_color")
            price_raw = price_node.get_text(strip=True) if price_node else "£0.0"
            try:
                price = float(price_raw.replace("£", "").strip())
            except ValueError:
                price = 0.0

            # 3. Trích xuất Đánh giá sao (star rating)
            star_node = card.select_one("p.star-rating")
            rating = 0
            if star_node:
                classes = star_node.get("class", [])
                for cls in classes:
                    if cls in rating_map:
                        rating = rating_map[cls]
                        break

            # 4. Trạng thái còn hàng
            stock_node = card.select_one("div.product_price > p.instock")
            in_stock = True if stock_node and "In stock" in stock_node.get_text() else False

            books_data.append({
                "title": title,
                "price": price,
                "rating": rating,
                "in_stock": in_stock,
                "url": full_url,
                "scraped_at": time.time()
            })

        # Nguyên tắc Polite Crawling: Delay ngẫu nhiên từ 1.0 đến 2.0 giây giữa các request
        time.sleep(random.uniform(1.0, 2.0))

    return books_data


if __name__ == "__main__":
    print("=== DEMO CÀO DỮ LIỆU TĨNH VỚI BEAUTIFUL SOUP 4 ===")
    results = scrape_books_catalog(max_pages=1)
    print(f"\n[✓] Đã thu thập {len(results)} bản ghi.")
    if results:
        print("\n--- Mẫu 3 sản phẩm đầu tiên ---")
        for idx, book in enumerate(results[:3], 1):
            print(f"{idx}. {book['title']}")
            print(f"   Giá: {book['price']} GBP | Đánh giá: {book['rating']} sao | Còn hàng: {book['in_stock']}")
            print(f"   Link: {book['url']}")
