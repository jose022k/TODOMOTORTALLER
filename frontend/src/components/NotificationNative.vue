<template>
  <div class="native-notifier">
    <audio ref="audioEl" src="/sounds/notification.wav" preload="auto" data-notif-sound style="display:none"></audio>

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

    <!-- In-App Toasts (shown in mobile/PWA views) -->
    <div class="in-app-toast-container">
      <transition-group name="toast-list" tag="div">
        <div
          v-for="toast in activeToasts"
          :key="toast.id"
          class="in-app-toast"
          @click="handleToastClick(toast)"
        >
          <div class="toast-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
          </div>
          <div class="toast-content">
            <div class="toast-title">Todomotortaller</div>
            <div class="toast-body">{{ toast.mensaje }}</div>
          </div>
          <button class="toast-close" @click.stop="removeToast(toast.id)">&times;</button>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";

const OPEN_CHAT_TYPES = new Set(["mensaje_recibido", "evidencia_enviada"]);

// ── Audio Engine: synthesized crystal glass marimba chime ───────────────────
function playNotifSound() {
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();

    // Premium dual-tone glass marimba chime (A5 + E6 + A6 crystal cascade)
    const notes = [
      { main: 880.00, harmonic: 1760.00, start: 0.00, dur: 0.25, vol: 0.30 },
      { main: 1318.51, harmonic: 2637.02, start: 0.07, dur: 0.28, vol: 0.35 },
      { main: 1760.00, harmonic: 3520.00, start: 0.14, dur: 0.35, vol: 0.40 },
    ];

    notes.forEach(({ main, harmonic, start, dur, vol }) => {
      const t = ctx.currentTime + start;

      // Main sine oscillator
      const osc1 = ctx.createOscillator();
      const env1 = ctx.createGain();
      osc1.type = "sine";
      osc1.frequency.value = main;
      osc1.connect(env1);
      env1.connect(ctx.destination);
      env1.gain.setValueAtTime(0, t);
      env1.gain.linearRampToValueAtTime(vol, t + 0.008);
      env1.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      osc1.start(t);
      osc1.stop(t + dur);

      // Glass harmonic overtone (triangle wave for warmth)
      const osc2 = ctx.createOscillator();
      const env2 = ctx.createGain();
      osc2.type = "triangle";
      osc2.frequency.value = harmonic;
      osc2.connect(env2);
      env2.connect(ctx.destination);
      env2.gain.setValueAtTime(0, t);
      env2.gain.linearRampToValueAtTime(vol * 0.3, t + 0.005);
      env2.gain.exponentialRampToValueAtTime(0.0001, t + dur * 0.6);
      osc2.start(t);
      osc2.stop(t + dur * 0.6);
    });

    setTimeout(() => { try { ctx.close(); } catch { /* */ } }, 800);
  } catch { /* AudioContext not supported */ }
}

function unlockAudio() {
  // No-op: each call to playNotifSound() creates its own fresh context
  // which avoids the suspended state issue on mobile.
}
// ── End Audio Engine ────────────────────────────────────────────────────────

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
    };
  },
  mounted() {
    this.swRegistration = null;

    // Get SW registration for native OS notifications
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.ready
        .then((reg) => { this.swRegistration = reg; })
        .catch(() => {});

      // Listen for SW postMessage (plays sound when push arrives and app is open)
      this._swMsg = (event) => {
        if (event.data && event.data.type === "PLAY_NOTIFICATION_SOUND") {
          playNotifSound();
        }
      };
      navigator.serviceWorker.addEventListener("message", this._swMsg);
    }

    // Listen for WS real-time notification events
    this._onNotif = this.onNewNotification.bind(this);
    window.addEventListener("notification-new", this._onNotif);

    // Show permission prompt
    this.checkPermission();

    // Start shared polling (only if not already polling)
    if (this.authStore.isAuthenticated) {
      this.notifStore.startPolling();
    }
  },
  beforeUnmount() {
    window.removeEventListener("notification-new", this._onNotif);
    if ("serviceWorker" in navigator && this._swMsg) {
      navigator.serviceWorker.removeEventListener("message", this._swMsg);
    }
    // Don't stop polling here — NotificationsDropdown might still need it
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

      // Register in shared store (deduplication + badge update)
      const isNew = this.notifStore.onNewNotification(notif);
      if (!isNew) return;

      // Play sound
      playNotifSound();

      // Show in-app toast ONLY on mobile/PWA (on PC, user only receives native browser OS notifications)
      const isMobile = window.innerWidth <= 768 || (typeof window !== "undefined" && window.navigator && window.navigator.standalone);
      if (isMobile) {
        this.showInAppToast(notif);
      }

      // Show native browser OS notification (bottom right box on PC, top banner on mobile)
      await this.showNativeNotification(notif);
    },

    showInAppToast(notif) {
      this.activeToasts.push(notif);
      setTimeout(() => this.removeToast(notif.id), 6000);
    },
    removeToast(id) {
      this.activeToasts = this.activeToasts.filter((t) => t.id !== id);
    },
    handleToastClick(notif) {
      const url = this.buildUrl(notif);
      this.removeToast(notif.id);
      if (url && url !== "/") {
        this.$router.push(url).catch(() => { window.location.href = url; });
      }
    },

    async showNativeNotification(notif) {
      if (!("Notification" in window) || Notification.permission !== "granted") return;
      const url = this.buildUrl(notif);
      const opts = {
        body: notif.mensaje || "",
        icon: "/img/icons/logo-192.png",
        badge: "/img/icons/logo-192.png",
        data: { url },
        vibrate: [200, 100, 200],
        silent: false,
        tag: "notif-" + notif.id,
        renotify: true,
      };
      if (this.swRegistration && this.swRegistration.showNotification) {
        try {
          await this.swRegistration.showNotification("Todomotortaller", opts);
          return;
        } catch { /* fall through */ }
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
  bottom: 24px;
  right: 20px;
  z-index: 100000;
  display: flex;
  flex-direction: column-reverse;
  gap: 10px;
  pointer-events: none;
  max-width: calc(100vw - 40px);
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