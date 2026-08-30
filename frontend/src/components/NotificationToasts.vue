<template>
  <div v-if="isMobile && isVisible" :class="['notif-toasts', isMobile ? 'notif-toasts--mobile' : 'notif-toasts--desktop']">
    <transition-group name="toast">
      <div
        v-for="t in state.toasts"
        :key="t.key"
        class="notif-toast"
        @click="onToastClick(t)"
      >
        <div :class="['notif-toast-icon', iconClass(t.tipo)]">
          <span v-if="t.tipo === 'orden_creada'">+</span>
          <span v-else-if="t.tipo === 'orden_en_proceso'">&#9881;</span>
          <span v-else-if="t.tipo === 'orden_completada'">&#10003;</span>
          <span v-else-if="t.tipo === 'orden_cancelada'">&#10007;</span>
          <span v-else-if="t.tipo === 'mensaje_recibido'">&#9993;</span>
          <span v-else-if="t.tipo === 'evidencia_enviada'">&#128247;</span>
          <span v-else>&#8505;</span>
        </div>
        <div class="notif-toast-body">
          <p class="notif-toast-text">{{ t.mensaje }}</p>
          <span class="notif-toast-time">{{ timeAgo(t.ts) }}</span>
        </div>
        <button class="notif-toast-close" @click.stop="close(t.key)" aria-label="Cerrar">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script>
import { useNotifications } from "@/composables/useNotifications";

export default {
  name: "NotificationToasts",
  setup() {
    const { state, removeToast, buildUrl } = useNotifications();
    return { state, removeToast, buildUrl };
  },
  data() {
    return { isMobile: this.computeMobile(), isVisible: this.computeVisible() };
  },
  mounted() {
    window.addEventListener("resize", this.onResize);
    document.addEventListener("visibilitychange", this.onVisibility);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.onResize);
    document.removeEventListener("visibilitychange", this.onVisibility);
  },
  methods: {
    computeMobile() {
      const standalone =
        window.matchMedia &&
        window.matchMedia("(display-mode: standalone)").matches;
      return window.innerWidth <= 768 || standalone;
    },
    computeVisible() {
      try {
        return typeof document === "undefined" || document.visibilityState === "visible";
      } catch (e) {
        return true;
      }
    },
    onResize() {
      this.isMobile = this.computeMobile();
    },
    onVisibility() {
      this.isVisible = this.computeVisible();
    },
    iconClass(tipo) {
      if (tipo === "orden_creada") return "ic-blue";
      if (tipo === "orden_en_proceso") return "ic-amber";
      if (tipo === "orden_completada") return "ic-green";
      if (tipo === "orden_cancelada") return "ic-red";
      if (tipo === "mensaje_recibido") return "ic-blue";
      if (tipo === "evidencia_enviada") return "ic-amber";
      return "ic-gray";
    },
    close(key) {
      this.removeToast(key);
    },
    async onToastClick(t) {
      const url = this.buildUrl(t);
      this.removeToast(t.key);
      if (url && url !== "/notifications") {
        this.$router.push(url);
      } else {
        this.$router.push("/notifications");
      }
    },
    timeAgo(ts) {
      const diff = Math.floor((Date.now() - ts) / 1000);
      if (diff < 60) return "ahora";
      if (diff < 3600) return `hace ${Math.floor(diff / 60)} min`;
      if (diff < 86400) return `hace ${Math.floor(diff / 3600)} h`;
      return new Date(ts).toLocaleDateString();
    },
  },
};
</script>

<style scoped>
.notif-toasts {
  position: fixed;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}
.notif-toasts--desktop {
  right: 20px;
  bottom: 20px;
  width: 340px;
}
.notif-toasts--mobile {
  left: 12px;
  right: 12px;
  bottom: calc(96px + env(safe-area-inset-bottom, 0px));
}
.notif-toast {
  pointer-events: auto;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-left: 4px solid #ffaa00;
  border-radius: 12px;
  padding: 12px 12px 12px 14px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.notif-toast:hover {
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.24);
}
.notif-toast-icon {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 700;
}
.ic-blue { background: #dbeafe; color: #2563eb; }
.ic-amber { background: #fef3c7; color: #d97706; }
.ic-green { background: #d1fae5; color: #059669; }
.ic-red { background: #fee2e2; color: #dc2626; }
.ic-gray { background: #f1f5f9; color: #64748b; }
.notif-toast-body {
  flex: 1;
  min-width: 0;
}
.notif-toast-text {
  font-size: 0.85rem;
  color: #1a1a1a;
  margin: 0 0 3px;
  line-height: 1.35;
  word-break: break-word;
}
.notif-toast-time {
  font-size: 0.72rem;
  color: #94a3b8;
}
.notif-toast-close {
  flex-shrink: 0;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 2px;
  display: flex;
  align-items: center;
  border-radius: 6px;
}
.notif-toast-close:hover {
  color: #1a1a1a;
  background: #f1f5f9;
}
.toast-enter-active,
.toast-leave-active {
  transition: all 0.28s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(16px) scale(0.98);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
html.dark .notif-toast {
  background: #1a1f2e;
  border-color: #1e293b;
  border-left-color: #ffaa00;
}
html.dark .notif-toast-text { color: #e2e8f0; }
html.dark .notif-toast-close:hover { background: #0d1117; color: #e2e8f0; }
</style>
