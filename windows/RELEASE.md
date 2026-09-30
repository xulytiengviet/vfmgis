Bản 0.1.2 sửa lỗi `PathTooLongException` khi giải nén trên máy Windows người dùng.

Rút ngắn thư mục runtime, bỏ thư mục bọc dài trong ZIP và khởi tạo hỗ trợ đường dẫn dài trước mọi thao tác đường dẫn. EXE tự chứa thông tin .NET Framework 4.8 và manifest; không cần tạo tệp `.config` thủ công. Nếu tệp runtime lần trước đã tải đầy đủ và đúng SHA-256, bản mới dùng lại để tránh tải lại 503 MB. Giữ nguyên thư mục cũ và dữ liệu người dùng.

Tải **VFMGIS-Windows.exe** rồi nhấp đúp trên Windows 10/11 64-bit.

Lần đầu cần Internet để tải gvSIG 2.6.0 và Java đi kèm từ máy chủ chính thức (khoảng 503 MB). Chương trình kiểm tra SHA-256 của runtime, tự giải nén vào LocalAppData và mở VFMGIS. Không cần cài Python, Java hoặc chép plugin thủ công. Những lần sau dùng runtime đã lưu.

Đây là launcher VFMGIS dựa trên gvSIG; bản chạy vẫn dùng lõi gvSIG. Mã nguồn launcher và phần mở rộng ở repository và có trong gói ZIP. Tệp EXE chưa được ký số; không tắt các cơ chế bảo vệ của Windows.

`VFMGIS-Windows.zip` chứa cùng EXE và tài liệu. Bộ tải giữ nguyên runtime gvSIG tải từ nguồn chính thức; không phát hành lại runtime trong EXE/ZIP này.
