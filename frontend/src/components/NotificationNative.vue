<template>
  <div class="native-notifier"></div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";

const NATIVE_NOTIF_TYPES = new Set([
  "orden_creada",
  "orden_en_proceso",
  "orden_cancelada",
  "mensaje_recibido",
  "evidencia_enviada",
]);
const OPEN_CHAT_TYPES = new Set(["mensaje_recibido", "evidencia_enviada"]);

function playNotifSound() {
  try {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    const ctx = new Ctx();
    if (ctx.state === "suspended") ctx.resume();
    const now = ctx.currentTime;
    [880, 1320].forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.value = freq;
      const t = now + i * 0.12;
      gain.gain.setValueAtTime(0.0001, t);
      gain.gain.exponentialRampToValueAtTime(0.25, t + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.18);
      osc.connect(gain).connect(ctx.destination);
      osc.start(t);
      osc.stop(t + 0.2);
    });
  } catch (e) {
    /* silent */
  }
}

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
    console.log("[NativeNotif] Mounted, listening for notification-new events");
    console.log("[NativeNotif] Notification permission:", typeof Notification !== "undefined" ? Notification.permission : "N/A");
  },
  beforeUnmount() {
    window.removeEventListener("notification-new", this.onNewNotification);
  },
  methods: {
    async onNewNotification(event) {
      const notif = event.detail;
      if (!notif || !notif.tipo) return;
      if (!NATIVE_NOTIF_TYPES.has(notif.tipo)) return;
      if (!("Notification" in window)) return;
      if (Notification.permission !== "granted") return;
      console.log("[NativeNotif] Received notification:", notif.id, notif.tipo, notif.mensaje);
      playNotifSound();
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
      const url = this.buildUrl(notif);
      const options = {
        body: notif.mensaje || "",
        icon: "/img/app-icon-512.png",
        badge: "/img/app-icon-512.png",
        data: { url },
        vibrate: [200, 100, 200],
      };
      if (this.isMobileView()) {
        let reg = this.swRegistration;
        if (!reg) {
          try { reg = await navigator.serviceWorker.getRegistration(); } catch { reg = null; }
        }
        if (reg && reg.showNotification) {
          try { await reg.showNotification("Todomotortaller", options); return; } catch (e) { /* fallback */ }
        }
      }
      try {
        const n = new Notification("Todomotortaller", options);
        n.onclick = () => {
          window.focus();
          if (url) window.location.href = url;
          n.close();
        };
      } catch (e) { /* notification blocked */ }
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
