ML 실험 데이터와 실행 코드 · 2026-11-17

students-v1.csv: UCI student-por.csv의 열 선택, 정답 생성, 식별자 및 고정 분할 추가
Cortez, P. (2008). Student Performance. UCI Machine Learning Repository. https://doi.org/10.24432/C5TG7T
라이선스: CC BY 4.0 https://creativecommons.org/licenses/by/4.0/
입력: studytime, failures, absences, schoolsup, internet
정답: G3<10이면 below_10=1, 그 외 0
분할: train 389 / validation 130 / test 130. 초기값 42
studytime: 주당 시간 구간 1=<2h / 2=2~5h / 3=5~10h / 4=>10h
failures: 과거 과목 실패 코드. 범주 처리
absences: 결석 횟수
schoolsup/internet: yes/no 응답
row_id와 split: 모델 입력 제외
SHA256: 5e01746d0128a964c31cb02597fc1176c182bd502c31a2f669aa8ab0f16de387

실행: 알고리즘 페이지의 전체 코드 복사 > Colab 코드 셀에 붙여넣기 > 실행 > students-v1.csv 선택
실행 환경: 기본 CPU. GPU 및 API 키 불필요
CSV 버전 검증 후 동일한 학습·검증 분할 적용
최종 보관 자료: 기본 실행에서 평가 제외. 조건 확정 후 별도 확인
성적 구간 분류와 실제 지원 필요성의 구분. 관측 자료만으로 인과 효과 추론 불가
