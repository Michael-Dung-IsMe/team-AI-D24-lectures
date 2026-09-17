"""
VÍ DỤ 6: PIPELINE KHÉP KÍN TỪ CRAWL WEB TỚI HUẤN LUYỆN MÔ HÌNH AI
Mục đích: Tích hợp hoàn chỉnh chuỗi giá trị dữ liệu cho Kỹ sư AI:
          Thu thập (Crawl) -> Lưu trữ NoSQL (MongoDB Bulk Upsert) -> Đọc ra Pandas DataFrame
"""

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient, UpdateOne
import pandas as pd
import time
from typing import List, Dict, Any


def crawl_books_by_category(category_url: str, category_name: str) -> List[Dict[str, Any]]:
    """Cào sách thuộc thể loại cụ thể từ books.toscrape.com"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    print(f"[*] Bắt đầu cào dữ liệu thể loại '{category_name}' từ: {category_url}")
    
    try:
        response = requests.get(category_url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[!] Lỗi tải trang: {e}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    items = []
    cards = soup.select("article.product_pod")

    for card in cards:
        title_node = card.select_one("h3 > a")
        title = title_node["title"] if title_node and title_node.has_attr("title") else "Unknown"
        rel_link = title_node["href"] if title_node else ""
        clean_rel_link = rel_link.replace("../", "")
        product_url = f"http://books.toscrape.com/catalogue/{clean_rel_link}"

        price_node = card.select_one("p.price_color")
        price = float(price_node.get_text(strip=True).replace("£", "")) if price_node else 0.0

        star_node = card.select_one("p.star-rating")
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        rating = 0
        if star_node:
            for cls in star_node.get("class", []):
                if cls in rating_map:
                    rating = rating_map[cls]
                    break

        items.append({
            "title": title,
            "url": product_url,
            "price": price,
            "rating": rating,
            "category": category_name,
            "crawled_timestamp": time.time()
        })

    return items


def ingest_to_mongodb(records: List[Dict[str, Any]], db_name: str = "ai_lake", coll_name: str = "raw_books"):
    """Thực hiện lưu trữ vào MongoDB bằng Bulk Upsert theo trường 'url'"""
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
    db = client[db_name]
    collection = db[coll_name]

    # Đảm bảo Unique Index trên trường URL để chống trùng lặp
    collection.create_index([("url", 1)], unique=True)

    # Chuẩn bị danh sách thao tác Bulk UpdateOne
    bulk_ops = [
        UpdateOne({"url": item["url"]}, {"$set": item}, upsert=True)
        for item in records
    ]

    if bulk_ops:
        result = collection.bulk_write(bulk_ops)
        print(f"[✓] Bulk write hoàn tất: {result.upserted_count} bản ghi chèn mới, "
              f"{result.modified_count} bản ghi được cập nhật.")

    client.close()


def export_to_ai_dataframe(db_name: str = "ai_lake", coll_name: str = "raw_books") -> pd.DataFrame:
    """Truy vấn dữ liệu từ MongoDB và chuyển đổi trực tiếp sang Pandas DataFrame"""
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
    collection = client[db_name][coll_name]

    # Loại bỏ trường _id để tránh lỗi ObjectId không tương thích với một số module AI
    cursor = collection.find({}, {"_id": 0})
    df = pd.DataFrame(list(cursor))

    client.close()
    return df


if __name__ == "__main__":
    print("=== DEMO FULL END-TO-END PIPELINE: CRAWLER -> MONGODB -> PANDAS ===")
    
    # Bước 1: Crawl
    science_url = "http://books.toscrape.com/catalogue/category/books/science_22/index.html"
    raw_data = crawl_books_by_category(science_url, category_name="Science")
    print(f"[+] Thu thập được {len(raw_data)} cuốn sách.")

    # Bước 2: Ingest MongoDB (Chạy nhiều lần vẫn không bị trùng lặp)
    ingest_to_mongodb(raw_data)

    # Bước 3: Export ra DataFrame phục vụ phân tích / huấn luyện mô hình
    df_ai = export_to_ai_dataframe()
    print("\n--- BÁO CÁO TỔNG QUAN DATAFRAME CHO MÔ HÌNH AI ---")
    print(df_ai.info())
    print("\nThống kê mô tả (Descriptive Statistics):")
    print(df_ai[["price", "rating"]].describe())
    print("\n5 dòng dữ liệu mẫu:")
    print(df_ai[["title", "price", "rating", "category"]].head())
