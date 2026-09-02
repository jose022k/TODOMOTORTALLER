import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import "./assets/styles.css";
import "./registerServiceWorker";
import router from "./router";

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount("#app");
