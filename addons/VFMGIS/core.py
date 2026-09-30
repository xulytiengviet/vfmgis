# encoding: utf-8
# SPDX-License-Identifier: GPL-3.0-or-later
"""Portable validation and project model (Python 2.7/Jython and Python 3)."""
from __future__ import unicode_literals
import io
import json
import math
import os
import re
import tempfile

MAX_FEATURES = 50000
TABLE_LIMIT = 2000
PROJECT_VERSION = 1


def finite(value):
    value = float(value)
    if math.isnan(value) or math.isinf(value):
        raise ValueError('Giá trị phải là số hữu hạn.')
    return value


def positive(value):
    value = finite(value)
    if value <= 0:
        raise ValueError('Giá trị phải lớn hơn 0.')
    return value


def crs_code(value):
    value = value.strip().upper()
    if not re.match(r'^EPSG:[1-9][0-9]{2,6}$', value):
        raise ValueError('Nhập hệ tọa độ dạng EPSG:4326 hoặc EPSG:32648.')
    return value


def require_metric(crs):
    # Only explicitly verified metre-based CRSs. Never infer units from coordinates.
    code = int(crs_code(crs).split(':')[1])
    if not (32601 <= code <= 32660 or 32701 <= code <= 32760 or code in (3405, 3406)):
        raise ValueError('Công cụ mét yêu cầu UTM WGS84 hoặc VN-2000 EPSG:3405/3406. '
                         'Hãy xuất chuyển hệ tọa độ rồi mở trong dự án mới.')


def validate_shape(path):
    if not path.lower().endswith('.shp'):
        raise ValueError('Chọn tệp .shp.')
    folder = os.path.dirname(os.path.abspath(path))
    names = set(n.lower() for n in os.listdir(folder))
    stem = os.path.splitext(os.path.basename(path))[0].lower()
    missing = [stem + ext for ext in ('.shp', '.shx', '.dbf', '.prj') if stem + ext not in names]
    if missing:
        raise ValueError('Thiếu tệp đi kèm: ' + ', '.join(missing))
    return os.path.abspath(path)


def fresh_output(path):
    path = os.path.abspath(path)
    if not path.lower().endswith('.shp'):
        path += '.shp'
    stem = os.path.splitext(os.path.basename(path))[0].lower()
    names = set(n.lower() for n in os.listdir(os.path.dirname(path)))
    if any(stem + ext in names for ext in ('.shp', '.shx', '.dbf', '.prj', '.cpg')):
        raise ValueError('Tên đầu ra đã tồn tại. Chọn tên mới để bảo toàn dữ liệu.')
    return path


def statistics(values):
    numbers = []
    for value in values:
        if value is None or value == '':
            continue
        try:
            numbers.append(finite(value))
        except (ValueError, TypeError):
            continue
    if not numbers:
        raise ValueError('Trường không có giá trị số hợp lệ.')
    return {'count': len(numbers), 'min': min(numbers), 'max': max(numbers),
            'sum': sum(numbers), 'mean': sum(numbers) / len(numbers)}


def csv_cell(value):
    try:
        text = unicode(value) if value is not None else ''
    except NameError:
        text = str(value) if value is not None else ''
    # Prevent formula evaluation when opening exported tables in Excel.
    if text.lstrip().startswith(('=', '+', '-', '@')):
        text = "'" + text
    return '"' + text.replace('"', '""') + '"'


def write_csv(path, headers, rows):
    with io.open(path, 'w', encoding='utf-8-sig', newline='') as stream:
        for row in [headers] + list(rows):
            stream.write(','.join(csv_cell(v) for v in row) + '\r\n')


def save_project(path, crs, layers, extent):
    folder = os.path.dirname(os.path.abspath(path))
    payload = {'format': 'VFMGIS', 'version': PROJECT_VERSION, 'crs': crs_code(crs),
               'extent': [finite(x) for x in extent], 'layers': []}
    for layer in layers:
        item = dict(layer)
        try:
            item['path'] = os.path.relpath(item['path'], folder)
        except ValueError:  # Different drives on Windows.
            pass
        payload['layers'].append(item)
    fd, tmp = tempfile.mkstemp(prefix='.vfm-', dir=folder)
    os.close(fd)
    try:
        with io.open(tmp, 'w', encoding='utf-8') as stream:
            stream.write(json.dumps(payload, ensure_ascii=False, indent=2))
        if hasattr(os, 'replace'):
            os.replace(tmp, path)
        else:  # Jython/Windows: use Java atomic replacement where supported.
            from java.nio.file import Files, Paths, StandardCopyOption
            Files.move(Paths.get(tmp), Paths.get(os.path.abspath(path)),
                       StandardCopyOption.REPLACE_EXISTING)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def load_project(path):
    with io.open(path, encoding='utf-8') as stream:
        value = json.load(stream)
    if value.get('format') != 'VFMGIS' or value.get('version') != PROJECT_VERSION:
        raise ValueError('Không phải dự án VFMGIS phiên bản 1.')
    value['crs'] = crs_code(value['crs'])
    extent = [finite(x) for x in value['extent']]
    if len(extent) != 4 or extent[0] >= extent[2] or extent[1] >= extent[3]:
        raise ValueError('Phạm vi bản đồ không hợp lệ.')
    value['extent'] = extent
    if not isinstance(value['layers'], list) or len(value['layers']) > 100:
        raise ValueError('Dự án hỗ trợ tối đa 100 lớp.')
    for item in value['layers']:
        if item.get('kind') not in ('shape', 'raster'):
            raise ValueError('Loại lớp không được hỗ trợ.')
        item['path'] = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(path)), item['path']))
        if not os.path.isfile(item['path']):
            raise ValueError('Không tìm thấy dữ liệu: ' + item['path'])
        if item['kind'] == 'shape':
            validate_shape(item['path'])
    return value
