"""Build a deterministic source/add-on distribution, not a gvSIG binary."""
from pathlib import Path
import hashlib
import zipfile

root = Path(__file__).resolve().parents[1]
out = root / 'dist'
out.mkdir(exist_ok=True)
archive = out / 'VFMGIS-0.1.0-gvsig-addon.zip'
files = [p for p in root.rglob('*') if p.is_file() and not any(
    part in ('.git', '__pycache__', 'dist') or part.endswith('.pyc')
    for part in p.relative_to(root).parts)]
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
    for path in sorted(files):
        info = zipfile.ZipInfo('VFMGIS-0.1.0/' + path.relative_to(root).as_posix(), (2026, 9, 30, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        bundle.writestr(info, path.read_bytes())
print(archive)
print('SHA256:', hashlib.sha256(archive.read_bytes()).hexdigest())
