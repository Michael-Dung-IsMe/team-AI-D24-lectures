"""
Frontend Streamlit Dashboard - Tương thích với tên file trong bài giảng:
streamlit run frontend_app.py
(Đồng bộ hoàn toàn với examples/04_frontend_app.py)
"""

import time
import requests
import streamlit as st
import pandas as pd

# 1. CẤU HÌNH TRANG STREAMLIT
st.set_page_config(
    page_title="AI Feedback Dashboard - ProPTIT D24",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. KHỞI TẠO SESSION STATE
if "history" not in st.session_state:
    st.session_state.history = []

if "request_count" not in st.session_state:
    st.session_state.request_count = 0

if "server_status" not in st.session_state:
    st.session_state.server_status = "Chưa kiểm tra"

# 3. THANH ĐIỀU KHIỂN BÊN (SIDEBAR)
with st.sidebar:
    st.header("⚙️ Cấu hình Hệ thống")
    api_url = st.text_input("Địa chỉ máy chủ Backend API:", value="http://127.0.0.1:8000")
    
    if st.button("🔍 Kiểm tra kết nối API"):
        try:
            ping_resp = requests.get(f"{api_url}/", timeout=2.0)
            if ping_resp.status_code == 200:
                st.session_state.server_status = "🟢 Hoạt động (Online)"
                st.sidebar.success("Kết nối thành công tới FastAPI!")
            else:
                st.session_state.server_status = f"🟡 Phản hồi mã {ping_resp.status_code}"
        except Exception:
            st.session_state.server_status = "🔴 Mất kết nối (Offline)"
            st.sidebar.error("Không tìm thấy server! Hãy chắc chắn bạn đã chạy file `03_backend_api.py` hoặc `backend_api.py`.")
            
    st.metric(label="Trạng thái Backend", value=st.session_state.server_status)
    st.metric(label="Tổng số lượt phân tích", value=st.session_state.request_count)
    
    st.write("---")
    st.subheader("🧹 Quản trị Phiên")
    if st.button("Xóa toàn bộ lịch sử", type="secondary"):
        st.session_state.history.clear()
        st.session_state.request_count = 0
        st.rerun()

# 4. TIÊU ĐỀ CHÍNH & PHÂN TAB CHỨC NĂNG
st.title("🛍️ Hệ thống Trợ lý AI Phân tích & Phản hồi Đánh giá Khách hàng")
st.caption(r"Dự án tích hợp Frontend Streamlit $\longleftrightarrow$ Backend FastAPI (Team AI ProPTIT D24)")

tab1, tab2 = st.tabs([
    "📦 1. Phân tích Cảm xúc Đánh giá (JSON POST)", 
    "⚡ 2. Trợ lý CSKH Soạn Thư Phản hồi (Real-time Streaming)"
])

# TAB 1: KẾT NỐI API TIÊU CHUẨN
with tab1:
    st.subheader("Đánh giá Cảm xúc & Đề xuất Hành động cho Bộ phận CSKH")
    
    st.write("👉 **Chọn nhanh câu đánh giá mẫu:**")
    c1, c2, c3 = st.columns(3)
    if c1.button("👍 Mẫu Hài lòng (5 sao)"):
        st.session_state["review_input_val"] = "Sản phẩm giao cực kỳ nhanh, chất lượng tuyệt vời, nhân viên tư vấn nhiệt tình!"
    if c2.button("👎 Mẫu Khiếu nại (1 sao)"):
        st.session_state["review_input_val"] = "Hàng nhận được bị nứt vỡ, chất lượng quá tệ, đóng gói cẩu thả, đề nghị hoàn tiền."
    if c3.button("😐 Mẫu Trung tính (3 sao)"):
        st.session_state["review_input_val"] = "Sản phẩm dùng tạm được, giá hơi cao một chút, đóng gói bình thường."

    col_input1, col_input2 = st.columns([3, 1])
    with col_input1:
        user_review = st.text_area(
            "Nội dung đánh giá của khách hàng:",
            value=st.session_state.get("review_input_val", ""),
            height=110,
            placeholder="Nhập nhận xét từ khách hàng...",
            key="tab1_review_area"
        )
    with col_input2:
        category = st.selectbox(
            "Ngành hàng:",
            ["Điện tử & Công nghệ", "Thời trang & Phụ kiện", "Gia dụng & Đời sống", "Khác"]
        )

    if st.button("🚀 Gửi phân tích lên Backend API", type="primary"):
        if not user_review.strip():
            st.warning("⚠️ Vui lòng nhập nội dung đánh giá trước khi gửi.")
        else:
            with st.spinner("Đang gửi HTTP POST request tới FastAPI Backend..."):
                start_time = time.time()
                try:
                    payload = {
                        "review_text": user_review.strip(),
                        "product_category": category
                    }
                    response = requests.post(
                        f"{api_url}/predict",
                        json=payload,
                        timeout=5.0
                    )
                    latency_ms = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.request_count += 1
                        st.success("✅ Phân tích thành công từ mô hình AI!")
                        
                        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                        sentiment_badge = "🟢 TÍCH CỰC" if data["sentiment_label"] == "POSITIVE" else (
                            "🔴 TIÊU CỰC" if data["sentiment_label"] == "NEGATIVE" else "🟡 TRUNG TÍNH"
                        )
                        m_col1.metric("Nhãn Cảm xúc", sentiment_badge)
                        m_col2.metric("Số sao Ước tính", f"{'⭐' * data['estimated_stars']} ({data['estimated_stars']}/5)")
                        m_col3.metric("Độ tin cậy", f"{data['confidence']:.2%}")
                        m_col4.metric("Độ trễ API", f"{latency_ms:.1f} ms")
                        
                        st.info(f"💡 **Hành động CSKH khuyến nghị:** {data['recommended_action']}")
                        
                        st.session_state.history.append({
                            "Thời gian": time.strftime("%H:%M:%S"),
                            "Nội dung": user_review[:60] + ("..." if len(user_review) > 60 else ""),
                            "Ngành hàng": category,
                            "Cảm xúc": data["sentiment_label"],
                            "Sao": data["estimated_stars"],
                            "Độ tin cậy": f"{data['confidence']:.2%}",
                            "Độ trễ": f"{latency_ms:.1f} ms"
                        })
                    elif response.status_code == 422:
                        st.error(f"❌ Lỗi 422 (Unprocessable Entity): Dữ liệu gửi lên sai schema của FastAPI!\n{response.text}")
                    else:
                        st.error(f"❌ Lỗi từ máy chủ ({response.status_code}): {response.text}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("🚨 **Lỗi kết nối (ConnectionError):** Không thể kết nối tới Backend API! "
                             "Hãy đảm bảo bạn đã chạy file `03_backend_api.py` hoặc `backend_api.py` bằng Uvicorn trên cổng 8000.")
                except requests.exceptions.Timeout:
                    st.error("⏳ **Lỗi quá thời gian chờ (Timeout):** Máy chủ không phản hồi trong 5 giây.")

# TAB 2: KẾT NỐI API STREAMING
with tab2:
    st.subheader("Trợ lý AI CSKH Soạn Thư Phản hồi Khách hàng Thời gian thực")
    st.caption("Cơ chế HTTP Streaming: Nhận từng token từ server và hiển thị ngay lập tức (Typing effect).")
    
    stream_review = st.text_input(
        "Nhập đánh giá của khách hàng cần AI soạn câu trả lời:",
        value=user_review if user_review else "Sản phẩm giao rất nhanh, mình ưng ý lắm!",
        key="tab2_input"
    )
    
    if st.button("✍️ Soạn thư phản hồi ngay (Streaming)", type="primary"):
        if not stream_review.strip():
            st.warning("⚠️ Vui lòng nhập nội dung đánh giá.")
        else:
            try:
                def customer_reply_streamer():
                    with requests.get(
                        f"{api_url}/predict-stream",
                        params={"review_text": stream_review.strip()},
                        stream=True,
                        timeout=10.0
                    ) as resp:
                        if resp.status_code == 200:
                            for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
                                if chunk:
                                    yield chunk
                        else:
                            yield f"❌ Lỗi HTTP từ máy chủ: {resp.status_code}"

                st.session_state.request_count += 1
                st.write("---")
                st.markdown("#### 💬 Thư phản hồi gợi ý từ Trợ lý AI:")
                st.write_stream(customer_reply_streamer)
                
            except requests.exceptions.ConnectionError:
                st.error("🚨 Không thể kết nối tới máy chủ Streaming Backend! Kiểm tra xem server ở cổng 8000 có đang chạy không.")

# 5. HIỂN THỊ BẢNG LỊCH SỬ PHÂN TÍCH
st.divider()
st.subheader("📜 Bảng Thống kê & Lịch sử Đánh giá trong Phiên làm việc")

if st.session_state.history:
    df_history = pd.DataFrame(st.session_state.history)
    st.dataframe(df_history, use_container_width=True)
    csv_data = df_history.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Tải lịch sử phân tích (CSV)",
        data=csv_data,
        file_name="ai_feedback_history.csv",
        mime="text/csv"
    )
else:
    st.info("Chưa có lượt phân tích nào trong phiên. Hãy nhập đánh giá và bấm gửi ở Tab 1 để ghi nhận dữ liệu!")
