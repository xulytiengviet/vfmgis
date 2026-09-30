# encoding: utf-8
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run main() in gvSIG Scripting Composer. Uses a NEW temporary directory."""
from __future__ import unicode_literals
import os
import tempfile
from addons.VFMGIS import engine
from addons.VFMGIS.sample import create_sample


def stage(message):
    from java.lang import System
    report = System.getenv('VFMGIS_TEST_REPORT')
    if report:
        import io
        with io.open(report + '.progress', 'a', encoding='utf-8') as output:
            output.write(unicode(message) + '\n')


def run():
    root = tempfile.mkdtemp(prefix='vfmgis-smoke-')
    stage('create sample')
    layer = create_sample(os.path.join(root, 'sample.shp'))
    stage('read sample')
    rows = engine.read_rows(layer)
    assert len(rows) == 6
    assert abs(sum(engine.jts(g).getArea() for _, g in rows) - 2160000) < 0.01
    stage('attribute filter')
    headers, values, count = engine.table_rows(layer, 'ID > 2')
    assert count == 4 and len(values) == 4
    assert engine.select_expression(layer, 'ID > 4') == 2
    for operation in ('buffer', 'dissolve', 'centroid', 'reproject'):
        stage(operation)
        output, path, count = engine.process(layer, operation, os.path.join(root, operation+'.shp'),
            'EPSG:32648', distance=100, target_crs='EPSG:4326' if operation == 'reproject' else None)
        assert os.path.exists(path)
        expected = 1 if operation == 'dissolve' else 6
        assert count == expected, (operation, count)
        assert len(engine.read_rows(output)) == expected
    stage('clip')
    output, path, count = engine.process(layer, 'clip', os.path.join(root, 'clip.shp'),
                                         'EPSG:32648', mask=layer)
    assert count == 6
    assert abs(sum(engine.jts(g).getArea() for _, g in engine.read_rows(output)) - 2160000) < 0.01
    return root


def main(*args):
    from gvsig.commonsdialog import msgbox
    msgbox('Kiểm tra tích hợp thành công. Dữ liệu kiểm tra: ' + run())
