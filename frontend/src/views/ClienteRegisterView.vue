<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1 class="auth-title">Crear Cuenta de Cliente</h1>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="nombre">Nombre Completo</label>
          <input id="nombre" v-model="form.nombre" type="text" placeholder="Juan Perez" required />
        </div>
        <div class="form-group">
          <label for="cedula">Cédula</label>
          <input id="cedula" v-model="form.cedula" type="text" placeholder="123456789" required />
        </div>
        <div class="form-group">
          <label for="telefono">Teléfono</label>
          <input id="telefono" v-model="form.telefono" type="text" placeholder="+58 414 1234567" required />
        </div>
        <div class="form-group">
          <label for="direccion">Dirección</label>
          <input id="direccion" v-model="form.direccion" type="text" placeholder="Av. Principal..." required />
        </div>
        <div class="form-group">
          <label for="email">Email</label>
          <input id="email" v-model="form.email" type="email" placeholder="tu@email.com" required />
        </div>
        <div class="form-group">
          <label for="password">Contraseña</label>
          <input id="password" v-model="form.password" type="password" placeholder="••••••••" required />
        </div>
        <div class="form-group">
          <label for="confirmPassword">Confirmar Contraseña</label>
          <input id="confirmPassword" v-model="confirmPassword" type="password" placeholder="••••••••" required />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="btn-primary btn-full" :disabled="loading">
          {{ loading ? "Registrando..." : "Crear Cuenta" }}
        </button>
      </form>
      <div class="auth-link">
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
  background: var(--color-light);
  border: 1px solid var(--color-muted);
  border-radius: 8px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
}
.auth-title {
  color: var(--color-dark);
  font-size: 24px;
  margin-bottom: 24px;
  text-align: center;
}
.form-group { margin-bottom: 16px; }
.form-group label {
  display: block;
  margin-bottom: 4px;
  color: var(--color-dark);
  font-weight: 600;
  font-size: 14px;
}
.btn-full { width: 100%; margin-top: 8px; }
.btn-full:disabled { opacity: 0.6; cursor: not-allowed; }
.error-msg { color: #e74c3c; font-size: 14px; margin-bottom: 8px; text-align: center; }
.auth-link { margin-top: 16px; text-align: center; font-size: 14px; color: var(--color-muted); }
.auth-link a { color: var(--color-primary); font-weight: 600; text-decoration: none; }
.auth-link a:hover { text-decoration: underline; }
</style>
