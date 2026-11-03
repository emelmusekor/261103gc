(function buildWorker(){
const fs=require('fs'),path=require('path'),root=path.resolve(__dirname,'..'),web=path.join(root,'web'),dist=path.join(root,'dist');
if(path.basename(root)!=='261103gc'||dist!==path.join(root,'dist')||!dist.startsWith(root+path.sep)||!fs.existsSync(path.join(web,'index.html')))throw Error('Invalid build paths');
function walk(d){return fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>{const full=path.join(d,e.name);if(e.isSymbolicLink())throw Error('Symbolic links are not allowed');return e.isDirectory()?walk(full):[full]})}
const assets={};for(const f of walk(web)){const name='/'+path.relative(web,f).replaceAll(path.sep,'/');assets[name]=fs.readFileSync(f,'utf8');}
const core=fs.readFileSync(path.join(root,'server/ai.mjs'),'utf8').replace(/^export /gm,''),worker=fs.readFileSync(path.join(root,'server/worker.mjs'),'utf8').replace(/^export /gm,'');
const manifestPath=path.join(root,'.openai/hosting.json'),manifest=fs.existsSync(manifestPath)?JSON.parse(fs.readFileSync(manifestPath,'utf8')):{};delete manifest.static;
const bundle=core+'\n'+worker+'\nconst ASSETS='+JSON.stringify(assets)+';\nexport default createWorker(ASSETS,handleAI);\n';
console.log('Verified build target: '+dist);
fs.rmSync(dist,{recursive:true,force:true});fs.mkdirSync(path.join(dist,'server'),{recursive:true});fs.mkdirSync(path.join(dist,'.openai'),{recursive:true});
fs.writeFileSync(path.join(dist,'server/index.js'),bundle);fs.writeFileSync(path.join(dist,'.openai/hosting.json'),JSON.stringify(manifest));
if(fs.existsSync(manifestPath))fs.writeFileSync(manifestPath,JSON.stringify(manifest));
console.log(JSON.stringify({assets:Object.keys(assets).length,bytes:Buffer.byteLength(bundle),entry:'dist/server/index.js'}));
})();