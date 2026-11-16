"""Generate monochrome algorithm visualizations and copyable Colab code pages."""
from pathlib import Path
import html
import json

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'web/class/20261117'
manifest = json.loads((DEST / 'downloads/manifest.json').read_text(encoding='utf-8'))
verification = json.loads((DEST / 'downloads/verification.json').read_text(encoding='utf-8'))
blocks = json.loads((DEST / 'downloads/code-blocks.json').read_text(encoding='utf-8'))
algorithms = manifest['algorithms']
e = html.escape
NAV = [('index','시작'),('data','데이터'),('practice','알고리즘'),('results','결과 비교'),('notes','기록')]


def page(name, title, body, active=None, nested=False, motion=False):
    prefix = '../' if nested else ''
    nav = ''.join(f'<a href="{prefix}{key}.html"' + (' aria-current="page"' if key == (active or name) else '') + f'>{label}</a>' for key,label in NAV)
    scripts = f'<script src="{prefix}lesson.js?v=5" defer></script>' + (f'<script src="{prefix}algorithm-motion.js?v=5" defer></script>' if motion else '')
    document = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="알고리즘 시각화, 공통 데이터, Google Colab 실행 코드"><title>{e(title)}</title><link rel="stylesheet" href="{prefix}lesson.css?v=5"></head><body><a class="skip" href="#main">본문 바로가기</a><div class="nav-wrap"><nav aria-label="탐구 메뉴">{nav}</nav></div><main id="main">{body}</main><footer class="footer"><a href="{prefix}../../index.html">기존 실험 모음 ↗</a></footer>{scripts}</body></html>'''
    file = DEST / (f'algorithms/{name}.html' if nested else f'{name}.html')
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(document, encoding='utf-8')


def intro(kicker,title,desc):
    return f'<div class="intro"><h1>{title}</h1><p class="lede">{desc}</p></div>'


def field(key,label,hint='',rows=3):
    return f'<label class="field">{label}' + (f'<small>{hint}</small>' if hint else '') + f'<textarea data-note="{key}" rows="{rows}" aria-label="{e(label)}"></textarea></label>'


def copybox(identifier,title,text,kind='프롬프트'):
    return f'<div class="prompt"><div class="prompt-top"><h3>{e(title)}</h3><button type="button" class="copy" data-copy="{identifier}" data-copy-label="{kind} 복사">{kind} 복사</button></div><pre id="{identifier}">{e(text.strip())}</pre></div>'


def step(number,title,text):
    return f'<li><span class="number">{number}</span><div><h3>{title}</h3><p>{text}</p></div></li>'


routes = ''.join(f'<a class="algorithm-row" href="algorithms/{a["id"]}.html"><span class="number">0{i+1}</span><div><h2>{a["name"]}</h2><p>{a["concept"]}</p></div><span class="arrow">원리 시각화 ↗</span></a>' for i,a in enumerate(algorithms))
page('index','알고리즘',intro('','알고리즘','분류 과정 시각화 · 공통 데이터 · 코랩 실행 코드') + f'''
<div class="actions"><a class="button primary" href="practice.html">알고리즘 선택</a><a class="button" href="downloads/students-v1.csv" download>공통 CSV 다운로드 ↓</a></div><section class="section algorithm-list">{routes}</section>
''')

page('data','공통 데이터',intro('DATASET / STUDENT PERFORMANCE','공통 데이터','UCI Student Performance · 포르투갈어 과목 관측 자료 · 649개 사례') + '''
<div class="actions"><a class="button primary" href="downloads/students-v1.csv" download>CSV 다운로드 ↓</a><a class="button" href="downloads/DATA-README.txt" download>데이터 설명 ↓</a></div><div class="metrics"><div class="metric"><strong>389</strong><span>학습 자료</span></div><div class="metric"><strong>130</strong><span>설정 비교용 검증 자료</span></div><div class="metric"><strong>130</strong><span>최종 확인용 보관 자료</span></div><div class="metric"><strong>5</strong><span>공통 입력 항목</span></div></div>
<section class="section"><h2>예측 대상과 입력</h2><div class="table-wrap"><table><thead><tr><th>항목</th><th>의미</th><th>처리</th></tr></thead><tbody><tr><td>studytime</td><td>주당 공부시간 구간: 1=&lt;2h / 2=2~5h / 3=5~10h / 4=&gt;10h</td><td>범주 변환</td></tr><tr><td>failures</td><td>과거 과목 실패 관련 코드</td><td>범주 변환</td></tr><tr><td>absences</td><td>결석 횟수</td><td>학습 자료 기준 표준화</td></tr><tr><td>schoolsup</td><td>추가 학교 교육 지원 여부</td><td>yes/no 범주 변환</td></tr><tr><td>internet</td><td>가정 내 인터넷 접근 여부</td><td>yes/no 범주 변환</td></tr><tr><td>below_10</td><td>최종 성적 G3&lt;10이면 1, 그 외 0</td><td>정답 · 입력 제외</td></tr><tr><td>row_id / split</td><td>사례 식별자 / 학습·검증·보관 구분</td><td>입력 제외</td></tr></tbody></table></div><p class="caption">G1·G2·G3와 나머지 배경 항목의 공통 입력 제외. G3는 정답 생성에만 사용</p></section>
<section class="section"><h2>비교 조건</h2><ul><li>고정된 층화 분할 60% / 20% / 20%, 초기값 42</li><li>모든 알고리즘에 동일한 입력·자료 분할·전처리 적용</li><li>전처리 학습 범위: train 자료만 포함</li><li>설정 비교 범위: validation 자료</li><li>설정 확정 후 test 자료에서 별도 확인</li></ul></section>
<section class="section"><h2>정확도 84.6%의 의미</h2><p>검증 자료: 10점 이상 110명, 10점 미만 20명. 전원을 10점 이상으로 분류하는 기준 모델의 정확도 84.6%, 10점 미만 재현율 0%</p><div class="note">전체 정확도와 소수 범주 누락 인원의 동시 확인. 성적 구간과 실제 지원 필요성의 구분</div></section>
<div class="evidence"><p>원자료: <a href="https://archive.ics.uci.edu/dataset/320/student+performance">Cortez (2008), Student Performance · UCI</a> · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></p><p>가공 내역: 입력 선택, 정답 생성, 사례 식별자 및 고정 분할 추가. <a href="downloads/student-por-original.csv" download>원본 CSV</a> · <a href="downloads/manifest.json">버전 정보</a></p><p>자료 누출과 전처리: <a href="https://scikit-learn.org/stable/common_pitfalls.html">scikit-learn 공식 문서</a></p></div>''')

page('practice','알고리즘 선택',intro('ALGORITHMS / 05','알고리즘 선택','분류 과정의 단계별 시각화 · 매개변수 변경 · 동일 조건의 코랩 실험') + f'<div class="algorithm-list">{routes}</div>' + '''<section class="section"><h2>공통 실행 순서</h2><ol class="steps">''' + step('01','공통 CSV 다운로드','students-v1.csv 원본 저장') + step('02','전체 코드 복사','알고리즘 페이지의 코드 복사 버튼 사용') + step('03','코랩 코드 셀 실행','새 코드 셀에 붙여넣기 → 실행 → CSV 파일 선택') + step('04','결과 비교','result-*.json 다운로드 후 비교 페이지에 추가') + '''</ol></section>''')

for a in algorithms:
    notes = {'logistic':'시각화: 두 연속 특성과 경사하강법 · 코랩: 다섯 입력의 전처리와 scikit-learn 최적화',
             'tree':'시각화: 지니 불순도 기준 · 코랩: 분할 기준과 최소 잎 크기 변경 가능',
             'forest':'시각화: 나무 5개 · 코랩: 나무 수 변경 가능(기본 100개)',
             'knn':'시각화: 두 특성의 유클리드 거리 · 코랩: 표준화·범주 변환 후 특성 공간의 거리',
             'svm':'시각화: RBF γ=2 · 코랩 기본값: RBF gamma=scale. 커널·gamma 변경 가능'}
    b = blocks[a['id']]
    code = (DEST / 'downloads' / a['filename']).read_text(encoding='utf-8')
    prompt_plan = f'''대상 알고리즘: {a['name']}
입력: studytime, failures, absences, schoolsup, internet
정답: below_10
고정 조건: 제공 CSV의 train/validation/test 분할 유지
변경 조건: {a['parameter']} = {a['values']}
요청 사항:
- 계산 순서와 각 단계의 의미 제시
- 학습 정확도와 검증 정확도의 변화 가능성 구분
- 실행 전 예상값과 실제 측정값의 구분
- 미실행 성능 수치의 생성 금지'''
    prompt_debug = f'''대상: {a['name']} 코랩 실행 코드
오류 메시지와 실패한 코드:
[붙여넣기]
요청 사항:
- 원인 설명과 최소 수정 코드 제시
- 입력 항목과 고정 자료 분할 유지
- validation 및 test 자료의 fit 포함 금지
- 수정 후 재실행 범위와 확인 기준 제시'''
    prompt_analysis = '''실제 실행 결과:
[설정별 표, 기준 모델 결과, 오분류 사례 붙여넣기]
요청 사항:
- 전체 정확도, 10점 미만 재현율, 오류 인원 수의 비교
- 예상과 관찰, 근거와 추정의 구분
- 누락된 정보의 확인 요청
- 미제공 수치 및 인과관계의 추가 금지
- 알고리즘 이해를 확인하는 질문 1개 제시, 정답의 선제 제공 금지'''
    content = intro('ALGORITHM / '+a['id'].upper(),a['name'],a['concept'])
    content += f'<section class="motion-lab" data-algorithm="{a["id"]}"></section><p class="caption">{notes[a["id"]]}</p>'
    controls = a['controls']
    table_rows = ''.join(f'<tr><td>{c["label"]}</td><td><code>{c["variable"]}</code></td><td>{e(" / ".join(v["label"] for v in c["choices"]))}</td><td>{c["observation"]}</td></tr>' for c in controls)
    content += f'''<section class="section"><h2>변경 항목과 확인할 결과</h2><div class="table-wrap"><table><thead><tr><th>변경 항목</th><th>코드 상단 변수</th><th>변경값</th><th>관찰 대상</th></tr></thead><tbody>{table_rows}</tbody></table></div>{field(a['id']+'_forecast','실행 전 예상','한 가지 항목 변경에 따른 점수·오류 사례의 예상 차이')}</section>'''
    config_text = '\n'.join(c['variable'] + ' = ' + c['default'] for c in controls)
    content += f'''<section class="section" id="colab-code"><h2>코랩 실행 코드</h2><div class="code-config"><h3>변경 위치 · 전체 코드 상단</h3><pre id="experiment-config">{e(config_text)}</pre><p class="caption">기본 코드 복사 후 코랩에서 위 변수 직접 수정. 한 번에 항목 1개 변경 → 전체 코드 재실행 → 점수와 오류 사례 비교. 공통 CSV와 자료 분할 유지</p></div><div class="run-strip"><span>① CSV 저장</span><span>② 전체 코드 복사</span><span>③ 코랩 셀에 붙여넣기</span><span>④ 변수 수정 후 실행</span></div><div class="actions"><a class="button" href="../downloads/students-v1.csv" download>CSV 다운로드 ↓</a><button class="primary" type="button" data-copy="full-code" data-copy-label="전체 코드 복사">전체 코드 복사</button><a class="button" href="https://colab.research.google.com/" target="_blank" rel="noopener">Google Colab ↗</a></div><p class="caption">기본 CPU · GPU 및 API 키 불필요 · 파일 선택 창에서 students-v1.csv 지정</p><details><summary>전체 코드 보기</summary><pre id="full-code">{e(code)}</pre></details><details><summary>단계별 코드</summary><div>'''
    content += ''.join(copybox('code-'+str(i),part['title'],part['code'],'코드') for i,part in enumerate(b))
    content += '</div></details></section>'
    content += '<section class="section"><h2>프롬프트</h2>' + copybox('plan','원리와 실행 전 예상',prompt_plan) + '<details><summary>오류 수정</summary><div>'+copybox('debug','최소 수정과 재실행',prompt_debug)+'</div></details><details><summary>결과 해석</summary><div>'+copybox('analysis','실제 측정값에 근거한 해석',prompt_analysis)+'</div></details></section>'
    content += '<section class="section"><h2>결과 기록</h2>' + field(a['id']+'_observation','예상과 실제 결과의 차이','설정, 학습·검증 점수, 오류 인원 수') + field(a['id']+'_errorcase','오분류 사례','row_id, 실제 정답, 예측, 오류 유형') + '</section>'
    transfer_questions = {
        'logistic': '모델 출력값 0.4인 사례: 분류 기준값 0.3과 0.7에서의 판단 차이와 근거',
        'tree': '학습 정확도 100%, 낮은 검증 정확도: 깊이와 최소 잎 크기의 다음 변경 방향 및 근거',
        'forest': '나무 수 10개에서 300개로 증가 후 검증 점수 유지: 다음 실험과 선택 근거',
        'knn': '가장 가까운 사례 1개의 정답 변경: K=1과 K=15 예측에 미칠 수 있는 영향과 근거',
        'svm': 'C 증가 후 학습 점수 상승·검증 점수 하락: 다음 확인 변수와 선택 근거',
    }
    content += '<section class="section"><h2>다른 조건에 적용</h2>' + field(a['id']+'_transfer','판단과 근거',transfer_questions[a['id']] + ' · AI 도움 없는 2문장 설명') + '</section>'
    observed = next(x for x in verification['scripts'] if x['algorithm']==a['id'])['selected_metrics']
    content += f'''<details><summary>기본 설정의 검증 결과</summary><p>설정 {e(str(a['default']))} · 정확도 {observed['accuracy']*100:.1f}% · 10점 미만 재현율 {observed['recall_below_10']*100:.1f}% · 누락 {observed['fn']}/20명</p><p class="caption">2026-11-16 · Python / scikit-learn {verification['sklearn']} · 제공 코드의 실제 실행값</p></details><div class="next"><a href="../practice.html">← 알고리즘 목록</a><a href="../results.html">결과 비교 →</a></div>'''
    page(a['id'],a['name'],content,active='practice',nested=True,motion=True)

page('results','결과 비교',intro('','결과 비교','동일한 검증 대상 130명 · 같은 알고리즘의 설정 변경 결과 비교') + '''
<label class="field" for="result-files">코랩 결과 JSON<small>result-*.json 복수 선택 가능 · 같은 알고리즘의 서로 다른 설정 추가 가능</small></label><input id="result-files" type="file" accept=".json,application/json" multiple disabled><p id="result-status" class="status" role="status">공통 조건 확인 중</p><div id="result-empty" class="results-empty"><h3>등록된 결과 없음</h3><p>코랩 실행 후 result-*.json 다운로드 → 파일 추가</p></div><section id="result-table" class="section" hidden><p class="fine" id="result-count"></p><div class="table-wrap"><table><thead><tr><th>알고리즘</th><th>비교값</th><th>추가 설정</th><th>학습 정확도</th><th>검증 정확도</th><th>10점 미만 재현율</th><th>10점 미만 누락</th><th>10점 이상 오표시</th></tr></thead><tbody id="results-body"></tbody></table></div><p class="caption">업로드 파일의 데이터 버전·입력·검증 대상·수치 일관성 확인. 실제 실행 여부의 별도 확인 필요</p></section><div class="actions"><button type="button" id="export-comparison">비교 결과 다운로드 ↓</button></div>
<section class="section"><h2>다수 범주 기준 모델</h2><div class="table-wrap"><table><thead><tr><th>예측 방식</th><th>정확도</th><th>10점 미만 재현율</th><th>10점 미만 누락</th><th>10점 이상 오표시</th></tr></thead><tbody><tr><td>전원 10점 이상</td><td>84.6%</td><td>0%</td><td>20/20명</td><td>0/110명</td></tr></tbody></table></div></section><section class="section"><h2>설정 선택 기준</h2><p>전체 오분류 최소화 / 10점 미만 사례의 누락 최소화 / 잘못된 표시의 영향 / 적용 가능한 범위</p>''' + field('conclusion','선택한 모델과 근거','목적, 설정, 수치, 오류 사례, 남은 한계') + '''<div class="note">최종 확인: 코드의 FINAL_VALUE 설정 후 RUN_FINAL_TEST=True 변경. 최종 점수에 따른 재선택 시 별도 보관 자료 필요</div></section>''')

page('notes','실험 기록',intro('','실험 기록','모형·설정·실측값·오류 사례·판단 근거') + '<label class="field">알고리즘<select data-note="algorithm" aria-label="알고리즘"><option value="">선택</option>' + ''.join(f'<option>{a["name"]}</option>' for a in algorithms) + '</select></label>' + field('forecast','실행 전 예상') + field('observation','실제 결과와의 차이') + field('errorcase','오분류 사례','식별자, 정답, 예측, 오류 유형') + field('conclusion','선택과 근거') + field('unknown','추가 확인 사항') + '''<div class="actions"><button class="primary" type="button" data-export-notes>기록 다운로드 ↓</button><a class="button" href="results.html">결과 비교</a></div><p id="export-status" class="status" role="status"></p>''')
print(json.dumps({'pages':len(list(DEST.rglob('*.html'))),'algorithms':len(algorithms),'format':'copyable Python'},ensure_ascii=False))
