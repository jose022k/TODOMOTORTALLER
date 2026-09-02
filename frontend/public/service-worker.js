/* Todomotortaller Production Service Worker v3 */
const CACHE_NAME = 'todomotortaller-v3';

self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

// Web Push: runs in background even when screen is off / app is closed
self.addEventListener('push', (event) => {
  let parsed = null;
  if (event.data) {
    try { parsed = event.data.json(); }
    catch { try { parsed = { title: "Todomotortaller", body: event.data.text() }; } catch { parsed = null; } }
  }

  const title    = (parsed && parsed.title) || 'Todomotortaller';
  const body     = (parsed && parsed.body)  || 'Tienes una nueva notificación';
  const icon     = new URL((parsed && parsed.icon)  || '/img/app-icon-192.png', self.location.origin).href;
  const badge    = new URL((parsed && parsed.badge) || '/img/app-icon-192.png', self.location.origin).href;
  const pushData = (parsed && parsed.data) || {};
  const count    = (typeof pushData.unread_count === 'number') ? pushData.unread_count : 1;

  const pushTask = (async () => {
    // 1. Update app icon badge on PWA home screen
    try {
      if ('setAppBadge' in self)      { count > 0 ? await self.setAppBadge(count) : await self.clearAppBadge(); }
      if ('setAppBadge' in navigator) { count > 0 ? await navigator.setAppBadge(count) : await navigator.clearAppBadge(); }
    } catch { /* ignore */ }

    // 2. Check if user currently has an active, visible tab open
    const wins = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
    const isVisible = wins.some((w) => w.visibilityState === 'visible');

    // Notify open windows so live lists refresh
    for (const w of wins) {
      w.postMessage({
        type: 'PUSH_RECEIVED',
        data: { ...(parsed || {}), ...pushData },
        unreadCount: count,
      });
    }

    // 3. Only trigger OS status bar notification if app is in BACKGROUND or SCREEN OFF
    // (If foreground, NotificationNative.vue handles single display to avoid duplicates)
    if (!isVisible) {
      const notifOpts = {
        body,
        icon,
        badge,
        data: pushData,
        vibrate: [400, 150, 400, 150, 400],
        silent: false,
        requireInteraction: false,
        tag: pushData.id ? 'notif-' + pushData.id : 'notif-' + Date.now(),
        renotify: true,
        timestamp: Date.now(),
      };
      await self.registration.showNotification(title, notifOpts);
    }
  })();

  event.waitUntil(pushTask);
});

// Notification tap → open / focus the app
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || '/';
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((wins) => {
      const hit = wins.find((w) => {
        try {
          return new URL(w.url).origin === self.location.origin;
        } catch { return false; }
      });
      if (hit) {
        hit.navigate(url);
        hit.focus();
      } else {
        self.clients.openWindow(url);
      }
    })
  );
});

self.addEventListener('notificationclose', () => {});
