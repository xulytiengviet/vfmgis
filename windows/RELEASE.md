# VFMGIS 0.2.0 preview — giao diện gvSIG gốc tiếng Việt

Tải `VFMGIS-Windows.exe`, đóng phiên gvSIG cũ rồi nhấp đúp. Lần đầu tự tải gvSIG 2.6.0 build 3335 và Java (~503 MB), kiểm tra SHA-256, cài riêng vào `%LOCALAPPDATA%\VFMGIS\r3` và mở giao diện gvSIG gốc với `--language=vi`. Không cần cài Java/Python hoặc sửa Registry.

Thay đổi từ 0.1.2: bỏ tự mở cửa sổ Swing riêng; dùng khung nhìn, menu, bảng thuộc tính và công cụ gvSIG nguyên bản. Bổ sung tài nguyên tiếng Việt và nhãn Swing. Giữ nguyên bộ chạy r2 và dữ liệu cũ. Dự án sử dụng `.gvsproj` gốc; `.vfm` cũ chưa được chuyển đổi tự động.

Độ phủ tài nguyên: 19.180/19.180 mục trong 131 bộ, có kiểm tra biến thay thế. 2.621 mục đã rà soát, 16.519 mục nháp dịch máy, 40 giá trị kỹ thuật. **Chưa phải bản Việt hóa toàn bộ sản phẩm 100% đã được kiểm chứng**: còn chuỗi viết trực tiếp trong mã, tài nguyên bên thứ ba và rà soát toàn bộ hộp thoại. Xem `localization-report.json`.

Bản preview chỉ được tải lên khi kiểm thử Windows đạt: giao diện/menu gốc tiếng Việt, bản đồ Shapefile và xử lý dữ liệu thật. `windows-native.png` chụp runtime kiểm thử. EXE chưa ký số; không cần tắt phần mềm bảo vệ Windows. Lần đầu cần Internet, các lần sau dùng runtime đã cài.

GPL-3.0-or-later; lõi gvSIG thuộc gvSIG Association và các tác giả gốc, không thay thế thông tin bản quyền.
