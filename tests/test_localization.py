"""Regression tests for Java bundle syntax and translation safety."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / 'localization' / 'properties.py'
spec = importlib.util.spec_from_file_location('java_properties', path)
props = importlib.util.module_from_spec(spec)
spec.loader.exec_module(props)

class PropertiesTests(unittest.TestCase):
    def test_upstream_escaped_keys_and_continuations(self):
        original = b'# comment\nFile\\ name=First\\\n  second\npath=C\\:\\\\maps\\\\test.shp\nmsg: T\\u1ec7p {0}\\n%s\n'
        self.assertEqual(props.loads(original), {'File name': 'Firstsecond', 'path': 'C:\\maps\\test.shp', 'msg': 'Tệp {0}\n%s'})

    def test_unicode_is_written_for_java8_properties(self):
        self.assertIn(b'\\u1ec7', props.dumps({'file': 'Tệp'}))
        self.assertEqual(props.loads(b'file=T\\u1ec7p\n'), {'file': 'Tệp'})

    def test_literal_backslash_and_key_delimiters(self):
        self.assertEqual(props.loads(b'key\\=x\\:y=value\\\\u1234\n'), {'key=x:y': 'value\\u1234'})

if __name__ == '__main__': unittest.main()
