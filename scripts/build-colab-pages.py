"""Build focused, separate class pages from the validated lesson materials."""
from pathlib import Path
import html
import json

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "web/class/20261117"
manifest = json.loads((DEST / "downloads/manifest.json").read_text(encoding="utf-8"))
verification = json.loads((DEST / "downloads/verification.json").read_text(encoding="utf-8"))
algorithms = manifest["algorithms"]
e = html.escape
nav_items = [("index", "시작"), ("data", "데이터"), ("practice", "알고리즘 실습"), ("results", "결과 비교"), ("productivity", "생산성"), ("education", "교육학"), ("notes", "나의 기록")]


def page(name, title, body, active=None, nested=False):
    prefix = "../" if nested else ""
    current = active or name
    nav = "".join(f'<a href="{prefix}{key}.html"' + (' aria-current="page"' if key == current else '') + f'>{label}</a>' for key,label in nav_items)
    output = f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="공통 데이터와 알고리즘별 코랩 실습, 생산성과 교육학을 연결하는 머신러닝 수업 자료."><title>{e(title)} · 11월 17일 탐구 실험실</title><link rel="stylesheet" href="{prefix}lesson.css?v=1"></head>
<body><a class="skip" href="#main">본문으로 바로 가기</a><header class="mast"><a class="brand" href="{prefix}index.html">탐구 실험실 <span class="fine">/ ML × AI</span></a><span class="course">가천대학교 머신러닝<br>2026.11.17</span></header><div class="nav-wrap"><nav aria-label="탐구 메뉴">{nav}<span class="sticky-status" id="save-status">기록은 이 브라우저에만 저장</span></nav></div><main id="main">{body}</main><footer class="footer"><span>ML 실험실 · 2026.11.17</span><a href="{prefix}../../index.html">기존 실험 모음 ↗</a></footer><script src="{prefix}lesson.js?v=1" defer></script></body></html>'''
    file = DEST / ("algorithms/" + name + ".html" if nested else name + ".html")
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(output, encoding="utf-8")


def intro(number, title, lede):
    return f'<div class="intro"><p class="eyebrow">FIELD NOTES / {number}</p><h1>{title}</h1><p class="lede">{lede}</p></div>'


def prompt(identifier, title, text):
    return f'<div class="prompt"><div class="prompt-top"><h3>{e(title)}</h3><button type="button" class="copy" data-copy="{identifier}">프롬프트 복사</button></div><pre id="{identifier}">{e(text.strip())}</pre></div>'


def field(key, label, hint="", rows=4):
    return f'<label class="field">{label}' + (f'<small>{hint}</small>' if hint else '') + f'<textarea data-note="{key}" rows="{rows}" aria-label="{e(label)}"></textarea></label>'


page("index", "같은 데이터, 다른 판단", intro("00", "같은 데이터,<br>다른 판단.", "학생 데이터 649개. 알고리즘 5개. 무엇을 잘 맞히고, 누구를 놓치는지 직접 확인해 보세요.") + '''
<div class="actions"><a class="button primary" href="data.html">공통 데이터부터 시작</a><a class="button" href="downloads/lesson-kit.zip" download>데이터 + 노트북 한 번에 받기 ↓</a></div>
<section class="section" aria-label="세 가지 탐구"><a class="route" href="practice.html"><span class="number">01</span><div><strong>머신러닝 · 무엇을 잘 맞혔는가?</strong><p>같은 학생, 다른 알고리즘. 정확도와 놓친 사례를 함께 비교합니다.</p></div><span class="go">실습하기 →</span></a><a class="route" href="productivity.html"><span class="number">02</span><div><strong>생산성 · 언제 일이 끝났는가?</strong><p>AI 초안 완성과 사람이 검증을 마친 시점 사이의 일을 기록합니다.</p></div><span class="go">살펴보기 →</span></a><a class="route" href="education.html"><span class="number">03</span><div><strong>교육학 · 누가 학습했는가?</strong><p>AI를 닫고 다시 설명합니다. 같은 정확도의 모델을 다른 교육 상황에 놓아봅니다.</p></div><span class="go">판단하기 →</span></a></section>
<section class="section"><h2>알고리즘 선택</h2><div class="table-wrap"><table><thead><tr><th>로지스틱 회귀</th><th>결정트리</th><th>랜덤포레스트</th><th>K-NN</th><th>SVM</th></tr></thead><tbody><tr><td><a href="algorithms/logistic.html">실행하기 →</a></td><td><a href="algorithms/tree.html">실행하기 →</a></td><td><a href="algorithms/forest.html">실행하기 →</a></td><td><a href="algorithms/knn.html">실행하기 →</a></td><td><a href="algorithms/svm.html">실행하기 →</a></td></tr></tbody></table></div><p class="caption">Google Colab · 기본 CPU · API 키 없이 실행</p></section>''')

val = manifest["splits"]["validation"]
majority = (val["rows"] - val["below_10"]) / val["rows"]
page("data", "공통 데이터 받기", intro("01", "파일을 같게.<br>비교할 학생도 같게.", "파일과 검증 대상이 서로 다르면 알고리즘의 차이인지 자료의 차이인지 알기 어렵습니다. 모두 같은 수업용 CSV를 사용하고, 파일에 미리 지정한 학습·검증 구분을 유지합니다.") + f'''
<div class="actions"><a class="button primary" href="downloads/students-v1.csv" download>공통 CSV 내려받기 ↓</a><a class="button" href="downloads/lesson-kit.zip" download>전체 실습 묶음 ↓</a><a class="button" href="downloads/DATA-README.txt" download>데이터 설명 ↓</a></div>
<div class="metrics"><div class="metric"><strong>649</strong><span>전체 관측 사례</span></div><div class="metric"><strong>389</strong><span>학습에 사용하는 사례</span></div><div class="metric"><strong>130</strong><span>설정을 비교하는 검증 사례</span></div><div class="metric"><strong>130</strong><span>선택 후 확인할 보관 사례</span></div></div>
<div class="split-viz" aria-label="학습 389명, 검증 130명, 최종 확인 130명"><span class="split-train">학습 60%</span><span class="split-val">검증 20%</span><span class="split-test">보관 20%</span></div>
<section class="section"><h2>무엇을 예측하나요?</h2><p>UCI Student Performance의 포르투갈어 과목 자료를 가공했습니다. 두 포르투갈 학교의 관측 자료에서 <strong>최종 성적 G3가 10점 미만인지</strong> 구분합니다. 학교나 학생의 성취를 평가하는 실제 서비스가 아니라, 모델의 예측과 한계를 살펴보는 실습입니다.</p><div class="note"><strong>성적 구간 ≠ 학생의 능력 전체 ≠ 실제 지원 필요성.</strong> 이번에 만든 정답은 성적 구간일 뿐입니다. 언제 측정된 정보인지 확인하지 않고 학기 초의 조기 예측이라고 설명해서도 안 됩니다.</div></section>
<section class="section"><h2>CSV에서 볼 항목</h2><div class="table-wrap"><table><thead><tr><th>열 이름</th><th>의미</th><th>이번 실습에서의 역할</th></tr></thead><tbody>
<tr><td>row_id</td><td>원자료 행 번호에 기반한 수업용 식별자</td><td>틀린 사례 확인용 · 입력 제외</td></tr><tr><td>studytime</td><td>주당 공부시간 구간: 1=&lt;2h, 2=2~5h, 3=5~10h, 4=&gt;10h</td><td>입력 · 범주로 처리</td></tr><tr><td>failures</td><td>과거 과목 실패에 관한 원자료 코드</td><td>입력 · 범주로 처리</td></tr><tr><td>absences</td><td>결석 횟수. 출석률이 아님</td><td>입력 · 학습 자료 기준으로 표준화</td></tr><tr><td>schoolsup</td><td>추가 학교 교육 지원 여부 yes/no</td><td>입력 · 지원 효과를 뜻하지 않음</td></tr><tr><td>internet</td><td>가정의 인터넷 접근 여부 yes/no</td><td>입력 · 배경과 기회에 관한 논의 가능</td></tr><tr><td>below_10</td><td>G3&lt;10이면 1, 아니면 0</td><td>맞혀야 하는 정답 · 입력 제외</td></tr><tr><td>split</td><td>train / validation / test</td><td>자료의 용도 표시 · 입력 제외</td></tr>
</tbody></table></div><p class="caption">기존 성적 없이 무엇을 알 수 있는지 보기 위해 G1·G2를 제외했습니다. G3는 정답을 만든 뒤 실습용 CSV에서 제거했습니다. 성별·가족 배경 등 나머지 열도 공통 입력에 포함하지 않았습니다.</p></section>
<section class="section"><h2>정확도 {100*majority:.1f}%면 잘한 걸까요?</h2><p>검증 자료 130명 중 110명은 10점 이상, 20명은 10점 미만입니다. 모두를 10점 이상이라고 답하기만 해도 정확도는 {100*majority:.1f}%입니다. 하지만 10점 미만인 학생은 <strong>한 명도 찾지 못합니다.</strong></p><div class="chart" aria-label="검증 자료 구성"><div class="bar-row"><span>10점 이상</span><div class="bar-track"><div class="bar" style="width:{110/130*100:.2f}%"></div></div><span>110명</span></div><div class="bar-row"><span>10점 미만</span><div class="bar-track"><div class="bar warn" style="width:{20/130*100:.2f}%"></div></div><span>20명</span></div></div><p class="caption">그래서 노트북에는 단순 기준 모델, 두 범주의 재현율, 오류 인원 수를 함께 넣었습니다.</p></section>
<section class="section"><h2>읽는 법과 재현 조건</h2><ul><li>엑셀에서는 CSV를 열어 열 이름과 값을 살펴봅니다. 변경 없이 보관하세요.</li><li>같은 CSV가 노트북에도 포함되어 있습니다. 코랩에서는 별도 데이터 업로드나 외부 주소 접속 없이 실행됩니다.</li><li>자료 분리는 정답 비율을 고려한 층화 분할, 초기값 42로 고정했습니다.</li><li>전처리는 학습 자료에서만 학습하며, 검증 자료를 학습에 넣지 않습니다.</li><li>매개변수를 비교할 때는 validation을 사용하고, test는 선택을 확정한 뒤에만 확인합니다.</li></ul></section>
<div class="evidence"><p>출처: Cortez, P. (2008), <a href="https://archive.ics.uci.edu/dataset/320/student+performance" target="_blank" rel="noopener">Student Performance · UCI</a>. <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. 열 선택·정답 생성·식별자·분할을 추가한 가공 자료입니다. <a href="downloads/student-por-original.csv" download>원본 CSV</a> · <a href="downloads/manifest.json">버전과 가공 정보</a></p><p>전처리와 자료 누출: <a href="https://scikit-learn.org/stable/common_pitfalls.html">scikit-learn 공식 설명</a></p></div><div class="next"><a href="index.html">← 시작</a><a href="practice.html">알고리즘 고르기 →</a></div>''')

rows = "".join(f'<tr><td><a href="algorithms/{a["id"]}.html">{a["name"]} →</a></td><td>{a["concept"]}</td><td>{a["question"]}</td><td><code>{a["parameter"]}</code></td></tr>' for a in algorithms)
page("practice", "알고리즘별 코랩 실습", intro("02", "알고리즘 선택", "같은 입력 5개로 성적 10점 미만 여부를 예측합니다. 알고리즘을 고르고, 매개변수 하나를 바꿔 결과를 비교하세요.") + f'''
<div class="table-wrap"><table><thead><tr><th>내가 맡을 알고리즘</th><th>판단 방식</th><th>실험할 질문</th><th>바꿀 조건</th></tr></thead><tbody>{rows}</tbody></table></div>
<section class="section"><h2>공통 조건</h2><div class="table-wrap"><table><tbody><tr><th>입력</th><td>studytime · failures · absences · schoolsup · internet</td></tr><tr><th>자료</th><td>학습 389명 / 검증 130명 / 최종 확인 130명</td></tr><tr><th>기준 모델</th><td>학습 자료에서 가장 많은 범주만 답하기</td></tr><tr><th>확인할 값</th><td>학습·검증 정확도, 범주별 재현율, 놓친 사례와 잘못 표시한 사례</td></tr></tbody></table></div></section>
<div class="note">더 해볼 수 있다면: 학습 자료 20명 / 학습 정답 20% 뒤집기 / 결석 항목 제외를 실행하세요. 각각 원본 조건에서 따로 시작하므로 변경이 누적되지 않습니다.</div>
<div class="next"><a href="data.html">← 공통 데이터</a><a href="results.html">결과 비교 →</a></div>''')

marks = {
    "logistic": '<path d="M15 100H170M20 15V100M25 90 160 20"/><circle class="dot" cx="45" cy="32" r="4"/><circle class="dot" cx="65" cy="40" r="4"/><circle class="dot" cx="40" cy="57" r="4"/><circle cx="115" cy="80" r="4"/><circle cx="142" cy="60" r="4"/>',
    "tree": '<path d="M90 15V35M90 35 45 60M90 35 135 60M45 60 25 95M45 60 65 95M135 60 115 95M135 60 155 95"/><circle class="dot" cx="90" cy="15" r="5"/><circle cx="45" cy="60" r="5"/><circle cx="135" cy="60" r="5"/>',
    "forest": '<path d="M35 15V35M35 35 12 65M35 35 58 65M90 15V35M90 35 67 65M90 35 113 65M145 15V35M145 35 122 65M145 35 168 65M35 80 90 105M90 80V105M145 80 90 105"/><circle class="dot" cx="90" cy="105" r="5"/>',
    "knn": '<circle cx="90" cy="60" r="45" stroke-dasharray="4 5"/><circle class="dot" cx="90" cy="60" r="6"/><circle class="dot" cx="65" cy="45" r="4"/><circle class="dot" cx="110" cy="35" r="4"/><circle cx="110" cy="80" r="4"/><circle cx="25" cy="25" r="4"/><circle cx="158" cy="100" r="4"/>',
    "svm": '<path d="M10 95C60 95 45 25 170 25M10 80C60 80 45 10 170 10M10 110C60 110 45 40 170 40"/><circle class="dot" cx="40" cy="30" r="4"/><circle class="dot" cx="62" cy="22" r="4"/><circle cx="130" cy="72" r="4"/><circle cx="150" cy="94" r="4"/>',
}
for a in algorithms:
    observed = next(x for x in verification["notebooks"] if x["algorithm"] == a["id"])["selected_metrics"]
    base_prompt = f'''나는 {a["name"]}으로 제공된 학생 데이터를 실험하고 있어.
내 질문은 “{a["question"]}”야.
{a["parameter"]}를 {a["values"]}로 바꾸되, CSV·입력 5개·train/validation 구분·전처리는 그대로 유지해.
먼저 이 알고리즘의 판단 방식을 쉬운 비유 하나와 실제 처리 방식으로 설명해줘.
그다음 내 예상이 맞는지 질문해줘. 실행 결과를 아직 주지 않았으니 정확도나 실험 결론은 만들지 마.
내가 확인할 코랩 셀과 비교할 지표를 짚어줘.'''
    debug_prompt = f'''아래는 제공된 {a["name"]} 코랩 노트북에서 난 오류야.
[실패한 셀의 코드와 오류 메시지를 붙여넣기]
원인을 먼저 설명하고 필요한 최소 수정만 제안해줘.
students-v1.csv의 입력 항목과 고정 split을 바꾸거나, 검증 자료를 fit에 넣거나, 전체 노트북을 새로 만들지 마.
수정 후 어떤 셀부터 다시 실행하고 무엇으로 해결 여부를 확인할지 알려줘.'''
    analysis_prompt = f'''아래는 내가 실제로 실행한 {a["name"]}의 결과야.
[조건별 표, 기준 모델 결과, 틀린 사례를 붙여넣기]
1. 예상과 관찰을 구분해 설명해줘.
2. 정확도, 10점 미만 재현율, 놓친 인원 수로 서로 다른 결론이 나오는지 확인해줘.
3. 내 해석에서 근거가 없는 부분은 질문으로 돌려줘.
4. 항목의 중요도를 성적의 원인이나 지원의 효과로 설명하지 마.
5. 내가 제공하지 않은 수치를 추가하지 마.
마지막에는 이 알고리즘을 내가 이해했는지 확인하는 질문 하나만 해줘. 내가 답하기 전에는 정답을 주지 마.'''
    body = f'<div class="algo-head"><div>{intro("02 / " + a["id"].upper(), a["name"], a["question"])}</div><svg class="algo-mark" viewBox="0 0 180 120" role="img" aria-label="{a["name"]}의 개념 그림">{marks[a["id"]]}</svg></div>'
    body += f'''<p>{a["concept"]}</p><div class="download-note"><h2>노트북을 열고 실행하기</h2><div class="actions"><a class="button primary" href="../downloads/{a["filename"]}" download>내 노트북 내려받기 ↓</a><a class="button" href="https://colab.research.google.com/" target="_blank" rel="noopener">Google Colab 열기 ↗</a></div><ol><li>코랩의 <strong>파일 → 노트북 업로드</strong>에서 내려받은 .ipynb를 엽니다.</li><li>런타임은 기본 CPU로 충분합니다. GPU·API 키가 필요하지 않습니다.</li><li>공통 CSV가 노트북에 포함되어 있습니다. 별도 데이터 업로드나 외부 접속이 필요하지 않습니다.</li><li>실행 전에 아래에 예상을 적은 뒤, 셀을 위에서부터 실행합니다.</li></ol></div>
<section class="section"><h2>이번에 바꾸는 것은 하나입니다</h2><div class="table-wrap"><table><thead><tr><th>바꿀 항목</th><th>값</th><th>읽는 법</th></tr></thead><tbody><tr><td><code>{a["parameter"]}</code></td><td>{e(str(a["values"]))}</td><td>{a["parameter_note"]}</td></tr></tbody></table></div><p class="caption">고정 조건: 입력 5개, 학습 389명, 검증 130명, 학습 자료에서만 학습하는 전처리. 기본 설정은 {e(str(a["default"]))}입니다.</p>{field(a["id"] + "_forecast", "실행 전 내 예상", "어느 설정에서 학습 점수와 검증 점수가 각각 높아질까요? 이유를 한 문장으로 적으세요.", 3)}</section>
<section class="section"><h2>실행 후 꼭 확인할 세 가지</h2><ol><li>단순 기준 모델의 정확도 84.6%보다 나아졌나요? 10점 미만 사례도 더 찾았나요?</li><li>학습 점수와 검증 점수의 차이가 설정에 따라 어떻게 바뀌었나요?</li><li>틀린 사례 한 명의 row_id와 오류 유형은 무엇인가요?</li></ol>{field(a["id"] + "_observation", "내 예상과 실제 결과", "예상 / 관찰한 수치 / 가능한 설명을 구분하세요.")}{field(a["id"] + "_errorcase", "틀린 사례 하나", "row_id, 실제 정답, 예측, 확인한 입력 항목을 적으세요. 데이터에 없는 성격이나 노력은 추측하지 않습니다.", 3)}</section>
<section class="section"><h2>AI에게 물어볼 때</h2>{prompt(a["id"] + "-plan", "실행 전 · 알고리즘과 예상", base_prompt)}<details><summary>실행이 막힐 때 · 오류 수정 프롬프트</summary><div>{prompt(a["id"] + "-debug", "최소 수정으로 원인 찾기", debug_prompt)}</div></details><details><summary>실행 후 · 실제 결과 해석 프롬프트</summary><div>{prompt(a["id"] + "-analysis", "내 결과에서만 설명하기", analysis_prompt)}</div></details></section>
<section class="section"><h2>자료와 항목 바꾸기</h2><p>노트북의 추가 실험 셀에는 학습 20명, 학습 정답 20% 뒤집기, 결석 항목 제외가 들어 있습니다. 각각 원본 학습 자료에서 따로 시작합니다. 검증 자료를 새로 뽑지 않습니다.</p><div class="note warning">20명 실험은 범주별 10명씩 뽑으므로 자료 수와 범주 비율이 함께 바뀝니다. 차이를 자료 수만의 효과라고 단정하지 마세요. 오류를 섞거나 항목을 빼도 한 번의 검증 점수가 반드시 낮아지는 것은 아닙니다.</div></section>
<details><summary>실행이 막혔을 때만 · 실제 실행으로 확인한 참고 결과</summary><div><p>기본 설정 {e(str(a["default"]))}에서 검증 정확도 <strong>{observed["accuracy"]*100:.1f}%</strong>, 10점 미만 재현율 <strong>{observed["recall_below_10"]*100:.1f}%</strong>, 놓친 사례 <strong>{observed["fn"]}/20명</strong>이었습니다.</p><p class="caption">2026-11-16, Python 로컬 환경·scikit-learn {e(verification["sklearn"])}에서 제공한 노트북의 코드 셀을 순서대로 실행한 값입니다. 라이브러리 버전에 따라 결과가 달라질 수 있습니다. 예상값이 아닙니다.</p><a class="source-link" href="../downloads/reference-{a["id"]}.json" download>참고 결과 JSON ↓</a></div></details>
<div class="next"><a href="../practice.html">← 다른 알고리즘</a><a href="../results.html">result-{a["id"]}.json으로 비교하기 →</a></div>'''
    page(a["id"], a["name"] + " 실습", body, active="practice", nested=True)

page("results", "실제로 나온 결과 비교", intro("03", "정확도가 가장 높은 모델을<br>바로 고르면 될까요?", "코랩에서 내려받은 result-*.json을 읽어 같은 검증 자료에서의 결과를 나란히 봅니다. 설정을 고를 기준을 먼저 정하고, 오류의 종류와 인원 수를 함께 확인합니다.") + '''
<label class="field" for="result-files">코랩의 결과 JSON 선택<small>여러 알고리즘 파일을 한 번에 선택할 수 있습니다. 파일은 이 브라우저에서만 읽으며 서버로 전송하지 않습니다.</small></label><input id="result-files" type="file" accept=".json,application/json" multiple disabled><p id="result-status" class="status" role="status">공통 자료 조건을 읽는 중입니다.</p>
<div id="result-empty" class="results-empty"><h3>아직 읽은 결과가 없습니다</h3><p>노트북의 ‘결과 파일 내려받기’ 셀을 실행해 result-알고리즘.json을 받으세요. 파일의 데이터 버전·입력·검증 학생·수치 일관성을 확인한 뒤 표를 만듭니다.</p></div>
<section id="result-table" class="section" hidden><p class="fine" id="result-count"></p><div class="table-wrap"><table><thead><tr><th>알고리즘</th><th>설정</th><th>학습 정확도</th><th>검증 정확도</th><th>10점 미만 재현율</th><th>10점 미만 놓침</th><th>10점 이상 잘못 표시</th></tr></thead><tbody id="results-body"></tbody></table></div><p class="caption">표는 사용자가 선택한 파일의 수치입니다. 형식과 비교 조건을 확인하며, 이 업로드만으로 실제 실행 여부를 증명하지는 않습니다.</p></section>
<div class="result-actions"><button type="button" id="export-comparison">비교 결과 JSON 내려받기 ↓</button></div>
<section class="section"><h2>기준 모델은 누구를 놓치나요?</h2><div class="table-wrap"><table><thead><tr><th>모델</th><th>검증 정확도</th><th>10점 미만 재현율</th><th>10점 미만 놓침</th><th>10점 이상 잘못 표시</th></tr></thead><tbody><tr><td>모두 10점 이상이라고 답하기</td><td>84.6%</td><td>0%</td><td>20 / 20명</td><td>0 / 110명</td></tr></tbody></table></div><p class="caption">학습 자료의 다수 범주만 답하는 기준 모델을 동일한 검증 자료에 적용한 실제 값입니다.</p></section>
<section class="section"><h2>선택하기 전에 설명하기</h2><div class="columns"><div class="panel"><h3>어떤 목적의 비교인가요?</h3><p>전체 성적 구간을 많이 맞히는 것과 10점 미만 사례를 놓치지 않는 것은 같은 기준이 아닙니다. 잘못 표시해 발생하는 영향도 함께 생각하세요.</p></div><div class="panel"><h3>여기서 고른 설정은 검증 결과입니다</h3><p>설정을 고른 뒤 노트북의 최종 확인 셀에서 FINAL_VALUE를 선택한 값으로 맞추고 RUN_FINAL_TEST=True로 한 번 확인합니다. 그 점수를 보고 다시 고르면 새 보관 자료가 필요합니다.</p></div></div>''' + field("conclusion", "내가 선택할 모델과 조건", "목적 / 선택 / 수치와 오류 사례 근거 / 남은 한계를 적으세요.") + '''</section><div class="next"><a href="practice.html">← 알고리즘 실습</a><a href="productivity.html">이번 작업의 생산성 살펴보기 →</a></div>''')

productivity_prompt = '''아래는 내가 코랩에서 실제로 확인한 결과야.
[알고리즘·설정·기준 모델 결과·검증 결과·틀린 사례 붙여넣기]
알고리즘과 설정, 기준 모델과의 비교, 놓친 사례, 해석의 한계를 포함해 5문장의 결과 보고서를 써줘.
내가 주지 않은 수치를 추가하거나 관찰한 관계를 원인으로 바꾸지 마.
정보가 없으면 확인할 수 없다고 적어줘.'''
page("productivity", "생산성: 일이 끝난 시점", intro("04", "초안이 나왔다.<br>그때 일이 끝났나요?", "방금 만든 모델 결과로 짧은 보고서를 작성해 봅니다. AI가 초안을 만드는 데 든 시간과, 그 초안을 내가 책임질 수 있는 결과로 바꾸는 데 든 일을 나누어 기록합니다.") + '''
<div class="quote">생산성을 판단할 단위는 ‘생성한 문장 수’일까요,<br>‘검증까지 마친 쓸 수 있는 결과’일까요?</div>
<section class="section"><h2>작은 실험 · 같은 결과로 5문장 보고서 만들기</h2><ol class="steps"><li><span class="number">01</span><div><h3>실제 결과를 주고 초안 요청</h3><p>검증 표와 틀린 사례를 아래 프롬프트에 넣습니다. 요청 작성과 대기 시간을 기록합니다.</p></div></li><li><span class="number">02</span><div><h3>초안을 원본 출력과 대조</h3><p>수치, 기준 모델과의 비교, 놓친 사례, 인과관계 표현을 직접 확인합니다.</p></div></li><li><span class="number">03</span><div><h3>수정 후에 완료 표시</h3><p>틀리거나 빠진 부분을 고치고 수정·검증 시간을 기록합니다. 잘못된 내용이 없었다면 무엇으로 확인했는지 남깁니다.</p></div></li></ol>''' + prompt("productivity-prompt", "실제 결과로 초안 만들기", productivity_prompt) + '''</section>
<section class="section"><h2>초안 이후의 일을 빠뜨리지 않기</h2><div class="number-grid"><label class="field">요청 작성 · 분<input id="time-prompt" data-note="요청 작성 시간(분)" type="number" min="0" max="300" step="0.1" value="0"></label><label class="field">응답 대기 · 분<input id="time-wait" data-note="응답 대기 시간(분)" type="number" min="0" max="300" step="0.1" value="0"></label><label class="field">오류 수정 · 분<input id="time-fix" data-note="오류 수정 시간(분)" type="number" min="0" max="300" step="0.1" value="0"></label><label class="field">결과 검증 · 분<input id="time-check" data-note="결과 검증 시간(분)" type="number" min="0" max="300" step="0.1" value="0"></label></div><div class="metrics"><div class="metric"><strong id="time-total">0.0분</strong><span>검증 완료까지의 전체 시간</span></div><div class="metric"><strong id="time-after">0.0분</strong><span>초안 이후 수정·검증 시간</span></div></div><p class="fine">시간이 겹친 경우 이중으로 더하지 않도록 구분해 적으세요. AI 없이 같은 일을 한 비교 기록이 없으므로 ‘몇 배 빨라졌다’는 계산은 하지 않습니다.</p></section>
<section class="section"><h2>내가 확인한 증거</h2><ul class="checklist"><li><label><input type="checkbox" data-note="검증_수치">검증 대상 수와 정확도가 실제 출력과 일치한다.</label></li><li><label><input type="checkbox" data-note="검증_기준모델">기준 모델보다 나아졌다는 표현에 비교 근거가 있다.</label></li><li><label><input type="checkbox" data-note="검증_놓침">10점 미만 사례를 놓친 인원 수가 맞다.</label></li><li><label><input type="checkbox" data-note="검증_인과">항목의 중요도를 성적의 원인이나 지원 효과로 설명하지 않았다.</label></li></ul>''' + field("report_revision", "AI 초안에서 내가 고친 것", "수정 전 표현 / 실제 출력의 근거 / 수정 후 표현을 남기세요.") + '''</section>
<section class="section"><h2>다음부터 무엇을 맡길까요?</h2><div class="table-wrap"><table><thead><tr><th>작업</th><th>맡길 수 있는 부분</th><th>사람이 확인할 부분</th></tr></thead><tbody><tr><td>반복 실행</td><td>정해진 조건의 코드와 표 생성</td><td>비교 조건과 데이터 분리</td></tr><tr><td>결과 설명</td><td>원본 수치를 읽기 쉬운 초안으로 변환</td><td>틀린 해석·누락·추가한 주장</td></tr><tr><td>모델 선택</td><td>각 선택의 장단점 정리</td><td>목적, 오류의 영향, 최종 책임</td></tr></tbody></table></div>''' + field("productivity_decision", "다음 작업의 역할 분담", "AI에게 맡길 일 / 직접 할 일 / 완료를 인정할 증거를 구체적으로 적으세요.") + '''</section>
<div class="evidence"><h3>연구와 연결하기</h3><p>고객지원 현장 연구에서는 AI 보조 도구의 생산성 효과가 작업자의 경험과 숙련도에 따라 달랐습니다. 이 한 직무의 결과를 우리 수업이나 모든 AI 작업의 효과로 그대로 옮기지 않습니다. 이번 기록으로 확인하는 것은 내 작업의 시간 구성과 검토 부담입니다. <a href="https://doi.org/10.1093/qje/qjae044" target="_blank" rel="noopener">Brynjolfsson, Li & Raymond, Generative AI at Work (QJE, 2025)</a></p></div><div class="next"><a href="results.html">← 실제 결과 비교</a><a href="education.html">학습과 교육적 판단 살펴보기 →</a></div>''')

hint_prompt = '''내가 설명한 머신러닝 개념을 점검하는 튜터가 되어줘.
먼저 내가 쓴 설명을 읽고 불분명한 부분을 찾는 질문 하나만 해줘.
내가 답하면 피드백하고 필요한 힌트를 조금씩 줘.
내가 생각하기 전에 완성된 설명이나 정답을 먼저 주지 마.
내가 이해했다는 근거가 없으면 이해했다고 칭찬하지 마.
[내가 쓴 알고리즘 설명 붙여넣기]'''
page("education", "교육학: 누가 학습했는가", intro("05", "모델이 학습했다.<br>나는 무엇을 배웠나요?", "코드가 실행된 것, 모델이 잘 맞힌 것, 내가 개념을 설명할 수 있는 것은 서로 다른 성과입니다. AI 도움 전후의 내 설명을 남기고, 같은 성능 수치를 교육적 선택에 적용해 봅니다.") + '''
<section class="section"><h2>작은 실험 1 · 설명을 받기 전에 설명해 보기</h2><p>먼저 AI 없이 두 문장으로 적습니다. 알고리즘은 무엇을 참고해 판단하며, 학습 자료에서 잘 맞혀도 검증 자료에서 틀릴 수 있는 이유는 무엇인가요?</p>''' + field("before", "AI 도움 전 내 설명", "빈칸이 남아도 괜찮습니다. 내가 현재 아는 범위를 남깁니다.") + prompt("education-hint", "완성된 답 대신 질문과 힌트 요청", hint_prompt) + field("after", "대화를 닫고 다시 쓴 내 설명", "AI 답을 복사하지 말고, 방금 설명한 내용을 자기 말로 다시 적으세요.") + '''<div class="note">이 기록은 내 이해를 점검하는 짧은 관찰입니다. 한 번 해본 결과로 특정 프롬프트의 교육 효과를 입증할 수는 없습니다.</div></section>
<section class="section"><h2>새 문제에도 설명할 수 있나요?</h2><div class="panel"><h3>학습 100%·검증 60%인 모델 A와<br>학습 80%·검증 80%인 모델 B</h3><p>같은 검증 자료를 사용했다면 새 자료에 대한 근거는 어느 쪽이 더 나아 보이나요? 결정을 내리기 전에 검증 대상 수, 기준 모델, 범주별 오류 중 무엇을 더 확인하고 싶나요?</p></div>''' + field("transfer", "AI 없이 새 문제에 답하기", "선택과 그 이유, 추가로 필요한 정보를 구분해 적으세요.") + '''</section>
<section class="section"><h2>작은 실험 2 · 같은 정확도, 다른 교육적 선택</h2><p><span class="tag">교육용 가상 사례</span> 실제 코랩 결과와 별개인 상황입니다. 학생 20명 중 성적 10점 미만은 6명, 10점 이상은 14명입니다. 두 모델 모두 16명을 맞혀 정확도는 80%입니다.</p><div class="table-wrap"><table><thead><tr><th>모델</th><th>10점 미만 놓침</th><th>10점 이상 잘못 표시</th><th>10점 미만 재현율</th><th>전체 정확도</th></tr></thead><tbody><tr><td>A</td><td>4명</td><td>0명</td><td>2/6 = 33.3%</td><td>80%</td></tr><tr><td>B</td><td>1명</td><td>3명</td><td>5/6 = 83.3%</td><td>80%</td></tr></tbody></table></div>
<fieldset><legend>상황 1 · 희망자에게 추가 상담을 제안합니다</legend><p class="fine">표시된 학생에게만 연락한다면 누구를 놓치고, 누구에게 불필요한 연락을 할까요?</p><div class="radio-line"><label><input type="radio" name="counsel" value="A" data-note="counsel_choice">모델 A</label><label><input type="radio" name="counsel" value="B" data-note="counsel_choice">모델 B</label><label><input type="radio" name="counsel" value="모델만으로 선택 보류" data-note="counsel_choice">모델만으로 선택 보류</label></div></fieldset>
<fieldset><legend>상황 2 · 표시된 학생에게 자동으로 불이익을 줍니다</legend><p class="fine">같은 분류가 수강 제한이나 기회 박탈로 이어진다면 같은 선택을 할 수 있을까요?</p><div class="radio-line"><label><input type="radio" name="penalty" value="A" data-note="penalty_choice">모델 A</label><label><input type="radio" name="penalty" value="B" data-note="penalty_choice">모델 B</label><label><input type="radio" name="penalty" value="모델만으로 선택 보류" data-note="penalty_choice">모델만으로 선택 보류</label></div></fieldset><p id="decision-feedback" class="decision-feedback" aria-live="polite" hidden></p>''' + field("education_reason", "두 상황에서 내가 선택한 이유", "어떤 오류의 영향을 더 우려했나요? 사람의 확인, 이의 제기, 학생의 선택권은 어디에 필요할까요?") + '''<div class="note warning">성적 10점 미만 여부는 실제 지원 필요성의 정답이 아닙니다. 모델을 고르는 문제에 앞서, 이 정보를 이 목적으로 사용해도 되는지 판단해야 합니다.</div></section>
<section class="section"><h2>데이터에 있는 관계와 교육적 효과</h2><div class="panel"><h3>추가 지원을 받는 학생의 성적이 낮게 관찰되었다면?</h3><p>지원이 성적을 낮췄다고 바로 말할 수 있을까요? 원래 어려움을 겪던 학생에게 지원이 제공되었을 가능성, 지원 전의 상태, 측정 시점, 비교할 집단을 생각해 보세요. 이번 관측 자료와 모델 중요도만으로 지원의 인과 효과를 확인할 수 없습니다.</p></div>''' + field("policy", "내가 정할 교육적 사용 원칙", "모델은 어디까지 제안하고, 사람은 무엇을 확인한 뒤 어떤 결정을 할 수 있나요?") + '''</section><div class="evidence"><h3>연구와 연결하기</h3><p>고등학교 수학 연구는 AI를 사용하는 연습 중 수행과 AI 없이 치르는 평가를 구분했고, 튜터의 도움 방식에 따른 차이를 보고했습니다. 이를 모든 과목의 효과로 일반화하지 않으면서 ‘결과물 완성과 학습을 어떻게 따로 확인할까’를 묻습니다. <a href="https://hamsabastani.github.io/education_llm.pdf" target="_blank" rel="noopener">Bastani 외, Generative AI Without Guardrails Can Harm Learning (2025)</a></p></div><div class="next"><a href="productivity.html">← 생산성 기록</a><a href="notes.html">나의 기록 마무리 →</a></div>''')

page("notes", "나의 기록", intro("06", "실험 기록", "모델·설정·실제 수치·오류 사례와 판단을 적으세요. 다른 페이지에서 쓴 내용도 함께 내려받을 수 있습니다. 기록은 이 브라우저에만 저장됩니다.") + '''
<label class="field">내가 맡은 알고리즘<select data-note="algorithm" aria-label="내가 맡은 알고리즘"><option value="">선택하세요</option>''' + "".join(f'<option>{a["name"]}</option>' for a in algorithms) + '''</select></label>''' + field("forecast", "처음의 예상", "어떤 조건에서 무엇이 달라질 것이라고 생각했나요?") + field("observation", "실제로 확인한 차이", "설정, 검증 점수, 오류 인원 수를 함께 적으세요.") + field("errorcase", "내가 확인한 오류 사례", "row_id와 실제·예측의 차이, 확인한 근거를 남기세요.") + field("conclusion", "목적에 맞는 내 선택", "정확도 순위 외에 어떤 기준을 썼나요?") + field("unknown", "여전히 모르는 점", "한계가 있는 부분을 확인된 사실과 구분해 적으세요.") + '''
<section class="section"><h2>마지막 확인</h2><ul class="checklist"><li><label><input type="checkbox" data-note="완료_실행">코랩에서 내 알고리즘을 실행하고 실제 결과 파일을 받았다.</label></li><li><label><input type="checkbox" data-note="완료_비교">같은 검증 대상에서 기준 모델과 내 결과를 비교했다.</label></li><li><label><input type="checkbox" data-note="완료_생산성">AI 초안에서 사람이 검토하고 수정한 일을 기록했다.</label></li><li><label><input type="checkbox" data-note="완료_설명">AI를 닫고 알고리즘과 결과를 자기 말로 설명했다.</label></li><li><label><input type="checkbox" data-note="완료_한계">교육적으로 사용할 수 있는 범위와 확인하지 못한 점을 구분했다.</label></li></ul></section>
<div class="actions"><button class="primary" type="button" data-export-notes>내 기록 전체 내려받기 ↓</button><a class="button" href="results.html">실행 결과 비교로 돌아가기</a></div><p id="export-status" class="status" role="status"></p><p class="caption">실행 수치는 코랩의 result-*.json, 내 예상과 판단은 이 기록 파일에 담깁니다. 브라우저 데이터가 지워지기 전에 내려받으세요.</p>''')

print(json.dumps(dict(pages=len(list(DEST.rglob('*.html'))), algorithms=len(algorithms)), ensure_ascii=False))
