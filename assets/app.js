(async function flatApp(){
'use strict';const $=s=>document.querySelector(s),data=await fetch('catalog.json').then(r=>{if(!r.ok)throw Error('catalog');return r.json()}),page=document.body.dataset.page;
const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function notes(d){return `<h2>${d.title}</h2><p>${d.good}</p><h3>직접 비교해 보기</h3><p>${d.mission}</p><h3>유지하고 보완한 부분</h3><ul>${d.changes.map(t=>`<li>${t}</li>`).join('')}</ul><p class="minor">살펴볼 개념: ${d.concept}</p>`;}
function viewer(root,d,initial='improved',onMode){
const versions={improved:{label:'개선본',file:`labs/${d.id}/index.html?v=2`},original:{label:'원본',file:`labs/${d.id}/original.html?v=2`}};
if(d.document)versions.document={label:'개발 설명서',file:`labs/${d.id}/document.html`};
const modes=[['improved','개선본'],['original','원본'],['compare','나란히 비교'],['feedback','피드백'],['source','코드'],...(d.document?[['document','개발 설명서']]:[])];
root.innerHTML=`<div class="view-tabs" role="tablist" aria-label="프로그램 보기">${modes.map(([id,label])=>`<button role="tab" type="button" data-mode="${id}">${label}</button>`).join('')}</div><div class="view-actions"><a data-open target="_blank" rel="noopener">새 창에서 열기</a><a data-download download>파일 저장</a></div><div class="live-frames"></div><section class="notes-pane" hidden>${notes(d)}</section><section class="code-pane" hidden><div class="code-tools"><label>코드 선택 <select data-code><option value="improved">개선본</option><option value="original">원본</option></select></label><button data-copy type="button">복사</button><span data-code-status role="status"></span></div><pre><code></code></pre></section>`;
const frames=new Map(),q=s=>root.querySelector(s),frameArea=q('.live-frames');
let activeMode='',fetchId=0;
function create(name){
if(frames.has(name))return frames.get(name);
const v=versions[name],section=document.createElement('section');section.className='frame-section';section.dataset.version=name;
const heading=document.createElement('h2');heading.className='version-label';heading.textContent=v.label;
const frame=document.createElement('iframe');frame.className='program-frame';frame.title=d.title+' '+v.label;frame.setAttribute('sandbox','allow-scripts allow-same-origin allow-downloads allow-modals');frame.referrerPolicy='no-referrer';frame.style.height='650px';
section.append(heading,frame);frameArea.append(section);frames.set(name,{section,frame,observer:null});
function resize(){if(section.hidden||frameArea.hidden)return;try{const doc=frame.contentDocument;if(!doc?.body)return;const style=getComputedStyle(doc.body);const height=Math.ceil(doc.body.getBoundingClientRect().height+parseFloat(style.marginTop||0)+parseFloat(style.marginBottom||0));const next=Math.max(480,Math.min(20000,height+3));if(Math.abs(parseFloat(frame.style.height)-next)>3)frame.style.height=next+'px';}catch{}}
frame.addEventListener('load',()=>{try{const doc=frame.contentDocument;if(!doc?.body)return;const style=doc.createElement('style');style.textContent='html,body,#app{min-height:0!important}';doc.head.append(style);frames.get(name).observer=new ResizeObserver(resize);frames.get(name).observer.observe(doc.body);doc.fonts?.ready.then(resize);resize();}catch{}});
frames.get(name).resize=resize;frame.src=v.file;return frames.get(name);
}
async function loadCode(){
const seq=++fetchId,name=q('[data-code]').value;
q('[data-code-status]').textContent='';q('code').textContent='불러오는 중…';
try{const r=await fetch(versions[name].file);if(!r.ok)throw Error();const text=await r.text();if(seq===fetchId)q('code').textContent=text;}catch{if(seq===fetchId)q('code').textContent='코드를 불러올 수 없습니다. 다시 선택해 주세요.'}
}
function setMode(mode,notify=true){
if(!modes.some(([x])=>x===mode))mode='improved';activeMode=mode;
root.querySelectorAll('[data-mode]').forEach(b=>{const selected=b.dataset.mode===mode;b.setAttribute('aria-selected',String(selected));b.tabIndex=selected?0:-1;});
frameArea.hidden=['feedback','source'].includes(mode);q('.notes-pane').hidden=mode!=='feedback';q('.code-pane').hidden=mode!=='source';
frameArea.classList.toggle('is-comparing',mode==='compare');
const names=mode==='compare'?['original','improved']:versions[mode]?[mode]:[];
names.forEach(create);frames.forEach((v,name)=>{v.section.hidden=!names.includes(name);v.section.querySelector('.version-label').hidden=mode!=='compare';});
const file=versions[mode]?.file||versions.improved.file;q('[data-open]').href=file;q('[data-download]').href=file;q('[data-download]').download=d.id+'-'+(versions[mode]?mode:'improved')+'.html';
q('.view-actions').hidden=mode==='feedback'||mode==='source';
if(mode==='source')loadCode();
requestAnimationFrame(()=>frames.forEach(v=>v.resize?.()));
if(notify)onMode?.(mode);
}
q('.view-tabs').addEventListener('click',e=>{const b=e.target.closest('[data-mode]');if(b)setMode(b.dataset.mode)});
q('.view-tabs').addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();const tabs=[...root.querySelectorAll('[data-mode]')],i=tabs.findIndex(b=>b.dataset.mode===activeMode),n=e.key==='Home'?0:e.key==='End'?tabs.length-1:(i+(e.key==='ArrowLeft'?-1:1)+tabs.length)%tabs.length;setMode(tabs[n].dataset.mode);tabs[n].focus()});
q('[data-code]').addEventListener('change',loadCode);
q('[data-copy]').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(q('code').textContent);q('[data-code-status]').textContent='복사했습니다.'}catch{q('[data-code-status]').textContent='코드를 선택해 복사해 주세요.'}});
setMode(initial,false);
return {setMode,destroy(){frames.forEach(v=>v.observer?.disconnect());root.replaceChildren();}};
}
if(page==='home'){
let category='전체';const cats=['전체',...new Set(data.map(d=>d.category))];
$('#categoryFilters').innerHTML=cats.map(c=>`<button type="button" data-category="${c}" aria-pressed="${c===category}">${c}</button>`).join('');
function render(){const query=$('#search').value.trim().toLowerCase(),list=data.filter(d=>(category==='전체'||d.category===category)&&[d.title,d.desc,d.category,...d.skills].join(' ').toLowerCase().includes(query));$('#labList').innerHTML=list.map(d=>`<article class="lab-row"><span class="row-number">${d.n}</span><div><h2><a href="lab.html?id=${d.id}">${d.title}</a></h2><p>${d.desc}</p></div><div class="row-links"><a href="lab.html?id=${d.id}">열기</a><a href="lab.html?id=${d.id}&view=compare">원본과 비교</a></div></article>`).join('');$('#emptyState').hidden=!!list.length;$('#searchStatus').textContent=list.length+'개 프로그램';}
$('#categoryFilters').onclick=e=>{const b=e.target.closest('button');if(!b)return;category=b.dataset.category;$('#categoryFilters').querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));render();};
$('#search').oninput=render;$('#clearSearch').onclick=()=>{$('#search').value='';category='전체';$('#categoryFilters').querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.category===category)));render()};render();
}
if(page==='lab'){
const params=new URLSearchParams(location.search),d=data.find(x=>x.id===params.get('id'));
if(!d){$('#main').innerHTML='<h1>프로그램을 찾을 수 없습니다.</h1><a href="index.html">실험 모음으로</a>';return;}
document.title=d.title+' · 탐구 실험실';$('#labHeading').innerHTML=`<div class="page-title"><h1>${d.title}</h1><p>${d.desc}</p></div>`;
const v=viewer($('#labViewer'),d,params.get('view')||'improved',mode=>{const url=new URL(location.href);url.searchParams.set('view',mode);history.replaceState(null,'',url)});
if(params.get('code')==='original'){const select=$('#labViewer [data-code]');select.value='original';select.dispatchEvent(new Event('change'));}
}
if(page==='feedback'){
$('#feedbackLab').innerHTML=data.map(d=>`<option value="${d.id}">${d.title}</option>`).join('');
let active=null;const remembered=new Map();
function select(){if(active)$('#feedbackViewer').append(active.root);const id=$('#feedbackLab').value,d=data.find(d=>d.id===id);$('#feedbackViewer').querySelectorAll('.viewer-instance').forEach(n=>n.hidden=true);if(!remembered.has(id)){const root=document.createElement('div');root.className='viewer-instance';$('#feedbackViewer').append(root);remembered.set(id,{root,api:viewer(root,d)});}active=remembered.get(id);active.root.hidden=false;active.api.setMode('improved');}
$('#feedbackLab').onchange=select;select();
$('#reviewList').innerHTML=data.map(d=>`<details class="review-item" id="${d.id}"><summary>${d.n}　${d.title}</summary>${notes(d)}<p><button type="button" data-show="${d.id}">위에서 직접 해보기</button>　<a href="lab.html?id=${d.id}&view=compare">원본과 나란히 비교</a></p></details>`).join('');
$('#reviewList').onclick=e=>{const b=e.target.closest('[data-show]');if(b){$('#feedbackLab').value=b.dataset.show;select();$('#feedbackLab').scrollIntoView({behavior:'smooth',block:'start'});}};
}
if(page==='archive'){
$('#archiveList').innerHTML=data.map(d=>`<article class="lab-row"><span class="row-number">${d.n}</span><div><h2>${d.title}</h2><p>${d.category}</p></div><div class="row-links"><a href="lab.html?id=${d.id}&view=original">원본 실행</a><a href="lab.html?id=${d.id}&view=source&code=original">코드</a><a href="labs/${d.id}/original.html" download="${d.id}-original.html">파일 저장</a>${d.document?`<a href="lab.html?id=${d.id}&view=document">설명서</a>`:''}</div></article>`).join('');
}
})().catch(()=>{document.getElementById('main').innerHTML='<p>자료를 불러오지 못했습니다. 새로고침해 주세요.</p>';});