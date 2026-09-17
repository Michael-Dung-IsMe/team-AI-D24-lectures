# Danh sách Tài liệu Tham khảo & Tự học - Buổi 8: MongoDB & Data Crawl

> **Đối tượng:** Team AI ProPTIT D24  
> **Chủ đề:** Web Scraping (Static, Dynamic, API Sniffing) & Lưu trữ Quản lý Dữ liệu với NoSQL MongoDB  
> **Tiêu chuẩn kiểm duyệt:** Tất cả các liên kết trong danh sách này đã được **DOUBLE-CHECK** và xác thực khả dụng (Live & Accessible).

---

## 1. Bảng Tổng hợp Tài liệu Đọc & Tham khảo

| Tiêu đề | URL | Nguồn | Năm | Mức độ | Tóm tắt |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **PyMongo Driver Official Tutorial** | [Link](https://pymongo.readthedocs.io/en/stable/tutorial.html) | MongoDB Official Docs | 2024 | **Core** | Hướng dẫn chính thống về kết nối MongoDB trong Python, các thao tác CRUD cơ bản, truy vấn document và cấu hình connection pool. |
| **Beautiful Soup 4 Documentation** | [Link](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) | Leonard Richardson | 2024 | **Core** | Tài liệu chuẩn của Beautiful Soup, hướng dẫn chi tiết cách parse cây DOM, duyệt tag, tìm kiếm theo thuộc tính và CSS Selector. |
| **Playwright for Python Documentation** | [Link](https://playwright.dev/python/docs/intro) | Microsoft | 2024 | **Core** | Tài liệu chính thức về Playwright Python: tự động hóa trình duyệt headless, xử lý SPA, cuộn trang vô hạn và bắt sự kiện web động. |
| **Requests: HTTP for Humans** | [Link](https://requests.readthedocs.io/en/latest/) | Kenneth Reitz & PSF | 2024 | **Core** | Cẩm nang sử dụng thư viện HTTP chuẩn của Python: Custom Headers, Cookies, Session persistence, timeout và xử lý status code. |
| **MongoDB Aggregation Pipeline Manual** | [Link](https://www.mongodb.com/docs/manual/aggregation/) | MongoDB Official Docs | 2024 | **Advanced** | Tài liệu kỹ thuật nâng cao về xử lý và biến đổi dữ liệu phân tích với các stage `$match`, `$group`, `$project`, `$unwind`. |
| **MongoDB Indexes & Query Optimization** | [Link](https://www.mongodb.com/docs/manual/indexes/) | MongoDB Official Docs | 2024 | **Advanced** | Hướng dẫn thiết lập Single Index, Compound Index, Unique Index để tối ưu hiệu năng đọc/ghi và chống duplicate bản ghi crawl. |
| **Robots.txt Specifications & Introduction** | [Link](https://developers.google.com/search/docs/crawling-indexing/robots/intro) | Google Search Central | 2024 | **Core** | Quy chuẩn chính thức về file robots.txt, User-Agent directive, Disallow/Allow và đạo đức thu thập dữ liệu web an toàn. |
| **Async HTTP Client with aiohttp** | [Link](https://docs.aiohttp.org/en/stable/client_quickstart.html) | aio-libs | 2024 | **Advanced** | Kỹ thuật crawl dữ liệu bất đồng bộ (Asynchronous Crawling) với `aiohttp` và `asyncio` để tăng tốc độ cào hàng ngàn trang cùng lúc. |

---

## 2. Video Tutorials Chọn lọc (Thực hành Thực chiến)

| Tiêu đề Video | URL Video | Kênh / Tác giả | Thời lượng | Mức độ | Tóm tắt nội dung |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Web Scraping with Python - Beautiful Soup Crash Course** | [Xem trên YouTube](https://www.youtube.com/watch?v=XVv6mJpFOb0) | freeCodeCamp.org (JimShapedCoding) | ~60 phút | **Core** | Khóa học ngắn thực chiến: Cào trang web việc làm thực tế, phân tích cấu trúc HTML, lọc thông tin và lưu trữ kết quả có định dạng. |
| **Python MongoDB Tutorial using PyMongo** | [Xem trên YouTube](https://www.youtube.com/watch?v=rE_bJl2GAY8) | Tech With Tim | ~35 phút | **Core** | Hướng dẫn từng bước cách cài đặt, kết nối MongoDB Atlas/Local từ Python, chèn dữ liệu, update và truy vấn nâng cao với toán tử `pymongo`. |

---

## 3. Lộ trình Khuyến nghị Dành cho D24

1. **Giai đoạn 1 (Nắm chắc nền tảng):** Đọc qua tài liệu **Requests** và **Beautiful Soup 4**, sau đó xem video Crash Course của freeCodeCamp để nắm chắc cách bóc tách HTML tĩnh.
2. **Giai đoạn 2 (Xử lý dữ liệu & Lưu trữ):** Đọc **PyMongo Driver Tutorial**, xem video của Tech With Tim và thực hành chèn dữ liệu crawl được vào MongoDB.
3. **Giai đoạn 3 (Thực chiến nâng cao):** Đọc tài liệu **Playwright for Python** để xử lý các trang cuộn vô hạn/SPA; tìm hiểu về **MongoDB Indexes** và **Aggregation Pipeline** để chuẩn bị tập dữ liệu hoàn hảo cho training AI hoặc RAG pipeline.
