(()=>{
const start=()=>{const id=document.body.dataset.program,content={
history:['선택한 사료의 내용과 관점','Gemini가 선택한 기록을 바탕으로 서술을 생성합니다. 화면의 관점 지표는 미리 정한 사료 분류로 계산합니다.','출처 선택이 만든 편향·주장과 근거의 대응','선택 사료를 바꿔 같은 질문을 다시 하고 문장별 근거를 대조하세요.'],
fashion:['윤곽의 폭·길이·다리 분기 같은 형태 특성','윤곽 판별은 사람이 정한 특징과 도감 규칙을 사용합니다. Gemini는 업로드한 이미지나 스케치에서 관찰 근거를 설명합니다.','특징 설계와 학습된 이미지 모델의 차이','한 부분만 바꾼 뒤 어떤 특성과 후보가 달라지는지 비교하세요.'],
math:['문제의 조건·표현·수학 기호와 풀이','Gemini가 풀이를 생성합니다. 계산 실험실과 역산 도구는 정해진 수학 규칙으로 계산합니다.','그럴듯한 생성 결과와 검증 가능한 정답의 차이','같은 문제를 다른 방법으로 검산하고 조건이 빠졌을 때 답을 단정하는지 확인하세요.'],
pose:['사진에서 보이는 관절과 촬영 조건','Gemini가 사진의 관절 후보를 찾고, 브라우저가 2차원 점의 각도를 계산합니다. 촬영 조건 실험의 점수는 규칙으로 만든 시뮬레이션입니다.','예측 좌표의 오차와 실제 측정값의 차이','관절 점을 직접 고치고 촬영 방향을 바꾸어 계산된 각도가 얼마나 달라지는지 비교하세요.'],
drone:['기울기·진동·고도 변화의 세 수치와 상태 레이블','K-NN이 가까운 학습 사례의 다수결로 분류합니다. Gemini는 실제 계산값과 검증 결과를 해석합니다.','특성의 단위·이웃 수·자료 분리와 일반화','고정한 검증 자료에서 K와 학습 레이블만 바꿔 오분류와 유형별 재현율을 비교하세요.'],
probability:['복원추출의 빨간 공 관측 기록과 자료 출처','관찰 빈도로 확률을 추정하는 기초 통계 모델입니다. Gemini가 실제 관측과 예측의 차이를 해석합니다.','표본 변동과 다른 분포에서 가져온 데이터의 편향','같은 초기값에서 표본 수와 자료 출처를 따로 바꾸어 오차가 줄어드는지 확인하세요.'],
career:['탐구·분석과 협력·소통 두 좌표 및 유형 레이블','K-NN이 가까운 사례의 다수결로 분류합니다. Gemini가 활동 글을 잠정적인 좌표로 옮기거나 검증 결과를 해석합니다.','특징 선택·레이블 오류·검증 자료를 통한 일반화','학습과 검증 자료를 나눈 뒤 한 유형의 학습 사례를 제외해 어떤 오분류가 생기는지 확인하세요.']
}[id];if(!content)return;const d=document.createElement('details');d.className='ml-model-note';d.id='modelLearningNote';const s=document.createElement('summary');s.textContent='모델이 보는 것, 사람이 확인할 것';d.append(s);const dl=document.createElement('dl');['입력 특성','예측과 계산','핵심 개념','검증할 실험'].forEach((title,i)=>{const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=title;dd.textContent=content[i];dl.append(dt,dd)});d.append(dl);document.getElementById('investigationStart')?.after(d)};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();