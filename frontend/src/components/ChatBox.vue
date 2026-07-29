<template>
  <div class="chat-box">
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="chat-empty">
        No hay mensajes aún. Envía el primero.
      </div>
      <div
        v-for="msg in messages"
        :key="msg.id"
        :class="['chat-msg', { 'chat-msg-own': msg.remitente_rol === myRole && msg.remitente_id === myId }]"
      >
        <div class="msg-header">
          <strong class="msg-author">{{ msg.remitente_nombre }}</strong>
          <span class="msg-role" :class="'role-' + msg.remitente_rol">{{ msg.remitente_rol }}</span>
          <span class="msg-time">{{ formatTime(msg.fecha_hora) }}</span>
        </div>
        <div class="msg-body">{{ msg.contenido }}</div>
      </div>
    </div>
    <div class="chat-input-row">
      <input
        v-model="text"
        type="text"
        class="chat-input"
        placeholder="Escribe un mensaje..."
        @keyup.enter="send"
        :disabled="!canChat"
      />
      <button class="btn-chat-send" @click="send" :disabled="!canChat || !text.trim()">Enviar</button>
    </div>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  name: "ChatBox",
  props: {
    ordenId: { type: Number, required: true },
    canChat: { type: Boolean, default: false },
    myRole: { type: String, default: "" },
    myId: { type: Number, default: 0 },
  },
  data() {
    return {
      messages: [],
      text: "",
      polling: null,
    };
  },
  mounted() {
    this.fetchMessages();
    this.polling = setInterval(() => this.fetchMessages(), 5000);
  },
  beforeUnmount() {
    if (this.polling) clearInterval(this.polling);
  },
  methods: {
    async fetchMessages() {
      try {
        const { data } = await api.get(`/chat/${this.ordenId}`);
        this.messages = data;
        this.$nextTick(() => {
          const el = this.$refs.messagesContainer;
          if (!el) return;
          const threshold = 50;
          const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < threshold;
          if (nearBottom) el.scrollTop = el.scrollHeight;
        });
      } catch (e) { /* polling error silently */ }
    },
    scrollToBottom() {
      const el = this.$refs.messagesContainer;
      if (el) el.scrollTop = el.scrollHeight;
    },
    async send() {
      if (!this.text.trim()) return;
      const text = this.text;
      this.text = "";
      const tempMsg = { id: -Date.now(), contenido: text, fecha_hora: new Date().toISOString(), remitente_id: this.myId, remitente_rol: this.myRole, editado: false };
      this.messages.push(tempMsg);
      this.$nextTick(() => this.scrollToBottom());
      try {
        const { data } = await api.post(`/chat/${this.ordenId}`, { contenido: text, orden_servicio_id: this.ordenId });
        const idx = this.messages.indexOf(tempMsg);
        if (idx !== -1) this.messages.splice(idx, 1, data);
      } catch (err) {
        this.messages = this.messages.filter(m => m.id !== tempMsg.id);
        alert(err.response?.data?.detail || "Error al enviar mensaje");
      }
    },
    formatTime(dt) {
      if (!dt) return "";
      const d = new Date(dt);
      return d.toLocaleString("es-VE", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
    },
  },
};
</script>

<style scoped>
.chat-box {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}
.chat-messages {
  max-height: 300px;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.chat-empty {
  text-align: center;
  color: #94a3b8;
  padding: 24px;
  font-size: 0.9rem;
}
.chat-msg {
  background: #f8fafc;
  border-radius: 10px;
  padding: 10px 14px;
  max-width: 85%;
  align-self: flex-start;
}
.chat-msg-own {
  background: #eff6ff;
  align-self: flex-end;
}
.msg-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}
.msg-author {
  font-size: 0.82rem;
  color: #1e293b;
}
.msg-role {
  font-size: 0.7rem;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
  text-transform: uppercase;
}
.role-admin { background: #fef3c7; color: #92400e; }
.role-mecanico { background: #dbeafe; color: #1e40af; }
.role-cliente { background: #dcfce7; color: #166534; }
.msg-time {
  font-size: 0.7rem;
  color: #94a3b8;
  margin-left: auto;
}
.msg-body {
  font-size: 0.9rem;
  color: #334155;
  line-height: 1.4;
}
.chat-input-row {
  display: flex;
  border-top: 1px solid #e2e8f0;
}
.chat-input {
  flex: 1;
  border: none;
  padding: 12px 16px;
  font-size: 0.9rem;
  outline: none;
}
.chat-input:disabled {
  background: #f1f5f9;
  cursor: not-allowed;
}
.btn-chat-send {
  background: #ffaa00;
  color: #1a1a1a;
  border: none;
  padding: 12px 20px;
  font-weight: 700;
  cursor: pointer;
  font-size: 0.85rem;
}
.btn-chat-send:disabled {
  background: #e2e8f0;
  color: #94a3b8;
  cursor: not-allowed;
}
</style>
