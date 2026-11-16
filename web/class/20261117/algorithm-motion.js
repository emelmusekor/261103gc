(function(global){
'use strict';

// All displayed predictions below come from these small, deterministic models.
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const sigmoid=x=>x>=0?1/(1+Math.exp(-x)):Math.exp(x)/(1+Math.exp(x));
const distance2=(a,b)=>(a.x-b.x)**2+(a.y-b.y)**2;
function random(seed){let state=seed>>>0;return()=>{state=(1664525*state+1013904223)>>>0;return state/4294967296;};}
function dataset(){const rng=random(261117),points=[];for(let label=0;label<2;label++)for(let i=0;i<14;i++)points.push({x:clamp((label?.40:-.40)+(rng()-.5)*.95,-.93,.93),y:clamp((label?.34:-.34)+(rng()-.5)*.95,-.93,.93),label,id:points.length});for(const [x,y,label]of [[-.65,.55,0],[.58,-.58,1],[-.12,.28,0],[.20,-.12,1]])points.push({x,y,label,id:points.length});return points;}
function logisticTrain(points,C=1,iterations=1200){
let w=[0,0],b=0;const lambda=1/(C*points.length),learningRate=.35,history=[];
for(let iteration=0;iteration<iterations;iteration++){let gx=lambda*w[0],gy=lambda*w[1],gb=0;for(const p of points){const error=sigmoid(w[0]*p.x+w[1]*p.y+b)-p.label;gx+=error*p.x/points.length;gy+=error*p.y/points.length;gb+=error/points.length;}w=[w[0]-learningRate*gx,w[1]-learningRate*gy];b-=learningRate*gb;if(iteration%100===0)history.push({w:[...w],b});}
const score=p=>w[0]*p.x+w[1]*p.y+b;
const loss=-points.reduce((sum,p)=>{const prediction=clamp(sigmoid(score(p)),1e-12,1-1e-12);return sum+p.label*Math.log(prediction)+(1-p.label)*Math.log(1-prediction);},0)/points.length;
return{w,b,C,loss,history,score,probability:p=>sigmoid(score(p)),predict:p=>score(p)>=0?1:0};
}
const counts=points=>[points.filter(p=>p.label===0).length,points.filter(p=>p.label===1).length];
const impurity=points=>{if(!points.length)return 0;const c=counts(points);return 1-(c[0]/points.length)**2-(c[1]/points.length)**2;};
function cartTrain(points,maxDepth=4,rng=null){
function grow(sample,depth){const totals=counts(sample),node={depth,n:sample.length,counts:totals,prediction:totals[1]>totals[0]?1:0,leaf:true};if(depth>=maxDepth||!totals[0]||!totals[1]||sample.length<2)return node;
let best=null;const dimensions=rng?[rng()<.5?'x':'y']:['x','y'];
for(const feature of dimensions){const values=[...new Set(sample.map(p=>p[feature]))].sort((a,b)=>a-b);for(let k=0;k<values.length-1;k++){const threshold=(values[k]+values[k+1])/2,left=sample.filter(p=>p[feature]<=threshold),right=sample.filter(p=>p[feature]>threshold);const score=(left.length*impurity(left)+right.length*impurity(right))/sample.length;if(!best||score<best.score-1e-12)best={feature,threshold,left,right,score};}}
if(!best||impurity(sample)-best.score<1e-10)return node;
return{...node,leaf:false,feature:best.feature,threshold:best.threshold,gain:impurity(sample)-best.score,left:grow(best.left,depth+1),right:grow(best.right,depth+1)};
}return grow(points,0);
}
function treePath(tree,point){const path=[];let node=tree;while(!node.leaf){const direction=point[node.feature]<=node.threshold?'left':'right';path.push({node,direction});node=node[direction];}return{path,leaf:node,prediction:node.prediction};}
const predictTree=(tree,point)=>treePath(tree,point).prediction;
function forestTrain(points,maxDepth=4,seed=42,size=5){const rng=random(seed),trees=[],samples=[];for(let i=0;i<size;i++){const sample=Array.from({length:points.length},()=>points[Math.floor(rng()*points.length)]);samples.push(sample);trees.push(cartTrain(sample,maxDepth,rng));}return{trees,samples,maxDepth};}
function forestVote(model,point){const votes=model.trees.map(tree=>predictTree(tree,point)),one=votes.reduce((a,b)=>a+b,0);return{votes,zero:votes.length-one,one,prediction:one>votes.length/2?1:0};}
function knn(points,point,k=5){const neighbors=points.map((p,index)=>({...p,index,distance:Math.sqrt(distance2(p,point))})).sort((a,b)=>a.distance-b.distance||a.index-b.index).slice(0,Math.min(k,points.length));const one=neighbors.reduce((sum,p)=>sum+p.label,0);return{neighbors,one,zero:neighbors.length-one,prediction:one>neighbors.length/2?1:0};}
function svmTrain(points,C=1,gamma=2){
// Pairwise dual-coordinate optimization (SMO); labels are transformed to -1/+1.
const n=points.length,y=points.map(p=>p.label?1:-1),alpha=Array(n).fill(0),K=points.map(a=>points.map(b=>Math.exp(-gamma*distance2(a,b))));let b=0,passes=0,iterations=0;
const trainScore=i=>alpha.reduce((sum,a,j)=>sum+a*y[j]*K[j][i],b);
while(passes<12&&iterations<1800){let changed=0;iterations++;
for(let i=0;i<n;i++){const Ei=trainScore(i)-y[i];if(!((y[i]*Ei<-.001&&alpha[i]<C-1e-8)||(y[i]*Ei>.001&&alpha[i]>1e-8)))continue;
const candidates=Array.from({length:n},(_,j)=>({j,E:trainScore(j)-y[j]})).filter(v=>v.j!==i).sort((a,z)=>Math.abs(Ei-z.E)-Math.abs(Ei-a.E));
for(const candidate of candidates){const j=candidate.j,Ej=candidate.E,ai=alpha[i],aj=alpha[j];let L,H;
if(y[i]!==y[j]){L=Math.max(0,aj-ai);H=Math.min(C,C+aj-ai);}else{L=Math.max(0,ai+aj-C);H=Math.min(C,ai+aj);}if(H-L<1e-10)continue;
const eta=K[i][i]+K[j][j]-2*K[i][j];if(eta<=1e-12)continue;
const nextJ=clamp(aj+y[j]*(Ei-Ej)/eta,L,H);if(Math.abs(nextJ-aj)<1e-8)continue;
const nextI=ai+y[i]*y[j]*(aj-nextJ),b1=b-Ei-y[i]*(nextI-ai)*K[i][i]-y[j]*(nextJ-aj)*K[i][j],b2=b-Ej-y[i]*(nextI-ai)*K[i][j]-y[j]*(nextJ-aj)*K[j][j];
alpha[i]=nextI;alpha[j]=nextJ;b=nextI>1e-8&&nextI<C-1e-8?b1:nextJ>1e-8&&nextJ<C-1e-8?b2:(b1+b2)/2;changed++;break;
}}
passes=changed===0?passes+1:0;
}
// Recover the intercept from global KKT bounds, including the all-at-C case.
// With no free support vector the optimum can admit an interval of intercepts;
// the midpoint gives a deterministic representative instead of the last pair's b.
let lower=-Infinity,upper=Infinity;const freeIntercepts=[];
for(let i=0;i<n;i++){const withoutBias=alpha.reduce((sum,a,j)=>sum+a*y[j]*K[j][i],0),candidate=y[i]-withoutBias;
if(alpha[i]>1e-7&&alpha[i]<C-1e-7)freeIntercepts.push(candidate);
else if(alpha[i]<=1e-7){if(y[i]>0)lower=Math.max(lower,candidate);else upper=Math.min(upper,candidate);}
else{if(y[i]>0)upper=Math.min(upper,candidate);else lower=Math.max(lower,candidate);}}
if(freeIntercepts.length)b=freeIntercepts.reduce((sum,v)=>sum+v,0)/freeIntercepts.length;
else if(Number.isFinite(lower)&&Number.isFinite(upper))b=(lower+upper)/2;
const score=p=>alpha.reduce((sum,a,j)=>sum+a*y[j]*Math.exp(-gamma*distance2(points[j],p)),b);
return{alpha,b,C,gamma,iterations,support:points.map((p,i)=>({point:p,index:i,alpha:alpha[i]})).filter(s=>s.alpha>1e-6),score,predict:p=>score(p)>=0?1:0};
}
const API={random,dataset,distance2,sigmoid,logisticTrain,impurity,cartTrain,treePath,predictTree,forestTrain,forestVote,knn,svmTrain};
global.AlgorithmMotionModel=API;
if(typeof document==='undefined')return;

const configurations={
logistic:{name:'로지스틱 회귀',parameter:'C',values:[.1,1,10],initial:1,steps:['특성 입력','가중합 계산','시그모이드 변환','기준값 비교'],descriptions:['새 점의 두 특성값 입력','학습된 가중치와 절편을 이용한 선형 점수 계산','시그모이드 함수를 통한 0~1 출력값 변환','출력값 0.5를 기준으로 한 범주 구분']},
tree:{name:'결정트리',parameter:'최대 깊이',values:[2,4,null],initial:4,steps:['전체 자료','조건 분할','경로 추적','말단 투표'],descriptions:['두 범주가 섞인 전체 자료','지니 불순도 감소를 기준으로 한 조건 분할','새 점의 특성값에 따른 좌·우 경로 선택','도착한 말단 노드의 다수 범주 선택']},
forest:{name:'랜덤포레스트',parameter:'최대 깊이',values:[2,4,null],initial:4,steps:['복원 추출','다른 나무 학습','나무별 예측','다수결 집계'],descriptions:['중복을 허용한 학습 사례 재추출','노드별 무작위 특성 선택과 서로 다른 분할','같은 새 점에 대한 다섯 나무의 개별 예측','다섯 예측의 다수결에 따른 최종 범주 선택']},
knn:{name:'K-NN',parameter:'K',values:[1,5,15],initial:5,steps:['새 점 입력','거리 계산','이웃 선택','다수결 집계'],descriptions:['분류할 새 점의 위치 입력','두 특성 공간에서의 유클리드 거리 계산','거리순으로 정렬한 가까운 K개 이웃 선택','선택한 이웃의 정답을 이용한 다수결']},
svm:{name:'SVM',parameter:'C',values:[.1,1,10],initial:1,steps:['자료 입력','서포트 벡터','경계와 여유','결정함수 판정'],descriptions:['두 특성을 사용하는 RBF 커널 분류','학습된 쌍대계수 α가 0보다 큰 서포트 벡터 표시','결정함수 f(x)의 0 및 ±1 등고선 표시','새 점의 결정함수 부호를 이용한 범주 구분']}
};
const SVG='http://www.w3.org/2000/svg',plot={left:54,top:30,size:350};
const px=x=>plot.left+(x+1)*plot.size/2,py=y=>plot.top+(1-y)*plot.size/2;
const format=x=>Number(x).toFixed(3);
let instance=0;
function element(name,attributes={},text){const node=document.createElementNS(SVG,name);for(const [key,value]of Object.entries(attributes))node.setAttribute(key,String(value));if(text!==undefined)node.textContent=String(text);return node;}
function contour(field,level,steps=32){let path='';const value=(i,j)=>({x:-1+2*i/steps,y:-1+2*j/steps});
for(let i=0;i<steps;i++)for(let j=0;j<steps;j++){const corners=[value(i,j),value(i+1,j),value(i+1,j+1),value(i,j+1)],hits=[];for(let k=0;k<4;k++){const a=corners[k],z=corners[(k+1)%4],fa=field(a)-level,fz=field(z)-level;if((fa>=0)!==(fz>=0)){const ratio=fa/(fa-fz);hits.push({x:a.x+ratio*(z.x-a.x),y:a.y+ratio*(z.y-a.y)});}}for(let k=0;k+1<hits.length;k+=2)path+=`M${px(hits[k].x).toFixed(2)},${py(hits[k].y).toFixed(2)}L${px(hits[k+1].x).toFixed(2)},${py(hits[k+1].y).toFixed(2)}`;}
return path;
}
function drawPartitions(parent,tree,bounds={x0:-1,x1:1,y0:-1,y1:1},maxDepth=99,pathNodes=new Set()){
if(tree.leaf||tree.depth>=maxDepth)return;
const selected=pathNodes.has(tree),line=tree.feature==='x'?{x1:px(tree.threshold),x2:px(tree.threshold),y1:py(bounds.y0),y2:py(bounds.y1)}:{x1:px(bounds.x0),x2:px(bounds.x1),y1:py(tree.threshold),y2:py(tree.threshold)};
parent.append(element('line',{...line,stroke:'#000000','stroke-width':selected?3:1,'stroke-dasharray':selected?'':'5 4',class:'motion-split'}));
const left={...bounds},right={...bounds};if(tree.feature==='x'){left.x1=tree.threshold;right.x0=tree.threshold;}else{left.y1=tree.threshold;right.y0=tree.threshold;}
drawPartitions(parent,tree.left,left,maxDepth,pathNodes);drawPartitions(parent,tree.right,right,maxDepth,pathNodes);
}
function mount(root){
const algorithm=root.dataset.algorithm,config=configurations[algorithm];if(!config)return;
const id=++instance,points=dataset(),reduced=typeof matchMedia==='function'&&matchMedia('(prefers-reduced-motion: reduce)').matches;let query={x:.1,y:.1},stage=0,value=config.initial,model,timer=null,playing=false,wantedPlaying=!reduced;
root.innerHTML=`<div class="motion-heading"><h2>판단 과정</h2><p class="caption">원리 설명용 2차원 가상 데이터 · 코랩의 실제 5개 입력과 별도</p></div><div class="motion-controls"><button type="button" data-action="play" aria-pressed="false">재생</button><button type="button" data-action="previous">이전 단계</button><button type="button" data-action="next">다음 단계</button><button type="button" data-action="reset">초기화</button><label>${config.parameter} <select aria-label="${config.name} ${config.parameter}">${config.values.map(v=>`<option value="${v===null?'none':v}"${v===config.initial?' selected':''}>${v===null?'제한 없음':v}</option>`).join('')}</select></label></div><ol class="motion-steps">${config.steps.map((name,index)=>`<li><button type="button" data-step="${index}"><span>0${index+1}</span> ${name}</button></li>`).join('')}</ol><div class="motion-board"><svg class="motion-svg" viewBox="0 0 450 430" role="img" tabindex="0" aria-label="${config.name} 분류 과정. 그래프 클릭 또는 화살표 키를 통한 새 점 위치 변경"></svg><div class="motion-readout"></div></div><p class="motion-stage" aria-live="polite" aria-atomic="true"></p><div class="motion-position"><label>새 점 · 특성 1 <input type="range" min="-0.95" max="0.95" step="0.05" value="0.1" data-axis="x" aria-label="새 점 특성 1"></label><label>새 점 · 특성 2 <input type="range" min="-0.95" max="0.95" step="0.05" value="0.1" data-axis="y" aria-label="새 점 특성 2"></label></div><p class="caption">○ 범주 0 · ● 범주 1 · ◇ 새 점 · 그래프 클릭 / 화살표 키 / 위치 슬라이더</p>`;
const svg=root.querySelector('svg'),readout=root.querySelector('.motion-readout'),status=root.querySelector('.motion-stage'),play=root.querySelector('[data-action=play]');
function train(){if(algorithm==='logistic')model=logisticTrain(points,value);else if(algorithm==='tree')model=cartTrain(points,value===null?Infinity:value);else if(algorithm==='forest')model=forestTrain(points,value===null?Infinity:value);else if(algorithm==='svm')model=svmTrain(points,value,2);}
function prediction(p){if(algorithm==='logistic'||algorithm==='svm')return model.predict(p);if(algorithm==='tree')return predictTree(model,p);if(algorithm==='forest')return forestVote(model,p).prediction;return knn(points,p,value).prediction;}
function addText(target,x,y,text,extra={}){target.append(element('text',{x,y,fill:'#000000','font-size':11,'font-family':'system-ui, sans-serif',...extra},text));}
function metric(label,number){return`<div class="motion-metric"><span>${label}</span><strong>${number}</strong></div>`;}
function draw(){
svg.replaceChildren();const defs=element('defs'),clip=element('clipPath',{id:`motion-clip-${id}`});clip.append(element('rect',{x:plot.left,y:plot.top,width:plot.size,height:plot.size}));defs.append(clip);svg.append(defs);
svg.append(element('rect',{x:plot.left,y:plot.top,width:plot.size,height:plot.size,fill:'#ffffff',stroke:'#000000'}));
const graph=element('g',{'clip-path':`url(#motion-clip-${id})`});svg.append(graph);
if(stage===3&&(algorithm==='knn'||algorithm==='forest'))graph.append(element('path',{d:contour(p=>algorithm==='knn'?(prediction(p)?1:-1):forestVote(model,p).one-forestVote(model,p).zero,0),fill:'none',stroke:'#000000','stroke-width':3,class:'motion-decision-boundary'}));
for(const t of [-1,-.5,0,.5,1]){addText(svg,px(t),plot.top+plot.size+19,t.toFixed(1),{'text-anchor':'middle'});addText(svg,plot.left-10,py(t)+4,t.toFixed(1),{'text-anchor':'end'});}
addText(svg,plot.left+plot.size/2,plot.top+plot.size+43,'특성 1',{'text-anchor':'middle','font-size':12});addText(svg,14,plot.top+plot.size/2,'특성 2',{'text-anchor':'middle',transform:`rotate(-90 14 ${plot.top+plot.size/2})`,'font-size':12});
let information='',highlight=new Set();
if(algorithm==='logistic'){
const z=model.score(query),p=model.probability(query);if(stage>=1){graph.append(element('line',{x1:px(query.x),x2:px(query.x),y1:py(query.y),y2:py(0),stroke:'#000000','stroke-dasharray':'4 4'}));graph.append(element('line',{x1:px(query.x),x2:px(0),y1:py(query.y),y2:py(query.y),stroke:'#000000','stroke-dasharray':'4 4'}));}if(stage>=2)graph.append(element('path',{d:contour(model.score,0),fill:'none',stroke:'#000000','stroke-width':2.4}));
information=`<h3>선형 점수 → 출력값</h3><p class="motion-formula">z = ${format(model.w[0])}x₁ + ${format(model.w[1])}x₂ ${model.b<0?'−':'+'} ${format(Math.abs(model.b))}</p>${metric('새 점의 가중합 z',stage>=1?format(z):'—')}${metric('시그모이드 σ(z)',stage>=2?format(p):'—')}${metric('예측 범주',stage>=3?String(p>=.5?1:0):'—')}<p class="caption">L2 규제 · 경사하강 학습<br>C=${value} · 자료 ${points.length}개<br>학습 로그손실 ${format(model.loss)}<br>0.5 기준값에 따른 분류</p>`;
if(stage>=2)information+=`<svg viewBox="0 0 220 95" class="motion-sigmoid" aria-label="시그모이드 곡선과 현재 출력값"><path d="M15 80H210M110 10V80" stroke="#000000" fill="none"/><path d="${Array.from({length:61},(_,i)=>{const x=-6+i/5;return(i?'L':'M')+(15+(x+6)/12*195).toFixed(1)+','+(80-sigmoid(x)*65).toFixed(1);}).join('')}" stroke="#000000" stroke-width="2" fill="none"/><circle cx="${15+(clamp(z,-6,6)+6)/12*195}" cy="${80-p*65}" r="4" fill="#000000"/></svg>`;
}else if(algorithm==='knn'){
const vote=knn(points,query,value);highlight=new Set(vote.neighbors.map(p=>p.id));if(stage>=1)for(const p of points)graph.append(element('line',{x1:px(query.x),y1:py(query.y),x2:px(p.x),y2:py(p.y),stroke:'#000000','stroke-width':highlight.has(p.id)?1.6:.7,'stroke-dasharray':highlight.has(p.id)?'':'2 4'}));
if(stage>=2)graph.append(element('circle',{cx:px(query.x),cy:py(query.y),r:vote.neighbors.at(-1).distance*plot.size/2,fill:'none',stroke:'#000000','stroke-width':1.8,'stroke-dasharray':'5 4'}));
information=`<h3>거리순 이웃 선택</h3>${metric('선택한 이웃 수',stage>=2?String(value):'—')}${metric('범주 0 / 범주 1',stage>=2?`${vote.zero} / ${vote.one}`:'—')}${metric('예측 범주',stage>=3?String(vote.prediction):'—')}<p class="caption">두 특성의 유클리드 거리<br>선택 이웃: 큰 점·굵은 실선<br>거리 동률 시 사례 번호순 정렬<br>최종 굵은 선: 격자 보간 결정 경계</p>`;
if(stage>=1)information+=`<ol class="motion-neighbor-list">${vote.neighbors.slice(0,5).map(p=>`<li>사례 ${String(p.id+1).padStart(2,'0')} · 거리 ${format(p.distance)} · 범주 ${p.label}</li>`).join('')}</ol>`;
}else if(algorithm==='tree'){
const route=treePath(model,query);if(stage>=1)drawPartitions(graph,model,undefined,stage===1?1:99,stage>=2?new Set(route.path.map(item=>item.node)):new Set());
information=`<h3>조건에 따른 경로</h3>${metric('말단의 범주 0 / 범주 1',stage>=2?route.leaf.counts.join(' / '):'—')}${metric('예측 범주',stage>=3?String(route.prediction):'—')}<p class="caption">지니 불순도 감소 기준의 실제 분할<br>깊이 상한 ${value===null?'제한 없음':value}</p>`;
if(stage>=2)information+=`<ol class="motion-path">${route.path.map(item=>`<li>특성 ${item.node.feature==='x'?'1':'2'} ${item.direction==='left'?'≤':'>'} ${format(item.node.threshold)}<span> ${item.direction==='left'?'왼쪽':'오른쪽'} 이동</span></li>`).join('')}<li>말단 도착 · 사례 ${route.leaf.n}개</li></ol>`;
}else if(algorithm==='forest'){
const vote=forestVote(model,query),unique=new Set(model.samples[0].map(p=>p.id));if(stage===0)highlight=unique;if(stage>=1)drawPartitions(graph,model.trees[0],undefined,99,stage===2?new Set(treePath(model.trees[0],query).path.map(item=>item.node)):new Set());
information=`<h3>서로 다른 나무의 투표</h3>${metric('첫 나무 복원 추출',`${points.length}회 / 서로 다른 ${unique.size}개`)}<div class="motion-votes">${vote.votes.map((v,i)=>`<div class="motion-vote${stage>=2?' is-revealed':''}"><span>나무 ${i+1}</span><strong>${stage>=2?v:'—'}</strong></div>`).join('')}</div>${metric('범주 0 / 범주 1',stage>=2?`${vote.zero} / ${vote.one}`:'—')}${metric('최종 예측 범주',stage>=3?String(vote.prediction):'—')}<p class="caption">복원 추출 선택: 큰 점·바깥 테두리<br>점선: 첫 나무의 분할 조건<br>최종 굵은 선: 다수결 결정 경계<br>결정 경계의 격자 보간 근사<br>노드마다 두 특성 중 하나의 무작위 선택<br>시각화: 나무 5개 · 코랩 기본값: 100개</p>`;
}else{
if(stage>=2){for(const level of [-1,1])graph.append(element('path',{d:contour(model.score,level),fill:'none',stroke:'#000000','stroke-width':1.2,'stroke-dasharray':'5 4'}));graph.append(element('path',{d:contour(model.score,0),fill:'none',stroke:'#000000','stroke-width':2.6}));}
if(stage>=1)for(const support of model.support)graph.append(element('circle',{cx:px(support.point.x),cy:py(support.point.y),r:10,fill:'none',stroke:'#000000','stroke-width':1.5,class:'motion-support'}));
information=`<h3>RBF 결정함수</h3>${metric('서포트 벡터',stage>=1?`${model.support.length} / ${points.length}개`:'—')}${metric('새 점의 f(x)',stage>=2?format(model.score(query)):'—')}${metric('예측 범주',stage>=3?String(model.predict(query)):'—')}<p class="caption">실선: f(x)=0<br>점선: f(x)=−1, +1<br>서포트 벡터: α&gt;0 사례<br>여유 안쪽·오분류 사례 포함 가능<br>시각화: RBF γ=2 고정 · C=${value}<br>코랩 기본값: RBF γ='scale'<br>확률이 아닌 결정함수 값<br>SMO 방식의 쌍대 최적화</p>`;
}
for(const p of points){const selectionStage=(algorithm==='knn'&&stage>=2)||(algorithm==='forest'&&stage===0),selected=selectionStage&&highlight.has(p.id),radius=selectionStage?(selected?5.5:3):4.5;if(selected)graph.append(element('circle',{cx:px(p.x),cy:py(p.y),r:8,fill:'none',stroke:'#000000','stroke-width':1}));graph.append(element('circle',{cx:px(p.x),cy:py(p.y),r:radius,fill:p.label?'#000000':'#ffffff',stroke:'#000000','stroke-width':selected?2:1.3}));}
const qx=px(query.x),qy=py(query.y);graph.append(element('circle',{cx:qx,cy:qy,r:13,fill:'none',stroke:'#000000','stroke-width':1,'stroke-dasharray':'2 3',class:'motion-query-ring'}));graph.append(element('path',{d:`M${qx} ${qy-7}l7 7-7 7-7-7Z`,fill:'#ffffff',stroke:'#000000','stroke-width':2.2}));
readout.innerHTML=information;status.textContent=`${stage+1} / 4 · ${config.descriptions[stage]}`;
root.querySelectorAll('[data-step]').forEach(button=>{const selected=Number(button.dataset.step)===stage;button.setAttribute('aria-current',selected?'step':'false');button.classList.toggle('is-current',selected);});
root.querySelector('[data-action=previous]').disabled=stage===0;
root.querySelector('[data-action=next]').disabled=stage===3;
root.querySelectorAll('[data-axis]').forEach(input=>input.value=String(query[input.dataset.axis]));
root.classList.toggle('is-playing',playing);
}
function stop(preserveIntent=false){if(!preserveIntent)wantedPlaying=false;playing=false;if(timer)clearInterval(timer);timer=null;play.textContent='재생';play.setAttribute('aria-pressed','false');root.classList.remove('is-playing');}
function start(){wantedPlaying=true;if(timer)return;playing=true;play.textContent='정지';play.setAttribute('aria-pressed','true');root.classList.add('is-playing');timer=setInterval(()=>{if(document.hidden)return;stage=(stage+1)%4;draw();},1800);}
root.querySelector('[data-action=play]').addEventListener('click',()=>playing?stop():start());
root.querySelector('[data-action=previous]').addEventListener('click',()=>{stop();stage=Math.max(0,stage-1);draw();});
root.querySelector('[data-action=next]').addEventListener('click',()=>{stop();stage=Math.min(3,stage+1);draw();});
root.querySelector('[data-action=reset]').addEventListener('click',()=>{stop();stage=0;value=config.initial;query={x:.1,y:.1};root.querySelector('select').value=String(value);train();draw();});
root.querySelectorAll('[data-step]').forEach(button=>button.addEventListener('click',()=>{stop();stage=Number(button.dataset.step);draw();}));
root.querySelector('select').addEventListener('change',event=>{stop();value=event.target.value==='none'?null:Number(event.target.value);train();draw();});
root.querySelectorAll('[data-axis]').forEach(input=>input.addEventListener('input',()=>{stop();query[input.dataset.axis]=Number(input.value);draw();}));
svg.addEventListener('click',event=>{const matrix=svg.getScreenCTM();if(!matrix)return;const point=svg.createSVGPoint();point.x=event.clientX;point.y=event.clientY;const local=point.matrixTransform(matrix.inverse());if(local.x<plot.left||local.x>plot.left+plot.size||local.y<plot.top||local.y>plot.top+plot.size)return;stop();query={x:clamp((local.x-plot.left)/plot.size*2-1,-.95,.95),y:clamp(1-(local.y-plot.top)/plot.size*2,-.95,.95)};draw();});
svg.addEventListener('keydown',event=>{const changes={ArrowLeft:['x',-.05],ArrowRight:['x',.05],ArrowDown:['y',-.05],ArrowUp:['y',.05]};if(!changes[event.key])return;event.preventDefault();stop();const [axis,delta]=changes[event.key];query[axis]=clamp(query[axis]+delta,-.95,.95);draw();});
train();draw();
if(!reduced)start();
if(typeof IntersectionObserver!=='undefined'){const observer=new IntersectionObserver(entries=>{for(const entry of entries){if(!entry.isIntersecting&&playing)stop(true);else if(entry.isIntersecting&&wantedPlaying&&!playing)start();}},{threshold:0});observer.observe(root);}
}
document.querySelectorAll('.motion-lab[data-algorithm]').forEach(mount);
})(globalThis);
