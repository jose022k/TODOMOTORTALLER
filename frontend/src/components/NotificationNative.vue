<template>
  <div class="native-notifier">
    <!-- Permission banner -->
    <div v-if="showPermBanner" class="notif-perm-banner">
      <div class="notif-perm-banner-inner">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
        </svg>
        <span>Activa las notificaciones para recibir alertas</span>
        <button class="notif-perm-btn" @click="requestPermission">Activar</button>
        <button class="notif-perm-close" @click="dismissPerm">&times;</button>
      </div>
      <!-- Solo aparece si el navegador las tiene bloqueadas (no es lo mismo que no haberlas activado) -->
      <div v-if="bloqueado" class="notif-perm-ayuda">
        <strong>Tu navegador las tiene bloqueadas.</strong> {{ ayuda }}
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
import { setupPush } from "@/services/push";

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
      bloqueado: false,
      activeToasts: [],
      swRegistration: null,
    };
  },
  computed: {
    ayuda() {
      // Sin candado (http://) el navegador bloquea las notificaciones por su cuenta:
      // no es algo que el usuario pueda desbloquear desde el aviso.
      if (typeof window !== "undefined" && window.isSecureContext === false) {
        return "Esta página está en http:// y el navegador solo permite notificaciones en sitios con candado (https:// o localhost). En el sitio oficial y en localhost sí funcionan.";
      }
      return "Pulsa el candado de la barra de direcciones → Notificaciones → Permitir y recarga la página.";
    },
  },
  mounted() {
    // Grab SW registration for native showNotification()
    this.getReg();

    // Single window event listener — handles ALL notification-new events
    this._onNotif = this.onNewNotification.bind(this);
    window.addEventListener("notification-new", this._onNotif);

    // Mostrar el aviso "Activa las notificaciones" apenas se abre la app
    this.checkPermission();

    // Si el usuario lo activa desde los ajustes del navegador, se quita el aviso.
    // OJO: solo se comprueba al volver a estar visible; si no, cada cambio de
    // pestaña reabriría el aviso antes de tiempo y retrasaría los 60 s.
    this._onPermVis = () => {
      if (document.visibilityState !== "visible") return;
      if ("Notification" in window && Notification.permission === "granted") {
        this.checkPermission();
      }
    };
    document.addEventListener("visibilitychange", this._onPermVis);

    // Start badge/count polling
    if (this.authStore.isAuthenticated) {
      this.notifStore.startPolling();
    }
  },
  beforeUnmount() {
    window.removeEventListener("notification-new", this._onNotif);
    document.removeEventListener("visibilitychange", this._onPermVis);
    if (this._permTimer) clearTimeout(this._permTimer);
    if (this._regPromise) this._regPromise = null;
  },
  methods: {
    permisoOtorgado() {
      // Navegador sin soporte de notificaciones: no hay nada que activar
      if (typeof Notification === "undefined") return true;
      return Notification.permission === "granted";
    },

    checkPermission() {
      if (!("Notification" in window)) return;
      if (Notification.permission === "granted") {
        this.showPermBanner = false;
        this.bloqueado = false;
        if (this._permTimer) {
          clearTimeout(this._permTimer);
          this._permTimer = null;
        }
        return;
      }
      // El aviso es SIEMPRE el mismo y SIEMPRE trae su botón "Activar".
      // "bloqueado" solo indica si el navegador ya las tiene denegadas.
      this.bloqueado = Notification.permission === "denied";
      this.showPermBanner = true;
      this.agendarPermiso();
    },

    /**
     * El aviso vuelve a aparecer a los 60 segundos y sigue apareciendo cada
     * 60 s hasta que el usuario pulse "Activar" (o lo active en el navegador).
     * Cierra con la X y no se puede deshacer para siempre.
     */
    agendarPermiso() {
      if (this._permTimer) clearTimeout(this._permTimer);
      this._permTimer = setTimeout(() => {
        if (!("Notification" in window) || Notification.permission === "granted") {
          this._permTimer = null;
          return;
        }
        this.bloqueado = Notification.permission === "denied";
        this.showPermBanner = true;
        this.agendarPermiso();
      }, 60000);
    },

    async requestPermission() {
      if (!("Notification" in window)) return;
      unlockAudio();
      try {
        const result = await Notification.requestPermission();
        if (result === "granted") {
          this.bloqueado = false;
          this.showPermBanner = false;
          if (this._permTimer) {
            clearTimeout(this._permTimer);
            this._permTimer = null;
          }
          // Suscripción a Web Push: así avisa aunque la app esté cerrada
          setupPush().catch(() => {});
          playNotifSound();
        } else {
          this.bloqueado = true;
          this.showPermBanner = true;
          this.agendarPermiso();
        }
      } catch {
        this.agendarPermiso();
      }
    },

    dismissPerm() {
      // Se cierra, pero vuelve a salir en 60 s hasta que se active
      this.showPermBanner = false;
      this.agendarPermiso();
    },

    /** Registro del Service Worker (necesario en Android: no existe new Notification()). */
    async getReg() {
      if (this.swRegistration) return this.swRegistration;
      if (this._regPromise) return this._regPromise;
      if (!("serviceWorker" in navigator)) return null;

      this._regPromise = (async () => {
        try {
          const reg = await Promise.race([
            navigator.serviceWorker.ready,
            new Promise((_, rej) => setTimeout(() => rej(new Error("timeout")), 4000)),
          ]);
          if (reg) {
            this.swRegistration = reg;
            return reg;
          }
        } catch { /* seguimos abajo */ }
        try {
          const reg = await navigator.serviceWorker.getRegistration();
          if (reg) {
            this.swRegistration = reg;
            return reg;
          }
        } catch { /* ignore */ }
        this._regPromise = null;
        return null;
      })();

      return this._regPromise;
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

      // Aún no ha pulsado "Activar": no se muestra ni se sonía nada.
      // La campanita y el contador siguen actualizándose igualmente.
      if (!this.permisoOtorgado()) return;

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
      const reg = await this.getReg();
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
  z-index: 99999;
  animation: slideDown 0.3s ease;
  width: max-content;
  max-width: min(92vw, 420px);
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
.notif-perm-ayuda {
  margin-top: 6px;
  max-width: 340px;
  background: #1a1a1a;
  border: 1px solid #78350f;
  color: #fde68a;
  padding: 9px 14px;
  border-radius: 10px;
  font-size: 12px;
  line-height: 1.45;
  text-align: left;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.notif-perm-ayuda strong { color: #ffaa00; }

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