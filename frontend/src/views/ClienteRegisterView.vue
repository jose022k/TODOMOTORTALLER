<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-logo">
          <img src="https://res.cloudinary.com/dorj3mvvr/image/upload/v1783609693/logos/logotaller01.png" alt="Todomotortaller" class="logo-img" />
        </div>
        <h1 class="auth-title">Crear Cuenta</h1>
        <p class="auth-desc">Regístrate como cliente del taller</p>
      </div>
      <form @submit.prevent="handleRegister">
        <div class="form-row">
          <div class="input-group">
            <label for="nombre">Nombre y apellido</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <input id="nombre" v-model="form.nombre" type="text" placeholder="Juan Perez" required @input="onNombreInput" />
            </div>
          </div>
          <div class="input-group">
            <label for="cedula">Cédula</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
              <input id="cedula" v-model="form.cedula" type="text" maxlength="8" placeholder="12345678" required @input="onCedulaInput" />
            </div>
          </div>
        </div>
        <div class="form-row">
          <div class="input-group">
            <label for="telefono">Teléfono</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
              <input id="telefono" v-model="form.telefono" type="tel" maxlength="10" placeholder="04121234567" required @input="onTelefonoInput" />
            </div>
          </div>
          <div class="input-group">
            <label for="email">Email</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
              <input id="email" v-model="form.email" type="email" placeholder="ejemplo@gmail.com" required />
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
              <input id="password" v-model="form.password" :type="showPassword ? 'text' : 'password'" placeholder="••••••••" required />
              <button type="button" class="toggle-pw" @click="showPassword = !showPassword" :title="showPassword ? 'Ocultar' : 'Mostrar'">
                <svg v-if="showPassword" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffaa00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffaa00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              </button>
            </div>
            <!-- Password strength indicator -->
            <div v-if="form.password" class="strength-meter">
              <div class="strength-bars">
                <div class="bar" :class="{ 'active weak': passwordStrength.level === 'weak' || passwordStrength.level === 'medium' || passwordStrength.level === 'strong' }"></div>
                <div class="bar" :class="{ 'active medium': passwordStrength.level === 'medium' || passwordStrength.level === 'strong' }"></div>
                <div class="bar" :class="{ 'active strong': passwordStrength.level === 'strong' }"></div>
              </div>
              <div class="strength-label" :class="passwordStrength.class">
                Contraseña {{ passwordStrength.label }}
                <span v-if="passwordStrength.level !== 'strong'" class="strength-hint">
                  (Fuerte: 8+ caracteres, mayúscula, número y símbolo)
                </span>
              </div>
            </div>
          </div>
          <div class="input-group">
            <label for="confirmPassword">Confirmar</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/><line x1="12" y1="16" x2="12" y2="16"/></svg>
              <input id="confirmPassword" v-model="confirmPassword" :type="showConfirm ? 'text' : 'password'" placeholder="••••••••" required />
              <button type="button" class="toggle-pw" @click="showConfirm = !showConfirm" :title="showConfirm ? 'Ocultar' : 'Mostrar'">
                <svg v-if="showConfirm" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffaa00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffaa00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              </button>
            </div>
          </div>
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="btn-submit" :disabled="loading">
          <span v-if="loading" class="btn-spinner"></span>
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
      showPassword: false,
      showConfirm: false,
      error: "",
      loading: false,
    };
  },
  computed: {
    passwordStrength() {
      const pw = this.form.password || "";
      if (!pw) return { label: "", level: "", class: "" };
      const hasMinLen = pw.length >= 8;
      const hasUpper = /[A-ZÁÉÍÓÚÑ]/.test(pw);
      const hasNumber = /[0-9]/.test(pw);
      const hasSymbol = /[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s]/.test(pw);

      if (hasMinLen && hasUpper && hasNumber && hasSymbol) {
        return { label: "Fuerte", level: "strong", class: "text-strong" };
      }
      if (pw.length >= 6 && ((hasUpper && hasNumber) || (hasNumber && hasSymbol) || (hasUpper && hasSymbol))) {
        return { label: "Media", level: "medium", class: "text-medium" };
      }
      return { label: "Débil", level: "weak", class: "text-weak" };
    },
  },
  methods: {
    onNombreInput(e) {
      let val = e.target.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]/g, "");
      this.form.nombre = val.replace(/\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]/g, (char) => char.toUpperCase());
    },
    onCedulaInput(e) {
      this.form.cedula = e.target.value.replace(/\D/g, "").slice(0, 8);
    },
    onTelefonoInput(e) {
      this.form.telefono = e.target.value.replace(/\D/g, "").slice(0, 10);
    },
    async handleRegister() {
      this.error = "";

      // 1. Validar Nombre
      if (!this.form.nombre.trim()) {
        this.error = "El nombre y apellido es obligatorio";
        return;
      }

      // 2. Validar Cédula (máximo 8 dígitos, solo números)
      if (!/^\d{5,8}$/.test(this.form.cedula)) {
        this.error = "La cédula debe contener solo números (máximo 8 dígitos)";
        return;
      }

      // 3. Validar Correo (@gmail.com, @outlook.com, @icloud.com)
      const emailOk = /^[^\s@]+@(gmail\.com|outlook\.com|icloud\.com)$/i.test(this.form.email.trim());
      if (!emailOk) {
        this.error = "El correo debe terminar en @gmail.com, @outlook.com o @icloud.com";
        return;
      }

      // 4. Validar Contraseña coincidente
      if (this.form.password !== this.confirmPassword) {
        this.error = "Las contraseñas no coinciden";
        return;
      }

      if (this.form.telefono.length < 10) {
        this.error = "El teléfono debe tener al menos 10 dígitos";
        return;
      }

      this.loading = true;
      try {
        const authStore = useAuthStore();
        await authStore.registerCliente({
          email: this.form.email.trim().toLowerCase(),
          nombre: this.form.nombre.trim(),
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
  align-items: flex-start;
  min-height: 80vh;
  padding-top: 10px;
}
.auth-card {
  background: #fff;
  border-radius: 20px;
  padding: 24px 40px 28px;
  width: 100%;
  max-width: 560px;
}
html:not(.dark) .auth-card {
  box-shadow: 0 10px 40px rgba(0,0,0,0.18), 0 4px 12px rgba(0,0,0,0.08);
}
.auth-header {
  text-align: center;
  margin-bottom: 14px;
}
.auth-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0;
}
.logo-img {
  height: 72px;
  width: auto;
  display: block;
}
.auth-title {
  font-size: 24px;
  font-weight: 800;
  color: #1a1a1a;
  letter-spacing: -0.3px;
  margin: 6px 0 0;
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
  margin-bottom: 12px;
}
.input-group label {
  display: block;
  margin-bottom: 4px;
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
.input-wrapper input::placeholder {
  color: #cbd5e1;
}
.error-msg {
  color: #e74c3c;
  font-size: 12.5px;
  margin-bottom: 6px;
  text-align: center;
  background: #fef2f2;
  padding: 5px 12px;
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
.toggle-pw {
  position: absolute;
  right: 8px;
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
.btn-spinner {
  width: 18px;
  height: 18px;
  display: inline-block;
  border-radius: 50%;
  background: conic-gradient(from 0deg, transparent 0deg, currentColor 120deg, transparent 300deg);
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 3px), #000 calc(100% - 2px));
  mask: radial-gradient(farthest-side, transparent calc(100% - 3px), #000 calc(100% - 2px));
  animation: spin 0.8s linear infinite;
  vertical-align: middle;
}
.auth-footer {
  margin-top: 16px;
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

/* ===== MOBILE / PWA native feel ===== */
@media (max-width: 768px) {
  .auth-container {
    align-items: flex-start;
    padding-top: 16px;
    padding-bottom: 80px;
  }
  .auth-card {
    border-radius: 16px;
    padding: 20px 20px 24px;
    margin: 0 4px;
  }
  .logo-img {
    height: 60px;
  }
  .auth-title {
    font-size: 22px;
  }
  .auth-desc {
    font-size: 13px;
  }
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  .input-group {
    margin-bottom: 14px;
  }
  .input-group label {
    font-size: 13px;
    margin-bottom: 5px;
  }
  .input-wrapper input {
    padding: 14px 14px 14px 42px;
    border-radius: 12px;
    font-size: 16px;
  }
  .input-icon {
    left: 14px;
  }
  .btn-submit {
    padding: 15px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 800;
    margin-top: 4px;
  }
  .toggle-pw {
    right: 10px;
    padding: 8px;
  }
  .auth-footer {
    font-size: 14px;
    margin-top: 20px;
  }
}
html.dark .auth-card {
  background: #1a1f2e;
}
html.dark .auth-title {
  color: #e2e8f0;
}
html.dark .auth-desc {
  color: #64748b;
}
html.dark .input-group label {
  color: #cbd5e1;
}
html.dark .input-wrapper input {
  background: #0f172a;
  border-color: #1e293b;
  color: #e2e8f0;
}
html.dark .input-wrapper input:focus {
  border-color: #ffaa00;
  background: #1e293b;
}
html.dark .input-wrapper input::placeholder {
  color: #475569;
}
html.dark .error-msg {
  background: #2d1215;
  color: #fca5a5;
}

/* Password strength meter */
.strength-meter {
  margin-top: 6px;
}
.strength-bars {
  display: flex;
  gap: 4px;
  height: 4px;
  width: 100%;
}
.bar {
  flex: 1;
  height: 100%;
  background: #e2e8f0;
  border-radius: 2px;
  transition: background 0.3s;
}
.bar.active.weak { background: #ef4444; }
.bar.active.medium { background: #f59e0b; }
.bar.active.strong { background: #10b981; }
.strength-label {
  font-size: 11.5px;
  font-weight: 700;
  margin-top: 4px;
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.text-weak { color: #ef4444; }
.text-medium { color: #f59e0b; }
.text-strong { color: #10b981; }
.strength-hint {
  font-size: 10.5px;
  font-weight: 500;
  color: #64748b;
}
html.dark .bar { background: #334155; }
html.dark .strength-hint { color: #94a3b8; }
</style>
