const { defineConfig } = require("@vue/cli-service");

// Backend (siempre en la PC que ejecuta los servidores)
const API_TARGET = "http://localhost:8000";

/**
 * En desarrollo todo pasa por el servidor de desarrollo (puerto 8080):
 *
 *   navegador  →  https://192.168.0.194:8080/api/auth/login
 *             →  dev-server  →  http://localhost:8000/auth/login
 *
 * De esa forma el navegador nunca llama a otro puerto/IP, así que:
 *  - funciona desde la PC (localhost) y desde cualquier otro dispositivo,
 *  - no hay problemas de CORS,
 *  - no hace falta abrir el puerto 8000 en el Firewall de Windows.
 *
 * El prefijo "/api" evita chocar con rutas del frontend que empiezan igual
 * que endpoints del backend (/faq, /admin, /notifications).
 *
 * ⚠️ SE SIRVE POR HTTPS (candado). El navegador SOLO permite notificaciones,
 * Service Worker y PWA en páginas seguras (https:// o localhost); en http://
 * las bloquea por su cuenta. El certificado es autofirmado: la primera vez
 * que se abre la página en cada dispositivo hay que pulsar
 * "Avanzado → Continuar" en el aviso del navegador.
 */
const proxy = {
  "/api": {
    target: API_TARGET,
    changeOrigin: true,
    pathRewrite: { "^/api": "" },
  },
  // WebSocket en tiempo real (usa window.location, misma origen)
  "/socket": {
    target: API_TARGET,
    changeOrigin: true,
    ws: true,
  },
  // Recursos estáticos del backend (imágenes subidas y sonido de alerta)
  "/uploads": {
    target: API_TARGET,
    changeOrigin: true,
  },
  "/sounds": {
    target: API_TARGET,
    changeOrigin: true,
  },
};

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    // ⚠️ NECESARIO para las notificaciones, el Service Worker y el PWA.
    // El navegador bloquea todo eso en páginas http:// sin candado.
    // Certificado autofirmado: la primera vez hay que pulsar
    // "Avanzado → Continuar" en el aviso del navegador.
    https: true,
    allowedHosts: "all",
    headers: {
      "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
      Pragma: "no-cache",
      Expires: "0",
      "Surrogate-Control": "no-store",
    },
    proxy,
  },
});

















