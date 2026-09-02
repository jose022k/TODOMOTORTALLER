<template>
  <div class="notifications-page">
    <div class="notif-page-header">
      <h2>Notificaciones</h2>
      <div class="notif-page-actions">
        <button v-if="unread > 0" class="notif-action-btn" @click="markAllRead">Marcar todas leídas</button>
        <button v-if="notifications.length > 0" class="notif-action-btn notif-action-danger" @click="clearAll">Limpiar</button>
      </div>
    </div>

    <div v-if="loading" class="notif-page-loading">
      <div class="notif-page-spinner"></div>
      <p>Cargando notificaciones...</p>
    </div>

    <div v-else-if="notifications.length === 0" class="notif-page-empty">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
      <p>No hay notificaciones</p>
    </div>

    <div v-else class="notif-page-list">
      <div
        v-for="n in notifications"
        :key="n.id"
        :class="['notif-page-item', { 'notif-page-unread': !n.leido }]"
        @click="markRead(n)"
      >
        <div class="notif-page-icon-wrap">
          <span v-if="n.tipo === 'orden_creada'" class="notif-page-icon notif-page-icon-blue">+</span>
          <span v-else-if="n.tipo === 'orden_en_proceso'" class="notif-page-icon notif-page-icon-amber">&#9881;</span>
          <span v-else-if="n.tipo === 'orden_completada'" class="notif-page-icon notif-page-icon-green">&#10003;</span>
          <span v-else-if="n.tipo === 'orden_cancelada'" class="notif-page-icon notif-page-icon-red">&#10007;</span>
          <span v-else-if="n.tipo === 'mensaje_recibido'" class="notif-page-icon notif-page-icon-blue">&#9993;</span>
          <span v-else-if="n.tipo === 'evidencia_enviada'" class="notif-page-icon notif-page-icon-amber">&#128247;</span>
          <span v-else class="notif-page-icon notif-page-icon-gray">&#8505;</span>
        </div>
        <div class="notif-page-content">
          <p class="notif-page-text">{{ n.mensaje }}</p>
          <span class="notif-page-time">{{ timeAgo(n.fecha_creacion) }}</span>
        </div>
        <div v-if="!n.leido" class="notif-page-dot"></div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";

export default {
  name: "NotificationsView",
  setup() {
    const authStore = useAuthStore();
    const notifStore = useNotificationsStore();
    return { authStore, notifStore };
  },
  data() {
    return {
      notifications: [],
      loading: false,
    };
  },
  computed: {
    unread() {
      return this.notifStore.unreadCount;
    },
  },
  async mounted() {
    await this.fetchNotifications();
    this.notifStore.fetchUnreadCount();
  },
  methods: {
    async fetchNotifications() {
      this.loading = true;
      try {
        const { data } = await api.get("/notifications/", { params: { limit: 50 } });
        this.notifications = Array.isArray(data) ? data : [];
      } catch {
        // silent
      } finally {
        this.loading = false;
      }
    },
    async markRead(n) {
      if (n.leido) {
        this.navigateTo(n);
        return;
      }
      n.leido = true;
      this.notifStore.markOneRead(n.id);
      api.put(`/notifications/${n.id}/read`).catch(() => {});
      this.navigateTo(n);
    },
    async navigateTo(n) {
      const orderId = n.orden_servicio_id;
      if (!orderId) return;
      const role = this.authStore.user?.rol;
      const openChat = n.tipo === "mensaje_recibido" || n.tipo === "evidencia_enviada";
      let url;
      if (role === "cliente") {
        url = openChat ? `/cliente/orders?order_id=${orderId}&open_chat=1` : `/tracker/${orderId}`;
      } else if (role === "admin") {
        url = `/admin/service-orders?order_id=${orderId}${openChat ? "&open_chat=1" : ""}`;
      } else {
        url = `/mecanico/orders?order_id=${orderId}${openChat ? "&open_chat=1" : ""}`;
      }
      this.$router.push(url);
    },
    markAllRead() {
      this.notifStore.markAllRead();
      this.notifications.forEach((n) => (n.leido = true));
      api.put("/notifications/read-all").catch(() => {});
    },
    clearAll() {
      this.notifications = [];
      this.notifStore.clearAll();
      api.delete("/notifications/").catch(() => {});
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
.notifications-page {
  max-width: 600px;
  margin: 0 auto;
}
.notif-page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.notif-page-header h2 {
  font-size: 1.3rem;
  color: #1a1a1a;
}
.notif-page-actions {
  display: flex;
  gap: 8px;
}
.notif-action-btn {
  background: none;
  border: none;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  color: #ffaa00;
  transition: background 0.15s;
}
.notif-action-btn:hover {
  background: rgba(255, 170, 0, 0.1);
}
.notif-action-danger {
  color: #dc2626;
}
.notif-action-danger:hover {
  background: rgba(220, 38, 38, 0.1);
}
.notif-page-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 16px;
  color: #94a3b8;
  gap: 12px;
}
.notif-page-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 170, 0, 0.25);
  border-top-color: #ffaa00;
  border-radius: 50%;
  animation: notif-spin 0.8s linear infinite;
}
@keyframes notif-spin {
  to { transform: rotate(360deg); }
}
.notif-page-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 64px 16px;
  color: #94a3b8;
  gap: 12px;
}
.notif-page-list {
  display: flex;
  flex-direction: column;
}
.notif-page-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 12px;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid #f1f5f9;
  border-radius: 8px;
}
.notif-page-item:hover {
  background: #f8fafc;
}
.notif-page-unread {
  background: #fffbeb;
}
.notif-page-unread:hover {
  background: #fef3c7;
}
.notif-page-icon-wrap {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.notif-page-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
}
.notif-page-icon-blue { background: #dbeafe; color: #2563eb; }
.notif-page-icon-amber { background: #fef3c7; color: #d97706; }
.notif-page-icon-green { background: #d1fae5; color: #059669; }
.notif-page-icon-red { background: #fee2e2; color: #dc2626; }
.notif-page-icon-gray { background: #f1f5f9; color: #64748b; }
.notif-page-content {
  flex: 1;
  min-width: 0;
}
.notif-page-text {
  font-size: 0.9rem;
  color: #1a1a1a;
  margin: 0 0 4px;
  line-height: 1.4;
}
.notif-page-time {
  font-size: 0.75rem;
  color: #94a3b8;
}
.notif-page-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ffaa00;
  flex-shrink: 0;
  margin-top: 12px;
}

/* ===== MOBILE / PWA Android-style ===== */
@media (max-width: 768px) {
  .notifications-page {
    padding: 0 0 80px;
    max-width: 100%;
  }
  .notif-page-header {
    padding: 12px 16px;
    margin-bottom: 0;
    background: #fff;
    border-bottom: 1px solid #f1f5f9;
    position: sticky;
    top: 0;
    z-index: 10;
  }
  .notif-page-header h2 {
    font-size: 1.1rem;
    font-weight: 700;
  }
  .notif-action-btn {
    font-size: 12px;
    padding: 6px 10px;
    border-radius: 8px;
  }
  .notif-page-item {
    padding: 14px 16px;
    border-bottom: 1px solid #f1f5f9;
    border-radius: 0;
    gap: 14px;
    margin: 0;
  }
  .notif-page-unread {
    background: #fffbeb;
    border-left: 3px solid #ffaa00;
  }
  .notif-page-icon-wrap {
    width: 40px;
    height: 40px;
  }
  .notif-page-icon {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    font-size: 16px;
  }
  .notif-page-text {
    font-size: 0.9rem;
    line-height: 1.5;
  }
  .notif-page-time {
    font-size: 0.72rem;
    margin-top: 4px;
    display: block;
  }
  .notif-page-dot {
    width: 8px;
    height: 8px;
    margin-top: 8px;
  }
  .notif-page-empty {
    padding: 80px 24px;
  }
}
html.dark .notifications-page .notif-page-header {
  background: #0d1117;
  border-bottom-color: #1e293b;
}
</style>

<style>
html.dark .notif-page-header h2 { color: #e2e8f0; }
html.dark .notif-page-item:hover { background: #1e293b; }
html.dark .notif-page-unread { background: #1e1b0a; }
html.dark .notif-page-unread:hover { background: #29250e; }
html.dark .notif-page-item { border-bottom-color: #1e293b; }
html.dark .notif-page-text { color: #e2e8f0; }
</style>
