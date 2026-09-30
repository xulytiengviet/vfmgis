import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('core', Path(__file__).resolve().parents[1] / 'addons/VFMGIS/core.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


class CoreTests(unittest.TestCase):
    def test_distance_rejects_nonfinite_and_nonpositive(self):
        for value in ('nan', 'inf', '-inf', 0, -3, 'abc'):
            with self.assertRaises((ValueError, TypeError)):
                core.positive(value)
        self.assertEqual(core.positive('100.5'), 100.5)

    def test_metric_guard(self):
        for code in ('EPSG:32648', 'EPSG:32748', 'EPSG:3405'):
            core.require_metric(code)
        for code in ('EPSG:4326', 'EPSG:3857', 'EPSG:32600', 'EPSG:99999'):
            with self.assertRaises(ValueError):
                core.require_metric(code)

    def test_crs_validation(self):
        self.assertEqual(core.crs_code(' epsg:4326 '), 'EPSG:4326')
        for code in ('4326', 'EPSG:0', 'EPSG:4326; print(1)'):
            with self.assertRaises(ValueError):
                core.crs_code(code)

    def test_statistics_ignores_null_text_nonfinite(self):
        s = core.statistics([None, '', 'abc', 'nan', 'inf', 1, 2, 3])
        self.assertEqual(s, dict(count=3, min=1, max=3, sum=6, mean=2))
        with self.assertRaises(ValueError):
            core.statistics([None, 'abc'])

    def test_csv_unicode_quoting_and_formula_protection(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'table.csv'
            core.write_csv(str(p), ['Tên', 'Giá trị'], [['Vĩnh Long, "GIS"', '=1+1'], ['A', None]])
            text = p.read_text(encoding='utf-8-sig')
            self.assertIn('"Vĩnh Long, ""GIS"""', text)
            self.assertIn('"\'=1+1"', text)

    def test_sidecars_and_output_collision_case_insensitive(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'map.shp'
            p.touch()
            with self.assertRaises(ValueError):
                core.validate_shape(str(p))
            for extension in ('.SHX', '.DBF', '.PRJ'):
                p.with_suffix(extension).touch()
            self.assertEqual(core.validate_shape(str(p)), str(p))
            with self.assertRaises(ValueError):
                core.fresh_output(str(p))
            p.with_name('other.DBF').touch()
            with self.assertRaises(ValueError):
                core.fresh_output(str(p.with_name('other.shp')))

    def test_project_roundtrip_relative_paths_and_missing_data(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = root / 'ảnh.tif'
            data.touch()
            p = root / 'project.vfm'
            layers = [dict(path=str(data), kind='raster', name='Vĩnh Long', visible=False)]
            core.save_project(str(p), 'EPSG:4326', layers, [105, 9, 107, 11])
            raw = json.loads(p.read_text())
            self.assertEqual(raw['layers'][0]['path'], 'ảnh.tif')
            restored = core.load_project(str(p))
            self.assertEqual(restored['layers'], layers)
            core.save_project(str(p), 'EPSG:4326', layers, [104, 8, 108, 12])
            self.assertEqual(core.load_project(str(p))['extent'], [104, 8, 108, 12])
            data.unlink()
            with self.assertRaises(ValueError):
                core.load_project(str(p))

    def test_project_rejects_version_and_invalid_extent(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'bad.vfm'
            base = dict(format='VFMGIS', version=2, crs='EPSG:4326', layers=[], extent=[0, 0, 1, 1])
            p.write_text(json.dumps(base))
            with self.assertRaises(ValueError):
                core.load_project(str(p))
            base.update(version=1, extent=[0, 0, 0, 1])
            p.write_text(json.dumps(base))
            with self.assertRaises(ValueError):
                core.load_project(str(p))


if __name__ == '__main__':
    unittest.main()
