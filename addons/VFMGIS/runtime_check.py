# encoding: utf-8
# SPDX-License-Identifier: GPL-3.0-or-later
"""Executed by the Windows CI runner inside an actual gvSIG session."""
from __future__ import unicode_literals
import io
import os
import traceback
from java.lang import System


def _run(report):
    try:
        from addons.VFMGIS.smoke import run as smoke
        root = smoke()
        from javax.swing import SwingUtilities
        box = {}
        def open_workspace():
            try:
                from addons.VFMGIS.ui import Workspace
                from addons.VFMGIS import engine, core
                window = Workspace('EPSG:32648')
                path = os.path.join(root, 'sample.shp')
                layer = engine.load_layer(window.view, path, 'shape', 'EPSG:32648')
                window.register(layer, path, 'shape')
                window.zoom(0.8)
                window.toggle_layer()
                window.toggle_layer()
                _, x, y, _ = window.extent()
                assert window.frame.isVisible()
                assert len(window.layers) == 1
                project = os.path.join(root, 'test.vfm')
                core.save_project(project, window.crs, window.records, window.extent())
                assert len(core.load_project(project)['layers']) == 1
                box['window'] = window
            except BaseException:
                box['error'] = traceback.format_exc()
        SwingUtilities.invokeAndWait(open_workspace)
        if 'error' in box:
            raise RuntimeError(box['error'])
        window = box['window']
        from javax.swing import Timer
        def finish(event):
            event.getSource().stop()
            try:
                from java.awt.image import BufferedImage
                from javax.imageio import ImageIO
                from java.io import File
                image = BufferedImage(window.frame.getWidth(), window.frame.getHeight(), BufferedImage.TYPE_INT_RGB)
                graphics = image.createGraphics()
                window.frame.paint(graphics)
                graphics.dispose()
                ImageIO.write(image, 'png', File(os.path.join(os.path.dirname(report), 'dist', 'windows-runtime.png')))
                with io.open(report, 'w', encoding='utf-8') as output:
                    output.write('PASS: gvSIG runtime; sample, filter, selection, buffer, dissolve, centroid, reproject, clip, Swing workspace, MapControl, layer toggle, project roundtrip.\n' + root)
                System.exit(0)
            except Exception:
                with io.open(report, 'w', encoding='utf-8') as output:
                    output.write(unicode(traceback.format_exc()))
                System.exit(1)
        timer = Timer(7000, finish)
        timer.setRepeats(False)
        timer.start()
    except Exception:
        with io.open(report, 'w', encoding='utf-8') as output:
            output.write(unicode(traceback.format_exc()))
        System.exit(1)


def run(report):
    # DAL operations must use a worker, as they do in the application.
    from threading import Thread
    def watchdog():
        import time
        time.sleep(75)
        from java.lang import Thread as JavaThread
        with io.open(report, 'w', encoding='utf-8') as output:
            output.write('FAIL: integration stalled; thread stacks\n')
            for entry in JavaThread.getAllStackTraces().entrySet():
                thread, stack = entry.getKey(), entry.getValue()
                output.write(unicode(thread.getName()) + '\n')
                for frame in stack:
                    output.write('  ' + unicode(frame) + '\n')
        System.exit(1)
    monitor = Thread(target=watchdog)
    monitor.setDaemon(True)
    monitor.start()
    worker = Thread(target=_run, args=(report,))
    worker.setDaemon(True)
    worker.start()
