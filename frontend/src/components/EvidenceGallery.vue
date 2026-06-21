<template>
  <div class="evidence-gallery">
    <div v-if="evidencias.length === 0" class="ev-empty">
      No hay evidencias registradas.
    </div>
    <div v-else class="ev-grid">
      <div
        v-for="ev in evidencias"
        :key="ev.id"
        class="ev-item"
        @click="openLightbox(ev.url)"
      >
        <img :src="imageUrl(ev.url)" :alt="'Evidencia ' + ev.id" />
      </div>
    </div>

    <div class="ev-upload">
      <label v-if="!previewUrl" class="upload-btn">
        <span>+ Agregar Foto</span>
        <input type="file" accept="image/*" capture="environment" @change="selectFile" />
      </label>
      <div v-else class="preview-box">
        <button class="preview-x" title="Quitar foto" @click="clearPreview">×</button>
        <img :src="previewUrl" class="preview-img" />
        <button class="btn-primary btn-full" @click="confirmUpload" :disabled="uploading">{{ uploading ? "Subiendo..." : "Subir Foto" }}</button>
      </div>
    </div>

    <div v-if="lightboxUrl" class="lightbox" @click.self="lightboxUrl = ''">
      <img :src="lightboxUrl" class="lightbox-img" />
      <button class="lightbox-close" @click="lightboxUrl = ''">×</button>
    </div>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  name: "EvidenceGallery",
  props: {
    ordenId: { type: Number, required: true },
  },
  data() {
    return {
      evidencias: [],
      lightboxUrl: "",
      polling: null,
      selectedFile: null,
      previewUrl: "",
      uploading: false,
    };
  },
  mounted() {
    this.fetchEvidencias();
    this.polling = setInterval(() => this.fetchEvidencias(), 5000);
  },
  beforeUnmount() {
    if (this.polling) clearInterval(this.polling);
  },
  methods: {
    async fetchEvidencias() {
      try {
        const { data } = await api.get(`/chat/${this.ordenId}/evidencias`);
        this.evidencias = data;
      } catch (e) { /* polling error silently */ }
    },
    selectFile(e) {
      const file = e.target.files[0];
      if (!file) return;
      this.selectedFile = file;
      this.previewUrl = URL.createObjectURL(file);
    },
    clearPreview() {
      if (this.previewUrl) URL.revokeObjectURL(this.previewUrl);
      this.selectedFile = null;
      this.previewUrl = "";
    },
    async confirmUpload() {
      if (!this.selectedFile) return;
      this.uploading = true;
      const formData = new FormData();
      formData.append("file", this.selectedFile);
      try {
        await api.post(`/chat/${this.ordenId}/evidencias`, formData);
        this.clearPreview();
        await this.fetchEvidencias();
      } catch (err) {
        alert("Error al subir evidencia: " + (err.response?.data?.detail || err.message));
      } finally {
        this.uploading = false;
      }
    },
    imageUrl(url) {
      if (url && url.startsWith("/")) return api.defaults.baseURL + url;
      return url;
    },
    openLightbox(url) {
      this.lightboxUrl = this.imageUrl(url);
    },
  },
};
</script>

<style scoped>
.evidence-gallery {
  padding: 8px 0;
}
.ev-empty {
  text-align: center;
  color: #94a3b8;
  padding: 20px;
  font-size: 0.9rem;
}
.ev-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 8px;
}
.ev-item {
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid #e2e8f0;
  aspect-ratio: 1;
  position: relative;
}
.ev-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s;
}
.ev-item:hover img {
  transform: scale(1.05);
}
.lightbox {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.lightbox-img {
  max-width: 90%;
  max-height: 90%;
  border-radius: 8px;
}
.ev-upload { margin-top: 12px; }
.upload-btn {
  display: inline-block; padding: 8px 16px; background: #ffaa00; color: #1a1a1a;
  border-radius: 8px; font-weight: 600; font-size: 0.85rem; cursor: pointer;
  transition: background 0.2s;
}
.upload-btn:hover { background: #e09900; }
.upload-btn input { display: none; }
.preview-box {
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  padding: 8px;
  text-align: center;
  position: relative;
}
.preview-x {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  background: rgba(239,68,68,0.85);
  color: #fff;
  font-size: 15px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}
.preview-x:hover {
  background: #dc2626;
}
.preview-img {
  max-width: 100%;
  max-height: 180px;
  border-radius: 4px;
  margin-bottom: 8px;
}
.btn-full { width: 100%; }
.preview-box .btn-primary {
  padding: 6px 16px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
}
.preview-box .btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.lightbox-close {
  position: absolute;
  top: 20px;
  right: 30px;
  background: none;
  border: none;
  color: #fff;
  font-size: 2rem;
  cursor: pointer;
}
</style>
