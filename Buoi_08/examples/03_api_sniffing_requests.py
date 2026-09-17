"""
VÍ DỤ 3: BẮT API NGẦM (REVERSE ENGINEERING / API SNIFFING)
Mục đích: Tìm và gọi trực tiếp Backend API nội bộ mà trang web sử dụng để nạp dữ liệu,
          bỏ qua bước render và bóc tách HTML DOM, mang lại hiệu năng cao nhất.
"""

import requests
import time
import random
from typing import List, Dict, Any


def fetch_via_internal_api(endpoint: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Gửi request trực tiếp tới API endpoint nội bộ với headers giả lập trình duyệt.
    
    Args:
        endpoint: Đường dẫn API endpoint.
        params: Các tham số truy vấn (Query parameters).
        
    Returns:
        Danh sách dữ liệu JSON đã được parse thành Python List/Dict.
    """
    # Headers chuẩn hóa bắt chước request từ Fetch/XHR của Google Chrome
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive"
    }

    # Thiết lập Session để tự động quản lý Cookies và tái sử dụng kết nối TCP
    with requests.Session() as session:
        session.headers.update(headers)

        print(f"[*] Đang gửi GET request trực tiếp tới API: {endpoint}")
        try:
            # Exponential backoff retry loop mẫu
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    response = session.get(endpoint, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"[✓] Gọi API thành công! Nhận {len(data) if isinstance(data, list) else 1} bản ghi JSON.")
                        return data if isinstance(data, list) else [data]
                    elif response.status_code == 429:
                        # Gặp Rate Limit -> Sleep cấp số nhân + jitter
                        wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                        print(f"[!] Bị giới hạn tần suất (429), chờ {wait_time:.2f}s trước khi thử lại...")
                        time.sleep(wait_time)
                    else:
                        print(f"[!] Server trả về mã lỗi HTTP: {response.status_code}")
                        break
                except requests.exceptions.RequestException as e:
                    print(f"[!] Thử lần {attempt}/{max_retries} thất bại: {e}")
                    time.sleep(2)

        except Exception as e:
            print(f"[!] Lỗi không xác định: {e}")

    return []


if __name__ == "__main__":
    print("=== DEMO BẮT VÀ GỌI TRỰC TIẾP API NGẦM (JSON) ===")
    
    # Sử dụng API công khai chuẩn REST JSON của JSONPlaceholder / SampleAPIs để demo
    sample_api_url = "https://jsonplaceholder.typicode.com/posts"
    query_params = {"_limit": 5}  # Giả lập tham số lọc/phân trang

    posts = fetch_via_internal_api(sample_api_url, params=query_params)
    
    if posts:
        print("\n--- Mẫu 2 bản ghi JSON nhận được trực tiếp ---")
        for idx, post in enumerate(posts[:2], 1):
            print(f"{idx}. ID: {post.get('id')} | Tiêu đề: {post.get('title')}")
            print(f"   Nội dung: {post.get('body')[:60]}...")
