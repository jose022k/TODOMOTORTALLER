<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1 class="auth-title">Bienvenido a TodoMotor Taller</h1>
      <p class="auth-subtitle">Selecciona tu tipo de usuario para iniciar sesión</p>
      <div class="login-options">
        <router-link to="/login/cliente" class="login-option btn-primary">
          🏍️ Soy Cliente
        </router-link>
        <router-link to="/login/mecanico" class="login-option btn-secondary">
          🔧 Soy Mecánico
        </router-link>
        <router-link to="/login/admin" class="login-option btn-admin">
          🛡️ Soy Administrador
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "LoginView",
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
  max-width: 420px;
  text-align: center;
}
.auth-title {
  color: var(--color-dark);
  font-size: 24px;
  margin-bottom: 8px;
}
.auth-subtitle {
  color: var(--color-muted);
  font-size: 14px;
  margin-bottom: 28px;
}
.login-options {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.login-option {
  display: block;
  padding: 14px 20px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
  text-align: center;
  transition: transform 0.15s, box-shadow 0.15s;
}
.login-option:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.btn-primary {
  background: var(--color-primary);
  color: white;
}
.btn-secondary {
  background: #2ecc71;
  color: white;
}
.btn-admin {
  background: #34495e;
  color: white;
}
</style>
