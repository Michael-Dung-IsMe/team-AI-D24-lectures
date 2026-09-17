# 🛍️ Thư mục Ví dụ Thực hành: Hệ thống AI Phân tích & Phản hồi Đánh giá Khách hàng

> **Khóa học:** AI Core - Team AI ProPTIT D24  
> **Buổi 06:** Interface Programming & API Integration  
> **Kiến trúc:** Client (Streamlit / Gradio) $\longleftrightarrow$ Server (FastAPI) $\longleftrightarrow$ Mock AI Model  

---

## 📂 Danh mục các Ví dụ trong Pipeline

| File mã nguồn | Công nghệ | Mục tiêu & Bài toán giải quyết | Cổng chạy (Port) |
| :--- | :--- | :--- | :---: |
| [`01_gradio_sentiment_quickstart.py`](01_gradio_sentiment_quickstart.py) | **Gradio** | Làm quen bọc hàm AI thành Web UI chỉ với 1 hàm `gr.Interface`. Phù hợp làm demo thuật toán siêu tốc (POC). | `7860` |
| [`02_streamlit_state_management.py`](02_streamlit_state_management.py) | **Streamlit** | Thấu hiểu cơ chế Top-to-Bottom Execution và cách dùng `st.session_state` để tránh mất dữ liệu khi kịch bản bị Rerun. | `8501` |
| [`03_backend_api.py`](03_backend_api.py) | **FastAPI + Uvicorn** | Đóng gói logic AI thành Backend API chuẩn: Endpoint POST phân tích cảm xúc (JSON) và Endpoint GET sinh câu trả lời CSKH (Streaming). | `8000` |
| [`04_frontend_app.py`](04_frontend_app.py) | **Streamlit + Requests** | Dashboard vận hành hoàn chỉnh kết nối trực tiếp đến Backend FastAPI, hỗ trợ đầy đủ phân tích JSON và trải nghiệm Typing Effect dạng luồng. | `8501` |

---

## 🚀 Hướng dẫn Chạy Nhanh

### Bước 0: Kích hoạt Môi trường ảo `.venv`
Mở PowerShell tại thư mục `Buoi_06`:
```powershell
# Kích hoạt venv
.\.venv\Scripts\Activate.ps1
```

---

### Ví dụ 1: Thử nghiệm nhanh với Gradio
```powershell
python examples\01_gradio_sentiment_quickstart.py
```
- Truy cập trình duyệt: [http://127.0.0.1:7860](http://127.0.0.1:7860)
- Bấm vào một trong các câu mẫu bên dưới để xem mô hình phân loại cảm xúc (Tích cực / Tiêu cực), số sao ước lượng và độ tin cậy.

---

### Ví dụ 2: Khảo sát vòng đời Streamlit & Session State
```powershell
streamlit run examples\02_streamlit_state_management.py
```
- Truy cập trình duyệt: [http://localhost:8501](http://localhost:8501)
- Bấm nút ở **Cột Trái** (Biến thường): Bạn sẽ thấy số đếm không bao giờ vượt quá 1.
- Bấm nút ở **Cột Phải** (`st.session_state`): Số đếm tăng liên tục và bảng lịch sử bên dưới được tích lũy bền vững.

---

### Ví dụ 3 & 4: Mô hình Client - Server Tách biệt Hoàn chỉnh
Để chạy hệ thống hoàn chỉnh, bạn mở **2 cửa sổ Terminal**:

#### Terminal 1: Khởi động Backend API (FastAPI)
```powershell
uvicorn examples.03_backend_api:app --reload --port 8000
```
- Kiểm tra tài liệu Swagger UI tự động tại: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### Terminal 2: Khởi động Giao diện Người dùng (Streamlit Frontend)
```powershell
streamlit run examples\04_frontend_app.py
```
- Truy cập trình duyệt: [http://localhost:8501](http://localhost:8501)
- **Tab 1:** Nhập nhận xét hoặc chọn nút mẫu $\rightarrow$ Bấm *"Gửi phân tích lên Backend API"* $\rightarrow$ Nhận kết quả từ `/predict` kèm đo thời gian phản hồi (latency).
- **Tab 2:** Nhập yêu cầu $\rightarrow$ Bấm *"Soạn thư phản hồi ngay"* $\rightarrow$ Nhận luồng văn bản trả về từng chữ qua `/predict-stream` với `st.write_stream`.
- **Cuối trang:** Tải file CSV lịch sử toàn bộ các lần phân tích trong phiên.
