<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-logo">
          <img src="https://res.cloudinary.com/dorj3mvvr/image/upload/v1783609693/logos/logotaller01.png" alt="Todomotortaller" class="logo-img" />
        </div>
        <h1 class="auth-title">Inicio de Sesión</h1>
        <p class="auth-desc">Accede al sistema del taller</p>
      </div>
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="email">Correo electrónico</label>
          <div class="input-wrapper">
            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            <input id="email" v-model="email" type="email" placeholder="tu@email.com" required />
          </div>
        </div>
        <div class="input-group">
          <label for="password">Contraseña</label>
          <div class="input-wrapper">
            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            <input id="password" v-model="password" :type="showPassword ? 'text' : 'password'" placeholder="••••••••" required />
            <button type="button" class="toggle-pw" @click="showPassword = !showPassword" :title="showPassword ? 'Ocultar' : 'Mostrar'">
              <svg v-if="showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ffaa00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ffaa00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </div>
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="btn-submit" :disabled="loading">
          <svg v-if="loading" class="btn-spinner" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10" stroke-dasharray="31.4 31.4" stroke-linecap="round"/></svg>
          <span>{{ loading ? "Entrando..." : "Iniciar Sesión" }}</span>
        </button>
      </form>
      <div class="auth-footer">
        ¿Eres cliente? <router-link to="/register/cliente">Regístrate aquí</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";

export default {
  name: "LoginView",
  data() {
    return { email: "", password: "", error: "", loading: false, showPassword: false };
  },
  methods: {
    async handleLogin() {
      this.error = "";
      this.loading = true;
      try {
        const authStore = useAuthStore();
        await authStore.login(this.email, this.password);
        if (authStore.isAdmin) this.$router.push("/admin");
        else if (authStore.isMecanico) this.$router.push("/mecanico/orders");
        else if (authStore.isCliente) this.$router.push("/cliente/orders");
        else this.$router.push("/");
      } catch (err) {
        this.error = err.response?.data?.detail || "Error al iniciar sesión";
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
  padding: 32px 40px 36px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04);
}
.auth-header {
  text-align: center;
  margin-bottom: 28px;
}
.auth-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}
.logo-img {
  height: 80px;
  width: auto;
  display: block;
}
.auth-title {
  font-size: 22px;
  font-weight: 800;
  color: #1a1a1a;
  letter-spacing: -0.3px;
  margin-bottom: 4px;
}
.auth-desc {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}
.input-group {
  margin-bottom: 18px;
}
.input-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
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
  left: 14px;
  color: #94a3b8;
  pointer-events: none;
  flex-shrink: 0;
}
.input-wrapper input {
  width: 100%;
  padding: 12px 14px 12px 42px;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
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
.toggle-pw {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: background 0.2s;
}
.toggle-pw:hover {
  background: rgba(255, 170, 0, 0.1);
}

.input-wrapper input::placeholder {
  color: #cbd5e1;
}
.error-msg {
  color: #e74c3c;
  font-size: 13px;
  margin-bottom: 12px;
  text-align: center;
  background: #fef2f2;
  padding: 8px 12px;
  border-radius: 8px;
}
.btn-submit {
  width: 100%;
  padding: 12px;
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
  margin-top: 24px;
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
