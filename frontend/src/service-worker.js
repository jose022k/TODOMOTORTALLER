/* eslint-disable */

import { precacheAndRoute } from "workbox-precaching";
import { registerRoute } from "workbox-routing";
import { StaleWhileRevalidate, CacheFirst } from "workbox-strategies";
import { CacheableResponsePlugin } from "workbox-cacheable-response";
import { ExpirationPlugin } from "workbox-expiration";

precacheAndRoute(self.__WB_MANIFEST);

self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

registerRoute(
  ({ request }) => request.mode === "navigate",
  new StaleWhileRevalidate({
    cacheName: "pages",
  })
);

registerRoute(
  ({ request }) =>
    request.destination === "style" ||
    request.destination === "script" ||
    request.destination === "worker",
  new StaleWhileRevalidate({
    cacheName: "assets",
  })
);

registerRoute(
  ({ request }) => request.destination === "image",
  new CacheFirst({
    cacheName: "images",
    plugins: [
      new CacheableResponsePlugin({ statuses: [0, 200] }),
      new ExpirationPlugin({ maxEntries: 60, maxAgeSeconds: 30 * 24 * 60 * 60 }),
    ],
  })
);

self.addEventListener("push", (event) => {
  if (!event.data) return;
  let parsed = null;
  try {
    parsed = event.data.json();
  } catch {
    parsed = null;
  }

  const title = (parsed && parsed.title) || "Todomotortaller";
  const body = (parsed && parsed.body) || event.data.text();
  const icon = (parsed && parsed.icon) || "/img/icons/logo-192.png";
  const badge = (parsed && parsed.badge) || "/img/icons/logo-192.png";
  const pushData = (parsed && parsed.data) || {};
  const unreadCount = typeof pushData.unread_count === "number" ? pushData.unread_count : null;

  // Update app badge if supported
  if (unreadCount !== null && typeof navigator.setAppBadge === "function") {
    navigator.setAppBadge(unreadCount).catch(() => {});
  }

  const notifOptions = {
    body,
    icon,
    badge,
    data: pushData,
    vibrate: [200, 100, 200],
    silent: false,
  };

  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((windowClients) => {
      // Tell every open window to play the sound
      for (const client of windowClients) {
        client.postMessage({ type: "PLAY_NOTIFICATION_SOUND" });
      }

      // Only show OS notification if no window is currently visible/focused
      const hasVisibleClient = windowClients.some((c) => c.visibilityState === "visible");
      if (!hasVisibleClient) {
        return self.registration.showNotification(title, notifOptions);
      }
    })
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || "/";
  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((windowClients) => {
      const matching = windowClients.find((c) => {
        const cUrl = new URL(c.url);
        const nUrl = new URL(url, self.location.origin);
        return cUrl.pathname === nUrl.pathname;
      });
      if (matching) {
        matching.navigate(url);
        matching.focus();
      } else {
        clients.openWindow(url);
      }
    })
  );
});

self.addEventListener("notificationclose", (event) => {
  const data = event.notification.data || {};
  fetch("/notifications/push/close", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: data.url || "/" }),
  }).catch(() => {});
});
