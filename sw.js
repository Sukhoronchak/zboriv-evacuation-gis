// sw.js - Сервіс-воркер для ГІС Евакуація Зборів (Версія 5 - Фоновий режим)

// 1. Встановлення: активуємо новий воркер негайно
self.addEventListener('install', (event) => {
    console.log('SW: Встановлено');
    self.skipWaiting();
});

// 2. Активація: беремо контроль над усіма клієнтами (вкладками)
self.addEventListener('activate', (event) => {
    console.log('SW: Активовано');
    event.waitUntil(clients.claim());
});

// 3. Обробка запитів (Fetch): виправлення TypeError при помилках мережі
self.addEventListener('fetch', (event) => {
    event.respondWith(
        fetch(event.request).catch(err => {
            console.warn('SW: Помилка мережі або CORS:', event.request.url);
            return new Response('Network error', { status: 408 });
        })
    );
});

// 4. Опрацювання фонових сповіщень (Push)
self.addEventListener('push', function(event) {
    console.log('SW: Отримано сигнал Push');
    
    let title = '🚨 ТРИВОГА: ЗБОРІВ';
    let options = {
        body: 'Виявлено нову загрозу! Терміново перевірте карту та маршрути евакуації.',
        icon: 'https://cdn-icons-png.flaticon.com/512/564/564440.png',
        badge: 'https://cdn-icons-png.flaticon.com/512/564/564440.png',
        vibrate: [500, 100, 500, 100, 500], // Потужна вібрація
        data: { dateOfArrival: Date.now() },
        actions: [
            { action: 'explore', title: 'Відкрити карту' }
        ]
    };

    event.waitUntil(self.registration.showNotification(title, options));
});

// 5. Обробка кліку на сповіщення: фокусування вікна або відкриття нової вкладки
self.addEventListener('notificationclick', function(event) {
    event.notification.close(); // Закриваємо банер

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
            // Шукаємо вже відкриту вкладку нашого сайту
            for (let i = 0; i < clientList.length; i++) {
                let client = clientList[i];
                if (client.url.includes(self.location.origin) && 'focus' in client) {
                    return client.focus();
                }
            }
            // Якщо вкладку не знайдено — відкриваємо нову (шлях ./ для GitHub Pages)
            if (clients.openWindow) {
                return clients.openWindow('./'); 
            }
        })
    );
});// sw.js - Сервіс-воркер для ГІС Евакуація Зборів (Версія 4 - CORS Fix)

// 1. Встановлення: активуємо негайно
self.addEventListener('install', (event) => {
    console.log('SW: Встановлено');
    self.skipWaiting();
});

// 2. Активація: контроль над усіма вкладками
self.addEventListener('activate', (event) => {
    console.log('SW: Активовано');
    event.waitUntil(clients.claim());
});

// 3. ОБРОБКА ЗАПИТІВ (Виправлено для запобігання TypeError)
self.addEventListener('fetch', (event) => {
    event.respondWith(
        fetch(event.request).catch(err => {
            console.warn('SW: Помилка мережі або CORS при запиті:', event.request.url);
            // Повертаємо порожню відповідь, щоб не "валити" проміс воркера
            return new Response('Network error', { status: 408, statusText: 'Network Error or CORS blocked' });
        })
    );
});

// 4. Очікування Push-повідомлень
self.addEventListener('push', function(event) {
    console.log('SW: Отримано сигнал Push');
});

// 5. Оновлена обробка кліку: фокусування вікна та виправлення 404
self.addEventListener('notificationclick', function(event) {
    event.notification.close();

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
            for (let i = 0; i < clientList.length; i++) {
                let client = clientList[i];
                if (client.url.includes(self.location.origin) && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow('./'); 
            }
        })
    );
});
