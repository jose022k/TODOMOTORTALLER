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
  try { parsed = event.data.json(); } catch { parsed = null; }

  const title = (parsed && parsed.title) || "Todomotortaller";
  const body = (parsed && parsed.body) || "";
  const iconPath = (parsed && parsed.icon) || "/img/app-icon-192.png";
  const badgePath = (parsed && parsed.badge) || "/img/app-icon-192.png";
  const icon = new URL(iconPath, self.location.origin).href;
  const badge = new URL(badgePath, self.location.origin).href;
  const pushData = (parsed && parsed.data) || {};
  const unreadCount = (pushData && typeof pushData.unread_count === "number") ? pushData.unread_count : null;

  // Update PWA home screen icon badge safely
  try {
    if (typeof self.navigator !== "undefined" && typeof self.navigator.setAppBadge === "function") {
      const count = (unreadCount !== null) ? unreadCount : 1;
      if (count > 0) {
        self.navigator.setAppBadge(count).catch(() => {});
      } else if (typeof self.navigator.clearAppBadge === "function") {
        self.navigator.clearAppBadge().catch(() => {});
      }
    }
  } catch { /* silent */ }

  const sound = new URL("/sounds/notification.wav", self.location.origin).href;

  const notifOptions = {
    body,
    icon,
    badge,
    sound,
    data: pushData,
    vibrate: [200, 100, 200],
    silent: false,
    requireInteraction: false,
    tag: pushData.id ? "notif-" + pushData.id : "notif-" + Date.now(),
    renotify: true,
  };

  event.waitUntil(
    Promise.all([
      clients.matchAll({ type: "window", includeUncontrolled: true }).then((windowClients) => {
        for (const client of windowClients) {
          client.postMessage({ type: "PLAY_NOTIFICATION_SOUND", data: pushData });
        }
      }),
      self.registration.showNotification(title, notifOptions)
    ])
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || "/";
  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((windowClients) => {
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
        clients.openWindow(url);
      }
    })
  );
});

self.addEventListener("notificationclose", () => {});

