<template>
  <div class="toast-container">
    <transition-group name="toast">
      <div
        v-for="t in toasts"
        :key="t.key"
        class="toast-item"
        @click="onToastClick(t)"
      >
        <div :class="['toast-icon', `toast-icon-${t.colorClass}`]">
          <span v-html="t.icon"></span>
        </div>
        <div class="toast-body">
          <p class="toast-title">Todomotortaller</p>
          <p class="toast-message">{{ t.mensaje }}</p>
          <span class="toast-time">{{ timeAgo(t.fecha_creacion) }}</span>
        </div>
        <button class="toast-close" @click.stop="removeToast(t)">&times;</button>
      </div>
    </transition-group>
  </div>
</template>

<script>
import api from "@/services/api";
import { useAuthStore } from "@/stores/auth";

const ICONS = {
  orden_creada: { icon: "+", colorClass: "blue" },
  orden_en_proceso: { icon: "&#9881;", colorClass: "amber" },
  orden_completada: { icon: "&#10003;", colorClass: "green" },
  orden_cancelada: { icon: "&#10007;", colorClass: "red" },
  mensaje_recibido: { icon: "&#9993;", colorClass: "blue" },
  evidencia_enviada: { icon: "&#128247;", colorClass: "amber" },
  default: { icon: "&#8505;", colorClass: "gray" },
};

export default {
  name: "NotificationToasts",
  setup() {
    const authStore = useAuthStore();
    return { authStore };
  },
  data() {
    return {
      toasts: [],
      nextKey: 1,
      timers: {},
    };
  },
  mounted() {
    window.addEventListener("notification-new", this.onNewNotification);
  },
  beforeUnmount() {
    window.removeEventListener("notification-new", this.onNewNotification);
    Object.values(this.timers).forEach((t) => clearTimeout(t));
  },
  methods: {
    onNewNotification(event) {
      const notif = event.detail;
      if (!notif) return;
      const meta = ICONS[notif.tipo] || ICONS.default;
      const key = this.nextKey++;
      const toast = {
        key,
        id: notif.id,
        tipo: notif.tipo,
        mensaje: notif.mensaje,
        orden_servicio_id: notif.orden_servicio_id,
        fecha_creacion: notif.fecha_creacion,
        icon: meta.icon,
        colorClass: meta.colorClass,
      };
      this.toasts.push(toast);
      if (this.toasts.length > 4) {
        const oldest = this.toasts.shift();
        this.clearTimer(oldest.key);
      }
      this.timers[key] = setTimeout(() => this.removeToast(toast), 6000);

      // Si la página está en segundo plano, mostrar notificación nativa del sistema
      if (document.hidden || !document.hasFocus()) {
        this.showNativeNotification(notif);
      }
    },
    async showNativeNotification(notif) {
      if (!("Notification" in window)) return;
      if (Notification.permission !== "granted") return;
      try {
        const reg = await navigator.serviceWorker.getRegistration();
        if (!reg) return;
        const url = this.buildUrl(notif);
        await reg.showNotification("Todomotortaller", {
          body: notif.mensaje || "",
          icon: "/img/icons/logo-192.png",
          badge: "/img/icons/logo-192.png",
          data: { url },
          vibrate: [200, 100, 200],
          sound: "/sounds/notification.wav",
        });
      } catch {
        // silent
      }
    },
    removeToast(toast) {
      this.toasts = this.toasts.filter((t) => t.key !== toast.key);
      this.clearTimer(toast.key);
    },
    clearTimer(key) {
      if (this.timers[key]) {
        clearTimeout(this.timers[key]);
        delete this.timers[key];
      }
    },
    async onToastClick(toast) {
      this.removeToast(toast);
      if (toast.orden_servicio_id) {
        this.navigateTo(toast);
      }
      if (toast.id) {
        try {
          await api.put(`/notifications/${toast.id}/read`);
        } catch {
          // silent
        }
      }
    },
    async navigateTo(n) {
      const orderId = n.orden_servicio_id;
      if (!orderId) return;
      if (n.tipo === "mensaje_recibido" || n.tipo === "evidencia_enviada") {
        try {
          const { data } = await api.get(`/service-orders/${orderId}`);
          if (data.estado === "completada" || data.estado === "cancelada") {
            alert("La orden ya fue " + (data.estado === "completada" ? "completada" : "cancelada") + ".");
            return;
          }
        } catch {
          // if error, proceed anyway
        }
      }
      this.$router.push(this.buildUrl(n));
    },
    buildUrl(n) {
      const orderId = n.orden_servicio_id;
      if (!orderId) return "/";
      const role = this.authStore.user?.rol;
      const openChat = n.tipo === "mensaje_recibido" || n.tipo === "evidencia_enviada";
      if (role === "cliente") {
        return openChat ? `/cliente/orders?order_id=${orderId}&open_chat=1` : `/tracker/${orderId}`;
      } else if (role === "admin") {
        return `/admin/service-orders?order_id=${orderId}${openChat ? "&open_chat=1" : ""}`;
      }
      return `/mecanico/orders?order_id=${orderId}${openChat ? "&open_chat=1" : ""}`;
    },
    timeAgo(dateStr) {
      const now = new Date();
      const date = new Date(dateStr);
      const diff = Math.floor((now - date) / 1000);
      if (diff < 60) return "ahora";
      if (diff < 3600) return `${Math.floor(diff / 60)}min`;
      if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
      if (diff < 604800) return `${Math.floor(diff / 86400)}d`;
      return date.toLocaleDateString();
    },
  },
};
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 420px;
}
.toast-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.25);
  padding: 18px 20px;
  cursor: pointer;
  border-left: 5px solid #ffaa00;
  transition: background 0.15s;
  width: 380px;
}
.toast-item:hover {
  background: #f8fafc;
}
.toast-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
}
.toast-icon-blue { background: #dbeafe; color: #2563eb; }
.toast-icon-amber { background: #fef3c7; color: #d97706; }
.toast-icon-green { background: #d1fae5; color: #059669; }
.toast-icon-red { background: #fee2e2; color: #dc2626; }
.toast-icon-gray { background: #f1f5f9; color: #64748b; }
.toast-body {
  flex: 1;
  min-width: 0;
}
.toast-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #ffaa00;
  margin: 0 0 3px;
}
.toast-message {
  font-size: 0.95rem;
  color: #1a1a1a;
  margin: 0 0 5px;
  line-height: 1.4;
}
.toast-time {
  font-size: 0.8rem;
  color: #94a3b8;
}
.toast-close {
  background: none;
  border: none;
  font-size: 1.4rem;
  line-height: 1;
  color: #94a3b8;
  cursor: pointer;
  padding: 0 2px;
}
.toast-close:hover {
  color: #dc2626;
}
.toast-enter-active {
  transition: all 0.25s ease;
}
.toast-leave-active {
  transition: all 0.2s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(40px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(40px);
}
html.dark .toast-item {
  background: #1f2937;
  border-left-color: #ffaa00;
}
html.dark .toast-item:hover {
  background: #2d3748;
}
html.dark .toast-message {
  color: #f1f5f9;
}
html.dark .toast-close {
  color: #94a3b8;
}
</style>
