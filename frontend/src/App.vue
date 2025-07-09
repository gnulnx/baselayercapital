<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <!-- <nav>
    <RouterLink to="/">Home</RouterLink>
    <RouterLink to="/about">About</RouterLink>
  </nav> -->

  <RouterView />
</template>

<style scoped>
nav {
  width: 100%;
  font-size: 14px;
  text-align: center;
  margin: 1rem 0;
}

nav a.router-link-exact-active {
  color: var(--color-text);
  font-weight: bold;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
  text-decoration: none;
}

nav a:first-of-type {
  border: 0;
}
</style>
