// Finance Alerts service worker: shows pushed alerts and keeps the last 50 on the phone.
const SHELL = 'finance-alerts-v1';
const FILES = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'badge-96.png'];

self.addEventListener('install', e => { e.waitUntil(caches.open(SHELL).then(c => c.addAll(FILES))); self.skipWaiting(); });
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== SHELL).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(fetch(e.request).then(r => { const c = r.clone(); caches.open(SHELL).then(s => s.put(e.request, c)); return r; })
    .catch(() => caches.match(e.request)));
});

function db() {
  return new Promise((ok, bad) => {
    const r = indexedDB.open('finance-alerts', 1);
    r.onupgradeneeded = () => r.result.createObjectStore('alerts', { keyPath: 'at' });
    r.onsuccess = () => ok(r.result); r.onerror = () => bad(r.error);
  });
}
async function remember(a) {
  const d = await db();
  await new Promise(ok => { const t = d.transaction('alerts', 'readwrite'); t.objectStore('alerts').put(a); t.oncomplete = ok; t.onerror = ok; });
  const keys = await new Promise(ok => { const r = d.transaction('alerts').objectStore('alerts').getAllKeys(); r.onsuccess = () => ok(r.result); r.onerror = () => ok([]); });
  if (keys.length > 50) { const t = d.transaction('alerts', 'readwrite'); keys.slice(0, keys.length - 50).forEach(k => t.objectStore('alerts').delete(k)); }
}

self.addEventListener('push', e => {
  let p = {};
  try { p = e.data ? e.data.json() : {}; } catch { p = { body: e.data && e.data.text() }; }
  const a = { at: Date.now(), title: p.title || 'Finance alert', body: p.body || '', asOf: p.asOf || null };
  e.waitUntil(Promise.all([
    remember(a).catch(() => {}),
    self.registration.showNotification(a.title, { body: a.body, tag: p.tag || 'finance', icon: 'icon-192.png', badge: 'badge-96.png', data: { at: a.at } }),
    self.clients.matchAll({ type: 'window' }).then(cs => cs.forEach(c => c.postMessage({ type: 'alert' }))),
  ]));
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(cs => {
    const c = cs.find(x => new URL(x.url).pathname.startsWith('/alerts/'));
    return c ? c.focus() : self.clients.openWindow('./');
  }));
});
