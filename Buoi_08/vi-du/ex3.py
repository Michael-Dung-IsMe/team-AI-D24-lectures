import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

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
    print(f"[OK] Lấy thành công {len(quotes)} câu trích dẫn. Bản ghi đầu:", quotes[0])