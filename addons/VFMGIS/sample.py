# encoding: utf-8
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import unicode_literals
import gvsig
from gvsig import geom


def create_sample(path):
    schema = gvsig.createFeatureType()
    schema.append('ID', 'INTEGER')
    schema.append('TEN', 'STRING', 80)
    schema.append('DANSO', 'INTEGER')
    schema.append('GEOMETRY', 'GEOMETRY')
    schema.get('GEOMETRY').setGeometryType(geom.POLYGON, geom.D2)
    layer = gvsig.createShape(schema, filename=path, CRS='EPSG:32648')
    layer.edit()
    for i, name in enumerate(['Khu A', 'Khu B', 'Khu C', 'Khu D', 'Khu E', 'Khu F']):
        x, y = 600000 + (i % 3)*700, 1130000 + (i // 3)*700
        polygon = geom.createPolygon(geom.D2, [[x,y], [x+600,y], [x+600,y+600],
                                                   [x,y+600], [x,y]])
        layer.append(ID=i+1, TEN=name, DANSO=500+i*175, GEOMETRY=polygon)
    layer.commit()
    layer.setName('Khu thực hành · dữ liệu giả lập')
    return layer
