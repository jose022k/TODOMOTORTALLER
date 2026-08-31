<template>
  <div class="native-notifier">
    <div v-if="showPrompt" class="notif-permission-banner">
      <span>Habilita las notificaciones para recibir alertas de mensajes y evidencias.</span>
      <button class="notif-permission-btn" @click="requestPerm">Activar</button>
      <button class="notif-permission-dismiss" @click="dismissPrompt">×</button>
    </div>
  </div>
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
  data() {
    return {
      showPrompt: false,
    };
  },
  mounted() {
    this.swRegistration = null;
    navigator.serviceWorker?.ready.then((reg) => {
      this.swRegistration = reg;
    }).catch(() => {});
    window.addEventListener("notification-new", this.onNewNotification);
    this.checkPermissionPrompt();
  },
  beforeUnmount() {
    window.removeEventListener("notification-new", this.onNewNotification);
  },
  methods: {
    checkPermissionPrompt() {
      if (typeof Notification === "undefined") return;
      if (Notification.permission !== "default") return;
      if (this.isMobileOrPwa()) return;
      if (sessionStorage.getItem("notif_prompt_dismissed")) return;
      this.showPrompt = true;
    },
    isMobileOrPwa() {
      try {
        if (window.matchMedia?.("(display-mode: standalone)").matches) return true;
        if (window.navigator?.standalone) return true;
        if (window.innerWidth <= 768) return true;
      } catch {}
      return false;
    },
    async requestPerm() {
      if ("Notification" in window) {
        const result = await Notification.requestPermission().catch(() => "default");
        if (result === "granted") this.showPrompt = false;
      }
    },
    dismissPrompt() {
      this.showPrompt = false;
      sessionStorage.setItem("notif_prompt_dismissed", "1");
    },
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
        } catch {
          // fallback to new Notification
        }
      }
      try {
        const n = new Notification("Todomotortaller", {
          body: notif.mensaje || "",
          icon: "/img/icons/logo-192.png",
          tag: `notif-${notif.id}`,
        });
        n.onclick = () => {
          window.focus();
          if (url && url !== "/") this.$router?.push(url);
          n.close();
        };
      } catch {
        // silent
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

<style scoped>
.notif-permission-banner {
  position: fixed;
  top: 70px;
  left: 50%;
  transform: translateX(-50%);
  background: #1a1a1a;
  color: #fff;
  padding: 10px 16px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  z-index: 9999;
  font-size: 13px;
  max-width: 480px;
  width: calc(100% - 32px);
}
.notif-permission-btn {
  background: #ffaa00;
  color: #1a1a1a;
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
}
.notif-permission-btn:hover {
  background: #e69500;
}
.notif-permission-dismiss {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 18px;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
  flex-shrink: 0;
}
.notif-permission-dismiss:hover {
  color: #fff;
}
</style>