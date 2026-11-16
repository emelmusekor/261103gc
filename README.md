[실험 모음](https://learning-experiments-gc261103.incheon-seok-1409.chatgpt.site)

## 2026년 11월 17일 수업

[수업 자료](https://learning-experiments-gc261103.incheon-seok-1409.chatgpt.site/class/20261117/index.html)에는 공통 데이터, 알고리즘별 코랩 실습 5개, 결과 비교, 생산성, 교육학, 개인 기록 페이지가 있습니다. 공지문과 시간표는 포함하지 않습니다.

- `web/class/20261117/downloads/lesson-kit.zip`: CSV·노트북·출처 설명 묶음.
- `students-v1.csv`: UCI Student Performance의 포르투갈어 과목 자료를 가공한 공통 파일. 원자료 출처와 CC BY 4.0 표기는 데이터 페이지와 DATA-README.txt에 있습니다.
- 학습 389명 / 검증 130명 / 보관 130명으로 고정했습니다. 노트북 기본 실행은 보관 자료를 평가하지 않습니다.
- 기록은 브라우저에만 저장하며, 결과 JSON도 브라우저에서만 읽습니다. 이름·학번·API 키를 수집하지 않습니다.

### 자료를 다시 만들고 확인하기

Python에 numpy, pandas, scikit-learn이 필요합니다. 노트북의 초기 뼈대는 설치된 jupyter-notebook 도구를 사용합니다.

```text
python scripts/build-colab-materials.py
python scripts/build-colab-pages.py
node scripts/check.cjs
node --test test/*.test.mjs
node scripts/build-worker.cjs
```

첫 단계는 원자료를 내려받아 버전과 고정 분할을 만들고, 노트북 5개의 모든 코드 셀을 순서대로 실행합니다. 이미 받은 원자료가 있으면 재사용합니다. 배포 파일에 실행 출력은 넣지 않으며 실제 실행으로 확인한 값은 reference-*.json과 verification.json에 둡니다. 코랩 자체에서 로그인하여 실행한 검증과 로컬 Python 검증은 구분합니다.

검증 지표와 입력 조건을 바꾸면 기존 결과와 바로 비교할 수 없습니다. CSV 바이트를 변경했다면 manifest와 노트북의 SHA256도 함께 갱신해야 합니다. CSV에 대한 Git 줄바꿈 변환은 .gitattributes에서 차단합니다.
