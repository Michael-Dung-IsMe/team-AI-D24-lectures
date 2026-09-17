# HƯỚNG DẪN THỰC HÀNH CHI TIẾT - BUỔI 06
# INTERFACE PROGRAMMING & API INTEGRATION

> **Dành cho:** Giảng viên, Trợ giảng & Học viên Team AI ProPTIT D24  
> **Chủ đề bài toán thống nhất:** **"Hệ thống Trợ lý AI Phân tích & Phản hồi Đánh giá Khách hàng (Customer Feedback AI Assistant)"**  
> **Mục tiêu cốt lõi:** Làm chủ quy trình từ thử nghiệm mô hình AI nhanh (POC với Gradio), hiểu cơ chế giao diện động (Streamlit Session State), đóng gói Backend API chuẩn công nghiệp (FastAPI) và tích hợp truyền nhận dữ liệu thời gian thực (HTTP Streaming).

---

## MỤC LỤC
1. [Danh sách Thư viện & Vai trò Kỹ thuật](#1-danh-sách-thư-viện--vai-trò-kỹ-thuật)
2. [Hướng dẫn Thiết lập Môi trường Ảo (venv)](#2-hướng-dẫn-thiết-lập-môi-trường-ảo-venv)
3. [Tổng quan Đề bài Thống nhất & Pipeline Thực hành](#3-tổng-quan-đề-bài-thống-nhất--pipeline-thực-hành)
4. [Hướng dẫn Chi tiết Từng Ví dụ & Kết quả Mong muốn](#4-hướng-dẫn-chi-tiết-từng-ví-dụ--kết-quả-mong-muốn)
   - [Ví dụ 1: Thử nghiệm Siêu tốc với Gradio](#ví-dụ-1-thử-nghiệm-siêu-tốc-với-gradio-01_gradio_sentiment_quickstartpy)
   - [Ví dụ 2: Khảo sát Vòng đời Streamlit & Quản lý Session State](#ví-dụ-2-khảo-sát-vòng-đời-streamlit--quản-lý-session-state-02_streamlit_state_managementpy)
   - [Ví dụ 3: Đóng gói Dịch vụ AI thành Backend API với FastAPI](#ví-dụ-3-đóng-gói-dịch-vụ-ai-thành-backend-api-với-fastapi-03_backend_apipy)
   - [Ví dụ 4: Xây dựng Dashboard Hoàn chỉnh Kết nối Backend API](#ví-dụ-4-xây-dựng-dashboard-hoàn-chỉnh-kết-nối-backend-api-04_frontend_apppy)
5. [Kịch bản Chạy Phối hợp Client - Server (End-to-End Demo)](#5-kịch-bản-chạy-phối-hợp-client---server-end-to-end-demo)
6. [Cẩm nang Khắc phục Lỗi Thường gặp (Troubleshooting & FAQ)](#6-cẩm-nang-khắc-phục-lỗi-thường-gặp-troubleshooting--faq)

---

## 1. Danh sách Thư viện & Vai trò Kỹ thuật

Tất cả các thư viện cần thiết đã được tổng hợp trong file `requirements.txt`:

```txt
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.0
streamlit>=1.31.0
gradio>=4.20.0
requests>=2.31.0
pandas>=2.0.0
```

### Chi tiết vai trò của từng thư viện trong hệ thống:
- **`fastapi`**: Web framework bất đồng bộ (Asynchronous) hiệu năng cực cao, đóng vai trò **"Nhân viên phục vụ / Tầng 2 Backend"** nhận request từ giao diện và trả về kết quả suy luận.
- **`uvicorn[standard]`**: Máy chủ ASGI chạy ngầm cho FastAPI, hỗ trợ xử lý hàng nghìn kết nối đồng thời với thư viện C-speed (`uvloop`, `httptools`).
- **`pydantic`**: Thư viện ép kiểu và kiểm tra tính hợp lệ của dữ liệu (Data Validation). Tự động chặn các request sai định dạng và sinh mã lỗi `422 Unprocessable Entity` rõ ràng.
- **`gradio`**: Thư viện tạo Web UI cực nhanh chỉ với 3-5 dòng code, chuyên dùng cho các bài toán thử nghiệm nhanh thuật toán (POC) hoặc demo báo cáo nội bộ.
- **`streamlit`**: Thư viện dựng giao diện Dashboard AI tương tác cao cấp với Python thuần túy, hỗ trợ quản trị trạng thái (`st.session_state`) và hiển thị dữ liệu dạng luồng (`st.write_stream`).
- **`requests`**: Thư viện HTTP Client kinh điển của Python, giúp Streamlit gửi `GET`/`POST` requests qua mạng tới FastAPI Backend.
- **`pandas`**: Thư viện cấu trúc bảng dữ liệu `DataFrame`, phục vụ quản lý lịch sử đánh giá và xuất file CSV.

---

## 2. Hướng dẫn Thiết lập Môi trường Ảo (venv)

Thực hiện theo các bước sau trong terminal của máy tính (Windows PowerShell hoặc Command Prompt):

### Bước 2.1: Điều hướng tới thư mục Buổi 06
```powershell
cd "d:\ProPTIT\Giáo án dạy team AI D24\Buoi_06"
```

### Bước 2.2: Khởi tạo môi trường ảo Python
```powershell
python -m venv .venv
```
Lệnh trên sẽ tạo một thư mục `.venv` cô lập chứa trình thông dịch Python và thư viện độc lập.

### Bước 2.3: Kích hoạt môi trường ảo
Trên **PowerShell**:
```powershell
.\.venv\Scripts\Activate.ps1
```
*Mẹo khắc phục lỗi quyền thực thi kịch bản (Execution Policy Error):*  
Nếu PowerShell báo lỗi `cannot be loaded because running scripts is disabled on this system`, hãy mở PowerShell dưới quyền Administrator và chạy lệnh:
```powershell
Set-ExecutionPolicy Unrestricted -Scope Process
```
Sau đó kích hoạt lại lệnh trên.

Trên **Command Prompt (CMD)**:
```cmd
.venv\Scripts\activate.bat
```

*(Khi kích hoạt thành công, bạn sẽ thấy tiền tố `(.venv)` xuất hiện ở đầu dòng lệnh).*

### Bước 2.4: Nâng cấp pip và cài đặt toàn bộ thư viện
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Bước 2.5: Kiểm tra cài đặt thành công
```powershell
python -c "import streamlit, gradio, fastapi, requests; print('✅ Tất cả thư viện đã sẵn sàng!')"
```

---

## 3. Tổng quan Đề bài Thống nhất & Pipeline Thực hành

Hệ thống được thiết kế xoay quanh bài toán thực tế: **"Xây dựng Trợ lý AI Phân tích & Phản hồi Đánh giá Khách hàng cho Sàn Thương Mại Điện Tử"**.

### Sơ đồ luồng phát triển 4 chặng:

```
[Chặng 1: Thử nghiệm POC] 
01_gradio_sentiment_quickstart.py (Port 7860)
 └── Dựng UI kiểm tra hàm phân loại đánh giá trong 10 dòng code
           │
           ▼
[Chặng 2: Nắm vững Vòng đời UI] 
02_streamlit_state_management.py (Port 8501)
 └── Trực quan hóa Top-to-Bottom & dùng Session State lưu lịch sử review
           │
           ▼
[Chặng 3: Đóng gói API Backend] 
03_backend_api.py (Port 8000)
 ├── POST /predict: Trả kết quả JSON (Nhãn, Điểm tin cậy, Sao)
 └── GET /predict-stream: Luồng streaming thư trả lời CSKH
           │
           ▼
[Chặng 4: Dashboard Vận hành Toàn diện] 
04_frontend_app.py (Port 8501)
 └── Kết nối API Backend, Tab 1 REST POST, Tab 2 Streaming Typing Effect
```

---

## 4. Hướng dẫn Chi tiết Từng Ví dụ & Kết quả Mong muốn

### Ví dụ 1: Thử nghiệm Siêu tốc với Gradio (`01_gradio_sentiment_quickstart.py`)

#### Mục tiêu:
Giúp học viên làm quen với việc bọc bất kỳ hàm xử lý Python nào thành Web UI trực quan chỉ với `gr.Interface(fn, inputs, outputs)`.

#### Cách chạy:
```powershell
python examples\01_gradio_sentiment_quickstart.py
```

#### Kết quả mong muốn:
- Server mở tại: `http://127.0.0.1:7860`
- Giao diện gồm 1 ô nhập văn bản và 3 ô hiển thị kết quả (Cảm xúc, Độ tin cậy, Số sao).
- Có sẵn 3 câu ví dụ ở dưới cùng trang; bấm vào một ví dụ, hệ thống tự điền và suy luận ngay:
  - *Ví dụ 1: "Sản phẩm dùng rất mượt, giao hàng siêu nhanh..."* $\rightarrow$ **🟢 TÍCH CỰC**, Độ tin cậy `86.0%`, ⭐⭐⭐⭐⭐ (5/5).
  - *Ví dụ 2: "Chất lượng sản phẩm quá tệ, vừa mở ra đã bị nứt vỏ..."* $\rightarrow$ **🔴 TIÊU CỰC**, Độ tin cậy `86.0%`, ⭐☆☆☆☆ (1/5).

---

### Ví dụ 2: Khảo sát Vòng đời Streamlit & Quản lý Session State (`02_streamlit_state_management.py`)

#### Mục tiêu:
Trực quan hóa sự khác biệt giữa biến thông thường và `st.session_state` khi kịch bản Streamlit bị Rerun (chạy lại từ dòng 1 đến dòng cuối).

#### Cách chạy:
```powershell
streamlit run examples\02_streamlit_state_management.py
```

#### Kết quả mong muốn:
- Mở tại: `http://localhost:8501`
- Màn hình chia thành 2 cột so sánh trực tiếp:
  - **Cột Trái (Biến thường):** Bấm nút *"Duyệt 1 Đánh giá"*, biến chỉ nhảy lên `1`. Bấm lần nữa, vẫn là `1`. Khi gõ chữ vào ô text ở dưới, biến lập tức bị reset về `0`.
  - **Cột Phải (`st.session_state`):** Bấm nút, bộ đếm tăng đều đặn `1, 2, 3...`, đồng thời mỗi lần bấm đều ghi nhận một dòng mới vào Bảng Lịch sử bên dưới. Tương tác với bất kỳ widget nào khác cũng không làm mất dữ liệu.

---

### Ví dụ 3: Đóng gói Dịch vụ AI thành Backend API với FastAPI (`03_backend_api.py`)

#### Mục tiêu:
Cung cấp Backend API chuẩn hóa theo phong cách Microservices, phục vụ đồng thời cả yêu cầu REST JSON truyền thống và truyền luồng thời gian thực (Chunked Streaming).

#### Cách chạy:
```powershell
uvicorn examples.03_backend_api:app --reload --port 8000
```
*(Hoặc chạy trực tiếp: `python examples\03_backend_api.py`)*

#### Kết quả mong muốn:
- Server khởi động trên cổng `8000`.
- Truy cập Swagger UI tương tác tại: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Thử nghiệm 2 Endpoints:
  1. **POST `/predict`**:
     - Request Body:
       ```json
       {
         "review_text": "Sản phẩm rất tốt, giao hàng cực nhanh!",
         "product_category": "Điện tử & Công nghệ"
       }
       ```
     - Response (Status 200 OK):
       ```json
       {
         "status": "success",
         "original_review": "Sản phẩm rất tốt, giao hàng cực nhanh!",
         "product_category": "Điện tử & Công nghệ",
         "sentiment_label": "POSITIVE",
         "confidence": 0.88,
         "estimated_stars": 5,
         "recommended_action": "Gửi lời cảm ơn khách hàng và mời đánh giá gian hàng 5 sao."
       }
       ```
  2. **GET `/predict-stream?review_text=Hàng kém chất lượng`**:
     - Trả về luồng `text/plain` từng từ một với delay 120ms/từ mô phỏng GPU LLM.

---

### Ví dụ 4: Xây dựng Dashboard Hoàn chỉnh Kết nối Backend API (`04_frontend_app.py`)

#### Mục tiêu:
Ứng dụng Streamlit đóng vai trò Frontend Client kết nối tới máy chủ FastAPI qua HTTP `requests`, kết hợp xử lý cả REST POST và Streaming Generator.

#### Cách chạy:
*(Yêu cầu file `03_backend_api.py` đang chạy ở cổng 8000)*
```powershell
streamlit run examples\04_frontend_app.py
```

#### Kết quả mong muốn:
- Mở tại: `http://localhost:8501`
- **Thanh bên (Sidebar):** Bấm nút *"Kiểm tra kết nối API"*, trạng thái chuyển thành `🟢 Hoạt động (Online)`.
- **Tab 1 - Phân tích Cảm xúc (POST Request):**
  - Nhập nhận xét hoặc bấm 1 trong 3 nút mẫu.
  - Bấm *"🚀 Gửi phân tích lên Backend API"*.
  - Giao diện hiển thị: Nhãn cảm xúc (Badge xanh/đỏ/vàng), Số sao đánh giá, Độ tin cậy (%), và Độ trễ mạng (Latency tính bằng mili-giây).
  - Tự động ghi vào bảng lịch sử cuối trang.
- **Tab 2 - Trợ lý CSKH Soạn Thư Phản hồi (Real-time Streaming):**
  - Nhập đánh giá của khách hàng $\rightarrow$ Bấm *"✍️ Soạn thư phản hồi ngay"*.
  - Chữ hiển thị chạy từng từ mượt mà ra màn hình (Typing effect) nhờ `st.write_stream`.
- **Cuối trang:** Bảng lịch sử toàn bộ các lượt đánh giá và nút tải file CSV về máy tính.

---

## 5. Kịch bản Chạy Phối hợp Client - Server (End-to-End Demo)

Đây là quy trình giảng viên thực hiện khi giảng dạy trên lớp:

```
┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐
│        TERMINAL 1: BACKEND           │     │         TERMINAL 2: FRONTEND         │
│                                      │     │                                      │
│ $ .\.venv\Scripts\Activate.ps1       │     │ $ .\.venv\Scripts\Activate.ps1       │
│ $ uvicorn examples.03_backend_api:   │     │ $ streamlit run                      │
│     app --reload --port 8000         │     │     examples\04_frontend_app.py     │
│                                      │     │                                      │
│ [Uvicorn running on port 8000]       │     │ [Streamlit running on port 8501]     │
└──────────────────┬───────────────────┘     └──────────────────┬───────────────────┘
                   │                                            │
                   │           HTTP POST /predict               │
                   │ ◄───────────────────────────────────────── │
                   │            JSON Response                   │
                   │ ─────────────────────────────────────────► │
                   │                                            │
                   │        HTTP GET /predict-stream            │
                   │ ◄───────────────────────────────────────── │
                   │      Chunked Streaming (Tokens)            │
                   │ ═════════════════════════════════════════► │
```

1. **Bước 1:** Bật Terminal 1, khởi động FastAPI (`uvicorn examples.03_backend_api:app --reload --port 8000`).
2. **Bước 2:** Bật Terminal 2, khởi động Streamlit (`streamlit run examples\04_frontend_app.py`).
3. **Bước 3:** Trình diễn Tab 1: Phân tích đánh giá, cho học viên thấy Terminal 1 nhận log `POST /predict 200 OK` và Terminal 2 hiển thị thẻ kết quả.
4. **Bước 4:** Trình diễn Tab 2: Bấm nút sinh phản hồi, cho học viên thấy Terminal 1 liên tục đẩy chunk và chữ chạy trên màn hình Streamlit ngay tức thì.
5. **Bước 5 (Tình huống sư phạm):** Giảng viên chủ động tắt Terminal 1 (Ctrl + C) rồi bấm lại nút ở Streamlit $\rightarrow$ Giao diện bắt được ngoại lệ và hiện cảnh báo màu đỏ *"Không thể kết nối tới Backend API"*, giúp học viên hiểu cách xử lý lỗi mạng trong thực tế.

---

## 6. Cẩm nang Khắc phục Lỗi Thường gặp (Troubleshooting & FAQ)

### ❌ Lỗi 1: `requests.exceptions.ConnectionError: [WinError 10061] No connection could be made`
- **Nguyên nhân:** Bạn chưa khởi động Backend FastAPI hoặc Backend bị lỗi dừng giữa chừng.
- **Cách xử lý:** Mở cửa sổ Terminal riêng, chạy lại `uvicorn examples.03_backend_api:app --reload --port 8000`. Kiểm tra địa chỉ `http://127.0.0.1:8000` trên trình duyệt xem có thông báo `"status": "online"` hay chưa.

### ❌ Lỗi 2: Lỗi `422 Unprocessable Entity` khi gọi POST `/predict`
- **Nguyên nhân:** Tên trường trong dictionary gửi đi không khớp với Pydantic model.
- **Cách xử lý:** Kiểm tra file Streamlit: Schema FastAPI yêu cầu khóa là `review_text`, nếu bạn gửi `payload = {"text": ...}` hoặc `{"content": ...}` thì FastAPI sẽ từ chối ngay. Bắt buộc sửa thành:
  ```python
  payload = {"review_text": user_review}
  ```

### ❌ Lỗi 3: Chữ không hiện từng từ mà đợi 5 giây mới hiện hết cả đoạn
- **Nguyên nhân:** Trong lệnh gọi `requests.get()`, lập trình viên quên thêm cờ `stream=True`, hoặc không dùng `iter_content` với `yield`.
- **Cách xử lý:** Đảm bảo cú pháp chuẩn:
  ```python
  with requests.get(url, params=params, stream=True) as resp:
      for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
          if chunk:
              yield chunk
  ```

### ❌ Lỗi 4: Lỗi xung đột cổng `Address already in use` (Port 8000 hoặc 8501 bị chiếm dụng)
- **Nguyên nhân:** Một phiên bản cũ của server vẫn đang chạy ngầm trên cổng đó.
- **Cách xử lý:**
  - Đổi sang cổng khác: `uvicorn examples.03_backend_api:app --reload --port 8001` (và sửa URL tương ứng trên giao diện Streamlit).
  - Hoặc tắt tiến trình đang chiếm cổng trên Windows:
    ```powershell
    Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
    ```

---

> 🎯 **Chúc toàn thể Team AI ProPTIT D24 có một buổi học thực hành thú vị, làm chủ trọn vẹn kỹ năng đóng gói API và xây dựng giao diện AI chuyên nghiệp!**
