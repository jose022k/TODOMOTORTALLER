<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-logo">
        <img src="https://res.cloudinary.com/dorj3mvvr/image/upload/v1783609693/logos/logotaller01.png" alt="Todomotortaller" class="logo-img" />
      </div>
      <h1 class="auth-title">Crear Cuenta</h1>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="nombre">Nombre Completo</label>
          <input id="nombre" v-model="form.nombre" type="text" placeholder="Nombre del mecánico" required />
        </div>
        <div class="form-group">
          <label for="email">Email</label>
          <input id="email" v-model="form.email" type="email" placeholder="mecanico@email.com" required />
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
        <p v-if="success" class="success-msg">{{ success }}</p>
        <button type="submit" class="btn-primary btn-full" :disabled="loading">
          {{ loading ? "Registrando..." : "Registrar Mecánico" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";

export default {
  name: "RegisterView",
  data() {
    return {
      form: { nombre: "", email: "", password: "" },
      confirmPassword: "",
      error: "",
      success: "",
      loading: false,
    };
  },
  methods: {
    async handleRegister() {
      this.error = "";
      this.success = "";
      if (this.form.password !== this.confirmPassword) {
        this.error = "Las contraseñas no coinciden";
        return;
      }
      this.loading = true;
      try {
        const authStore = useAuthStore();
        await authStore.registerMecanico({
          email: this.form.email,
          nombre: this.form.nombre,
          password: this.form.password,
        });
        this.success = "Mecánico registrado exitosamente";
        this.form = { nombre: "", email: "", password: "" };
        this.confirmPassword = "";
      } catch (err) {
        this.error = err.response?.data?.detail || "Error al registrar mecánico";
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
  padding: 20px 40px 40px;
  width: 100%;
  max-width: 400px;
}
.auth-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2px;
}
.logo-img {
  height: 50px;
  width: auto;
  display: block;
}
.auth-title {
  color: var(--color-dark);
  font-size: 24px;
  margin-bottom: 12px;
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
.success-msg { color: #2ecc71; font-size: 14px; margin-bottom: 8px; text-align: center; }
</style>
