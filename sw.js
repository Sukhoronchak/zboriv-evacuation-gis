// sw.js - Сервіс-воркер для активації PWA функцій
self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
    // Просто пропускаємо запити через мережу
    event.respondWith(fetch(event.request));
});self.addEventListener('install', (e) => {
  console.log('Service Worker installed');
});

self.addEventListener('fetch', (e) => {
  // Просто пропускаємо запити
});

self.addEventListener('push', function(event) {
    // Це дозволить системі знати, що ми очікуємо дані
});
