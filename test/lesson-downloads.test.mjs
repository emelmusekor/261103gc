import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {gunzipSync} from 'node:zlib';
import {createWorker} from '../server/worker.mjs';

const directory=path.resolve('web/class/20261117/downloads');
const manifest=JSON.parse(fs.readFileSync(path.join(directory,'manifest.json'),'utf8'));
test('published dataset hash and all five notebook identities agree',()=>{
const bytes=fs.readFileSync(path.join(directory,'students-v1.csv'));
assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),manifest.sha256);
assert.equal(manifest.splits.train.rows,389);assert.equal(manifest.splits.validation.rows,130);assert.equal(manifest.splits.test.rows,130);
assert.equal(new Set(manifest.validation_row_ids).size,130);
for(const spec of manifest.algorithms){const notebook=JSON.parse(fs.readFileSync(path.join(directory,spec.filename),'utf8'));assert.equal(notebook.nbformat,4);const code=notebook.cells.filter(c=>c.cell_type==='code').map(c=>c.source.join('')).join('\n');assert(code.includes(manifest.sha256));assert(code.includes('RUN_FINAL_TEST = False'));assert(code.includes(`ALGORITHM = '${spec.id}'`));assert(!code.includes('urlopen'));const embedded=code.match(/EMBEDDED_CSV_GZIP_BASE64 = "([A-Za-z0-9+/=]+)"/);assert(embedded);assert.deepEqual(gunzipSync(Buffer.from(embedded[1],'base64')),bytes);assert(notebook.cells.filter(c=>c.cell_type==='code').every(c=>c.outputs.length===0&&c.execution_count===null));}
});
test('worker preserves binary ZIP bytes and supplies real download MIME types',async()=>{
const zip=fs.readFileSync(path.join(directory,'lesson-kit.zip'));
const notebook=fs.readFileSync(path.join(directory,'01-logistic-regression.ipynb'),'utf8');
const worker=createWorker({'/kit.zip':{base64:zip.toString('base64')},'/lesson.ipynb':notebook,'/students.csv':'x,y\n1,0\n'},()=>{throw Error('not an AI request')});
const response=await worker.fetch(new Request('https://test.invalid/kit.zip'),{});
assert.equal(response.headers.get('content-type'),'application/zip');assert.equal(response.headers.get('content-disposition'),'attachment; filename="kit.zip"');assert.deepEqual(Buffer.from(await response.arrayBuffer()),zip);
const head=await worker.fetch(new Request('https://test.invalid/kit.zip',{method:'HEAD'}),{});assert.equal((await head.arrayBuffer()).byteLength,0);assert.equal(head.headers.get('content-type'),'application/zip');
const ipynb=await worker.fetch(new Request('https://test.invalid/lesson.ipynb'),{});assert.equal(ipynb.headers.get('content-type'),'application/x-ipynb+json');assert.equal((await ipynb.json()).nbformat,4);
const csv=await worker.fetch(new Request('https://test.invalid/students.csv'),{});assert.equal(csv.headers.get('content-type'),'text/csv; charset=utf-8');
});
test('reference reports preserve the comparison population and confusion matrix arithmetic',()=>{
for(const spec of manifest.algorithms){const report=JSON.parse(fs.readFileSync(path.join(directory,`reference-${spec.id}.json`),'utf8'));assert.equal(report.scope,'validation');assert.equal(report.dataset_sha256,manifest.sha256);assert.deepEqual(report.validation_row_ids,manifest.validation_row_ids);assert.equal(report.runs.length,3);assert.equal(report.stress.length,3);for(const metric of [report.baseline,...report.runs,...report.stress]){assert.equal(metric.n,130);assert.equal(metric.tn+metric.fp,110);assert.equal(metric.tp+metric.fn,20);assert.equal(metric.accuracy,(metric.tn+metric.tp)/130);assert.equal(metric.recall_below_10,metric.tp/20);}}
});
