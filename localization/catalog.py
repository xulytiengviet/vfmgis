"""Collect native gvSIG text bundles from the pinned runtime inventory."""
import json
import re
import zipfile
from pathlib import Path
from properties import loads


def collect(archive):
    bundles = {}
    with zipfile.ZipFile(archive) as z:
        for name in sorted(z.namelist()):
            # gvSIG's native language contract uses text[_locale].properties.
            m = re.search(r'(^|/)text(?:_(en|en_US|en_us|es))?\.properties$', name)
            if not m:
                continue
            root = name[:m.start()] + m[1]
            locale = m[2] or 'default'
            bundles.setdefault(root, {})[locale] = loads(z.read(name))
    result = {}
    for root, versions in bundles.items():
        values = {}
        for language in ['default', 'es', 'en_us', 'en_US', 'en']:
            values.update({k: v for k, v in versions.get(language, {}).items() if v.strip()})
        result[root] = values
    return result

if __name__ == '__main__':
    import sys
    data = collect(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(len(data), 'bundles;', sum(map(len, data.values())), 'entries;', len(set(v for b in data.values() for v in b.values())), 'unique source strings')
