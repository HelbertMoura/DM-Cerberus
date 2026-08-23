// Service Worker — Dev Maniac's Hub
// Versão: 3.1.0 · 23/08/2026 (fix: SW nao cacheava 2FA setup, forcar reload)
// Estrategia: network-first pra HTML, cache-first pra assets estaticos,
// rotas de auth/health SEMPRE na rede (nunca cache).
// REGRA: qualquer mudanca em styles.css/app.js/icones exige bump do CACHE_VERSION.

const CACHE_VERSION = 'dm-hub-v11';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;

const STATIC_ASSETS = [
  '/',
  '/login',                  // novo login Astro (v2)
  '/login.html',             // legacy fallback
  '/login.css',              // CSS legacy
  '/hub.html',
  '/status.html',
  '/dashboard.html',
  '/offline.html',
  '/styles.css',
  '/app.js',
  '/manifest.webmanifest',
  '/assets/brand/dev-maniacs-mark.png',
  '/assets/brand/dev-maniacs-mascot.webp',
  '/assets/brand/dev-maniacs-icon-32.png',
  '/assets/brand/dev-maniacs-icon-180.png',
  '/assets/brand/dev-maniacs-icon-192.png',
  '/assets/brand/dev-maniacs-icon-512.png',
];

// Nunca cachear (sessao/health/oauth mudam a cada request)
const NEVER_CACHE = ['/auth/', '/api/', '/health.php'];

// ========== INSTALL ==========
self.addEventListener('install', (event) => {
  console.log('[SW] Installing v11...');
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// ========== ACTIVATE ==========
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating v11...');
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys
          .filter((key) => key !== STATIC_CACHE && key !== DYNAMIC_CACHE)
          .map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// ========== FETCH ==========
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // So mesmo origin; ignora Google Fonts, code-server etc
  if (url.origin !== location.origin) return;

  // Rotas dinamicas: sempre rede (sem cache, sem fallback offline)
  if (NEVER_CACHE.some((p) => url.pathname.startsWith(p))) return;

  // HTML: network-first com fallback offline
  if (request.mode === 'navigate' || (request.headers.get('accept') || '').includes('text/html')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const clone = response.clone();
          caches.open(DYNAMIC_CACHE).then((cache) => cache.put(request, clone));
          return response;
        })
        .catch(() =>
          caches.match(request).then((r) => r || caches.match('/offline.html'))
        )
    );
    return;
  }

  // Assets: cache-first
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
  const data = event.data ? event.data.json() : { title: 'DM Hub', body: 'Nova notificacao' };
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/assets/brand/dev-maniacs-icon-192.png',
      badge: '/assets/brand/dev-maniacs-icon-32.png',
      tag: 'dm-hub-notification',
      requireInteraction: false,
    })
  );
});