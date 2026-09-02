/* Todomotortaller Production Service Worker */
const CACHE_NAME = 'todomotortaller-v1';

self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

// Web Push Event Handler (runs in background even when app/browser is closed)
self.addEventListener('push', (event) => {
  if (!event.data) return;

  let parsed = null;
  try {
    parsed = event.data.json();
  } catch {
    parsed = null;
  }

  const title = (parsed && parsed.title) || 'Todomotortaller';
  const body = (parsed && parsed.body) || '';
  const iconPath = (parsed && parsed.icon) || '/img/app-icon-192.png';
  const badgePath = (parsed && parsed.badge) || '/img/app-icon-192.png';
  const icon = new URL(iconPath, self.location.origin).href;
  const badge = new URL(badgePath, self.location.origin).href;
  const pushData = (parsed && parsed.data) || {};
  const unreadCount = (pushData && typeof pushData.unread_count === 'number') ? pushData.unread_count : null;
  const count = (unreadCount !== null && unreadCount !== undefined) ? unreadCount : 1;

  // 1. Update PWA home screen icon badge in top-right corner
  const badgePromise = (async () => {
    try {
      if (typeof navigator !== 'undefined' && 'setAppBadge' in navigator) {
        if (count > 0) await navigator.setAppBadge(count);
        else if ('clearAppBadge' in navigator) await navigator.clearAppBadge();
      } else if ('setAppBadge' in self) {
        if (count > 0) await self.setAppBadge(count);
        else if ('clearAppBadge' in self) await self.clearAppBadge();
      }
    } catch (e) { /* silent */ }
  })();

  // 2. System notification in Android top status bar with sound & vibration
  const notifOptions = {
    body,
    icon,
    badge,
    data: pushData,
    vibrate: [300, 100, 300, 100, 300],
    silent: false,
    requireInteraction: true,
    tag: pushData.id ? 'notif-' + pushData.id : 'notif-' + Date.now(),
    renotify: true,
    timestamp: Date.now(),
    actions: pushData.url ? [{ action: 'open', title: 'Ver' }] : [],
  };

  const showNotifPromise = self.registration.showNotification(title, notifOptions);

  // 3. Notify open window clients for in-app sound & UI update
  const notifyClientsPromise = self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
    for (const client of windowClients) {
      client.postMessage({ type: 'PLAY_NOTIFICATION_SOUND', data: pushData, unreadCount: count });
    }
  }).catch(() => {});

  event.waitUntil(Promise.all([showNotifPromise, badgePromise, notifyClientsPromise]));
});

// Notification Click Handler (opens/focuses app when user taps status bar notification)
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || '/';
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
      const matching = windowClients.find((c) => {
        try {
          const cUrl = new URL(c.url);
          const nUrl = new URL(url, self.location.origin);
          return cUrl.pathname === nUrl.pathname;
        } catch { return false; }
      });
      if (matching) {
        matching.navigate(url);
        matching.focus();
      } else {
        self.clients.openWindow(url);
      }
    })
  );
});

self.addEventListener('notificationclose', () => {});
