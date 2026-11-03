(function check(){
const fs=require('fs'),p=require('path'),vm=require('vm'),root=p.resolve(__dirname,'dist');
function walk(d){return fs.readdirSync(d,{withFileTypes:true}).flatMap(x=>x.isDirectory()?walk(p.join(d,x.name)):[p.join(d,x.name)])}
const files=walk(root);let failures=[];
for(const f of files.filter(x=>x.endsWith('.html'))){
const text=fs.readFileSync(f,'utf8');
for(const [i,m] of [...text.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].entries())try{new vm.Script(m[1])}catch(e){failures.push(p.relative(root,f)+' script '+i+': '+e.message)}
for(const m of text.matchAll(/(?:href|src)=["']([^"']+)["']/g)){let url=m[1];if(/^(?:https?:|data:|blob:|#|javascript:|\$\{)/.test(url))continue;url=url.split(/[?#]/)[0];if(!url)continue;const target=p.resolve(p.dirname(f),url);if(!fs.existsSync(target))failures.push(p.relative(root,f)+' missing '+url)}
}
for(const file of ['assets/app.js','assets/notebook.js'])try{new vm.Script(fs.readFileSync(p.join(root,file),'utf8'))}catch(e){failures.push(file+': '+e.message)}
console.log(JSON.stringify({files:files.length,failures},null,2));if(failures.length)process.exitCode=1;
})();