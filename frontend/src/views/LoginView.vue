<template>
  <div class="login">
    <h1>Login</h1>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="username">Username</label>
        <input v-model="username" type="text" id="username" required />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input v-model="password" type="password" id="password" required />
      </div>

      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const username = ref('')
const password = ref('')

const handleSubmit = () => {
  console.log('Logging in with:', {
    username: username.value,
    password: password.value,
  })

  // You can use fetch or axios here
  // Example:
  /*
  fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: username.value, password: password.value })
  }).then(...).catch(...)
  */
}
</script>

<style scoped>
.login {
  max-width: 400px;
  padding: 2rem;
  background-color: #1e1e1e;
  border-radius: 8px;
  color: white;

  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

input {
  padding: 0.5rem;
  border: 1px solid #555;
  border-radius: 4px;
  background-color: #2a2a2a;
  color: white;
}

button {
  padding: 0.75rem;
  background-color: orange;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

button:hover {
  background-color: darkorange;
}
</style>
