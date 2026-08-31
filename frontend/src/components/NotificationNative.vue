<template>
  <div class="native-notifier">
    <audio ref="audioEl" src="/sounds/notification.wav" preload="auto" style="display:none"></audio>
    <div v-if="showPermBanner" class="notif-perm-banner">
      <div class="notif-perm-banner-inner">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
        <span>{{ permDenied ? "Activa las notificaciones en la configuración de tu navegador" : "Habilita las notificaciones para recibir alertas" }}</span>
        <button v-if="!permDenied" class="notif-perm-btn" @click="requestPermission">Activar</button>
        <button class="notif-perm-close" @click="dismissPerm">&times;</button>
      </div>
    </div>
    <div v-if="unreadCount > 0" class="notif-pwa-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</div>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";
import api from "@/services/api";

const OPEN_CHAT_TYPES = new Set(["mensaje_recibido", "evidencia_enviada"]);

let audioCtx = null;
let notifAudio = null;

function ensureAudioCtx() {
  if (audioCtx) return audioCtx;
  try {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  } catch (e) { void e; }
  return audioCtx;
}

function unlockAudio() {
  const ctx = ensureAudioCtx();
  if (!ctx) return;
  try {
    if (ctx.state === "suspended") ctx.resume();
  } catch (e) { void e; }
}

function playNotifSound() {
  unlockAudio();
  if (notifAudio) {
    try {
      notifAudio.currentTime = 0;
      const p = notifAudio.play();
      if (p && p.catch) p.catch(() => {});
      return;
    } catch (e) { void e; }
  }
  const ctx = ensureAudioCtx();
  if (ctx && audioCtx.state === "suspended") {
    try { ctx.resume(); } catch (e) { void e; }
  }
  const audioEl = document.querySelector('audio[src="/sounds/notification.wav"]');
  if (audioEl) {
    try {
      audioEl.currentTime = 0;
      const p = audioEl.play();
      if (p && p.catch) p.catch(() => {});
    } catch (e) { void e; }
  }
}

function preloadSound() {
  try {
    notifAudio = new Audio("/sounds/notification.wav");
    notifAudio.preload = "auto";
    notifAudio.load();
  } catch (e) { void e; }
}

export default {
  name: "NotificationNative",
  setup() {
    const authStore = useAuthStore();
    return { authStore };
  },
  data() {
    return {
      showPermBanner: false,
      permDenied: false,
      pollTimer: null,
      knownIds: new Set(),
      unreadCount: 0,
    };
  },
  mounted() {
    this.swRegistration = null;
    navigator.serviceWorker?.ready.then((reg) => { this.swRegistration = reg; }).catch(() => {});
    window.addEventListener("notification-new", this.onNewNotification);
    window.addEventListener("click", unlockAudio, { passive: true });
    window.addEventListener("touchstart", unlockAudio, { passive: true });
    window.addEventListener("keydown", unlockAudio, { passive: true });
    preloadSound();
    this.checkPermission();
    this.fetchUnread();
    this.pollTimer = setInterval(() => {
      this.fetchUnread();
      this.pollNotifications();
    }, 10000);
  },
  beforeUnmount() {
    window.removeEventListener("notification-new", this.onNewNotification);
    window.removeEventListener("click", unlockAudio);
    window.removeEventListener("touchstart", unlockAudio);
    window.removeEventListener("keydown", unlockAudio);
    if (this.pollTimer) clearInterval(this.pollTimer);
  },
  methods: {
    checkPermission() {
      if (!("Notification" in window)) return;
      if (Notification.permission !== "granted") {
        this.showPermBanner = true;
        this.permDenied = Notification.permission === "denied";
      }
    },
    async requestPermission() {
      if (!("Notification" in window)) return;
      unlockAudio();
      try {
        const result = await Notification.requestPermission();
        this.showPermBanner = false;
        if (result === "granted") {
          playNotifSound();
        }
        this.permDenied = false;
      } catch (e) { void e; }
      this.showPermBanner = false;
    },
    dismissPerm() {
      this.showPermBanner = false;
    },
    async onNewNotification(event) {
      const notif = event.detail;
      if (!notif || this.knownIds.has(notif.id)) return;
      this.knownIds.add(notif.id);
      this.unreadCount++;
      playNotifSound();
      await this.showNativeNotification(notif);
    },
    async fetchUnread() {
      if (!this.authStore.isAuthenticated) return;
      try {
        const { data } = await api.get("/notifications/unread-count");
        this.unreadCount = data.count || 0;
        if (typeof navigator.setAppBadge === "function") {
          try { navigator.setAppBadge(this.unreadCount); } catch (e) { void e; }
        }
      } catch (e) { void e; }
    },
    async pollNotifications() {
      if (!this.authStore.isAuthenticated) return;
      try {
        const { data } = await api.get("/notifications/", { params: { limit: 10 } });
        if (!Array.isArray(data)) return;
        for (const n of data) {
          if (!n.leido && !this.knownIds.has(n.id)) {
            this.knownIds.add(n.id);
            this.unreadCount++;
            playNotifSound();
            await this.showNativeNotification(n);
          }
        }
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

<style scoped>
.notif-perm-banner {
  position: fixed;
  top: env(safe-area-inset-top, 70px);
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  animation: slideDown 0.3s ease;
  width: max-content;
  max-width: 90vw;
}
.notif-perm-banner-inner {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #1a1a1a;
  color: #fff;
  padding: 10px 18px;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  font-size: 14px;
  font-weight: 500;
}
.notif-perm-banner-inner svg {
  color: #ffaa00;
  flex-shrink: 0;
}
.notif-perm-btn {
  background: #ffaa00;
  color: #1a1a1a;
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
}
.notif-perm-btn:hover {
  background: #e69900;
}
.notif-perm-close {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 18px;
  cursor: pointer;
  padding: 0 2px;
  line-height: 1;
}
.notif-perm-close:hover {
  color: #fff;
}
.notif-pwa-badge {
  position: fixed;
  top: env(safe-area-inset-top, 10px);
  right: 10px;
  z-index: 99999;
  min-width: 22px;
  height: 22px;
  border-radius: 11px;
  background: #dc2626;
  color: #fff;
  font-size: 12px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.5);
  pointer-events: none;
  line-height: 1;
}
@keyframes slideDown {
  from { opacity: 0; transform: translateX(-50%) translateY(-10px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}
</style>