# Bài giảng Chi tiết: Interface Programming & API Integration

> **Đối tượng:** Team AI ProPTIT D24
> **Thời lượng dự kiến:** 120 phút  
> **Mục tiêu cốt lõi:** Nắm vững khái niệm **Model Context Protocol (MCP)**, hiểu vì sao MCP là tiêu chuẩn tương lai cho AI Agent và biết cách tích hợp MCP Server (Google Stitch) vào IDE; làm chủ cơ chế luồng hoạt động của Streamlit (Top-to-bottom, Session State); tích hợp giao diện Streamlit với API Backend bằng thư viện `requests`; và làm chủ kỹ thuật truyền nhận dữ liệu thời gian thực (HTTP Streaming).

---

### Bảng Phân Bổ Thời Gian Chi Tiết (Lecture Timeline - 120 phút)

| Phần | Nội dung chính | Thời lượng | Trọng tâm sư phạm |
| :--- | :--- | :---: | :--- |
| **Phần 1** | Khởi động & Ôn tập nhanh (Revision) | **5 phút** | Điểm nhanh Client-Server, HTTP/JSON đã học, đặt bài toán làm UI thay thế Swagger UI |
| **Phần 2** | Công cụ Giao diện & Chuyên đề MCP | **55 phút** | • Gradio (10')<br>• **Chuyên đề chuyên sâu MCP & Google Stitch (25')**<br>• Streamlit & Cơ chế Top-to-Bottom, Session State (20') |
| **Phần 3** | Kết nối Giao diện Streamlit với API | **40 phút** | Thực hành viết `requests.post()`, parse JSON, xử lý lỗi kết nối, cập nhật UI |
| **Phần 4** | Streaming Data từ API lên Streamlit | **10 phút** | Demo `StreamingResponse`, Async generator `yield` và `st.write_stream` |
| **Phần 5** | Tổng kết, Q&A & Bài tập về nhà | **10 phút** | Hệ thống hóa kiến thức, giao bài tập về nhà |

---

## 1. Khởi động & Ôn tập nhanh (Revision): Từ API Dịch vụ đến Backend & Frontend UI (5 phút)

> 💡 **Lưu ý giảng dạy:** Vì học viên đã học về khái niệm API và cách sử dụng các API có sẵn của các nền tảng (OpenAI, Gemini...) ở buổi học trước, giảng viên **không giảng lại từ đầu** khái niệm API cơ bản hay cấu trúc JSON. Dành 5 phút đầu giờ để điểm nhanh kiến thức cũ, khơi gợi bối cảnh và đặt bài toán cho buổi học hôm nay: từ việc tiêu thụ (consume) API dịch vụ chuyển sang tự đóng gói mô hình AI thành API Backend và xây dựng Frontend UI.

### 1.1 Điểm nhanh kiến thức cũ & Đặt vấn đề bài học
- **Những gì đã có ở buổi trước:** Học viên đã nắm vững khái niệm API, cách sử dụng các API dịch vụ có sẵn của các nền tảng (như OpenAI, Gemini...) bằng Python/Postman, hiểu cơ chế HTTP Request/Response và định dạng JSON.
- **Vấn đề đặt ra:** Ngoài việc tiêu thụ các API có sẵn, khi phát triển dịch vụ AI riêng, chúng ta cần tự tạo một **Backend API** để đóng gói mô hình, đồng thời người dùng cuối (khách hàng, ban giám khảo, người không biết code) **không thể sử dụng Postman hay đọc Swagger UI**. Họ cần một giao diện trực quan với nút bấm, ô nhập liệu và màn hình hiển thị kết quả ngay tức thì.
- **Nhiệm vụ hôm nay:** Học cách tự tạo **Backend API (với FastAPI)** để đóng gói mô hình AI, và làm chủ **Frontend UI (Gradio/Streamlit)** kết hợp **MCP Stitch** để xây dựng một ứng dụng AI hoàn chỉnh.

---

### 1.2 Nhắc lại: Mô hình Nhà hàng 3 Tầng & Vai trò của Mock Function
Để củng cố tư duy tách rời kiến trúc (Decoupling):

```
[Khách hàng] <---> [Tầng 1: Phòng ăn (UI/Frontend - Streamlit/Gradio)]
                               |
                        (Yêu cầu / Món ăn)
                               v
                    [Tầng 2: Nhân viên phục vụ (API/Backend - FastAPI)]
                               |
                        (Order / Chế biến)
                               v
                    [Tầng 3: Bếp trưởng & Bếp chính (AI Model Core)]
```

1. **Mặt tiền / Phòng ăn (UI/Frontend):** Nơi tiếp xúc trực tiếp với người dùng. Cần trực quan, thân thiện (Streamlit, Gradio).
2. **Nhân viên phục vụ (API Backend):** Nhận Request từ bàn ăn, kiểm tra tính hợp lệ (Pydantic), chuyển xuống bếp và bưng Response về.
3. **Nhà bếp (AI Model Core):** Nơi tiêu tốn tài nguyên nặng (GPU, RAM, weights lớn).
4. **Món ăn giả định (Mock Function):**
   - Khi mô hình AI thật đang huấn luyện hoặc quá nặng, ta viết một hàm giả lập nhận input và trả về kết quả mẫu: `def mock_model(text): return {"prediction": text.upper()}`.
   - **Mục đích:** Giúp kỹ sư kiểm thử toàn bộ luồng kết nối từ UI $\rightarrow$ API $\rightarrow$ UI một cách trơn tru trước khi nhúng mô hình thực tế.

---

## 2. Cơ sở Lý thuyết & Kiến trúc Hệ thống

### 2.1 [Ôn tập nhanh] Giao thức HTTP, Vòng đời Request-Response & Định dạng JSON

Giao thức **HTTP (HyperText Transfer Protocol)** là nền tảng giao tiếp của toàn bộ mạng Internet. Trong bài toán phục vụ mô hình AI, mối quan hệ Client - Server tuân theo vòng đời sau:

1. **Client (Giao diện Streamlit/Gradio):** Tạo ra một thông điệp **HTTP Request** gửi đến Server.
2. **Server (FastAPI):** Nhận request, phân tích cú pháp, gọi hàm dự đoán của mô hình, đóng gói kết quả vào **HTTP Response** gửi ngược lại.

#### Các thành phần chính của HTTP Message
- **HTTP Methods (Phương thức):**
  - `GET`: Yêu cầu máy chủ cung cấp tài nguyên (không làm thay đổi trạng thái hệ thống, thường không có Body).
  - `POST`: Gửi dữ liệu từ Client lên Server để xử lý (thường mang theo Payload lớn như văn bản, mảng số liệu, hoặc file ảnh nhị phân).
- **HTTP Status Codes (Mã trạng thái):**
  - `200 OK`: Xử lý thành công hoàn toàn.
  - `400 Bad Request`: Yêu cầu gửi lên bị sai định dạng.
  - `404 Not Found`: Không tìm thấy đường dẫn (Endpoint).
  - `422 Unprocessable Entity`: Dữ liệu đúng cú pháp JSON nhưng sai kiểu dữ liệu mà Server yêu cầu (FastAPI/Pydantic trả về mã này rất thường xuyên).
  - `500 Internal Server Error`: Lỗi sập mã nguồn bên trong Server (ví dụ mô hình bị lỗi OOM - Out of Memory).

#### Mô hình hóa Toán học & Dữ liệu của Giao dịch API
Một phiên giao dịch inference giữa Client và Server có thể được biểu diễn như một ánh xạ:

$$ \mathcal{T}: \mathcal{X} \xrightarrow{\text{Request}} \mathcal{S} \xrightarrow{f_\theta} \mathcal{Y} \xrightarrow{\text{Response}} \mathcal{X}' $$

Trong đó:
- $\mathcal{X}$: Không gian dữ liệu đầu vào tại Client (chuỗi văn bản, file ảnh thô).
- $\mathcal{S}$: Cấu trúc dữ liệu chuẩn hóa dạng JSON truyền qua đường truyền mạng. Dữ liệu này được biểu diễn dưới dạng tập hợp các cặp khóa - giá trị:
  $$ \mathcal{Q}_{\text{JSON}} = \left\{ (k_i, v_i) \mid k_i \in \text{String}, v_i \in \{\text{String, Number, Boolean, Array, Object}\} \right\}_{i=1}^n $$
- $f_\theta$: Hàm suy luận của mô hình AI với bộ trọng số $\theta$.
- $\mathcal{Y}$: Kết quả dự đoán (logits, nhãn lớp, điểm tin cậy xác suất $P(y \mid x) \in [0, 1]$).
- $\mathcal{X}'$: Định dạng hiển thị kết quả trên giao diện người dùng.

> ⚠️ **Lưu ý sống còn:** JSON chỉ chấp nhận các kiểu dữ liệu nguyên thủy. Một tensor PyTorch $\mathbf{T} \in \mathbb{R}^{B \times C \times H \times W}$ hoặc mảng NumPy `ndarray` **không thể** nhét trực tiếp vào chuỗi JSON. Bắt buộc phải chuyển đổi về dạng `list` thông qua `.tolist()` hoặc mã hóa chuỗi Base64 trước khi gửi qua API.

---

### 2.2 Gradio: Giải pháp Tạo Giao diện Siêu tốc (10 phút)
- **Bản chất:** Gradio là thư viện mã nguồn mở cho phép biến bất kỳ hàm Python nào thành giao diện web tương tác chỉ với 3-5 dòng code thông qua class `gr.Interface(fn, inputs, outputs)`.
- **Ưu điểm vượt trội:**
  - Tốc độ cực nhanh: Rất thích hợp để làm mockup, test thuật toán, demo đồ án cho giảng viên hoặc chia sẻ nhanh với đồng đội thông qua tham số `share=True` (tạo link public `.gradio.live` trong 72h).
  - Tự động sinh giao diện tương ứng theo kiểu dữ liệu (`gr.Textbox`, `gr.Image`, `gr.Audio`).
- **Nhược điểm:** Khó tùy biến bố cục phức tạp, khả năng can thiệp vào CSS và quản lý session nhiều bước bị hạn chế $\rightarrow$ Thường chỉ dùng làm bàn đạp thử nghiệm trước khi chuyển sang Streamlit.

---

### 2.3 Chuyên đề Chuyên sâu: Model Context Protocol (MCP) & Google Stitch (25 phút)

#### Khái niệm Model Context Protocol (MCP) - "Cổng USB Type-C của AI"
**Model Context Protocol (MCP)** là một chuẩn giao tiếp mở do Anthropic giới thiệu vào cuối năm 2024, hiện đang trở thành tiêu chuẩn công nghiệp được hỗ trợ bởi các AI IDE tiên tiến nhất (Antigravity IDE, Cursor, Claude Desktop, v.v.).

- **Vấn đề trước khi có MCP (Sự phân mảnh kết nối):**
  - Khi muốn AI Coding Agent đọc file thiết kế từ Figma/Stitch, đọc schema từ Database hay tương tác với GitHub, mỗi công ty/dịch vụ phải tự xây dựng một extension hoặc plugin riêng. Lập trình viên phải tự viết code API tích hợp riêng biệt, rời rạc và không đồng nhất.
- **Giải pháp của MCP (Giao thức chuẩn hóa mở):**
  - Tương tự như cách cổng **USB-C** thay thế toàn bộ các loại cổng sạc, cáp màn hình, cáp dữ liệu riêng lẻ trên máy tính, **MCP chuẩn hóa mọi luồng kết nối giữa Mô hình AI (Host) và Dữ liệu/Công cụ bên ngoài (Server)**.

#### 3 Thành phần Trụ cột trong Giao thức MCP
Mỗi MCP Server cung cấp 3 loại năng lực cho AI Agent:
1. **Resources (Tài nguyên dữ liệu):** Các nguồn dữ liệu chỉ đọc (read-only data) như file thiết kế, schema database, log hệ thống, tương tự như HTTP GET.
2. **Tools (Công cụ hành động):** Các hàm mà AI Agent có thể quyết định thực thi (Executable functions) có kèm schema tham số, tương tự như HTTP POST (ví dụ: `get_canvas`, `export_css`).
3. **Prompts (Mẫu câu lệnh có ngữ cảnh):** Các mẫu hướng dẫn chuẩn hóa giúp người dùng tương tác hiệu quả nhất với tài nguyên đó.

#### Kiến trúc 3 Tầng của Hệ sinh thái MCP
Giao tiếp giữa IDE và MCP Server diễn ra thông qua giao thức **JSON-RPC 2.0** (qua Standard I/O hoặc Server-Sent Events):

```
+-------------------------------------------------------------------+
|                        AI IDE (MCP Host)                          |
|    [AI Coding Agent / LLM Engine] <---> [MCP Client Manager]     |
+-------------------------------------------------^-----------------+
                                                  | JSON-RPC 2.0 (Stdio / SSE)
                                                  v
+-------------------------------------------------------------------+
|                     Google Stitch MCP Server                      |
|   - Exposes Tools: `get_canvas_hierarchy`, `export_color_tokens`  |
|   - Exposes Resources: `stitch://project-d24/dashboard_ui`        |
+-------------------------------------------------^-----------------+
                                                  | REST API / Cloud Sync
                                                  v
+-------------------------------------------------------------------+
|             Nền tảng Thiết kế Google Stitch (Cloud)               |
+-------------------------------------------------------------------+
```

#### Bảng so sánh Toàn diện: MCP vs. API Truyền thống
Giảng viên nhấn mạnh bảng so sánh này để học viên thấy rõ bước chuyển dịch công nghệ:

| Tiêu chí | API Truyền thống (REST / HTTP) | Giao thức MCP (Model Context Protocol) |
| :--- | :--- | :--- |
| **Đối tượng gọi** | Do **con người** tự viết code gọi thủ công (`requests.post`) | Do **AI Agent** tự động gọi dựa theo prompt của người dùng |
| **Khám phá công cụ (Discovery)** | Tĩnh: Dev phải đọc tài liệu Swagger/Postman và hardcode endpoint | Động: Agent tự kết nối MCP Server, tự đọc danh sách Tools & Schema có sẵn |
| **Tính tương thích** | Mỗi dịch vụ có cấu trúc request/response riêng biệt | Chuẩn hóa chung một giao thức (JSON-RPC 2.0) cho mọi công cụ |
| **Vai trò trong lập trình UI** | Dev tự nhìn thiết kế, tự code frontend, tự viết hàm gọi API | AI Agent đọc trực tiếp canvas thiết kế qua MCP, tự sinh code Streamlit chuẩn xác |

#### Google Stitch là gì?
**Google Stitch** (`stitch.withgoogle.com`) là nền tảng thiết kế giao diện ứng dụng web/mobile dựa trên Generative AI của Google Labs. Người dùng chỉ cần cung cấp prompt văn bản hoặc tải lên bản phác thảo tay, Stitch sẽ tạo ra các màn hình UI hoàn chỉnh với đầy đủ bảng màu (Color Palette), khoảng cách (Padding, Margins), và cấu trúc component.

#### Điểm đột phá khi kết hợp Stitch + MCP:
1. Kỹ sư AI không cần mở trình duyệt, nhìn mã màu rồi gõ từng dòng CSS/HTML thủ công.
2. AI Coding Agent trong IDE có quyền gọi trực tiếp tool của Stitch để đọc thông số của Canvas thiết kế.
3. Agent tự động chuyển đổi các Component thị giác trên Canvas thành mã nguồn Frontend (React, HTML hoặc Streamlit layout) chuẩn xác từng pixel.

---

### 2.4 Streamlit: Cơ chế Top-to-Bottom & Session State (20 phút)

Điểm khác biệt lớn nhất giữa Streamlit và các framework web truyền thống (như React hay Django) là **Mô hình thực thi theo kịch bản (Script Execution Model)**:

```
[Người dùng tương tác: Bấm nút / Gõ text]
                     |
                     v
   [Streamlit kích hoạt sự kiện RERUN]
                     |
                     v
   [Toàn bộ file .py được chạy lại từ dòng 1 -> dòng cuối]
                     |
                     v
   [Render lại toàn bộ giao diện dựa trên code mới]
```

#### Vấn đề mất trạng thái (Stateless Pitfall)
Nếu ta khai báo một biến đếm thông thường:
```python
count = 0
if st.button("Tăng"):
    count += 1
st.write(count)
```
Mỗi khi bấm nút, Streamlit chạy lại từ dòng 1, gán lại `count = 0`, sau đó mới vào `if st.button`, tăng lên 1 và in ra 1. Bấm nút lần thứ 2, `count` lại bị gán về 0! Biến này sẽ **không bao giờ vượt quá 1**.

#### Giải pháp: Không gian trạng thái phiên (Session State)
Streamlit cung cấp `st.session_state` hoạt động như một vùng nhớ liên tục (persistent dictionary) gắn liền với phiên duyệt web của từng người dùng:

$$ S_{t+1} = \begin{cases} S_t & \text{khi rerun không làm thay đổi trạng thái} \\ g(S_t, \text{action}) & \text{khi người dùng thực hiện một tương tác có gán state} \end{cases} $$

Mọi dữ liệu cần lưu giữ qua các lần chạy (lịch sử trò chuyện, kết quả dự đoán, file đã upload) đều phải được lưu trữ trong `st.session_state`.

> 💡 **Gợi ý giảng dạy:** Dành 3 phút cho sinh viên tự gõ thử đoạn code biến đếm lỗi ở trên để tận mắt thấy con số bị "kẹt" ở 1. Đây là bài học thực tế sâu sắc nhất giúp sinh viên ghi nhớ nguyên lý hoạt động của Streamlit.

---

### 2.5 Cơ chế Truyền Dữ liệu Thời gian thực (Streaming vs Blocking) (10 phút)

Trong các bài toán Generative AI (LLMs sinh văn bản, Speech-to-Text), thời gian để mô hình sinh xong toàn bộ câu trả lời có thể mất từ 5 đến 30 giây:

$$ T_{\text{total}} = T_{\text{prefill}} + \sum_{i=1}^{M} t_{\text{decode}}^{(i)} $$

Trong đó $M$ là tổng số lượng tokens cần sinh.

- **Cơ chế Blocking truyền thống:** Client gửi request và máy chủ giữ kết nối im lặng cho tới khi $M$ tokens được tạo xong mới đóng gói JSON gửi về. Người dùng phải nhìn màn hình loading xoay tròn trong 10-20 giây. Thời gian chờ phản hồi đầu tiên (**Time To First Byte - TTFB**) bằng $T_{\text{total}}$.
- **Cơ chế Streaming (Chunked Transfer Encoding):** Máy chủ sử dụng header HTTP `Transfer-Encoding: chunked`. Ngay khi sinh được token $t_1$, máy chủ lập tức đẩy token này qua đường ống mạng về Client. Client hứng được token nào thì in ngay token đó ra màn hình.
  - Kết quả: TTFB giảm xuống chỉ còn $T_{\text{prefill}} \approx 200 - 500\text{ms}$. Người dùng nhìn thấy văn bản chạy ra từng chữ một (Typing Effect) tương tự ChatGPT, tạo cảm giác hệ thống phản hồi ngay lập tức.

---

## 3. Triển khai Mã nguồn & Hướng dẫn Thực hành (Code Walkthrough)

Tiến trình thực hành được chia thành các chặng theo đúng timeline 120 phút của buổi học:
- **Chặng 1 [Phần 2 - 10 phút]:** Thử nghiệm bọc hàm với Gradio (`gradio_quickstart.py`).
- **Chặng 2 [Phần 2 - 25 phút]:** Chuyên đề MCP & Google Stitch: Cấu hình `mcp.json` và yêu cầu AI Agent đọc bản vẽ tự động sinh code UI.
- **Chặng 3 [Phần 3 - 40 phút]:** Sử dụng Template Backend FastAPI (`backend_api.py`) và xây dựng Frontend Streamlit (`frontend_app.py`) kết nối API qua `requests.post()`.
- **Chặng 4 [Phần 4 - 10 phút]:** Kỹ thuật Streaming thời gian thực: Kết nối endpoint streaming và hiển thị với `st.write_stream`.

---

### 3.1 [Phần 2 - 10 phút] Dựng nhanh Giao diện Thử nghiệm với Gradio (`gradio_quickstart.py`)

Gradio phù hợp nhất cho các buổi demo ngắn, báo cáo tiến độ nội bộ hoặc tạo đường link chia sẻ tạm thời qua Internet (`share=True`).

```python
import gradio as gr

# 1. Định nghĩa Mock Model (Hàm giả lập xử lý AI)
def mock_analyze_sentiment(text: str) -> str:
    """Hàm giả lập phân tích cảm xúc văn bản."""
    clean_text = text.strip()
    if not clean_text:
        return "Vui lòng nhập nội dung hợp lệ!"
    
    # Giả lập logic dự đoán
    length = len(clean_text)
    sentiment = "TÍCH CỰC (Positive)" if length % 2 == 0 else "TIÊU CỰC (Negative)"
    confidence = min(0.5 + (length / 100.0), 0.99)
    
    return f"Kết quả: {sentiment} | Độ tin cậy: {confidence:.2%}"

# 2. Xây dựng giao diện với Interface
demo = gr.Interface(
    fn=mock_analyze_sentiment,
    inputs=gr.Textbox(lines=3, placeholder="Nhập câu tiếng Việt cần phân tích cảm xúc..."),
    outputs=gr.Textbox(label="Kết quả suy luận của Mô hình"),
    title="Demo Phân Tích Cảm Xúc - ProPTIT D24",
    description="Giao diện thử nghiệm nhanh được tạo tự động bằng Gradio."
)

# 3. Khởi chạy Web Server cục bộ
if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
```

#### Phân tích chi tiết từng dòng code:
- **Dòng 4 - 15:** Khởi tạo hàm `mock_analyze_sentiment`. Hàm này nhận tham số `text: str` và trả về chuỗi kết quả. Khi tích hợp mô hình PyTorch thực tế, toàn bộ logic tiền xử lý tensor, `model(input_tensor)` và ánh xạ nhãn sẽ nằm trọn trong hàm này.
- **Dòng 18 - 25:** Khởi tạo đối tượng `gr.Interface`. Đây là class cốt lõi của Gradio:
  - `fn=mock_analyze_sentiment`: Chỉ định hàm Python mục tiêu cần bọc thành UI.
  - `inputs=gr.Textbox(...)`: Tự động tạo ô nhập văn bản nhiều dòng (`lines=3`).
  - `outputs=gr.Textbox(...)`: Tự động tạo ô hiển thị chuỗi kết quả trả về từ hàm `fn`.
- **Dòng 29:** `demo.launch(...)` mở một máy chủ web tại địa chỉ `http://127.0.0.1:7860`. Nếu thêm tham số `share=True`, Gradio sẽ tự động tạo một đường link public tạm thời (dạng `xxxx.gradio.live`) có hiệu lực trong 72 giờ qua hầm kết nối (tunnel).

> 💡 **Gợi ý giảng dạy:** Nhắc học viên thấy rõ ưu điểm của Gradio: Không cần quan tâm tới routing, request, response hay CSS. Điểm trừ: Bố cục rất khó tùy biến tự do theo ý muốn.

---

### 3.2 [Phần 2 - 25 phút] Chuyên đề Thực hành: Tích hợp Stitch MCP Server vào IDE

Để sử dụng Google Stitch hỗ trợ sinh code giao diện, chúng ta tiến hành cấu hình MCP Server vào IDE lập trình (ví dụ: Antigravity IDE, Cursor, hoặc Claude Desktop).

#### Bước 1: Khởi tạo và lấy thông tin dự án trên Google Stitch
1. Truy cập `https://stitch.withgoogle.com/` bằng tài khoản Google.
2. Tạo một Workspace mới và thiết kế một màn hình đơn giản (ví dụ: *"Dashboard hiển thị kết quả phân loại ảnh chó mèo kèm thanh xác suất"*).
3. Tại menu cài đặt dự án, sao chép mã định danh dự án (`Project ID`) và Token xác thực.

#### Bước 2: Cấu hình file `mcp.json` trong IDE
Trong thư mục cấu hình của IDE (ví dụ: `.gemini/antigravity/mcp.json` hoặc cấu hình MCP Server của Cursor), khai báo định nghĩa server:

```json
{
  "mcpServers": {
    "stitch-designer": {
      "command": "npx",
      "args": [
        "-y",
        "@google/stitch-mcp-server",
        "--project-id", "proptit-d24-ai-demo",
        "--api-key", "AIzaSyYOUR_STITCH_API_KEY_HERE"
      ],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

#### Bước 3: Ra lệnh cho AI Agent tương tác với Stitch qua MCP
Sau khi lưu cấu hình, khởi động lại bảng điều khiển MCP của IDE. Lúc này AI Agent đã được trang bị các tool đọc canvas của Stitch. Ta chỉ cần mở khung chat của IDE và prompt:

> *"Hãy gọi tool từ stitch-designer để lấy cấu trúc layout của màn hình Dashboard vừa tạo, sau đó sinh mã nguồn Python Streamlit tương ứng với đầy đủ các widget và mã màu như thiết kế."*

Agent sẽ tự động gọi tool, phân tích cấu trúc phân cấp (Hierarchical DOM/Component Tree) và viết ra file code giao diện chính xác.

---

### 3.3 [Template Chuẩn bị sẵn] Backend API với FastAPI (`backend_api.py`)

> 💡 **Lưu ý giảng dạy:** Vì trọng tâm chính của buổi học là làm chủ giao diện **Streamlit/Gradio** và **MCP Stitch**, phần code Backend FastAPI này được giảng viên **cung cấp sẵn dưới dạng template mẫu (`backend_api.py`)** dựa trên các khái niệm HTTP Request/Response đã học ở buổi trước. Giảng viên điểm nhanh cấu trúc file để học viên hiểu cách tự đóng gói API Backend, sau đó cho học viên chạy server trong Terminal:
> ```bash
> uvicorn backend_api:app --reload --port 8000
> ```
> Điều này giúp lớp tiết kiệm thời gian và tập trung trọn vẹn vào việc viết giao diện Streamlit kết nối tới API này.

File này đóng vai trò "Nhà bếp", cung cấp 2 endpoint:
1. Endpoint POST thông thường (`/predict`): Nhận JSON, suy luận và trả JSON.
2. Endpoint GET Streaming (`/predict-stream`): Nhận yêu cầu và stream từng token về Client.

```python
import asyncio
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# 1. Khởi tạo ứng dụng FastAPI với siêu dữ liệu
app = FastAPI(
    title="ProPTIT D24 AI Serving API",
    description="Dịch vụ backend suy luận mô hình và streaming dữ liệu",
    version="1.0.0"
)

# 2. Định nghĩa Schema kiểm định dữ liệu đầu vào (Input Validation)
class TextInferenceRequest(BaseModel):
    text: str = Field(
        ..., 
        min_length=1, 
        max_length=500, 
        description="Đoạn văn bản đầu vào cần phân tích",
        json_schema_extra={"example": "Hôm nay thời tiết rất đẹp, tôi thấy vui."}
    )

# 3. Định nghĩa Schema chuẩn hóa dữ liệu đầu ra (Output Serialization)
class TextInferenceResponse(BaseModel):
    status: str
    original_text: str
    predicted_label: str
    confidence: float

# 4. Endpoint Inference truyền thống (Request-Response JSON chuẩn)
@app.post(
    "/predict", 
    response_model=TextInferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Dự đoán cảm xúc (Standard JSON)"
)
def predict_endpoint(request_data: TextInferenceRequest):
    """
    Nhận chuỗi văn bản JSON, mô phỏng chạy mô hình AI và trả về kết quả JSON.
    """
    raw_text = request_data.text.strip()
    
    # Kiểm tra tính hợp lệ nghiệp vụ
    if not raw_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chuỗi văn bản không được chỉ chứa khoảng trắng."
        )
    
    # Giả lập logic tính toán của mô hình (Mock Model)
    label = "POSITIVE" if len(raw_text) % 2 == 0 else "NEGATIVE"
    score = 0.9425
    
    return TextInferenceResponse(
        status="success",
        original_text=raw_text,
        predicted_label=label,
        confidence=score
    )

# 5. Hàm Generator bất đồng bộ sinh dữ liệu dạng luồng (Token Streamer)
async def mock_llm_token_generator(prompt: str) -> AsyncGenerator[str, None]:
    """Mô phỏng mô hình ngôn ngữ lớn (LLM) trả về từng token kèm độ trễ."""
    simulated_tokens = [
        "Xin", "chào", "team", "AI", "D24!", "Hệ", "thống", "đang", "tiến", "hành",
        "phân", "tích", "chuỗi:", f"\"{prompt}\".", "Mô", "hình", "đánh", "giá", 
        "ngữ", "cảnh", "hoàn", "toàn", "chuẩn", "xác.", "Hoàn", "tất", "suy", "luận!"
    ]
    
    for token in simulated_tokens:
        # Giả lập thời gian tính toán của GPU cho mỗi token (150ms)
        await asyncio.sleep(0.15)
        # Yield dữ liệu kèm khoảng trắng để Client hiển thị
        yield f"{token} "

# 6. Endpoint Streaming dữ liệu về Client qua giao thức HTTP
@app.get(
    "/predict-stream",
    summary="Dự đoán cảm xúc theo cơ chế Streaming thời gian thực"
)
async def predict_stream_endpoint(text: str):
    """
    Duy trì kết nối mở và trả về từng mảnh dữ liệu text/plain.
    """
    if not text or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tham số 'text' không được để trống."
        )
        
    return StreamingResponse(
        mock_llm_token_generator(text.strip()),
        media_type="text/plain"
    )

# Chạy server với lệnh Terminal: uvicorn backend_api:app --reload --port 8000
```

#### Phân tích chi tiết từng dòng code:
- **Dòng 13 - 20:** Lớp `TextInferenceRequest` kế thừa từ `pydantic.BaseModel`. Thư viện Pydantic sẽ tự động ép kiểu và validate: nếu Client gửi dữ liệu thiếu trường `text` hoặc độ dài vượt quá 500 ký tự, FastAPI lập tức trả về mã lỗi `422 Unprocessable Entity` kèm mô tả chi tiết mà lập trình viên không cần viết hàm `if/else` thủ công.
- **Dòng 34:** `@app.post("/predict", response_model=TextInferenceResponse)`:
  - Khai báo phương thức `POST`.
  - Tham số `response_model` đảm bảo dữ liệu trả về từ hàm luôn tuân thủ đúng cấu trúc `TextInferenceResponse`. FastAPI sẽ tự động lọc bỏ các trường nhạy cảm không mong muốn.
- **Dòng 61 - 74:** Hàm `mock_llm_token_generator`:
  - Khai báo với từ khóa `async def` và trả về một `AsyncGenerator`.
  - Thay vì dùng `return`, hàm sử dụng `yield f"{token} "`. Từ khóa `yield` tạm dừng hàm, gửi token hiện tại qua mạng, rồi tiếp tục chạy vòng lặp kế tiếp.
  - `await asyncio.sleep(0.15)` nhường quyền thực thi cho Event Loop của Python trong lúc đợi, không gây nghẽn (blocking) máy chủ khi phục vụ hàng nghìn người dùng đồng thời.
- **Dòng 88 - 93:** `StreamingResponse`: Lớp phản hồi đặc biệt của FastAPI giúp giữ kết nối TCP mở và liên tục ghi các byte dữ liệu ra socket mạng mỗi khi generator nhả ra dữ liệu mới.

---

### 3.4 [Phần 3 & 4 - 50 phút] Xây dựng Frontend Streamlit Kết nối API & Streaming (`frontend_app.py`)

> 💡 **Phân bổ thời gian thực hành:**
> - **Chặng 3 [Phần 3 - 40 phút - Trọng tâm chính]:** Viết giao diện Streamlit, thiết lập layout 2 cột, lấy input của người dùng và gửi HTTP POST request (`requests.post('http://localhost:8000/predict', json=payload)`), bóc tách kết quả hiển thị bằng `st.success()`, và lưu lịch sử vào `st.session_state`.
> - **Chặng 4 [Phần 4 - 10 phút - Nâng cao]:** Bổ sung nút bấm nhận dữ liệu dạng luồng (Streaming), sử dụng `requests.get(..., stream=True)` kết hợp `st.write_stream` để tạo hiệu ứng gõ chữ trực tiếp.

File này đóng vai trò "Mặt tiền", kết nối tới Backend FastAPI qua mạng:

```python
import time
import requests
import streamlit as st

# 1. Cấu hình trang (Phải là lệnh Streamlit đầu tiên trong script)
st.set_page_config(
    page_title="AI Inference Visualizer - ProPTIT D24",
    page_icon="🧠",
    layout="wide"
)

API_BASE_URL = "http://localhost:8000"

# 2. Khởi tạo Session State để lưu giữ trạng thái qua các lần Rerun
if "history" not in st.session_state:
    st.session_state.history = []

if "request_count" not in st.session_state:
    st.session_state.request_count = 0

# 3. Thanh bên (Sidebar) hiển thị thống kê hệ thống
with st.sidebar:
    st.header("⚙️ Thông tin Hệ thống")
    st.info(f"API Server Target: `{API_BASE_URL}`")
    st.metric(label="Tổng số Request đã thực hiện", value=st.session_state.request_count)
    
    if st.button("Xóa lịch sử dự đoán"):
        st.session_state.history.clear()
        st.rerun()

# 4. Tiêu đề và giao diện chính dạng Tabs
st.title("🚀 Hệ thống Giám sát & Trực quan hóa Mô hình AI")
tab_standard, tab_stream = st.tabs(["📦 1. Dự đoán Tiêu chuẩn (JSON API)", "⚡ 2. Dự đoán Streaming (Real-time)"])

# =========================================================================
# TAB 1: KẾT NỐI API TIÊU CHUẨN (REQUESTS POST)
# =========================================================================
with tab_standard:
    st.subheader("Truy vấn Mô hình thông qua RESTful POST Request")
    
    input_text = st.text_area(
        "Nhập văn bản cần đánh giá cảm xúc:", 
        height=100, 
        placeholder="Ví dụ: Khóa học AI của ProPTIT giảng dạy rất dễ hiểu!",
        key="standard_text_input"
    )
    
    if st.button("Gửi dự đoán lên API", type="primary"):
        if not input_text.strip():
            st.warning("⚠️ Vui lòng nhập nội dung trước khi gửi.")
        else:
            with st.spinner("Đang gửi HTTP POST tới FastAPI Backend..."):
                start_time = time.time()
                try:
                    # Đóng gói Dictionary và gửi qua mạng bằng thư viện requests
                    payload = {"text": input_text.strip()}
                    response = requests.post(
                        f"{API_BASE_URL}/predict",
                        json=payload,
                        timeout=5.0
                    )
                    latency = (time.time() - start_time) * 1000  # Đổi sang mili-giây
                    
                    # Kiểm tra mã trạng thái HTTP
                    if response.status_code == 200:
                        result_data = response.json()
                        st.session_state.request_count += 1
                        
                        # Hiển thị kết quả trực quan
                        st.success("✅ Nhận phản hồi thành công từ máy chủ!")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Nhãn dự đoán", result_data["predicted_label"])
                        col2.metric("Độ tin cậy", f"{result_data['confidence']:.2%}")
                        col3.metric("Độ trễ API", f"{latency:.1f} ms")
                        
                        # Lưu vào lịch sử phiên
                        st.session_state.history.append({
                            "type": "Standard",
                            "input": input_text,
                            "output": result_data["predicted_label"],
                            "time": time.strftime("%H:%M:%S")
                        })
                    else:
                        st.error(f"❌ Máy chủ trả về mã lỗi {response.status_code}: {response.text}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("🚨 Không thể kết nối tới máy chủ API! Hãy đảm bảo bạn đã khởi động `backend_api.py` bằng Uvicorn trên cổng 8000.")
                except requests.exceptions.Timeout:
                    st.error("⏳ Yêu cầu quá thời gian chờ (Timeout > 5s). Máy chủ xử lý quá tải.")

# =========================================================================
# TAB 2: KẾT NỐI API STREAMING (CHUNKING VIA ST.WRITE_STREAM)
# =========================================================================
with tab_stream:
    st.subheader("Trải nghiệm Sinh dữ liệu dạng Luồng (Server-Sent Streaming)")
    
    stream_prompt = st.text_input(
        "Nhập chủ đề cần AI sinh văn bản:", 
        placeholder="Ví dụ: Deep Learning with PyTorch",
        key="stream_text_input"
    )
    
    if st.button("Khởi động Luồng Stream", type="secondary"):
        if not stream_prompt.strip():
            st.warning("⚠️ Vui lòng nhập nội dung gợi ý.")
        else:
            try:
                # Định nghĩa một Generator phía Client để đọc từng chunk từ HTTP Stream
                def client_stream_consumer():
                    """Generator đọc luồng byte từ FastAPI và yield ra từng ký tự/từ."""
                    with requests.get(
                        f"{API_BASE_URL}/predict-stream",
                        params={"text": stream_prompt.strip()},
                        stream=True,  # QUAN TRỌNG: Giữ kết nối mạng mở
                        timeout=10.0
                    ) as stream_resp:
                        if stream_resp.status_code == 200:
                            # iter_content giải mã từng chunk byte nhận được từ mạng
                            for chunk in stream_resp.iter_content(chunk_size=None, decode_unicode=True):
                                if chunk:
                                    yield chunk
                        else:
                            yield f"Lỗi từ máy chủ: HTTP {stream_resp.status_code}"

                st.session_state.request_count += 1
                st.write("---")
                st.markdown("#### 💬 Phản hồi trực tiếp từ Mô hình:")
                
                # st.write_stream tự động xử lý generator và tạo hiệu ứng gõ chữ
                st.write_stream(client_stream_consumer)
                
            except requests.exceptions.ConnectionError:
                st.error("🚨 Mất kết nối tới Backend Streaming Server.")

# 5. Hiển thị bảng lịch sử ở cuối trang
if st.session_state.history:
    st.write("---")
    st.subheader("📜 Lịch sử các lần suy luận trong phiên")
    st.dataframe(st.session_state.history, use_container_width=True)
```

#### Phân tích chi tiết từng dòng code:
- **Dòng 13 - 17:** Kiểm tra và khởi tạo `st.session_state.history` và `st.session_state.request_count`. Nếu biến đã tồn tại trong phiên duyệt web, ta không khởi tạo lại để bảo toàn dữ liệu.
- **Dòng 52:** `requests.post(..., json=payload, timeout=5.0)`: Tham số `json=` tự động thực hiện 2 việc: gọi `json.dumps(payload)` để chuyển dictionary thành chuỗi JSON và gắn HTTP header `Content-Type: application/json`. Đặt `timeout=5.0` là chuẩn bắt buộc trong lập trình thực tế để tránh trường hợp ứng dụng bị treo vĩnh viễn khi mạng rớt.
- **Dòng 105 - 120:** Hàm `client_stream_consumer()`:
  - Sử dụng `requests.get(..., stream=True)`. Cờ `stream=True` báo cho thư viện `requests` **không được tải toàn bộ body về bộ nhớ đệm ngay**, mà chỉ đọc phần headers trước và giữ nguyên socket kết nối mở.
  - `stream_resp.iter_content(chunk_size=None, decode_unicode=True)` liên tục lắng nghe trên socket, đọc từng gói tin TCP vừa tới, chuyển thành chuỗi unicode và `yield` ngay lập tức.
- **Dòng 127:** `st.write_stream(client_stream_consumer)`: Hàm tiện ích đỉnh cao được giới thiệu từ Streamlit 1.31+. Nó nhận vào một generator (đồng bộ hoặc bất đồng bộ), tự động cập nhật phần tử DOM trên trình duyệt theo thời gian thực và hiển thị hiệu ứng gõ chữ mượt mà.

---

## 4. Các lỗi thường gặp (Common Pitfalls & FAQ)

Dưới đây là các lỗi kinh điển mà học viên D24 thường xuyên gặp phải khi lần đầu kết nối giao diện và API:

### ❌ Lỗi 1: Nhầm lẫn giữa Biến thường và `st.session_state` làm mất dữ liệu
- **Hiện tượng:** Sau khi bấm nút "Gửi dự đoán", bảng kết quả hiện ra. Nhưng ngay khi người dùng gõ vào một ô text khác hoặc bấm tab khác, kết quả vừa dự đoán **biến mất không dấu vết**.
- **Nguyên nhân:** Do chưa hiểu cơ chế Rerun của Streamlit. Khi tương tác với ô text thứ hai, file `.py` chạy lại từ đầu và biến cục bộ lưu kết quả của lần bấm nút trước bị khởi tạo lại thành rỗng.
- **Cách khắc phục:** Luôn gán kết quả trả về từ API vào `st.session_state.last_result = result_data` và render giao diện dựa trên dữ liệu lưu trong state.

---

### ❌ Lỗi 2: Lỗi `requests.exceptions.ConnectionError: [Errno 111] Connection refused`
- **Hiện tượng:** Giao diện Streamlit báo lỗi màu đỏ rực ngay khi bấm nút gửi.
- **Nguyên nhân:**
  1. Chưa chạy máy chủ FastAPI (chưa bật lệnh `uvicorn`).
  2. Bật FastAPI nhưng nhầm cổng (ví dụ: FastAPI chạy port 8000 nhưng trong code Streamlit lại gõ `http://localhost:8501` - vốn là cổng của chính Streamlit!).
- **Cách khắc phục:** Mở một cửa sổ Terminal riêng, gõ `uvicorn backend_api:app --reload --port 8000`. Kiểm tra bằng cách vào trình duyệt gõ `http://localhost:8000/docs`, nếu thấy Swagger UI hiện lên thì Backend mới thực sự sẵn sàng.

---

### ❌ Lỗi 3: Lỗi `422 Unprocessable Entity` từ FastAPI
- **Hiện tượng:** API không trả về 200 mà trả về mã lỗi 422 kèm theo chuỗi JSON: `{"detail":[{"loc":["body","text"],"msg":"field required"}]}`.
- **Nguyên nhân:** Mismatch (không khớp) giữa Schema của Pydantic và Payload gửi đi từ Client. Ví dụ: Schema trong FastAPI định nghĩa trường là `text`, nhưng trong Streamlit lại đóng gói dictionary là `payload = {"input_content": user_text}`.
- **Cách khắc phục:** So khớp chính xác 100% tên trường (keys) và kiểu dữ liệu (Data types) giữa class `BaseModel` và dictionary gửi đi trong `requests.post(json=...)`.

---

### ❌ Lỗi 4: Streaming không hiện từng chữ mà chờ tải xong mới phụt ra cả đoạn
- **Hiện tượng:** Mặc dù Backend dùng `StreamingResponse`, nhưng trên giao diện Streamlit vẫn phải chờ 5 giây rồi chữ mới hiện ra toàn bộ một lần, mất hoàn toàn hiệu ứng gõ chữ.
- **Nguyên nhân:** Quên tham số `stream=True` trong hàm `requests.get()`, hoặc truyền nhầm chuỗi tĩnh vào `st.write_stream` thay vì truyền một hàm Generator.
- **Cách khắc phục:** Đảm bảo `stream=True` luôn được bật và hàm đọc dữ liệu phải sử dụng từ khóa `yield`.

---

## 5. Tổng kết & Điểm mấu chốt (Key Takeaways) (10 phút)

1. **Mock Function trong Quy trình Phát triển:** Luôn viết hàm giả lập output để hoàn thiện trọn vẹn luồng Frontend $\leftrightarrow$ Backend trước khi cắm mô hình AI nặng.
2. **Kiến trúc Tách biệt (Decoupling):** Phân định rạch ròi trách nhiệm: Frontend (Streamlit) lo giao diện hiển thị; Backend (FastAPI) lo quản lý tài nguyên tính toán (GPU/VRAM) và phục vụ mô hình. Không gộp model nặng vào file script của giao diện.
3. **Kỷ nguyên AI Agent với Model Context Protocol (MCP):**
   - MCP là chuẩn giao tiếp mở đóng vai trò "Cổng USB-C cho AI", giúp LLM/Agent kết nối trực tiếp với công cụ và dữ liệu ngoài.
   - Nhờ MCP Server (như Google Stitch), kỹ sư AI có thể để Agent tự động đọc thiết kế và sinh code giao diện Streamlit thay vì code tay thủ công.
4. **Làm chủ Vòng đời Streamlit:** Ghi nhớ nguyên lý **Top-to-Bottom Execution**. Mọi tương tác đều kích hoạt chạy lại toàn bộ script từ dòng đầu tiên; sử dụng `st.session_state` để lưu giữ lịch sử và trạng thái phiên làm việc bền vững.
5. **Trải nghiệm Thời gian thực với HTTP Streaming:** Luôn áp dụng HTTP Streaming (`StreamingResponse` + `st.write_stream`) cho các bài toán Generative AI / LLMs để giảm thiểu tối đa thời gian phản hồi đầu tiên (Time To First Byte - TTFB) cho người dùng.

---

## 6. Tài liệu tham khảo

- [1] **Streamlit Documentation:** [Streamlit Official Documentation - Get Started](https://docs.streamlit.io/get-started) (Hướng dẫn cài đặt và tổng quan widget).
- [2] **Gradio Guides:** [Gradio Quickstart Guide](https://www.gradio.app/guides/quickstart) (Tổng quan cú pháp `gr.Interface` và chia sẻ link public).
- [3] **Real Python Guide:** [Python Requests: Working with Web APIs](https://realpython.com/python-requests/) (Hướng dẫn chuyên sâu về gửi nhận HTTP Request và xử lý JSON trong Python).
- [4] **FastAPI Documentation:** [FastAPI First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/) (Xây dựng REST API tốc độ cao với Python và Pydantic).
- [5] **Model Context Protocol Specification:** [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) (Đặc tả kỹ thuật chính thức về giao thức kết nối mở MCP của Anthropic).
- [6] **Google Labs:** [Google Stitch: AI-powered UI Design](https://stitch.withgoogle.com/) (Nền tảng sinh và thiết kế UI thông minh).
- [7] **Danh mục Đọc mở rộng & Video bài giảng:** Xem chi tiết tại [reading_list.md](reading_list.md).
