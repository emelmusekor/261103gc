(function aiTools(){
const run=()=>{
const id=document.body.dataset.program,$=id=>document.getElementById(id),bridge=()=>window.LabBridge;
let mathImage=null,lastMath=null,poseImage=null,points={},dragging=null,photoRevision=0;
const element=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
function block(root,title,items){if(!items?.length)return;root.append(element('h4',title));const list=element('ul');for(const t of items)list.append(element('li',typeof t==='string'?t:JSON.stringify(t)));root.append(list)}
function status(root,text,bad=false){const node=root.querySelector('.ai-status');node.textContent=text;node.classList.toggle('is-error',bad)}
function resultNode(root){const output=root.querySelector('.ai-output');output.replaceChildren();return output}
function showObserved(root,value){root.querySelector('.observed-result')?.remove();let text='';if(value.result){const r=value.reading;text='실행한 분류: '+value.result+(r?' / 기울기 '+r.t.toFixed(1)+'°, 진동 '+r.v.toFixed(1)+', 고도 변화 '+r.a.toFixed(1):'')}else if(value.prediction){text='현재 추천: '+value.prediction+(value.x!==undefined?' / 좌표 ('+value.x+', '+value.y+')':'')+(value.added!==undefined?' / 추가한 사례 '+value.added+'개':'')}else if(value.draws){text='실제로 '+value.draws+'번 뽑아 빨간 공이 '+value.observed_red+'번 나왔습니다. 관측 비율은 '+(value.observed_red/value.draws*100).toFixed(1)+'%입니다.'}else text='조건을 적용했습니다.';root.append(element('p',text,'observed-result'));}
function applyButton(root,label,fn){const button=element('button',label);button.type='button';button.addEventListener('click',()=>{try{const result=fn();showObserved(root,result)}catch{root.append(element('p','조건을 적용하지 못했습니다. 입력값을 확인해 주세요.'))}});root.append(button)}
async function request(task,question,context,image){
const response=await fetch('/api/analyze',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({apiKey:window.LabAPI?.key()||"",task,question,context,...(image?{image}: {})})});let data;try{data=await response.json()}catch{throw Error('응답을 읽을 수 없습니다. 다시 시도해 주세요.')}if(!response.ok)throw Error(data.message||'분석하지 못했습니다. 다시 시도해 주세요.');return data.result;
}
async function normalizedImage(source){
const objectURL=source instanceof File?URL.createObjectURL(source):null;
try{
if(source instanceof File&&(!/^image\/(?:png|jpeg|webp)$/.test(source.type)||source.size>10*1024*1024))throw Error('PNG·JPG·WebP 사진 10MB 이하를 선택해 주세요.');
const img=await new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=()=>reject(Error('사진을 읽을 수 없습니다.'));img.src=objectURL||source});
if(img.width*img.height>40000000)throw Error('사진 해상도를 줄여 다시 선택해 주세요.');
const scale=Math.min(1,1280/Math.max(img.width,img.height)),width=Math.max(1,Math.round(img.width*scale)),height=Math.max(1,Math.round(img.height*scale)),c=document.createElement('canvas');c.width=width;c.height=height;const x=c.getContext('2d');x.fillStyle='white';x.fillRect(0,0,width,height);x.drawImage(img,0,0,width,height);return {data:c.toDataURL('image/jpeg',.88),width,height};
}finally{if(objectURL)URL.revokeObjectURL(objectURL)}
}
function mathRender(root,result){
const out=resultNode(root);out.append(element('h3',result.conclusion),element('p',result.answer,'math-final'));const steps=element('ol');for(const step of result.steps){const li=element('li');li.append(element('strong',step.title),element('p',step.detail));steps.append(li)}out.append(steps,element('h4','다른 방법으로 확인'),element('p',result.verification));block(out,'이어 생각할 질문',result.questions);lastMath=result;bridge()?.record?.($('mathQuestion')?.value||'',result.answer);
}
function renderHistory(result){
const answer=$('answer');answer.replaceChildren();for(const p of result.paragraphs){const line=element('p',p.text);const refs=element('span',undefined,'ai-citations');for(const source of p.source_ids){const b=element('button',source);b.type='button';b.title='근거 사료 '+source;b.onclick=()=>{$('src-'+source)?.scrollIntoView({behavior:'smooth',block:'center'});$('src-'+source)?.focus()};refs.append(b)}line.append(refs);answer.append(line)}const out=$('historyOutput');out.replaceChildren(element('h3',result.title));block(out,'자료에서 확인할 빈자리',result.missing_questions);out.append(element('p',result.next_question));
}
function renderFashion(root,r){const out=resultNode(root);out.append(element('h3',r.name));block(out,'사진에서 확인한 형태',r.observations.map(o=>o.feature+' — '+o.observation));block(out,'함께 살펴볼 후보',r.alternatives.map(a=>a.name+' — '+a.reason));block(out,'사진만으로 확인하기 어려운 점',r.unknowns);block(out,'패턴을 살펴볼 때',r.pattern_suggestions);}
function drawPose(){
if(!poseImage)return;const svg=$('posePhoto'),ns='http://www.w3.org/2000/svg';svg.removeAttribute('hidden');svg.setAttribute('viewBox',`0 0 ${poseImage.width} ${poseImage.height}`);svg.replaceChildren();const image=document.createElementNS(ns,'image');image.setAttribute('href',poseImage.data);image.setAttribute('width',poseImage.width);image.setAttribute('height',poseImage.height);svg.append(image);
const labels={hip:'엉덩이',knee:'무릎',ankle:'발목'};
for(const name of ['hip','knee','ankle']){
const point=points[name];if(!point?.visible)continue;const x=point.x*poseImage.width,y=point.y*poseImage.height,circle=document.createElementNS(ns,'circle');circle.setAttribute('cx',x);circle.setAttribute('cy',y);circle.setAttribute('r',Math.max(8,poseImage.width*.016));circle.setAttribute('fill',name===$('posePoint').value?'#bd6b31':'#176e68');circle.setAttribute('stroke','#fff');circle.setAttribute('stroke-width',Math.max(2,poseImage.width*.003));circle.dataset.point=name;svg.append(circle);const text=document.createElementNS(ns,'text');text.textContent=labels[name];text.setAttribute('x',Math.min(poseImage.width-60,x+poseImage.width*.02));text.setAttribute('y',Math.max(20,y-10));text.setAttribute('fill','#fff');text.setAttribute('stroke','#222');text.setAttribute('stroke-width','0.7');text.setAttribute('paint-order','stroke');text.setAttribute('font-size',Math.max(16,poseImage.width*.025));svg.append(text);}
const [a,b,c]=['hip','knee','ankle'].map(n=>points[n]);const out=$('poseMeasuredAngle');if(a?.visible&&b?.visible&&c?.visible){const u=[(a.x-b.x)*poseImage.width,(a.y-b.y)*poseImage.height],v=[(c.x-b.x)*poseImage.width,(c.y-b.y)*poseImage.height],den=Math.hypot(...u)*Math.hypot(...v);out.textContent=den?'사진의 관절 점으로 계산한 각도: '+(Math.acos(Math.max(-1,Math.min(1,(u[0]*v[0]+u[1]*v[1])/den)))*180/Math.PI).toFixed(1)+'°':'서로 다른 관절 위치를 선택해 주세요.';}else out.textContent='세 관절의 위치를 확인하면 사진 속 각도를 계산합니다.';
$('posePointControls').hidden=false;
}
function renderPose(root,r){points=Object.fromEntries(r.landmarks.map(p=>[p.name,{...p}]));drawPose();const out=resultNode(root);out.append(element('h3',r.summary));block(out,'사진에서 관찰한 점',r.observations);block(out,'확인할 질문',r.questions);}
function renderDrill(root,r,type){
const out=resultNode(root);out.append(element('h3',r.summary));block(out,'실제 기록에서 확인한 근거',r.evidence);block(out,type==='drone'?'다른 가능한 설명':'해석할 때 확인할 점',r.alternatives||r.limits);out.append(element('h4','다음에 해볼 조건'));
const labels=type==='drone'?{tilt:'기울기',vibration:'진동',altitude:'고도 변화',noise:'노이즈',bias:'편향',k:'이웃 수',distance:'거리 방식',failure:'고장 조건'}:{red:'실제 주머니 빨간 공',other_red:'비교 주머니 빨간 공',n:'관찰 기록 수',trials:'반복 수'};
const list=element('dl',undefined,'experiment-values');for(const [key,value]of Object.entries(r.experiment)){list.append(element('dt',labels[key]),element('dd',String(value)))}out.append(list,element('p',r.question));applyButton(out,'이 조건으로 새 실험',()=>bridge().apply(r.experiment));
}
function renderCareer(root,r){
const out=resultNode(root);out.append(element('h3',r.summary));block(out,'활동에서 읽은 근거',r.evidence.map(e=>'“'+e.quote+'” — '+e.interpretation));const row=element('div',undefined,'ai-actions');
const x=element('input'),y=element('input');for(const [el,value,label]of [[x,r.x,'탐구·분석'],[y,r.y,'협력·소통']]){el.type='number';el.min='0';el.max='100';el.value=value;el.setAttribute('aria-label',label);const lab=element('label',label+' ');lab.append(el);row.append(lab)}out.append(row);applyButton(out,'확인한 좌표로 탐구',()=>{if(!x.value.trim()||!y.value.trim()||![+x.value,+y.value].every(v=>Number.isFinite(v)&&v>=0&&v<=100))throw Error();return bridge().applyProfile({x:+x.value,y:+y.value})});out.append(element('h4','데이터 구성을 바꾸어 보기'),element('p',r.question),element('p',`추가할 사례 (${r.experiment.x}, ${r.experiment.y}) · ${r.experiment.label===0?'탐구형':'협력형'}`));applyButton(out,'이 사례를 추가해 비교',()=>bridge().add(r.experiment));
}
async function perform(action,button){
const type=action==='mathCheck'?'math':action,root=$(type==='pose'?'poseAI':type),buttons=[...root.querySelectorAll('[data-ai-action]')];let context=bridge()?.context?.()||{},question=$(type+'Question')?.value.trim()||'',image=null,task;
try{
if(type==='history'){task='history.write';if(!context.sources?.length)throw Error('사료를 하나 이상 선택해 주세요.');if(!question)question='선택한 사료의 관점과 사건의 원인을 설명해 줘.';}
if(type==='math'){task=action==='mathCheck'?'math.check':'math.solve';const work=$('mathWork').value.trim();if(!question&&!mathImage)throw Error('문제나 사진을 먼저 입력해 주세요.');if(action==='mathCheck'&&!work&&!lastMath)throw Error('확인할 풀이를 적거나 먼저 문제를 풀어 보세요.');context={...context,work,previous_solution:action==='mathCheck'&&!work?lastMath:null};image=mathImage?.data;}
if(type==='fashion'){task='fashion.analyze';if(window.GarmentPhoto)image=(await normalizedImage(window.GarmentPhoto)).data;else{const c=bridge().canvas(),pixels=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let count=0;for(let i=3;i<pixels.length;i+=4)if(pixels[i]>40)count++;if(count<120)throw Error('사진을 올리거나 실루엣을 먼저 그려 주세요.');image=(await normalizedImage(c.toDataURL())).data;}question=question||'이 의복의 형태와 구별할 특징을 분석해 줘.';}
if(type==='pose'){task='pose.analyze';if(!poseImage)throw Error('운동 사진을 먼저 선택해 주세요.');image=poseImage.data;context={...context,image_width:poseImage.width,image_height:poseImage.height};question=question||'이 사진의 관절과 촬영 조건을 분석해 줘.';}
if(type==='drone'){task='drone.investigate';question=question||'현재 센서와 이웃의 결과를 분석하고 한 가지 조건을 바꾸어 검증할 실험을 제안해 줘.';}
if(type==='probability'){task='probability.investigate';question=question||'실험 기록을 해석하고 자료 출처와 표본 수의 차이를 확인할 다음 실험을 제안해 줘.';}
if(type==='career'){task='career.explore';if(question.length<5)throw Error('관심 활동을 조금 더 구체적으로 적어 주세요.');}
buttons.forEach(b=>b.disabled=true);status(root,'분석하고 있습니다…');root.setAttribute('aria-busy','true');const revision=photoRevision,key=JSON.stringify(context),result=await request(task,question,context,image);
if(type==='history'&&JSON.stringify(bridge().context())!==key)throw Error('사료 선택이 바뀌었습니다. 현재 사료로 다시 서술해 주세요.');
if(type==='pose'&&revision!==photoRevision)throw Error('사진이 바뀌었습니다. 새 사진으로 다시 분석해 주세요.');
if(type==='history')renderHistory(result);if(type==='math')mathRender(root,result);if(type==='fashion')renderFashion(root,result);if(type==='pose')renderPose(root,result);if(type==='drone'||type==='probability')renderDrill(root,result,type);if(type==='career')renderCareer(root,result);
status(root,'분석을 마쳤습니다.');
}catch(e){status(root,e.message||'분석하지 못했습니다. 다시 시도해 주세요.',true)}
finally{buttons.forEach(b=>b.disabled=false);root?.removeAttribute('aria-busy')}
}
document.querySelectorAll('[data-ai-action]').forEach(button=>button.addEventListener('click',()=>perform(button.dataset.aiAction,button)));
if(id==='math'){
$('mathImage').addEventListener('change',async e=>{try{if(!e.target.files[0])return;mathImage=await normalizedImage(e.target.files[0]);$('mathPreview').src=mathImage.data;$('mathPreview').hidden=false;status($('math'),'사진을 선택했습니다.')}catch(e){status($('math'),e.message,true)}});
$('interpret').onclick=async()=>{const button=$('interpret');button.disabled=true;$('promptResult').textContent='문장을 읽고 있습니다…';try{const question=$('wording').selectedOptions[0].textContent;const r=await request('math.solve',question,{...bridge().context(),wording:$('wording').value});$('promptResult').replaceChildren(element('strong',r.answer),...r.steps.map(s=>element('p',s.detail)));bridge().record(question,r.answer)}catch(e){$('promptResult').textContent=e.message}finally{button.disabled=false}};
}
if(id==='pose'){
$('poseSimulation').onclick=()=>bridge().photoMode(false);$('posePhotograph').onclick=()=>bridge().photoMode(true);
$('poseImage').addEventListener('change',async e=>{try{if(!e.target.files[0])return;poseImage=await normalizedImage(e.target.files[0]);photoRevision++;points={};drawPose();status($('poseAI'),'사진을 선택했습니다. 관절 찾기를 눌러 보세요.')}catch(e){status($('poseAI'),e.message,true)}});
$('posePoint').onchange=drawPose;
const svg=$('posePhoto');
function move(e,name){const pt=svg.createSVGPoint();pt.x=e.clientX;pt.y=e.clientY;const p=pt.matrixTransform(svg.getScreenCTM().inverse());points[name]={name,x:Math.max(0,Math.min(1,p.x/poseImage.width)),y:Math.max(0,Math.min(1,p.y/poseImage.height)),visible:true};drawPose();}
svg.addEventListener('pointerdown',e=>{if(!poseImage)return;e.preventDefault();dragging=e.target.dataset.point||$('posePoint').value;$('posePoint').value=dragging;svg.setPointerCapture(e.pointerId);move(e,dragging)});svg.addEventListener('pointermove',e=>{if(dragging)move(e,dragging)});svg.addEventListener('pointerup',()=>dragging=null);svg.addEventListener('pointercancel',()=>dragging=null);
}
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{once:true});else run();
})();