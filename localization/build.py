"""Build a Vietnamese resource overlay; never modify gvSIG's Java classes."""
import io
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from catalog import collect
from properties import dumps, loads
from seed_translation import placeholders

BASE = Path(__file__).parent

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

def invariant(key, source):
    # Resource-valued properties and technical identifiers are not prose.
    return bool(re.fullmatch(r'(?:https?://\S+|[\w./-]+\.(?:txt|html?|xml|png|gif|jpg|pdf|properties)|[\d\s.,+*/=()%-]+)', source))

def build(archive, output):
    catalog = collect(archive)
    memory = {}
    for path in sorted((BASE / 'vi').glob('*.json')):
        memory.update(read_json(path))
    reviewed = read_json(BASE / 'overrides.json')
    keys = read_json(BASE / 'key-overrides.json')
    counter = Counter()
    missing, mismatches, unchanged = [], [], []
    translated_bundles = {}
    for path, source in catalog.items():
        translated = {}
        for key, value in source.items():
            if invariant(key, value):
                target, status = value, 'technical_value'
            elif key in keys:
                target, status = keys[key], 'reviewed'
            elif value in reviewed:
                target, status = reviewed[value], 'reviewed'
            elif value in memory:
                target, status = memory[value], 'machine_draft'
            else:
                missing.append({'bundle': path, 'key': key, 'source': value})
                continue
            if placeholders(value) != placeholders(target):
                mismatches.append({'bundle': path, 'key': key, 'source': value, 'target': target})
                continue
            if value == target and status == 'machine_draft':
                unchanged.append({'bundle': path, 'key': key, 'source': value})
            translated[key] = target
            counter[status] += 1
        translated_bundles[path] = translated
    report = {
        'core': 'gvSIG 2.6.0 build 3335',
        'scope': '131 native text[_locale].properties bundles in the pinned official runtime; not a claim of 100% product localization',
        'bundles': len(catalog), 'source_entries': sum(map(len, catalog.values())),
        'translated_entries': sum(map(len, translated_bundles.values())),
        'status_counts': dict(counter), 'missing': missing, 'placeholder_errors': mismatches,
        'unchanged_draft_entries': unchanged,
        'product_fully_localized': False,
        'remaining_review': ['Machine-draft terminology and grammar', 'Hardcoded strings in Java/Jython', 'Third-party resource families other than text.properties', 'All dialogs and error paths on Windows 10/11']
    }
    report['resource_coverage_percent'] = round(100 * report['translated_entries'] / report['source_entries'], 4)
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    (output / 'localization-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if missing or mismatches:
        raise SystemExit('Missing translations or unsafe placeholders; see localization-report.json')
    # Merge the global catalog last, to preserve gvSIG's authoritative key meanings.
    merged = {}
    for path, values in sorted(translated_bundles.items(), key=lambda item: 'translations.all/' in item[0]):
        merged.update(values)
    # Some upstream config.xml menus reference keys absent from every bundle.
    merged.update(read_json(BASE / 'extra-keys.json'))
    loose, jar_entries = {}, {}
    for path, values in translated_bundles.items():
        relative = path.split('/', 1)[1]
        if '!/' in relative:
            resource = relative.split('!/', 1)[1] + 'text_vi.properties'
            # Duplicate package resource names share the global gvSIG key vocabulary.
            jar_entries.setdefault(resource, {}).update(values)
        else:
            loose[relative + 'text_vi.properties'] = dumps(values)
    loose['i18n/translations.all/text_vi.properties'] = dumps(merged)
    # Register the locale without dropping any other installed language.
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if name.endswith('/locale.config') and '/i18n/' in name:
                data = z.read(name)
                loose[name.split('/', 1)[1]] = data.rstrip() + b'\nlocale=vi\n'
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as jar:
        jar.writestr('META-INF/MANIFEST.MF', b'Manifest-Version: 1.0\n\n')
        for name, values in sorted(jar_entries.items()): jar.writestr(name, dumps(values))
    loose['lib/vfmgis-language-vi.jar'] = buffer.getvalue()
    with zipfile.ZipFile(output / 'locale.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(loose.items()): z.writestr(name, data)
    # Roundtrip all generated translations through Java-properties semantics.
    for values in translated_bundles.values():
        assert loads(dumps(values)) == values
    print(json.dumps({k: report[k] for k in ['bundles', 'source_entries', 'translated_entries', 'resource_coverage_percent', 'status_counts']}, ensure_ascii=False))

if __name__ == '__main__': build(sys.argv[1], sys.argv[2])
