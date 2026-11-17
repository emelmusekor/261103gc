"""Execute every offered code setting and verify the fitted estimator options."""
import ast
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

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "web/class/20261117/downloads"
manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
csv_bytes = (DATA / "students-v1.csv").read_bytes()
output = ROOT.parent / ".private/colab-variant-results"
output.mkdir(parents=True, exist_ok=True)
checks = []
for algorithm in manifest["algorithms"]:
    source = (DATA / algorithm["filename"]).read_text(encoding="utf-8")
    # Keep extension modules loaded outside patch.dict's module snapshot.
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(source.split("# students-v1.csv 업로드", 1)[0], "imports", "exec"), {})
    for control in algorithm["controls"]:
        for choice in control["choices"]:
            if choice["python"] == control["default"]:
                continue
            code, replacements = re.subn(r"^" + re.escape(control["variable"]) + r" = .+$", lambda _: control["variable"] + " = " + choice["python"], source, count=1, flags=re.M)
            assert replacements == 1
            full = algorithm["id"] == "logistic" or choice == control["choices"][-1]
            if not full:
                code = code.split("# 03 · 오분류와 항목 중요도", 1)[0]
            files = types.SimpleNamespace(upload=lambda: {"students-v1 (1).csv": csv_bytes}, download=lambda _: None)
            colab = types.ModuleType("google.colab")
            colab.files = files
            namespace = {}
            original_cwd = Path.cwd()
            with tempfile.TemporaryDirectory(prefix="gc-variant-") as temporary:
                try:
                    os.chdir(temporary)
                    with contextlib.redirect_stdout(io.StringIO()), patch.dict(sys.modules, {"google.colab": colab}):
                        exec(compile(code, algorithm["filename"], "exec"), namespace)
                finally:
                    os.chdir(original_cwd)
            assert namespace[control["variable"]] == ast.literal_eval(choice["python"])
            assert len(namespace["runs"]) == len(namespace["PARAMETER_VALUES"])
            assert all(run["n"] == 130 for run in namespace["runs"])
            for model in namespace["models"].values():
                parameters = model.named_steps["model"].get_params()
                for key, value in namespace["MODEL_OPTIONS"].items():
                    assert parameters[key] == value, (algorithm["id"], key)
            if full:
                report = namespace["report"]
                assert report["configuration"]["model_options"] == namespace["MODEL_OPTIONS"]
                filename = f'{algorithm["id"]}-{control["variable"]}-{choice["python"]}.json'
                filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)
                (output / filename).write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
            if algorithm["id"] == "logistic" and control["variable"] == "PREDICTION_THRESHOLD":
                for model in namespace["models"].values():
                    probabilities = model.predict_proba(namespace["validation"][namespace["FEATURES"]])[:, 1]
                    actual = namespace["predict_labels"](model, namespace["validation"][namespace["FEATURES"]])
                    assert (actual == (probabilities >= namespace["PREDICTION_THRESHOLD"]).astype(int)).all()
            checks.append(dict(algorithm=algorithm["id"], variable=control["variable"], value=choice["python"], full_run=full))
print(json.dumps(dict(variants=len(checks), full_runs=sum(c["full_run"] for c in checks), checks=checks), ensure_ascii=False))
