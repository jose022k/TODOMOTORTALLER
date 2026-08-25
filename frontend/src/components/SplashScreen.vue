<template>
  <transition name="splash-fade">
    <div v-if="visible" class="pwa-splash" role="img" aria-label="Todomotortaller">
      <div class="pwa-splash-inner">
        <img
          class="pwa-splash-logo"
          src="https://res.cloudinary.com/dorj3mvvr/image/upload/v1783609693/logos/logotaller01.png"
          alt="Todomotortaller"
        />
        <p class="pwa-splash-name">Todomotortaller</p>
        <div class="pwa-splash-spinner" aria-hidden="true"></div>
      </div>
    </div>
  </transition>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { usePwa } from "@/composables/usePwa";

export default {
  name: "SplashScreen",
  setup() {
    const { isPwa } = usePwa();
    const visible = ref(false);
    let timer = null;

    onMounted(() => {
      // Solo se muestra cuando la app corre como PWA instalada (standalone),
      // nunca en la vista web del navegador (ni móvil ni escritorio).
      if (isPwa.value) {
        visible.value = true;
        timer = setTimeout(() => {
          visible.value = false;
        }, 1600);
      }
    });

    onBeforeUnmount(() => {
      if (timer) clearTimeout(timer);
    });

    return { visible };
  },
};
</script>

<style scoped>
.pwa-splash {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #1a1a1a;
  padding: env(safe-area-inset-top) env(safe-area-inset-right)
    env(safe-area-inset-bottom) env(safe-area-inset-left);
}

.pwa-splash-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 18px;
}

.pwa-splash-logo {
  width: 120px;
  height: auto;
  display: block;
}

.pwa-splash-name {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: #ffaa00;
}

.pwa-splash-spinner {
  width: 34px;
  height: 34px;
  border: 3px solid rgba(255, 170, 0, 0.25);
  border-top-color: #ffaa00;
  border-radius: 50%;
  animation: pwa-splash-spin 0.9s linear infinite;
}

@keyframes pwa-splash-spin {
  to {
    transform: rotate(360deg);
  }
}

.splash-fade-leave-active {
  transition: opacity 0.4s ease;
}
.splash-fade-leave-to {
  opacity: 0;
}
</style>
