
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {handleAI} from './ai.mjs';
const root=path.resolve('web'),env={};
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml'};
let server;
async function handler(req,res){
 try{
 const url=new URL(req.url,'http://127.0.0.1:4173');
 if(url.pathname.startsWith('/api/')){
 const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>4100000){res.writeHead(413);res.end();return}chunks.push(chunk)}
 const request=new Request(url,{method:req.method,headers:req.headers,body:['GET','HEAD'].includes(req.method)?undefined:Buffer.concat(chunks)});
 const response=await handleAI(request,env);res.writeHead(response.status,Object.fromEntries(response.headers));res.end(Buffer.from(await response.arrayBuffer()));return;
 }
 let file=path.resolve(root,'.'+decodeURIComponent(url.pathname));if(file!==root&&!file.startsWith(root+path.sep))throw Error();
 if(!fs.existsSync(file)&&fs.existsSync(file+'.html'))file+='.html';
 if(fs.statSync(file).isDirectory())file=path.join(file,'index.html');
 res.writeHead(200,{'content-type':mime[path.extname(file)]||'application/octet-stream','cache-control':'no-store'});fs.createReadStream(file).pipe(res);
 }catch{res.writeHead(404);res.end('Not found')}
}
if(process.argv.includes('--stdin-secret')){
 let buffer='';if(process.stdin.isTTY)process.stdin.setRawMode(true);
 process.stdin.setEncoding('utf8');process.stdin.on('data',chunk=>{
 buffer+=chunk;const i=buffer.search(/[\r\n]/);if(i<0)return;
 const line=buffer.slice(0,i);buffer=buffer.slice(i+1).replace(/^[\r\n]+/,'');
 let config;try{config=JSON.parse(line)}catch{console.error('Invalid configuration');return}
 if(config.stop){server?.close(()=>process.exit(0));return}
 env.GEMINI_API_KEY=config.key;env.GEMINI_MODEL=config.model||'gemini-3.5-flash';
 if(!server)server=http.createServer(handler).listen(4173,'127.0.0.1',()=>console.log('Local: http://127.0.0.1:4173'));
 });process.stdin.resume();console.log('Ready for server configuration on hidden stdin.');
}else{
 env.GEMINI_API_KEY=process.env.GEMINI_API_KEY;env.GEMINI_MODEL=process.env.GEMINI_MODEL;
 server=http.createServer(handler).listen(4173,'127.0.0.1',()=>console.log('Local: http://127.0.0.1:4173'));
}
