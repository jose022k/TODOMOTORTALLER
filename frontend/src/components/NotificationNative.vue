<template>
  <div class="native-notifier">
    <!-- Permission banner -->
    <div v-if="showPermBanner" class="notif-perm-banner">
      <div class="notif-perm-banner-inner">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
        </svg>
        <span>{{ permDenied ? "Activa las notificaciones en la configuración de tu navegador" : "Habilita las notificaciones para recibir alertas" }}</span>
        <button v-if="!permDenied" class="notif-perm-btn" @click="requestPermission">Activar</button>
        <button class="notif-perm-close" @click="dismissPerm">&times;</button>
      </div>
    </div>

    <!-- In-App Toasts: shown on mobile/PWA AND for session alerts on all screens -->
    <div class="in-app-toast-container">
      <transition-group name="toast-list" tag="div">
        <div
          v-for="toast in activeToasts"
          :key="toast._tid"
          class="in-app-toast"
          :class="{ 'toast--session': toast.tipo === 'sistema' }"
          @click="handleToastClick(toast)"
        >
          <div class="toast-icon">
            <svg v-if="toast.tipo !== 'sistema'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <div class="toast-content">
            <div class="toast-title">{{ toast.tipo === 'sistema' ? 'Sesión' : 'Todomotortaller' }}</div>
            <div class="toast-body">{{ toast.mensaje }}</div>
          </div>
          <button class="toast-close" @click.stop="removeToast(toast._tid)">&times;</button>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";

const OPEN_CHAT_TYPES = new Set(["mensaje_recibido", "evidencia_enviada"]);

// ── Audio Engine ──────────────────────────────────────────────────────────────
function unlockAudio() {
  try {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    if (!window._sharedAudioCtx || window._sharedAudioCtx.state === "closed") {
      window._sharedAudioCtx = new Ctx();
    }
    if (window._sharedAudioCtx && window._sharedAudioCtx.state === "suspended") {
      const p = window._sharedAudioCtx.resume();
      if (p && typeof p.catch === "function") {
        p.catch(() => {});
      }
    }
  } catch { /* ignore */ }
}

if (typeof window !== "undefined") {
  window.addEventListener("touchstart", unlockAudio, { passive: true, once: false });
  window.addEventListener("click", unlockAudio, { passive: true, once: false });
}

function playNotifSound() {
  // En PC escritorio NO reproducir chime web; el SO/navegador emite su sonido nativo por defecto
  if (!isMobileOrPwa()) return;
  try {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    let ctx = window._sharedAudioCtx;
    if (!ctx || ctx.state === "closed") {
      ctx = new Ctx();
      window._sharedAudioCtx = ctx;
    }
    const resume = ctx.state === "suspended" ? ctx.resume() : Promise.resolve();
    resume.then(() => {
      const notes = [
        { f: 880.00, h: 1760.00, t: 0.00, d: 0.25, v: 0.55 },
        { f: 1318.51, h: 2637.02, t: 0.08, d: 0.28, v: 0.60 },
        { f: 1760.00, h: 3520.00, t: 0.16, d: 0.35, v: 0.65 },
      ];
      notes.forEach(({ f, h, t: start, d, v }) => {
        const t = ctx.currentTime + start;
        const o1 = ctx.createOscillator(); const g1 = ctx.createGain();
        o1.type = "sine"; o1.frequency.value = f;
        o1.connect(g1); g1.connect(ctx.destination);
        g1.gain.setValueAtTime(0, t);
        g1.gain.linearRampToValueAtTime(v, t + 0.008);
        g1.gain.exponentialRampToValueAtTime(0.0001, t + d);
        o1.start(t); o1.stop(t + d);

        const o2 = ctx.createOscillator(); const g2 = ctx.createGain();
        o2.type = "triangle"; o2.frequency.value = h;
        o2.connect(g2); g2.connect(ctx.destination);
        g2.gain.setValueAtTime(0, t);
        g2.gain.linearRampToValueAtTime(v * 0.3, t + 0.005);
        g2.gain.exponentialRampToValueAtTime(0.0001, t + d * 0.6);
        o2.start(t); o2.stop(t + d * 0.6);
      });
    }).catch(() => {});
  } catch { /* AudioContext not supported */ }
}
// ── End Audio Engine ──────────────────────────────────────────────────────────

function isMobileOrPwa() {
  if (typeof window === "undefined") return false;
  return (
    window.innerWidth <= 900 ||
    window.matchMedia("(display-mode: standalone)").matches ||
    (window.navigator && window.navigator.standalone === true)
  );
}

export default {
  name: "NotificationNative",
  setup() {
    const authStore = useAuthStore();
    const notifStore = useNotificationsStore();
    return { authStore, notifStore };
  },
  data() {
    return {
      showPermBanner: false,
      permDenied: false,
      activeToasts: [],
      swRegistration: null,
    };
  },
  mounted() {
    // Grab SW registration for native showNotification()
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.ready
        .then((reg) => { this.swRegistration = reg; })
        .catch(() => {});
    }

    // Single window event listener — handles ALL notification-new events
    this._onNotif = this.onNewNotification.bind(this);
    window.addEventListener("notification-new", this._onNotif);

    // Show permission prompt if not granted
    this.checkPermission();

    // Start badge/count polling
    if (this.authStore.isAuthenticated) {
      this.notifStore.startPolling();
    }
  },
  beforeUnmount() {
    window.removeEventListener("notification-new", this._onNotif);
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
        if (result === "granted") {
          playNotifSound();
          this.permDenied = false;
        } else {
          this.permDenied = result === "denied";
        }
      } catch { /* ignored */ }
      this.showPermBanner = false;
    },
    dismissPerm() {
      this.showPermBanner = false;
    },

    async onNewNotification(event) {
      const notif = event.detail;
      if (!notif) return;

      // ── Session / system alerts: always show toast + sound on ALL screens ──
      const isSession = notif.tipo === "sistema" || (notif.id && String(notif.id).startsWith("session-warn"));
      if (isSession) {
        playNotifSound();
        this.pushToast(notif);
        return;
      }

      // ── Regular notifications: deduplication first ──
      const isNew = this.notifStore.onNewNotification(notif);
      if (!isNew) return;

      // Sound on all screens
      playNotifSound();

      if (isMobileOrPwa()) {
        // Mobile / PWA: show in-app toast
        this.pushToast(notif);
        // ALSO attempt native SW notification so it appears in status bar
        await this.showNativeNotification(notif);
      } else {
        // Desktop: only native browser OS notification (bottom-right box)
        await this.showNativeNotification(notif);
      }
    },

    pushToast(notif) {
      const tid = (notif.id ? String(notif.id) : "") + "-" + Date.now();
      const item = { ...notif, _tid: tid };
      this.activeToasts.push(item);
      setTimeout(() => this.removeToast(tid), 8000);
    },
    removeToast(tid) {
      this.activeToasts = this.activeToasts.filter((t) => t._tid !== tid);
    },
    handleToastClick(notif) {
      const url = this.buildUrl(notif);
      this.removeToast(notif._tid);
      if (url && url !== "/") {
        this.$router.push(url).catch(() => { window.location.href = url; });
      }
    },

    async showNativeNotification(notif) {
      if (!("Notification" in window) || Notification.permission !== "granted") return;
      const url = this.buildUrl(notif);
      const opts = {
        body: notif.mensaje || "",
        icon: "/img/app-icon-192.png",
        badge: "/img/app-icon-192.png",
        data: { url },
        vibrate: [200, 100, 200],
        silent: false,
        tag: "notif-" + (notif.id || Date.now()),
        renotify: true,
      };
      const reg = this.swRegistration;
      if (reg && reg.showNotification) {
        try {
          await reg.showNotification("Todomotortaller", opts);
          return;
        } catch { /* fall through to legacy */ }
      }
      try {
        const n = new Notification("Todomotortaller", opts);
        n.onclick = () => {
          window.focus();
          if (url && url !== "/") window.location.href = url;
          n.close();
        };
      } catch { /* ignored */ }
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
.notif-perm-banner-inner svg { color: #ffaa00; flex-shrink: 0; }
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
.notif-perm-btn:hover { background: #e69900; }
.notif-perm-close {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 18px;
  cursor: pointer;
  padding: 0 2px;
  line-height: 1;
}
.notif-perm-close:hover { color: #fff; }

/* Toast Container */
.in-app-toast-container {
  position: fixed;
  bottom: 80px;
  right: 16px;
  z-index: 100000;
  display: flex;
  flex-direction: column-reverse;
  gap: 10px;
  pointer-events: none;
  max-width: calc(100vw - 32px);
}
@media (min-width: 901px) {
  /* On desktop, only session toasts are shown — they sit bottom-right */
  .in-app-toast-container {
    bottom: 24px;
    right: 20px;
  }
}
.in-app-toast {
  background: #1a1a1a;
  color: #fff;
  border-left: 4px solid #ffaa00;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.35);
  display: flex;
  align-items: flex-start;
  gap: 12px;
  width: 320px;
  max-width: 100%;
  pointer-events: auto;
  cursor: pointer;
}
.toast--session {
  border-left-color: #ef4444;
  background: #1f1010;
}
.toast--session .toast-icon { color: #ef4444; }
.toast--session .toast-title { color: #fca5a5; }
.toast-icon { color: #ffaa00; flex-shrink: 0; margin-top: 2px; }
.toast-content { flex: 1; min-width: 0; }
.toast-title { font-weight: 700; font-size: 14px; margin-bottom: 3px; }
.toast-body { font-size: 13px; color: #d1d5db; line-height: 1.4; word-break: break-word; }
.toast-close {
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  flex-shrink: 0;
}
.toast-close:hover { color: #fff; }

/* Transitions */
.toast-list-enter-active { transition: all 0.35s cubic-bezier(.25,.8,.25,1); }
.toast-list-leave-active { transition: all 0.25s ease; }
.toast-list-enter-from { opacity: 0; transform: translateX(40px); }
.toast-list-leave-to { opacity: 0; transform: scale(0.88); }

@keyframes slideDown {
  from { opacity: 0; transform: translateX(-50%) translateY(-12px); }
  to   { opacity: 1; transform: translateX(-50%) translateY(0); }
}
</style>