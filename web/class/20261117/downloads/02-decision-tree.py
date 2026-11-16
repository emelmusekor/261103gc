# 결정트리 · 트리 깊이와 과적합의 관계
# 실행 환경: Google Colab / 기본 CPU
# 데이터: students-v1.csv 선택
# 출처: Cortez, P. (2008). Student Performance. UCI Machine Learning Repository. https://doi.org/10.24432/C5TG7T

# 01 · 변경 설정과 CSV 업로드
# 변경 설정: 한 번에 항목 하나 변경 후 전체 코드 재실행
ALGORITHM = 'tree'
ALGORITHM_NAME = '결정트리'
PARAMETER_NAME = 'max_depth'
PARAMETER_VALUES = [2, 4, None]
DEFAULT_VALUE = 4
MIN_SAMPLES_LEAF = 1
SPLIT_CRITERION = 'gini'
PREDICTION_THRESHOLD = 0.5
MODEL_OPTIONS = {"min_samples_leaf": MIN_SAMPLES_LEAF, "criterion": SPLIT_CRITERION}

from pathlib import Path
import hashlib, io, json, platform
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

# students-v1.csv 업로드 및 공통 버전 확인
EXPECTED_SHA256 = "5e01746d0128a964c31cb02597fc1176c182bd502c31a2f669aa8ab0f16de387"
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
assert set(df[TARGET]) == {0, 1} and set(df.split) == {"train", "validation", "test"}
display(df.head())
display(df.groupby("split")[TARGET].agg(자료수="size", 성적10점미만="sum"))
print("studytime: 1=<2시간, 2=2~5시간, 3=5~10시간, 4=>10시간 (주당)")
print("최종 보관 자료 평가 제외")


# 02 · 모델 정의와 설정 비교
train = df.loc[df.split == "train"].copy()
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
print("정확도와 10점 미만 누락 인원 수의 동시 확인")

runs = []
models = {}
for value in PARAMETER_VALUES:
    model = build_model(ALGORITHM, value)
    model.fit(train[FEATURES], train[TARGET])
    result = {"parameter": PARAMETER_NAME, "value": value,
              "train_accuracy": float(accuracy_score(train[TARGET], predict_labels(model, train[FEATURES]))),
              **evaluate(model)}
    runs.append(result)
    models[str(value)] = model
display(pd.DataFrame(runs).round(4))
print("기준 모델 검증 정확도:", round(baseline_metrics["accuracy"], 4))
print("설정 선택 기준: 전체 정확도 또는 10점 미만 재현율")


# 03 · 오분류와 항목 중요도
# 자동으로 1등을 고르지 않습니다. 우선 페이지에 지정된 기본 설정을 살펴봅니다.
SELECTED_VALUE = DEFAULT_VALUE if DEFAULT_VALUE in PARAMETER_VALUES else PARAMETER_VALUES[0]
selected_model = models[str(SELECTED_VALUE)]
pred = predict_labels(selected_model, validation[FEATURES])
cases = validation[["row_id"] + FEATURES + [TARGET]].copy()
cases["prediction"] = pred
cases["wrong"] = cases[TARGET] != cases.prediction
cases["error_type"] = np.where((cases[TARGET] == 1) & (cases.prediction == 0), "10점 미만 놓침",
                              np.where((cases[TARGET] == 0) & (cases.prediction == 1), "10점 이상 잘못 표시", "일치"))
display(cases.loc[cases.wrong].head(10))
print("오분류 0건의 다른 자료에 대한 일반화 불가")
importance = permutation_importance(selected_model, validation[FEATURES], validation[TARGET],
                                    scoring=importance_score, n_repeats=10, random_state=42)
display(pd.DataFrame({"항목": FEATURES, "검증점수_감소_평균": importance.importances_mean,
                      "흔들림_표준편차": importance.importances_std}).sort_values("검증점수_감소_평균", ascending=False))
print("중요도: 해당 모델과 자료에서의 의존도. 인과관계의 근거 아님")


# 04 · 자료 변경과 결과 파일 저장
# 세 조건은 매번 원본 학습 자료에서 따로 시작합니다. 검증 대상과 정답은 그대로 둡니다.
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
print("20명 실험: 학습량과 범주 비율의 동시 변경. 자료 수 단독 효과로 해석 불가")
print("오류 추가와 항목 제거에 따른 점수 하락의 보장 없음")

report = {
    "schema_version": 1, "data_version": DATA_VERSION, "dataset_sha256": actual_hash,
    "split_id": SPLIT_ID, "scope": "validation", "features": FEATURES,
    "algorithm": ALGORITHM, "algorithm_name": ALGORITHM_NAME,
    "configuration": {"model_options": MODEL_OPTIONS, "prediction_threshold": PREDICTION_THRESHOLD if ALGORITHM == "logistic" else None},
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
    print("로컬 실행 결과: 현재 폴더에 파일 저장")
else:
    files.download(str(output))


# 05 · 설정 확정 후 최종 확인
# 조건을 확정한 뒤에만 True로 바꾸세요. 기본 '모두 실행'에서는 test를 열지 않습니다.
RUN_FINAL_TEST = False
FINAL_VALUE = SELECTED_VALUE  # 검증 결과로 고른 값을 적습니다.
if RUN_FINAL_TEST:
    assert FINAL_VALUE in PARAMETER_VALUES
    final_model = build_model(ALGORITHM, FINAL_VALUE)
    final_model.fit(train[FEATURES], train[TARGET])
    print("선택한 설정:", PARAMETER_NAME, FINAL_VALUE)
    display(pd.DataFrame([evaluate(final_model, data=test)], index=["최종 보관 자료"]))
    print("최종 점수에 따른 설정 재선택 시 독립된 보관 자료 추가 필요")
else:
    print("최종 보관 자료 평가 제외. 설정 확정 후 RUN_FINAL_TEST=True 변경")
