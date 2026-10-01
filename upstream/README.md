# Nguồn core gvSIG nguyên bản

Core đang chạy: **gvSIG Desktop 2.6.0 build 3335**, Andami **2.0.436**. ZIP chính thức được khóa bằng SHA-256 trong `windows/runtime.json`. VFMGIS dùng nguyên bytecode gvSIG và bổ sung tài nguyên tiếng Việt; không biên dịch lại hay thay thế lõi GIS.

Đích nguồn Java tương ứng được ghi trong `core.json`. Workflow `upstream-source.yml` cài Subversion, lấy thông tin SVN và xuất đúng tag, kiểm tra phiên bản POM trước khi lưu vào nhánh `upstream/gvsig-2.0.436`. Không tự chuyển sang trunk hoặc bản khác khi tag không truy cập được.

**Trạng thái ngày 01/10/2026: chưa nhập được cây mã Java gốc.** Cả HTTPS và HTTP trên `devel.gvsig.org` trả `svn: E170013` / `E175012: Connection timed out`. Vì vậy nhánh nguồn chưa được tạo; không có tuyên bố đã fork hay biên dịch toàn bộ core.

Bằng chứng: https://github.com/xulytiengviet/vfmgis/actions/runs/36832939425 (artifact `original-core-provenance`, gồm lỗi của cả hai kết nối). Workflow có thể chạy lại khi upstream truy cập được.
