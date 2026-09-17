"""
VÍ DỤ 4: THAO TÁC CƠ SỞ DỮ LIỆU NOSQL MONGODB VỚI PYMONGO
Mục đích: Hướng dẫn kết nối, quản lý Collection, thực hiện đầy đủ các thao tác CRUD
          và kỹ thuật sống còn UPSERT để chống trùng lặp dữ liệu cào.
"""

from pymongo import MongoClient
import time
from typing import Dict, Any


def run_mongodb_crud_demo():
    # 1. KHỞI TẠO KẾT NỐI
    # Kết nối tới MongoDB Local (cổng mặc định 27017)
    uri = "mongodb://localhost:27017/"
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)

    try:
        # Ping kiểm tra trạng thái máy chủ
        client.admin.command("ping")
        print("[✓] Kết nối thành công tới máy chủ MongoDB!")
    except Exception as e:
        print(f"[!] Không thể kết nối tới MongoDB tại {uri}: {e}")
        print("[i] Gợi ý: Hãy kiểm tra kết nối MongoDB qua Extension trên IDE hoặc chuỗi kết nối MongoDB Atlas.")
        return

    # 2. CHỌN DATABASE VÀ COLLECTION
    db = client["proptit_d24_demo"]
    collection = db["articles"]

    # Xóa sạch collection cũ để chạy demo mới
    collection.drop()

    # 3. THIẾT LẬP UNIQUE INDEX (Cực kỳ quan trọng để đảm bảo tính toàn vẹn)
    collection.create_index([("article_url", 1)], unique=True)
    print("[✓] Đã tạo Unique Index trên trường 'article_url'.")

    # 4. CREATE: Chèn dữ liệu mẫu (insert_one & insert_many)
    sample_article_1 = {
        "title": "Tổng quan về LLM và Retrieval-Augmented Generation (RAG)",
        "article_url": "https://ai.proptit.com/post/rag-overview",
        "views": 1500,
        "tags": ["AI", "NLP", "LLM"],
        "is_published": True,
        "created_at": time.time()
    }
    insert_res = collection.insert_one(sample_article_1)
    print(f"[+] Đã chèn 1 document với _id: {insert_res.inserted_id}")

    batch_articles = [
        {
            "title": "Tối ưu hóa Huấn luyện Mô hình với PyTorch DDP",
            "article_url": "https://ai.proptit.com/post/pytorch-ddp",
            "views": 850,
            "tags": ["AI", "PyTorch", "Performance"],
            "is_published": True,
            "created_at": time.time()
        },
        {
            "title": "Giới thiệu Kiến trúc Transformer từ Scratch",
            "article_url": "https://ai.proptit.com/post/transformer-intro",
            "views": 2400,
            "tags": ["Deep Learning", "NLP", "Transformer"],
            "is_published": False,
            "created_at": time.time()
        }
    ]
    many_res = collection.insert_many(batch_articles)
    print(f"[+] Đã chèn hàng loạt {len(many_res.inserted_ids)} documents.")

    # 5. READ: Truy vấn dữ liệu với các Query Operators ($gt, $in, $regex)
    print("\n--- TRUY VẤN: Lọc các bài viết có views > 1000 ---")
    query = {"views": {"$gt": 1000}}
    # Projection: Bỏ trường _id (0), chỉ lấy title và views (1)
    projection = {"_id": 0, "title": 1, "views": 1}
    for doc in collection.find(query, projection):
        print(f" - {doc['title']} (Lượt xem: {doc['views']})")

    print("\n--- TRUY VẤN: Tìm bài viết có chứa tag 'NLP' ---")
    tag_query = {"tags": {"$in": ["NLP"]}}
    for doc in collection.find(tag_query, {"_id": 0, "title": 1, "tags": 1}):
        print(f" - {doc['title']} | Tags: {doc['tags']}")

    # 6. UPDATE VỚI KỸ THUẬT UPSERT (Update or Insert)
    print("\n--- KỸ THUẬT UPSERT: Cập nhật bài viết cũ / Chèn nếu chưa có ---")
    incoming_data = {
        "title": "Tổng quan về LLM và Retrieval-Augmented Generation (RAG) [Bản cập nhật]",
        "article_url": "https://ai.proptit.com/post/rag-overview",
        "views": 1800,  # Views tăng
        "last_scraped_at": time.time()
    }

    upsert_res = collection.update_one(
        {"article_url": incoming_data["article_url"]},  # Điều kiện tìm kiếm
        {"$set": incoming_data},                        # Dữ liệu cập nhật
        upsert=True                                      # Bật tính năng Upsert
    )
    if upsert_res.matched_count > 0:
        print("[✓] Đã tìm thấy bản ghi theo URL và cập nhật views mới thành công!")
    elif upsert_res.upserted_id is not None:
        print(f"[+] Chưa có URL này, đã tự động chèn mới với ID: {upsert_res.upserted_id}")

    # 7. DELETE: Xóa dữ liệu
    del_res = collection.delete_many({"is_published": False})
    print(f"[-] Đã xóa {del_res.deleted_count} bài viết chưa xuất bản (is_published = False).")

    # Đóng kết nối
    client.close()
    print("[*] Đóng kết nối MongoDB thành công.")


if __name__ == "__main__":
    print("=== DEMO PYMONGO CRUD & UPSERT ===")
    run_mongodb_crud_demo()
