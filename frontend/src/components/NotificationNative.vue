<template>
  <div class="native-notifier"></div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";

const OPEN_CHAT_TYPES = new Set(["mensaje_recibido", "evidencia_enviada"]);
const notifSound = new Audio("/sounds/notification.wav");

export default {
  name: "NotificationNative",
  setup() {
    const authStore = useAuthStore();
    return { authStore };
  },
  mounted() {
    this.swRegistration = null;
    navigator.serviceWorker?.ready.then((reg) => {
      this.swRegistration = reg;
    }).catch(() => {});
    window.addEventListener("notification-new", this.onNewNotification);
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission().catch(() => {});
    }
  },
  beforeUnmount() {
    window.removeEventListener("notification-new", this.onNewNotification);
  },
  methods: {
    playSound() {
      try {
        notifSound.currentTime = 0;
        notifSound.play().catch(() => {});
      } catch (e) { void e; }
    },
    async onNewNotification(event) {
      const notif = event.detail;
      if (!notif) return;
      this.playSound();
      await this.ensureRegistration();
      await this.showNativeNotification(notif);
    },
    async ensureRegistration() {
      if (this.swRegistration) return;
      try {
        this.swRegistration = await navigator.serviceWorker.getRegistration();
      } catch (e) { void e; }
    },
    async showNativeNotification(notif) {
      if (!("Notification" in window)) return;
      if (Notification.permission !== "granted") return;
      const url = this.buildUrl(notif);
      if (this.swRegistration) {
        try {
          await this.swRegistration.showNotification("Todomotortaller", {
            body: notif.mensaje || "",
            icon: "/img/icons/logo-192.png",
            badge: "/img/icons/logo-192.png",
            data: { url },
            vibrate: [200, 100, 200],
          });
          return;
        } catch (e) { void e; }
      }
      try {
        var n = new Notification("Todomotortaller", {
          body: notif.mensaje || "",
          icon: "/img/icons/logo-192.png",
          tag: "notif-" + notif.id,
        });
        n.onclick = function () {
          window.focus();
          if (url && url !== "/") window.location.href = url;
          n.close();
        };
      } catch (e) { void e; }
    },
    buildUrl(n) {
      const orderId = n.orden_servicio_id;
      if (!orderId) return "/";
      const role = this.authStore.user?.rol;
      const openChat = OPEN_CHAT_TYPES.has(n.tipo);
      if (role === "cliente") {
        return openChat ? `/cliente/orders?order_id=${orderId}&open_chat=1` : `/tracker/${orderId}`;
      } else if (role === "admin") {
        return `/admin/service-orders?order_id=${orderId}${openChat ? "&open_chat=1" : ""}`;
      }
      return `/mecanico/orders?order_id=${orderId}${openChat ? "&open_chat=1" : ""}`;
    },
  },
};
</script>
