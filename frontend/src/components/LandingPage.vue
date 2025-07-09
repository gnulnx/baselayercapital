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
        points="0,50 20,50 25,30 35,70 45,50 60,50 70,20 80,80 90,50 500,50"
      >
        <animate attributeName="points"
          dur="2s"
          repeatCount="indefinite"
          values="
            0,50 20,50 25,30 35,70 45,50 60,50 70,20 80,80 90,50 500,50;
            0,50 20,50 25,70 35,30 45,50 60,50 70,80 80,20 90,50 500,50;
            0,50 20,50 25,30 35,70 45,50 60,50 70,20 80,80 90,50 500,50
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
}
</style>
