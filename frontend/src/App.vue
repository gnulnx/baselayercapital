<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <nav>
    <RouterLink to="/login">Login</RouterLink>
    <RouterLink to="/about">About</RouterLink>
    <RouterLink to="/">Home</RouterLink>
  </nav>

  <RouterView />
</template>

<style scoped lang="scss">
@use '@/assets/scss/variables.scss' as *;

nav {
  position: fixed;
  height: $nav-total-offset;
  top: 0rem;
  padding-top: 0.75rem;
  left: 0px;
  right: 0px;
  display: flex;
  justify-content: center;
  // border: 1px solid green;
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
