<template>
  <transition name="fade">
    <div v-if="visible" class="loading-overlay">
      <div class="loader">
        <svg class="moto-wheel" width="90" height="90" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
          <circle cx="50" cy="50" r="45" fill="none" stroke="#333" stroke-width="8" />
          <circle cx="50" cy="50" r="45" fill="none" stroke="#222" stroke-width="12" stroke-dasharray="8 6" />
          <circle cx="50" cy="50" r="32" fill="none" stroke="#555" stroke-width="2" />
          <circle cx="50" cy="50" r="28" fill="none" stroke="#666" stroke-width="1.5" stroke-dasharray="4 3" />
          <line x1="50" y1="18" x2="50" y2="82" stroke="#888" stroke-width="2.5" />
          <line x1="18" y1="50" x2="82" y2="50" stroke="#888" stroke-width="2.5" />
          <line x1="27" y1="27" x2="73" y2="73" stroke="#888" stroke-width="2.5" />
          <line x1="73" y1="27" x2="27" y2="73" stroke="#888" stroke-width="2.5" />
          <circle cx="50" cy="50" r="10" fill="#ffaa00" stroke="#e69900" stroke-width="2" />
          <circle cx="50" cy="50" r="4" fill="#1a1a1a" />
        </svg>
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
.moto-wheel {
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
  display: block;
}
.loader-text {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
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
