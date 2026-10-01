# Việt hóa trực tiếp gvSIG gốc

## Nguồn dữ liệu và quy trình

`windows/runtime.json` khóa gvSIG Desktop 2.6.0 build 3335 bằng SHA-256. `inventory.py` trích tài nguyên từ ZIP gốc và JAR. `catalog.py` đọc ngữ nghĩa Java Properties, hợp nhất bản gốc/Tây Ban Nha/Anh, giữ khóa không đổi. 148 bộ tài nguyên có tổng 19.336 mục, 9.494 chuỗi nguồn khác nhau.

`vi/*.json`: bản dịch nháp tạo một lần từ các chuỗi giao diện công khai bằng dịch máy (Google Translate). Không gửi dữ liệu người dùng, hình học, dự án hoặc thông tin đăng nhập. Tệp này được lưu trong Git, không tự dịch lúc chạy/build. `seed_translation.py` là công cụ tạo nháp tùy chọn, không được gọi trong CI phát hành.

`overrides.json`: các bản dịch thuật ngữ/thao tác thông dụng đã được rà soát. `key-overrides.json`: hiệu chỉnh theo khóa cho các từ có nhiều nghĩa (ví dụ View/Window). `build.py` ưu tiên giá trị kỹ thuật, bản dịch theo khóa, bản dịch đã rà soát, rồi bản dịch nháp.

Tệp phát hành `localization-report.json` thống kê từng loại và liệt kê nguyên văn mục còn giữ tiếng nguồn. Không coi các mục đó là đã duyệt. Bộ dựng dừng khi thiếu bản dịch hoặc thay đổi biến thay thế. Tên tệp, URL và giá trị số cần thiết cho chương trình được giữ nguyên.

## Cơ chế nạp ngôn ngữ

- `i18n/translations.all/text_vi.properties` qua lớp nạp tài nguyên gốc của Andami.
- Tệp tiếng Việt đi kèm các bộ tài nguyên rời; `lib/vfmgis-language-vi.jar` chứa các tài nguyên có đường dẫn package trong JAR gốc.
- Thêm `locale=vi` vào danh sách ngôn ngữ gốc, không xóa ngôn ngữ khác.
- Truyền `--language=vi` trước khi khởi tạo menu. Không đổi chữ menu sau khi menu đã dựng để che lỗi nạp ngôn ngữ.
- `addons/VFMGIS/native.py` chỉ thiết lập nhãn Swing, thương hiệu VFMGIS và mở khung nhìn gốc. Bytecode lõi gvSIG không bị sửa.

## Cổng kiểm tra và giới hạn

Độ phủ hiện tại: 19.336/19.336 mục (100% trong phạm vi 148 bộ tài nguyên đã kiểm kê). 2.666 mục đã rà soát; 16.630 mục nháp máy; 40 giá trị kỹ thuật.

**Chưa đồng nghĩa Việt hóa toàn bộ sản phẩm 100%.** Công việc còn lại được ghi rõ trong `remaining_review` của báo cáo:

- Rà soát thuật ngữ và ngữ pháp của bản dịch nháp, đặc biệt chức năng chuyên sâu.
- Chuỗi viết trực tiếp trong Java/Jython và các bộ tài nguyên giao diện bên thứ ba chưa được kiểm kê.
- Kiểm tra tất cả hộp thoại, lời nhắc lỗi và bố cục chữ trên Windows 10/11.

CI kiểm tra menu trên giao diện gốc, mở bản đồ gốc với Shapefile thật và các phép xử lý DAL. Ảnh `windows-native.png` và `native-menus.json` là bằng chứng từ runtime. CI không tự chứng nhận mọi màn hình.

## Góp bản dịch

Sửa `overrides.json` theo nguyên văn chuỗi nguồn hoặc `key-overrides.json` theo khóa chính xác. Giữ nguyên `{0}`, `%s`, URL, thẻ HTML, dấu nháy của MessageFormat. Chạy lại `build.py`, xem báo cáo rồi kiểm tra trên gvSIG. Không tăng số mục đã rà soát bằng cách đánh dấu toàn bộ bản dịch máy là hoàn tất.
