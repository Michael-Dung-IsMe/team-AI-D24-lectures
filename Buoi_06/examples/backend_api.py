"""
Backend API với FastAPI - Tương thích với lệnh chạy trong bài giảng:
uvicorn backend_api:app --reload --port 8000
(Đồng bộ với examples/03_backend_api.py)
"""

import asyncio
from typing import AsyncGenerator, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# 1. KHỞI TẠO ỨNG DỤNG FASTAPI VÀ CẤU HÌNH SIÊU DỮ LIỆU
app = FastAPI(
    title="Customer Feedback AI Serving API - ProPTIT D24",
    description="Backend API phục vụ mô hình phân loại cảm xúc đánh giá khách hàng & Trợ lý CSKH tự động sinh câu trả lời (Streaming)",
    version="1.0.0"
)

# Cấu hình CORS để Frontend kết nối thông suốt
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. ĐỊNH NGHĨA SCHEMAS (PYDANTIC MODELS)
class ReviewInferenceRequest(BaseModel):
    review_text: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Đoạn văn bản đánh giá sản phẩm của khách hàng",
        json_schema_extra={"example": "Sản phẩm dùng rất tốt, đóng gói kỹ và giao hàng nhanh!"}
    )
    product_category: Optional[str] = Field(
        default="Điện thoại & Phụ kiện",
        description="Ngành hàng của sản phẩm"
    )

class ReviewInferenceResponse(BaseModel):
    status: str
    original_review: str
    product_category: str
    sentiment_label: str
    confidence: float
    estimated_stars: int
    recommended_action: str

# 3. ENDPOINT KIỂM TRA TRẠNG THÁI SERVER (HEALTH CHECK)
@app.get("/", summary="Trang chủ & Kiểm tra trạng thái máy chủ")
def root_endpoint():
    return {
        "message": "Chào mừng đến với API Phân Tích Đánh Giá Khách Hàng - ProPTIT D24",
        "status": "online",
        "docs_url": "http://localhost:8000/docs"
    }

# 4. ENDPOINT POST TIÊU CHUẨN (STANDARD RESTFUL REQUEST-RESPONSE)
@app.post(
    "/predict",
    response_model=ReviewInferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Phân tích cảm xúc đánh giá khách hàng (JSON Response)"
)
def predict_review_sentiment(payload: ReviewInferenceRequest):
    raw_text = payload.review_text.strip()
    if not raw_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nội dung đánh giá không được chỉ chứa khoảng trắng."
        )
    
    clean_lower = raw_text.lower()
    pos_words = ["tốt", "tuyệt vời", "hài lòng", "nhanh", "đẹp", "chất lượng", "ưng ý", "thích", "xuất sắc"]
    neg_words = ["tệ", "kém", "chậm", "hỏng", "thất vọng", "xấu", "lỗi", "đắt", "vỡ"]
    
    pos_score = sum(1 for w in pos_words if w in clean_lower)
    neg_score = sum(1 for w in neg_words if w in clean_lower)
    
    if pos_score > neg_score:
        label = "POSITIVE"
        stars = 5
        confidence = min(0.72 + pos_score * 0.08, 0.98)
        action = "Gửi lời cảm ơn khách hàng và mời đánh giá gian hàng 5 sao."
    elif neg_score > pos_score:
        label = "NEGATIVE"
        stars = 1
        confidence = min(0.72 + neg_score * 0.08, 0.97)
        action = "Chuyển gấp cho đội CSKH liên hệ hỗ trợ kỹ thuật hoặc hoàn tiền/đổi trả."
    else:
        is_even = len(raw_text) % 2 == 0
        label = "POSITIVE" if is_even else "NEUTRAL"
        stars = 4 if is_even else 3
        confidence = 0.70
        action = "Ghi nhận đóng góp để nâng cao chất lượng trải nghiệm."
        
    return ReviewInferenceResponse(
        status="success",
        original_review=raw_text,
        product_category=payload.product_category or "Chung",
        sentiment_label=label,
        confidence=round(confidence, 4),
        estimated_stars=stars,
        recommended_action=action
    )

# 5. ASYNC GENERATOR: SINH PHẢN HỒI DẠNG STREAMING
async def stream_customer_reply_generator(review_text: str) -> AsyncGenerator[str, None]:
    is_negative = any(w in review_text.lower() for w in ["tệ", "kém", "chậm", "hỏng", "thất vọng", "lỗi", "vỡ"])
    if is_negative:
        tokens = [
            "Kính", "gửi", "Quý", "khách,", "\n\n",
            "Đội", "ngũ", "Chăm", "sóc", "Khách", "hàng", "chân", "thành", "xin", "lỗi", "Quý", "khách",
            "về", "trải", "nghiệm", "chưa", "hài", "lòng", "vừa", "qua.", "\n",
            "Hệ", "thống", "đã", "ghi", "nhận", "phản", "hồi:", f"\"{review_text}\".", "\n",
            "Chúng", "tôi", "đã", "chuyển", "thông", "tin", "tới", "bộ", "phận", "kỹ", "thuật",
            "và", "sẽ", "chủ", "động", "gọi", "điện", "hỗ", "trợ", "đổi", "mới", "sản", "phẩm",
            "trong", "vòng", "24", "giờ.", "\n\n",
            "Trân", "trọng,", "\n", "Đội", "ngũ", "Hỗ", "trợ", "Khách", "hàng", "ProPTIT!"
        ]
    else:
        tokens = [
            "Kính", "gửi", "Quý", "khách,", "\n\n",
            "Cảm", "ơn", "Quý", "khách", "đã", "tin", "tưởng", "và", "dành", "thời", "gian", "đánh", "giá", "5", "sao",
            "cho", "sản", "phẩm!", "\n",
            "Lời", "khen", "của", "Quý", "khách", "về", "sản", "phẩm:", f"\"{review_text}\"",
            "là", "động", "lực", "rất", "lớn", "cho", "đội", "ngũ", "phát", "triển.", "\n\n",
            "Chúc", "Quý", "khách", "có", "những", "trải", "nghiệm", "thật", "tuyệt", "vời!", "\n",
            "Trân", "trọng,", "\n", "Đội", "ngũ", "ProPTIT", "D24."
        ]
    for token in tokens:
        await asyncio.sleep(0.12)
        yield f"{token} "

# 6. ENDPOINT GET STREAMING
@app.get(
    "/predict-stream",
    summary="Sinh câu phản hồi chăm sóc khách hàng dạng luồng (Server-Sent Streaming)"
)
async def stream_customer_reply_endpoint(
    review_text: str = Query(..., description="Nội dung đánh giá cần AI soạn thảo phản hồi")
):
    if not review_text or not review_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tham số 'review_text' không được để trống."
        )
    return StreamingResponse(
        stream_customer_reply_generator(review_text.strip()),
        media_type="text/plain"
    )

# 7. KHỞI CHẠY TRỰC TIẾP
if __name__ == "__main__":
    import uvicorn
    print("=" * 65)
    print("🚀 Đang khởi động FastAPI Backend Server...")
    print("👉 Swagger API Documentation: http://127.0.0.1:8000/docs")
    print("=" * 65)
    uvicorn.run(app, host="127.0.0.1", port=8000)
