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
});

// 5. Оновлена обробка кліку: виправляє помилку 404 та фокусує вікно
self.addEventListener('notificationclick', function(event) {
    event.notification.close(); // Закриваємо банер сповіщення

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
            // Перевіряємо, чи застосунок уже відкритий у якійсь вкладці
            for (let i = 0; i < clientList.length; i++) {
                let client = clientList[i];
                // Якщо знайдено відкриту вкладку нашого сайту — фокусуємося на ній
                if (client.url.includes(self.location.origin) && 'focus' in client) {
                    return client.focus();
                }
            }
            // Якщо застосунок закритий — відкриваємо головну сторінку (відносно sw.js)
            if (clients.openWindow) {
                return clients.openWindow('./'); 
            }
        })
    );
});
