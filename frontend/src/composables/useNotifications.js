import { reactive } from "vue";
import api from "@/services/api";
import { useAuthStore } from "@/stores/auth";

const state = reactive({
  unreadCount: 0,
  initialized: false,
});

let lastUnreadCount = -1;
const shownNotifIds = new Set();
let baselineLoaded = false;
let pollCount = 0;
const RECENT_MS = 60000;

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

function isRecent(notif) {
  if (!notif.fecha_creacion) return true;
  try {
    const created = new Date(notif.fecha_creacion).getTime();
    return Date.now() - created < RECENT_MS;
  } catch {
    return false;
  }
}

async function refreshCount() {
  try {
    const { data } = await api.get("/notifications/unread-count");
    const newCount = data.count || 0;
    pollCount++;

    if (!baselineLoaded) {
      baselineLoaded = true;
      lastUnreadCount = newCount;
      state.unreadCount = newCount;
      setBadge(newCount);
      console.log(`[NotifPoll #${pollCount}] count=${newCount} last=-1 baseline=false shownIds=0`);
      console.log("[NotifPoll] Baseline set:", newCount);
      return;
    }

    console.log(`[NotifPoll #${pollCount}] count=${newCount} last=${lastUnreadCount} baseline=${baselineLoaded} shownIds=${shownNotifIds.size}`);

    if (newCount > lastUnreadCount) {
      console.log(`[NotifPoll] Count INCREASED: ${lastUnreadCount} -> ${newCount}, fetching list...`);
      try {
        const { data: notifs } = await api.get("/notifications/?limit=5");
        console.log("[NotifPoll] Got", notifs.length, "notifications:", notifs);
        let dispatched = 0;
        for (const notif of notifs) {
          if (!notif.leido && !shownNotifIds.has(notif.id)) {
            shownNotifIds.add(notif.id);
            if (isRecent(notif)) {
              window.dispatchEvent(
                new CustomEvent("notification-new", { detail: notif })
              );
              dispatched++;
            }
          }
        }
        console.log(`[NotifPoll] Dispatched ${dispatched} notification-new events`);
      } catch (e) {
        console.error("[NotifPoll] Failed to fetch notification list:", e.message);
      }
    }

    lastUnreadCount = newCount;
    state.unreadCount = newCount;
    setBadge(newCount);
  } catch (e) {
    console.error("[NotifPoll] Failed to refresh unread count:", e.message, e.response?.status);
  }
}

export function useNotifications() {
  function init() {
    if (state.initialized) {
      refreshCount();
      return;
    }
    state.initialized = true;
    console.log("[NotifInit] Initializing notification system");
    if (typeof Notification !== "undefined" && Notification.permission === "default") {
      const reqPerm = () => {
        Notification.requestPermission().catch(() => {});
        document.removeEventListener("click", reqPerm);
      };
      document.addEventListener("click", reqPerm);
    }
    window.addEventListener("notification-new", (e) => {
      if (e.detail && e.detail.id) shownNotifIds.add(e.detail.id);
    });
    refreshCount();
    setInterval(refreshCount, 10000);
  }

  function requestPermission() {
    if (typeof Notification === "undefined") return;
    if (Notification.permission === "default") {
      Notification.requestPermission().catch(() => {});
    }
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

  return { state, init, refreshCount, buildUrl, requestPermission };
}

window.__notifDebug = async function() {
  const apiMod = await import("@/services/api");
  const { data } = await apiMod.default.get("/notifications/debug");
  console.table(data);
  return data;
};
