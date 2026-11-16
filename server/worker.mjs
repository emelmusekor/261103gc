export const createWorker=function createWorker(assets,analyze){
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml','.csv':'text/csv; charset=utf-8','.ipynb':'application/x-ipynb+json','.txt':'text/plain; charset=utf-8','.zip':'application/zip'};
return {async fetch(request,env){
const url=new URL(request.url);if(url.pathname.startsWith('/api/'))return analyze(request,env);
if(!['GET','HEAD'].includes(request.method))return new Response('Method not allowed',{status:405});
let name;try{name=decodeURIComponent(url.pathname)}catch{return new Response('Bad path',{status:400})}
if(name.endsWith('/'))name+='index.html';if(!Object.hasOwn(assets,name)&&Object.hasOwn(assets,name+'.html'))name+='.html';
if(!Object.hasOwn(assets,name))return new Response(assets['/404.html']||'Not found',{status:404,headers:{'content-type':'text/html; charset=utf-8'}});
const ext=name.slice(name.lastIndexOf('.')),asset=assets[name];
const headers={'content-type':types[ext]||'text/plain; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff','referrer-policy':'same-origin'};
if(['.csv','.ipynb','.zip','.txt'].includes(ext))headers['content-disposition']='attachment; filename="'+name.slice(name.lastIndexOf('/')+1).replaceAll('"','')+'"';
let body=asset;if(asset&&typeof asset==='object'&&asset.base64)body=Uint8Array.from(atob(asset.base64),c=>c.charCodeAt(0));
return new Response(request.method==='HEAD'?null:body,{headers});
}};
};
