import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createWorker} from '../server/worker.mjs';

const directory=path.resolve('web/class/20261117/downloads');
const manifest=JSON.parse(fs.readFileSync(path.join(directory,'manifest.json'),'utf8'));
test('published dataset hash and all five copyable Python scripts agree',()=>{
const bytes=fs.readFileSync(path.join(directory,'students-v1.csv'));
assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),manifest.sha256);
assert.equal(manifest.splits.train.rows,389);assert.equal(manifest.splits.validation.rows,130);assert.equal(manifest.splits.test.rows,130);
assert.equal(new Set(manifest.validation_row_ids).size,130);
assert(!fs.readdirSync(directory).some(file=>file.endsWith('.ipynb')));
const blocks=JSON.parse(fs.readFileSync(path.join(directory,'code-blocks.json'),'utf8'));
for(const spec of manifest.algorithms){assert(spec.filename.endsWith('.py'));const code=fs.readFileSync(path.join(directory,spec.filename),'utf8');assert(code.includes(manifest.sha256));assert(code.includes('RUN_FINAL_TEST = False'));assert(code.includes(`ALGORITHM = '${spec.id}'`));assert(code.includes('files.upload()'));assert(!code.includes('urlopen'));assert.equal(blocks[spec.id].length,5);assert(blocks[spec.id].every(part=>code.includes(part.code)));}
});
test('worker preserves binary ZIP bytes and supplies real download MIME types',async()=>{
const zip=fs.readFileSync(path.join(directory,'lesson-kit.zip'));
const code=fs.readFileSync(path.join(directory,'01-logistic-regression.py'),'utf8');
const worker=createWorker({'/kit.zip':{base64:zip.toString('base64')},'/lesson.py':code,'/students.csv':'x,y\n1,0\n'},()=>{throw Error('not an AI request')});
const response=await worker.fetch(new Request('https://test.invalid/kit.zip'),{});
assert.equal(response.headers.get('content-type'),'application/zip');assert.equal(response.headers.get('content-disposition'),'attachment; filename="kit.zip"');assert.deepEqual(Buffer.from(await response.arrayBuffer()),zip);
const head=await worker.fetch(new Request('https://test.invalid/kit.zip',{method:'HEAD'}),{});assert.equal((await head.arrayBuffer()).byteLength,0);assert.equal(head.headers.get('content-type'),'application/zip');
const python=await worker.fetch(new Request('https://test.invalid/lesson.py'),{});assert.equal(python.headers.get('content-type'),'text/x-python; charset=utf-8');assert.equal(await python.text(),code);
const csv=await worker.fetch(new Request('https://test.invalid/students.csv'),{});assert.equal(csv.headers.get('content-type'),'text/csv; charset=utf-8');
});
test('reference reports preserve the comparison population and confusion matrix arithmetic',()=>{
for(const spec of manifest.algorithms){const report=JSON.parse(fs.readFileSync(path.join(directory,`reference-${spec.id}.json`),'utf8'));assert.equal(report.scope,'validation');assert.equal(report.dataset_sha256,manifest.sha256);assert.deepEqual(report.validation_row_ids,manifest.validation_row_ids);assert.equal(report.runs.length,3);assert.equal(report.stress.length,3);for(const metric of [report.baseline,...report.runs,...report.stress]){assert.equal(metric.n,130);assert.equal(metric.tn+metric.fp,110);assert.equal(metric.tp+metric.fn,20);assert.equal(metric.accuracy,(metric.tn+metric.tp)/130);assert.equal(metric.recall_below_10,metric.tp/20);}}
});

test('lesson styles use only pure black or white and pages omit unwanted labels',()=>{
const css=fs.readFileSync(path.resolve('web/class/20261117/lesson.css'),'utf8');
const colors=css.match(/#[0-9a-fA-F]{3,8}\b/g)||[];
assert(colors.length>0);assert(colors.every(color=>['#000000','#ffffff'].includes(color.toLowerCase())));
assert(!/opacity\s*:\s*0?\.\d/.test(css));
const pages=['index','data','practice','results','notes'].map(name=>name+'.html').concat(manifest.algorithms.map(a=>'algorithms/'+a.id+'.html'));
for(const name of pages){const html=fs.readFileSync(path.resolve('web/class/20261117',name),'utf8');for(const label of ['가천대학교 머신러닝','브라우저 내 기록 저장','ML 실험실','ML · DATA · HUMAN DECISIONS'])assert(!html.includes(label),name+' contains '+label);}
for(const a of manifest.algorithms){const html=fs.readFileSync(path.resolve('web/class/20261117/algorithms',a.id+'.html'),'utf8');for(const control of a.controls)assert(html.includes(control.variable));assert(!html.includes('data-code-variable'));assert(html.includes('코랩에서 위 변수 직접 수정'));}
});

test('algorithm practice integrates prediction and transfer without separate agenda pages',()=>{
const root=path.resolve('web/class/20261117');
assert(!fs.existsSync(path.join(root,'productivity.html')));assert(!fs.existsSync(path.join(root,'education.html')));
for(const file of ['index.html','practice.html',...manifest.algorithms.map(a=>'algorithms/'+a.id+'.html')]){const html=fs.readFileSync(path.join(root,file),'utf8');assert(!html.includes('productivity.html'));assert(!html.includes('education.html'));assert(!html.includes('>생산성<'));assert(!html.includes('>교육학<'));}
for(const a of manifest.algorithms){const html=fs.readFileSync(path.join(root,'algorithms',a.id+'.html'),'utf8');assert(html.includes('data-note="'+a.id+'_forecast"'));assert(html.includes('data-note="'+a.id+'_errorcase"'));assert(html.includes('data-note="'+a.id+'_transfer"'));assert(html.includes('AI 도움 없는 2문장 설명'));}
});
