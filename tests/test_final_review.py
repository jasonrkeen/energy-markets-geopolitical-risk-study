import hashlib
import json
import numpy as np
import pandas as pd
import pytest
from scipy.stats import f
from src.v2_data import require_complete_sample
from src.stability import period_labels, review
from scripts.release_inputs import validate_release_inputs


def test_common_date_comparison_rejects_missing_and_nonfinite_months():
    index = pd.date_range('2000-10-31', periods=5, freq='ME')
    frame = pd.DataFrame({'xle': np.arange(5.)}, index=index)
    assert require_complete_sample(frame, index, ['xle']).equals(frame)
    for bad in [frame.iloc[:-1], frame.assign(xle=[1, 2, np.inf, 4, 5])]:
        with pytest.raises(ValueError, match='Fixed comparison'):
            require_complete_sample(bad, index, ['xle'])


def test_stability_rejects_shifted_full_length_window():
    with pytest.raises(ValueError):
        period_labels(pd.date_range('2000-11-30', periods=306, freq='ME'))


def test_stability_wald_matches_independent_sandwich(tmp_path):
    rng = np.random.default_rng(20261111)
    dates = pd.date_range('2000-10-31', periods=306, freq='ME')
    frame = pd.DataFrame(rng.normal(size=(306, 5)), index=dates,
                         columns=['xle', 'gpr100', 'oil', 'market', 'xle_lag1'])
    for col in ['xle_date', 'oil_date', 'market_date']:
        frame[col] = dates
    review(frame, tmp_path)
    base = np.column_stack([np.ones(306), frame[['gpr100','oil','market']]])
    label = np.repeat(np.arange(3), 102)
    design = np.column_stack([base, base*(label==1)[:,None], base*(label==2)[:,None]])
    beta = np.linalg.lstsq(design, frame.xle, rcond=None)[0]
    scores = design * (frame.xle.to_numpy() - design@beta)[:,None]
    meat = scores.T@scores
    for lag in range(1,7):
        cross = scores[lag:].T@scores[:-lag]
        meat += (1-lag/7)*(cross+cross.T)
    bread = np.linalg.inv(design.T@design)
    cov = bread@meat@bread * 306/(306-12)
    tests = pd.read_csv(tmp_path/'stability_tests.csv').set_index('test')
    for name, cols in [('equal_oil_slopes',[6,10]), ('equal_all_coefficients',list(range(4,12)))]:
        b = beta[cols]
        statistic = b@np.linalg.solve(cov[np.ix_(cols,cols)],b)/len(cols)
        assert tests.loc[name,'p'] == pytest.approx(f.sf(statistic,len(cols),294), rel=1e-10)


def test_release_builder_rejects_stale_tables_receipt_and_code(tmp_path):
    (tmp_path/'docs').mkdir();(tmp_path/'outputs/v2').mkdir(parents=True)
    table = tmp_path/'outputs/v2/example.csv';table.write_bytes(b'value\n1\n')
    source = tmp_path/'main.py';source.write_bytes(b'# frozen\n')
    def h(path): return hashlib.sha256(path.read_bytes()).hexdigest()
    hashes = {'example.csv': h(table)}
    frozen = tmp_path/'docs/RELEASE_TEXT_INPUTS.json'
    frozen.write_text(json.dumps({'csv_sha256':hashes, 'other_sha256':{}}))
    receipt = tmp_path/'docs/CLEAN_VALIDATION.json'
    payload = dict(csv_sha256=hashes,csv_hashes_equal=True,tests_passed=1,source_code_hashes={'main.py':h(source)})
    receipt.write_text(json.dumps(payload))
    assert validate_release_inputs(tmp_path)['tests_passed']==1
    table.write_bytes(b'value\n2\n')
    with pytest.raises(ValueError,match='stale'):validate_release_inputs(tmp_path)
    payload['csv_sha256']={'example.csv':h(table)}
    receipt.write_text(json.dumps(payload))
    with pytest.raises(ValueError,match='stale'):validate_release_inputs(tmp_path)
    table.write_bytes(b'value\n1\n');payload['csv_sha256']=hashes;receipt.write_text(json.dumps(payload))
    source.write_bytes(b'# altered\n')
    with pytest.raises(ValueError,match='source changed'):validate_release_inputs(tmp_path)
