"""
Ví dụ 2: Cơ chế Top-to-Bottom & Quản lý Session State trong Streamlit
Chủ đề: Hệ thống AI Phân tích & Phản hồi Đánh giá Khách hàng (Customer Feedback AI)
Giáo án Team AI ProPTIT D24 - Buổi 06

Mục tiêu học tập:
1. Trực quan hóa nguyên lý thực thi theo kịch bản (Script Execution Model) của Streamlit.
2. Thấu hiểu 'Stateless Pitfall' (Bẫy mất trạng thái) khi dùng biến Python thông thường.
3. Làm chủ kỹ thuật lưu trữ biến liên tục qua các lần Rerun với st.session_state.
4. Quản lý danh sách đánh giá đã duyệt trong ca làm việc.
"""

import streamlit as st
import datetime

# 1. CẤU HÌNH TRANG (Bắt buộc phải là lệnh Streamlit đầu tiên trong file)
st.set_page_config(
    page_title="Streamlit State Management Demo - ProPTIT D24",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 Mô phỏng Vòng đời Streamlit: Top-to-Bottom & Session State")
st.markdown(
    """
    Khi chuyển từ **Gradio** sang làm **Dashboard chuyên nghiệp trên Streamlit**, học viên thường gặp hiện tượng: 
    *Mỗi khi người dùng bấm nút hoặc gõ phím, trang web tự động chạy lại từ dòng 1 đến dòng cuối (Rerun).* 
    Nếu không biết cách quản lý bộ nhớ phiên, các biến đếm và dữ liệu đánh giá sẽ **bị xóa sạch**!
    """
)

st.divider()

# ==============================================================================
# 2. KHỞI TẠO SESSION STATE (Vùng nhớ bền vững theo từng phiên duyệt web)
# ==============================================================================
if "session_counter" not in st.session_state:
    st.session_state.session_counter = 0

if "processed_reviews" not in st.session_state:
    st.session_state.processed_reviews = []

# ==============================================================================
# 3. BIẾN PYTHON THÔNG THƯỜNG (Sẽ bị reset lại về 0 mỗi khi kịch bản Rerun)
# ==============================================================================
# Lưu ý quan trọng: Dòng này sẽ được thực thi lại mỗi lần có bất kỳ tương tác nào!
normal_variable_counter = 0

# ==============================================================================
# 4. TRỰC QUAN HÓA SO SÁNH 2 CỘT (SIDE-BY-SIDE COMPARISON)
# ==============================================================================
col_left, col_right = st.columns(2)

# --- CỘT TRÁI: CÁCH TIẾP CẬN LỖI (STATELESS PITFALL) ---
with col_left:
    st.error("### ❌ Cách tiếp cận SAI: Dùng Biến Thông Thường")
    st.caption("Biến được khai báo bình thường: `normal_counter = 0`")
    
    st.code(
        """
# Mỗi lần bấm nút, file chạy lại từ đầu:
normal_counter = 0
if st.button("Duyệt review (Biến thường)"):
    normal_counter += 1
st.metric("Tổng đã duyệt", normal_counter)
        """,
        language="python"
    )
    
    # Bấm nút tăng biến thường
    if st.button("👉 Bấm duyệt 1 Đánh giá (Biến thường)", key="btn_normal", type="secondary"):
        normal_variable_counter += 1
        st.toast(f"Đã gán: normal_variable_counter = {normal_variable_counter}", icon="⚠️")
        
    st.metric(
        label="Số lượng review đã duyệt (Biến thường)",
        value=normal_variable_counter,
        delta="Không bao giờ vượt quá 1!" if normal_variable_counter == 1 else "Bị reset về 0"
    )
    
    st.warning(
        "💡 **Giải thích hiện tượng:** Mỗi khi bạn bấm nút, Streamlit rerun lại toàn bộ script. "
        "Dòng `normal_variable_counter = 0` chạy lại, đưa biến về 0. Sau đó mới chạy vào lệnh `if`, "
        "tăng lên 1. Lần bấm tiếp theo chu trình này lặp lại y hệt $\rightarrow$ Giá trị **mãi mãi bị kẹt ở 1**!"
    )

# --- CỘT PHẢI: CÁCH TIẾP CẬN CHUẨN (SESSION STATE) ---
with col_right:
    st.success("### ✅ Cách tiếp cận ĐÚNG: Dùng `st.session_state`")
    st.caption("Khởi tạo an toàn: `if 'key' not in st.session_state: st.session_state.key = 0`")
    
    st.code(
        """
# Kiểm tra nếu chưa tồn tại trong Session thì mới khởi tạo:
if "counter" not in st.session_state:
    st.session_state.counter = 0

if st.button("Duyệt review (Session State)"):
    st.session_state.counter += 1
st.metric("Tổng đã duyệt", st.session_state.counter)
        """,
        language="python"
    )
    
    # Nút bấm tăng biến trong session state
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("👉 Bấm duyệt 1 Đánh giá (Session)", key="btn_session", type="primary"):
            st.session_state.session_counter += 1
            now = datetime.datetime.now().strftime("%H:%M:%S")
            st.session_state.processed_reviews.append({
                "STT": st.session_state.session_counter,
                "Thời gian": now,
                "Nội dung mẫu": f"Đánh giá khách hàng #{st.session_state.session_counter}: Dịch vụ tuyệt vời!",
                "Trạng thái": "Đã xử lý"
            })
            st.toast(f"Đã tăng bộ đếm lên {st.session_state.session_counter}!", icon="✅")
            
    with col_btn2:
        if st.button("🔄 Đặt lại bộ nhớ (Reset State)", key="btn_reset"):
            st.session_state.session_counter = 0
            st.session_state.processed_reviews = []
            st.rerun()

    st.metric(
        label="Số lượng review đã duyệt (Session State)",
        value=st.session_state.session_counter,
        delta=f"+{st.session_state.session_counter} tích lũy" if st.session_state.session_counter > 0 else None
    )

    st.info(
        "💡 **Giải thích:** `st.session_state` hoạt động như một Dictionary lưu trữ dữ liệu bền vững "
        "riêng cho từng trình duyệt của người dùng. Khi Streamlit rerun, dữ liệu trong `session_state` "
        "vẫn được bảo toàn nguyên vẹn."
    )

# ==============================================================================
# 5. HIỂN THỊ DANH SÁCH REVIEW ĐÃ LƯU TRỮ TRONG PHIÊN LÀM VIỆC
# ==============================================================================
st.divider()
st.subheader("📋 Bảng Lịch sử Đánh giá được lưu trong `st.session_state.processed_reviews`")

if st.session_state.processed_reviews:
    st.dataframe(st.session_state.processed_reviews, use_container_width=True)
else:
    st.write("*(Chưa có đánh giá nào được duyệt trong phiên. Hãy bấm nút màu xanh ở Cột Phải để tích lũy dữ liệu!)*")

# Widget phụ để kiểm chứng tính bền vững của state
st.write("---")
st.text_input("✍️ Gõ bất kỳ nội dung nào vào ô này rồi nhấn Enter (để thử kích hoạt Rerun):", placeholder="Gõ thử chữ bất kỳ...")
st.caption("👉 Chú ý: Sau khi bạn gõ text và Enter, Streamlit rerun trang web. Cột Trái sẽ bị reset về 0, nhưng Cột Phải và Bảng Lịch sử vẫn nguyên vẹn!")
