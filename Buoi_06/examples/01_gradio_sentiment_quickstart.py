"""
Ví dụ 1: Xây dựng Giao diện Thử nghiệm Siêu tốc với Gradio
Chủ đề: Hệ thống AI Phân tích & Phản hồi Đánh giá Khách hàng (Customer Feedback AI)
Giáo án Team AI ProPTIT D24 - Buổi 06

Mục tiêu học tập:
1. Hiểu cách bọc một hàm Python xử lý logic AI thành Web UI chỉ với gr.Interface.
2. Nắm vững cách định nghĩa inputs, outputs và truyền dữ liệu mẫu (examples).
3. Hiểu vai trò của Mock Model trong giai đoạn Proof of Concept (POC).
"""

import gradio as gr
from typing import Tuple, Dict

# ==============================================================================
# 1. ĐỊNH NGHĨA MOCK MODEL (Hàm giả lập mô hình phân tích đánh giá khách hàng)
# ==============================================================================
def analyze_customer_review(review_text: str) -> Tuple[str, str, str]:
    """
    Giả lập mô hình phân loại cảm xúc đánh giá khách hàng (Review Sentiment Analysis).
    
    Args:
        review_text (str): Đoạn nhận xét/đánh giá sản phẩm của khách hàng.
        
    Returns:
        Tuple[str, str, str]: (Nhãn cảm xúc, Mức độ tin cậy, Đánh giá số sao ước tính)
    """
    clean_text = review_text.strip().lower()
    if not clean_text:
        return "⚠️ Vui lòng nhập nội dung đánh giá!", "0%", "☆☆☆☆☆ (0/5)"
    
    # Danh sách từ khóa phân tích cơ bản (Giả lập logic trích xuất đặc trưng NLP)
    positive_words = ["tốt", "tuyệt vời", "hài lòng", "nhanh", "đẹp", "chất lượng", "ưng ý", "thích", "xuất sắc"]
    negative_words = ["tệ", "kém", "chậm", "hỏng", "thất vọng", "xấu", "lỗi", "đắt", "không thích", "vỡ"]
    
    pos_count = sum(1 for word in positive_words if word in clean_text)
    neg_count = sum(1 for word in negative_words if word in clean_text)
    
    # Quyết định nhãn cảm xúc và ước lượng số sao
    if pos_count > neg_count:
        sentiment = "🟢 TÍCH CỰC (Positive Review)"
        stars = "⭐⭐⭐⭐⭐ (5/5)"
        confidence = min(0.70 + (pos_count * 0.08), 0.98)
    elif neg_count > pos_count:
        sentiment = "🔴 TIÊU CỰC (Negative Review)"
        stars = "⭐☆☆☆☆ (1/5)"
        confidence = min(0.70 + (neg_count * 0.08), 0.96)
    else:
        # Nếu không có từ khóa hoặc số lượng bằng nhau, fallback theo độ dài chuỗi
        is_pos = len(clean_text) % 2 == 0
        sentiment = "🟢 TÍCH CỰC (Positive Review)" if is_pos else "🟡 TRUNG TÍNH (Neutral / Mixed)"
        stars = "⭐⭐⭐⭐☆ (4/5)" if is_pos else "⭐⭐⭐☆☆ (3/5)"
        confidence = 0.65
        
    return sentiment, f"{confidence:.1%}", stars


# ==============================================================================
# 2. XÂY DỰNG GIAO DIỆN VỚI GRADIO INTERFACE
# ==============================================================================
# Dữ liệu mẫu giúp học viên test nhanh chỉ bằng 1 cú click chuột
sample_reviews = [
    ["Sản phẩm dùng rất mượt, giao hàng siêu nhanh, nhân viên đóng gói cẩn thận!"],
    ["Chất lượng sản phẩm quá tệ, đóng gói sơ sài, vừa mở ra đã bị nứt vỏ."],
    ["Hàng giao đúng hạn, dùng tạm ổn trong tầm giá, cần trải nghiệm thêm."],
]

demo = gr.Interface(
    fn=analyze_customer_review,
    inputs=gr.Textbox(
        lines=4,
        placeholder="Nhập nội dung đánh giá sản phẩm từ khách hàng vào đây...",
        label="Nội dung đánh giá (Customer Review Text)"
    ),
    outputs=[
        gr.Textbox(label="1. Phân loại Cảm xúc (Sentiment Label)"),
        gr.Textbox(label="2. Độ tin cậy của Mô hình (Confidence Score)"),
        gr.Textbox(label="3. Đánh giá Sao ước lượng (Estimated Rating)")
    ],
    title="🛍️ Trợ lý Phân tích Đánh giá Khách hàng - ProPTIT D24",
    description="Giao diện thử nghiệm nhanh (POC) xây dựng bằng Gradio. Dành cho buổi học số 06.",
    examples=sample_reviews
)

# ==============================================================================
# 3. KHỞI CHẠY WEB SERVER CỤC BỘ
# ==============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Đang khởi động Gradio Server trên cổng 7860...")
    print("👉 Mở trình duyệt và truy cập: http://127.0.0.1:7860")
    print("=" * 60)
    # server_port=7860 là cổng mặc định chuẩn của Gradio
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False, theme="soft")
