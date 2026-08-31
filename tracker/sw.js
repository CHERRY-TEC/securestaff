const CACHE='rbm-tracker-v3';
const ASSETS=['./','./index.html','./rbm-logo.png','./manifest.json'];
self.addEventListener('install', e=>{ e.waitUntil(caches.open(CACHE).then(c=> c.addAll(ASSETS).catch(()=>{}))); self.skipWaiting(); });
self.addEventListener('activate', e=>{ e.waitUntil(caches.keys().then(k=> Promise.all(k.filter(x=>x!==CACHE).map(x=> caches.delete(x))))); self.clients.claim(); });
self.addEventListener('fetch', e=>{ e.respondWith(caches.match(e.request).then(r=> r|| fetch(e.request))); });
