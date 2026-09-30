# VFMGIS — GIS desktop cơ bản bằng tiếng Việt

**Long Ngo phát triển · Phiên bản 0.1.0 thử nghiệm · GPL-3.0-or-later**

VFMGIS là phần mở rộng desktop chạy **bên trong gvSIG Desktop**, dành cho sinh viên và người học GIS. Giao diện riêng viết bằng Java Swing/Jython, lấy cảm hứng từ bố cục ArcView: danh sách lớp bên trái, bản đồ giữa, bảng thuộc tính dưới. Dữ liệu được đọc và vẽ bằng lõi gvSIG thực; không có bản đồ giả hoặc dịch vụ backend.

> **Trạng thái:** mã nguồn đã có; kiểm thử Python cho mô hình dự án và kiểm tra đầu vào đã chạy. Môi trường phát triển hiện chưa có gvSIG, nên **chưa xác nhận chạy đầu cuối trên gvSIG/Windows**. Đây chưa phải bản phát hành ổn định hoặc bộ cài `.exe` độc lập. Cần thực hiện [kiểm tra tích hợp](docs/KIEM_THU.md) trước khi dùng trong lớp học.

## Chức năng được triển khai

| Nhóm | Chức năng | Phạm vi bản 0.1 |
|---|---|---|
| Dự án | Tạo/mở/lưu `.vfm`, đường dẫn tương đối, lưu CRS và phạm vi | Không nhúng dữ liệu vào dự án |
| Dữ liệu | Shapefile và GeoTIFF | SHP cần `.shp`, `.shx`, `.dbf`, `.prj`; các lớp phải cùng CRS |
| Lớp | Bật/tắt, đổi tên, đổi thứ tự, bỏ khỏi bản đồ | Không xóa tệp nguồn |
| Bản đồ | Kéo di chuyển, cuộn zoom, toàn lớp, lấy tọa độ | Tọa độ theo CRS dự án |
| Thuộc tính | Bảng, sắp xếp, lọc biểu thức, chọn đối tượng | Hiển thị tối đa 2.000 hàng; bảng chỉ đọc |
| Xuất | CSV UTF-8, ảnh PNG, Shapefile kết quả | CSV xuất các hàng đã tải, không phải toàn lớp |
| Phân tích | Buffer, clip vùng, dissolve toàn lớp, centroid | Tạo đầu ra mới; chỉ ID và hình học |
| CRS | Xuất chuyển hệ tọa độ qua gvSIG | Giữ thuộc tính; mở kết quả khác CRS ở dự án mới |
| Đo/thống kê | Khoảng cách phẳng hai điểm; min/max/sum/mean | Mét chỉ cho UTM WGS84 và EPSG:3405/3406; thống kê các hàng đã tải |
| Học tập | Tạo sáu ô vùng mẫu, hướng dẫn nhanh | Dữ liệu giả lập, không phải địa giới |

Toàn bộ nhãn chức năng do VFMGIS tạo dùng tiếng Việt. Các cửa sổ gvSIG gốc, thông báo driver và một số nhãn của hộp thoại hệ thống vẫn phụ thuộc ngôn ngữ gvSIG/Java; **chưa Việt hóa toàn bộ gvSIG**.

## Cài đặt trên Windows

1. Cài gvSIG Desktop có **Scripting/Jython**. API được đối chiếu tài liệu gvSIG 2.3/2.4; cần kiểm thử riêng với bản gvSIG đang dùng. Dùng Java đi kèm bộ gvSIG.
2. Tải mã nguồn: **Code → Download ZIP**, giải nén.
3. Trong gvSIG mở **Tools → Scripting → Scripting Composer**, xác định thư mục `scripts/addons` của môi trường hiện tại. Đóng gvSIG trước khi chép tệp.
4. Chép thư mục `addons/VFMGIS` của kho này vào thư mục `addons` đó. Không chép cả thư mục kho vào `addons`.
5. Mở lại gvSIG, chọn **VFMGIS → Mở VFMGIS**. Nếu menu chưa đăng ký, chạy `addons/VFMGIS/launch.py` trong Scripting Composer.

Có thể dùng bộ chép/cài PowerShell, với **đường dẫn addons thực tế của máy**:

```powershell
.\tools\install.ps1 -AddonsDirectory "C:\duong-dan-thuc-te\scripts\addons"
```

Bộ cài sao lưu thư mục VFMGIS cũ trước khi cập nhật. Không cần quyền quản trị nếu thư mục scripts thuộc người dùng. Không chạy `launch.py` bằng Python 3 ngoài gvSIG: các thư viện `gvsig`, `java`, `javax` do runtime gvSIG cung cấp.

## Bài thực hành đầu tiên

1. **Trợ giúp → Bài thực hành mẫu**, chọn một tên `.shp` mới.
2. Cửa sổ dự án UTM 48N mở ra với sáu ô vùng giả lập, mỗi ô 600 × 600 m.
3. **Thuộc tính** → nhập `ID > 2` → **Áp dụng**: có 4 hàng.
4. **Chọn trên bản đồ**: 4 đối tượng được chọn; thao tác phân tích vẫn xử lý **toàn lớp**.
5. **Phân tích → Vùng đệm**, nhập 100 m, lưu một tệp mới.
6. **Lưu dự án** thành `.vfm`, đóng rồi mở lại để kiểm tra.

## Kiến trúc và nguồn gvSIG

- `core.py`: kiểm tra đầu vào, CRS, dự án JSON, CSV và thống kê; tương thích Python 2.7/3.
- `engine.py`: adapter gvSIG DAL, Shapefile/raster, hình học JTS, chuyển CRS.
- `ui.py`: cửa sổ Swing, MapControl của gvSIG, quản lý lớp và tác vụ nền.
- `actions.py` / `autorun.*`: đăng ký phần mở rộng theo mẫu CoordinateCapture của gvSIG Association.
- `sample.py`, `smoke.py`: dữ liệu bài học và kiểm tra tích hợp trong runtime thật.
- `tools/`: cài đặt và đóng gói; `.github/workflows/`: kiểm thử nguồn và artifact ZIP.

Đã tham khảo trực tiếp [gvsig-desktop-docs](https://github.com/gvSIGAssociation/gvsig-desktop-docs) và điều chỉnh mẫu đăng ký action từ [CoordinateCapture](https://github.com/gvSIGAssociation/gvsig-desktop-scripting-CoordinateCapture). Chi tiết tệp và SHA tại [THIRD_PARTY.md](THIRD_PARTY.md).

`gvsig-web-fw`, `gvsig-online`, `gvnix` và `gvsig-mobile` không được đưa vào bản desktop này vì không cần web server, geoportal hay Android. Không có tuyên bố tương thích plugin ArcView hoặc liên kết chính thức với Esri/gvSIG Association.

## Phát triển và đóng gói

```bash
python -m unittest discover -s tests -v
python -m compileall -q addons tools
python tools/package.py
```

GitHub Actions xuất `VFMGIS-0.1.0-gvsig-addon.zip` trong **Actions → lượt chạy thành công → Artifacts**. ZIP chứa mã nguồn phần mở rộng, tài liệu, bộ cài; không chứa gvSIG/Java và không phải `.exe`.

## Giới hạn cần biết

- Phân tích tối đa 50.000 đối tượng; độ phức tạp hình học vẫn có thể làm tăng RAM và thời gian. Chưa có hủy tác vụ đang chạy.
- Chưa có số hóa/chỉnh sửa đỉnh, undo/redo, bố cục in tỷ lệ, ký hiệu phân lớp, GeoPackage/GeoJSON, WMS/WMTS hoặc cơ sở dữ liệu.
- Clip và dissolve chỉ nhận vùng; centroid là trọng tâm toán học, có thể nằm ngoài vùng lõm. Buffer/distance là phép tính phẳng.
- Không đoán CRS từ vị trí hoặc gán mọi dữ liệu VN-2000 cùng một EPSG. Người dùng phải xác nhận CRS nguồn đúng; phép chuyển datum phụ thuộc cấu hình gvSIG.
- Dự án chỉ lưu các lớp do VFMGIS quản lý; tệp `.vfm` không thay thế định dạng dự án gvSIG.
- Chưa đo hiệu năng trên máy Windows và chưa công bố chứng nhận tương thích một bản gvSIG cụ thể.

Xem [kiến trúc](docs/KIEN_TRUC.md) và [kiểm thử](docs/KIEM_THU.md). Mã nguồn GPL-3.0-or-later; xem `LICENSE` và `THIRD_PARTY.md`.
