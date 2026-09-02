<template>
  <div class="about">
    <!-- Map -->
    <div class="map-wrapper">
      <iframe
        src="https://maps.google.com/maps?q=10.338461,-67.038735&z=16&output=embed"
        width="100%"
        height="480"
        style="border:0; border-radius: 16px;"
        allowfullscreen=""
        loading="lazy"
      ></iframe>
      <a href="https://goo.gl/maps/tJmdf4q8x6SjhfM7A?g_st=am" target="_blank" class="maps-btn">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
        Abrir en Maps
      </a>

      <!-- Desktop contact card — overlaid on map, hidden on mobile -->
      <div class="contact-card desktop-only">
        <div class="contact-header">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffaa00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
          <span>Contacto</span>
        </div>
        <a href="https://wa.me/584142102141" target="_blank" class="contact-row whatsapp">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="#25D366" stroke="none"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
          <span class="contact-label">WhatsApp</span>
          <span class="contact-number">04142102141</span>
        </a>
        <a href="tel:+584127703652" class="contact-row call">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffaa00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"/></svg>
          <span class="contact-label">Llamadas</span>
          <span class="contact-number">04127703652</span>
        </a>
      </div>
    </div>

    <!-- Mobile FAB — appears BELOW the map, hidden on desktop -->
    <div class="mobile-contact-fab mobile-only">
      <!-- Panel renders FIRST in DOM so it appears above the button -->
      <transition name="fab-panel">
        <div v-if="contactOpen" class="fab-contact-card">
          <div class="contact-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffaa00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            <span>Contacto</span>
          </div>
          <a href="https://wa.me/584142102141" target="_blank" class="contact-row whatsapp">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="#25D366" stroke="none"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
            <span class="contact-label">WhatsApp</span>
            <span class="contact-number">04142102141</span>
          </a>
          <a href="tel:+584127703652" class="contact-row call">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffaa00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"/></svg>
            <span class="contact-label">Llamadas</span>
            <span class="contact-number">04127703652</span>
          </a>
        </div>
      </transition>

      <!-- Button always at bottom -->
      <button
        class="fab-btn"
        @click="contactOpen = !contactOpen"
        :aria-expanded="contactOpen"
        aria-label="Contacto"
      >
        <svg v-if="!contactOpen" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"/>
        </svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "AboutView",
  data() {
    return {
      contactOpen: false,
    };
  },
};
</script>

<style scoped>
.about {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

/* ---- Map ---- */
.map-wrapper {
  position: relative;
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.35);
  margin-top: 48px;
}
.map-wrapper iframe {
  display: block;
  border-radius: 16px;
}

/* ---- "Abrir en Maps" button ---- */
.maps-btn {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 10;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(6px);
  color: #1a1a1a;
  font-size: 13px;
  font-weight: 600;
  padding: 8px 14px;
  border-radius: 8px;
  text-decoration: none;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
  transition: background 0.2s;
}
.maps-btn:hover { background: #fff; color: #ffaa00; }

/* ---- Desktop contact card (absolute overlay on map) ---- */
.contact-card {
  position: absolute;
  bottom: 24px;
  right: 24px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(10px);
  border-radius: 14px;
  padding: 20px 24px;
  min-width: 220px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.5);
}

/* ---- Shared contact styles ---- */
.contact-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1a1a1a;
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(0,0,0,0.08);
}
.contact-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 8px;
  border-radius: 10px;
  text-decoration: none;
  transition: background 0.2s;
  color: #1a1a1a;
}
.contact-row:hover { background: rgba(255,170,0,0.12); }
.contact-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}
.contact-number {
  margin-left: auto;
  font-size: 14px;
  font-weight: 600;
  color: #ffaa00;
}
.contact-row.whatsapp .contact-number { color: #25D366; }

/* ---- Visibility helpers ---- */
.desktop-only { display: block; }
.mobile-only  { display: none;  }

/* ---- Mobile FAB (below map) ---- */
.mobile-contact-fab {
  flex-direction: column;
  align-items: flex-end;
  margin-top: 14px;
}
.fab-btn {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #ffaa00;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 18px rgba(255,170,0,0.45);
  transition: background 0.2s, transform 0.15s;
}
.fab-btn:active { transform: scale(0.93); }

.fab-contact-card {
  margin-bottom: 10px;
  width: 100%;
  background: rgba(255,255,255,0.97);
  backdrop-filter: blur(10px);
  border-radius: 14px;
  padding: 16px 18px;
  box-shadow: 0 6px 28px rgba(0,0,0,0.13);
  border: 1px solid rgba(255,255,255,0.5);
}

/* Slide-fade transition */
.fab-panel-enter-active,
.fab-panel-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}
.fab-panel-enter-from,
.fab-panel-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.97);
}

/* ---- Mobile breakpoint ---- */
@media (max-width: 768px) {
  .desktop-only { display: none !important; }
  .mobile-only  { display: flex !important; }
}
</style>
