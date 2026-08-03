/* eslint-disable */

import { precacheAndRoute } from "workbox-precaching";
import { registerRoute } from "workbox-routing";
import { StaleWhileRevalidate, CacheFirst } from "workbox-strategies";
import { CacheableResponsePlugin } from "workbox-cacheable-response";
import { ExpirationPlugin } from "workbox-expiration";

precacheAndRoute(self.__WB_MANIFEST);

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
  try {
    const data = event.data.json();
    const options = {
      body: data.body || "",
      icon: data.icon || "/img/icons/logo-192.png",
      badge: data.badge || "/img/icons/logo-192.png",
      data: data.data || {},
      vibrate: [200, 100, 200],
      sound: data.sound || "/sounds/notification.wav",
    };
    event.waitUntil(self.registration.showNotification(data.title || "Todomotortaller", options));
  } catch {
    const text = event.data.text();
    event.waitUntil(self.registration.showNotification("Todomotortaller", { body: text }));
  }
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
