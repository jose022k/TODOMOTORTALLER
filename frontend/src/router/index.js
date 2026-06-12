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
  // Admin
  {
    path: "/admin",
    name: "admin",
    component: () =>
      import(/* webpackChunkName: "admin" */ "../views/Admin.vue"),
    meta: { requiresAuth: true, rol: "admin" },
  },
  {
    path: "/admin/users",
    name: "admin-users",
    component: () =>
      import(/* webpackChunkName: "admin-users" */ "../views/AdminUsersView.vue"),
    meta: { requiresAuth: true, rol: "admin" },
  },
  {
    path: "/admin/catalog",
    name: "admin-catalog",
    component: () =>
      import(/* webpackChunkName: "admin-catalog" */ "../views/CatalogoMotosView.vue"),
    meta: { requiresAuth: true, rol: "admin" },
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

router.beforeEach((to, from, next) => {
  const publicPages = ["/login", "/loginMecanico", "/loginCliente", "/register/cliente"];
  const authStore = useAuthStore();

  // Page requires auth
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next("/login");
  }

  // Page requires admin role
  if (to.meta.rol === "admin" && authStore.isAuthenticated && !authStore.isAdmin) {
    return next("/");
  }

  // Public pages only for non-authenticated
  if (publicPages.includes(to.path) && authStore.isAuthenticated) {
    return next("/");
  }

  next();
});

export default router;
