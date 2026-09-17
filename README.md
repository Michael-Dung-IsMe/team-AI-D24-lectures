# Giáo án & Tài liệu học tập - Team AI ProPTIT D24

Repository hiện tại lưu trữ nội dung bài giảng và các file liên quan của các buổi do mình đứng lớp.

## Cấu trúc (Cập nhật theo buổi)

```text
.
├── Buoi_06/           # Buổi 06: Giao diện AI & Tích hợp API (Streamlit, Gradio, FastAPI)
├── Buoi_08/           # Buổi 08: Thu thập dữ liệu & MongoDB Pipeline (Requests, BS4, Playwright, MongoDB)
├── requirements.txt   # Danh sách thư viện Python tổng hợp dùng chung cho toàn khóa
└── README.md          # Tài liệu giới thiệu tổng quan và hướng dẫn thiết lập môi trường
```
---

## Hướng Dẫn Thiết Lập Môi Trường (Setup)

Dự án sử dụng một môi trường ảo Python (`.venv`) duy nhất đặt tại thư mục gốc để phục vụ xuyên suốt tất cả các buổi học.

### 1. Khởi tạo môi trường ảo
Mở terminal tại thư mục gốc của project:
```powershell
# Tạo môi trường ảo .venv
python -m venv .venv

# Kích hoạt môi trường (trên Windows PowerShell)
.\.venv\Scripts\Activate.ps1
```

### 2. Cài đặt các thư viện phụ thuộc
Cài đặt toàn bộ các thư viện cần thiết từ file `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### 3. Cài đặt trình duyệt cho Playwright (dành cho Web Scraping)
```powershell
playwright install chromium
```

---

## Quy Định Nộp Bài Tập Về Nhà (Homework)

1. **Định dạng file nộp:** 
   - Tạo file Jupyter Notebook theo cú pháp: `[Tên]_homework_buoi[XX].ipynb` (Ví dụ: `DungPM_homework_buoi8.ipynb`).
   - Bài làm cần bao gồm: Mã nguồn hoàn chỉnh, giải thích các bước thực hiện và ảnh chụp màn hình minh chứng kết quả (có thể paste trực tiếp ảnh vào cell Markdown).
2. **Vị trí nộp bài:**
   - Đẩy bài làm vào thư mục `BTVN` của buổi tương ứng (Ví dụ: `Buoi_08/BTVN/[Tên]_homework_buoi8.ipynb`).