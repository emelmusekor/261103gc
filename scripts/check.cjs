(function validateApp(){
const fs=require('fs'),path=require('path'),vm=require('vm'),root=path.resolve(__dirname,'..','web'),errors=[];
function walk(d){return fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(d,e.name)):[path.join(d,e.name)])}
for(const f of walk(root)){
if(f.endsWith('.js'))try{new vm.Script(fs.readFileSync(f,'utf8'))}catch(e){errors.push(path.relative(root,f)+': '+e.message)}
if(!f.endsWith('.html'))continue;const s=fs.readFileSync(f,'utf8');
for(const m of s.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g))try{new vm.Script(m[1])}catch(e){errors.push(path.relative(root,f)+': '+e.message)}
for(const m of s.matchAll(/(?:href|src)=["']([^"']+)["']/g)){const url=m[1];if(/^(?:https?:|data:|blob:|#|\$\{)/.test(url))continue;const file=url.split(/[?#]/)[0];if(file&&!fs.existsSync(path.resolve(path.dirname(f),file)))errors.push(path.relative(root,f)+' missing '+file);}
}
const home=fs.readFileSync(path.join(root,'index.html'),'utf8'),app=fs.readFileSync(path.join(root,'assets/app.js'),'utf8');if(/피드백|개선본|코드 보기/.test(home+app))errors.push('Management labels remain in learner navigation');
console.log(JSON.stringify({errors},null,2));if(errors.length)process.exitCode=1;
})();