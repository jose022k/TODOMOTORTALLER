<template>
  <transition name="modal">
    <div v-if="visible" class="modal-overlay" @click.self="$emit('cancel')">
      <div class="modal-card">
        <div class="modal-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#ffaa00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <h3 class="modal-title">{{ title }}</h3>
        <p class="modal-message">{{ message }}</p>
        <div class="modal-actions">
          <button class="modal-btn cancel" @click="$emit('cancel')">{{ cancelText }}</button>
          <button class="modal-btn confirm" @click="$emit('confirm')">{{ confirmText }}</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: "ConfirmModal",
  props: {
    visible: { type: Boolean, default: false },
    title: { type: String, default: "Confirmar" },
    message: { type: String, default: "¿Estás seguro?" },
    confirmText: { type: String, default: "Sí" },
    cancelText: { type: String, default: "Cancelar" },
  },
  emits: ["confirm", "cancel"],
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9998;
}
.modal-card {
  background: #fff;
  border-radius: 20px;
  padding: 32px 36px 28px;
  width: 90%;
  max-width: 380px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,0.25);
}
.modal-icon {
  margin-bottom: 12px;
}
.modal-title {
  font-size: 20px;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 8px;
}
.modal-message {
  font-size: 15px;
  color: #666;
  margin-bottom: 24px;
  line-height: 1.4;
}
.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
.modal-btn {
  padding: 10px 28px;
  border-radius: 10px;
  border: none;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.modal-btn.cancel {
  background: #f1f3f5;
  color: #555;
}
.modal-btn.cancel:hover {
  background: #e8eaed;
}
.modal-btn.confirm {
  background: #ffaa00;
  color: #1a1a1a;
}
.modal-btn.confirm:hover {
  background: #f5a000;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255,170,0,0.3);
}
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}
.modal-enter-active .modal-card,
.modal-leave-active .modal-card {
  transition: transform 0.25s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .modal-card {
  transform: scale(0.92);
}
.modal-leave-to .modal-card {
  transform: scale(0.92);
}
</style>
