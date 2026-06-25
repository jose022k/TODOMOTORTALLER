<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-logo">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#ffaa00" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <h1 class="auth-title">Crear Cuenta</h1>
        <p class="auth-desc">Regístrate como cliente del taller</p>
      </div>
      <form @submit.prevent="handleRegister">
        <div class="form-row">
          <div class="input-group">
            <label for="nombre">Nombre</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <input id="nombre" v-model="form.nombre" type="text" placeholder="Juan Perez" required />
            </div>
          </div>
          <div class="input-group">
            <label for="cedula">Cédula</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
              <input id="cedula" v-model="form.cedula" type="text" placeholder="123456789" required />
            </div>
          </div>
        </div>
        <div class="form-row">
          <div class="input-group">
            <label for="telefono">Teléfono</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
              <input id="telefono" v-model="form.telefono" type="text" placeholder="+58 414 1234567" required />
            </div>
          </div>
          <div class="input-group">
            <label for="email">Email</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
              <input id="email" v-model="form.email" type="email" placeholder="tu@email.com" required />
            </div>
          </div>
        </div>
        <div class="input-group">
          <label for="direccion">Dirección</label>
          <div class="input-wrapper">
            <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
            <input id="direccion" v-model="form.direccion" type="text" placeholder="Av. Principal..." required />
          </div>
        </div>
        <div class="form-row">
          <div class="input-group">
            <label for="password">Contraseña</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              <input id="password" v-model="form.password" type="password" placeholder="••••••••" required />
            </div>
          </div>
          <div class="input-group">
            <label for="confirmPassword">Confirmar</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/><line x1="12" y1="16" x2="12" y2="16"/></svg>
              <input id="confirmPassword" v-model="confirmPassword" type="password" placeholder="••••••••" required />
            </div>
          </div>
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="btn-submit" :disabled="loading">
          <svg v-if="loading" class="btn-spinner" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10" stroke-dasharray="31.4 31.4" stroke-linecap="round"/></svg>
          <span>{{ loading ? "Registrando..." : "Crear Cuenta" }}</span>
        </button>
      </form>
      <div class="auth-footer">
        ¿Ya tienes cuenta? <router-link to="/login">Inicia Sesión aquí</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";

export default {
  name: "ClienteRegisterView",
  data() {
    return {
      form: {
        nombre: "",
        cedula: "",
        telefono: "",
        direccion: "",
        email: "",
        password: "",
      },
      confirmPassword: "",
      error: "",
      loading: false,
    };
  },
  methods: {
    async handleRegister() {
      this.error = "";
      if (this.form.password !== this.confirmPassword) {
        this.error = "Las contraseñas no coinciden";
        return;
      }
      this.loading = true;
      try {
        const authStore = useAuthStore();
        await authStore.registerCliente({
          email: this.form.email,
          nombre: this.form.nombre,
          cedula: this.form.cedula,
          telefono: this.form.telefono,
          direccion: this.form.direccion,
          password: this.form.password,
        });
        alert("Cuenta creada exitosamente. Ahora puedes iniciar sesión.");
        this.$router.push("/login");
      } catch (err) {
        this.error = err.response?.data?.detail || "Error al registrarse";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}
.auth-card {
  background: #fff;
  border-radius: 20px;
  padding: 36px 36px 32px;
  width: 100%;
  max-width: 520px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04);
}
.auth-header {
  text-align: center;
  margin-bottom: 24px;
}
.auth-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: #fff7e6;
  margin-bottom: 12px;
}
.auth-title {
  font-size: 22px;
  font-weight: 800;
  color: #1a1a1a;
  letter-spacing: -0.3px;
  margin-bottom: 2px;
}
.auth-desc {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}
.form-row {
  display: flex;
  gap: 12px;
}
.form-row .input-group {
  flex: 1;
  min-width: 0;
}
.input-group {
  margin-bottom: 14px;
}
.input-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 12.5px;
  font-weight: 700;
  color: #1a1a1a;
  letter-spacing: 0.2px;
}
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}
.input-icon {
  position: absolute;
  left: 12px;
  color: #94a3b8;
  pointer-events: none;
  flex-shrink: 0;
}
.input-wrapper input {
  width: 100%;
  padding: 10px 12px 10px 38px;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13.5px;
  color: #1a1a1a;
  background: #f8fafc;
  transition: all 0.2s;
  outline: none;
}
.input-wrapper input:focus {
  border-color: #ffaa00;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(255, 170, 0, 0.1);
}
.input-wrapper input::placeholder {
  color: #cbd5e1;
}
.error-msg {
  color: #e74c3c;
  font-size: 13px;
  margin-bottom: 10px;
  text-align: center;
  background: #fef2f2;
  padding: 7px 12px;
  border-radius: 8px;
}
.btn-submit {
  width: 100%;
  padding: 11px;
  border: none;
  border-radius: 10px;
  background: #ffaa00;
  color: #1a1a1a;
  font-size: 15px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-submit:hover:not(:disabled) {
  background: #f5a000;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 170, 0, 0.3);
}
.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
@keyframes spin { to { transform: rotate(360deg); } }
.btn-spinner { animation: spin 0.8s linear infinite; }
.auth-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #94a3b8;
}
.auth-footer a {
  color: #ffaa00;
  font-weight: 700;
  text-decoration: none;
}
.auth-footer a:hover {
  text-decoration: underline;
}
</style>
