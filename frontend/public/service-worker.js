/*
 * Self-destructing service worker for development.
 * Replaces any old cached SW and cleans up after itself.
 */
self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", () => {
  self.registration.unregister();
  if (self.clients) {
    self.clients.matchAll({ type: "window" }).then((clients) => {
      clients.forEach((client) => client.navigate(client.url));
    });
  }
});
