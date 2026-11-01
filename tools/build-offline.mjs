import fs from 'node:fs';
const cat=JSON.parse(fs.readFileSync('public/catalog.json','utf8'));const shell=['/','/index.html','/icon.svg','/manifest.webmanifest','/catalog.json',...fs.readdirSync('dist/assets').map(x=>'/assets/'+x),...fs.readdirSync('dist/fonts').map(x=>'/fonts/'+x)];
fs.writeFileSync('dist/sw.js',`const VERSION=${JSON.stringify(cat.version)},SHELL='anatomy-shell-'+VERSION,PACKS='anatomy-packs-'+VERSION;const FILES=${JSON.stringify(shell)};
self.addEventListener('install',e=>{e.waitUntil(caches.open(SHELL).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(self.clients.claim());});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(u.origin!==self.location.origin||e.request.method!=='GET')return;const pack=u.pathname.startsWith('/packs/')||u.pathname.startsWith('/software/');e.respondWith(caches.open(pack?PACKS:SHELL).then(async c=>{const hit=await c.match(e.request);if(hit)return hit;try{const r=await fetch(e.request);if(r.ok&&(pack||FILES.includes(u.pathname)))await c.put(e.request,r.clone());return r;}catch(err){if(e.request.mode==='navigate')return await c.match('/index.html');throw err;}}));});`);
console.log('Offline shell generated:',shell.length,'files');
