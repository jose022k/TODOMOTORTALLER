<template>
  <div class="native-notifier"></div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";

const OPEN_CHAT_TYPES = new Set(["mensaje_recibido", "evidencia_enviada"]);

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
  },
  beforeUnmount() {
    window.removeEventListener("notification-new", this.onNewNotification);
  },
  methods: {
    async onNewNotification(event) {
      const notif = event.detail;
      if (!notif) return;
      await this.ensureRegistration();
      await this.showNativeNotification(notif);
    },
    async ensureRegistration() {
      if (this.swRegistration) return;
      try {
        this.swRegistration = await navigator.serviceWorker.getRegistration();
      } catch {
        this.swRegistration = null;
      }
    },
    async showNativeNotification(notif) {
      if (!("Notification" in window)) return;
      if (Notification.permission !== "granted") return;
      if (this.isMobileView()) return;
      const url = this.buildUrl(notif);
      const options = {
        body: notif.mensaje || "",
        icon: "/img/app-icon-512.png",
        badge: "/img/app-icon-512.png",
        data: { url },
        silent: true,
        vibrate: [200, 100, 200],
      };
      try {
        const reg = this.swRegistration;
        if (reg && reg.showNotification) {
          await reg.showNotification("Todomotortaller", options);
          return;
        }
      } catch {
        // fallback a Notification del navegador
      }
      try {
        const n = new Notification("Todomotortaller", options);
        n.onclick = () => {
          window.focus();
          if (url) window.location.href = url;
          n.close();
        };
      } catch {
        // silent
      }
    },
    isMobileView() {
      try {
        const standalone =
          window.matchMedia &&
          window.matchMedia("(display-mode: standalone)").matches;
        return window.innerWidth <= 768 || standalone;
      } catch (e) {
        return false;
      }
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