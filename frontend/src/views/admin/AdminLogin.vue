<template>
  <div class="relative min-h-screen flex items-center justify-center bg-primary overflow-hidden">
    <!-- Background orbs -->
    <div class="absolute inset-0 pointer-events-none">
      <div class="absolute w-[500px] h-[500px] rounded-full blur-[100px] opacity-40 bg-primary-foreground -top-[200px] -right-[100px]"></div>
      <div class="absolute w-[400px] h-[400px] rounded-full blur-[100px] opacity-20 bg-white -bottom-[150px] -left-[100px]"></div>
    </div>

    <!-- Login card -->
    <div class="relative z-10 w-full max-w-[400px] bg-card border border-border rounded-xl p-10 shadow-xl mx-5">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-14 h-14 bg-primary rounded-xl text-primary-foreground mb-4">
          <svg class="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
            <polyline points="13 2 13 9 20 9"></polyline>
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-foreground mb-2">FileRunner</h1>
        <p class="text-sm text-muted-foreground">管理员登录</p>
      </div>

      <!-- Form -->
      <form class="flex flex-col gap-5" @submit.prevent="handleLogin">
        <!-- Username -->
        <div class="flex flex-col gap-2">
          <Label class="text-sm font-medium text-foreground">用户名</Label>
          <div class="relative flex items-center">
            <svg class="absolute left-3 w-4 h-4 text-muted-foreground pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            <Input v-model="form.username" type="text" placeholder="请输入用户名" class="w-full py-3 pl-10 pr-3 text-sm text-foreground bg-background border border-border rounded-lg focus-visible:ring-ring focus-visible:ring-2 focus-visible:ring-offset-2 placeholder:text-muted-foreground" />
          </div>
        </div>

        <!-- Password -->
        <div class="flex flex-col gap-2">
          <Label class="text-sm font-medium text-foreground">密码</Label>
          <div class="relative flex items-center">
            <svg class="absolute left-3 w-4 h-4 text-muted-foreground pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <Input v-model="form.password" type="password" placeholder="请输入密码" class="w-full py-3 pl-10 pr-3 text-sm text-foreground bg-background border border-border rounded-lg focus-visible:ring-ring focus-visible:ring-2 focus-visible:ring-offset-2 placeholder:text-muted-foreground" />
          </div>
        </div>

        <!-- Submit -->
        <Button type="submit" :disabled="loading" class="w-full py-3 px-6 text-sm font-semibold text-primary-foreground bg-primary rounded-lg transition-all duration-200 hover:bg-primary/90 hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed">
          <span v-if="loading" class="inline-block w-4 h-4 border-2 border-primary-foreground/30 rounded-full border-t-primary-foreground animate-spin"></span>
          <span v-else>登 录</span>
        </Button>
      </form>

      <!-- Footer -->
      <div class="mt-6 text-center">
        <router-link to="/" class="inline-flex items-center gap-1.5 text-sm text-muted-foreground no-underline transition-colors duration-150 hover:text-primary">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          返回首页
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import api from '../../api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const router = useRouter()
const loading = ref(false)
const form = ref({ username: '', password: '' })

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    toast.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await api.post('/admin/login', form.value)
    localStorage.setItem('admin_token', res.data.access_token)
    toast.success('登录成功')
    router.push('/admin/dashboard')
  } catch (err: any) {
    toast.error(err.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>
