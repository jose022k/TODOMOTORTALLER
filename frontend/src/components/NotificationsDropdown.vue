<template>
  <div class="notif-wrapper" ref="wrapper">
    <a href="#" class="nav-icon-btn notif-bell" @click.prevent="toggleDropdown" data-tooltip="Notificaciones">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
      </svg>
      <span v-if="unread > 0" class="notif-badge">{{ unread > 99 ? '99+' : unread }}</span>
    </a>

    <transition name="dropdown">
      <div v-if="open" class="notif-dropdown">
        <div class="notif-dropdown-header">
          <h3>Notificaciones</h3>
          <div class="notif-header-actions">
            <button v-if="unread > 0" class="mark-all-btn" @click="markAllRead">Leer todas</button>
            <button v-if="notifications.length > 0" class="clear-all-btn" @click="clearAll">Limpiar</button>
          </div>
        </div>

        <div v-if="loading" class="notif-loading">Cargando...</div>
        <div v-else-if="notifications.length === 0" class="notif-empty">No hay notificaciones</div>

        <div v-else class="notif-list">
          <div
            v-for="n in notifications"
            :key="n.id"
            :class="['notif-item', { 'notif-unread': !n.leido }]"
            @click="markRead(n)"
          >
            <div class="notif-icon-wrap">
              <span v-if="n.tipo === 'orden_creada'" class="notif-icon notif-icon-blue">+</span>
              <span v-else-if="n.tipo === 'orden_en_proceso'" class="notif-icon notif-icon-amber">&#9881;</span>
              <span v-else-if="n.tipo === 'orden_completada'" class="notif-icon notif-icon-green">&#10003;</span>
              <span v-else-if="n.tipo === 'orden_cancelada'" class="notif-icon notif-icon-red">&#10007;</span>
              <span v-else-if="n.tipo === 'mensaje_recibido'" class="notif-icon notif-icon-blue">&#9993;</span>
              <span v-else-if="n.tipo === 'evidencia_enviada'" class="notif-icon notif-icon-amber">&#128247;</span>
              <span v-else class="notif-icon notif-icon-gray">&#8505;</span>
            </div>
            <div class="notif-content">
              <p class="notif-text">{{ n.mensaje }}</p>
              <span class="notif-time">{{ timeAgo(n.fecha_creacion) }}</span>
            </div>
            <div v-if="!n.leido" class="notif-dot"></div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import api from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";

export default {
  name: "NotificationsDropdown",
  setup() {
    const authStore = useAuthStore();
    const notifStore = useNotificationsStore();
    return { authStore, notifStore };
  },
  data() {
    return {
      open: false,
      notifications: [],
      loading: false,
    };
  },
  computed: {
    unread() {
      return this.notifStore.unreadCount;
    },
  },
  methods: {
    async toggleDropdown() {
      this.open = !this.open;
      if (this.open) {
        await this.fetchNotifications();
      }
    },
    async fetchNotifications() {
      this.loading = true;
      try {
        const { data } = await api.get("/notifications/", { params: { limit: 20 } });
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
    handleClickOutside(e) {
      if (this.$refs.wrapper && !this.$refs.wrapper.contains(e.target)) {
        this.open = false;
      }
    },
  },
  mounted() {
    // Ensure shared polling is running (started by NotificationNative, but also start here as fallback)
    if (this.authStore.isAuthenticated) {
      this.notifStore.startPolling();
    }
    document.addEventListener("click", this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener("click", this.handleClickOutside);
    // Don't stop polling — NotificationNative might still be mounted
  },
  watch: {
    $route() {
      this.notifStore.fetchUnreadCount();
    },
  },
};
</script>

<style scoped>
.notif-wrapper {
  position: relative;
}
.notif-bell {
  color: #ffffff;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.notif-bell:hover {
  background: rgba(255, 170, 0, 0.15);
}
.notif-badge {
  position: absolute;
  top: 1px;
  right: 1px;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  background: #dc2626;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  line-height: 1;
  pointer-events: none;
}
.notif-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 380px;
  max-height: 480px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  z-index: 1000;
}
.notif-dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid #e2e8f0;
}
.notif-dropdown-header h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}
.notif-header-actions {
  display: flex;
  gap: 8px;
}
.mark-all-btn, .clear-all-btn {
  background: none;
  border: none;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.15s;
}
.mark-all-btn {
  color: #ffaa00;
}
.mark-all-btn:hover {
  background: #fff7e6;
}
.clear-all-btn {
  color: #dc2626;
}
.clear-all-btn:hover {
  background: #fee2e2;
}
.notif-loading,
.notif-empty {
  padding: 40px 16px;
  text-align: center;
  color: #94a3b8;
  font-size: 0.9rem;
}
.notif-list {
  overflow-y: auto;
  flex: 1;
}
.notif-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid #f1f5f9;
}
.notif-item:hover {
  background: #f8fafc;
}
.notif-unread {
  background: #fffbeb;
}
.notif-unread:hover {
  background: #fef3c7;
}
.notif-icon-wrap {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.notif-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
}
.notif-icon-blue { background: #dbeafe; color: #2563eb; }
.notif-icon-amber { background: #fef3c7; color: #d97706; }
.notif-icon-green { background: #d1fae5; color: #059669; }
.notif-icon-red { background: #fee2e2; color: #dc2626; }
.notif-icon-gray { background: #f1f5f9; color: #64748b; }
.notif-content {
  flex: 1;
  min-width: 0;
}
.notif-text {
  font-size: 0.85rem;
  color: #1a1a1a;
  margin: 0 0 3px;
  line-height: 1.35;
}
.notif-time {
  font-size: 0.75rem;
  color: #94a3b8;
}
.notif-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ffaa00;
  flex-shrink: 0;
  margin-top: 12px;
}
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
