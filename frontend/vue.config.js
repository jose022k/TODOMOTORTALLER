const { defineConfig } = require("@vue/cli-service");
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      "/uploads": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/notifications": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  pwa: {
    name: "Todomotortaller",
    themeColor: "#ffaa00",
    msTileColor: "#1a1a1a",
    appleMobileWebAppCapable: "yes",
    manifestOptions: {
      display: "standalone",
      background_color: "#1a1a1a",
    },
    workboxPluginMode: "InjectManifest",
    workboxOptions: {
      swSrc: "./src/service-worker.js",
      swDest: "service-worker.js",
    },
  },
});
