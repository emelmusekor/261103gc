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
NAV = [('index','시작'),('data','데이터'),('practice','알고리즘'),('results','결과 비교'),('productivity','생산성'),('education','교육학'),('notes','기록')]


def page(name, title, body, active=None, nested=False, motion=False):
    prefix = '../' if nested else ''
    nav = ''.join(f'<a href="{prefix}{key}.html"' + (' aria-current="page"' if key == (active or name) else '') + f'>{label}</a>' for key,label in NAV)
    scripts = f'<script src="{prefix}lesson.js?v=3" defer></script>' + (f'<script src="{prefix}algorithm-motion.js?v=3" defer></script>' if motion else '')
    document = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="머신러닝 알고리즘 시각화, 공통 데이터, Google Colab 복사 코드"><title>{e(title)} · ML 실험실</title><link rel="stylesheet" href="{prefix}lesson.css?v=3"></head><body><a class="skip" href="#main">본문 바로가기</a><header class="mast"><a class="brand" href="{prefix}index.html">ML 실험실<span> / 2026.11.17</span></a><span class="course">가천대학교 머신러닝</span></header><div class="nav-wrap"><nav aria-label="탐구 메뉴">{nav}<span class="sticky-status" id="save-status">브라우저 내 기록 저장</span></nav></div><main id="main">{body}</main><footer class="footer"><span>ML · DATA · HUMAN DECISIONS</span><a href="{prefix}../../index.html">기존 실험 모음 ↗</a></footer>{scripts}</body></html>'''
    file = DEST / (f'algorithms/{name}.html' if nested else f'{name}.html')
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(document, encoding='utf-8')


def intro(kicker,title,desc):
    return f'<div class="intro"><p class="eyebrow">{e(kicker)}</p><h1>{title}</h1><p class="lede">{desc}</p></div>'


def field(key,label,hint='',rows=3):
    return f'<label class="field">{label}' + (f'<small>{hint}</small>' if hint else '') + f'<textarea data-note="{key}" rows="{rows}" aria-label="{e(label)}"></textarea></label>'


def copybox(identifier,title,text,kind='프롬프트'):
    return f'<div class="prompt"><div class="prompt-top"><h3>{e(title)}</h3><button type="button" class="copy" data-copy="{identifier}" data-copy-label="{kind} 복사">{kind} 복사</button></div><pre id="{identifier}">{e(text.strip())}</pre></div>'


def step(number,title,text):
    return f'<li><span class="number">{number}</span><div><h3>{title}</h3><p>{text}</p></div></li>'


routes = ''.join(f'<a class="algorithm-row" href="algorithms/{a["id"]}.html"><span class="number">0{i+1}</span><div><h2>{a["name"]}</h2><p>{a["concept"]}</p></div><span class="arrow">원리 시각화 ↗</span></a>' for i,a in enumerate(algorithms))
page('index','머신러닝 알고리즘',intro('MACHINE LEARNING / VISUAL LAB','분류의 원리.<br>판단의 근거.','알고리즘별 모션그래픽 · 동일 데이터의 모형 비교 · 복사형 코랩 실행 코드') + f'''
<div class="actions"><a class="button primary" href="practice.html">알고리즘 선택</a><a class="button" href="downloads/students-v1.csv" download>공통 CSV 다운로드 ↓</a></div><section class="section algorithm-list">{routes}</section>
<section class="section"><div class="columns"><a class="panel topic-link" href="productivity.html"><span class="eyebrow">PRODUCTIVITY</span><h2>초안 이후의 작업</h2><p>생성·수정·검증의 시간과 역할 분담</p></a><a class="panel topic-link" href="education.html"><span class="eyebrow">EDUCATION</span><h2>수행과 학습의 구분</h2><p>독립 설명·오류의 영향·교육적 사용 범위</p></a></div></section>''')

page('data','공통 데이터',intro('DATASET / STUDENT PERFORMANCE','공통 데이터','UCI Student Performance · 포르투갈어 과목 관측 자료 · 649개 사례') + '''
<div class="actions"><a class="button primary" href="downloads/students-v1.csv" download>CSV 다운로드 ↓</a><a class="button" href="downloads/DATA-README.txt" download>데이터 설명 ↓</a></div><div class="metrics"><div class="metric"><strong>389</strong><span>학습 자료</span></div><div class="metric"><strong>130</strong><span>설정 비교용 검증 자료</span></div><div class="metric"><strong>130</strong><span>최종 확인용 보관 자료</span></div><div class="metric"><strong>5</strong><span>공통 입력 항목</span></div></div>
<section class="section"><h2>예측 대상과 입력</h2><div class="table-wrap"><table><thead><tr><th>항목</th><th>의미</th><th>처리</th></tr></thead><tbody><tr><td>studytime</td><td>주당 공부시간 구간: 1=&lt;2h / 2=2~5h / 3=5~10h / 4=&gt;10h</td><td>범주 변환</td></tr><tr><td>failures</td><td>과거 과목 실패 관련 코드</td><td>범주 변환</td></tr><tr><td>absences</td><td>결석 횟수</td><td>학습 자료 기준 표준화</td></tr><tr><td>schoolsup</td><td>추가 학교 교육 지원 여부</td><td>yes/no 범주 변환</td></tr><tr><td>internet</td><td>가정 내 인터넷 접근 여부</td><td>yes/no 범주 변환</td></tr><tr><td>below_10</td><td>최종 성적 G3&lt;10이면 1, 그 외 0</td><td>정답 · 입력 제외</td></tr><tr><td>row_id / split</td><td>사례 식별자 / 학습·검증·보관 구분</td><td>입력 제외</td></tr></tbody></table></div><p class="caption">G1·G2·G3와 나머지 배경 항목의 공통 입력 제외. G3는 정답 생성에만 사용</p></section>
<section class="section"><h2>비교 조건</h2><ul><li>고정된 층화 분할 60% / 20% / 20%, 초기값 42</li><li>모든 알고리즘에 동일한 입력·자료 분할·전처리 적용</li><li>전처리 학습 범위: train 자료만 포함</li><li>설정 비교 범위: validation 자료</li><li>설정 확정 후 test 자료에서 별도 확인</li></ul></section>
<section class="section"><h2>정확도 84.6%의 의미</h2><p>검증 자료: 10점 이상 110명, 10점 미만 20명. 전원을 10점 이상으로 분류하는 기준 모델의 정확도 84.6%, 10점 미만 재현율 0%</p><div class="note">전체 정확도와 소수 범주 누락 인원의 동시 확인. 성적 구간과 실제 지원 필요성의 구분</div></section>
<div class="evidence"><p>원자료: <a href="https://archive.ics.uci.edu/dataset/320/student+performance">Cortez (2008), Student Performance · UCI</a> · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></p><p>가공 내역: 입력 선택, 정답 생성, 사례 식별자 및 고정 분할 추가. <a href="downloads/student-por-original.csv" download>원본 CSV</a> · <a href="downloads/manifest.json">버전 정보</a></p><p>자료 누출과 전처리: <a href="https://scikit-learn.org/stable/common_pitfalls.html">scikit-learn 공식 문서</a></p></div>''')

page('practice','알고리즘 선택',intro('ALGORITHMS / 05','알고리즘 선택','분류 과정의 단계별 시각화 · 매개변수 변경 · 동일 조건의 코랩 실험') + f'<div class="algorithm-list">{routes}</div>' + '''<section class="section"><h2>공통 실행 순서</h2><ol class="steps">''' + step('01','공통 CSV 다운로드','students-v1.csv 원본 저장') + step('02','전체 코드 복사','알고리즘 페이지의 코드 복사 버튼 사용') + step('03','코랩 코드 셀 실행','새 코드 셀에 붙여넣기 → 실행 → CSV 파일 선택') + step('04','결과 비교','result-*.json 다운로드 후 비교 페이지에 추가') + '''</ol></section>''')

for a in algorithms:
    notes = {'logistic':'시각화: 두 연속 특성과 경사하강법 · 코랩: 다섯 입력의 전처리와 scikit-learn 최적화',
             'tree':'시각화와 코랩의 깊이 조건: 2 / 4 / 제한 없음',
             'forest':'시각화: 나무 5개 · 코랩: 나무 100개 · 깊이 조건: 2 / 4 / 제한 없음',
             'knn':'시각화: 두 특성의 유클리드 거리 · 코랩: 표준화·범주 변환 후 특성 공간의 거리',
             'svm':'시각화: RBF γ=2 · 코랩: RBF gamma=scale. 결정함수 값과 확률의 구분'}
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
    content += f'''<section class="section"><h2>매개변수와 관찰 항목</h2><div class="table-wrap"><table><thead><tr><th>변경 항목</th><th>값</th><th>의미</th></tr></thead><tbody><tr><td><code>{a['parameter']}</code></td><td>{e(str(a['values']))}</td><td>{a['parameter_note']}</td></tr></tbody></table></div><div class="observation-grid"><div><h3>01 · 학습과 검증</h3><p>설정별 두 점수의 차이</p></div><div><h3>02 · 기준 모델</h3><p>정확도 84.6%와 재현율 0%의 비교</p></div><div><h3>03 · 오분류</h3><p>누락 사례와 잘못 표시한 사례의 구분</p></div></div>{field(a['id']+'_forecast','실행 전 예상','설정별 학습 점수와 검증 점수의 예상 차이')}</section>'''
    content += f'''<section class="section" id="colab-code"><h2>코랩 실행 코드</h2><div class="run-strip"><span>① CSV 저장</span><span>② 전체 코드 복사</span><span>③ 코랩 셀에 붙여넣기</span><span>④ 실행 후 CSV 선택</span></div><div class="actions"><a class="button" href="../downloads/students-v1.csv" download>CSV 다운로드 ↓</a><button class="primary" type="button" data-copy="full-code" data-copy-label="전체 코드 복사">전체 코드 복사</button><a class="button" href="https://colab.research.google.com/" target="_blank" rel="noopener">Google Colab ↗</a></div><p class="caption">기본 CPU · GPU 및 API 키 불필요 · 파일 선택 창에서 students-v1.csv 지정</p><details><summary>전체 코드 보기</summary><pre id="full-code">{e(code)}</pre></details><details><summary>단계별 코드</summary><div>'''
    content += ''.join(copybox('code-'+str(i),part['title'],part['code'],'코드') for i,part in enumerate(b))
    content += '</div></details></section>'
    content += '<section class="section"><h2>프롬프트</h2>' + copybox('plan','원리와 실행 전 예상',prompt_plan) + '<details><summary>오류 수정</summary><div>'+copybox('debug','최소 수정과 재실행',prompt_debug)+'</div></details><details><summary>결과 해석</summary><div>'+copybox('analysis','실제 측정값에 근거한 해석',prompt_analysis)+'</div></details></section>'
    content += '<section class="section"><h2>결과 기록</h2>' + field(a['id']+'_observation','예상과 실제 결과의 차이','설정, 학습·검증 점수, 오류 인원 수') + field(a['id']+'_errorcase','오분류 사례','row_id, 실제 정답, 예측, 오류 유형') + '</section>'
    observed = next(x for x in verification['scripts'] if x['algorithm']==a['id'])['selected_metrics']
    content += f'''<details><summary>기본 설정의 검증 결과</summary><p>설정 {e(str(a['default']))} · 정확도 {observed['accuracy']*100:.1f}% · 10점 미만 재현율 {observed['recall_below_10']*100:.1f}% · 누락 {observed['fn']}/20명</p><p class="caption">2026-11-16 · Python / scikit-learn {verification['sklearn']} · 제공 코드의 실제 실행값</p></details><div class="next"><a href="../practice.html">← 알고리즘 목록</a><a href="../results.html">결과 비교 →</a></div>'''
    page(a['id'],a['name'],content,active='practice',nested=True,motion=True)

page('results','결과 비교',intro('MODEL COMPARISON','결과 비교','동일한 검증 대상 130명 · 알고리즘별 세 설정 · 정확도와 오류 유형의 동시 비교') + '''
<label class="field" for="result-files">코랩 결과 JSON<small>result-*.json 복수 선택 가능 · 브라우저 내 처리 · 서버 전송 없음</small></label><input id="result-files" type="file" accept=".json,application/json" multiple disabled><p id="result-status" class="status" role="status">공통 조건 확인 중</p><div id="result-empty" class="results-empty"><h3>등록된 결과 없음</h3><p>코랩 실행 후 result-*.json 다운로드 → 파일 추가</p></div><section id="result-table" class="section" hidden><p class="fine" id="result-count"></p><div class="table-wrap"><table><thead><tr><th>알고리즘</th><th>설정</th><th>학습 정확도</th><th>검증 정확도</th><th>10점 미만 재현율</th><th>10점 미만 누락</th><th>10점 이상 오표시</th></tr></thead><tbody id="results-body"></tbody></table></div><p class="caption">업로드 파일의 데이터 버전·입력·검증 대상·수치 일관성 확인. 실제 실행 여부의 별도 확인 필요</p></section><div class="actions"><button type="button" id="export-comparison">비교 결과 다운로드 ↓</button></div>
<section class="section"><h2>다수 범주 기준 모델</h2><div class="table-wrap"><table><thead><tr><th>예측 방식</th><th>정확도</th><th>10점 미만 재현율</th><th>10점 미만 누락</th><th>10점 이상 오표시</th></tr></thead><tbody><tr><td>전원 10점 이상</td><td>84.6%</td><td>0%</td><td>20/20명</td><td>0/110명</td></tr></tbody></table></div></section><section class="section"><h2>설정 선택 기준</h2><p>전체 오분류 최소화 / 10점 미만 사례의 누락 최소화 / 잘못된 표시의 영향 / 적용 가능한 범위</p>''' + field('conclusion','선택한 모델과 근거','목적, 설정, 수치, 오류 사례, 남은 한계') + '''<div class="note">최종 확인: 코드의 FINAL_VALUE 설정 후 RUN_FINAL_TEST=True 변경. 최종 점수에 따른 재선택 시 별도 보관 자료 필요</div></section>''')

page('productivity','생산성',intro('PRODUCTIVITY','초안 이후의 작업','요청 작성·응답 대기·오류 수정·결과 검증의 시간 구성과 역할 분담') + '''
<section class="section"><h2>5문장 결과 보고서</h2>''' + copybox('productivity-prompt','실제 출력 기반 보고서','''실제 실행 결과:
[알고리즘, 설정, 기준 모델, 검증 지표, 오류 사례 붙여넣기]
요청: 5문장의 결과 보고서 작성
포함 사항: 알고리즘과 설정 / 기준 모델과의 비교 / 놓친 사례 / 해석의 한계
금지 사항: 미제공 수치 생성 / 관찰 관계의 인과관계 전환
정보 부족 시 확인 불가 항목의 명시''') + '''</section><section class="section"><h2>작업 시간</h2><div class="number-grid"><label class="field">요청 작성 · 분<input id="time-prompt" data-note="요청 작성 시간(분)" type="number" min="0" max="300" step="0.1" value="0"></label><label class="field">응답 대기 · 분<input id="time-wait" data-note="응답 대기 시간(분)" type="number" min="0" max="300" step="0.1" value="0"></label><label class="field">오류 수정 · 분<input id="time-fix" data-note="오류 수정 시간(분)" type="number" min="0" max="300" step="0.1" value="0"></label><label class="field">결과 검증 · 분<input id="time-check" data-note="결과 검증 시간(분)" type="number" min="0" max="300" step="0.1" value="0"></label></div><div class="metrics"><div class="metric"><strong id="time-total">0.0분</strong><span>전체 시간</span></div><div class="metric"><strong id="time-after">0.0분</strong><span>초안 이후 수정·검증 시간</span></div></div><p class="caption">중복 시간 제외. AI 미사용 조건과의 동일 작업 비교 없이는 생산성 향상 배수 산출 불가</p></section><section class="section"><h2>검증 항목</h2><ul class="checklist"><li><label><input type="checkbox" data-note="검증_수치">검증 대상 수와 정확도의 원본 출력 일치</label></li><li><label><input type="checkbox" data-note="검증_기준모델">기준 모델과의 비교 근거 확인</label></li><li><label><input type="checkbox" data-note="검증_놓침">누락 인원 수의 일치</label></li><li><label><input type="checkbox" data-note="검증_인과">인과관계로 확대된 표현의 제거</label></li></ul>''' + field('report_revision','수정 내용','초안 표현 / 원본 근거 / 수정 후 표현') + field('productivity_decision','다음 작업의 역할 분담','AI 위임 범위 / 직접 판단 범위 / 완료 기준') + '''</section><div class="evidence"><p>고객지원 현장 연구: 경험·숙련도에 따른 AI 보조 효과의 차이. 단일 직무의 결과를 다른 작업에 적용할 때의 범위 제한. <a href="https://doi.org/10.1093/qje/qjae044">Generative AI at Work, QJE (2025)</a></p></div>''')

page('education','교육학',intro('EDUCATION','수행과 학습의 구분','AI 도움 전 설명 · 도움 이후 독립 설명 · 새로운 상황으로의 적용') + '''
<section class="section"><h2>알고리즘의 독립 설명</h2>''' + field('before','AI 도움 전 설명','알고리즘의 판단 방식과 검증 오류의 발생 이유') + copybox('education-hint','질문과 힌트 중심의 점검','''학습자 설명:
[내 설명 붙여넣기]
요청 사항:
- 불분명한 부분을 확인하는 질문 1개 제시
- 학습자 응답 이후 피드백과 단계적 힌트 제공
- 완성된 설명과 정답의 선제 제공 금지
- 이해 여부의 확인 근거 제시''') + field('after','AI 대화 종료 후 재설명','인용 없이 자기 언어로 작성') + '''</section><section class="section"><h2>새 상황의 판단</h2><div class="panel"><h3>모델 A: 학습 100% · 검증 60%<br>모델 B: 학습 80% · 검증 80%</h3><p>동일한 검증 자료를 전제로 한 선택과 추가 확인 항목: 검증 대상 수, 기준 모델, 범주별 오류</p></div>''' + field('transfer','선택과 추가 확인 사항','AI 도움 없이 작성') + '''</section><section class="section"><h2>같은 정확도, 다른 오류</h2><p><span class="tag">교육용 가상 사례</span> 전체 20명: 10점 미만 6명 / 10점 이상 14명</p><div class="table-wrap"><table><thead><tr><th>모델</th><th>10점 미만 누락</th><th>10점 이상 오표시</th><th>10점 미만 재현율</th><th>정확도</th></tr></thead><tbody><tr><td>A</td><td>4명</td><td>0명</td><td>33.3%</td><td>80%</td></tr><tr><td>B</td><td>1명</td><td>3명</td><td>83.3%</td><td>80%</td></tr></tbody></table></div><fieldset><legend>상황 1 · 추가 상담 제안</legend><div class="radio-line"><label><input type="radio" name="counsel" value="A" data-note="counsel_choice">모델 A</label><label><input type="radio" name="counsel" value="B" data-note="counsel_choice">모델 B</label><label><input type="radio" name="counsel" value="모델만으로 선택 보류" data-note="counsel_choice">선택 보류</label></div></fieldset><fieldset><legend>상황 2 · 표시 결과에 따른 자동 불이익</legend><div class="radio-line"><label><input type="radio" name="penalty" value="A" data-note="penalty_choice">모델 A</label><label><input type="radio" name="penalty" value="B" data-note="penalty_choice">모델 B</label><label><input type="radio" name="penalty" value="모델만으로 선택 보류" data-note="penalty_choice">선택 보류</label></div></fieldset><p id="decision-feedback" class="decision-feedback" aria-live="polite" hidden></p>''' + field('education_reason','상황별 선택의 근거','오류의 영향, 사람의 확인, 이의 제기, 학생의 선택권') + '''<div class="note">성적 구간과 실제 지원 필요성의 구분. 사용 목적의 타당성과 모델 성능의 별도 검토</div></section><section class="section"><h2>관찰된 관계와 지원 효과</h2><p>추가 지원 집단의 낮은 성적 관찰 시 검토 항목: 지원 전 상태, 지원 대상 선정, 측정 시점, 비교 집단. 관측 자료와 모델 중요도만을 이용한 지원 효과의 인과 추론 불가</p>''' + field('policy','교육적 사용 원칙','모델의 제안 범위 / 사람의 확인 절차 / 허용 가능한 결정') + '''</section><div class="evidence"><p>고등학교 수학 연구: AI 보조 중 수행과 AI 없는 평가의 구분, 도움 방식에 따른 차이. 다른 과목·기간에 대한 일반화의 범위 제한. <a href="https://hamsabastani.github.io/education_llm.pdf">Bastani 외, Generative AI Without Guardrails Can Harm Learning (2025)</a></p></div>''')

page('notes','실험 기록',intro('RECORD','실험 기록','모형·설정·실측값·오류 사례·판단 근거. 브라우저 내 자동 저장 및 기록 파일 다운로드') + '<label class="field">알고리즘<select data-note="algorithm" aria-label="알고리즘"><option value="">선택</option>' + ''.join(f'<option>{a["name"]}</option>' for a in algorithms) + '</select></label>' + field('forecast','실행 전 예상') + field('observation','실제 결과와의 차이') + field('errorcase','오분류 사례','식별자, 정답, 예측, 오류 유형') + field('conclusion','선택과 근거') + field('unknown','추가 확인 사항') + '''<div class="actions"><button class="primary" type="button" data-export-notes>기록 다운로드 ↓</button><a class="button" href="results.html">결과 비교</a></div><p id="export-status" class="status" role="status"></p>''')
print(json.dumps({'pages':len(list(DEST.rglob('*.html'))),'algorithms':len(algorithms),'format':'copyable Python'},ensure_ascii=False))
