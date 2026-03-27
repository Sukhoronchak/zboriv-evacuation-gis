// sw.js - Сервіс-воркер для ГІС Евакуація Зборів

// 1. Встановлення: змушуємо новий воркер активуватися негайно
self.addEventListener('install', (event) => {
    console.log('SW: Встановлено');
    self.skipWaiting();
});

// 2. Активація: беремо контроль над усіма вкладками одразу
self.addEventListener('activate', (event) => {
    console.log('SW: Активовано');
    event.waitUntil(clients.claim());
});

// 3. Обробка запитів: пропускаємо все через мережу (щоб дані завжди були свіжі)
self.addEventListener('fetch', (event) => {
    event.respondWith(fetch(event.request));
});

// 4. Очікування Push-повідомлень (зарезервовано для майбутнього)
self.addEventListener('push', function(event) {
    console.log('SW: Отримано сигнал Push');
    // Тут можна додати логіку відображення сповіщення, якщо сервер надішле сигнал
});

// 5. Обробка кліку на сповіщення (щоб відкривався застосунок)
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/')
    );
});
