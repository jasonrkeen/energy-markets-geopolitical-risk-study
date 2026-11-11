"""Verify exact bytes of an extracted release bundle using only the standard library."""
import hashlib
import json
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'BUNDLE_MANIFEST.json').read_text(encoding='utf-8'))
    for name, expected in manifest['files'].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f'Missing or invalid bundle path: {name}')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Checksum mismatch: {name}')
    print(f"Verified {len(manifest['files'])} files against the supplied integrity manifest.")
    print('This checks bundle integrity, not independent source authenticity.')

if __name__ == '__main__':
    main()
