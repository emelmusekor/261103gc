"""Prepare a common dataset and five copyable Colab Python scripts."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
import types
from unittest.mock import patch
from pathlib import Path
import urllib.request
import zipfile

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "web" / "class" / "20261117"
DATA = LESSON / "downloads"
DATA.mkdir(parents=True, exist_ok=True)
SITE = "https://emelmusekor.github.io/261103gc/web/class/20261117"
SOURCE_URL = "https://archive.ics.uci.edu/static/public/320/student%2Bperformance.zip"
FEATURES = ["studytime", "failures", "absences", "schoolsup", "internet"]
ALGORITHMS = [
    dict(id="logistic", name="로지스틱 회귀", filename="01-logistic-regression.py", parameter="C", values=[0.1, 1.0, 10.0], default=1.0,
         concept="가중합과 시그모이드 함수를 통한 이진 분류", question="규제 강도와 분류 경계의 관계", parameter_note="작은 C: 규제 강화 · 큰 C: 규제 완화"),
    dict(id="tree", name="결정트리", filename="02-decision-tree.py", parameter="max_depth", values=[2, 4, None], default=4,
         concept="불순도 감소에 따른 조건 분기와 말단 노드의 분류", question="트리 깊이와 과적합의 관계", parameter_note="깊이 증가: 세부 분기 증가 · None: 깊이 제한 해제"),
    dict(id="forest", name="랜덤포레스트", filename="03-random-forest.py", parameter="max_depth", values=[2, 4, None], default=4,
         concept="복원추출과 무작위 특성 선택으로 만든 여러 트리의 예측 결합", question="개별 트리와 결합 예측의 차이", parameter_note="나무 수 고정 실험에서 개별 깊이 비교 · 기본 나무 수 100개"),
    dict(id="knn", name="K-NN", filename="04-knn.py", parameter="n_neighbors", values=[1, 5, 15], default=5,
         concept="가까운 K개 사례의 정답을 이용한 다수결 분류", question="이웃 수와 예측의 민감도", parameter_note="작은 K: 개별 사례에 민감 · 큰 K: 넓은 범위의 이웃 반영"),
    dict(id="svm", name="SVM", filename="05-svm.py", parameter="C", values=[0.1, 1.0, 10.0], default=1.0,
         concept="RBF 커널과 서포트 벡터를 이용한 분류 경계 학습", question="오류 벌점과 분류 경계의 관계", parameter_note="큰 C: 학습 오류의 벌점 증가 · RBF 커널과 gamma 고정"),
]


def control(variable, label, default, choices, observation):
    return dict(variable=variable, label=label, default=repr(default),
                choices=[dict(python=repr(value), label=str(value)) for value in choices], observation=observation)


CONTROLS = {
    "logistic": [control("CLASS_WEIGHT", "범주 가중치", None, [None, "balanced"], "소수 범주 재현율과 전체 정확도의 변화"), control("PREDICTION_THRESHOLD", "분류 기준값", 0.5, [0.3, 0.5, 0.7], "낮은 기준값에서 누락과 오표시 인원 수의 변화")],
    "tree": [control("MIN_SAMPLES_LEAF", "말단 노드의 최소 사례 수", 1, [1, 5, 10], "작은 잎과 큰 잎의 학습·검증 점수 차이"), control("SPLIT_CRITERION", "분할 기준", "gini", ["gini", "entropy"], "같은 깊이에서의 분할과 오류 사례 차이")],
    "forest": [control("N_ESTIMATORS", "나무 수", 100, [10, 100, 300], "나무 수 증가에 따른 점수와 실행 시간의 변화"), control("MAX_FEATURES", "분기별 특성 후보", "sqrt", ["sqrt", None], "일부 특성과 전체 특성을 사용하는 투표 결과 차이")],
    "knn": [control("NEIGHBOR_WEIGHTS", "이웃 투표 방식", "uniform", ["uniform", "distance"], "동일 투표와 거리 가중 투표의 차이"), control("DISTANCE_P", "거리 계산", 2, [1, 2], "맨해튼 거리(p=1)와 유클리드 거리(p=2)의 이웃 차이")],
    "svm": [control("SVM_KERNEL", "커널", "rbf", ["rbf", "linear"], "비선형 경계와 선형 경계의 검증 결과 차이"), control("SVM_GAMMA", "RBF의 영향 범위", "scale", ["scale", 0.1, 1.0, 10.0], "RBF 커널에서 gamma 증가에 따른 경계의 민감도")],
}
OPTION_EXPRESSIONS = {
    "logistic": '{"class_weight": CLASS_WEIGHT}',
    "tree": '{"min_samples_leaf": MIN_SAMPLES_LEAF, "criterion": SPLIT_CRITERION}',
    "forest": '{"n_estimators": N_ESTIMATORS, "max_features": MAX_FEATURES}',
    "knn": '{"weights": NEIGHBOR_WEIGHTS, "p": DISTANCE_P}',
    "svm": '{"kernel": SVM_KERNEL, "gamma": SVM_GAMMA}',
}
for item in ALGORITHMS:
    alternative = [0.01, 0.1, 1.0, 10.0] if item["id"] in {"logistic", "svm"} else [1, 2, 4, 8, None] if item["id"] in {"tree", "forest"} else [1, 3, 5, 15]
    item["controls"] = [control("PARAMETER_VALUES", item["parameter"] + " 비교값", item["values"], [item["values"], alternative], "비교 범위를 바꾼 뒤 학습·검증 점수의 변화")] + CONTROLS[item["id"]]


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
                validation_targets=dict(zip(table.loc[table.split == "validation", "row_id"], table.loc[table.split == "validation", "below_10"].astype(int).tolist())),
                splits={name:dict(rows=len(part), below_10=int(part.below_10.sum())) for name,part in table.groupby("split")},
                algorithms=ALGORITHMS)
write_json(DATA / "manifest.json", manifest)

core_imports = '''from pathlib import Path
import hashlib, io, json, platform, time
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
from sklearn.tree import DecisionTreeClassifier, export_text
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

load_data = f'''# students-v1.csv 업로드 및 공통 버전 확인
EXPECTED_SHA256 = "{digest}"
DATA_VERSION = "gc-20261117-v1"
SPLIT_ID = "gc-20261117-stratified-60-20-20-v1"
csv_path = Path("students-v1.csv")
if csv_path.exists():
    data_bytes = csv_path.read_bytes()
else:
    try:
        from google.colab import files
    except ImportError as error:
        raise FileNotFoundError("현재 폴더에 students-v1.csv 배치 필요") from error
    uploaded = files.upload()
    csv_files = [content for name, content in uploaded.items() if name.lower().endswith(".csv")]
    if len(csv_files) != 1:
        raise ValueError("공통 CSV 파일 1개 선택 필요")
    data_bytes = csv_files[0]
actual_hash = hashlib.sha256(data_bytes).hexdigest()
if actual_hash != EXPECTED_SHA256:
    raise ValueError("CSV 버전 불일치: 원본 students-v1.csv 사용 필요")
df = pd.read_csv(io.BytesIO(data_bytes), encoding="utf-8-sig")
assert len(df) == 649 and df.row_id.is_unique
assert set(df[TARGET]) == {{0, 1}} and set(df.split) == {{"train", "validation", "test"}}
display(df.head())
display(df.groupby("split")[TARGET].agg(자료수="size", 성적10점미만="sum"))
print("studytime: 1=<2시간, 2=2~5시간, 3=5~10시간, 4=>10시간 (주당)")
print("아직 test 자료로 모델을 평가하지 않습니다.")
'''

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
        "logistic": lambda: LogisticRegression(C=value, max_iter=3000, random_state=42, **MODEL_OPTIONS),
        "tree": lambda: DecisionTreeClassifier(max_depth=value, random_state=42, **MODEL_OPTIONS),
        "forest": lambda: RandomForestClassifier(max_depth=value, random_state=42, n_jobs=1, **MODEL_OPTIONS),
        "knn": lambda: KNeighborsClassifier(n_neighbors=value, **MODEL_OPTIONS),
        "svm": lambda: SVC(C=value, **MODEL_OPTIONS),
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

def predict_labels(model, data):
    if ALGORITHM == "logistic" and isinstance(model, Pipeline):
        return (model.predict_proba(data)[:, 1] >= PREDICTION_THRESHOLD).astype(int)
    return model.predict(data)

def evaluate(model, data=validation, columns=FEATURES):
    return metrics(data[TARGET], predict_labels(model, data[columns]))

def importance_score(model, data, y_true):
    return balanced_accuracy_score(y_true, predict_labels(model, data))

baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(train[FEATURES], train[TARGET])
baseline_metrics = evaluate(baseline)
display(pd.DataFrame([baseline_metrics], index=["다수 범주만 답하는 기준 모델"]))
print("정확도만 보고 성공이라고 말할 수 있을까요? 10점 미만을 놓친 수를 함께 보세요.")
'''

experiment_code = '''runs = []
models = {}
predictions_by_value = []
comparison = validation[["row_id", TARGET]].copy()
for value in PARAMETER_VALUES:
    model = build_model(ALGORITHM, value)
    started = time.perf_counter()
    model.fit(train[FEATURES], train[TARGET])
    fit_seconds = time.perf_counter() - started
    estimator = model.named_steps["model"]
    diagnostic = {}
    if ALGORITHM == "logistic":
        diagnostic["coefficient_norm"] = float(np.linalg.norm(estimator.coef_))
    elif ALGORITHM == "tree":
        diagnostic = {"tree_depth": int(estimator.get_depth()), "leaf_count": int(estimator.get_n_leaves())}
    elif ALGORITHM == "forest":
        diagnostic = {"n_trees": len(estimator.estimators_), "mean_tree_depth": float(np.mean([t.get_depth() for t in estimator.estimators_]))}
    elif ALGORITHM == "svm":
        diagnostic["support_vectors"] = int(estimator.n_support_.sum())
    result = {"parameter": PARAMETER_NAME, "value": value,
              "train_accuracy": float(accuracy_score(train[TARGET], predict_labels(model, train[FEATURES]))),
              "fit_seconds": fit_seconds, **diagnostic, **evaluate(model)}
    result["generalization_gap"] = result["train_accuracy"] - result["accuracy"]
    result["flagged"] = result["tp"] + result["fp"]
    runs.append(result)
    models[str(value)] = model
    labels = predict_labels(model, validation[FEATURES])
    comparison[f"prediction_{value}"] = labels
    predictions_by_value.append({"value": value, "rows": [
        {"row_id": str(row_id), "actual": int(actual), "predicted": int(predicted)}
        for row_id, actual, predicted in zip(validation.row_id, validation[TARGET], labels)
    ]})
print("설정 비교 / 1=10점 미만, 0=10점 이상")
display(pd.DataFrame(runs).round(4).T)
prediction_columns = [c for c in comparison if c.startswith("prediction_")]
comparison["prediction_changed"] = comparison[prediction_columns].nunique(axis=1) > 1
print("설정 간 예측 변경 사례:", int(comparison.prediction_changed.sum()), "명")
display(comparison.loc[comparison.prediction_changed].head(10))
print("예측 변경 0명도 유효한 관찰. 서로 다른 실행 간 비교: 결과 JSON을 비교 페이지에 함께 등록")
print("기준 모델 검증 정확도:", round(baseline_metrics["accuracy"], 4))
print("값을 고르는 기준은 정확도인가요, 10점 미만 사례를 놓치지 않는 것인가요?")
'''

inspect_code = '''# 자동으로 1등을 고르지 않습니다. 우선 페이지에 지정된 기본 설정을 살펴봅니다.
SELECTED_VALUE = DEFAULT_VALUE if DEFAULT_VALUE in PARAMETER_VALUES else PARAMETER_VALUES[0]
selected_model = models[str(SELECTED_VALUE)]
pred = predict_labels(selected_model, validation[FEATURES])
cases = validation[["row_id"] + FEATURES + [TARGET]].copy()
cases["prediction"] = pred
cases["wrong"] = cases[TARGET] != cases.prediction
cases["error_type"] = np.where((cases[TARGET] == 1) & (cases.prediction == 0), "10점 미만 놓침",
                              np.where((cases[TARGET] == 0) & (cases.prediction == 1), "10점 이상 잘못 표시", "일치"))
estimator = selected_model.named_steps["model"]
prepared = selected_model.named_steps["prepare"].transform(validation[FEATURES])
default_ids = comparison.loc[comparison.prediction_changed, "row_id"].tolist() or cases.loc[cases.wrong, "row_id"].tolist() or validation.row_id.tolist()
inspection_id = INSPECT_ROW_ID or default_ids[0]
focus = validation.loc[validation.row_id == inspection_id]
if len(focus) != 1:
    raise ValueError("검증 자료에 포함된 row_id 1개 지정 필요")
if ALGORITHM == "logistic":
    cases["score"] = selected_model.predict_proba(validation[FEATURES])[:, 1]
    for threshold in [0.3, 0.5, 0.7]:
        cases[f"threshold_{threshold}"] = (cases.score >= threshold).astype(int)
    print("동일한 모델 점수에 서로 다른 분류 기준값 적용")
    display(cases.sort_values("score", ascending=False)[["row_id", TARGET, "score", "threshold_0.3", "threshold_0.5", "threshold_0.7"]].head(20))
elif ALGORITHM == "tree":
    cases["leaf_id"] = estimator.apply(prepared)
    cases["train_leaf_n"] = estimator.tree_.n_node_samples[cases.leaf_id]
    names = selected_model.named_steps["prepare"].get_feature_names_out()
    print("선택한 트리의 상단 분기 / 결석 기준값은 표준화된 값")
    print(export_text(estimator, feature_names=list(names), max_depth=3))
elif ALGORITHM == "forest":
    cases["score"] = selected_model.predict_proba(validation[FEATURES])[:, 1]
    print("score: 나무별 10점 미만 확률 추정값의 평균. 단순한 정답 투표 비율과 구분")
elif ALGORITHM == "knn":
    distances, indices = estimator.kneighbors(selected_model.named_steps["prepare"].transform(focus[FEATURES]))
    neighbors = train.iloc[indices[0]][["row_id", TARGET]].copy()
    neighbors["distance"] = distances[0]
    if NEIGHBOR_WEIGHTS == "uniform":
        weights = np.ones(len(neighbors))
    elif (distances[0] == 0).any():
        weights = (distances[0] == 0).astype(float)
    else:
        weights = 1 / distances[0]
    neighbors["vote_weight"] = weights / weights.sum()
    print("이웃 확인 대상:", focus.row_id.iloc[0], "정답:", int(focus[TARGET].iloc[0]), "예측:", int(predict_labels(selected_model, focus[FEATURES])[0]))
    display(neighbors)
    print("거리: 표준화·범주 변환 후 공간의 거리. 거리 0인 이웃 존재 시 해당 이웃만 가중 투표 반영")
elif ALGORITHM == "svm":
    cases["decision_score"] = selected_model.decision_function(validation[FEATURES])
    print("decision_score: 분류 경계의 어느 쪽인지 나타내는 값. 확률 아님")
print("상세 확인 사례:", inspection_id)
display(cases.loc[cases.row_id == inspection_id])
print("선택 설정:", SELECTED_VALUE, "오분류 사례")
display(cases.loc[cases.wrong].head(10))
print("틀린 사례가 없더라도 다른 자료에서도 완벽하다는 뜻은 아닙니다.")
importance = permutation_importance(selected_model, validation[FEATURES], validation[TARGET],
                                    scoring=importance_score, n_repeats=10, random_state=42)
display(pd.DataFrame({"항목": FEATURES, "검증점수_감소_평균": importance.importances_mean,
                      "흔들림_표준편차": importance.importances_std}).sort_values("검증점수_감소_평균", ascending=False))
print("이 중요도는 이 모델과 자료에서의 의존도를 뜻합니다. 학생 성적의 원인이나 지원의 효과를 증명하지 않습니다.")
'''

stress_code = '''# 세 조건은 매번 원본 학습 자료에서 따로 시작합니다. 검증 대상과 정답은 그대로 둡니다.
stress_rows = []
small = train.groupby(TARGET, group_keys=False).sample(n=10, random_state=42)
small_model = build_model(ALGORITHM, SELECTED_VALUE)
small_model.fit(small[FEATURES], small[TARGET])
stress_rows.append({"condition": "학습 20명(범주별 10명)", **evaluate(small_model)})

noisy = train.copy()
flip_ids = noisy.sample(frac=0.2, random_state=42).index
noisy.loc[flip_ids, TARGET] = 1 - noisy.loc[flip_ids, TARGET]
noisy_model = build_model(ALGORITHM, SELECTED_VALUE)
noisy_model.fit(noisy[FEATURES], noisy[TARGET])
stress_rows.append({"condition": f"학습 정답 {len(flip_ids)}개 뒤집기", **evaluate(noisy_model)})

reduced_features = [c for c in FEATURES if c != "absences"]
reduced_model = build_model(ALGORITHM, SELECTED_VALUE, reduced_features)
reduced_model.fit(train[reduced_features], train[TARGET])
stress_rows.append({"condition": "결석 항목 제외", **evaluate(reduced_model, columns=reduced_features)})
display(pd.DataFrame([{"condition": "선택 설정", **evaluate(selected_model)}] + stress_rows).round(4))
print("20명 실험은 학습량과 범주 비율이 함께 바뀝니다. 차이를 자료 수만의 효과라고 단정하지 마세요.")
print("오류나 항목 제거가 이번 분할에서 반드시 점수를 낮추는 것은 아닙니다.")
'''

export_code = '''report = {
    "schema_version": 1, "data_version": DATA_VERSION, "dataset_sha256": actual_hash,
    "split_id": SPLIT_ID, "scope": "validation", "features": FEATURES,
    "algorithm": ALGORITHM, "algorithm_name": ALGORITHM_NAME,
    "configuration": {"model_options": MODEL_OPTIONS, "prediction_threshold": PREDICTION_THRESHOLD if ALGORITHM == "logistic" else None},
    "baseline": baseline_metrics, "runs": runs, "stress": stress_rows,
    "selected_value": SELECTED_VALUE, "selected_metrics": evaluate(selected_model),
    "predictions_by_value": predictions_by_value,
    "validation_row_ids": validation.row_id.tolist(),
    "environment": {"python": platform.python_version(), "sklearn": sklearn.__version__},
}
output = Path(f"result-{ALGORITHM}.json")
output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
cases.to_csv(f"cases-{ALGORITHM}.csv", index=False, encoding="utf-8-sig")
comparison.to_csv(f"prediction-comparison-{ALGORITHM}.csv", index=False, encoding="utf-8-sig")
print("생성 파일:", output.name, f"cases-{ALGORITHM}.csv", f"prediction-comparison-{ALGORITHM}.csv")
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



def formal_code(source):
    changes = {
        "아직 test 자료로 모델을 평가하지 않습니다.": "최종 보관 자료 평가 제외",
        "정확도만 보고 성공이라고 말할 수 있을까요? 10점 미만을 놓친 수를 함께 보세요.": "정확도와 10점 미만 누락 인원 수의 동시 확인",
        "값을 고르는 기준은 정확도인가요, 10점 미만 사례를 놓치지 않는 것인가요?": "설정 선택 기준: 전체 정확도 또는 10점 미만 재현율",
        "틀린 사례가 없더라도 다른 자료에서도 완벽하다는 뜻은 아닙니다.": "오분류 0건의 다른 자료에 대한 일반화 불가",
        "이 중요도는 이 모델과 자료에서의 의존도를 뜻합니다. 학생 성적의 원인이나 지원의 효과를 증명하지 않습니다.": "중요도: 해당 모델과 자료에서의 의존도. 인과관계의 근거 아님",
        "20명 실험은 학습량과 범주 비율이 함께 바뀝니다. 차이를 자료 수만의 효과라고 단정하지 마세요.": "20명 실험: 학습량과 범주 비율의 동시 변경. 자료 수 단독 효과로 해석 불가",
        "오류나 항목 제거가 이번 분할에서 반드시 점수를 낮추는 것은 아닙니다.": "오류 추가와 항목 제거에 따른 점수 하락의 보장 없음",
        "로컬 실행: 현재 폴더의 파일을 사용하세요.": "로컬 실행 결과: 현재 폴더에 파일 저장",
        "이 결과를 보고 다시 설정을 바꾸면 test도 다음 선택을 위한 검증 자료가 됩니다.": "최종 점수에 따른 설정 재선택 시 독립된 보관 자료 추가 필요",
        "test 자료는 아직 평가하지 않았습니다. 먼저 결과에 대한 판단을 기록하세요.": "최종 보관 자료 평가 제외. 설정 확정 후 RUN_FINAL_TEST=True 변경",
    }
    for before, after in changes.items():
        source = source.replace(before, after)
    return source.strip() + "\n"

verification = []
code_blocks = {}
for item in ALGORITHMS:
    settings = '# 변경 설정: 한 번에 항목 하나 변경 후 전체 코드 재실행\n' + f'ALGORITHM = {item["id"]!r}\nALGORITHM_NAME = {item["name"]!r}\nPARAMETER_NAME = {item["parameter"]!r}\nPARAMETER_VALUES = {item["values"]!r}\nDEFAULT_VALUE = {item["default"]!r}\n'
    settings += "\n".join(c["variable"] + " = " + c["default"] for c in CONTROLS[item["id"]]) + "\n"
    if item["id"] != "logistic":
        settings += "PREDICTION_THRESHOLD = 0.5\n"
    settings += "MODEL_OPTIONS = " + OPTION_EXPRESSIONS[item["id"]] + "\n"
    settings += "# 상세 확인 사례: None은 자동 선택, 특정 사례는 'POR-002' 형식으로 지정\nINSPECT_ROW_ID = None\n"
    blocks = [
        dict(title="01 · 변경 설정과 CSV 업로드", code=formal_code(settings + "\n" + core_imports + "\n" + load_data)),
        dict(title="02 · 모델 정의와 설정 비교", code=formal_code(helpers + "\n" + experiment_code)),
        dict(title="03 · 오분류와 항목 중요도", code=formal_code(inspect_code)),
        dict(title="04 · 자료 변경과 결과 파일 저장", code=formal_code(stress_code + "\n" + export_code)),
        dict(title="05 · 설정 확정 후 최종 확인", code=formal_code(final_code)),
    ]
    code_blocks[item["id"]] = blocks
    source = f'# {item["name"]} · {item["question"]}\n# 실행 환경: Google Colab / 기본 CPU\n# 데이터: students-v1.csv 선택\n# 출처: {manifest["attribution"]}\n\n' + "\n\n".join("# " + part["title"] + "\n" + part["code"] for part in blocks)
    (DATA / item["filename"]).write_text(source, encoding="utf-8", newline="\n")
    uploads, downloads = [], []
    fake_files = types.SimpleNamespace(upload=lambda: uploads.append(True) or {"students-v1.csv": csv_file.read_bytes()}, download=lambda filename: downloads.append(filename))
    fake_colab = types.ModuleType("google.colab")
    fake_colab.files = fake_files
    namespace = {"__name__": "__lesson_validation__"}
    previous_cwd = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="gc-colab-check-") as temporary:
        try:
            os.chdir(temporary)
            with contextlib.redirect_stdout(io.StringIO()), patch.dict(sys.modules, {"google.colab": fake_colab}):
                exec(compile(source, item["filename"], "exec"), namespace)
            assert uploads == [True] and downloads == [f'result-{item["id"]}.json']
            assert Path(downloads[0]).exists()
        finally:
            os.chdir(previous_cwd)
    assert namespace["RUN_FINAL_TEST"] is False
    report = namespace["report"]
    assert report["dataset_sha256"] == digest and all(r["n"] == 130 for r in report["runs"])
    assert len(report["validation_row_ids"]) == len(set(report["validation_row_ids"])) == 130
    assert all(0 <= r["accuracy"] <= 1 for r in report["runs"] + report["stress"])
    write_json(DATA / f'reference-{item["id"]}.json', report)
    verification.append(dict(algorithm=item["id"], blocks_executed=len(blocks), upload_path_verified=True, selected_metrics=report["selected_metrics"], baseline=report["baseline"]))
write_json(DATA / "code-blocks.json", code_blocks)
write_json(DATA / "verification.json", dict(date="2026-11-16", sklearn=__import__("sklearn").__version__, dataset_sha256=digest, scripts=verification, final_test_executed=False))
readme = [
    "ML 실험 데이터와 실행 코드 · 2026-11-17", "",
    "students-v1.csv: UCI student-por.csv의 열 선택, 정답 생성, 식별자 및 고정 분할 추가",
    manifest["attribution"], "라이선스: CC BY 4.0 https://creativecommons.org/licenses/by/4.0/",
    "입력: studytime, failures, absences, schoolsup, internet",
    "정답: G3<10이면 below_10=1, 그 외 0",
    "분할: train 389 / validation 130 / test 130. 초기값 42",
    "studytime: 주당 시간 구간 1=<2h / 2=2~5h / 3=5~10h / 4=>10h",
    "failures: 과거 과목 실패 코드. 범주 처리", "absences: 결석 횟수",
    "schoolsup/internet: yes/no 응답", "row_id와 split: 모델 입력 제외",
    "SHA256: " + digest, "",
    "실행: 알고리즘 페이지의 전체 코드 복사 > Colab 코드 셀에 붙여넣기 > 실행 > students-v1.csv 선택",
    "실행 환경: 기본 CPU. GPU 및 API 키 불필요", "CSV 버전 검증 후 동일한 학습·검증 분할 적용",
    "최종 보관 자료: 기본 실행에서 평가 제외. 조건 확정 후 별도 확인",
    "성적 구간 분류와 실제 지원 필요성의 구분. 관측 자료만으로 인과 효과 추론 불가",
]
(DATA / "DATA-README.txt").write_text("\n".join(readme) + "\n", encoding="utf-8")
# Retire only the five generated notebook artifacts previously published by this project.
for name in ['01-logistic-regression.ipynb','02-decision-tree.ipynb','03-random-forest.ipynb','04-knn.ipynb','05-svm.ipynb']:
    old_file = DATA / name
    if old_file.exists():
        old_file.unlink()
with zipfile.ZipFile(DATA / "lesson-kit.zip", "w", compression=zipfile.ZIP_DEFLATED) as bundle:
    for file in sorted(DATA.iterdir()):
        if file.suffix == ".py" or file.name in {"students-v1.csv", "manifest.json", "DATA-README.txt", "student-por-original.csv"}:
            bundle.write(file, file.name)
print(json.dumps(dict(rows=len(table), splits=manifest["splits"], scripts=len(verification), sha256=digest, upload_verified=all(x['upload_path_verified'] for x in verification)), ensure_ascii=False))
