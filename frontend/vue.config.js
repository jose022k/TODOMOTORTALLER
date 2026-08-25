const { defineConfig } = require("@vue/cli-service");
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    allowedHosts: "all",
    proxy: {
      "/uploads": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/notifications": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/socket": {
        target: "http://localhost:8000",
        ws: true,
        changeOrigin: true,
      },
    },
  },
  pwa: {
    name: "Todomotortaller",
    short_name: "Todomotortaller",
    themeColor: "#ffaa00",
    msTileColor: "#1a1a1a",
    appleMobileWebAppCapable: "yes",
    appleMobileWebAppStatusBarStyle: "black-translucent",
    manifestOptions: {
      id: "/",
      display: "standalone",
      start_url: "/",
      scope: "/",
      description: "Sistema de gestión del taller mecánico",
      categories: ["business", "utilities"],
      background_color: "#1a1a1a",
      theme_color: "#ffaa00",
      icons: [
        { src: "img/icons/logo-192.png", sizes: "192x192", type: "image/png" },
        { src: "img/icons/logo-512.png", sizes: "512x512", type: "image/png" },
        { src: "img/icons/android-chrome-maskable-192x192.png", sizes: "192x192", type: "image/png", purpose: "maskable" },
        { src: "img/icons/android-chrome-maskable-512x512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
      ],
    },
    workboxPluginMode: "GenerateSW",
    workboxOptions: {
      skipWaiting: true,
      clientsClaim: true,
    },
  },
});