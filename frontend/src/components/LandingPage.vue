<template>
  <div class="landing-container">
    <img src="@/assets/imgs/BaseLayerCapital.png" alt="Base Layer Capital Logo" class="logo" />
    <p class=" tagline">
        Volatility is Vitality
    </p>

    <svg class="ekg-line" viewBox="0 0 500 100" preserveAspectRatio="none">
        <polyline 
            fill="none"
            stroke="#f7931a"
            stroke-width="3"
            points="
            50,50 60,50 65,30 75,70 85,50 100,50 110,20 120,80 130,50
            150,50 160,30 170,70 180,50 190,50 200,20 210,80 220,50
            240,50 250,30 260,70 270,50 280,50 290,20 300,80 310,50
            "
        >
            <animate attributeName="points"
            dur="2s"
            repeatCount="indefinite"
            values="
                50,50 60,50 65,30 75,70 85,50 100,50 110,20 120,80 130,50
                150,50 160,30 170,70 180,50 190,50 200,20 210,80 220,50
                240,50 250,30 260,70 270,50 280,50 290,20 300,80 310,50;

                50,50 60,50 65,70 75,30 85,50 100,50 110,80 120,20 130,50
                150,50 160,70 170,30 180,50 190,50 200,80 210,20 220,50
                240,50 250,70 260,30 270,50 280,50 290,80 300,20 310,50;

                50,50 60,50 65,30 75,70 85,50 100,50 110,20 120,80 130,50
                150,50 160,30 170,70 180,50 190,50 200,20 210,80 220,50
                240,50 250,30 260,70 270,50 280,50 290,20 300,80 310,50
            "
            />
        </polyline>
    </svg>
  </div>
</template>

<style scoped>
.landing-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  text-align: center;
  padding: 2rem;
  box-sizing: border-box;
}

.logo {
  max-width: 300px;
  width: 80%;
  height: auto;
}

.tagline {
  margin-top: 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #f7931a;
  animation: pulse 2.5s infinite;
  margin-top: -20px;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.5;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
}

.ekg-line {
  width: 100%;
  max-width: 500px;
  height: 100px;
  margin-top: 20px;
  margin-left: 150px;
}

</style>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
</script>