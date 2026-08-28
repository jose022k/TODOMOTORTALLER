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
        <div class="pwa-splash-progress" aria-hidden="true">
          <svg class="progress-ring" width="56" height="56" viewBox="0 0 56 56">
            <circle class="ring-bg" cx="28" cy="28" r="24" />
            <circle class="ring-fg" cx="28" cy="28" r="24" />
          </svg>
        </div>
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
        // Logo aparece gradualmente (2.5s) + barra circular (~2.8s) y luego entra a la PWA.
        timer = setTimeout(() => {
          visible.value = false;
        }, 3400);
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
  width: 130px;
  height: auto;
  display: block;
  opacity: 0;
  transform: scale(0.92);
  animation: logo-appear 2.5s ease forwards;
}

.pwa-splash-name {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: #ffaa00;
  opacity: 0;
  animation: name-appear 1.2s ease forwards;
  animation-delay: 1.4s;
}

/* Barra circular de carga (determinante) */
.pwa-splash-progress {
  margin-top: 6px;
  opacity: 0;
  animation: name-appear 0.6s ease forwards;
  animation-delay: 2.5s;
}
.progress-ring {
  transform: rotate(-90deg);
}
.ring-bg {
  fill: none;
  stroke: rgba(255, 170, 0, 0.18);
  stroke-width: 4;
}
.ring-fg {
  fill: none;
  stroke: #ffaa00;
  stroke-width: 4;
  stroke-linecap: round;
  stroke-dasharray: 150.8; /* 2 * pi * 24 */
  stroke-dashoffset: 150.8;
  animation: ring-fill 0.9s linear forwards;
  animation-delay: 2.5s;
}

@keyframes logo-appear {
  from {
    opacity: 0;
    transform: scale(0.92);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
@keyframes name-appear {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
@keyframes ring-fill {
  to {
    stroke-dashoffset: 0;
  }
}

.splash-fade-leave-active {
  transition: opacity 0.4s ease;
}
.splash-fade-leave-to {
  opacity: 0;
}
</style>
