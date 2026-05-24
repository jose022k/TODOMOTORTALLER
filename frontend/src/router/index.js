import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import HomeView from "../views/HomeView.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    path: "/about",
    name: "about",
    component: () =>
      import(/* webpackChunkName: "about" */ "../views/AboutView.vue"),
  },
  // Login Admin
  {
    path: "/login",
    name: "login",
    component: () =>
      import(/* webpackChunkName: "login-admin" */ "../views/AdminLoginView.vue"),
  },
  // Login Mecánico
  {
    path: "/loginMecanico",
    name: "login-mecanico",
    component: () =>
      import(/* webpackChunkName: "login-mecanico" */ "../views/MecanicoLoginView.vue"),
  },
  // Login Cliente
  {
    path: "/loginCliente",
    name: "login-cliente",
    component: () =>
      import(/* webpackChunkName: "login-cliente" */ "../views/ClienteLoginView.vue"),
  },
  // Registro público de clientes
  {
    path: "/register/cliente",
    name: "register-cliente",
    component: () =>
      import(/* webpackChunkName: "register-cliente" */ "../views/ClienteRegisterView.vue"),
  },
  // Registro de mecánicos (solo admin autenticado)
  {
    path: "/register",
    name: "register",
    component: () =>
      import(/* webpackChunkName: "register" */ "../views/RegisterView.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

router.beforeEach((to, from, next) => {
  const publicPages = ["/login", "/loginMecanico", "/loginCliente", "/register/cliente"];
  const authRequired = !publicPages.includes(to.path);
  const authStore = useAuthStore();

  if (authRequired && !authStore.isAuthenticated) {
    return next("/login");
  }

  // /register (mecánicos) solo para admins autenticados
  if (to.path === "/register" && authStore.isAuthenticated && !authStore.isAdmin) {
    return next("/");
  }

  next();
});

export default router;
