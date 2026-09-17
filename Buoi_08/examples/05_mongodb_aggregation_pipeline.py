"""
VÍ DỤ 5: MONGODB AGGREGATION PIPELINE CHO PHÂN TÍCH DỮ LIỆU AI
Mục đích: Sử dụng chuỗi xử lý Pipeline đa tầng ($match -> $group -> $sort -> $project)
          để tính toán thống kê, trích xuất dữ liệu phân tích ngay bên trong Database Engine.
"""

from pymongo import MongoClient
from typing import List, Dict, Any


def run_aggregation_demo():
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
    try:
        client.admin.command("ping")
    except Exception as e:
        print(f"[!] Lỗi kết nối MongoDB: {e}")
        return

    db = client["proptit_d24_demo"]
    collection = db["products_catalog"]
    collection.drop()

    # Chuẩn bị tập dữ liệu sản phẩm phong phú
    sample_products = [
        {"name": "Laptop Gaming Legion 5", "category": "Laptop", "price": 1200.0, "rating": 4.8, "sold": 150},
        {"name": "MacBook Air M2", "category": "Laptop", "price": 1050.0, "rating": 4.9, "sold": 320},
        {"name": "Dell Inspiron 15", "category": "Laptop", "price": 650.0, "rating": 4.2, "sold": 95},
        {"name": "Bàn phím cơ Keychron K2", "category": "Phụ kiện", "price": 85.0, "rating": 4.7, "sold": 410},
        {"name": "Chuột Logitech MX Master 3S", "category": "Phụ kiện", "price": 99.0, "rating": 4.9, "sold": 550},
        {"name": "Tai nghe Sony WH-1000XM5", "category": "Âm thanh", "price": 350.0, "rating": 4.8, "sold": 210},
        {"name": "Loa Bluetooth Marshall Emberton", "category": "Âm thanh", "price": 160.0, "rating": 4.5, "sold": 130},
        {"name": "Tai nghe Airpods Pro 2", "category": "Âm thanh", "price": 240.0, "rating": 4.7, "sold": 480}
    ]
    collection.insert_many(sample_products)
    print(f"[+] Đã khởi tạo {len(sample_products)} sản phẩm mẫu.")

    # -------------------------------------------------------------------------
    # PIPELINE 1: Thống kê Giá trung bình, Doanh số và Số lượng theo Danh mục
    # -------------------------------------------------------------------------
    pipeline_category_stats = [
        # Stage 1: $match - Chỉ xét các sản phẩm có đánh giá từ 4.5 sao trở lên
        {"$match": {"rating": {"$gte": 4.5}}},

        # Stage 2: $group - Nhóm theo trường 'category'
        {
            "$group": {
                "_id": "$category",
                "avg_price": {"$avg": "$price"},
                "min_price": {"$min": "$price"},
                "max_price": {"$max": "$price"},
                "total_sold": {"$sum": "$sold"},
                "count": {"$sum": 1}
            }
        },

        # Stage 3: $project - Định dạng lại trường hiển thị và làm tròn giá
        {
            "$project": {
                "_id": 0,
                "danh_muc": "$_id",
                "gia_trung_binh": {"$round": ["$avg_price", 2]},
                "khoang_gia": ["$min_price", "$max_price"],
                "tong_da_ban": "$total_sold",
                "so_luong_sp": "$count"
            }
        },

        # Stage 4: $sort - Sắp xếp theo tổng lượng bán giảm dần
        {"$sort": {"tong_da_ban": -1}}
    ]

    print("\n--- BÁO CÁO 1: Thống kê hiệu suất theo Danh mục (Rating >= 4.5) ---")
    results = list(collection.aggregate(pipeline_category_stats))
    for r in results:
        print(f"Danh mục: {r['danh_muc']:<10} | Số SP: {r['so_luong_sp']} | "
              f"Giá TB: {r['gia_trung_binh']:<8} USD | Đã bán: {r['tong_da_ban']:<5} chiếc")

    client.close()


if __name__ == "__main__":
    print("=== DEMO MONGODB AGGREGATION PIPELINE ===")
    run_aggregation_demo()
