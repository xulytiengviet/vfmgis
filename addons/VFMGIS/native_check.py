# encoding: utf-8
# SPDX-License-Identifier: GPL-3.0-or-later
"""Exercise the actual native gvSIG desktop, not the old Swing workspace."""
from __future__ import unicode_literals
import io
import json
import os
from threading import Thread
from java.lang import System
from addons.VFMGIS.runtime_check import error_detail


def run(report):
    def fail():
        detail = error_detail()
        try:
            from java.awt import Robot, Toolkit, Rectangle
            from javax.imageio import ImageIO
            from java.io import File
            size = Toolkit.getDefaultToolkit().getScreenSize()
            ImageIO.write(Robot().createScreenCapture(Rectangle(size)), 'png',
                          File(os.path.join(os.path.dirname(report), 'dist', 'native-failure.png')))
        except: pass
        with io.open(report, 'w', encoding='utf-8') as f: f.write(detail)
        System.exit(1)

    def worker():
        try:
            from addons.VFMGIS.smoke import run as smoke
            root = smoke()
            from javax.swing import SwingUtilities, Timer, JFileChooser, UIManager
            from org.gvsig.andami import PluginServices
            from org.gvsig.i18n import Messages
            from addons.VFMGIS import native, engine
            import gvsig
            box = {}
            def open_native():
                try:
                    native.start()  # EXACT same entry point as an ordinary launch.
                    frame = PluginServices.getMainFrame()
                    frame.setSize(1280, 850)
                    view = gvsig.currentProject().createView('Bài thực hành mẫu', 'EPSG:32648')
                    layer = engine.load_layer(view, os.path.join(root, 'sample.shp'), 'shape', 'EPSG:32648')
                    view.centerView(layer.getFullEnvelope())
                    view.showWindow(maximize=True)
                    assert view.getLayers().getLayersCount() == 1
                    assert frame.isVisible()
                    box['frame'] = frame
                except:
                    box['error'] = error_detail()
            SwingUtilities.invokeAndWait(open_native)
            if 'error' in box: raise RuntimeError(box['error'])
            def finish(event):
                event.getSource().stop()
                try:
                    from java.awt.image import BufferedImage
                    from java.awt import Robot
                    from javax.imageio import ImageIO
                    from java.io import File
                    from java.util import Locale
                    frame = box['frame']
                    menus = []
                    bar = frame.getJMenuBar()
                    def walk(menu):
                        items = []
                        for i in range(menu.getItemCount()):
                            item = menu.getItem(i)
                            if item is None: continue
                            record = {'label': unicode(item.getText())}
                            if hasattr(item, 'getItemCount'): record['items'] = walk(item)
                            items.append(record)
                        return items
                    for i in range(bar.getMenuCount()):
                        menu = bar.getMenu(i)
                        if menu is not None: menus.append({'label': unicode(menu.getText()), 'items': walk(menu)})
                    with io.open(os.path.join(os.path.dirname(report), 'dist', 'native-menus.json'), 'w', encoding='utf-8') as f:
                        f.write(unicode(json.dumps(menus, ensure_ascii=False, indent=2)))
                    labels = [item['label'] for item in menus]
                    def flatten(items):
                        for item in items:
                            yield item['label']
                            for nested in flatten(item.get('items', [])): yield nested
                    all_labels = list(flatten(menus))
                    for leftover in ('_ Identify layer', 'Coordinate capture', 'Evaluate expression', 'Manage database workspace'):
                        assert leftover not in all_labels, leftover
                    for bad_term in ('Lời tiên tri', 'Ngói', 'Thác nước', 'Máy tính trường', 'Bật chụp nhanh'):
                        assert bad_term not in all_labels, bad_term
                    assert 'Tệp' in labels, repr(labels)
                    assert 'Trợ giúp' in labels, repr(labels)
                    assert 'Công cụ' in labels, repr(labels)
                    assert not any(label in ('File', 'View', 'Layer', 'Show', 'Map', 'Tools', 'Window', 'Help') for label in labels), repr(labels)
                    assert Locale.getDefault().getLanguage() == 'vi'
                    from java.util import ResourceBundle
                    from java.lang import ClassLoader
                    bundle = ResourceBundle.getBundle('org.gvsig.geoprocess.algorithm.buffer.buffer',
                        Locale('vi'), ClassLoader.getSystemClassLoader())
                    assert bundle.getString('Buffer') == 'Vùng đệm'
                    assert bundle.getString('Distance') == 'Khoảng cách'
                    assert UIManager.getString('FileChooser.cancelButtonText') == 'Hủy'
                    assert unicode(frame.getTitle()).startswith('VFMGIS')
                    image = BufferedImage(frame.getWidth(), frame.getHeight(), BufferedImage.TYPE_INT_RGB)
                    graphics = image.createGraphics()
                    graphics.setClip(0, 0, image.getWidth(), image.getHeight())
                    frame.paint(graphics)
                    graphics.dispose()
                    from java.awt import Toolkit, Rectangle
                    screenshot = Robot().createScreenCapture(Rectangle(Toolkit.getDefaultToolkit().getScreenSize()))
                    ImageIO.write(screenshot, 'png', File(os.path.join(os.path.dirname(report), 'dist', 'windows-native.png')))
                    with io.open(report, 'w', encoding='utf-8') as f:
                        f.write('PASS: original gvSIG desktop; native Vietnamese menus; native map view; real Shapefile rendering; Swing Vietnamese defaults; original DAL filter, selection, buffer, dissolve, centroid, reproject and clip.\n')
                        f.write('Menus: ' + ', '.join(labels) + '\n')
                        f.write('This test does not certify every dialog or machine-draft translation.\n')
                    System.exit(0)
                except: fail()
            timer = Timer(8000, finish)
            timer.setRepeats(False)
            timer.start()
        except: fail()
    thread = Thread(target=worker)
    thread.setDaemon(True)
    thread.start()
