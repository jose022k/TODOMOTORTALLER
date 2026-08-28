<template>
  <div class="home">
    <div class="carousel-container">
      <div class="carousel-track" :style="{ transform: `translateX(-${currentIndex * 100}%)` }">
        <div v-for="(img, i) in images" :key="i" class="carousel-slide">
          <img :src="img" :alt="'Taller ' + (i + 1)" />
        </div>
      </div>
      <button class="carousel-btn carousel-prev" @click="prev">&#10094;</button>
      <button class="carousel-btn carousel-next" @click="next">&#10095;</button>
      <div class="carousel-dots">
        <span
          v-for="(img, i) in images"
          :key="'dot-' + i"
          :class="{ active: i === currentIndex }"
          @click="currentIndex = i"
        ></span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomeView",
  data() {
    return {
      images: [
        "https://res.cloudinary.com/dorj3mvvr/image/upload/v1785258214/taller1.jpg",
        "https://res.cloudinary.com/dorj3mvvr/image/upload/v1785258215/taller2.jpg",
        "https://res.cloudinary.com/dorj3mvvr/image/upload/v1785258215/taller3.jpg",
        "https://res.cloudinary.com/dorj3mvvr/image/upload/v1785258216/taller4.jpg",
      ],
      currentIndex: 0,
      interval: null,
    };
  },
  mounted() {
    this.startAutoPlay();
  },
  beforeUnmount() {
    clearInterval(this.interval);
  },
  methods: {
    next() {
      this.currentIndex = (this.currentIndex + 1) % this.images.length;
    },
    prev() {
      this.currentIndex = (this.currentIndex - 1 + this.images.length) % this.images.length;
    },
    startAutoPlay() {
      this.interval = setInterval(() => {
        this.next();
      }, 4000);
    },
  },
};
</script>

<style scoped>
.home {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 20px;
  min-height: calc(100vh - 80px);
  background: #ffffff;
}
.carousel-container {
  position: relative;
  width: 90%;
  max-width: 1100px;
  overflow: hidden;
  border-radius: 12px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.35);
}
.carousel-track {
  display: flex;
  transition: transform 0.5s ease-in-out;
}
.carousel-slide {
  min-width: 100%;
}
.carousel-slide img {
  width: 100%;
  height: 500px;
  object-fit: cover;
  display: block;
}
.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(0,0,0,0.4);
  color: #fff;
  border: none;
  font-size: 28px;
  padding: 12px 16px;
  cursor: pointer;
  border-radius: 4px;
  z-index: 2;
  transition: background 0.2s;
}
.carousel-btn:hover {
  background: rgba(0,0,0,0.7);
}
.carousel-prev { left: 12px; }
.carousel-next { right: 12px; }
.carousel-dots {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
}
.carousel-dots span {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255,255,255,0.5);
  cursor: pointer;
  transition: background 0.3s;
}
.carousel-dots span.active {
  background: #ffaa00;
}
</style>
