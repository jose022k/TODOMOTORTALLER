<template>
  <div class="settings-wrap" ref="wrap">
    <button class="settings-trigger" :class="{ open: open }" title="Ajustes" @click.stop="open = !open">
      <svg class="settings-chevron" :class="{ rotated: open }" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
    </button>
    <div v-if="open" :class="['settings-panel', { 'settings-above': above }]" @click.stop>
      <div class="settings-section">
        <h4>Notificaciones</h4>
        <label class="settings-row">
          <span>Mensajes y evidencias</span>
          <input type="checkbox" :checked="prefs.notify_messages" @change="updatePref('notify_messages', $event.target.checked)" />
        </label>
        <label class="settings-row">
          <span>Órdenes de servicio</span>
          <input type="checkbox" :checked="prefs.notify_orders" @change="updatePref('notify_orders', $event.target.checked)" />
        </label>
      </div>
      <div class="settings-section">
        <h4>Apariencia</h4>
        <label class="settings-row">
          <span>Modo oscuro</span>
          <input type="checkbox" :checked="prefs.dark_mode" @change="updatePref('dark_mode', $event.target.checked)" />
        </label>
      </div>
      <div v-if="isAdmin" class="settings-section">
        <h4>Preguntas</h4>
        <div class="settings-row settings-action" @click="openAdminFaq">
          <span>Preguntas frecuentes</span>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/services/api";
import { useAuthStore } from "@/stores/auth";

export default {
  name: "SettingsDropdown",
  emits: ["theme-change"],
  props: {
    above: { type: Boolean, default: false },
  },
  computed: {
    isAdmin() {
      const authStore = useAuthStore();
      return authStore.isAdmin;
    },
  },
  data() {
    return {
      open: false,
      prefs: { notify_messages: true, notify_orders: true, dark_mode: false },
    };
  },
  mounted() {
    this.fetchPrefs();
    document.addEventListener("click", this.onClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener("click", this.onClickOutside);
  },
  methods: {
    async fetchPrefs() {
      try {
        const res = await api.get("/preferences/");
        this.prefs = res.data;
        this.$emit("theme-change", this.prefs.dark_mode);
      } catch { /* usa defaults */ }
    },
    async updatePref(key, val) {
      this.prefs[key] = val;
      this.$emit("theme-change", this.prefs.dark_mode);
      try {
        await api.put("/preferences/", { [key]: val });
      } catch { /* silently */ }
    },
    openAdminFaq() {
      this.open = false;
      window.dispatchEvent(new CustomEvent("open-admin-faq"));
    },
    onClickOutside(e) {
      if (this.open && this.$refs.wrap && !this.$refs.wrap.contains(e.target)) {
        this.open = false;
      }
    },
  },
};
</script>

<style scoped>
.settings-wrap {
  position: relative;
  display: flex;
  align-items: center;
  z-index: 120;
}
.settings-trigger {
  background: none;
  border: none;
  color: #8b9299;
  cursor: pointer;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.15s;
}
.settings-trigger:hover,
.settings-trigger.open {
  color: #ffaa00;
  background: rgba(255,170,0,0.1);
}
.settings-chevron {
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.settings-chevron.rotated {
  transform: rotate(180deg);
}
.settings-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: var(--settings-bg, #fff);
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  padding: 14px 0;
  min-width: 230px;
  z-index: 300;
  animation: settings-pop 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
@keyframes settings-pop {
  from { opacity: 0; transform: translateY(8px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.settings-above {
  position: fixed;
  bottom: calc(56px + env(safe-area-inset-bottom, 0px));
  right: 12px;
  top: auto;
  left: auto;
}
.settings-section {
  padding: 0 14px;
}
.settings-section + .settings-section {
  padding-top: 10px;
  margin-top: 10px;
  border-top: 1px solid var(--settings-border, #e5e7eb);
}
.settings-section h4 {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--settings-muted, #9ca3af);
  margin-bottom: 8px;
}
.settings-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 0.85rem;
  color: var(--settings-text, #1f2937);
  cursor: pointer;
}
.settings-row input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #ffaa00;
  cursor: pointer;
}
</style>
