# encoding: utf-8
# SPDX-License-Identifier: GPL-3.0-or-later
"""VFMGIS branding and startup on the ORIGINAL gvSIG desktop, without a second UI."""
from __future__ import unicode_literals
from java.util import Locale
from javax.swing import UIManager, JComponent
from org.gvsig.andami import PluginServices
import gvsig

_started = False

def configure_swing():
    Locale.setDefault(Locale('vi', 'VN'))
    JComponent.setDefaultLocale(Locale('vi', 'VN'))
    labels = {
        'OptionPane.okButtonText': 'Đồng ý', 'OptionPane.cancelButtonText': 'Hủy',
        'OptionPane.yesButtonText': 'Có', 'OptionPane.noButtonText': 'Không',
        'OptionPane.messageDialogTitle': 'Thông báo', 'OptionPane.titleText': 'Chọn tùy chọn',
        'FileChooser.openButtonText': 'Mở', 'FileChooser.saveButtonText': 'Lưu',
        'FileChooser.cancelButtonText': 'Hủy', 'FileChooser.updateButtonText': 'Cập nhật',
        'FileChooser.helpButtonText': 'Trợ giúp', 'FileChooser.openDialogTitleText': 'Mở tệp',
        'FileChooser.saveDialogTitleText': 'Lưu tệp', 'FileChooser.lookInLabelText': 'Tìm trong:',
        'FileChooser.saveInLabelText': 'Lưu tại:', 'FileChooser.fileNameLabelText': 'Tên tệp:',
        'FileChooser.filesOfTypeLabelText': 'Kiểu tệp:', 'FileChooser.acceptAllFileFilterText': 'Tất cả tệp',
        'FileChooser.upFolderToolTipText': 'Thư mục cha', 'FileChooser.homeFolderToolTipText': 'Thư mục cá nhân',
        'FileChooser.newFolderToolTipText': 'Tạo thư mục', 'FileChooser.listViewButtonToolTipText': 'Danh sách',
        'FileChooser.detailsViewButtonToolTipText': 'Chi tiết', 'FileChooser.fileNameHeaderText': 'Tên',
        'FileChooser.fileSizeHeaderText': 'Kích thước', 'FileChooser.fileTypeHeaderText': 'Kiểu',
        'FileChooser.fileDateHeaderText': 'Ngày sửa đổi', 'FileChooser.fileAttrHeaderText': 'Thuộc tính',
        'FileChooser.openButtonToolTipText': 'Mở tệp đã chọn', 'FileChooser.saveButtonToolTipText': 'Lưu tệp đã chọn',
        'FileChooser.cancelButtonToolTipText': 'Đóng hộp thoại', 'FileChooser.newFolderButtonText': 'Thư mục mới',
        'FileChooser.newFolderDialogText': 'Tên thư mục mới:', 'FileChooser.newFolderErrorText': 'Không tạo được thư mục',
        'ColorChooser.okText': 'Đồng ý', 'ColorChooser.cancelText': 'Hủy', 'ColorChooser.resetText': 'Đặt lại',
        'ColorChooser.previewText': 'Xem trước', 'ColorChooser.sampleText': 'Văn bản mẫu',
        'ColorChooser.swatchesNameText': 'Bảng màu', 'ColorChooser.swatchesRecentText': 'Gần đây',
        'InternalFrameTitlePane.closeButtonText': 'Đóng', 'InternalFrameTitlePane.maximizeButtonText': 'Phóng lớn',
        'InternalFrameTitlePane.minimizeButtonText': 'Thu nhỏ', 'InternalFrameTitlePane.restoreButtonText': 'Khôi phục'
    }
    for key, text in labels.items(): UIManager.put(key, text)


def start():
    global _started
    if _started: return
    configure_swing()
    frame = PluginServices.getMainFrame()
    # Use gvSIG's native prefix API: setTitle itself prepends this prefix.
    frame.setTitlePrefix('VFMGIS · lõi gvSIG 2.6')
    frame.setTitle('Chưa đặt tên')
    project = gvsig.currentProject()
    if unicode(project.getName()).lower() in ('untitled', 'sin titulo', 'sin título'):
        project.setName('Chưa đặt tên')
    view = project.createView('Bản đồ 01', 'EPSG:4326')
    view.showWindow(maximize=True)
    _started = True
    return view
