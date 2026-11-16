[실험 모음](https://learning-experiments-gc261103.incheon-seok-1409.chatgpt.site)

## 2026년 11월 17일 자료

[알고리즘](https://learning-experiments-gc261103.incheon-seok-1409.chatgpt.site/class/20261117/index.html)

- 알고리즘 5개: 실제 계산 기반 SVG 시각화, 4단계 재생, 설정·입력 위치 조절
- 실행 방식: 공통 CSV 다운로드 → 페이지의 전체 코드 복사 → Colab 코드 셀 실행 → CSV 선택
- 공개 자료 형식: CSV, 복사용 Python 코드, 결과 JSON. ipynb 파일 제외
- 공통 데이터: UCI Student Performance의 student-por.csv에서 입력 5개와 정답 생성, 고정 분할 추가
- 분할: 학습 389 / 검증 130 / 최종 보관 130. 기본 실행의 최종 보관 자료 평가 제외
- 원자료: Cortez (2008), https://doi.org/10.24432/C5TG7T · CC BY 4.0
- 기록과 결과 JSON의 브라우저 내 처리. 이름·학번·API 키 수집 없음

### 재생성 및 검증

Python 의존성: numpy, pandas, scikit-learn

```text
python scripts/build-colab-materials.py
python scripts/build-colab-pages.py
python scripts/check-colab-variants.py
node scripts/check.cjs
node --test test/*.test.mjs
node scripts/build-worker.cjs
```

첫 명령은 알고리즘별 전체 코드를 실행하고, 모의 Colab 파일 선택·다운로드 동작과 결과 수치를 확인합니다. 실제 코랩 계정 안에서의 실행과는 별도 검증입니다. 코드 복사 버튼의 내용은 .py 파일 및 단계별 코드와 동일합니다.

시각화는 원리 설명용 2차원 가상 자료를 사용하며 실제 CSV의 5개 입력과 구분합니다. SVM 시연은 RBF gamma=2, 코랩은 gamma=scale입니다. 랜덤포레스트 시연은 나무 5개, 코랩은 100개입니다. 설정 차이는 페이지에 표시합니다.

수치 테스트 범위: 로지스틱 회귀 로그손실, K-NN 이웃과 투표, CART 분기, 랜덤포레스트 복원추출과 투표, RBF SVM의 쌍대 제약 및 비선형 분류. UI 검증 범위: 단계 이동, 자동 재생, 감소 동작 설정, 입력 조절, 코드 복사, 모바일 레이아웃.

CSV 변경 시 manifest, 복사 코드의 SHA256, 참고 결과의 동시 갱신 필요. CSV 바이트 보존 및 Python LF 줄바꿈은 .gitattributes로 지정합니다.

페이지에는 기본 코드와 변경 변수·예시 값·관찰 항목만 제공합니다. 값의 수정과 실행은 코랩에서 직접 수행합니다. 결과 파일에 추가 설정을 기록하며 같은 알고리즘의 서로 다른 설정도 함께 비교합니다. 색은 #000000과 #ffffff만 사용하며 회색·투명도 혼합은 제외합니다. 상단 이름·소속·저장 상태 문구는 표시하지 않습니다.

설계 기준

환경 설정·반복 실행·표 생성·결과 전달의 부담을 줄이되, 실행 전 예상·조건 선택·오류 추적·독립 설명은 학생이 수행하도록 구성합니다. 생산성·교육학의 독립 페이지나 별도 토론 과제는 두지 않습니다. 각 알고리즘에 새로운 조건을 판단하는 짧은 적용 문항을 배치하고, 활동의 근거를 공통 기록 파일에 보존합니다.
