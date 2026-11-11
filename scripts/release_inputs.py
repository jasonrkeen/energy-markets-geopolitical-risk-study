"""Fail closed when a frozen release narrative no longer matches validated outputs."""
import hashlib
import json
from pathlib import Path


def normalized_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def validate_release_inputs(root: Path) -> dict:
    checks = json.loads((root/'docs/CLEAN_VALIDATION.json').read_text())
    editorial = json.loads((root/'docs/RELEASE_TEXT_INPUTS.json').read_text())
    frozen = editorial['csv_sha256']
    for name, expected in editorial['other_sha256'].items():
        if normalized_hash(root/name) != expected:
            raise ValueError(f'Release narrative input is stale: {name}')
    actual = {p.name: normalized_hash(p) for p in (root/'outputs/v2').glob('*.csv')}
    if not frozen or actual != frozen or actual != checks.get('csv_sha256'):
        raise ValueError('Release narrative or validation is stale; review the text against current numerical outputs')
    if not checks.get('csv_hashes_equal') or checks.get('tests_passed', 0) <= 0:
        raise ValueError('Successful validation receipt required')
    for name, expected in checks['source_code_hashes'].items():
        if normalized_hash(root/name) != expected:
            raise ValueError(f'Validated source changed: {name}')
    return checks
