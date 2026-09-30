# Nguồn tham khảo và giấy phép

VFMGIS: Copyright (C) 2026 Long Ngo. GPL-3.0-or-later, xem LICENSE.

## Mã được điều chỉnh

Mẫu `ScriptingExtension`, `createAction`, `registerAction` và `addMenu` trong `addons/VFMGIS/actions.py` được điều chỉnh từ:

- Kho: https://github.com/gvSIGAssociation/gvsig-desktop-scripting-CoordinateCapture
- Tệp: `actions.py`, blob SHA `7b2d9b687c1601f6636d37220cfdacc9a8a945a0`.
- Giấy phép: `LICENSE.txt`, blob SHA `695c13b489585f38e5bac5208c86320625b6c653`.
- Copyright (C) 2007-2018 gvSIG Association; GPL version 3 or later.
- Thay đổi: action/menu tiếng Việt, mở workspace VFMGIS; bỏ icon/i18n family của CoordinateCapture; thêm chống đăng ký lặp.

Cấu trúc `autorun.inf` theo cơ chế addon gvSIG, đối chiếu blob `253ebac60ea48eb56bfceb51f5a1743609f6694f`.

## Tài liệu API đối chiếu

Kho https://github.com/gvSIGAssociation/gvsig-desktop-docs, thư mục `gvsigdocs/es/source/scripting_devel_guide/2.3/`:

- `acceso_a_objetos.rst`: ViewDocument, selection, FeatureSet; SHA `44f534a7af21324f303898f538e29a49b24cb2ec`.
- `cargando_capas.rst`: loadShapeFile/loadRasterFile; SHA `45779941f84ac04664173f4ad87097e7f58f6aa1`.
- `trabajando_con_capas.rst`: createShape, edit/append/commit.
- `modulo_geom.rst`: tạo/chuyển hình học WKT.
- `geoprocesos.rst`: kiến trúc xử lý và giải phóng FeatureSet.

Tài liệu được dùng để viết adapter, không sao chép nguyên văn vào hướng dẫn VFMGIS.

## Phụ thuộc runtime

VFMGIS sử dụng các lớp gvSIG, Java Swing và JTS do bản gvSIG cài trên máy cung cấp. Kho này không phân phối lại binary của chúng. Giữ nguyên giấy phép của từng thành phần nếu sau này đóng gói cùng runtime; GPL của VFMGIS không thay thế giấy phép phụ thuộc. Không sử dụng tài sản, logo hay mã nguồn ArcView/Esri.

API Java đối chiếu bổ sung: `gvsigdocs/javadocs/2.6/html/org/gvsig/fmap/` (MapControl, ViewPort, FLayer, FLayers, FeatureType) và `org/gvsig/app/project/Project.html`. Dùng `getFullEnvelope`, chuyển tọa độ qua ViewPort và `FLayers.move` theo tài liệu 2.6.

## Bản phân phối native 0.2

Bộ tài nguyên ngôn ngữ được trích từ **gvSIG Desktop 2.6.0 build 3335 Windows x64**, đúng ZIP và SHA-256 trong `windows/runtime.json`. Khóa và chuỗi nguồn trong bộ dịch là tài nguyên của gvSIG và các mô-đun đi kèm; bản dịch và mã tích hợp giữ GPL-3.0-or-later. Gói `vfmgis-language-vi.jar` chỉ bổ sung tài nguyên, không thay bytecode Java gốc.

Tài liệu kiến trúc upstream: https://github.com/gvSIGAssociation/gvsig-desktop-docs/blob/master/gvsigdocs/es/source/developers_quick_start/2.3/02_use_gvsig_to_develop_gvsig.rst . Tài liệu này hướng dẫn tích hợp trên bản cài gvSIG 2.x thay vì sao chép toàn bộ workspace lõi cho một phần bổ sung.

Bản dịch nháp được tạo một lần từ chuỗi UI công khai; nguồn phương pháp và phạm vi được ghi trong `localization/README.md`. Không tuyên bố mã lõi gvSIG là mã do VFMGIS tự viết. Không tuyên bố đã biên dịch lại toàn bộ Java upstream.
