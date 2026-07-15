<template>
  <div class="flex min-h-screen bg-background">
    <!-- Sidebar -->
    <aside class="w-[240px] bg-card border-r border-border flex flex-col fixed top-0 left-0 bottom-0 z-100">
      <div class="h-16 px-5 flex items-center gap-3 border-b border-border">
        <div class="w-9 h-9 bg-primary rounded-lg flex items-center justify-center text-primary-foreground">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-5 h-5">
            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
            <polyline points="13 2 13 9 20 9"></polyline>
          </svg>
        </div>
        <span class="text-lg font-semibold text-foreground">FileRunner</span>
      </div>

      <nav class="flex-1 p-4 flex flex-col gap-1">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-muted-foreground no-underline text-sm font-medium transition-all duration-150 hover:bg-muted hover:text-foreground"
          :class="{ 'bg-primary/10 text-primary': isActive(item.path) }"
        >
          <span class="w-5 h-5 flex items-center justify-center" v-html="item.icon"></span>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="p-3 border-t border-border flex flex-col gap-1">
        <router-link to="/" class="flex items-center gap-2.5 w-full px-3.5 py-2.5 border-none rounded-lg bg-transparent text-muted-foreground text-sm font-medium cursor-pointer no-underline transition-all duration-150 hover:bg-muted hover:text-foreground">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-[18px] h-[18px]">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
          </svg>
          <span>返回前台</span>
        </router-link>
        <button class="flex items-center gap-2.5 w-full px-3.5 py-2.5 border-none rounded-lg bg-transparent text-muted-foreground text-sm font-medium cursor-pointer transition-all duration-150 hover:bg-destructive/10 hover:text-destructive" @click="logout">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-[18px] h-[18px]">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
          <span>退出登录</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 ml-[240px] flex flex-col min-h-screen">
      <header class="h-16 px-8 flex items-center justify-between bg-card border-b border-border sticky top-0 z-50">
        <div class="text-base font-semibold text-foreground">{{ currentPageTitle }}</div>
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-muted rounded-full flex items-center justify-center text-[13px] font-semibold text-foreground">管</div>
        </div>
      </header>

      <main class="flex-1 p-6 px-8 max-w-[calc(1200px-240px)] mx-auto w-full animate-[fade-in_0.2s_ease-out]">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const menuItems = [
  { path: '/admin/dashboard', label: '仪表盘', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="7" height="7" rx="1"></rect><rect x="14" y="3" width="7" height="7" rx="1"></rect><rect x="14" y="14" width="7" height="7" rx="1"></rect><rect x="3" y="14" width="7" height="7" rx="1"></rect></svg>' },
  { path: '/admin/settings', label: '全局设置', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>' },
  { path: '/admin/files', label: '分享管理', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>' },
  { path: '/admin/logs', label: '存取日志', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>' },
]

const currentPageTitle = computed(() => {
  const item = menuItems.find((i) => isActive(i.path))
  return item?.label || '管理后台'
})

function isActive(path: string) {
  if (path === '/admin/files') return route.path.startsWith('/admin/files')
  return route.path === path
}

function logout() {
  localStorage.removeItem('admin_token')
  router.push('/admin/login')
}
</script>
