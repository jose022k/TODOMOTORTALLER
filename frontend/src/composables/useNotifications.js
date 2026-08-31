import { reactive } from "vue";
import api from "@/services/api";

const state = reactive({
  unreadCount: 0,
  initialized: false,
});

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

async function fetchCount() {
  try {
    const { data } = await api.get("/notifications/unread-count");
    const count = data.count || 0;
    state.unreadCount = count;
    setBadge(count);
  } catch (e) {
    /* silent */
  }
}

export function useNotifications() {
  function init() {
    if (state.initialized) return;
    state.initialized = true;
    fetchCount();
    setInterval(fetchCount, 10000);
    requestPermission();
  }

  function requestPermission() {
    if (typeof Notification === "undefined") return;
    if (Notification.permission === "default") {
      Notification.requestPermission().catch(() => {});
    }
  }

  return { state, init, requestPermission };
}
