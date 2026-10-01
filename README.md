# VFMGIS — gvSIG Desktop tiếng Việt

VFMGIS 0.2 dùng **lõi và giao diện desktop nguyên bản của gvSIG 2.6.0 build 3335**. Menu, khung nhìn, bảng thuộc tính, trình biên tập, bố cục in và công cụ GIS đều là thành phần gvSIG. Không mở cửa sổ Swing VFMGIS riêng của phiên bản 0.1 khi khởi động.

**Trạng thái: bản xem trước, chưa được chứng nhận Việt hóa toàn bộ sản phẩm 100%.** Bộ dịch bao phủ 19.336/19.336 mục trong 148 bộ tài nguyên gvSIG và thuật toán GIS của runtime gốc. Đây là độ phủ tài nguyên, không phải tỷ lệ kiểm thử tất cả màn hình. Bản dịch gồm 2.666 mục đã rà soát, 16.630 mục từ bản dịch máy và 40 giá trị kỹ thuật giữ nguyên. Chuỗi viết trực tiếp trong mã, tài nguyên bên thứ ba và mọi nhánh lỗi vẫn cần rà soát. [Báo cáo và phạm vi](localization/README.md).

## Kiến trúc

- **Lõi gốc:** Andami, DAL, MapContext/MapControl, trình đọc vector/raster, hình học, CRS, trình biên tập và bộ xử lý không gian của gvSIG. Không viết lại hay giả lập các lớp này.
- **Ngôn ngữ:** thêm `text_vi.properties` qua cơ chế tài nguyên của gvSIG; gói JAR chỉ chứa tài nguyên tiếng Việt, không thay bytecode lõi.
- **Khởi động:** `--language=vi` được truyền từ đầu, trước khi tạo menu. `native.py` mở khung nhìn gvSIG gốc và thiết lập các nhãn Swing tiếng Việt.
- **Đóng gói:** EXE tự tải bộ chạy chính thức đã khóa SHA-256, thêm tài nguyên tiếng Việt rồi mở gvSIG. Không cần tự cài Java/Python.
- **Dự án:** dùng định dạng `.gvsproj` của gvSIG. Tệp `.vfm` thuộc giao diện thử nghiệm 0.1; không tự chuyển đổi hay ghi đè dữ liệu cũ.

Mã nguồn lõi và các thư viện vẫn thuộc các tác giả gvSIG; VFMGIS là bản phân phối bổ sung tài nguyên ngôn ngữ và mã khởi động. Kho này [chưa nhập được cây mã Java gốc do upstream hết thời gian kết nối](upstream/README.md) và không tuyên bố đã biên dịch lại lõi. Cách tích hợp được tài liệu gvSIG 2.x khuyến nghị: phát triển phần bổ sung trên bản cài gvSIG gốc. Xem [nguồn và giấy phép](THIRD_PARTY.md).

## Windows

Bản dựng bổ sung 148 bộ tài nguyên đã kiểm thử tại [Actions ngày 01/10/2026](https://github.com/xulytiengviet/vfmgis/actions/runs/36832833211); EXE nằm trong artifact `windows-build-evidence`. Bước đăng Release bị GitHub từ chối HTTP 403. [Kết quả và phần còn thiếu](docs/KIEM_THU_NATIVE.md).

Tải **bản 0.2.0 preview** tại [Releases](https://github.com/xulytiengviet/vfmgis/releases), chọn `VFMGIS-Windows.exe`. Bản preview không thay liên kết `releases/latest` của bản 0.1.2 cũ.

1. Đóng VFMGIS/gvSIG đang chạy.
2. Nhấp đúp EXE trên Windows 64-bit.
3. Lần đầu tải khoảng 503 MB gvSIG và Java; sau đó dùng bộ chạy đã lưu.

Bản 0.2 được cài riêng vào `%LOCALAPPDATA%\VFMGIS\r3`. Không xóa bộ chạy `r2` hay dữ liệu người dùng. Không cần sửa Registry; lỗi đường dẫn dài đã có kiểm tra hồi quy. EXE chưa ký số. Báo cáo kiểm thử được lưu trong mỗi lần chạy [GitHub Actions](https://github.com/xulytiengviet/vfmgis/actions).

## Xây dựng từ mã nguồn VFMGIS

Trên Windows có Python 3 và .NET Framework 4.8 build tools:

```powershell
# Tải runtime theo windows/runtime.json và kiểm tra SHA-256 trước khi chạy.
python localization/inventory.py runtime.zip inventory
python localization/build.py inventory/resources.zip dist
./windows/build.ps1
./windows/test-runtime.ps1
```

Bước kiểm kê đọc cả tài nguyên bên trong JAR. Bước dựng chặn mục thiếu và lỗi `{0}`/`%s`/HTML, kiểm tra đọc-ghi Java Properties và tạo `localization-report.json`. **Không gọi dịch vụ dịch trực tuyến khi build hoặc khi sử dụng phần mềm.** Các bản dịch được lưu sẵn trong Git để sửa và duyệt.

Kiểm thử Windows mở chính giao diện gvSIG gốc, kiểm tra nhãn menu, mở Shapefile mẫu và chạy các phép xử lý dữ liệu thật. Chi tiết ở [localization/README.md](localization/README.md). Tài liệu giao diện cũ 0.1 nằm tại [docs/PHIEN_BAN_0_1.md](docs/PHIEN_BAN_0_1.md).

GPL-3.0-or-later. Bản quyền gvSIG Association và các tác giả gốc; phần bổ sung VFMGIS: Long Ngo.
