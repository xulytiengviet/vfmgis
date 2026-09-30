# Kiến trúc VFMGIS 0.1

VFMGIS chạy trong tiến trình Java của gvSIG. Điểm vào `autorun.py` đăng ký action, action mở `ui.Workspace` trên Swing Event Dispatch Thread. Mỗi cửa sổ giữ một ViewDocument riêng và một MapControl dùng MapContext của view đó. VFMGIS không đổi mã lõi gvSIG và không đóng gói lại các plugin web/mobile.

| Thành phần | Trách nhiệm | Phụ thuộc |
|---|---|---|
| `actions.py` | Đăng ký menu VFMGIS | Andami, ApplicationLocator, ScriptingExtension |
| `ui.py` | Menu, lớp, bản đồ, bảng, tác vụ nền | Swing, MapControl |
| `engine.py` | DAL, truy vấn, hình học, ghi Shapefile | gvSIG Scripting API, JTS |
| `core.py` | Kiểm tra đường dẫn/CRS, dự án, CSV | Thư viện chuẩn Python |
| `sample.py` | Bộ dữ liệu mẫu 6 ô vùng UTM | gvSIG DAL/geom |

## Luồng dữ liệu

Đọc tệp → xác nhận CRS → gvSIG driver → lớp trong MapContext → MapControl vẽ. Lọc thuộc tính sử dụng bộ phân tích biểu thức của gvSIG; không thực thi Python từ ô nhập.

Đọc vector → sao chép hình học → kiểm tra hợp lệ → JTS → tạo Shapefile đầu ra mới. Chuyển CRS dùng `getCRS(source).getCT(target)` và `cloneGeometry().reProject(...)`. JTS thử namespace `org.locationtech`, sau đó `com.vividsolutions` cho runtime cũ.

Buffer, clip, dissolve và centroid tạo schema `ID + GEOMETRY`; UI xác nhận điều này trước khi chạy. Reproject sao chép schema và thuộc tính. Phép cắt chỉ giữ thành phần polygon, bỏ tiếp xúc điểm/đường. Lớp đầu ra chỉ được thêm sau khi ghi xong; tệp ghi lỗi có thể cần xóa thủ công.

## Lưu dự án

`.vfm` là JSON có version, CRS, extent và danh sách nguồn dữ liệu, tên, trạng thái hiển thị. Đường dẫn tương đối giúp di chuyển cả thư mục; dữ liệu khác ổ đĩa Windows giữ đường dẫn tuyệt đối. Kiểm tra tất cả đường dẫn trước khi mở. Lưu qua tệp tạm rồi thay thế để giảm rủi ro tệp dở dang.

## Tác vụ và quy mô

Đọc bảng và xử lý hình học chạy bằng SwingWorker. Khóa điều khiển của cửa sổ trong lúc làm việc; cập nhật Swing khi `done()` được gọi trên EDT. Mở dự án hiện tải tuần tự trên EDT; dự án nhiều lớp có thể làm cửa sổ tạm ngừng phản hồi. Chưa hỗ trợ hủy tác vụ hoặc xử lý hàng triệu đối tượng.

## Mở rộng sau bản 0.1

Các hạng mục chưa triển khai: đọc GeoPackage/GeoJSON, symbol/legend tiếng Việt, chỉnh sửa vector có undo, in bản đồ, chọn không gian theo click, task cancellation, kiểm tra CRS từ metadata thay cho xác nhận thủ công, đóng gói bản gvSIG tùy biến. Chỉ quyết định đóng gói `.exe` sau khi chốt phiên bản gvSIG và chạy kiểm thử Windows thực tế.
