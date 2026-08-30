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
    const newCount = data.count || 0;

    if (!baselineLoaded) {
      baselineLoaded = true;
      lastUnreadCount = newCount;
      state.unreadCount = newCount;
      setBadge(newCount);
      return;
    }

    if (newCount > lastUnreadCount) {
      try {
        const { data: notifs } = await api.get("/notifications/?limit=5");
        for (const notif of notifs) {
          if (!notif.leido && !shownNotifIds.has(notif.id)) {
            shownNotifIds.add(notif.id);
            window.dispatchEvent(
              new CustomEvent("notification-new", { detail: notif })
            );
          }
        }
      } catch (_) {
        /* silent */
      }
    }

    lastUnreadCount = newCount;
    state.unreadCount = newCount;
    setBadge(newCount);
  } catch (e) {
    /* silent */
  }
}

function onNew(notif) {
  if (!notif) return;
  if (shownNotifIds.has(notif.id)) return;
  shownNotifIds.add(notif.id);
  refreshCount();
}

export function useNotifications() {
  function init() {
    if (state.initialized) {
      refreshCount();
      return;
    }
    state.initialized = true;
    if (typeof Notification !== "undefined" && Notification.permission === "default") {
      const reqPerm = () => {
        Notification.requestPermission().catch(() => {});
        document.removeEventListener("click", reqPerm);
      };
      document.addEventListener("click", reqPerm);
    }
    window.addEventListener("notification-new", (e) => onNew(e.detail));
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
