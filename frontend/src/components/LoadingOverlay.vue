<template>
  <transition name="fade">
    <div v-if="visible" class="loading-overlay">
      <div class="loader">
        <div class="ring">
          <div class="ring-track"></div>
          <div class="ring-arc"></div>
          <div class="ring-glow"></div>
        </div>
        <p class="loader-text">{{ text }}</p>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: "LoadingOverlay",
  props: {
    visible: { type: Boolean, default: false },
    text: { type: String, default: "Cargando..." },
  },
};
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}
.loader {
  text-align: center;
}
.ring {
  position: relative;
  width: 90px;
  height: 90px;
  margin: 0 auto 18px;
}
.ring-track {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: conic-gradient(from 0deg, #2a2a2a, #3a3a3a, #2a2a2a);
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 10px), #000 calc(100% - 9px));
  mask: radial-gradient(farthest-side, transparent calc(100% - 10px), #000 calc(100% - 9px));
}
.ring-arc {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: conic-gradient(from 0deg, transparent 0deg, #ffaa00 120deg, #ffd166 200deg, transparent 300deg);
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 10px), #000 calc(100% - 9px));
  mask: radial-gradient(farthest-side, transparent calc(100% - 10px), #000 calc(100% - 9px));
  animation: spin 0.9s cubic-bezier(0.6, 0.1, 0.3, 0.9) infinite;
}
.ring-glow {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: conic-gradient(from 0deg, transparent 0deg, #ffaa00 130deg, #ffd166 200deg, transparent 300deg);
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 10px), #000 calc(100% - 9px));
  mask: radial-gradient(farthest-side, transparent calc(100% - 10px), #000 calc(100% - 9px));
  filter: blur(6px);
  opacity: 0.6;
  animation: spin 0.9s cubic-bezier(0.6, 0.1, 0.3, 0.9) infinite;
}
.loader-text {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
