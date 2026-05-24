<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1 class="auth-title">Iniciar Sesión</h1>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="tu@email.com"
            required
          />
        </div>
        <div class="form-group">
          <label for="password">Contraseña</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="••••••••"
            required
          />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="btn-primary btn-full" :disabled="loading">
          {{ loading ? "Entrando..." : "Iniciar Sesión" }}
        </button>
      </form>
      <p class="auth-link">
        ¿No tienes cuenta?
        <router-link to="/register">Regístrate</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";

export default {
  name: "LoginView",
  data() {
    return {
      email: "",
      password: "",
      error: "",
      loading: false,
    };
  },
  methods: {
    async handleLogin() {
      this.error = "";
      this.loading = true;
      try {
        const authStore = useAuthStore();
        await authStore.login(this.email, this.password);
        this.$router.push("/");
      } catch (err) {
        this.error =
          err.response?.data?.detail || "Error al iniciar sesión";
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
.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  margin-bottom: 4px;
  color: var(--color-dark);
  font-weight: 600;
  font-size: 14px;
}
.btn-full {
  width: 100%;
  margin-top: 8px;
}
.btn-full:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.error-msg {
  color: #e74c3c;
  font-size: 14px;
  margin-bottom: 8px;
  text-align: center;
}
.auth-link {
  margin-top: 16px;
  text-align: center;
  font-size: 14px;
  color: var(--color-muted);
}
</style>
