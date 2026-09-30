# encoding: utf-8
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import unicode_literals
import math
import os
import traceback
from java.lang import Throwable
import gvsig
from gvsig import geom
from java.awt import BorderLayout, Color, Dimension, FlowLayout, Font, GridLayout
from java.awt.event import MouseAdapter, WindowAdapter
from java.awt.image import BufferedImage
from java.io import File
from javax.imageio import ImageIO
from javax.swing import (JFrame, JPanel, JLabel, JButton, JScrollPane, JSplitPane,
    JTable, JTextField, JMenuBar, JMenu, JMenuItem, JOptionPane, JFileChooser,
    JToolBar, ListSelectionModel, SwingWorker, SwingUtilities, UIManager)
from javax.swing.table import DefaultTableModel
from javax.swing.filechooser import FileNameExtensionFilter
from org.gvsig.fmap.mapcontrol import MapControl
from addons.VFMGIS import core, engine


class ReadOnlyModel(DefaultTableModel):
    def isCellEditable(self, row, column):
        return False


class Job(SwingWorker):
    def __init__(self, owner, work, done):
        SwingWorker.__init__(self)
        self.owner, self.work, self.callback = owner, work, done

    def doInBackground(self):
        return self.work()

    def done(self):
        self.owner.set_busy(False)
        try:
            self.callback(self.get())
        except (Exception, Throwable) as error:
            self.owner.error(error)


class Closing(WindowAdapter):
    def __init__(self, owner):
        self.owner = owner

    def windowClosing(self, event):
        self.owner.close()


class MapMouse(MouseAdapter):
    def __init__(self, owner):
        self.owner, self.start = owner, None

    def mousePressed(self, event):
        if self.owner.busy:
            return
        self.start = self.owner.coordinate(event.getX(), event.getY())

    def mouseReleased(self, event):
        owner = self.owner
        if owner.busy or self.start is None:
            return
        end = owner.coordinate(event.getX(), event.getY())
        if owner.mode == 'pan':
            extent = owner.extent()
            dx, dy = self.start[0] - end[0], self.start[1] - end[1]
            owner.set_extent([extent[0]+dx, extent[1]+dy, extent[2]+dx, extent[3]+dy])
        elif owner.mode == 'capture':
            owner.info('X = %.6f\nY = %.6f\n%s' % (end[0], end[1], owner.crs))
        elif owner.mode == 'measure':
            try:
                core.require_metric(owner.crs)
                if owner.measure_start is None:
                    owner.measure_start = end
                    owner.status.setText('Đã lấy điểm đầu. Nhấp điểm cuối để đo khoảng cách phẳng.')
                else:
                    a = owner.measure_start
                    owner.measure_start = None
                    owner.info('Khoảng cách phẳng: %.3f mét' % math.hypot(end[0]-a[0], end[1]-a[1]))
            except (Exception, Throwable) as error:
                owner.error(error)
        self.start = None

    def mouseMoved(self, event):
        if not self.owner.busy:
            x, y = self.owner.coordinate(event.getX(), event.getY())
            self.owner.status.setText('X: %.5f   Y: %.5f   |   %s   |   %s' %
                                      (x, y, self.owner.crs, self.owner.mode_label))

    def mouseWheelMoved(self, event):
        if not self.owner.busy:
            self.owner.zoom(1.25 ** event.getWheelRotation())


class Workspace(object):
    def __init__(self, crs='EPSG:4326'):
        self.crs = core.crs_code(crs)
        self.records, self.layers, self.table_headers, self.table_data = [], [], [], []
        self.busy, self.dirty, self.project_path = False, False, None
        self.mode, self.mode_label, self.measure_start = 'pan', 'Kéo để di chuyển', None
        self.controls = []
        self.project = gvsig.currentProject()
        self.view = self.project.createView('VFMGIS')
        self.view.setProjection(gvsig.getCRS(self.crs))
        self.map = MapControl()
        self.map.setMapContext(self.view.getMapContext())
        self.map.setCurrentMapTool(None)
        self.frame = JFrame('VFMGIS 0.1 · GIS cơ bản | Long Ngo')
        self.frame.setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE)
        self.frame.addWindowListener(Closing(self))
        self.frame.setSize(1240, 820)
        self.frame.setMinimumSize(Dimension(940, 620))
        self.frame.setLocationRelativeTo(None)
        self.status = JLabel('Sẵn sàng · Thêm lớp dữ liệu hoặc mở bài thực hành')
        self.status.setBorder(__import__('javax.swing', fromlist=['BorderFactory']).BorderFactory.createEmptyBorder(7, 10, 7, 10))
        self.layer_model = ReadOnlyModel([], ['Hiện', 'Tên lớp', 'Loại'])
        self.layer_table = JTable(self.layer_model)
        self.layer_table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION)
        self.layer_table.setRowHeight(28)
        self.layer_table.getColumnModel().getColumn(0).setMaxWidth(48)
        self.layer_table.getSelectionModel().addListSelectionListener(self.layer_selected)
        self.table_model = ReadOnlyModel([], [])
        self.table = JTable(self.table_model)
        self.table.setAutoCreateRowSorter(True)
        self.table.setAutoResizeMode(JTable.AUTO_RESIZE_OFF)
        self.table.setRowHeight(25)
        self.expression = JTextField(25)
        self.expression.setToolTipText('Ví dụ: ID > 2 hoặc TEN = \'Trường học\'')
        self.table_count = JLabel('Chọn lớp rồi bấm Bảng thuộc tính')
        self.build_ui()
        mouse = MapMouse(self)
        self.map.addMouseListener(mouse)
        self.map.addMouseMotionListener(mouse)
        self.map.addMouseWheelListener(mouse)
        self.set_extent([104.7, 9.3, 107.2, 11.1], mark=False)
        self.frame.setVisible(True)

    def button(self, text, callback):
        button = JButton(text)
        button.addActionListener(lambda event: self.safe(callback))
        self.controls.append(button)
        return button

    def safe(self, callback):
        if self.busy:
            return
        try:
            callback()
        except (Exception, Throwable) as error:
            self.error(error)

    def info(self, message):
        JOptionPane.showMessageDialog(self.frame, message, 'VFMGIS', JOptionPane.INFORMATION_MESSAGE)

    def error(self, error):
        traceback.print_exc()
        JOptionPane.showMessageDialog(self.frame,
            'Không hoàn tất thao tác.\n%s' % error, 'VFMGIS · Thông báo', JOptionPane.ERROR_MESSAGE)

    def ask(self, prompt, initial=''):
        return JOptionPane.showInputDialog(self.frame, prompt, initial)

    def build_ui(self):
        bar = JMenuBar()
        menus = [
            ('Dự án', [('Dự án mới', self.new_project), ('Mở dự án…', self.open_project),
                       ('Lưu dự án…', self.save_project), ('Xuất ảnh bản đồ…', self.export_image),
                       ('Đóng VFMGIS', self.close)]),
            ('Dữ liệu', [('Thêm Shapefile…', lambda: self.add_file('shape')),
                        ('Thêm GeoTIFF…', lambda: self.add_file('raster')),
                        ('Bảng thuộc tính', self.attributes), ('Bật / tắt lớp', self.toggle_layer),
                        ('Đổi tên lớp…', self.rename_layer), ('Bỏ lớp khỏi bản đồ', self.remove_layer)]),
            ('Bản đồ', [('Toàn lớp', self.zoom_layer), ('Phóng to', lambda: self.zoom(0.7)),
                       ('Thu nhỏ', lambda: self.zoom(1.4)), ('Di chuyển', lambda: self.set_mode('pan')),
                       ('Lấy tọa độ', lambda: self.set_mode('capture')),
                       ('Đo khoảng cách', lambda: self.set_mode('measure'))]),
            ('Phân tích', [('Vùng đệm…', lambda: self.processing('buffer')),
                          ('Cắt theo vùng…', lambda: self.processing('clip')),
                          ('Gộp toàn bộ vùng…', lambda: self.processing('dissolve')),
                          ('Tạo trọng tâm…', lambda: self.processing('centroid')),
                          ('Xuất chuyển hệ tọa độ…', lambda: self.processing('reproject')),
                          ('Thống kê trường số…', self.stats)]),
            ('Trợ giúp', [('Bài thực hành mẫu', self.demo), ('Hướng dẫn nhanh', self.help),
                         ('Giới thiệu', lambda: self.info('VFMGIS 0.1 · Long Ngo phát triển\n'
                           'Phần mở rộng desktop dùng lõi gvSIG\nGPL-3.0-or-later\n'
                           'Phiên bản thử nghiệm; kiểm tra kết quả trước khi sử dụng.'))])]
        for title, actions in menus:
            menu = JMenu(title)
            for label, callback in actions:
                item = JMenuItem(label)
                item.addActionListener(lambda event, fn=callback: self.safe(fn))
                self.controls.append(item)
                menu.add(item)
            bar.add(menu)
        self.frame.setJMenuBar(bar)
        north = JPanel(BorderLayout())
        title = JLabel('  VFMGIS   /   Không gian học tập GIS')
        title.setFont(Font('Dialog', Font.BOLD, 19))
        title.setForeground(Color(24, 60, 83))
        title.setPreferredSize(Dimension(900, 44))
        north.add(title, BorderLayout.NORTH)
        toolbar = JToolBar()
        toolbar.setFloatable(False)
        for name, fn in [('Thêm lớp', lambda: self.add_file('shape')), ('Lưu', self.save_project),
                         ('＋', lambda: self.zoom(0.7)), ('−', lambda: self.zoom(1.4)),
                         ('Toàn lớp', self.zoom_layer), ('Di chuyển', lambda: self.set_mode('pan')),
                         ('Tọa độ', lambda: self.set_mode('capture')),
                         ('Đo', lambda: self.set_mode('measure')), ('Thuộc tính', self.attributes)]:
            toolbar.add(self.button(name, fn))
        north.add(toolbar, BorderLayout.SOUTH)
        left = JPanel(BorderLayout(4, 8))
        left.add(JLabel('  CÁC LỚP BẢN ĐỒ'), BorderLayout.NORTH)
        left.add(JScrollPane(self.layer_table), BorderLayout.CENTER)
        controls = JPanel(GridLayout(0, 2, 4, 4))
        for name, fn in [('Bật / tắt', self.toggle_layer), ('Đổi tên', self.rename_layer),
                         ('Lên trên', lambda: self.move_layer(-1)), ('Xuống dưới', lambda: self.move_layer(1))]:
            controls.add(self.button(name, fn))
        left.add(controls, BorderLayout.SOUTH)
        left.setPreferredSize(Dimension(265, 450))
        middle = JSplitPane(JSplitPane.HORIZONTAL_SPLIT, left, self.map)
        middle.setDividerLocation(265)
        bottom = JPanel(BorderLayout())
        query = JPanel(FlowLayout(FlowLayout.LEFT))
        query.add(JLabel('Lọc thuộc tính:'))
        query.add(self.expression)
        for name, fn in [('Áp dụng', self.attributes), ('Chọn trên bản đồ', self.select),
                         ('Bỏ lọc', self.clear_filter), ('Xuất CSV', self.export_csv)]:
            query.add(self.button(name, fn))
        bottom.add(query, BorderLayout.NORTH)
        bottom.add(JScrollPane(self.table), BorderLayout.CENTER)
        bottom.add(self.table_count, BorderLayout.SOUTH)
        split = JSplitPane(JSplitPane.VERTICAL_SPLIT, middle, bottom)
        split.setResizeWeight(0.75)
        split.setDividerLocation(490)
        self.frame.add(north, BorderLayout.NORTH)
        self.frame.add(split, BorderLayout.CENTER)
        self.frame.add(self.status, BorderLayout.SOUTH)

    def set_busy(self, busy):
        self.busy = busy
        for control in self.controls:
            control.setEnabled(not busy)
        self.layer_table.setEnabled(not busy)
        self.expression.setEnabled(not busy)
        self.status.setText('Đang xử lý dữ liệu…' if busy else 'Sẵn sàng')

    def job(self, work, done):
        self.set_busy(True)
        self.worker = Job(self, work, done)
        self.worker.execute()

    def selected(self):
        row = self.layer_table.getSelectedRow()
        if row < 0:
            raise ValueError('Hãy chọn một lớp trong danh sách bên trái.')
        return row, self.layers[row]

    def layer_selected(self, event):
        if event.getValueIsAdjusting() or self.busy:
            return
        for index, layer in enumerate(self.layers):
            layer.setActive(index == self.layer_table.getSelectedRow())
        self.table_model.setDataVector([], [])
        self.table_data, self.table_headers = [], []
        self.expression.setText('')
        self.table_count.setText('Bấm Bảng thuộc tính để đọc lớp đang chọn')

    def refresh_layers(self, index=0):
        rows = [['✓' if layer.isVisible() else '—', rec['name'],
                 'Vector' if rec['kind'] == 'shape' else 'Raster']
                for rec, layer in zip(self.records, self.layers)]
        self.layer_model.setDataVector(rows, ['Hiện', 'Tên lớp', 'Loại'])
        self.layer_table.getColumnModel().getColumn(0).setMaxWidth(48)
        if self.layers:
            self.layer_table.setRowSelectionInterval(index, index)
        self.map.getMapContext().invalidate()
        self.dirty = True

    def choose(self, title, extension, save=False):
        chooser = JFileChooser()
        chooser.setDialogTitle(title)
        chooser.setFileFilter(FileNameExtensionFilter(extension.upper(), [extension]))
        result = chooser.showSaveDialog(self.frame) if save else chooser.showOpenDialog(self.frame)
        if result != JFileChooser.APPROVE_OPTION:
            return None
        path = chooser.getSelectedFile().getAbsolutePath()
        if save and not path.lower().endswith('.' + extension):
            path += '.' + extension
        if save and os.path.exists(path) and JOptionPane.showConfirmDialog(
                self.frame, 'Ghi đè tệp này?', 'Xác nhận', JOptionPane.YES_NO_OPTION) != JOptionPane.YES_OPTION:
            return None
        return path

    def add_file(self, kind):
        path = self.choose('Chọn dữ liệu', 'shp' if kind == 'shape' else 'tif')
        if not path:
            return
        if kind == 'shape':
            core.validate_shape(path)
        code = self.ask('Xác nhận EPSG của dữ liệu nguồn (phải trùng dự án %s):' % self.crs, self.crs)
        if code is None:
            return
        if core.crs_code(code) != self.crs:
            raise ValueError('Hãy tạo dự án với CRS nguồn, mở lớp và xuất chuyển hệ tọa độ trước.')
        self.job(lambda: engine.load_layer(self.view, path, kind, self.crs),
                 lambda layer: self.register(layer, path, kind))

    def register(self, layer, path, kind, zoom=True):
        native = self.view.getMapContext().getLayers()
        native.move(layer, native, 0, None)
        self.layers.insert(0, layer)
        self.records.insert(0, {'path': os.path.abspath(path), 'kind': kind,
                               'name': layer.getName(), 'visible': True})
        self.refresh_layers()
        if zoom:
            self.zoom_layer()

    def extent(self):
        envelope = self.map.getMapContext().getViewPort().getEnvelope()
        return [envelope.getMinimum(0), envelope.getMinimum(1),
                envelope.getMaximum(0), envelope.getMaximum(1)]

    def set_extent(self, extent, mark=True):
        x1, y1, x2, y2 = extent
        w, h = max(x2-x1, 0.00001), max(y2-y1, 0.00001)
        aspect = max(self.map.getWidth(), 1) / float(max(self.map.getHeight(), 1))
        if self.map.getWidth() > 1:
            if w/h < aspect:
                w = h*aspect
            else:
                h = w/aspect
        cx, cy = (x1+x2)/2.0, (y1+y2)/2.0
        envelope = geom.createEnvelope([cx-w/2, cy-h/2], [cx+w/2, cy+h/2])
        self.map.getMapContext().getViewPort().setEnvelope(envelope)
        self.map.getMapContext().invalidate()
        if mark:
            self.dirty = True

    def coordinate(self, x, y):
        point = self.map.getMapContext().getViewPort().toMapPoint(int(x), int(y))
        return point.getX(), point.getY()

    def zoom(self, factor):
        a, b, c, d = self.extent()
        cx, cy = (a+c)/2, (b+d)/2
        w, h = (c-a)*factor/2, (d-b)*factor/2
        self.set_extent([cx-w, cy-h, cx+w, cy+h])

    def zoom_layer(self):
        _, layer = self.selected()
        e = layer.getFullEnvelope()
        self.set_extent([e.getMinimum(0), e.getMinimum(1), e.getMaximum(0), e.getMaximum(1)])
        self.zoom(1.1)

    def set_mode(self, mode):
        if mode == 'measure':
            core.require_metric(self.crs)
        self.mode = mode
        self.measure_start = None
        self.mode_label = {'pan': 'Kéo để di chuyển', 'capture': 'Nhấp để lấy tọa độ',
                           'measure': 'Nhấp hai điểm để đo'}[mode]
        self.status.setText(self.mode_label)

    def toggle_layer(self):
        index, layer = self.selected()
        layer.setVisible(not layer.isVisible())
        self.records[index]['visible'] = layer.isVisible()
        self.refresh_layers(index)

    def rename_layer(self):
        index, layer = self.selected()
        name = self.ask('Tên lớp:', layer.getName())
        if name and name.strip():
            layer.setName(name.strip())
            self.records[index]['name'] = name.strip()
            self.refresh_layers(index)

    def remove_layer(self):
        index, layer = self.selected()
        self.view.getMapContext().getLayers().removeLayer(layer)
        del self.records[index]
        del self.layers[index]
        self.refresh_layers()

    def move_layer(self, delta):
        index, layer = self.selected()
        target = index + delta
        if target < 0 or target >= len(self.layers):
            return
        native = self.view.getMapContext().getLayers()
        native.move(layer, native, 2 if delta < 0 else 3, self.layers[target])
        self.layers.insert(target, self.layers.pop(index))
        self.records.insert(target, self.records.pop(index))
        self.refresh_layers(target)

    def attributes(self):
        _, layer = self.selected()
        if not hasattr(layer, 'features'):
            raise ValueError('Raster không có bảng thuộc tính vector.')
        expression = self.expression.getText().strip() or None
        def finished(result):
            headers, rows, count = result
            self.table_headers, self.table_data = list(headers), list(rows)
            self.table_model.setDataVector([[u'' if v is None else unicode(v) for v in row] for row in rows], headers)
            self.table_count.setText('Hiển thị %s / %s đối tượng · CSV xuất các hàng đang hiển thị' % (len(rows), count))
        self.job(lambda: engine.table_rows(layer, expression, core.TABLE_LIMIT), finished)

    def select(self):
        _, layer = self.selected()
        expression = self.expression.getText().strip()
        if not expression:
            layer.getSelection().deselectAll()
            self.map.getMapContext().invalidate()
            return
        def finished(count):
            self.map.getMapContext().invalidate()
            self.info('Đã chọn %s đối tượng.' % count)
        self.job(lambda: engine.select_expression(layer, expression), finished)

    def clear_filter(self):
        self.expression.setText('')
        self.attributes()

    def export_csv(self):
        if not self.table_headers:
            raise ValueError('Mở bảng thuộc tính trước khi xuất.')
        path = self.choose('Xuất bảng đang hiển thị', 'csv', True)
        if path:
            core.write_csv(path, self.table_headers, self.table_data)
            self.info('Đã xuất %s hàng.' % len(self.table_data))

    def stats(self):
        if not self.table_headers:
            raise ValueError('Mở bảng thuộc tính trước khi thống kê.')
        field = JOptionPane.showInputDialog(self.frame, 'Trường số (chỉ tính các hàng đã tải):',
            'Thống kê', JOptionPane.QUESTION_MESSAGE, None, self.table_headers, self.table_headers[0])
        if field is None:
            return
        index = self.table_headers.index(field)
        result = core.statistics(row[index] for row in self.table_data)
        self.info('Số giá trị: %(count)s\nNhỏ nhất: %(min)s\nLớn nhất: %(max)s\n'
                  'Tổng: %(sum)s\nTrung bình: %(mean)s' % result)

    def processing(self, operation):
        index, layer = self.selected()
        if self.records[index]['kind'] != 'shape':
            raise ValueError('Chọn lớp vector.')
        distance, mask, target = None, None, None
        if operation == 'buffer':
            core.require_metric(self.crs)
            value = self.ask('Khoảng cách vùng đệm (mét):', '100')
            if value is None:
                return
            distance = core.positive(value)
        if operation == 'clip':
            candidates = [(i, rec['name']) for i, rec in enumerate(self.records)
                          if i != index and rec['kind'] == 'shape']
            if not candidates:
                raise ValueError('Thêm lớp vùng dùng làm mặt nạ trước.')
            labels = ['%s · %s' % (i+1, name) for i, name in candidates]
            choice = JOptionPane.showInputDialog(self.frame, 'Lớp vùng làm mặt nạ:', 'Cắt theo vùng',
                JOptionPane.QUESTION_MESSAGE, None, labels, labels[0])
            if choice is None:
                return
            mask = self.layers[candidates[labels.index(choice)][0]]
        if operation == 'reproject':
            value = self.ask('EPSG đích:', 'EPSG:32648')
            if value is None:
                return
            target = core.crs_code(value)
        elif JOptionPane.showConfirmDialog(self.frame,
                'Xử lý toàn bộ lớp. Kết quả gồm ID và hình học; không sao chép thuộc tính. Tiếp tục?',
                'Phạm vi xử lý', JOptionPane.YES_NO_OPTION) != JOptionPane.YES_OPTION:
            return
        path = self.choose('Lưu kết quả mới', 'shp', True)
        if not path:
            return
        path = core.fresh_output(path)
        def finished(result):
            output, output_path, count = result
            if target and target != self.crs:
                self.info('Đã xuất %s đối tượng. Mở trong dự án mới có CRS %s.\n%s' % (count, target, output_path))
            else:
                self.view.addLayer(output)
                self.register(output, output_path, 'shape')
                self.info('Đã tạo %s đối tượng.' % count)
        self.job(lambda: engine.process(layer, operation, path, self.crs,
                  distance=distance, mask=mask, target_crs=target), finished)

    def save_project(self):
        path = self.choose('Lưu dự án VFMGIS', 'vfm', True)
        if not path:
            return False
        core.save_project(path, self.crs, self.records, self.extent())
        self.project_path, self.dirty = path, False
        self.status.setText('Đã lưu dự án: ' + path)
        return True

    def new_project(self):
        value = self.ask('Hệ tọa độ dự án mới:', 'EPSG:4326')
        if value:
            Workspace(core.crs_code(value))

    def open_project(self):
        path = self.choose('Mở dự án VFMGIS', 'vfm')
        if not path:
            return
        data = core.load_project(path)  # Validate all paths before creating a view.
        window = Workspace(data['crs'])
        try:
            for record in reversed(data['layers']):
                layer = engine.load_layer(window.view, record['path'], record['kind'], data['crs'])
                window.register(layer, record['path'], record['kind'], zoom=False)
                layer.setName(record['name'])
                layer.setVisible(record.get('visible', True))
                window.records[0] = dict(record)
            window.refresh_layers()
            window.set_extent(data['extent'])
            window.project_path, window.dirty = path, False
        except (Exception, Throwable):
            window.map.dispose()
            window.project.remove(window.view)
            window.frame.dispose()
            raise

    def export_image(self):
        path = self.choose('Xuất ảnh bản đồ', 'png', True)
        if not path:
            return
        image = BufferedImage(self.map.getWidth(), self.map.getHeight(), BufferedImage.TYPE_INT_RGB)
        graphics = image.createGraphics()
        try:
            self.map.paint(graphics)
        finally:
            graphics.dispose()
        if not ImageIO.write(image, 'png', File(path)):
            raise ValueError('Không có bộ ghi PNG.')
        self.info('Đã xuất ảnh bản đồ: ' + path)

    def demo(self):
        value = self.choose('Tạo Shapefile bài thực hành (UTM 48N)', 'shp', True)
        if not value:
            return
        path = core.fresh_output(value)
        from addons.VFMGIS.sample import create_sample
        window = Workspace('EPSG:32648')
        def done(layer):
            window.view.addLayer(layer)
            window.register(layer, path, 'shape')
            window.info('Dữ liệu giả lập để học, không phải ranh giới hành chính.\n'
                        'Thử: ID > 2 → Chọn trên bản đồ → Vùng đệm 100 m.')
        window.job(lambda: create_sample(path), done)

    def help(self):
        self.info('1. Tạo dự án và chọn đúng EPSG.\n'
                  '2. Thêm Shapefile đủ .shp/.shx/.dbf/.prj hoặc GeoTIFF.\n'
                  '3. Chọn lớp bên trái; cuộn chuột để zoom, kéo để di chuyển.\n'
                  '4. Bảng thuộc tính → nhập ID > 2 → Áp dụng hoặc Chọn trên bản đồ.\n'
                  '5. Phân tích → chọn công cụ → lưu tên Shapefile mới.\n'
                  '6. Lưu dự án .vfm; giữ nguyên các tệp dữ liệu đi kèm.\n\n'
                  'Bảng tải tối đa 2.000 hàng; xử lý tối đa 50.000 đối tượng.\n'
                  'Dữ liệu trong dự án phải cùng CRS. Không tự đoán VN-2000.\n'
                  'Giao diện VFMGIS bằng tiếng Việt; cửa sổ gvSIG gốc giữ ngôn ngữ gốc.')

    def close(self):
        if self.busy:
            self.info('Chờ tác vụ hiện tại hoàn tất rồi đóng.')
            return
        if self.dirty:
            answer = JOptionPane.showConfirmDialog(self.frame, 'Lưu dự án trước khi đóng?',
                'VFMGIS', JOptionPane.YES_NO_CANCEL_OPTION)
            if answer in (JOptionPane.CANCEL_OPTION, JOptionPane.CLOSED_OPTION):
                return
            if answer == JOptionPane.YES_OPTION and not self.save_project():
                return
        self.map.dispose()
        self.project.remove(self.view)
        self.frame.dispose()


def main(*args):
    # Standard file-dialog strings are set once for the Vietnamese workspace.
    translations = {'FileChooser.openButtonText': 'Mở', 'FileChooser.saveButtonText': 'Lưu',
        'FileChooser.cancelButtonText': 'Hủy', 'FileChooser.fileNameLabelText': 'Tên tệp:',
        'FileChooser.filesOfTypeLabelText': 'Loại tệp:', 'FileChooser.lookInLabelText': 'Tìm trong:',
        'FileChooser.upFolderToolTipText': 'Thư mục cha', 'FileChooser.newFolderToolTipText': 'Thư mục mới',
        'OptionPane.yesButtonText': 'Có', 'OptionPane.noButtonText': 'Không',
        'OptionPane.cancelButtonText': 'Hủy', 'OptionPane.okButtonText': 'Đồng ý'}
    for key, text in translations.items():
        UIManager.put(key, text)
    SwingUtilities.invokeLater(lambda: Workspace())
