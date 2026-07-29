<template>
  <div class="chat-overlay" @click.self="$emit('close')">
    <div class="chat-modal">
      <div class="chat-header">
        <h3>Chat — Orden #{{ ordenId }}</h3>
        <button class="chat-close" @click="$emit('close')">×</button>
      </div>

      <div class="chat-body" ref="chatBody">
        <div v-if="messages.length === 0 && evidencias.length === 0" class="chat-empty">
          No hay mensajes aún. Envía el primero.
        </div>

        <template v-for="item in timeline" :key="item.key">
          <!-- Evidencia suelta (sin mensaje) -->
          <div v-if="item.type === 'evidencia'" class="evidencia-bubble">
            <img :src="imageUrl(item.url)" class="evidencia-img" @click="openLightbox(imageUrl(item.url))" />
          </div>
          <!-- Mensaje -->
          <div v-else class="msg-row" :class="item.mine ? 'msg-mine' : 'msg-other'">
            <div class="msg-bubble" :class="item.mine ? 'bubble-mine' : 'bubble-other'">
              <div class="msg-author">{{ senderLabel(item) }}</div>
              <template v-if="editingId === item.id">
                <input v-model="editText" class="edit-input" @keydown.enter="confirmEdit(item.id)" @keydown.esc="cancelEdit" />
                <div class="edit-actions">
                  <button class="edit-cancel" @click="cancelEdit">Cancelar</button>
                  <button class="edit-save" @click="confirmEdit(item.id)" :disabled="!editText.trim()">Guardar</button>
                </div>
              </template>
              <template v-else>
                <div v-if="item.evidencias.length" class="msg-attached-imgs">
                  <img
                    v-for="ev in item.evidencias"
                    :key="ev.id"
                    :src="imageUrl(ev.url)"
                    class="attached-img"
                    @click="openLightbox(imageUrl(ev.url))"
                  />
                </div>
                <div v-if="item.contenido" class="msg-text">{{ item.contenido }}</div>
                <div class="msg-footer">
                  <span class="msg-time">{{ formatTime(item.fecha_hora) }}<span v-if="item.editado" class="editado-badge"> · editado</span></span>
                  <button v-if="item.mine && item.canEdit" class="btn-edit" title="Editar mensaje" @click.stop="startEdit(item)">✏️</button>
                </div>
              </template>
            </div>
          </div>
        </template>
      </div>

      <!-- Lightbox -->
      <div v-if="lightboxUrl" class="lightbox" @click.self="lightboxUrl = ''">
        <img :src="lightboxUrl" class="lightbox-img" />
        <button class="lightbox-close" @click="lightboxUrl = ''">×</button>
      </div>

      <div class="chat-footer">
        <div class="chat-input-row">
          <label class="upload-icon-btn" title="Adjuntar foto">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
              <circle cx="12" cy="13" r="4"/>
            </svg>
            <input type="file" accept="image/*" capture="environment" @change="selectFile" />
          </label>
          <div class="input-wrap">
            <div v-if="previewUrl" class="inline-preview">
              <img :src="previewUrl" class="inline-preview-img" />
              <button class="inline-preview-x" @click="clearPreview">×</button>
            </div>
            <input
              v-model="text"
              class="chat-input"
              placeholder="Escribe un mensaje..."
              @keydown.enter="send"
              :disabled="!canChat"
            />
          </div>
          <button class="btn-send" @click="send" :disabled="(!text.trim() && !selectedFile) || uploading || !canChat">
            {{ uploading ? "..." : "Enviar" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  name: "ChatModal",
  props: {
    ordenId: { type: Number, required: true },
    myRole: { type: String, required: true },
    myId: { type: Number, required: true },
    canChat: { type: Boolean, default: false },
  },
  emits: ["close"],
  data() {
    return {
      messages: [],
      evidencias: [],
      text: "",
      polling: null,
      selectedFile: null,
      previewUrl: "",
      uploading: false,
      lightboxUrl: "",
      editingId: null,
      editText: "",
    };
  },
  computed: {
    timeline() {
      const now = new Date();
      const evidenciasByMsg = {};
      this.evidencias.forEach((e) => {
        if (e.mensaje_id) {
          if (!evidenciasByMsg[e.mensaje_id]) evidenciasByMsg[e.mensaje_id] = [];
          evidenciasByMsg[e.mensaje_id].push(e);
        }
      });
      const items = [];
      this.evidencias.forEach((e) => {
        if (!e.mensaje_id) {
          items.push({ type: "evidencia", key: "ev" + e.id, url: e.url, fecha: e.fecha });
        }
      });
      this.messages.forEach((m) => {
        const mine = m.remitente_id === this.myId && m.remitente_rol === this.myRole;
        const msgDate = new Date(m.fecha_hora);
        const canEdit = mine && (now - msgDate) < 600000;
        const attached = evidenciasByMsg[m.id] || [];
        items.push({
          type: "mensaje",
          key: "msg" + m.id,
          id: m.id,
          contenido: m.contenido,
          fecha_hora: m.fecha_hora,
          editado: m.editado,
          remitente_rol: m.remitente_rol,
          mine,
          canEdit,
          evidencias: attached,
        });
      });
      items.sort((a, b) => new Date(a.fecha || a.fecha_hora) - new Date(b.fecha || b.fecha_hora));
      return items;
    },
  },
  methods: {
    async fetchAll() {
      try {
        const [msgRes, evRes] = await Promise.all([
          api.get(`/chat/${this.ordenId}`),
          api.get(`/chat/${this.ordenId}/evidencias`),
        ]);
        this.messages = msgRes.data;
        this.evidencias = evRes.data;
        await this.$nextTick();
        this.scrollDown();
      } catch (e) { /* polling error silently */ }
    },
    scrollDown() {
      const el = this.$refs.chatBody;
      if (!el) return;
      const threshold = 50;
      const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < threshold;
      if (nearBottom) el.scrollTop = el.scrollHeight;
    },
    async send() {
      const textContent = this.text.trim();
      const file = this.selectedFile;
      if (!textContent && !file) return;
      this.uploading = true;
      const tempId = -Date.now();
      let tempMsg = null;
      let tempEv = null;
      if (textContent) {
        tempMsg = { id: tempId, contenido: textContent, fecha_hora: new Date().toISOString(), remitente_id: this.myId, remitente_rol: this.myRole, editado: false };
        this.messages.push(tempMsg);
        this.text = "";
      }
      if (file) {
        tempEv = { id: tempId, url: this.previewUrl, mensaje_id: tempId, fecha: new Date().toISOString() };
        this.evidencias.push(tempEv);
        this.clearPreview();
      }
      this.$nextTick(() => {
        requestAnimationFrame(() => {
          const el = this.$refs.chatBody;
          if (el) el.scrollTop = el.scrollHeight;
        });
      });
      try {
        if (textContent && file) {
          const fd = new FormData();
          fd.append("file", file);
          const [msgRes, evRes] = await Promise.all([
            api.post(`/chat/${this.ordenId}`, { contenido: textContent, orden_servicio_id: this.ordenId }),
            api.post(`/chat/${this.ordenId}/evidencias`, fd),
          ]);
          Object.assign(tempMsg, msgRes.data);
          const evIdx = this.evidencias.indexOf(tempEv);
          if (evIdx !== -1) this.evidencias.splice(evIdx, 1, evRes.data);
          if (msgRes.data.id) {
            evRes.data.mensaje_id = msgRes.data.id;
            api.patch(`/chat/${this.ordenId}/evidencias/${evRes.data.id}/link?mensaje_id=${msgRes.data.id}`).catch(() => {});
          }
        } else if (file) {
          const fd = new FormData();
          fd.append("file", file);
          const evRes = await api.post(`/chat/${this.ordenId}/evidencias`, fd);
          const evIdx = this.evidencias.indexOf(tempEv);
          if (evIdx !== -1) this.evidencias.splice(evIdx, 1, evRes.data);
        } else if (textContent) {
          const msgRes = await api.post(`/chat/${this.ordenId}`, { contenido: textContent, orden_servicio_id: this.ordenId });
          Object.assign(tempMsg, msgRes.data);
        }
      } catch (err) {
        if (tempMsg) this.messages = this.messages.filter(m => m.id !== tempMsg.id);
        if (tempEv) this.evidencias = this.evidencias.filter(e => e.id !== tempEv.id);
        alert("Error al enviar: " + (err.response?.data?.detail || err.message));
      } finally {
        this.uploading = false;
        this.$nextTick(() => {
          requestAnimationFrame(() => {
            const el = this.$refs.chatBody;
            if (el) el.scrollTop = el.scrollHeight;
          });
        });
      }
    },
    selectFile(e) {
      const file = e.target.files[0];
      if (!file) return;
      this.selectedFile = file;
      this.previewUrl = URL.createObjectURL(file);
    },
    clearPreview() {
      if (this.previewUrl) URL.revokeObjectURL(this.previewUrl);
      this.selectedFile = null;
      this.previewUrl = "";
    },
    senderLabel(item) {
      if (item.mine) return "Tú";
      const labels = { admin: "Admin", mecanico: "Mecánico", cliente: "Cliente" };
      return labels[item.remitente_rol] || item.remitente_rol;
    },
    startEdit(item) {
      this.editingId = item.id;
      this.editText = item.contenido;
    },
    cancelEdit() {
      this.editingId = null;
      this.editText = "";
    },
    async confirmEdit(msgId) {
      if (!this.editText.trim()) return;
      try {
        await api.put(`/chat/${this.ordenId}/${msgId}`, { contenido: this.editText });
        const msg = this.messages.find(m => m.id === msgId);
        if (msg) {
          msg.contenido = this.editText;
          msg.editado = true;
          msg.fecha_edicion = new Date().toISOString();
        }
        this.cancelEdit();
      } catch (err) {
        alert("Error al editar: " + (err.response?.data?.detail || err.message));
      }
    },
    onVisible() {
      if (document.visibilityState === "visible") this.fetchAll();
    },
    imageUrl(url) {
      if (url && url.startsWith("/")) return api.defaults.baseURL + url;
      return url;
    },
    openLightbox(url) {
      this.lightboxUrl = url;
    },
    formatTime(d) {
      if (!d) return "";
      return new Date(d).toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" });
    },
  },
  mounted() {
    this.fetchAll().then(() => {
      this.$nextTick(() => {
        const el = this.$refs.chatBody;
        if (el) el.scrollTop = el.scrollHeight;
      });
    });
    this.polling = setInterval(() => this.fetchAll(), 2000);
    document.addEventListener("visibilitychange", this.onVisible);
  },
  beforeUnmount() {
    if (this.polling) clearInterval(this.polling);
    document.removeEventListener("visibilitychange", this.onVisible);
  },
};
</script>

<style scoped>
.chat-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.45);
  z-index: 1100;
  display: flex;
  justify-content: center;
  align-items: center;
}
.chat-modal {
  width: 420px;
  max-width: 95vw;
  height: 80vh;
  max-height: 700px;
  background: #fff;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  overflow: hidden;
}
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: #ffaa00;
  color: #1a1a1a;
}
.chat-header h3 { font-size: 1rem; margin: 0; }
.chat-close { background: none; border: none; width: 36px; height: 36px; border-radius: 8px; color: #1a1a1a; font-size: 1.5rem; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.chat-close:hover { background: #fee2e2; color: #dc2626; }
.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
  background: #e5ddd5;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.chat-empty {
  text-align: center;
  color: #6b7280;
  font-size: 0.85rem;
  padding: 40px 0;
}
.evidencia-bubble {
  align-self: center;
  max-width: 240px;
}
.evidencia-img {
  width: 100%;
  border-radius: 10px;
  cursor: pointer;
  border: 2px solid #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}
.msg-attached-imgs {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
}
.attached-img {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
}
.msg-row {
  display: flex;
}
.msg-mine { justify-content: flex-end; }
.msg-other { justify-content: flex-start; }
.msg-bubble {
  max-width: 75%;
  padding: 8px 12px;
  border-radius: 10px;
  font-size: 0.9rem;
  position: relative;
  word-wrap: break-word;
}
.bubble-mine {
  background: #fef3c7;
  border-bottom-right-radius: 2px;
}
.bubble-other {
  background: #fff;
  border-bottom-left-radius: 2px;
}
.msg-author {
  font-size: 0.75rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 2px;
}
.msg-text { line-height: 1.4; }
.msg-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}
.msg-time {
  font-size: 0.65rem;
  color: #6b7280;
}
.editado-badge {
  color: #d97706;
  font-style: italic;
}
.btn-edit {
  background: none;
  border: none;
  font-size: 0.75rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  opacity: 0.4;
  transition: opacity 0.15s;
}
.msg-bubble:hover .btn-edit {
  opacity: 1;
}
.edit-input {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid #ffaa00;
  border-radius: 6px;
  font-size: 0.85rem;
  outline: none;
  box-sizing: border-box;
}
.edit-actions {
  display: flex;
  gap: 6px;
  margin-top: 4px;
}
.edit-cancel, .edit-save {
  padding: 3px 10px;
  border: none;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  font-weight: 600;
}
.edit-cancel { background: #f1f5f9; color: #475569; }
.edit-save { background: #ffaa00; color: #1a1a1a; }
.edit-save:disabled { opacity: 0.5; cursor: not-allowed; }
.chat-footer {
  padding: 10px 14px;
  background: #f0f0f0;
}
.chat-input-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}
.upload-icon-btn {
  cursor: pointer;
  color: #6b7280;
  display: flex;
  align-items: center;
  align-self: center;
  padding: 4px;
  border-radius: 8px;
  transition: all 0.15s;
}
.upload-icon-btn:hover {
  color: #ffaa00;
  background: #fff7e6;
}
.upload-icon-btn input { display: none; }
.chat-input {
  flex: 1;
  padding: 10px 14px;
  border: none;
  border-radius: 20px;
  font-size: 0.9rem;
  outline: none;
  background: #fff;
}
.btn-send {
  padding: 8px 16px;
  background: #ffaa00;
  color: #1a1a1a;
  border: none;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  white-space: nowrap;
}
.btn-send:disabled { opacity: 0.4; cursor: not-allowed; }
.input-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.inline-preview {
  position: relative;
  width: fit-content;
}
.inline-preview-img {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #d1d5db;
}
.inline-preview-x {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 18px; height: 18px;
  border-radius: 50%;
  border: none;
  background: rgba(239,68,68,0.9);
  color: #fff;
  font-size: 11px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}
.lightbox {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200;
}
.lightbox-img {
  max-width: 90%;
  max-height: 90%;
  border-radius: 8px;
}
.lightbox-close {
  position: absolute;
  top: 20px; right: 30px;
  background: none;
  border: none;
  color: #fff;
  font-size: 2rem;
  cursor: pointer;
}
</style>
