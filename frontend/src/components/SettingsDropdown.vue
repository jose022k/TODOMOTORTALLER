<template>
  <div class="settings-wrap" ref="wrap">
    <button class="settings-trigger" :class="{ open: open }" title="Ajustes" @click.stop="open = !open">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
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
    </div>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  name: "SettingsDropdown",
  emits: ["theme-change"],
  props: {
    above: { type: Boolean, default: false },
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
}
.settings-trigger {
  background: none;
  border: none;
  color: #b0b5b9;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  border-radius: 6px;
  transition: all 0.15s;
}
.settings-trigger:hover,
.settings-trigger.open {
  color: #ffaa00;
  background: rgba(255,170,0,0.1);
}
.settings-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: var(--settings-bg, #fff);
  border-radius: 10px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  padding: 12px 0;
  min-width: 220px;
  z-index: 200;
}
.settings-above {
  top: auto;
  bottom: calc(100% + 8px);
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
