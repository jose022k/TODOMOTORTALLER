import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";

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
  // Login unificado
  {
    path: "/login",
    name: "login",
    component: LoginView,
  },
  // Redirecciones de rutas antiguas de login
  {
    path: "/loginMecanico",
    redirect: "/login",
  },
  {
    path: "/loginCliente",
    redirect: "/login",
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
  {
    path: "/admin/service-orders",
    name: "admin-service-orders",
    component: () =>
      import(/* webpackChunkName: "admin-service-orders" */ "../views/AdminServiceOrdersView.vue"),
    meta: { requiresAuth: true, rol: "admin" },
  },
  {
    path: "/admin/reports",
    name: "admin-reports",
    component: () =>
      import(/* webpackChunkName: "admin-reports" */ "../views/AdminReportsView.vue"),
    meta: { requiresAuth: true, rol: "admin" },
  },
  // Mecánico
  {
    path: "/mecanico/orders",
    name: "mecanico-orders",
    component: () =>
      import(/* webpackChunkName: "mecanico-orders" */ "../views/MecanicoOrdersView.vue"),
    meta: { requiresAuth: true, rol: "mecanico" },
  },
  // Cliente
  {
    path: "/cliente/orders",
    name: "cliente-orders",
    component: () =>
      import(/* webpackChunkName: "cliente-orders" */ "../views/ClienteOrdersView.vue"),
    meta: { requiresAuth: true, rol: "cliente" },
  },
  // Tracker público (desde QR)
  {
    path: "/tracker/:id",
    name: "tracker",
    component: () =>
      import(/* webpackChunkName: "tracker" */ "../views/TrackerView.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

router.beforeEach((to, from, next) => {
  const publicPages = ["/login", "/register/cliente"];
  const authStore = useAuthStore();

  // Tracker público (sin auth)
  if (to.name === "tracker") return next();

  // Home page: redirigir según rol si está autenticado
  if (to.path === "/" && authStore.isAuthenticated) {
    if (authStore.isAdmin) return next("/admin");
    if (authStore.isMecanico) return next("/mecanico/orders");
    if (authStore.isCliente) return next("/cliente/orders");
  }

  // Page requires auth
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next("/login");
  }

  // Public pages only for non-authenticated
  if (publicPages.includes(to.path) && authStore.isAuthenticated) {
    if (authStore.isAdmin) return next("/admin");
    if (authStore.isMecanico) return next("/mecanico/orders");
    if (authStore.isCliente) return next("/cliente/orders");
    return next("/");
  }

  next();
});

export default router;
