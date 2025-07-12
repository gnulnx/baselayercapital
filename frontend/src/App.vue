<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <nav>
    <RouterLink to="/">Home</RouterLink>
    <RouterLink to="/about">About</RouterLink>
    <RouterLink to="/login">Login</RouterLink>
  </nav>

  <RouterView />
</template>

<style lang="scss">
@use '@/assets/scss/variables.scss' as *;

* {
  box-sizing: border-box;
}
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
}

nav {
  position: fixed;
  height: $nav-total-offset;
  top: 0rem;
  padding-top: 0.75rem;
  left: 0px;
  right: 0px;
  display: flex;
  justify-content: center;
  z-index: 1000;
  // border: 1px solid green;
}

nav a.router-link-exact-active {
  color: darkorange;
  font-weight: bold;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
  text-decoration: none;
  color: var(--color-text);
}

nav a:first-of-type {
  border: 0;
}
</style>
