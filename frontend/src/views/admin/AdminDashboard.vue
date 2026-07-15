<template>
  <div class="max-w-[var(--page-max-width)]">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div v-for="card in cards" :key="card.title" class="bg-card border border-border rounded-lg p-5 flex items-center gap-4 transition-all duration-200 hover:shadow-md">
        <div class="w-12 h-12 rounded-md flex items-center justify-center bg-primary/10 text-primary shrink-0">
          <span v-html="card.icon" class="w-6 h-6"></span>
        </div>
        <div class="flex-1">
          <div class="text-2xl font-bold text-primary leading-none">{{ card.value }}</div>
          <div class="text-[13px] text-muted-foreground mt-1">{{ card.title }}</div>
        </div>
      </div>
    </div>

    <div>
      <h3 class="text-base font-semibold text-primary mb-4">快捷操作</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <router-link to="/admin/files" class="flex items-center gap-4 p-5 bg-card border border-border rounded-lg no-underline transition-all duration-200 hover:shadow-md hover:border-muted-foreground/30">
          <div class="w-11 h-11 rounded-md flex items-center justify-center shrink-0 bg-primary/10 text-primary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-5 h-5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
          </div>
          <div class="flex-1 flex flex-col gap-0.5">
            <span class="text-sm font-semibold text-primary">文件管理</span>
            <span class="text-[13px] text-muted-foreground">查看和管理所有文件</span>
          </div>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-[18px] h-[18px] text-muted-foreground shrink-0">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </router-link>

        <router-link to="/admin/logs" class="flex items-center gap-4 p-5 bg-card border border-border rounded-lg no-underline transition-all duration-200 hover:shadow-md hover:border-muted-foreground/30">
          <div class="w-11 h-11 rounded-md flex items-center justify-center shrink-0 bg-primary/10 text-primary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-5 h-5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
            </svg>
          </div>
          <div class="flex-1 flex flex-col gap-0.5">
            <span class="text-sm font-semibold text-primary">访问日志</span>
            <span class="text-[13px] text-muted-foreground">查看下载记录</span>
          </div>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-[18px] h-[18px] text-muted-foreground shrink-0">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </router-link>

        <router-link to="/admin/settings" class="flex items-center gap-4 p-5 bg-card border border-border rounded-lg no-underline transition-all duration-200 hover:shadow-md hover:border-muted-foreground/30">
          <div class="w-11 h-11 rounded-md flex items-center justify-center shrink-0 bg-primary/10 text-primary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-5 h-5">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
          </div>
          <div class="flex-1 flex flex-col gap-0.5">
            <span class="text-sm font-semibold text-primary">系统设置</span>
            <span class="text-[13px] text-muted-foreground">配置系统参数</span>
          </div>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-[18px] h-[18px] text-muted-foreground shrink-0">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { toast } from 'vue-sonner'
import api from '../../api'
import { formatFileSize } from '../../utils/format'

const cards = ref([
  {
    title: '总文件数',
    value: '0',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>',
  },
  {
    title: '总传输量',
    value: '0 B',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>',
  },
  {
    title: '生效分享',
    value: '0',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
  },
])

onMounted(async () => {
  try {
    const res = await api.get('/admin/stats')
    const d = res.data
    cards.value[0].value = d.total_files
    cards.value[1].value = formatFileSize(d.total_transfer_bytes)
    cards.value[2].value = d.active_shares
  } catch {
    toast.error('加载统计数据失败')
  }
})
</script>
