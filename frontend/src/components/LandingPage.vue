<template>
  <div class="landing-container">
    <img src="@/assets/imgs/BaseLayerCapital.png" alt="Base Layer Capital Logo" class="logo" />
    <p class=" tagline">
        Volatility is Vitality
    </p>

    <!-- <p class="tagline">Volatility is Vitality</p> -->
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
</style>
