(function(){
'use strict';
const KEY='gc-20261117-v1-notes';
let notes={};
let storageOK=true;
try{notes=JSON.parse(localStorage.getItem(KEY)||'{}');if(!notes||typeof notes!=='object'||Array.isArray(notes))notes={};}catch{storageOK=false;}
function save(){try{localStorage.setItem(KEY,JSON.stringify(notes));}catch{storageOK=false;}}
function message(element,text,error=false){if(!element)return;element.textContent=text;element.classList.toggle('error',error);}
document.querySelectorAll('[data-note]').forEach(input=>{
const id=input.dataset.note;
if(Object.hasOwn(notes,id)){if(input.type==='checkbox')input.checked=Boolean(notes[id]);else if(input.type==='radio')input.checked=notes[id]===input.value;else input.value=String(notes[id]);}
input.addEventListener('input',()=>{if(input.type==='radio'&&!input.checked)return;notes[id]=input.type==='checkbox'?input.checked:input.value;save();});
});
document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{
const target=document.getElementById(button.dataset.copy);if(!target)return;
try{await navigator.clipboard.writeText(target.textContent);button.textContent='복사 완료';}
catch{const area=document.createElement('textarea');area.value=target.textContent;document.body.append(area);area.select();const ok=document.execCommand('copy');area.remove();button.textContent=ok?'복사 완료':'본문 선택 후 복사 필요';}
setTimeout(()=>button.textContent=button.dataset.copyLabel||'프롬프트 복사',2500);
}));
function download(filename,content,type='text/plain;charset=utf-8'){const url=URL.createObjectURL(new Blob([content],{type}));const a=document.createElement('a');a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
document.querySelectorAll('[data-export-notes]').forEach(button=>button.addEventListener('click',()=>{
const labels={algorithm:'내 알고리즘',forecast:'실행 전 예상',observation:'예상과 실제의 차이',errorcase:'틀린 사례와 근거',conclusion:'나의 모델 선택과 이유',before:'AI 도움 전 설명',after:'AI를 닫고 다시 쓴 설명',transfer:'새 문제에 대한 내 답',policy:'교육적 사용 원칙',report_revision:'AI 초안에서 내가 수정한 내용',productivity_decision:'다음 작업의 역할 분담',unknown:'여전히 모르는 점',counsel_choice:'상담 상황의 선택',penalty_choice:'자동 불이익 상황의 선택',education_reason:'두 상황에서 선택한 이유'};
const lines=['# 11월 17일 · 실험 기록','','실측값과 작성자의 관찰·판단 기록',''];
for(const [key,value]of Object.entries(notes)){if(value===''||value===false)continue;lines.push('## '+(labels[key]||key),String(value),'');}
download('my-ml-learning-notes.md',lines.join('\n'));message(document.getElementById('export-status'),'기록 파일 다운로드 완료');
}));
if(document.getElementById('time-total')){
const ids=['time-prompt','time-wait','time-fix','time-check'];
function updateTime(){const values=ids.map(id=>Math.max(0,Number(document.getElementById(id).value)||0));const total=values.reduce((a,b)=>a+b,0);const after=values[2]+values[3];document.getElementById('time-total').textContent=total.toFixed(1)+'분';document.getElementById('time-after').textContent=after.toFixed(1)+'분';
notes['소요 시간 합계']=total.toFixed(1)+'분';notes['초안 이후 수정·검증 시간']=after.toFixed(1)+'분';}
ids.forEach(id=>document.getElementById(id).addEventListener('input',updateTime));updateTime();
}
document.querySelectorAll('[name=counsel],[name=penalty]').forEach(radio=>radio.addEventListener('change',()=>{
const counsel=document.querySelector('[name=counsel]:checked')?.value;
const penalty=document.querySelector('[name=penalty]:checked')?.value;
const out=document.getElementById('decision-feedback');
if(counsel&&penalty){out.hidden=false;out.textContent=counsel===penalty?'두 상황의 동일 선택. 오류의 영향과 별도 확인 절차의 필요성 검토':'상황별 상이한 선택. 목적과 오류의 영향에 따른 판단 기준 비교';}
}));
const fileInput=document.getElementById('result-files');
if(fileInput){
let reports=[];let manifest;
const out=document.getElementById('result-status');
const table=document.getElementById('results-body');
const pct=value=>(100*value).toFixed(1)+'%';
const close=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<1e-8;
function checkMetrics(m){
if(!m||!['n','tn','fp','fn','tp','missed_below_10','false_flags'].every(k=>Number.isInteger(m[k])&&m[k]>=0))throw Error('오류 유형별 인원 수 형식 오류');
if(m.n!==130||m.tn+m.fp!==110||m.fn+m.tp!==20||m.missed_below_10!==m.fn||m.false_flags!==m.fp)throw Error('검증 대상 또는 오류 인원 수 불일치');
if(!close(m.accuracy,(m.tn+m.tp)/m.n)||!close(m.recall_below_10,m.tp/20)||!close(m.recall_at_least_10,m.tn/110)||!close(m.balanced_accuracy,(m.tp/20+m.tn/110)/2))throw Error('점수와 오류 인원 수 불일치');
}
function validate(r){
if(r.schema_version!==1||r.scope!=='validation'||r.dataset_sha256!==manifest.sha256||r.data_version!==manifest.version||r.split_id!==manifest.split_id)throw Error('데이터 버전 또는 비교 대상 불일치');
if(JSON.stringify(r.features)!==JSON.stringify(manifest.features)||!Array.isArray(r.validation_row_ids)||JSON.stringify([...r.validation_row_ids].sort())!==JSON.stringify([...manifest.validation_row_ids].sort()))throw Error('공통 입력 또는 검증 대상 불일치');
if(!manifest.algorithms.some(a=>a.id===r.algorithm)||!Array.isArray(r.runs)||!r.runs.length||r.runs.length>50||!Array.isArray(r.stress)||r.stress.length!==3)throw Error('실행 결과 형식 불일치');
const spec=manifest.algorithms.find(a=>a.id===r.algorithm);
function validValue(value){if(['tree','forest'].includes(r.algorithm)&&value===null)return true;return Number.isFinite(value)&&value>0&&(['tree','forest','knn'].includes(r.algorithm)?Number.isInteger(value):true);}
if(!r.runs.every(m=>m.parameter===spec.parameter&&validValue(m.value)&&Number.isFinite(m.train_accuracy)&&m.train_accuracy>=0&&m.train_accuracy<=1))throw Error('실험 설정 형식 오류');
if(r.configuration!==undefined){const c=r.configuration;if(!c||typeof c.model_options!=='object'||!c.model_options||Array.isArray(c.model_options)||JSON.stringify(c).length>2000)throw Error('추가 설정 형식 오류');if(r.algorithm==='logistic'&&!(typeof c.prediction_threshold==='number'&&c.prediction_threshold>0&&c.prediction_threshold<1))throw Error('분류 기준값 범위 오류');}
for(const metrics of [r.baseline,r.selected_metrics,...r.runs,...r.stress])checkMetrics(metrics);
if(r.baseline.tn!==110||r.baseline.fp!==0||r.baseline.fn!==20||r.baseline.tp!==0)throw Error('공통 기준 모델 결과 불일치');
if(!r.runs.some(m=>m.value===r.selected_value&&close(m.accuracy,r.selected_metrics.accuracy)&&m.fn===r.selected_metrics.fn&&m.fp===r.selected_metrics.fp))throw Error('선택 설정과 표시 점수 불일치');
return r;
}
function cell(row,text){const td=document.createElement('td');td.textContent=String(text);row.append(td);}
function configText(r){if(!r.configuration)return '추가 설정 미기록';const options=Object.entries(r.configuration.model_options).map(([key,value])=>key+'='+JSON.stringify(value));if(r.algorithm==='logistic')options.push('threshold='+r.configuration.prediction_threshold);return options.join(' / ');}
function experimentKey(r){const options=r.configuration?Object.entries(r.configuration.model_options).sort(([a],[b])=>a.localeCompare(b)):null;return JSON.stringify([r.algorithm,r.runs.map(m=>m.value),options,r.configuration?.prediction_threshold??null]);}
function render(){
table.replaceChildren();document.getElementById('result-empty').hidden=reports.length>0;document.getElementById('result-table').hidden=!reports.length;
for(const r of reports){const spec=manifest.algorithms.find(a=>a.id===r.algorithm);for(const run of r.runs){const tr=document.createElement('tr');cell(tr,spec.name);cell(tr,run.parameter+'='+String(run.value));cell(tr,configText(r));cell(tr,pct(run.train_accuracy));cell(tr,pct(run.accuracy));cell(tr,pct(run.recall_below_10));cell(tr,run.fn+' / 20명');cell(tr,run.fp+' / 110명');table.append(tr);}}
document.getElementById('result-count').textContent=reports.length+'개 실험 · '+new Set(reports.map(r=>r.algorithm)).size+'개 알고리즘 · '+reports.reduce((sum,r)=>sum+r.runs.length,0)+'개 설정';
}
fetch('downloads/manifest.json').then(response=>{if(!response.ok)throw Error('공통 자료 정보 로드 실패');return response.json();}).then(value=>{manifest=value;fileInput.disabled=false;message(out,'result-*.json 선택 · 복수 파일 추가 가능');}).catch(error=>message(out,error.message,true));
fileInput.addEventListener('change',async()=>{
const errors=[];let added=0;
for(const file of fileInput.files){try{if(file.size>1000000)throw Error('파일 크기 제한: 1MB 이하');const result=validate(JSON.parse(await file.text()));const key=experimentKey(result);reports=reports.filter(r=>experimentKey(r)!==key);reports.push(result);added++;}catch(error){errors.push(file.name+': '+error.message);}}
render();message(out,(added?added+'개 결과 등록 완료 · 동일 설정의 마지막 파일 적용 ':'')+errors.join(' / '),errors.length>0);fileInput.value='';
});
document.getElementById('export-comparison').addEventListener('click',()=>{if(!reports.length){message(out,'결과 파일 선택 필요',true);return;}download('comparison-results.json',JSON.stringify({data_version:manifest.version,scope:'validation',reports},null,2),'application/json');});
}
})();
