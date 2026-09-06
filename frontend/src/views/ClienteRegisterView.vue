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
      <!-- Botón de Google para registro de Clientes -->
      <div class="google-auth-box">
        <button type="button" class="btn-google" @click="triggerGoogleLogin" :disabled="loading || googleLoading">
          <span v-if="googleLoading" class="btn-spinner-google"></span>
          <svg v-else width="20" height="20" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
          </svg>
          <span>{{ googleLoading ? 'Conectando...' : 'Registrarse con Google' }}</span>
        </button>
      </div>

      <div class="divider">
        <span>o completa el formulario</span>
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

    <!-- Modal Completar Perfil de Google -->
    <div v-if="showGoogleModal" class="google-modal-backdrop" @click.self="showGoogleModal = false">
      <div class="google-modal-card">
        <div class="modal-header">
          <h2>Completar Datos de Registro</h2>
          <button class="btn-close" @click="showGoogleModal = false">&times;</button>
        </div>
        <p class="modal-sub">Ingresa tus datos requeridos para completar tu perfil de cliente:</p>
        <form @submit.prevent="submitGoogleProfile">
          <div class="form-group-modal">
            <label>Correo Electrónico (Google)</label>
            <input :value="googleForm.email" type="email" disabled class="input-disabled" />
          </div>
          <div class="form-group-modal">
            <label>Nombre y Apellido *</label>
            <input v-model="googleForm.nombre" type="text" required placeholder="Juan Pérez" @input="onNombreInputGoogle" />
          </div>
          <div class="form-group-modal">
            <label>Cédula *</label>
            <input v-model="googleForm.cedula" type="text" maxlength="8" placeholder="12345678" required @input="onCedulaInputGoogle" />
          </div>
          <div class="form-group-modal">
            <label>Teléfono *</label>
            <input v-model="googleForm.telefono" type="tel" maxlength="10" placeholder="04121234567" required @input="onTelefonoInputGoogle" />
          </div>
          <div class="form-group-modal">
            <label>Dirección</label>
            <input v-model="googleForm.direccion" type="text" placeholder="Av. Principal..." />
          </div>
          <div class="modal-actions-row">
            <button type="button" class="btn-secondary-modal" @click="showGoogleModal = false">Cancelar</button>
            <button type="submit" class="btn-primary-modal" :disabled="savingGoogle">
              {{ savingGoogle ? "Guardando..." : "Completar Registro" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <LoadingOverlay :visible="loading" text="Entrando al sistema..." />
  </div>
</template>

<script>
import api from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import LoadingOverlay from "@/components/LoadingOverlay.vue";

export default {
  name: "ClienteRegisterView",
  components: { LoadingOverlay },
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
      googleLoading: false,
      showGoogleModal: false,
      googleToken: "",
      savingGoogle: false,
      googleForm: {
        email: "",
        nombre: "",
        cedula: "",
        telefono: "",
        direccion: "",
      },
    };
  },
  mounted() {
    this.initGoogleAuth();
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
    initGoogleAuth() {
      // Usamos OAuth2 Token Client para abrir popup nativo de selección de cuenta
      this._googleClientReady = false;
      const clientId = process.env.VUE_APP_GOOGLE_CLIENT_ID || "216388527510-67ma9i2l90sqc14cd1aq23guutbtns45.apps.googleusercontent.com";
      const tryInit = () => {
        if (window.google && window.google.accounts && window.google.accounts.oauth2) {
          this._tokenClient = window.google.accounts.oauth2.initTokenClient({
            client_id: clientId,
            scope: "openid email profile",
            callback: (tokenResponse) => {
              if (tokenResponse.access_token) {
                this.processGoogleAccessToken(tokenResponse.access_token);
              } else {
                this.googleLoading = false;
                this.error = "No se pudo obtener acceso a Google. Intenta de nuevo.";
              }
            },
            error_callback: (err) => {
              this.googleLoading = false;
              if (err.type !== "popup_closed") {
                this.error = "Error al conectar con Google. Intenta de nuevo.";
              }
            },
          });
          this._googleClientReady = true;
        } else {
          setTimeout(tryInit, 200);
        }
      };
      tryInit();
    },
    triggerGoogleLogin() {
      if (!this._googleClientReady || !this._tokenClient) {
        this.error = "El servicio de Google no está disponible aún. Intenta de nuevo en un momento.";
        return;
      }
      this.googleLoading = true;
      this.error = "";
      // requestAccessToken abre el popup nativo de Google para seleccionar cuenta
      this._tokenClient.requestAccessToken({ prompt: "select_account" });
    },
    async processGoogleAccessToken(accessToken) {
      this.googleLoading = true;
      this.error = "";
      try {
        const { data } = await api.post("/auth/google/cliente", {
          access_token: accessToken,
        });
        this.googleToken = accessToken;

        if (data.needs_profile_completion) {
          this.googleForm = {
            email: data.google_email,
            nombre: data.google_name || "",
            cedula: "",
            telefono: "",
            direccion: "",
          };
          this.showGoogleModal = true;
        } else {
          this.loading = true;
          const authStore = useAuthStore();
          await authStore.setTokens(data.access_token, data.refresh_token);
          this.$router.push("/cliente/orders");
        }
      } catch (err) {
        this.loading = false;
        this.error = err.response?.data?.detail || "Error con autenticación de Google";
      } finally {
        this.googleLoading = false;
      }
    },
    onNombreInputGoogle(e) {
      let val = e.target.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]/g, "");
      this.googleForm.nombre = val.replace(/\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]/g, (char) => char.toUpperCase());
    },
    onCedulaInputGoogle(e) {
      this.googleForm.cedula = e.target.value.replace(/\D/g, "").slice(0, 8);
    },
    onTelefonoInputGoogle(e) {
      this.googleForm.telefono = e.target.value.replace(/\D/g, "").slice(0, 10);
    },
    async submitGoogleProfile() {
      if (!this.googleForm.nombre.trim()) {
        alert("El nombre y apellido es obligatorio.");
        return;
      }
      if (!/^\d{5,8}$/.test(this.googleForm.cedula)) {
        alert("La cédula debe contener solo números (máximo 8 dígitos).");
        return;
      }
      if (this.googleForm.telefono.length < 10) {
        alert("El teléfono debe tener al menos 10 dígitos.");
        return;
      }
      this.savingGoogle = true;
      this.loading = true;
      this.showGoogleModal = false;
      try {
        const { data } = await api.post("/auth/google/cliente/complete", {
          access_token: this.googleToken,
          cedula: this.googleForm.cedula,
          nombre: this.googleForm.nombre.trim(),
          telefono: this.googleForm.telefono,
          direccion: this.googleForm.direccion,
        });
        const authStore = useAuthStore();
        await authStore.setTokens(data.access_token, data.refresh_token);
        this.$router.push("/cliente/orders");
      } catch (err) {
        this.loading = false;
        this.showGoogleModal = true;
        alert(err.response?.data?.detail || "Error al completar el perfil.");
      } finally {
        this.savingGoogle = false;
      }
    },
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
  padding: 18px 32px 20px;
  width: 100%;
  max-width: 560px;
  box-sizing: border-box;
}
html:not(.dark) .auth-card {
  box-shadow: 0 10px 40px rgba(0,0,0,0.18), 0 4px 12px rgba(0,0,0,0.08);
}
.auth-header {
  text-align: center;
  margin-bottom: 10px;
}
.auth-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0;
}
.logo-img {
  height: 56px;
  width: auto;
  display: block;
}
.auth-title {
  font-size: 20px;
  font-weight: 800;
  color: #1a1a1a;
  letter-spacing: -0.3px;
  margin: 2px 0 0;
}
.auth-desc {
  font-size: 13px;
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
    padding-top: 10px;
    padding-bottom: 40px;
  }
  .auth-card {
    border-radius: 16px;
    padding: 16px 16px 20px;
    margin: 0 8px;
    max-width: 100%;
  }
  .logo-img {
    height: 48px;
  }
  .auth-title {
    font-size: 19px;
  }
  .auth-desc {
    font-size: 12.5px;
  }
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  .input-group {
    margin-bottom: 10px;
  }
  .input-group label {
    font-size: 12px;
    margin-bottom: 3px;
  }
  .input-wrapper input {
    padding: 10px 12px 10px 36px;
    border-radius: 10px;
    font-size: 14.5px;
  }
  .input-icon {
    left: 12px;
  }
  .btn-submit {
    padding: 11px;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 800;
    margin-top: 4px;
  }
  .toggle-pw {
    right: 8px;
    padding: 6px;
  }
  .auth-footer {
    font-size: 13px;
    margin-top: 12px;
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

/* Google Button & Divider */
.google-auth-box {
  margin-bottom: 8px;
  width: 100%;
  box-sizing: border-box;
}
.btn-google {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  padding: 9px 12px;
  height: 38px;
  background: #ffffff;
  border: 1.5px solid #cbd5e1;
  border-radius: 8px;
  color: #334155;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  white-space: nowrap;
  overflow: hidden;
}
.btn-google:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #94a3b8;
  transform: translateY(-1px);
}
.btn-google:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  transform: none;
}
html.dark .btn-google {
  background: #0f172a;
  border-color: #334155;
  color: #f8fafc;
}
html.dark .btn-google:hover:not(:disabled) {
  background: #1e293b;
}
.btn-spinner-google {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  display: inline-block;
  border-radius: 50%;
  border: 2px solid #cbd5e1;
  border-top-color: #4285F4;
  animation: spin 0.7s linear infinite;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 8px 0 12px;
  color: #94a3b8;
  font-size: 11.5px;
  font-weight: 600;
}
.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e2e8f0;
}
html.dark .divider::before,
html.dark .divider::after {
  border-bottom-color: #334155;
}
.divider span {
  padding: 0 10px;
}

/* Modal Google Completa Perfil */
.google-modal-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1200;
  padding: 16px;
}
.google-modal-card {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: 440px;
  padding: 24px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}
html.dark .google-modal-card {
  background: #1e293b;
  color: #f8fafc;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.modal-header h2 {
  font-size: 1.15rem;
  font-weight: 800;
  margin: 0;
}
.modal-sub {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 16px;
}
html.dark .modal-sub {
  color: #94a3b8;
}
.form-group-modal {
  margin-bottom: 14px;
}
.form-group-modal label {
  display: block;
  font-size: 12.5px;
  font-weight: 700;
  color: #475569;
  margin-bottom: 4px;
}
html.dark .form-group-modal label {
  color: #cbd5e1;
}
.form-group-modal input {
  width: 100%;
  padding: 10px 12px;
  border: 1.5px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}
html.dark .form-group-modal input {
  background: #0f172a;
  border-color: #334155;
  color: #f8fafc;
}
.input-disabled, input:disabled {
  background-color: #f1f5f9 !important;
  color: #64748b !important;
  cursor: not-allowed;
  border-color: #cbd5e1 !important;
}
html.dark .input-disabled, html.dark input:disabled {
  background-color: #0f172a !important;
  color: #94a3b8 !important;
  border-color: #334155 !important;
}
.modal-actions-row {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
.btn-primary-modal {
  padding: 10px 18px;
  background: #ffaa00;
  color: #1a1a1a;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
}
.btn-secondary-modal {
  padding: 10px 18px;
  background: transparent;
  border: 1px solid #cbd5e1;
  color: #475569;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
}
html.dark .btn-secondary-modal {
  border-color: #334155;
  color: #cbd5e1;
}
</style>
