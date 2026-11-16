import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const context={};vm.createContext(context);vm.runInContext(fs.readFileSync('web/class/20261117/algorithm-motion.js','utf8'),context);const M=context.AlgorithmMotionModel;
const data=M.dataset();
test('motion source uses only exact black and white without blending attributes',()=>{
const source=fs.readFileSync('web/class/20261117/algorithm-motion.js','utf8');const colors=[...source.matchAll(/#[0-9a-f]{3,8}/gi)].map(match=>match[0].toLowerCase());
assert(colors.length>0);assert(colors.every(color=>color==='#000000'||color==='#ffffff'));assert(!/\b(?:opacity|rgba|hsla)\b/i.test(source));assert(!source.includes('최종 배경'));
});
test('logistic training lowers log loss and prediction matches displayed sigmoid',()=>{
const model=M.logisticTrain(data,1);assert(model.loss<Math.log(2));
for(const query of [{x:.8,y:.8},{x:-.8,y:-.8},{x:.1,y:-.1}]){assert.equal(model.predict(query),model.probability(query)>=.5?1:0);assert(Math.abs(model.probability(query)-M.sigmoid(model.w[0]*query.x+model.w[1]*query.y+model.b))<1e-12);}
assert(M.logisticTrain(data,.1).w.reduce((s,v)=>s+v*v,0)<M.logisticTrain(data,10).w.reduce((s,v)=>s+v*v,0));
});
test('K-NN uses actual nearest distances and its vote changes with K',()=>{
const points=[{x:0,y:0,label:0,id:0},{x:.1,y:0,label:1,id:1},{x:.2,y:0,label:1,id:2}];const query={x:.01,y:0};
assert.equal(M.knn(points,query,1).prediction,0);assert.equal(M.knn(points,query,3).prediction,1);const sorted=M.knn(points,query,3).neighbors;assert.equal(sorted[0].id,0);assert(sorted.every((p,i)=>i===0||p.distance>=sorted[i-1].distance));
});
test('CART split reduces impurity and path decisions match the query',()=>{
const tree=M.cartTrain(data,4);assert.equal(tree.leaf,false);assert(tree.gain>0);
for(const query of data){const result=M.treePath(tree,query);for(const step of result.path)assert.equal(step.direction,query[step.node.feature]<=step.node.threshold?'left':'right');assert.equal(result.prediction,result.leaf.counts[1]>result.leaf.counts[0]?1:0);assert(result.path.length<=4);}
});
test('forest bootstrap and feature sampling are repeatable; visible votes equal final decision',()=>{
const forest=M.forestTrain(data,4,42,5),again=M.forestTrain(data,4,42,5);assert.equal(JSON.stringify(forest),JSON.stringify(again));assert(forest.samples.every(sample=>sample.length===data.length));assert(forest.samples.some(sample=>new Set(sample.map(p=>p.id)).size<data.length));
const result=M.forestVote(forest,{x:.1,y:.1});assert.equal(result.zero+result.one,5);assert.equal(result.prediction,result.one>2?1:0);assert.equal(JSON.stringify(result.votes),JSON.stringify(forest.trees.map(tree=>M.predictTree(tree,{x:.1,y:.1}))));
});
test('RBF SVM solves nonlinear XOR and obeys dual bounds and equality',()=>{
const points=[{x:-.8,y:-.8,label:0},{x:.8,y:.8,label:0},{x:-.8,y:.8,label:1},{x:.8,y:-.8,label:1}];
const model=M.svmTrain(points,10,2);assert(points.every(point=>model.predict(point)===point.label));assert(model.alpha.every(a=>a>=-1e-7&&a<=10+1e-7));assert(Math.abs(model.alpha.reduce((sum,a,i)=>sum+a*(points[i].label?1:-1),0))<1e-6);assert(model.support.length>0);
for(const support of model.support)assert(model.alpha[support.index]>1e-6);
});
test('SVM scene uses finite real decision scores for every configured C',()=>{
for(const C of [.1,1,10]){const model=M.svmTrain(data,C,2);assert(model.support.length>0);assert(Number.isFinite(model.b));for(const [i,point] of data.entries()){const margin=(point.label?1:-1)*model.score(point);assert(Number.isFinite(margin));if(model.alpha[i]<1e-7)assert(margin>=1-.01);else if(model.alpha[i]>C-1e-7)assert(margin<=1+.01);else assert(Math.abs(margin-1)<.01);}assert(Math.abs(model.alpha.reduce((sum,a,i)=>sum+a*(data[i].label?1:-1),0))<1e-5);}
});
