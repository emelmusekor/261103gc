export const createWorker=function createWorker(assets,analyze){
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml'};
return {async fetch(request,env){
const url=new URL(request.url);if(url.pathname.startsWith('/api/'))return analyze(request,env);
if(!['GET','HEAD'].includes(request.method))return new Response('Method not allowed',{status:405});
let name;try{name=decodeURIComponent(url.pathname)}catch{return new Response('Bad path',{status:400})}
if(name.endsWith('/'))name+='index.html';if(!Object.hasOwn(assets,name)&&Object.hasOwn(assets,name+'.html'))name+='.html';
if(!Object.hasOwn(assets,name))return new Response(assets['/404.html']||'Not found',{status:404,headers:{'content-type':'text/html; charset=utf-8'}});
const ext=name.slice(name.lastIndexOf('.'));return new Response(request.method==='HEAD'?null:assets[name],{headers:{'content-type':types[ext]||'text/plain; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff','referrer-policy':'same-origin'}});
}};
};
