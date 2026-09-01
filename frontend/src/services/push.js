import api from "./api";

let swRegistration = null;

export async function getVapidPublicKey() {
  const { data } = await api.get("/notifications/push/vapid-public-key");
  return data.publicKey;
}

export async function requestPermission() {
  if (!("Notification" in window)) return false;
  if (Notification.permission === "granted") return true;
  if (Notification.permission === "denied") return false;
  const result = await Notification.requestPermission();
  return result === "granted";
}

export async function registerSw() {
  if (!("serviceWorker" in navigator)) return null;
  try {
    const reg = await navigator.serviceWorker.register(
      `${process.env.BASE_URL}service-worker.js`
    );
    swRegistration = reg;
    return reg;
  } catch {
    return null;
  }
}

export async function subscribeUser() {
  if (!swRegistration) {
    await registerSw();
  }
  if (!swRegistration) return false;

  const vapidKey = await getVapidPublicKey();
  if (!vapidKey) return false;

  try {
    const subscription = await swRegistration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidKey),
    });

    await api.post("/notifications/push/subscribe", subscription.toJSON());
    return true;
  } catch {
    return false;
  }
}

export async function unsubscribeUser() {
  if (!swRegistration) return;
  try {
    const subscription = await swRegistration.pushManager.getSubscription();
    if (subscription) {
      await api.post("/notifications/push/unsubscribe", {
        endpoint: subscription.endpoint,
      });
      await subscription.unsubscribe();
    }
  } catch {
    // silent
  }
}

export async function setupPush() {
  const hasPermission = await requestPermission();
  if (!hasPermission) return false;
  const reg = await registerSw();
  if (!reg) return false;
  swRegistration = reg;

  const existing = await reg.pushManager.getSubscription();
  if (existing) {
    try {
      await api.post("/notifications/push/subscribe", existing.toJSON());
    } catch { /* silent */ }
    return true;
  }

  return await subscribeUser();
}

function urlBase64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}
