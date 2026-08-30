import { reactive } from "vue";
import api from "@/services/api";
import { useAuthStore } from "@/stores/auth";

const state = reactive({
  unreadCount: 0,
  toasts: [],
  soundEnabled: true,
  initialized: false,
});

let audioCtx = null;
let toastSeq = 0;

function playSound() {
  if (!state.soundEnabled) return;
  try {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    if (!audioCtx) audioCtx = new Ctx();
    if (audioCtx.state === "suspended") audioCtx.resume();
    const now = audioCtx.currentTime;
    [880, 1320].forEach((freq, i) => {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = "sine";
      osc.frequency.value = freq;
      const t = now + i * 0.12;
      gain.gain.setValueAtTime(0.0001, t);
      gain.gain.exponentialRampToValueAtTime(0.25, t + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.18);
      osc.connect(gain).connect(audioCtx.destination);
      osc.start(t);
      osc.stop(t + 0.2);
    });
  } catch (e) {
    /* silent */
  }
}

function setBadge(n) {
  try {
    if (n > 0) {
      if (navigator.setAppBadge) navigator.setAppBadge(n);
    } else if (navigator.clearAppBadge) {
      navigator.clearAppBadge();
    }
  } catch (e) {
    /* silent */
  }
}

async function refreshCount() {
  try {
    const { data } = await api.get("/notifications/unread-count");
    state.unreadCount = data.count || 0;
    setBadge(state.unreadCount);
  } catch (e) {
    /* silent */
  }
}

function removeToast(key) {
  const idx = state.toasts.findIndex((t) => t.key === key);
  if (idx !== -1) state.toasts.splice(idx, 1);
}

function onNew(notif) {
  if (!notif) return;
  const foregroundMobile =
    isMobileView() &&
    typeof document !== "undefined" &&
    document.visibilityState === "visible";
  if (foregroundMobile) {
    const key = `t${notif.id || 0}-${toastSeq++}`;
    state.toasts.push({
      key,
      id: notif.id,
      tipo: notif.tipo,
      mensaje: notif.mensaje || "",
      orden_servicio_id: notif.orden_servicio_id,
      ts: Date.now(),
    });
    if (state.toasts.length > 4) state.toasts.shift();
    setTimeout(() => removeToast(key), 7000);
    playSound();
  }
  refreshCount();
}

function isMobileView() {
  try {
    const standalone =
      window.matchMedia &&
      window.matchMedia("(display-mode: standalone)").matches;
    return window.innerWidth <= 768 || standalone;
  } catch (e) {
    return false;
  }
}

export function useNotifications() {
  function init() {
    if (state.initialized) {
      refreshCount();
      return;
    }
    state.initialized = true;
    if (typeof Notification !== "undefined" && Notification.permission === "default") {
      Notification.requestPermission().catch(() => {});
    }
    window.addEventListener("notification-new", (e) => onNew(e.detail));
    api
      .get("/preferences/")
      .then((res) => {
        state.soundEnabled = !!res.data.notify_messages;
      })
      .catch(() => {});
    refreshCount();
    setInterval(refreshCount, 20000);
  }

  function buildUrl(notif) {
    const orderId = notif.orden_servicio_id;
    if (!orderId) return "/notifications";
    const role = useAuthStore().user?.rol;
    const openChat =
      notif.tipo === "mensaje_recibido" || notif.tipo === "evidencia_enviada";
    if (role === "cliente") {
      return openChat
        ? `/cliente/orders?order_id=${orderId}&open_chat=1`
        : `/tracker/${orderId}`;
    }
    if (role === "admin") {
      return `/admin/service-orders?order_id=${orderId}${openChat ? "&open_chat=1" : ""}`;
    }
    return `/mecanico/orders?order_id=${orderId}${openChat ? "&open_chat=1" : ""}`;
  }

  return { state, init, refreshCount, removeToast, buildUrl };
}
