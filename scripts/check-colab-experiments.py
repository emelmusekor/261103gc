"""Execute the exact settings printed in every student experiment."""
import contextlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import types
from unittest.mock import patch
from algorithm_experiments import LABS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'web/class/20261117/downloads'
manifest = json.loads((DATA / 'manifest.json').read_text(encoding='utf-8'))
output = ROOT.parent / '.private/colab-experiment-results'
output.mkdir(parents=True, exist_ok=True)
checks = []
for spec in manifest['algorithms']:
    source = (DATA / spec['filename']).read_text(encoding='utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(source.split('# students-v1.csv 업로드', 1)[0], 'imports', 'exec'), {})
    for number, lab in enumerate(LABS[spec['id']], 1):
        for step, value in enumerate(lab['values'], 1):
            config = {**lab['config'], lab['variable']: value}
            code = source
            # Exercise an explicitly selected validation case, including K-NN inspection.
            config['INSPECT_ROW_ID'] = 'POR-002'
            for variable, setting in config.items():
                code, count = re.subn(r'^'+re.escape(variable)+r' = .+$', lambda _: f'{variable} = {setting!r}', code, count=1, flags=re.M)
                assert count == 1, (spec['id'], variable)
            files = types.SimpleNamespace(upload=lambda: {'students-v1 (1).csv': (DATA / 'students-v1.csv').read_bytes()}, download=lambda _: None)
            colab = types.ModuleType('google.colab')
            colab.files = files
            namespace = {}
            previous = Path.cwd()
            with tempfile.TemporaryDirectory(prefix='gc-experiment-') as directory:
                try:
                    os.chdir(directory)
                    with contextlib.redirect_stdout(io.StringIO()), patch.dict(sys.modules, {'google.colab': colab}):
                        exec(compile(code, spec['filename'], 'exec'), namespace)
                    assert Path(f'prediction-comparison-{spec["id"]}.csv').exists()
                finally:
                    os.chdir(previous)
            report = namespace['report']
            assert namespace['RUN_FINAL_TEST'] is False
            assert namespace['inspection_id'] == 'POR-002'
            for run, group in zip(report['runs'], report['predictions_by_value']):
                assert run['value'] == group['value']
                assert len(group['rows']) == 130
                counts = dict(tn=0, fp=0, fn=0, tp=0)
                for row in group['rows']:
                    assert row['actual'] == manifest['validation_targets'][row['row_id']]
                    counts[('tp' if row['predicted'] else 'fn') if row['actual'] else ('fp' if row['predicted'] else 'tn')] += 1
                assert all(run[k] == n for k,n in counts.items())
                assert run['fit_seconds'] >= 0
                assert abs(run['generalization_gap'] - (run['train_accuracy'] - run['accuracy'])) < 1e-10
            if spec['id'] == 'knn':
                assert abs(namespace['neighbors'].vote_weight.sum() - 1) < 1e-10
                assert len(namespace['neighbors']) == namespace['SELECTED_VALUE']
            if spec['id'] == 'tree':
                assert namespace['cases'].train_leaf_n.min() >= config['MIN_SAMPLES_LEAF']
            filename = f'{spec["id"]}-lab{number}-step{step}.json'
            (output / filename).write_text(json.dumps(report, ensure_ascii=False), encoding='utf-8')
            checks.append(dict(algorithm=spec['id'], lab=number, step=step, config=config))
            print(f'PASS {spec["id"]} lab{number} step{step}', flush=True)
assert len(LABS) == 5 and sum(map(len, LABS.values())) == 15
print(json.dumps(dict(experiments=15, executions=len(checks), final_test_executed=False), ensure_ascii=False))
