// Service Worker — Dev Maniac's Hub
// Versão: 3.0.0 · 23/08/2026 (migração login.html → /login Astro build)
// Estratégia: network-first pra HTML, cache-first pra assets estáticos,
// rotas de auth/health SEMPRE na rede (nunca cache).
// REGRA: qualquer mudança em styles.css/app.js/ícones exige bump do CACHE_VERSION.

const CACHE_VERSION = 'dm-hub-v10';
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
  '/assets/brand/dev-maniacs-mark.png',         // logo DM interno
  '/assets/brand/dev-maniacs-mascot.webp',      // asset avatar login
  '/assets/brand/dev-maniacs-icon-32.png',      // favicon
  '/assets/brand/dev-maniacs-icon-180.png',     // apple touch icon
  '/assets/brand/dev-maniacs-icon-192.png',     // PWA padrão
  '/assets/brand/dev-maniacs-icon-512.png',     // PWA maskable
];

// Nunca cachear (sessão/health/oauth mudam a cada request)
const NEVER_CACHE = ['/auth/', '/api/', '/health.php'];

// ========== INSTALL ==========
self.addEventListener('install', (event) => {
  console.log('[SW] Installing v2...');
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// ========== ACTIVATE ==========
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating v2...');
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

  // Só mesmo origin; ignora Google Fonts, code-server etc
  if (url.origin !== location.origin) return;

  // Rotas dinâmicas: sempre rede (sem cache, sem fallback offline)
  if (NEVER_CACHE.some((p) => url.pathname.startsWith(p))) return;

  // ========== HTML: network-first com fallback offline ==========
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
      icon: '/assets/brand/dev-maniacs-icon-192.png',
      badge: '/assets/brand/dev-maniacs-icon-32.png',
      tag: 'dm-hub-notification',
      requireInteraction: false,
    })
  );
});
