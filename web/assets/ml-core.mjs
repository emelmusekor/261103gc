export function partition(rows,fraction=.3,seed=42){
if(!Array.isArray(rows)||rows.some(r=>!r.id||!r.label||!Array.isArray(r.features)||!r.features.every(Number.isFinite))||new Set(rows.map(r=>r.id)).size!==rows.length)throw Error('자료의 식별자와 특성을 확인하세요.');
let state=Number(seed)>>>0;const rand=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296},train=[],validation=[];
for(const label of [...new Set(rows.map(r=>r.label))].sort()){const group=rows.filter(r=>r.label===label).map(r=>structuredClone(r));for(let i=group.length-1;i>0;i--){const j=Math.floor(rand()*(i+1));[group[i],group[j]]=[group[j],group[i]]}const n=group.length<2?0:Math.max(1,Math.min(group.length-1,Math.round(group.length*Math.max(.1,Math.min(.5,fraction)))));validation.push(...group.slice(0,n));train.push(...group.slice(n))}
return {train,validation};
}
export function predict(train,features,k,{scales=[],tie='abstain',labels=[]}={}){
const near=train.map((r,index)=>({...r,distance:Math.hypot(...r.features.map((x,i)=>(x-features[i])/(scales[i]||1))),index})).sort((a,b)=>a.distance-b.distance||String(a.id).localeCompare(String(b.id))).slice(0,Math.max(1,Math.round(k)));
const votes=Object.fromEntries(labels.map(l=>[l,0]));for(const row of near)votes[row.label]=(votes[row.label]||0)+1;
const ranked=Object.entries(votes).sort((a,b)=>b[1]-a[1]),tied=ranked.length>1&&ranked[0][1]===ranked[1][1],label=!near.length?null:tied&&tie==='abstain'?null:ranked[0][0];
return {label,near,votes};
}
export function score(train,validation,k,options={}){
const labels=options.labels||[...new Set([...train,...validation].map(r=>r.label))].sort(),cases=validation.map(row=>({...row,...predict(train,row.features,k,{...options,labels}),actual:row.label})),correct=cases.filter(r=>r.actual===r.label).length;
const confusion=labels.map(actual=>[...labels,null].map(predicted=>cases.filter(r=>r.actual===actual&&r.label===predicted).length));
const recall=labels.map((label,i)=>{const n=cases.filter(r=>r.actual===label).length;return {label,n,value:n?confusion[i][i]/n:null}}),measured=recall.filter(r=>r.value!==null);
const counts=labels.map(l=>[l,train.filter(r=>r.label===l).length]).sort((a,b)=>b[1]-a[1]),majority=counts[0]?.[0]||null;
return {total:cases.length,correct,accuracy:cases.length?correct/cases.length:null,balanced:measured.length?measured.reduce((s,r)=>s+r.value,0)/measured.length:null,labels,confusion,recall,cases,majority,baseline:cases.length?cases.filter(r=>r.actual===majority).length/cases.length:null};
}
export function alterTraining(rows,{exclude='',noise=0,labels=[]}={}){
const train=rows.filter(r=>r.label!==exclude).map(r=>structuredClone(r)),n=Math.floor(train.length*Math.max(0,Math.min(50,noise))/100);
let state=12345;const order=train.map((_,i)=>i);for(let i=order.length-1;i>0;i--){state=(Math.imul(state,1664525)+1013904223)>>>0;const j=Math.floor(state/4294967296*(i+1));[order[i],order[j]]=[order[j],order[i]]}for(let i=0;i<n;i++){const row=train[order[i]],at=labels.indexOf(row.label);if(labels.length>1)row.label=labels[(at+1)%labels.length]}
return {train,changed:labels.length>1?n:0,removed:rows.length-train.length};
}