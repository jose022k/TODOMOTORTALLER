<template>
  <div class="chat-overlay" @click.self="$emit('close')">
    <div class="chat-modal">
      <div class="chat-header">
        <div class="chat-header-main">
          <h3>Chat — Orden #{{ ordenId }}</h3>
          <button class="chat-close" @click="$emit('close')">×</button>
        </div>
        <div class="chat-presencia">
          <span v-if="rolesEnLinea.length === 0" class="presencia-vacio">Nadie más conectado ahora</span>
          <span v-for="rol in rolesEnLinea" :key="'on-' + rol" class="presencia-chip">
            <span class="presencia-punto"></span>En línea {{ etiquetaRol(rol) }}
          </span>
        </div>
      </div>

      <div class="chat-body" ref="chatBody">
        <div v-if="messages.length === 0 && evidencias.length === 0" class="chat-empty">
          No hay mensajes aún. Envía el primero.
        </div>

        <template v-for="item in timeline" :key="item.key">
          <!-- Evidencia suelta (sin mensaje) -->
          <div v-if="item.type === 'evidencia'" class="evidencia-bubble">
            <img :src="imageUrl(item.url)" class="evidencia-img" @load="onImageLoad" @click="openLightbox(imageUrl(item.url))" />
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
                    :key="ev._key || ev.id"
                    :src="imageUrl(ev.url)"
                    class="attached-img"
                    @load="onImageLoad"
                    @click="openLightbox(imageUrl(ev.url))"
                  />
                </div>
                <div v-if="item.contenido" class="msg-text">{{ item.contenido }}</div>
                <div class="msg-footer">
                  <span class="msg-time">{{ formatTime(item.fecha_hora) }}<span v-if="item.editado" class="editado-badge"> · editado</span></span>
                  <button v-if="item.mine && item.canEdit" class="btn-edit" title="Editar mensaje" @click.stop="startEdit(item)"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.85 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg></button>
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
        <div v-if="quienEscribe.length" class="chat-escribiendo">
          <span v-for="rol in quienEscribe" :key="'typ-' + rol" class="escribiendo-chip">
            {{ etiquetaRol(rol) }} escribiendo<span class="puntos"><i>.</i><i>.</i><i>.</i></span>
          </span>
        </div>
        <div class="chat-input-row">
          <div class="upload-btns">
            <label class="upload-icon-btn" title="Tomar foto">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                <circle cx="12" cy="13" r="4"/>
              </svg>
              <input type="file" accept="image/*" capture="environment" @change="selectFile" />
            </label>
            <label class="upload-icon-btn" title="Elegir de galería">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
              <input type="file" accept="image/*" @change="selectFile" />
            </label>
          </div>
          <div class="input-wrap">
            <div v-if="previewUrl" class="inline-preview">
              <img :src="previewUrl" class="inline-preview-img" />
              <button class="inline-preview-x" @click="clearPreview">×</button>
            </div>
            <input
              v-model="text"
              class="chat-input"
              placeholder="Escribe un mensaje..."
              @input="onInput"
              @blur="detenerEscritura"
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
import { avisarEscritura } from "@/services/orderSocket";

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
      atBottom: true,   // si el usuario está al final del chat (se actualiza con su scroll)
      participantes: [], // quién participa en la orden y quién está conectado
      escribiendoPor: {}, // rol -> timestamp de "está escribiendo"
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
          items.push({ type: "evidencia", key: "ev" + (e._key || e.id), url: e.url, fecha: e.fecha });
        }
      });
      this.messages.forEach((m) => {
        const mine = m.remitente_id === this.myId && m.remitente_rol === this.myRole;
        const msgDate = new Date(m.fecha_hora);
        const canEdit = mine && (now - msgDate) < 600000;
        const attached = evidenciasByMsg[m.id] || [];
        items.push({
          type: "mensaje",
          key: "msg" + (m._key || m.id),
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
    rolesEnLinea() {
      // Solo el ROL (sin nombres) y sin repetir: si hay dos admins conectados
      // se muestra un único "En línea Admin".
      const roles = [];
      this.participantes.forEach((p) => {
        if (!p.online) return;
        if (p.rol === this.myRole && p.id === this.myId) return;
        if (!roles.includes(p.rol)) roles.push(p.rol);
      });
      return roles;
    },
    quienEscribe() {
      const ahora = Date.now();
      return Object.keys(this.escribiendoPor).filter(
        (rol) => ahora - this.escribiendoPor[rol] < 4000
      );
    },
  },
  methods: {
    async fetchAll() {
      try {
        const [msgRes, evRes] = await Promise.all([
          api.get(`/chat/${this.ordenId}`),
          api.get(`/chat/${this.ordenId}/evidencias`),
        ]);
        // Conserva las claves locales: así Vue reutiliza los nodos del DOM en vez
        // de destruirlos y recrearlos en cada sondeo (evita saltos de scroll).
        const msgKeys = {};
        this.messages.forEach(m => { if (m._key && m.id) msgKeys[m.id] = m._key; });
        const evKeys = {};
        this.evidencias.forEach(e => { if (e._key && e.id) evKeys[e.id] = e._key; });
        const localLinks = {};
        this.evidencias.forEach(e => { if (e.id && e.mensaje_id) localLinks[e.id] = e.mensaje_id; });

        this.messages = msgRes.data.map(m => ({ ...m, _key: msgKeys[m.id] || m.id }));
        this.evidencias = evRes.data.map(ev => {
          if (localLinks[ev.id]) ev.mensaje_id = localLinks[ev.id];
          return { ...ev, _key: evKeys[ev.id] || ev.id };
        });
        await this.$nextTick();
        this.scrollDown();
      } catch (e) { /* polling error silently */ }
    },
    scrollDown(forzar = false) {
      const el = this.$refs.chatBody;
      if (!el) return;
      // Si el usuario subió para leer el historial, NO se lo arrastramos hacia abajo.
      // 'this.atBottom' conserva el valor previo a la actualización, por eso funciona.
      if (!forzar && !this.atBottom) return;
      const bajar = () => { el.scrollTop = el.scrollHeight; };
      this.$nextTick(() => {
        bajar();
        // Las imágenes terminan de cargar después y agrandan el contenido
        requestAnimationFrame(bajar);
      });
    },
    onChatScroll() {
      const el = this.$refs.chatBody;
      if (!el) return;
      this.atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 60;
    },
    onImageLoad() {
      // Al cargar una imagen crece el contenido: si estábamos abajo, seguimos abajo
      if (this.atBottom) this.scrollDown(true);
    },
    async send() {
      this.detenerEscritura();
      const textContent = this.text.trim();
      const file = this.selectedFile;
      if (!textContent && !file) return;
      this.uploading = true;
      const tempId = -Date.now();
      let tempMsg = null;
      let tempEv = null;
      if (textContent) {
        tempMsg = { _key: tempId, id: tempId, contenido: textContent, fecha_hora: new Date().toISOString(), remitente_id: this.myId, remitente_rol: this.myRole, editado: false };
        this.messages.push(tempMsg);
        this.text = "";
      }
      if (file) {
        tempEv = { _key: tempId, id: tempId, url: this.previewUrl, mensaje_id: textContent ? tempId : null, fecha: new Date().toISOString() };
        this.evidencias.push(tempEv);
        this.clearPreview();
      }
      try {
        if (textContent && file) {
          const msgRes = await api.post(`/chat/${this.ordenId}`, { contenido: textContent, orden_servicio_id: this.ordenId });
          Object.assign(tempMsg, msgRes.data);
          const fd = new FormData();
          fd.append("file", file);
          fd.append("mensaje_id", msgRes.data.id);
          const evRes = await api.post(`/chat/${this.ordenId}/evidencias`, fd);
          const evIdx = this.evidencias.indexOf(tempEv);
          const realEv = { _key: tempEv._key, ...evRes.data };
          if (evIdx !== -1) this.evidencias.splice(evIdx, 1, realEv);
        } else if (file) {
          const fd = new FormData();
          fd.append("file", file);
          const evRes = await api.post(`/chat/${this.ordenId}/evidencias`, fd);
          const evIdx = this.evidencias.indexOf(tempEv);
          if (evIdx !== -1) this.evidencias.splice(evIdx, 1, { _key: tempEv._key, ...evRes.data });
        } else if (textContent) {
          const msgRes = await api.post(`/chat/${this.ordenId}`, { contenido: textContent, orden_servicio_id: this.ordenId });
          Object.assign(tempMsg, msgRes.data);
        }
      } catch (err) {
        if (tempMsg) this.messages = this.messages.filter(m => (m._key || m.id) !== (tempMsg._key || tempMsg.id));
        if (tempEv) this.evidencias = this.evidencias.filter(e => (e._key || e.id) !== (tempEv._key || tempEv.id));
        alert("Error al enviar: " + (err.response?.data?.detail || err.message));
      } finally {
        this.uploading = false;
        // Al enviar un mensaje propio SIEMPRE se baja al final
        this.atBottom = true;
        this.scrollDown(true);
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
    onOrderUpdated(event) {
      // Cerramos el chat si la orden dejó de estar "en proceso".
      const detail = event && event.detail ? event.detail : {};
      const orderId = detail.order_id ?? detail.orden_servicio_id;
      const newStatus = detail.estado;
      if (orderId === this.ordenId && newStatus && newStatus !== "en_proceso") {
        this.$emit("close");
      }
    },
    onVisible() {
      if (document.visibilityState === "visible") {
        this.fetchAll();
        this.fetchPresence();
      }
    },
    async fetchPresence() {
      // Carga quiénes participan en la orden y quién está conectado ("En línea")
      try {
        const { data } = await api.get(`/chat/${this.ordenId}/presencia`);
        const lista = [];
        if (data.cliente) lista.push(data.cliente);
        if (data.mecanico) lista.push(data.mecanico);
        (data.admins || []).forEach((a) => lista.push(a));
        this.participantes = lista;
      } catch (e) { /* sin backend: se reintenta en el siguiente sondeo */ }
    },
    etiquetaRol(rol) {
      if (rol === "mecanico") return "Mecánico";
      if (rol === "cliente") return "Cliente";
      if (rol === "admin") return "Admin";
      return rol;
    },
    onTyping(event) {
      // Alguien del chat está escribiendo (o dejó de escribir)
      const d = event && event.detail;
      if (!d || d.orden_id !== this.ordenId) return;
      if (d.rol === this.myRole && d.user_id === this.myId) return;

      clearTimeout(this._typingTimers && this._typingTimers[d.rol]);
      const copia = { ...this.escribiendoPor };

      if (d.tipo === "escribiendo") {
        copia[d.rol] = Date.now();
        // Si no llega ningún aviso nuevo, el indicador se apaga solo
        if (!this._typingTimers) this._typingTimers = {};
        this._typingTimers[d.rol] = setTimeout(() => {
          const actual = { ...this.escribiendoPor };
          delete actual[d.rol];
          this.escribiendoPor = actual;
        }, 4000);
      } else {
        delete copia[d.rol];
      }
      this.escribiendoPor = copia;
    },
    onInput() {
      const escribiendo = this.text.trim().length > 0;
      clearTimeout(this._typingKeepalive);

      if (!escribiendo) {
        this.detenerEscritura();
        return;
      }
      if (!this._escribiendo) {
        this._escribiendo = true;
        avisarEscritura(this.ordenId, true);
      }
      // Si pasa un rato sin escribir, se avisa al resto que ya no está escribiendo
      this._typingKeepalive = setTimeout(() => this.detenerEscritura(), 2500);
    },
    detenerEscritura() {
      clearTimeout(this._typingKeepalive);
      if (!this._escribiendo) return;
      this._escribiendo = false;
      avisarEscritura(this.ordenId, false);
    },
    onChatActualizado(event) {
      // Evento WebSocket: alguien escribió o adjuntó algo en el chat.
      // Solo se recarga ESTE chat si es de esta orden; la lista de órdenes no se toca.
      const orden = event && event.detail ? event.detail.orden_id : null;
      if (orden !== this.ordenId) return;
      this.fetchAll();
    },
    onPresenceChanged(event) {
      const d = event && event.detail;
      if (!d) return;
      const p = this.participantes.find((x) => x.id === d.user_id && x.rol === d.rol);
      if (p) p.online = !!d.online;
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
      let str = String(d);
      if (!str.endsWith("Z") && !str.includes("+") && !str.includes("-", 10)) {
        str += "Z";
      }
      const dt = new Date(str);
      if (isNaN(dt.getTime())) return "";
      return dt.toLocaleTimeString("es-VE", { hour: "2-digit", minute: "2-digit", hour12: true });
    },
  },
  mounted() {
    // Registra la posición del usuario en el chat (¿está al final o leyendo arriba?)
    this._onScroll = () => this.onChatScroll();
    const el = this.$refs.chatBody;
    if (el) el.addEventListener("scroll", this._onScroll, { passive: true });

    this.atBottom = true;
    this.fetchAll().then(() => this.scrollDown(true));
    this.fetchPresence();

    // El chat se actualiza AL INSTANTE por WebSocket ("chat-actualizado").
    // Este sondeo lento es solo una red de seguridad por si se cae la conexión.
    this.polling = setInterval(() => {
      this.fetchAll();
      this.fetchPresence();
    }, 10000);

    document.addEventListener("visibilitychange", this.onVisible);
    window.addEventListener("order-updated", this.onOrderUpdated);
    window.addEventListener("chat-actualizado", this.onChatActualizado);
    window.addEventListener("presence-changed", this.onPresenceChanged);
    window.addEventListener("typing", this.onTyping);
  },
  beforeUnmount() {
    this.detenerEscritura();
    if (this._typingTimers) {
      Object.values(this._typingTimers).forEach((t) => clearTimeout(t));
    }
    if (this.polling) clearInterval(this.polling);
    const el = this.$refs.chatBody;
    if (el && this._onScroll) el.removeEventListener("scroll", this._onScroll);
    document.removeEventListener("visibilitychange", this.onVisible);
    window.removeEventListener("order-updated", this.onOrderUpdated);
    window.removeEventListener("chat-actualizado", this.onChatActualizado);
    window.removeEventListener("presence-changed", this.onPresenceChanged);
    window.removeEventListener("typing", this.onTyping);
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
  padding: 12px 18px 10px;
  background: #ffaa00;
  color: #1a1a1a;
}
.chat-header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.chat-header h3 { font-size: 1rem; margin: 0; }
.chat-close { background: none; border: none; width: 36px; height: 36px; border-radius: 8px; color: #1a1a1a; font-size: 1.5rem; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.chat-close:hover { background: #fee2e2; color: #dc2626; }
.chat-presencia {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
  min-height: 18px;
}
.presencia-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.72rem;
  font-weight: 600;
  background: rgba(255,255,255,0.75);
  border-radius: 999px;
  padding: 2px 9px;
  color: #166534;
}
.presencia-punto {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 2px rgba(34,197,94,0.25);
  flex: 0 0 auto;
}
.presencia-vacio {
  font-size: 0.72rem;
  font-weight: 500;
  color: #78350f;
  opacity: 0.75;
}
/* Indicador "escribiendo..." — abajo, sobre el campo de texto (estilo WhatsApp) */
.chat-escribiendo {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  min-height: 18px;
  padding: 0 4px 5px;
}
.escribiendo-chip {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 0.8rem;
  font-style: italic;
  font-weight: 500;
  color: #6b7280;
  line-height: 1.1;
}
.escribiendo-chip .puntos i {
  font-style: normal;
  animation: escribiendoPunto 1.2s infinite;
}
.escribiendo-chip .puntos i:nth-child(2) { animation-delay: 0.2s; }
.escribiendo-chip .puntos i:nth-child(3) { animation-delay: 0.4s; }
@keyframes escribiendoPunto {
  0%, 60%, 100% { opacity: 0.25; }
  30% { opacity: 1; }
}
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
  flex-direction: column;
  gap: 4px;
  margin-bottom: 6px;
}
.attached-img {
  width: 100%;
  max-height: 280px;
  object-fit: cover;
  border-radius: 10px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.msg-row {
  display: flex;
  margin-bottom: 2px;
}
.msg-mine { justify-content: flex-end; }
.msg-other { justify-content: flex-start; }
.msg-bubble {
  max-width: 75%;
  padding: 8px 12px;
  border-radius: 14px;
  font-size: 0.9rem;
  position: relative;
  word-wrap: break-word;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}
.bubble-mine {
  background: #fff3cd;
  border-bottom-right-radius: 4px;
}
.bubble-other {
  background: #fff;
  border-bottom-left-radius: 4px;
}
.msg-author {
  font-size: 0.7rem;
  font-weight: 600;
  color: #9ca3af;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.msg-text { line-height: 1.45; color: #1f2937; }
.msg-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}
.msg-time {
  font-size: 0.6rem;
  color: #9ca3af;
}
.editado-badge {
  color: #d97706;
  font-style: italic;
}
.btn-edit {
  background: none;
  border: none;
  cursor: pointer;
  padding: 3px;
  line-height: 1;
  opacity: 0;
  color: #9ca3af;
  border-radius: 6px;
  transition: all 0.15s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.btn-edit:hover {
  opacity: 1 !important;
  color: #ffaa00;
  background: rgba(255,170,0,0.1);
}
.msg-bubble:hover .btn-edit {
  opacity: 0.5;
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
.upload-btns {
  display: flex;
  gap: 2px;
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
