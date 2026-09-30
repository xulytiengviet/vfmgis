# encoding: utf-8
# SPDX-License-Identifier: GPL-3.0-or-later
"""gvSIG DAL / geometry adapter. Must run in the gvSIG Jython interpreter."""
from __future__ import unicode_literals
import os
import gvsig
from gvsig import geom
from addons.VFMGIS.core import MAX_FEATURES, positive, require_metric, fresh_output
try:
    from org.locationtech.jts.io import WKTReader
    from org.locationtech.jts.geom import GeometryFactory
except ImportError:
    from com.vividsolutions.jts.io import WKTReader
    from com.vividsolutions.jts.geom import GeometryFactory


def dispose(value):
    if value is not None and hasattr(value, 'dispose'):
        value.dispose()


def read_rows(layer, expression=None, limit=MAX_FEATURES):
    if not hasattr(layer, 'features'):
        raise ValueError('Chọn một lớp vector trong danh sách lớp.')
    features = layer.features(expression) if expression else layer.features()
    iterator = None
    try:
        if features.getSize() > limit:
            raise ValueError('Vượt giới hạn %s đối tượng. Hãy lọc hoặc chia nhỏ dữ liệu.' % limit)
        result = []
        iterator = features.iterator()
        while iterator.hasNext():
            f = iterator.next()
            values = dict(f.getValues())
            shape = f.getDefaultGeometry()
            result.append((values, shape.cloneGeometry() if shape is not None else None))
        return result
    finally:
        dispose(iterator)
        dispose(features)


def table_rows(layer, expression=None, limit=2000):
    features = layer.features(expression) if expression else layer.features()
    iterator = None
    try:
        count = features.getSize()
        fields = [a.getName() for a in layer.getSchema() if not a.getName() == layer.getSchema().getDefaultGeometryAttributeName()]
        rows = []
        iterator = features.iterator()
        while iterator.hasNext():
            f = iterator.next()
            if len(rows) >= limit:
                break
            rows.append([f.get(name) for name in fields])
        return fields, rows, count
    finally:
        dispose(iterator)
        dispose(features)


def select_expression(layer, expression):
    features = layer.features(expression)  # gvSIG expression parser, never Python eval.
    iterator = None
    try:
        if features.getSize() > MAX_FEATURES:
            raise ValueError('Tập chọn vượt 50.000 đối tượng.')
        selection = layer.getSelection()
        selection.deselectAll()
        iterator = features.iterator()
        while iterator.hasNext():
            feature = iterator.next()
            selection.select(feature)
        return features.getSize()
    finally:
        dispose(iterator)
        dispose(features)


def load_layer(view, path, kind, crs):
    loader = gvsig.loadShapeFile if kind == 'shape' else gvsig.loadRasterFile
    return loader(path, CRS=crs, gvViewName=view.getName(),
                  gvLayerName=os.path.splitext(os.path.basename(path))[0])


def jts(shape):
    if shape is None:
        raise ValueError('Có đối tượng rỗng. Hãy sửa dữ liệu trước khi xử lý.')
    result = WKTReader().read(shape.convertToWKT())
    if result.isEmpty() or not result.isValid():
        raise ValueError('Hình học rỗng hoặc không hợp lệ. Hãy kiểm tra dữ liệu nguồn.')
    return result


def process(layer, operation, path, crs, distance=None, mask=None, target_crs=None):
    """Write a new dataset; never mutate the source. All geometry work is planar."""
    path = fresh_output(path)
    rows = read_rows(layer)
    if not rows:
        raise ValueError('Lớp không có đối tượng.')
    schema = gvsig.createFeatureType()
    schema.append('ID', b'INTEGER')
    schema.append('GEOMETRY', b'GEOMETRY')
    if operation in ('buffer', 'dissolve', 'clip'):
        geometry_type = geom.MULTIPOLYGON
    elif operation == 'centroid':
        geometry_type = geom.POINT
    elif operation == 'reproject':
        schema = gvsig.createFeatureType(layer.getSchema())
        geometry_type = None
    else:
        raise ValueError('Công cụ không được hỗ trợ.')
    if geometry_type is not None:
        schema.get('GEOMETRY').setGeometryType(geometry_type, geom.D2)
    reader = WKTReader()
    factory = GeometryFactory()
    mask_geom = None
    if operation == 'buffer':
        require_metric(crs)
        distance = positive(distance)
    if operation in ('dissolve', 'clip'):
        if any(jts(g).getDimension() != 2 for _, g in rows):
            raise ValueError('Gộp và cắt trong bản này chỉ nhận lớp vùng.')
    if operation == 'clip':
        mask_rows = read_rows(mask)
        polygons = [jts(g) for _, g in mask_rows]
        if not polygons or any(g.getDimension() != 2 for g in polygons):
            raise ValueError('Lớp mặt nạ phải chứa vùng hợp lệ.')
        mask_geom = factory.buildGeometry(polygons).union()
    output_rows = []
    if operation == 'dissolve':
        merged = factory.buildGeometry([jts(g) for _, g in rows]).union()
        rows = [({}, geom.createGeometryFromWKT(merged.toText()))]
    transform = None
    if operation == 'reproject':
        transform = gvsig.getCRS(crs).getCT(gvsig.getCRS(target_crs))
    for index, (values, shape) in enumerate(rows):
        if operation == 'reproject':
            shape.reProject(transform)
            values[layer.getSchema().getDefaultGeometryAttributeName()] = shape
            output_rows.append(values)
            continue
        geometry = jts(shape)
        if operation == 'buffer':
            geometry = geometry.buffer(distance)
        elif operation == 'centroid':
            geometry = geometry.getCentroid()
        elif operation == 'clip':
            geometry = geometry.intersection(mask_geom)
        if geometry.isEmpty():
            continue
        if geometry_type == geom.MULTIPOLYGON:
            # Touching polygons can intersect in lines/points: retain polygonal pieces only.
            parts = []
            def collect(g):
                if g.getGeometryType() == 'Polygon':
                    parts.append(g)
                elif g.getGeometryType() in ('MultiPolygon', 'GeometryCollection'):
                    for i in range(g.getNumGeometries()):
                        collect(g.getGeometryN(i))
            collect(geometry)
            if not parts:
                continue
            geometry = factory.createMultiPolygon(parts)
        output_rows.append({'ID': index + 1, b'GEOMETRY': geom.createGeometryFromWKT(geometry.toText())})
    if not output_rows:
        raise ValueError('Không có kết quả giao nhau; chưa tạo tệp.')
    output = gvsig.createShape(schema, filename=path, CRS=target_crs or crs)
    try:
        output.edit()
        for values in output_rows:
            output.append(values)
        output.commit()
    except Exception:
        # Do not silently present a partially written file as a successful result.
        raise RuntimeError('Không ghi xong kết quả. Dữ liệu nguồn vẫn nguyên vẹn; '
                           'kiểm tra và xóa bộ tệp đầu ra chưa hoàn tất: ' + path)
    return output, path, len(output_rows)
