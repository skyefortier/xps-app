"""Reproducible source identity for fit exports, including uncommitted repairs."""
import hashlib
from importlib.metadata import version
from pathlib import Path


def software_metadata():
    root = Path(__file__).resolve().parent
    files = sorted(set(root.glob('*.py')) | set(root.glob('autofit/**/*.py'))
                   | set(root.glob('templates/*.html')) | set(root.glob('static/js/*.js'))
                   | set(root.glob('data/xps/**/*.json')))
    digest = hashlib.sha256()
    for path in files:
        data = path.read_bytes()
        digest.update(path.relative_to(root).as_posix().encode() + b'\0')
        digest.update(str(len(data)).encode() + b'\0' + data)
    return {
        'numerical_version': '2026.09-audit.1',
        'source_sha256': digest.hexdigest(),
        'dependencies': {name: version(name) for name in ('numpy', 'scipy', 'lmfit')},
    }
