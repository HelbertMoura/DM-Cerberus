// Service Worker — Dev Maniac's Hub
// Versão: 1.0.0 · 22/08/2026
// Estratégia: network-first pra HTML, cache-first pra assets estáticos

const CACHE_VERSION = 'dm-hub-v1';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;

const STATIC_ASSETS = [
  '/',
  '/login.html',
  '/dashboard.html',
  '/styles.css',
  '/app.js',
  '/manifest.webmanifest',
  '/assets/brand/dev-maniacs-mark.png',
  '/assets/brand/dev-maniacs-mascot.webp',
  '/assets/brand/dev-maniacs-social-card.png',
];

// ========== INSTALL ==========
self.addEventListener('install', (event) => {
  console.log('[SW] Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      console.log('[SW] Caching static assets');
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// ========== ACTIVATE ==========
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating...');
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys
          .filter((key) => key !== STATIC_CACHE && key !== DYNAMIC_CACHE)
          .map((key) => {
            console.log('[SW] Removing old cache:', key);
            return caches.delete(key);
          })
      );
    })
  );
  self.clients.claim();
});

// ========== FETCH ==========
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignora requests pra outros domínios (APIs externas, etc)
  if (url.origin !== location.origin) return;

  // ========== HTML: network-first ==========
  if (request.mode === 'navigate' || request.headers.get('accept').includes('text/html')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const clone = response.clone();
          caches.open(DYNAMIC_CACHE).then((cache) => cache.put(request, clone));
          return response;
        })
        .catch(() => caches.match(request).then((r) => r || caches.match('/login.html')))
    );
    return;
  }

  // ========== Assets: cache-first ==========
  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;
      return fetch(request).then((response) => {
        if (response.status === 200) {
          const clone = response.clone();
          caches.open(STATIC_CACHE).then((cache) => cache.put(request, clone));
        }
        return response;
      });
    })
  );
});

// ========== BACKGROUND SYNC (futuro) ==========
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-audit-log') {
    console.log('[SW] Background sync: audit log');
  }
});

// ========== PUSH (futuro) ==========
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : { title: 'DM Hub', body: 'Nova notificação' };
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/assets/brand/dev-maniacs-mark.png',
      badge: '/assets/brand/dev-maniacs-mark.png',
      tag: 'dm-hub-notification',
      requireInteraction: false,
    })
  );
});
