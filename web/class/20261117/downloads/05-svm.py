# SVM · 오류 벌점과 분류 경계의 관계
# 실행 환경: Google Colab / 기본 CPU
# 데이터: students-v1.csv 선택
# 출처: Cortez, P. (2008). Student Performance. UCI Machine Learning Repository. https://doi.org/10.24432/C5TG7T

# 01 · 변경 설정과 CSV 업로드
# 변경 설정: 한 번에 항목 하나 변경 후 전체 코드 재실행
ALGORITHM = 'svm'
ALGORITHM_NAME = 'SVM'
PARAMETER_NAME = 'C'
PARAMETER_VALUES = [0.1, 1.0, 10.0]
DEFAULT_VALUE = 1.0
SVM_KERNEL = 'rbf'
SVM_GAMMA = 'scale'
PREDICTION_THRESHOLD = 0.5
MODEL_OPTIONS = {"kernel": SVM_KERNEL, "gamma": SVM_GAMMA}
# 상세 확인 사례: None은 자동 선택, 특정 사례는 'POR-002' 형식으로 지정
INSPECT_ROW_ID = None

from pathlib import Path
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
from sklearn.preprocessing import OneHotEncoder, StandardScaler, FunctionTransformer
from sklearn.pipeline import Pipeline
from threadpoolctl import threadpool_limits
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

# students-v1.csv 업로드 및 공통 버전 확인
EXPECTED_SHA256 = "5e01746d0128a964c31cb02597fc1176c182bd502c31a2f669aa8ab0f16de387"
DATA_VERSION = "gc-20261117-v1"
SPLIT_ID = "gc-20261117-stratified-60-20-20-v1"
csv_path = Path("students-v1.csv")
data_bytes = csv_path.read_bytes() if csv_path.exists() else b""
if hashlib.sha256(data_bytes).hexdigest() != EXPECTED_SHA256:
    # 폴더에 원본 CSV가 없거나 다른 파일이면 다시 업로드
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

def snap_to_grid(values):
    # K-NN 거리 동점 처리 고정: 1/1024 단위 값으로 맞춰 컴퓨터마다 같은 거리 계산
    return np.round(values * 1024) / 1024

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
    if algorithm == "knn":
        # 이 자료는 거리가 같은 이웃이 많음. 동점 이웃 선택이 실행 환경에 따라 바뀌지 않도록 계산 순서 고정
        threadpool_limits(limits=1, user_api="openmp")
        preprocessor = Pipeline([("columns", preprocessor), ("grid", FunctionTransformer(snap_to_grid, feature_names_out="one-to-one"))])
    estimators = {
        "logistic": lambda: LogisticRegression(C=value, max_iter=3000, random_state=42, **MODEL_OPTIONS),
        "tree": lambda: DecisionTreeClassifier(max_depth=value, random_state=42, **MODEL_OPTIONS),
        "forest": lambda: RandomForestClassifier(max_depth=value, random_state=42, n_jobs=1, **MODEL_OPTIONS),
        "knn": lambda: KNeighborsClassifier(n_neighbors=value, algorithm="brute", **MODEL_OPTIONS),
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
print("설정 선택 기준: 전체 정확도 또는 10점 미만 재현율")


# 03 · 오분류와 항목 중요도
# 자동으로 1등을 고르지 않습니다. 우선 페이지에 지정된 기본 설정을 살펴봅니다.
SELECTED_VALUE = next((v for v in PARAMETER_VALUES if v == DEFAULT_VALUE), PARAMETER_VALUES[0])
if DEFAULT_VALUE not in PARAMETER_VALUES:
    print("DEFAULT_VALUE가 PARAMETER_VALUES에 없음 → 첫 값", SELECTED_VALUE, "사용")
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
