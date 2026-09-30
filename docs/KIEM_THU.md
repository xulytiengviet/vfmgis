# Kiểm thử và điều kiện phát hành

## Đã thực hiện trong môi trường phát triển

- `python -m unittest discover -s tests -v`: **8/8 đạt**.
- Kiểm tra cú pháp bằng Python 3 cho các tệp Python.
- Đóng gói ZIP nguồn bằng `tools/package.py`.

Các kiểm thử này xác nhận mô hình dự án, đường dẫn tương đối, phát hiện thiếu sidecar, không ghi đè bộ SHP, CRS/đơn vị, số không hữu hạn, thống kê, Unicode và bảo vệ CSV khỏi công thức. **Không xác nhận tính đúng của API Java, vẽ bản đồ hay kết quả xử lý gvSIG.**

## Đã thực hiện: runtime gvSIG/Jython trên Windows

Ngày 30/09/2026: [workflow Windows đạt](https://github.com/xulytiengviet/vfmgis/actions/runs/36690383790), Windows Server 2025 x64, gvSIG 2.6.0 build 3335, Jython 2.7.1 và Java đi kèm runtime. [Bản phát hành đã kiểm tra](https://github.com/xulytiengviet/vfmgis/releases/tag/windows-v0.1.1-20).

- Biên dịch và tự kiểm tra EXE .NET Framework.
- Xác minh SHA-256 ZIP runtime; giải nén bằng chính mã C# của trình cài, vào đường dẫn có dấu cách.
- Tự cài addon và khởi động gvSIG từ EXE.
- `smoke.py` đạt các kiểm tra dữ liệu bên dưới.
- Mở Swing workspace tiếng Việt, nạp lớp SHP, phóng bản đồ, bật/tắt lớp, lưu/đọc mô hình dự án `.vfm`.
- Kết xuất ảnh thật `windows-runtime.png`; đã xem ảnh và xác nhận sáu vùng mẫu được vẽ.

Artifact `windows-build-evidence` của workflow lưu báo cáo `runtime-test.txt`, ảnh giao diện và mã SHA-256. Đây là kiểm tra tự động trên Windows Server; chưa thay thế kiểm thử thủ công trên Windows 10/11 và bộ dữ liệu thực tế.

## Chạy lại kiểm tra tích hợp

Cần cài phần mở rộng vào gvSIG thật, sau đó mở Scripting Composer và chạy `addons/VFMGIS/smoke.py`. Script tạo thư mục tạm riêng, không đụng dữ liệu người dùng.

Script tự kiểm tra:

- Tạo 6 vùng 600 × 600 m; tổng diện tích 2.160.000 m².
- `ID > 2` trả 4 đối tượng; `ID > 4` chọn 2 đối tượng.
- Buffer 100 m, centroid, reproject sinh 6 bản ghi; dissolve sinh 1 bản ghi.
- Clip một lớp bằng chính nó giữ 6 vùng và tổng diện tích.

Các bước kiểm tra thủ công còn cần thực hiện trên máy người dùng:

| Thao tác | Kết quả mong đợi |
|---|---|
| Khởi động gvSIG | Menu VFMGIS xuất hiện đúng một lần |
| Mở workspace | Nhãn Việt, lớp trái, bản đồ giữa, bảng dưới |
| Tạo bài mẫu | 6 vùng vẽ được, toàn lớp, pan/zoom hoạt động |
| Bật/tắt/đổi thứ tự 2 lớp | Thứ tự hiển thị khớp bảng lớp |
| Lọc rồi đổi lớp | Không giữ bảng/biểu thức của lớp cũ |
| Đo cạnh ô mẫu | Xấp xỉ 600 m nếu bắt đúng hai góc |
| CRS EPSG:4326 → đo/buffer | Bị chặn, giải thích cần CRS mét |
| Lưu/mở .vfm | Khôi phục lớp, tên, trạng thái, phạm vi |
| Di chuyển cả thư mục dự án | Đường dẫn tương đối vẫn hoạt động |
| Đóng cửa sổ chưa lưu | Có lựa chọn lưu/bỏ qua/hủy |
| Buffer với tên SHP đã có | Từ chối ghi đè |
| Thiếu .prj/.dbf | Báo lỗi trước khi gọi driver |
| Xuất CSV/PNG | Tệp mở được, dấu Việt đúng, ảnh có bản đồ |
| Đóng/mở VFMGIS nhiều lần | Kiểm tra tài nguyên và view còn trong dự án gvSIG |

Ghi kết quả kèm phiên bản gvSIG, Jython, Java, Windows, EPSG, số đối tượng và ảnh màn hình. Ảnh kết xuất ứng dụng thật nằm trong artifact Windows nêu trên.

## Kiểm tra dữ liệu GIS trước khi phát hành

So sánh buffer/clip/dissolve với dữ liệu kiểm chứng trong một GIS độc lập. Kiểm tra đa vùng, vùng có lỗ, vùng lõm, hình học lỗi, null, dữ liệu rỗng, giao chỉ tại cạnh. Với VN-2000, dùng điểm khống chế đúng múi/kinh tuyến và phương pháp chuyển datum được phê duyệt cho bộ dữ liệu; không suy ra độ chính xác khảo sát chỉ từ EPSG.
