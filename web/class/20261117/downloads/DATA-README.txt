가천대학교 머신러닝 수업 · 2026-11-17

students-v1.csv: UCI Student Performance의 student-por.csv를 수업용으로 가공한 파일입니다.
출처: Cortez, P. (2008). Student Performance. UCI Machine Learning Repository. https://doi.org/10.24432/C5TG7T
라이선스: CC BY 4.0 https://creativecommons.org/licenses/by/4.0/
가공: 입력 5개 선택, G3<10인 below_10 정답 생성, 행 식별자 부여, 고정된 층화 분할 60/20/20.
G1·G2·G3 및 그 밖의 개인 배경 항목은 실습용 CSV의 입력에서 제외했습니다.
studytime: 주당 시간 구간 1=<2h / 2=2~5h / 3=5~10h / 4=>10h.
failures: 원자료의 과거 과목 실패 코드. 이번 실습에서는 범주로 처리합니다.
absences: 결석 횟수. 출석률이 아닙니다. schoolsup/internet: 원자료 yes/no 응답입니다.
row_id는 원자료의 행 번호에 기반한 수업용 식별자이며 실제 이름이 아닙니다.
split: train=389, validation=130, test=130. seed=42.
파일 SHA256: 5e01746d0128a964c31cb02597fc1176c182bd502c31a2f669aa8ab0f16de387

성적 10점 미만은 이번 분류의 정답 정의이며 실제 지원 필요성의 정답이 아닙니다.
자료의 관측 시점만으로 조기 예측이나 인과관계를 입증할 수 없습니다.
각 ipynb는 Colab에 업로드하고 위에서부터 실행합니다. GPU/API 키가 필요하지 않습니다.
공통 CSV가 노트북 안에 포함되어 있어 외부 주소에 접속하지 않고 실행됩니다.
같은 이름의 CSV를 직접 업로드하면 해당 파일을 먼저 읽고 SHA256으로 버전을 확인합니다.
노트북은 검증 자료를 비교에 사용하고, test는 기본 실행에서 평가하지 않습니다.
