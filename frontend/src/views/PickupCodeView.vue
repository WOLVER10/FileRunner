<template>
  <div class="min-h-screen flex flex-col bg-background">
    <div class="flex-1 flex items-center justify-center p-10">
      <div class="w-full max-w-md bg-card border border-border rounded-xl p-10 shadow-lg text-center">
        <div class="w-14 h-14 bg-primary/10 rounded-xl inline-flex items-center justify-center text-primary mb-4">
          <svg class="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-foreground mb-2">文件取件</h1>
        <p class="text-sm text-muted-foreground mb-6">请输入 6 位数字取件码</p>

        <div class="flex justify-center mb-6">
          <InputOTP v-model="code" :maxlength="6" @complete="goToPickup">
            <InputOTPGroup>
              <InputOTPSlot v-for="i in 6" :key="i" :index="i - 1" class="w-11 h-12 text-lg" />
            </InputOTPGroup>
          </InputOTP>
        </div>

        <button
          class="w-full py-3 px-6 bg-primary text-primary-foreground rounded-lg text-[15px] font-semibold hover:bg-primary/90 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="code.length !== 6"
          @click="goToPickup"
        >
          取件
        </button>
      </div>
    </div>

    <div class="text-center pb-4">
      <router-link to="/" class="inline-flex items-center justify-center px-6 py-2.5 rounded-lg text-sm font-medium text-foreground bg-muted border border-border no-underline transition-all duration-200 hover:bg-accent">
        我也要发文件
      </router-link>
    </div>

    <footer class="py-4 text-center text-xs text-muted-foreground border-t border-border">
      &copy; {{ new Date().getFullYear() }} FileRunner. All rights reserved.
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { InputOTP, InputOTPGroup, InputOTPSlot } from '@/components/ui/input-otp'

const router = useRouter()
const code = ref('')

function goToPickup() {
  if (code.value.length === 6) {
    router.push(`/get/${code.value}`)
  }
}
</script>
