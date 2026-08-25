import { ref, onMounted, onUnmounted } from "vue";

/**
 * Detecta si la app se está viendo como PWA instalada (modo standalone),
 * es decir, abierta desde el icono de inicio y NO desde un navegador web.
 * Devuelve un ref reactivo `isPwa` y un helper `isStandalone()`.
 */
const isPwa = ref(false);

function checkStandalone() {
  if (typeof window === "undefined") return false;
  const displayModeStandalone =
    window.matchMedia &&
    window.matchMedia("(display-mode: standalone)").matches;
  const iosStandalone = window.navigator.standalone === true;
  const displayModeWindow =
    window.matchMedia &&
    window.matchMedia("(display-mode: window-controls-overlay)").matches;
  return displayModeStandalone || iosStandalone || displayModeWindow;
}

let mediaQueryList = null;
let onChange = null;

export function usePwa() {
  onMounted(() => {
    isPwa.value = checkStandalone();
    if (window.matchMedia) {
      mediaQueryList = window.matchMedia("(display-mode: standalone)");
      onChange = () => {
        isPwa.value = checkStandalone();
      };
      if (mediaQueryList.addEventListener) {
        mediaQueryList.addEventListener("change", onChange);
      } else if (mediaQueryList.addListener) {
        mediaQueryList.addListener(onChange);
      }
    }
  });

  onUnmounted(() => {
    if (mediaQueryList && onChange) {
      if (mediaQueryList.removeEventListener) {
        mediaQueryList.removeEventListener("change", onChange);
      } else if (mediaQueryList.removeListener) {
        mediaQueryList.removeListener(onChange);
      }
    }
  });

  return { isPwa };
}
