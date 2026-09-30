"""Inventory original gvSIG resources, including resources nested in JARs."""
import io
import json
import sys
import zipfile
from pathlib import Path

source, destination = map(Path, sys.argv[1:])
destination.mkdir(parents=True, exist_ok=True)
entries = []
with zipfile.ZipFile(source) as runtime, zipfile.ZipFile(destination / 'resources.zip', 'w', zipfile.ZIP_DEFLATED) as output:
    for item in runtime.infolist():
        name = item.filename
        if item.is_dir():
            continue
        if name.endswith(('.properties', '.xml', '.ini', '.conf', '.sh', '.bat')):
            output.writestr(name, runtime.read(item))
            entries.append({'path': name, 'size': item.file_size})
        elif name.endswith('.jar'):
            with zipfile.ZipFile(io.BytesIO(runtime.read(item))) as jar:
                for entry in jar.infolist():
                    if entry.filename.endswith('.properties'):
                        path = name + '!/' + entry.filename
                        output.writestr(path, jar.read(entry))
                        entries.append({'path': path, 'size': entry.file_size})
                    elif entry.filename.endswith('.class') and any(x in entry.filename.lower() for x in ['i18n', 'andami/launcher', 'pluginservices', 'preferenceshandler', 'mainwindow']):
                        output.writestr(name + '!/' + entry.filename, jar.read(entry))
    (destination / 'files.txt').write_text('\n'.join(runtime.namelist()), encoding='utf-8')
(destination / 'inventory.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')
print('Inventoried', len(entries), 'resources')
