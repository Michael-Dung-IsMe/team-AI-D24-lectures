"""
VÍ DỤ 2: DYNAMIC WEB SCRAPING VỚI PLAYWRIGHT (HEADLESS BROWSER)
Mục đích: Tự động hóa trình duyệt để xử lý các trang Single Page Application (SPA),
          website tải dữ liệu bằng JavaScript và xử lý cuộn trang vô hạn (Infinite Scroll).
Trang mục tiêu: https://quotes.toscrape.com/scroll
"""

from playwright.sync_api import sync_playwright
import time
from typing import List, Dict, Any


def scrape_infinite_scroll_quotes(max_scrolls: int = 3) -> List[Dict[str, Any]]:
    """
    Sử dụng Playwright để tự động cuộn trang và thu thập các câu trích dẫn
    được nạp động qua JavaScript.
    
    Args:
        max_scrolls: Số lần cuộn chuột xuống đáy trang.
        
    Returns:
        Danh sách các dictionary chứa trích dẫn, tác giả và thẻ tags.
    """
    target_url = "https://quotes.toscrape.com/scroll"
    results: List[Dict[str, Any]] = []

    print("[*] Khởi động trình duyệt Playwright Chromium...")
    # Bọc trong context manager để đảm bảo tài nguyên trình duyệt luôn được đóng kín
    with sync_playwright() as p:
        # Chạy Chromium ở chế độ không đồ họa (headless) để tiết kiệm CPU/RAM
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print(f"[*] Điều hướng tới: {target_url}")
        # Chờ tới khi trang nạp xong cấu trúc DOM ban đầu
        page.goto(target_url, wait_until="domcontentloaded")

        # Chờ tối đa 5 giây cho container chứa các quote xuất hiện
        page.wait_for_selector("div.quotes", timeout=5000)

        for scroll_idx in range(1, max_scrolls + 1):
            print(f"[*] Cuộn trang lần {scroll_idx}/{max_scrolls}...")

            # Thực thi JavaScript trực tiếp trên trang để cuộn xuống đáy
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")

            # Chờ 1.5 giây để request ngầm nạp thêm nội dung mới vào DOM
            page.wait_for_timeout(1500)

        # Lấy danh sách tất cả các element quote đã xuất hiện sau khi cuộn
        quote_locators = page.locator("div.quote").all()
        print(f"[+] Tìm thấy tổng cộng {len(quote_locators)} trích dẫn trên trang.")

        for locator in quote_locators:
            text = locator.locator("span.text").inner_text()
            author = locator.locator("small.author").inner_text()
            tags = [tag.inner_text() for tag in locator.locator("a.tag").all()]

            results.append({
                "text": text.strip("“”\" "),
                "author": author.strip(),
                "tags": tags,
                "crawled_method": "playwright_headless"
            })

        # Đóng ngữ cảnh và tiến trình trình duyệt
        context.close()
        browser.close()

    return results


if __name__ == "__main__":
    print("=== DEMO CÀO DỮ LIỆU ĐỘNG VỚI PLAYWRIGHT ===")
    quotes = scrape_infinite_scroll_quotes(max_scrolls=2)
    print(f"\n[✓] Thu thập thành công {len(quotes)} trích dẫn.")
    if quotes:
        print("\n--- Mẫu 3 trích dẫn đầu tiên ---")
        for idx, q in enumerate(quotes[:3], 1):
            print(f"{idx}. \"{q['text']}\"")
            print(f"   Tác giả: {q['author']} | Tags: {q['tags']}")
