<template>
  <div id="app">
    <header class="app-header">
      <router-link to="/" class="logo">Todomotortaller</router-link>
      <nav class="app-nav">
        <router-link to="/">Home</router-link>
        <router-link to="/about">About</router-link>
        <template v-if="authStore.isAuthenticated">
          <span class="user-info">{{ authStore.user?.username }}</span>
          <button class="btn-logout" @click="handleLogout">Cerrar Sesión</button>
        </template>
        <template v-else>
          <router-link to="/login">Iniciar Sesión</router-link>
          <router-link to="/register">Registrarse</router-link>
        </template>
      </nav>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";

export default {
  name: "App",
  setup() {
    const authStore = useAuthStore();
    if (authStore.isAuthenticated && !authStore.user) {
      authStore.fetchUser();
    }
    return { authStore };
  },
  methods: {
    handleLogout() {
      this.authStore.logout();
      this.$router.push("/login");
    },
  },
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #1a1a1a;
  min-height: 100vh;
}
.app-header {
  background-color: #1a1a1a;
  padding: 16px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.logo {
  color: #ffaa00;
  font-size: 20px;
  font-weight: bold;
  text-decoration: none;
}
.app-nav {
  display: flex;
  align-items: center;
  gap: 16px;
}
.app-nav a {
  color: #ffffff;
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
}
.app-nav a:hover {
  color: #ffaa00;
}
.app-nav a.router-link-exact-active {
  color: #ffaa00;
}
.user-info {
  color: #b0b5b9;
  font-size: 14px;
}
.btn-logout {
  background: transparent;
  border: 1px solid #b0b5b9;
  color: #b0b5b9;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}
.btn-logout:hover {
  border-color: #ffaa00;
  color: #ffaa00;
}
.app-main {
  padding: 20px;
}
</style>
