<template>
  <div class="login">
    <h1>{{ isSignup ? 'Sign Up' : 'Login' }}</h1>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="email">Email</label>
        <input v-model="email" type="email" id="email" required placeholder="...@email.com" />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input v-model="password" type="password" id="password" required placeholder="xxxxxx"/>
      </div>

      <div v-if="isSignup && awaitingConfirmation" class="form-group">
        <label for="code">Confirmation Code</label>
        <input v-model="confirmationCode" type="text" id="code" maxlength="6" required />
      </div>

      <button type="submit">
        {{ isSignup ? (awaitingConfirmation ? 'Confirm' : 'Sign Up') : 'Login' }}
      </button>
    </form>

    <div class="toggle">
      <span>
        {{ isSignup ? 'Already have an account?' : 'Need an account?' }}
      </span>
      <br>
      <button @click="toggleMode">
        {{ isSignup ? 'Login' : 'Sign Up' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isSignup = ref(false)
const awaitingConfirmation = ref(false)
const email = ref('')
const password = ref('')
const confirmationCode = ref('')

const handleSubmit = () => {
  if (isSignup.value) {
    if (awaitingConfirmation.value) {
      console.log('Confirming signup with code:', confirmationCode.value)
      // Call API to verify code
    } else {
      console.log('Signing up with:', { email: email.value, password: password.value })
      // Call API to create account
      awaitingConfirmation.value = true
    }
  } else {
    console.log('Logging in with:', { email: email.value, password: password.value })
    // Call API to login
  }
}

const toggleMode = () => {
  isSignup.value = !isSignup.value
  awaitingConfirmation.value = false
  email.value = ''
  password.value = ''
  confirmationCode.value = ''
}
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables.scss' as *;
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

  @media (min-width: $breakpoint-md) {
        padding: 0.25rem;
    }
}

button {
  padding: 0.5rem;
  background-color: orange;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
  width: 100%;
}

button:hover {
  background-color: darkorange;
}

.toggle {
  margin-top: 1rem;
  text-align: center;
}

.toggle span {
  margin-right: 0.5rem;
}
</style>
