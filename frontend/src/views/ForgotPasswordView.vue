<template>
  <div class="forgot-password-container">
    <div class="forgot-card">
      <div class="forgot-header" v-if="step === 1">
        <h1>¿Olvidaste tu contraseña?</h1>
        <p>Te enviaremos un código de recuperación a tu correo.</p>
      </div>

      <!-- Paso 1: Ingresar correo -->
      <div v-if="step === 1" class="forgot-step">
        <div class="form-group">
          <label for="email">Correo electrónico</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="tu@correo.com"
            :class="{ 'input-error': emailError }"
            @blur="verificarEmail"
          />
          <span v-if="emailError" class="error-msg">{{ emailError }}</span>
        </div>
        <div class="form-group" v-if="sending">
          <p class="sending-msg center">Enviando código...</p>
        </div>
        <div class="form-group" v-if="!sending && messageSent">
          <p class="success-msg center">Código enviado. Revisa tu correo (incluye la bandeja de spam).</p>
        </div>
        <button
          v-if="!sending && !messageSent"
          @click="enviarCodigo"
          class="btn-primary"
          :disabled="!email || emailError || !emailPuedeRecuperar"
        >
          Enviar código
        </button>
        <button
          v-if="messageSent"
          @click="step = 2"
          class="btn-secondary"
        >
          Ya recibí el código
        </button>
      </div>

      <!-- Paso 2: Código + nueva contraseña -->
      <div v-if="step === 2" class="forgot-step">
        <div class="form-group">
          <label for="code">Código de verificación</label>
          <input
            id="code"
            v-model="code"
            type="text"
            maxlength="6"
            placeholder="123456"
            :class="{ 'input-error': codeError }"
          />
          <span v-if="codeError" class="error-msg">{{ codeError }}</span>
        </div>
        <div class="form-group">
          <label for="new_password">Nueva contraseña</label>
          <div class="input-wrapper">
            <input
              id="new_password"
              v-model="newPassword"
              :type="showNewPassword ? 'text' : 'password'"
              placeholder="Mínimo 6 caracteres"
              :class="{ 'input-error': newPasswordError }"
            />
            <button type="button" class="toggle-pw" @click="showNewPassword = !showNewPassword" :title="showNewPassword ? 'Ocultar' : 'Mostrar'">
              <svg v-if="showNewPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7fa7d4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7fa7d4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </div>
          <span v-if="newPasswordError" class="error-msg">{{ newPasswordError }}</span>
        </div>
        <div class="form-group">
          <label for="confirm_password">Confirmar contraseña</label>
          <div class="input-wrapper">
            <input
              id="confirm_password"
              v-model="confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="Repite la contraseña"
              :class="{ 'input-error': confirmPasswordError }"
            />
            <button type="button" class="toggle-pw" @click="showConfirmPassword = !showConfirmPassword" :title="showConfirmPassword ? 'Ocultar' : 'Mostrar'">
              <svg v-if="showConfirmPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7fa7d4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7fa7d4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </div>
          <span v-if="confirmPasswordError" class="error-msg">{{ confirmPasswordError }}</span>
        </div>
        <div class="form-group" v-if="resetting">
          <p class="sending-msg">Restableciendo contraseña...</p>
        </div>
        <button
          v-if="!resetting"
          @click="restablecer"
          class="btn-primary"
          :disabled="!code || !newPassword || !confirmPassword || codeError || newPasswordError || confirmPasswordError"
        >
          Restablecer contraseña
        </button>
      </div>

      <!-- Éxito -->
      <div v-if="step === 3" class="forgot-step success-step">
        <h2>✅ Contraseña actualizada</h2>
        <p>Tu contraseña se ha cambiado correctamente. Todas las sesiones activas se han cerrado por seguridad.</p>
        <router-link to="/login" class="btn-primary">Iniciar sesión</router-link>
      </div>

      <div class="forgot-footer">
        <router-link to="/login" class="text-link">← Volver al inicio de sesión</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";
import api from "@/services/api";

export default {
  name: "ForgotPasswordView",
  data() {
    return {
      step: 1, // 1 = email, 2 = código, 3 = éxito
      email: "",
      code: "",
      newPassword: "",
      confirmPassword: "",
      emailError: "",
      codeError: "",
      newPasswordError: "",
      confirmPasswordError: "",
      sending: false,
      resetting: false,
      messageSent: false,
      emailExiste: false,      // Si el email está registrado
      emailPuedeRecuperar: false, // Si es cliente o mecánico (puede recuperar)
      showNewPassword: false,
      showConfirmPassword: false,
    };
  },
  methods: {
    validarEmail() {
      this.emailError = "";
      if (!this.email) {
        this.emailError = "El correo es obligatorio.";
        this.emailExiste = false;
        this.emailPuedeRecuperar = false;
        return false;
      }
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!re.test(this.email)) {
        this.emailError = "Ingresa un correo válido.";
        this.emailExiste = false;
        this.emailPuedeRecuperar = false;
        return false;
      }
      return true;
    },
    async verificarEmail() {
      if (!this.validarEmail()) return;
      try {
        const { data } = await api.get("/auth/verificar-email", {
          params: { email: this.email },
        });
        this.emailExiste = data.existe;
        this.emailPuedeRecuperar = data.puede_recuperar;
        if (!data.existe) {
          this.emailError = "Este correo no está registrado en el sistema.";
        } else if (!data.puede_recuperar) {
          this.emailError = "Este correo no puede recuperar contraseña desde aquí.";
        } else {
          this.emailError = "";
        }
      } catch (err) {
        this.emailExiste = false;
        this.emailPuedeRecuperar = false;
        this.emailError = "Error al verificar el correo.";
      }
    },
    async enviarCodigo() {
      if (!this.validarEmail()) return;
      if (!this.emailPuedeRecuperar) return;
      this.sending = true;
      try {
        const { data } = await api.post("/auth/forgot-password", { email: this.email });
        if (data.email_enviado === false) {
          this.emailError = data.error || "No se pudo enviar el código. Inténtalo de nuevo.";
          this.messageSent = false;
        } else {
          this.messageSent = true;
        }
      } catch (err) {
        this.emailError = err.response?.data?.detail || "No se pudo enviar el código.";
        this.messageSent = false;
      } finally {
        this.sending = false;
      }
    },
    validarCodigo() {
      this.codeError = "";
      if (!this.code) {
        this.codeError = "El código es obligatorio.";
        return false;
      }
      if (!/^\d{6}$/.test(this.code)) {
        this.codeError = "El código debe tener 6 dígitos.";
        return false;
      }
      return true;
    },
    validarNuevaPassword() {
      this.newPasswordError = "";
      if (!this.newPassword) {
        this.newPasswordError = "La contraseña es obligatoria.";
        return false;
      }
      if (this.newPassword.length < 6) {
        this.newPasswordError = "Mínimo 6 caracteres.";
        return false;
      }
      return true;
    },
    validarConfirmarPassword() {
      this.confirmPasswordError = "";
      if (!this.confirmPassword) {
        this.confirmPasswordError = "Confirma tu contraseña.";
        return false;
      }
      if (this.confirmPassword !== this.newPassword) {
        this.confirmPasswordError = "Las contraseñas no coinciden.";
        return false;
      }
      return true;
    },
    async restablecer() {
      if (!this.validarCodigo()) return;
      if (!this.validarNuevaPassword()) return;
      if (!this.validarConfirmarPassword()) return;

      this.resetting = true;
      try {
        await api.post("/auth/reset-password", {
          email: this.email,
          code: this.code,
          new_password: this.newPassword,
        });
        this.step = 3;
        // Limpiar tokens por seguridad (sesiones cerradas en el backend)
        const authStore = useAuthStore();
        authStore.logout();
      } catch (err) {
        const detalle = err.response?.data?.detail || "Código inválido o expirado.";
        if (detalle.includes("Código incorrecto")) {
          this.codeError = "Código incorrecto. Inténtalo de nuevo.";
        } else {
          this.codeError = detalle;
        }
      } finally {
        this.resetting = false;
      }
    },
  },
};
</script>

<style scoped>
/* Contenedor igual al login — sin fondo gris */
.forgot-password-container {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  box-sizing: border-box;
}

/* Card igual al auth-card del login */
.forgot-card {
  background: #fff;
  border: 1px solid rgba(173, 201, 233, 0.5);
  border-radius: 20px;
  padding: 26px 32px 24px;
  width: 100%;
  max-width: 400px;
  box-sizing: border-box;
}

html:not(.dark) .forgot-card {
  box-shadow: 0 14px 36px rgba(22, 56, 95, 0.13), 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* Header igual al auth-header */
.forgot-header {
  text-align: center;
  margin-bottom: 20px;
}

.forgot-header h1 {
  margin: 0 0 6px 0;
  color: #16385f;
  font-size: 21px;
  font-weight: 800;
  letter-spacing: -0.4px;
  line-height: 1.25;
}

.forgot-header p {
  margin: 0;
  color: #6b8299;
  font-size: 13px;
}

/* Form groups igual al input-group del login */
.forgot-step {
  margin-bottom: 14px;
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 700;
  color: #1e3a5f;
  letter-spacing: 0.2px;
}

.form-group input {
  width: 100%;
  padding: 10px 14px;
  font-size: 14px;
  border: 1.5px solid #cbd5e1;
  border-radius: 8px;
  box-sizing: border-box;
}

.form-group input:focus {
  border-color: #ffaa00;
  outline: none;
  box-shadow: 0 0 0 3px rgba(255,170,0,0.15);
}

.form-group input.input-error {
  border-color: #dc2626;
}

.error-msg {
  color: #dc2626;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

/* Botón primario igual al btn-submit del login */
.btn-primary {
  width: 100%;
  padding: 12px;
  background-color: #FFAA00;
  color: #1a1a1a;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 8px;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255,170,0,0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Botón secundario igual al btn-secondary del admin */
.btn-secondary {
  width: 100%;
  padding: 10px;
  background-color: transparent;
  color: #FFAA00;
  border: 1px solid #FFAA00;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 8px;
}

.btn-secondary:hover {
  background: #fffbeb;
}

/* Link de texto igual al auth-footer */
.text-link {
  color: #6b8299;
  font-size: 13px;
  text-decoration: none;
}

.text-link:hover {
  color: #FFAA00;
  text-decoration: underline;
}

.sending-msg {
  color: #6b8299;
  font-size: 13px;
  margin-top: 8px;
}

.success-msg {
  color: #166534;
  font-size: 13px;
  margin-top: 8px;
}

.success-step {
  text-align: center;
}

.success-step h2 {
  color: #166534;
  margin-top: 0;
  font-size: 21px;
  font-weight: 800;
}

.center {
  text-align: center;
}

.forgot-footer {
  margin-top: 24px;
  text-align: center;
}

@media (max-width: 768px) {
  .forgot-card {
    width: 95%;
    padding: 20px 24px 16px;
  }
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper input {
  padding-right: 40px;
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
}

.toggle-pw svg {
  width: 18px;
  height: 18px;
}
</style>