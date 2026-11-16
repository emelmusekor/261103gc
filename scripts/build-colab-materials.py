"""Prepare a versioned, reproducible teaching dataset and five Colab tutorials."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import urllib.request
import zipfile

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "web" / "class" / "20261117"
DATA = LESSON / "downloads"
DATA.mkdir(parents=True, exist_ok=True)
SITE = "https://learning-experiments-gc261103.incheon-seok-1409.chatgpt.site/class/20261117"
SOURCE_URL = "https://archive.ics.uci.edu/static/public/320/student%2Bperformance.zip"
SKILL = Path.home() / ".codex/skills/jupyter-notebook/scripts/new_notebook.py"
FEATURES = ["studytime", "failures", "absences", "schoolsup", "internet"]
ALGORITHMS = [
    dict(id="logistic", name="로지스틱 회귀", filename="01-logistic-regression.ipynb", parameter="C", values=[0.1, 1.0, 10.0], default=1.0,
         concept="여러 항목의 정보를 합쳐 두 범주를 구분합니다.", question="규제를 약하게 하면 검증 결과도 좋아질까?", parameter_note="C가 작을수록 계수를 크게 만드는 데 더 강한 제약을 둡니다."),
    dict(id="tree", name="결정트리", filename="02-decision-tree.ipynb", parameter="max_depth", values=[2, 4, None], default=4,
         concept="조건에 따라 가지를 나누며 분류합니다.", question="질문을 끝없이 세분하면 처음 보는 학생도 더 잘 맞힐까?", parameter_note="깊이가 깊을수록 더 복잡한 분류 규칙을 만들 수 있습니다. None은 깊이 제한이 없다는 뜻입니다."),
    dict(id="forest", name="랜덤포레스트", filename="03-random-forest.ipynb", parameter="max_depth", values=[2, 4, None], default=4,
         concept="서로 다르게 학습한 여러 나무의 판단을 모읍니다.", question="나무를 여러 개 모으면 깊이를 늘렸을 때의 결과도 달라질까?", parameter_note="나무 수는 100개로 고정하고 각 나무의 깊이만 바꿉니다."),
    dict(id="knn", name="K-NN", filename="04-knn.ipynb", parameter="n_neighbors", values=[1, 5, 15], default=5,
         concept="입력 항목의 값이 가까운 사례들의 정답을 참고합니다.", question="한 명의 이웃과 여러 명의 이웃 중 어느 쪽을 더 믿을까?", parameter_note="K가 작으면 가까운 개별 사례에 민감하고, K가 크면 더 많은 이웃의 판단을 모읍니다."),
    dict(id="svm", name="SVM", filename="05-svm.ipynb", parameter="C", values=[0.1, 1.0, 10.0], default=1.0,
         concept="두 범주를 구분하는 경계를 학습합니다. 이번에는 RBF 커널을 사용합니다.", question="학습 오류를 더 강하게 벌주면 새 자료의 오류도 줄어들까?", parameter_note="C가 클수록 학습 자료의 분류 오류에 더 큰 벌점을 줍니다. 커널과 gamma는 고정합니다."),
]


def write_json(file: Path, value):
    file.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def find_csv(blob: bytes) -> bytes:
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        for name in archive.namelist():
            if name.rsplit("/", 1)[-1] == "student-por.csv":
                return archive.read(name)
        for name in archive.namelist():
            if name == "student.zip":
                return find_csv(archive.read(name))
    raise RuntimeError("The verified UCI source does not contain student-por.csv")


raw_file = DATA / "student-por-original.csv"
if raw_file.exists():
    raw_bytes = raw_file.read_bytes()
else:
    with urllib.request.urlopen(SOURCE_URL, timeout=45) as response:
        raw_bytes = find_csv(response.read())
    raw_file.write_bytes(raw_bytes)
raw = pd.read_csv(io.BytesIO(raw_bytes), sep=";")
assert len(raw) == 649 and set(FEATURES + ["G3"]).issubset(raw.columns)
table = raw[FEATURES].copy()
table.insert(0, "row_id", [f"POR-{i+1:03d}" for i in range(len(raw))])
table["below_10"] = (raw["G3"] < 10).astype(int)
train_index, hold_index = train_test_split(np.arange(len(table)), test_size=0.4, random_state=42, stratify=table["below_10"])
validation_index, test_index = train_test_split(hold_index, test_size=0.5, random_state=42, stratify=table.loc[hold_index, "below_10"])
table["split"] = ""
for label, indices in [("train", train_index), ("validation", validation_index), ("test", test_index)]:
    table.loc[indices, "split"] = label
assert table.row_id.is_unique and not table.isna().any().any()
assert set(table["split"]) == {"train", "validation", "test"}
csv_file = DATA / "students-v1.csv"
table.to_csv(csv_file, index=False, encoding="utf-8-sig", lineterminator="\n")
digest = hashlib.sha256(csv_file.read_bytes()).hexdigest()
manifest = dict(version="gc-20261117-v1", sha256=digest, source_sha256=hashlib.sha256(raw_bytes).hexdigest(),
                source_url=SOURCE_URL, source_page="https://archive.ics.uci.edu/dataset/320/student+performance",
                attribution="Cortez, P. (2008). Student Performance. UCI Machine Learning Repository. https://doi.org/10.24432/C5TG7T",
                license="CC BY 4.0", rows=len(table), features=FEATURES, target="below_10", target_definition="1 if G3 < 10, otherwise 0",
                split_seed=42, split_id="gc-20261117-stratified-60-20-20-v1",
                validation_row_ids=table.loc[table.split == "validation", "row_id"].tolist(),
                splits={name:dict(rows=len(part), below_10=int(part.below_10.sum())) for name,part in table.groupby("split")},
                algorithms=ALGORITHMS)
write_json(DATA / "manifest.json", manifest)

core_imports = '''from pathlib import Path
import hashlib, io, json, platform, urllib.request
import numpy as np
import pandas as pd
import sklearn
try:
    from IPython.display import display
except ImportError:
    display = print
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix
from sklearn.inspection import permutation_importance

FEATURES = ["studytime", "failures", "absences", "schoolsup", "internet"]
TARGET = "below_10"
print("Python", platform.python_version(), "| scikit-learn", sklearn.__version__)
'''

load_data = f'''# 同じ授業用ファイルを自動で読みます。手元のファイルを優先します。
DATA_URL = "{SITE}/downloads/students-v1.csv"
EXPECTED_SHA256 = "{digest}"
DATA_VERSION = "gc-20261117-v1"
SPLIT_ID = "gc-20261117-stratified-60-20-20-v1"
csv_path = Path("students-v1.csv")
if csv_path.exists():
    data_bytes = csv_path.read_bytes()
else:
    try:
        with urllib.request.urlopen(DATA_URL, timeout=30) as response:
            data_bytes = response.read()
    except Exception as error:
        raise RuntimeError("자동 다운로드에 실패했습니다. 수업 페이지에서 students-v1.csv를 내려받아 코랩 왼쪽 파일 영역에 올린 뒤 이 셀을 다시 실행하세요.") from error
actual_hash = hashlib.sha256(data_bytes).hexdigest()
if actual_hash != EXPECTED_SHA256:
    raise ValueError("수업용 CSV 버전이 다릅니다. 원본 students-v1.csv를 다시 받아 사용하세요.")
df = pd.read_csv(io.BytesIO(data_bytes), encoding="utf-8-sig")
assert len(df) == 649 and df.row_id.is_unique
assert set(df[TARGET]) == {{0, 1}} and set(df.split) == {{"train", "validation", "test"}}
display(df.head())
display(df.groupby("split")[TARGET].agg(자료수="size", 성적10점미만="sum"))
print("studytime: 1=<2시간, 2=2~5시간, 3=5~10시간, 4=>10시간 (주당)")
print("아직 test 자료로 모델을 평가하지 않습니다.")
'''.replace('# 同じ授業用ファイルを自動で読みます。手元のファイルを優先します。', '# 공통 CSV를 자동으로 읽습니다. 같은 이름의 로컬 파일이 있으면 먼저 사용합니다.')

helpers = '''train = df.loc[df.split == "train"].copy()
validation = df.loc[df.split == "validation"].copy()
test = df.loc[df.split == "test"].copy()
assert not (set(train.row_id) & set(validation.row_id) or set(train.row_id) & set(test.row_id) or set(validation.row_id) & set(test.row_id))

def build_model(algorithm, value, columns=FEATURES):
    # studytime과 failures의 구간 코드를 연속 시간/횟수라고 가정하지 않습니다.
    numeric = [c for c in ["absences"] if c in columns]
    categories = [c for c in columns if c not in numeric]
    transforms = []
    if numeric:
        transforms.append(("numeric", StandardScaler(), numeric))
    if categories:
        transforms.append(("category", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categories))
    preprocessor = ColumnTransformer(transforms, remainder="drop")
    estimators = {
        "logistic": lambda: LogisticRegression(C=value, max_iter=3000, random_state=42),
        "tree": lambda: DecisionTreeClassifier(max_depth=value, random_state=42),
        "forest": lambda: RandomForestClassifier(n_estimators=100, max_depth=value, random_state=42, n_jobs=1),
        "knn": lambda: KNeighborsClassifier(n_neighbors=value),
        "svm": lambda: SVC(C=value, kernel="rbf", gamma="scale"),
    }
    return Pipeline([("prepare", preprocessor), ("model", estimators[algorithm]())])

def metrics(y_true, prediction):
    tn, fp, fn, tp = confusion_matrix(y_true, prediction, labels=[0, 1]).ravel()
    return dict(n=int(tn+fp+fn+tp), accuracy=float(accuracy_score(y_true, prediction)),
                balanced_accuracy=float(balanced_accuracy_score(y_true, prediction)),
                recall_below_10=float(tp/(tp+fn)) if tp+fn else None,
                recall_at_least_10=float(tn/(tn+fp)) if tn+fp else None,
                missed_below_10=int(fn), false_flags=int(fp),
                tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp))

def evaluate(model, data=validation, columns=FEATURES):
    return metrics(data[TARGET], model.predict(data[columns]))

baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(train[FEATURES], train[TARGET])
baseline_metrics = evaluate(baseline)
display(pd.DataFrame([baseline_metrics], index=["다수 범주만 답하는 기준 모델"]))
print("정확도만 보고 성공이라고 말할 수 있을까요? 10점 미만을 놓친 수를 함께 보세요.")
'''

experiment_code = '''runs = []
models = {}
for value in PARAMETER_VALUES:
    model = build_model(ALGORITHM, value)
    model.fit(train[FEATURES], train[TARGET])
    result = {"parameter": PARAMETER_NAME, "value": value,
              "train_accuracy": float(accuracy_score(train[TARGET], model.predict(train[FEATURES]))),
              **evaluate(model)}
    runs.append(result)
    models[str(value)] = model
display(pd.DataFrame(runs).round(4))
print("기준 모델 검증 정확도:", round(baseline_metrics["accuracy"], 4))
print("값을 고르는 기준은 정확도인가요, 10점 미만 사례를 놓치지 않는 것인가요?")
'''

inspect_code = '''# 자동으로 1등을 고르지 않습니다. 우선 페이지에 지정된 기본 설정을 살펴봅니다.
SELECTED_VALUE = DEFAULT_VALUE
selected_model = models[str(SELECTED_VALUE)]
pred = selected_model.predict(validation[FEATURES])
cases = validation[["row_id"] + FEATURES + [TARGET]].copy()
cases["prediction"] = pred
cases["wrong"] = cases[TARGET] != cases.prediction
cases["error_type"] = np.where((cases[TARGET] == 1) & (cases.prediction == 0), "10점 미만 놓침",
                              np.where((cases[TARGET] == 0) & (cases.prediction == 1), "10점 이상 잘못 표시", "일치"))
display(cases.loc[cases.wrong].head(10))
print("틀린 사례가 없더라도 다른 자료에서도 완벽하다는 뜻은 아닙니다.")
importance = permutation_importance(selected_model, validation[FEATURES], validation[TARGET],
                                    scoring="balanced_accuracy", n_repeats=10, random_state=42)
display(pd.DataFrame({"항목": FEATURES, "검증점수_감소_평균": importance.importances_mean,
                      "흔들림_표준편차": importance.importances_std}).sort_values("검증점수_감소_평균", ascending=False))
print("이 중요도는 이 모델과 자료에서의 의존도를 뜻합니다. 학생 성적의 원인이나 지원의 효과를 증명하지 않습니다.")
'''

stress_code = '''# 세 조건은 매번 원본 학습 자료에서 따로 시작합니다. 검증 대상과 정답은 그대로 둡니다.
stress_rows = []
small = train.groupby(TARGET, group_keys=False).sample(n=10, random_state=42)
small_model = build_model(ALGORITHM, DEFAULT_VALUE)
small_model.fit(small[FEATURES], small[TARGET])
stress_rows.append({"condition": "학습 20명(범주별 10명)", **evaluate(small_model)})

noisy = train.copy()
flip_ids = noisy.sample(frac=0.2, random_state=42).index
noisy.loc[flip_ids, TARGET] = 1 - noisy.loc[flip_ids, TARGET]
noisy_model = build_model(ALGORITHM, DEFAULT_VALUE)
noisy_model.fit(noisy[FEATURES], noisy[TARGET])
stress_rows.append({"condition": f"학습 정답 {len(flip_ids)}개 뒤집기", **evaluate(noisy_model)})

reduced_features = [c for c in FEATURES if c != "absences"]
reduced_model = build_model(ALGORITHM, DEFAULT_VALUE, reduced_features)
reduced_model.fit(train[reduced_features], train[TARGET])
stress_rows.append({"condition": "결석 항목 제외", **evaluate(reduced_model, columns=reduced_features)})
display(pd.DataFrame([{"condition": "기본 설정", **evaluate(models[str(DEFAULT_VALUE)])}] + stress_rows).round(4))
print("20명 실험은 학습량과 범주 비율이 함께 바뀝니다. 차이를 자료 수만의 효과라고 단정하지 마세요.")
print("오류나 항목 제거가 이번 분할에서 반드시 점수를 낮추는 것은 아닙니다.")
'''

export_code = '''report = {
    "schema_version": 1, "data_version": DATA_VERSION, "dataset_sha256": actual_hash,
    "split_id": SPLIT_ID, "scope": "validation", "features": FEATURES,
    "algorithm": ALGORITHM, "algorithm_name": ALGORITHM_NAME,
    "baseline": baseline_metrics, "runs": runs, "stress": stress_rows,
    "selected_value": SELECTED_VALUE, "selected_metrics": evaluate(selected_model),
    "validation_row_ids": validation.row_id.tolist(),
    "environment": {"python": platform.python_version(), "sklearn": sklearn.__version__},
}
output = Path(f"result-{ALGORITHM}.json")
output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
cases.to_csv(f"cases-{ALGORITHM}.csv", index=False, encoding="utf-8-sig")
print("생성 파일:", output.name, f"cases-{ALGORITHM}.csv")
try:
    from google.colab import files
except ImportError:
    print("로컬 실행: 현재 폴더의 파일을 사용하세요.")
else:
    files.download(str(output))
'''

final_code = '''# 조건을 확정한 뒤에만 True로 바꾸세요. 기본 '모두 실행'에서는 test를 열지 않습니다.
RUN_FINAL_TEST = False
FINAL_VALUE = SELECTED_VALUE  # 검증 결과로 고른 값을 적습니다.
if RUN_FINAL_TEST:
    assert FINAL_VALUE in PARAMETER_VALUES
    final_model = build_model(ALGORITHM, FINAL_VALUE)
    final_model.fit(train[FEATURES], train[TARGET])
    print("선택한 설정:", PARAMETER_NAME, FINAL_VALUE)
    display(pd.DataFrame([evaluate(final_model, data=test)], index=["최종 보관 자료"]))
    print("이 결과를 보고 다시 설정을 바꾸면 test도 다음 선택을 위한 검증 자료가 됩니다.")
else:
    print("test 자료는 아직 평가하지 않았습니다. 먼저 결과에 대한 판단을 기록하세요.")
'''


def md(text):
    return dict(cell_type="markdown", metadata={}, source=text.strip().splitlines(keepends=True))


def code(text, tag):
    return dict(cell_type="code", metadata={"lesson_step": tag}, source=text.strip().splitlines(keepends=True), execution_count=None, outputs=[])


verification = []
for item in ALGORITHMS:
    notebook_file = DATA / item["filename"]
    if not notebook_file.exists():
        subprocess.run([sys.executable, str(SKILL), "--kind", "tutorial", "--title", item["name"] + " 비교 실습", "--out", str(notebook_file)], check=True, capture_output=True)
    notebook = json.loads(notebook_file.read_text(encoding="utf-8"))
    settings = f'ALGORITHM = {item["id"]!r}\nALGORITHM_NAME = {item["name"]!r}\nPARAMETER_NAME = {item["parameter"]!r}\nPARAMETER_VALUES = {item["values"]!r}\nDEFAULT_VALUE = {item["default"]!r}\n'
    notebook["metadata"].update(kernelspec=dict(display_name="Python 3", language="python", name="python3"), colab=dict(name=item["filename"], provenance=[]), language_info=dict(name="python", version="3.12"))
    notebook["cells"] = [
        md(f'# {item["name"]}: {item["question"]}\n\n{item["concept"]}\n\n**실행 방법:** Google Colab에서 이 노트북을 업로드한 뒤 위에서 아래로 실행합니다. GPU와 API 키는 필요하지 않습니다. CSV는 자동으로 읽습니다. 실패하면 수업 페이지의 students-v1.csv를 코랩 왼쪽 파일 영역에 올리세요.\n\n**남길 증거:** 예상 한 문장 → 조건별 실제 결과 → 틀린 사례 하나 → 내 판단.\n\n[수업 페이지]({SITE}/algorithms/{item["id"]}.html) · [데이터 출처](https://archive.ics.uci.edu/dataset/320/student+performance)'),
        md('## 1. 실행 전에 예상하기\n\n아래 값을 바꾸기 전에 어느 설정이 학습 자료와 검증 자료에서 유리할지 자기 말로 적어 보세요.\n\n학습 자료에서 잘 맞히는 것과 처음 보는 자료에서 잘 맞히는 것은 같은가요?'),
        code(core_imports, "imports"),
        code(load_data, "load"),
        md('## 2. 비교 조건 맞추기\n\n파일의 train / validation / test 표시를 그대로 사용합니다. row_id, split, below_10은 입력 항목이 아닙니다. 전처리도 학습 자료에만 fit합니다. studytime과 failures는 범주로 변환하고 absences만 표준화합니다.'),
        code(helpers, "helpers"),
        md(f'## 3. {item["parameter"]} 하나만 바꾸기\n\n{item["parameter_note"]}\n\n각 실행의 검증 대상은 같습니다. 먼저 학습 점수와 검증 점수가 함께 움직이는지 살펴보세요.'),
        code(settings, "settings"),
        code(experiment_code, "experiments"),
        md('## 4. 틀린 사례와 항목의 중요도 보기\n\n실제 10점 미만인데 놓친 사례를 찾아보세요. 그 학생의 성격이나 노력 부족을 데이터에 없는 정보로 추측하지 않습니다. 중요도는 이 모델의 의존도이며 인과관계가 아닙니다.'),
        code(inspect_code, "inspect"),
        md('## 5. 지난 실습과 연결하기\n\n학습 자료 20명 / 학습 정답 20% 오류 / 결석 항목 제외를 비교합니다. 변경 조건은 서로 누적하지 않습니다. 결과가 반드시 나빠진다고 가정하지 않습니다.'),
        code(stress_code, "stress"),
        md('## 6. 결과 파일 내려받기\n\nresult-알고리즘.json을 수업 사이트의 결과 비교 페이지에 올리세요. 업로드한 파일은 현재 브라우저에서만 읽습니다. 검증 대상과 데이터 버전이 다르면 비교에서 제외합니다.'),
        code(export_code, "export"),
        md('## 7. 내 판단을 먼저 기록하기\n\n- 조건을 바꾸기 전의 예상은 무엇이었나요?\n- 실제 결과와 어느 부분이 달랐나요?\n- 단순 기준 모델과 비교하면 어떤 오류를 더 줄였나요?\n- AI 없이 내 알고리즘을 두 문장으로 설명할 수 있나요?\n\n**작은 확인 문제:** 검증 자료 20명 중 18명이 10점 이상이라면, 모든 학생을 10점 이상으로 답하는 모델의 정확도와 10점 미만 재현율은 각각 얼마인가요?\n\n<details><summary>답 확인</summary>정확도는 90%, 10점 미만 재현율은 0%입니다. 정확도만으로 필요한 사례를 찾았다고 말할 수 없습니다.</details>'),
        md('## 8. 선택 확정 후에만 최종 확인\n\n검증 자료에서 설정을 고른 후 따로 보관한 test에서 한 번 확인합니다. test 결과를 보고 계속 설정을 고르면 새로운 보관 자료가 필요합니다. 이 소규모 자료에서의 결과를 실제 학습지원 도구의 성능으로 일반화하지 않습니다.'),
        code(final_code, "final"),
    ]
    for index, cell in enumerate(notebook["cells"]):
        cell["id"] = f'{item["id"]}-{index:02d}'
    write_json(notebook_file, notebook)
    namespace = {"__name__": "__lesson_validation__"}
    with contextlib.redirect_stdout(io.StringIO()):
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                source = "".join(cell["source"])
                if cell["metadata"]["lesson_step"] == "load":
                    source = source.replace('csv_path = Path("students-v1.csv")', f'csv_path = Path({str(csv_file)!r})')
                exec(compile(source, str(notebook_file), "exec"), namespace)
    assert namespace["RUN_FINAL_TEST"] is False
    report = namespace["report"]
    assert report["dataset_sha256"] == digest and all(r["n"] == 130 for r in report["runs"])
    assert len(report["validation_row_ids"]) == len(set(report["validation_row_ids"])) == 130
    assert all(0 <= r["accuracy"] <= 1 for r in report["runs"] + report["stress"])
    write_json(DATA / f'reference-{item["id"]}.json', report)
    verification.append(dict(algorithm=item["id"], cells_executed=sum(c["cell_type"] == "code" for c in notebook["cells"]), selected_metrics=report["selected_metrics"], baseline=report["baseline"]))
    for file in [ROOT / f'result-{item["id"]}.json', ROOT / f'cases-{item["id"]}.csv']:
        if file.exists():
            # These files are generated only by this execution; the published copies are separate.
            file.unlink()

write_json(DATA / "verification.json", dict(date="2026-11-16", sklearn=__import__("sklearn").__version__, dataset_sha256=digest, notebooks=verification, final_test_executed=False))
(DATA / "DATA-README.txt").write_text(f'''가천대학교 머신러닝 수업 · 2026-11-17

students-v1.csv: UCI Student Performance의 student-por.csv를 수업용으로 가공한 파일입니다.
출처: {manifest["attribution"]}
라이선스: CC BY 4.0 https://creativecommons.org/licenses/by/4.0/
가공: 입력 5개 선택, G3<10인 below_10 정답 생성, 행 식별자 부여, 고정된 층화 분할 60/20/20.
G1·G2·G3 및 그 밖의 개인 배경 항목은 실습용 CSV의 입력에서 제외했습니다.
studytime: 주당 시간 구간 1=<2h / 2=2~5h / 3=5~10h / 4=>10h.
failures: 원자료의 과거 과목 실패 코드. 이번 실습에서는 범주로 처리합니다.
absences: 결석 횟수. 출석률이 아닙니다. schoolsup/internet: 원자료 yes/no 응답입니다.
row_id는 원자료의 행 번호에 기반한 수업용 식별자이며 실제 이름이 아닙니다.
split: train={len(train_index)}, validation={len(validation_index)}, test={len(test_index)}. seed=42.
파일 SHA256: {digest}

성적 10점 미만은 이번 분류의 정답 정의이며 실제 지원 필요성의 정답이 아닙니다.
자료의 관측 시점만으로 조기 예측이나 인과관계를 입증할 수 없습니다.
각 ipynb는 Colab에 업로드하고 위에서부터 실행합니다. GPU/API 키가 필요하지 않습니다.
자동 데이터 읽기가 실패하면 students-v1.csv를 Colab 왼쪽 파일 영역에 업로드하세요.
노트북은 검증 자료를 비교에 사용하고, test는 기본 실행에서 평가하지 않습니다.
''', encoding="utf-8")
with zipfile.ZipFile(DATA / "lesson-kit.zip", "w", compression=zipfile.ZIP_DEFLATED) as bundle:
    for file in sorted(DATA.iterdir()):
        if file.suffix == ".ipynb" or file.name in {"students-v1.csv", "manifest.json", "DATA-README.txt", "student-por-original.csv"}:
            bundle.write(file, file.name)
print(json.dumps(dict(rows=len(table), splits=manifest["splits"], notebooks=len(verification), sha256=digest, validation=[dict(algorithm=v["algorithm"], accuracy=v["selected_metrics"]["accuracy"], recall=v["selected_metrics"]["recall_below_10"]) for v in verification]), ensure_ascii=False))
