# Kết quả bản dùng giao diện gvSIG gốc — 01/10/2026

Mã nguồn và tài nguyên VFMGIS đã cập nhật trên nhánh `main`.

## Đã đạt

- 11 kiểm thử Python, gồm đọc/ghi Java Properties, Unicode tiếng Việt, khóa có ký tự thoát và dòng nối.
- Kiểm kê 148 bộ tài nguyên gvSIG và thuật toán GIS: 19.336/19.336 mục có giá trị; không thiếu mục, không lỗi biến thay thế.
- 2.666 mục dùng bản dịch đã rà soát, 16.630 mục nháp máy, 40 giá trị kỹ thuật giữ nguyên. Có thêm khóa bổ sung cho menu upstream thiếu tài nguyên.
- Biên dịch EXE Windows và kiểm tra giải nén khi `LongPathsEnabled=0`.
- Khởi động **cửa sổ gvSIG gốc**, tên VFMGIS, menu tiếng Việt; không mở `Workspace` Swing cũ.
- Kiểm tra nhãn menu con đã sửa và nạp trực tiếp tài nguyên Java của thuật toán Buffer (`Vùng đệm`, `Khoảng cách`).
- Đọc/vẽ Shapefile mẫu, lọc, chọn, buffer, dissolve, centroid, chuyển CRS và clip bằng gvSIG thật.

Lượt Windows: https://github.com/xulytiengviet/vfmgis/actions/runs/36832833211 . Bước `Test bundled gvSIG integration` đã PASS. Artifact `windows-build-evidence` chứa EXE, ZIP, SHA256SUMS, ảnh `windows-native.png`, `native-menus.json` và báo cáo ngôn ngữ. Đã tải artifact xuống và đối chiếu SHA-256 của EXE/ZIP: khớp.

## Các phần chưa hoàn tất

- Bước đăng GitHub Release bị `HTTP 403: Resource not accessible by integration`, dù log xác nhận `Contents: write`. Lượt workflow tổng thể mang trạng thái failure do bước đăng Release; không phải lỗi biên dịch hay chạy GIS. Chưa xác định được chính sách phía GitHub gây từ chối; không tự mở rộng quyền hoặc thay token.
- Kho SVN core gốc không phản hồi qua cả HTTPS và HTTP. Chưa đưa được toàn bộ cây Java upstream vào kho này. Xem `upstream/README.md`.
- Chưa kiểm chứng Việt hóa 100% toàn sản phẩm: còn bản dịch máy cần rà soát, chuỗi viết trực tiếp trong mã, tài nguyên bên thứ ba và các nhánh hộp thoại/lỗi chưa kiểm tra. Độ phủ tài nguyên không phải bằng chứng tất cả màn hình đều hoàn chỉnh.
- Runner là Windows Server 2025, không phải bằng chứng kiểm thử mọi máy Windows 10/11.
