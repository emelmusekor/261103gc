(async function app(){
'use strict';
const $=s=>document.querySelector(s),data=await fetch('catalog.json').then(r=>{if(!r.ok)throw Error();return r.json()}).catch(()=>[]);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function illustration(d){
const ink=d.color;
const common=`fill="none" stroke="${ink}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"`;
const art={
history:`<g ${common}><path d="M70 25h85v100H70zM155 35h67v102h-67"/><path d="M84 44h48M84 55h56M84 66h35M84 85h47M84 96h40M168 53h39M168 66h28M168 83h37M168 96h32"/><circle cx="139" cy="115" r="18" fill="#f9faf2"/><path d="m152 128 19 19"/><path d="m130 115 6 6 12-14"/></g><circle cx="214" cy="29" r="4" fill="${ink}" opacity=".5"/>`,
fashion:`<g ${common}><path d="M104 28h68l-9 29 10 28 28 52h-126l29-52 9-28z" fill="#ffffff55"/><path d="M104 28 84 38l-18 31 22 15 21-28M172 28l20 10 20 31-22 15-21-28M113 57h50M104 85h69"/><path d="M239 28v109M234 35h10M234 57h10M234 79h10M234 101h10M234 123h10" opacity=".5"/><path d="M129 29c0 13 17 13 17 0"/></g><g stroke="${ink}" opacity=".2" stroke-dasharray="3 4"><path d="M48 57h172M48 85h172M138 14v138"/></g>`,
math:`<g ${common}><rect x="61" y="32" width="94" height="101" rx="6" fill="#fff6"/><path d="M76 52h62M77 70h22M117 70h20M77 89h22M117 89h20M77 108h22M117 108h20"/><circle cx="203" cy="65" r="28"/><path d="m188 64 11 11 20-23M176 115h53M193 101v28"/></g><text x="77" y="24" font-family="Georgia" font-size="16" fill="${ink}" opacity=".6">24 × 6</text>`,
pose:`<g ${common}><path d="M70 29v-9h21M210 29v-9h-21M70 124v15h21M210 124v15h-21" opacity=".6"/><circle cx="140" cy="40" r="12"/><path d="m140 53-7 43-29 22-20 9M133 96l33 15 27 21M139 65l-32 12-16 24M142 65l31 17 19-17"/><path d="m130 95 1 20 15 5" stroke-dasharray="3 3"/></g><g fill="#f7f9ef" stroke="${ink}" stroke-width="1.8">${[[140,65],[133,96],[104,118],[166,111],[107,77],[173,82]].map(([x,y])=>`<circle cx="${x}" cy="${y}" r="4"/>`).join('')}</g>`,
drone:`<g ${common}><path d="m108 65 64 0 0 45-64 0z" fill="#fff5"/><path d="m108 67-23-22M171 67l23-22M108 108l-23 20M172 108l22 20"/><ellipse cx="78" cy="40" rx="24" ry="9"/><ellipse cx="202" cy="40" rx="24" ry="9"/><ellipse cx="78" cy="133" rx="24" ry="9"/><ellipse cx="202" cy="133" rx="24" ry="9"/><path d="M112 86h12l5-12 10 24 8-18 5 6h16"/><path d="M249 69c11 10 11 26 0 36M237 77c6 6 6 15 0 21" opacity=".6"/></g>`,
probability:`<g ${common}><path d="M65 70h85l-9 67H75z" fill="#fff6"/><path d="M78 70V56c0-39 59-39 59 0v14M177 129h71M177 129V41"/><path d="m181 115 13-19 13 7 15-30 16 5 8-30"/></g>${[[88,91],[109,88],[130,94],[100,116],[121,119]].map(([x,y],i)=>`<circle cx="${x}" cy="${y}" r="7" fill="${i%3===0?'#7d98a3':ink}" opacity=".65"/>`).join('')}<path d="M178 82h71" stroke="${ink}" stroke-dasharray="3 4" opacity=".4"/>`,
career:`<g ${common}><path d="M56 137V20M56 137h184" opacity=".5"/><path d="M70 118 218 37" stroke-dasharray="4 5" opacity=".35"/></g>${[[85,110],[102,84],[130,119],[135,79],[173,115],[102,45],[129,36],[164,57],[199,38],[204,78]].map(([x,y],i)=>`<circle cx="${x}" cy="${y}" r="6" fill="${i<5?ink:'#a3ac7a'}" opacity=".7"/>`).join('')}<circle cx="157" cy="79" r="32" fill="none" stroke="${ink}" stroke-dasharray="4 4"/><path d="m157 69 3 7 8 1-6 5 2 8-7-4-7 4 2-8-6-5 8-1z" fill="${ink}"/>`
};
return `<svg viewBox="0 0 280 160" aria-hidden="true">${art[d.id]}</svg>`;
}
function review(d){
return `<div class="review-body"><p class="review-question">${d.question}</p><div class="before-after"><div><span>원본의 탐구</span><p>${d.before}</p></div><div><span>개선본에서 해볼 일</span><p>${d.after}</p></div></div><div class="mission"><b>이렇게 바꿔 보세요</b><p>${d.mission}</p></div><div class="understanding"><span>발견할 원리</span><p>${d.concept}</p></div><div class="review-actions"><button class="button primary" data-preview="${d.id}">이 개선본 바로 해보기 ↗</button><a class="button" href="lab.html?id=${d.id}&view=original">원본과 비교하기 →</a></div><details class="implementation-notes"><summary>설계의 강점과 구현 개선 자세히 보기</summary><div class="strength"><b>설계의 강점</b><br>${d.good}</div><div class="review-columns"><section><h4>원본에서 확인한 지점</h4><ul>${d.issues.map(x=>`<li>${x}</li>`).join('')}</ul></section><section><h4>개선한 동작</h4><ul>${d.changes.map(x=>`<li>${x}</li>`).join('')}</ul></section></div></details></div>`;
}
const page=document.body.dataset.page;
if(page==='home'){
let active='전체';
const cats=['전체','수학','역사','디자인','체육','기술','진로'];
$('#categoryFilters').innerHTML=cats.map(x=>`<button type="button" data-category="${x}" aria-pressed="${x===active}">${x}</button>`).join('');
function render(){
const query=$('#search').value.toLowerCase().trim();
const list=data.filter(d=>(active==='전체'||d.category===active)&&[d.title,d.category,d.desc,...d.skills].join(' ').toLowerCase().includes(query));
$('#visibleCount').textContent=String(list.length).padStart(2,'0');
$('#labGrid').innerHTML=list.map(d=>`<a class="lab-card ${d.id==='career'&&list.length===7?'wide':''}" href="lab.html?id=${d.id}" style="--accent:${d.color};--tint:${d.color}15"><div class="card-art"><span class="art-number">EXPERIMENT ${d.n}</span>${illustration(d)}</div><div class="card-content"><div class="card-category">${d.category} · ${d.tag}</div><h3>${d.title}</h3><p>${d.desc}</p><div class="card-tags">${d.skills.map(x=>`<span>${x}</span>`).join('')}</div><div class="card-bottom"><span>실험 시작하기</span><span aria-hidden="true">↗</span></div></div></a>`).join('');
$('#emptyState').hidden=list.length>0;
}
$('#categoryFilters').onclick=e=>{const b=e.target.closest('button');if(!b)return;active=b.dataset.category;$('#categoryFilters').querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));render()};
$('#search').oninput=render;
$('#clearSearch').onclick=()=>{$('#search').value='';active='전체';$('#categoryFilters').querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.category===active)));render()};
render();
const pts=[[64,78,0],[95,118,0],[82,214,0],[163,71,0],[155,172,0],[177,250,0],[224,133,0],[220,215,0],[297,62,1],[330,139,1],[305,245,1],[390,80,1],[415,191,1],[365,260,1],[450,117,1]],colors=['#6c8d5f','#b9a27d'];
let q={x:252,y:164};
function plot(){
const k=+$('#heroK').value,nearest=pts.map(([x,y,t])=>({x,y,t,dist:Math.hypot(x-q.x,y-q.y)})).sort((a,b)=>a.dist-b.dist).slice(0,k);
const votes=[nearest.filter(p=>p.t===0).length,nearest.filter(p=>p.t===1).length],r=nearest.at(-1).dist;
let svg=`<defs><pattern id="dotgrid" width="19" height="19" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".65" fill="#b8c5ae" opacity=".6"/></pattern></defs><rect x="22" y="15" width="470" height="300" fill="url(#dotgrid)"/><circle cx="${q.x}" cy="${q.y}" r="${r+5}" fill="${colors[votes[0]>votes[1]?0:1]}0f" stroke="#96ac83" stroke-dasharray="4 5"/>`;
nearest.forEach(p=>svg+=`<path d="M${q.x} ${q.y} ${p.x} ${p.y}" stroke="#94a784" stroke-width="1" stroke-dasharray="4 4"/>`);
pts.forEach(([x,y,t])=>svg+=`<circle cx="${x}" cy="${y}" r="6" fill="${colors[t]}"/><circle cx="${x}" cy="${y}" r="10" fill="none" stroke="${colors[t]}" stroke-opacity=".18"/>`);
svg+=`<circle cx="${q.x}" cy="${q.y}" r="13" fill="#234e3d" stroke="#f5f8ea" stroke-width="3"/><path d="M${q.x-4} ${q.y}h8m-4-4v8" stroke="#e3edc3" stroke-width="1.5"/><g><rect x="${Math.min(q.x+17,384)}" y="${q.y-20}" width="72" height="23" rx="4" fill="#fffdf4" stroke="#d1dac6"/><text x="${Math.min(q.x+25,392)}" y="${q.y-5}" font-size="10" font-family="sans-serif" fill="#5e7356">기준점</text></g>`;
$('#heroPlot').innerHTML=svg;
$('#heroResult').innerHTML=`<span class="mono">K = ${k}</span><br>초록 ${votes[0]} : 모래 ${votes[1]}`;
}
$('#heroK').oninput=plot;
$('#heroPlot').onclick=e=>{const pt=$('#heroPlot').createSVGPoint();pt.x=e.clientX;pt.y=e.clientY;const pos=pt.matrixTransform($('#heroPlot').getScreenCTM().inverse());q={x:Math.max(35,Math.min(470,pos.x)),y:Math.max(35,Math.min(292,pos.y))};plot()};
$('#heroPlot').onkeydown=e=>{if(!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key))return;e.preventDefault();q.x=Math.max(35,Math.min(470,q.x+(e.key==='ArrowLeft'?-10:e.key==='ArrowRight'?10:0)));q.y=Math.max(35,Math.min(292,q.y+(e.key==='ArrowUp'?-10:e.key==='ArrowDown'?10:0)));plot()};
plot();
}
if(page==='feedback'){
$('#reviewList').innerHTML=data.map((d,i)=>`<details class="review-item" id="${d.id}" ${i===0?'open':''}><summary><span class="review-number">${d.n}</span><h3>${d.title}</h3><span class="review-category">${d.category} · ${d.tag}</span><span class="review-toggle" aria-hidden="true">+</span></summary>${review(d)}</details>`).join('');
const select=$('#feedbackLab'),version=$('#feedbackVersion');select.innerHTML=data.map(d=>'<option value="'+d.id+'">'+d.title+'</option>').join('');function loadDemo(){const d=data.find(d=>d.id===select.value),original=version.value==='original';$('#feedbackDemoQuestion').textContent=d.question;$('#feedbackDemoPrompt').textContent=original?d.before:d.after;$('#feedbackDemoFrame').src='labs/'+d.id+'/'+(original?'original.html':'index.html');$('#feedbackDemoFrame').title=d.title+(original?' 원본':' 개선본');$('#feedbackDemoFrame').setAttribute('sandbox',original?'allow-scripts allow-downloads':'allow-scripts allow-same-origin allow-downloads');$('#feedbackDemoLink').href='labs/'+d.id+'/'+(original?'original.html':'index.html');}select.onchange=loadDemo;version.onchange=loadDemo;loadDemo();document.addEventListener('click',e=>{const button=e.target.closest('[data-preview]');if(button){select.value=button.dataset.preview;version.value='improved';loadDemo();$('#feedbackDemonstration').scrollIntoView({behavior:'smooth',block:'start'})}});if(location.hash){const found=document.getElementById(location.hash.slice(1));if(found)found.open=true;}
}
if(page==='archive'){
$('#archiveList').innerHTML=data.map(d=>`<article class="archive-row"><span class="mono">${d.n}</span><div><h2>${d.title}</h2><p>${d.category} · ${d.skills.join(' / ')}</p></div><div class="archive-actions"><a class="button" href="lab.html?id=${d.id}&view=original">원본 실행 ↗</a><a class="button" href="lab.html?id=${d.id}&view=source&code=original">코드 보기</a><a class="button" href="labs/${d.id}/original.html" download="${d.id}-original.html">HTML ↓</a>${d.document?`<a class="button" href="lab.html?id=${d.id}&view=document">개발 설명서 ↗</a>`:''}</div></article>`).join('');
}
if(page==='lab'){
const params=new URLSearchParams(location.search),d=data.find(x=>x.id===params.get('id'));
if(!d){$('#main').innerHTML='<section class="error-message"><h1>실험을 찾을 수 없습니다.</h1><p>실험 모음에서 주제를 다시 선택해 주세요.</p><a class="button primary" href="index.html">실험 모음으로 →</a></section>';return;}
document.title=d.title+' · 탐구 실험실';
$('#labHeading').innerHTML=`<section class="lab-heading" style="--accent:${d.color}"><div><p class="eyebrow">EXPERIMENT ${d.n} / ${d.category} · ${d.tag}</p><h1>${d.title}</h1><p>${d.desc}</p></div><a class="button primary" href="labs/${d.id}/index.html" target="_blank" rel="noopener">프로그램 크게 열기 ↗</a></section>`;
$('#tab-document').hidden=!d.document;
let loadSequence=0;
async function setView(view,update=true){
const seq=++loadSequence;
if(!['improved','original','source','feedback','document'].includes(view)||view==='document'&&!d.document)view='improved';
document.querySelectorAll('[data-view]').forEach(b=>{b.setAttribute('aria-selected',String(b.dataset.view===view));b.tabIndex=b.dataset.view===view?0:-1;});
$('#workbenchBody').setAttribute('aria-labelledby','tab-'+view);
if(update){const url=new URL(location.href);url.searchParams.set('view',view);history.replaceState(null,'',url);}
const file=`labs/${d.id}/${view==='original'?'original.html':view==='document'?'document.html':'index.html'}`;
if(['improved','original','document'].includes(view)){
$('#workbenchBody').innerHTML=`<div class="viewer-bar"><span>${view==='original'?'원본 프로그램':view==='document'?'개발 설명서':'개선 프로그램'}</span><div class="viewer-links"><a href="${file}" target="_blank" rel="noopener">새 창으로 열기 ↗</a><a href="${file}" download="${d.id}-${view}.html">파일 저장 ↓</a></div></div><iframe class="program-frame" title="${esc(d.title)} ${view==='original'?'원본':view==='document'?'개발 설명서':'개선본'}" sandbox="${view==='improved'?'allow-scripts allow-same-origin allow-downloads allow-modals':'allow-scripts allow-downloads'}" referrerpolicy="no-referrer" src="${file}"></iframe>`;
}else if(view==='feedback')$('#workbenchBody').innerHTML=`<div class="feedback-panel">${review(d)}</div>`;
else{
$('#workbenchBody').innerHTML='<div class="source-tools"><label for="codeVersion">코드 선택</label><select id="codeVersion"><option value="improved">개선 프로그램</option><option value="original">원본 프로그램</option></select><button id="copyCode">코드 복사</button><span id="codeStatus" role="status"></span></div><pre class="source-code"><code id="sourceCode">코드를 불러오는 중입니다.</code></pre>';
$('#codeVersion').value=params.get('code')==='original'?'original':'improved';
async function code(){
const version=$('#codeVersion').value;
$('#codeStatus').textContent='';
try{const r=await fetch(`labs/${d.id}/${version==='original'?'original.html':'index.html'}`);if(!r.ok)throw Error();const text=await r.text();if(seq===loadSequence&&$('#sourceCode'))$('#sourceCode').textContent=text;}catch{if(seq===loadSequence&&$('#sourceCode'))$('#sourceCode').textContent='코드를 불러오지 못했습니다. 페이지를 새로고침해 주세요.'}
}
$('#codeVersion').onchange=code;
$('#copyCode').onclick=async()=>{try{await navigator.clipboard.writeText($('#sourceCode').textContent);$('#codeStatus').textContent='복사했습니다.'}catch{$('#codeStatus').textContent='코드를 선택해서 복사해 주세요.'}};
code();
}
}
document.querySelector('.workbench-tabs').onclick=e=>{const b=e.target.closest('[data-view]');if(b)setView(b.dataset.view)};
document.querySelector('.workbench-tabs').onkeydown=e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();const tabs=[...document.querySelectorAll('[data-view]')].filter(x=>!x.hidden),i=tabs.findIndex(x=>x.getAttribute('aria-selected')==='true');const j=e.key==='Home'?0:e.key==='End'?tabs.length-1:(i+(e.key==='ArrowLeft'?-1:1)+tabs.length)%tabs.length;tabs[j].focus();setView(tabs[j].dataset.view)};
document.addEventListener('click',e=>{if(e.target.closest('[data-preview]')){setView('improved');document.querySelector('.workbench').scrollIntoView({behavior:'smooth'});}});setView(params.get('view')||'improved',false);
}
})().catch(()=>{const el=document.getElementById('main');if(el)el.innerHTML='<section class="error-message"><h1>자료를 불러오지 못했습니다.</h1><p>새로고침 후 다시 확인해 주세요.</p></section>';});