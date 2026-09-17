# Lab: Xây dựng Giao diện UI & Tích hợp Backend API cho AI Model

> **Tài liệu đồng hành:** [lecture_notes.md](../lecture_notes.md)  
> **Thời lượng dự kiến:** 60 - 90 phút

## Mục tiêu
- Thành thạo việc tạo Web UI nhanh chóng bằng thư viện Gradio.
- Xây dựng Backend API chuẩn RESTful với FastAPI và kiểm định dữ liệu bằng Pydantic `BaseModel`.
- Triển khai kỹ thuật HTTP Streaming (`StreamingResponse` + Async Generator) để truyền dữ liệu thời gian thực.
- Phát triển ứng dụng Web đa trang/đa tab bằng Streamlit, kết nối API qua thư viện `requests` và quản lý trạng thái phiên làm việc với `st.session_state`.

## Tóm tắt lý thuyết cần dùng
- **Gradio Quickstart:** Xem mục 2.1 & 3.1 trong [lecture_notes.md](../lecture_notes.md).
- **FastAPI & Pydantic Validation:** Xem mục 3.1 trong [lecture_notes.md](../lecture_notes.md).
- **HTTP Streaming & Async Generator:** Xem mục 2.4 & 3.3 trong [lecture_notes.md](../lecture_notes.md).
- **Streamlit Execution Lifecycle & Session State:** Xem mục 2.2 & 3.2 trong [lecture_notes.md](../lecture_notes.md).

## Hướng dẫn chuẩn bị môi trường
Cài đặt các thư viện cần thiết trước khi chạy notebook:
```bash
pip install fastapi uvicorn requests streamlit gradio pydantic
```

## Danh sách bài tập

| Task | Độ khó | Trọng số điểm | Mô tả ngắn |
|------|--------|---------------|------------|
| Task 1: Gradio Quickstart | Beginner | 20% | Bọc hàm mock model bằng `gr.Interface` |
| Task 2: FastAPI Backend API | Intermediate | 25% | Xây dựng API endpoint `/predict` với Pydantic schema |
| Task 3: Streaming API Endpoint | Intermediate | 25% | Tạo endpoint `/predict-stream` với `StreamingResponse` |
| Task 4: Streamlit Client UI | Advanced | 30% | Xây dựng Streamlit app 2 tab kết nối API & quản lý state |

## Tiêu chí chấm điểm
- **Task 1 (20%):** Chạy được Gradio UI, hàm `mock_predict` nhận input text và trả về chuỗi dự đoán hợp lệ.
- **Task 2 (25%):** FastAPI endpoint `/predict` nhận JSON payload đúng schema Pydantic, trả về status 200 và JSON phản hồi. Pass các câu lệnh `assert`.
- **Task 3 (25%):** Async generator nhả ra từng token dữ liệu, endpoint `/predict-stream` trả về `StreamingResponse` chuẩn `text/plain`.
- **Task 4 (30%):** Tab 1 gửi `requests.post` thành công và lưu lịch sử vào `st.session_state`; Tab 2 gọi `requests.get(..., stream=True)` và render hiệu ứng gõ chữ với `st.write_stream`.

## Nộp bài
- Học viên hoàn thiện code trong notebook `buoi_06_practice.ipynb`.
- Đẩy mã nguồn lên repository GitHub cá nhân/team và nộp lại link cho giảng viên.
