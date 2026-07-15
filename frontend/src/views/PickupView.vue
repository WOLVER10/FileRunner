<template>
  <div class="min-h-screen flex flex-col bg-background">
    <div class="flex-1 flex items-center justify-center p-10">
    <div class="w-full max-w-md bg-card border border-border rounded-xl p-10 shadow-lg">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="w-10 h-10 border-3 border-border rounded-full border-t-primary animate-spin mx-auto mb-4"></div>
        <p class="text-foreground">加载中...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-center py-5">
        <div class="w-16 h-16 rounded-full inline-flex items-center justify-center mb-4 bg-destructive/10 text-destructive">
          <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-foreground mb-2">{{ error }}</h2>
        <router-link to="/" class="inline-flex items-center gap-1.5 text-primary no-underline text-sm font-medium hover:underline">返回首页</router-link>
      </div>

      <!-- Cleaned -->
      <div v-else-if="fileInfo?.status === 'cleaned'" class="text-center py-5">
        <div class="w-16 h-16 rounded-full inline-flex items-center justify-center mb-4 bg-yellow-100 text-yellow-600">
          <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-foreground mb-2">文件已被清理</h2>
        <p class="text-sm text-muted-foreground mb-4">该文件已被管理员清理，无法下载</p>
        <router-link to="/" class="inline-flex items-center gap-1.5 text-primary no-underline text-sm font-medium hover:underline">返回首页</router-link>
      </div>

      <!-- Single File -->
      <div v-else-if="fileInfo && !fileInfo.is_group">
        <div class="text-center mb-6">
          <div class="w-14 h-14 bg-primary/10 rounded-xl inline-flex items-center justify-center text-primary mb-4">
            <svg class="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
              <polyline points="13 2 13 9 20 9"></polyline>
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-foreground mb-1">文件取件</h1>
          <p class="text-sm text-muted-foreground break-all">{{ fileInfo.filename }}</p>
        </div>

        <div class="mb-6">
          <div class="flex justify-between items-center py-3.5 border-b border-border">
            <span class="text-sm text-muted-foreground">文件数量</span>
            <span class="text-sm font-medium text-foreground">1 个</span>
          </div>
          <div class="flex justify-between items-center py-3.5 border-b border-border">
            <span class="text-sm text-muted-foreground">文件大小</span>
            <span class="text-sm font-medium text-foreground">{{ formatFileSize(fileInfo.size || 0) }}</span>
          </div>
          <div class="flex justify-between items-center py-3.5 border-b border-border">
            <span class="text-sm text-muted-foreground">剩余下载</span>
            <span class="text-sm font-medium" :class="{ 'text-destructive': fileInfo.remaining_downloads === 0, 'text-primary': fileInfo.remaining_downloads === -1 }">
              {{ fileInfo.remaining_downloads === -1 ? '无限次' : fileInfo.remaining_downloads + ' 次' }}
            </span>
          </div>
          <div class="flex justify-between items-center py-3.5">
            <span class="text-sm text-muted-foreground">过期时间</span>
            <span class="text-sm font-medium text-foreground">{{ formatRelativeTime(fileInfo.expires_at) }}</span>
          </div>
        </div>

        <button
          v-if="fileInfo.remaining_downloads === 0"
          class="w-full py-3 px-6 rounded-lg text-[15px] font-semibold cursor-not-allowed opacity-50 bg-muted text-muted-foreground"
          disabled
        >
          已失效
        </button>
        <button
          v-else
          class="w-full py-3 px-6 bg-primary text-primary-foreground rounded-lg text-[15px] font-semibold hover:bg-primary/90 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2"
          :disabled="downloading"
          @click="downloadSingle"
        >
          <span v-if="downloading" class="w-4 h-4 border-2 border-primary-foreground/30 rounded-full border-t-primary-foreground animate-spin"></span>
          {{ downloading ? '下载中...' : '下载文件' }}
        </button>
      </div>

      <!-- File Group -->
      <div v-else-if="fileInfo && fileInfo.is_group">
        <div class="text-center mb-6">
          <div class="w-14 h-14 bg-primary/10 rounded-xl inline-flex items-center justify-center text-primary mb-4">
            <svg class="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-foreground mb-1">文件取件</h1>
        </div>

        <div class="mb-6">
          <div class="flex justify-between items-center py-3.5 border-b border-border">
            <span class="text-sm text-muted-foreground">分享类型</span>
            <span class="text-sm font-medium text-foreground">{{ fileInfo.share_type === 'folder' ? '文件夹' : fileInfo.share_type === 'multi' ? '多文件' : '单文件' }}</span>
          </div>

          <div class="flex justify-between items-center py-3.5 border-b border-border">
            <span class="text-sm text-muted-foreground">文件数量</span>
            <span class="text-sm font-medium text-foreground">{{ fileInfo.file_count }} 个</span>
          </div>
          <div class="flex justify-between items-center py-3.5 border-b border-border">
            <span class="text-sm text-muted-foreground">文件大小</span>
            <span class="text-sm font-medium text-foreground">{{ formatFileSize(fileInfo.total_size || 0) }}</span>
          </div>
          <div class="flex justify-between items-center py-3.5 border-b border-border">
            <span class="text-sm text-muted-foreground">剩余下载</span>
            <span class="text-sm font-medium" :class="{ 'text-destructive': fileInfo.remaining_downloads === 0, 'text-primary': fileInfo.remaining_downloads === -1 }">
              {{ fileInfo.remaining_downloads === -1 ? '无限次' : fileInfo.remaining_downloads + ' 次' }}
            </span>
          </div>
          <div class="flex justify-between items-center py-3.5">
            <span class="text-sm text-muted-foreground">过期时间</span>
            <span class="text-sm font-medium text-foreground">{{ formatRelativeTime(fileInfo.expires_at) }}</span>
          </div>
        </div>

        <button
          v-if="fileInfo.remaining_downloads === 0"
          class="w-full py-3 px-6 rounded-lg text-[15px] font-semibold cursor-not-allowed opacity-50 bg-muted text-muted-foreground"
          disabled
        >
          已失效
        </button>
        <button
          v-else
          class="w-full py-3 px-6 bg-primary text-primary-foreground rounded-lg text-[15px] font-semibold hover:bg-primary/90 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2"
          :disabled="downloading"
          @click="downloadAll"
        >
          <span v-if="downloading" class="w-4 h-4 border-2 border-primary-foreground/30 rounded-full border-t-primary-foreground animate-spin"></span>
          {{ downloading ? '下载中...' : '全部下载 (ZIP)' }}
        </button>
        <button
          v-if="fileInfo.remaining_downloads !== 0"
          class="w-full mt-3 py-2.5 px-5 rounded-lg text-sm font-medium border border-border bg-transparent text-muted-foreground hover:bg-muted transition-all duration-200"
          @click="showFileListDialog = true"
        >
          查看分享内容
        </button>
      </div>
    </div>
    </div>

    <!-- Link to send files -->
    <div class="text-center pb-4">
      <router-link to="/" class="inline-flex items-center justify-center px-6 py-2.5 rounded-lg text-sm font-medium text-foreground bg-muted border border-border no-underline transition-all duration-200 hover:bg-accent">
        我也要发文件
      </router-link>
    </div>

    <!-- Footer -->
    <footer class="py-4 text-center text-xs text-muted-foreground border-t border-border">
      &copy; 2024 FileRunner. All rights reserved.
    </footer>
  </div>

  <!-- File List Dialog -->
  <Dialog v-model:open="showFileListDialog" @update:open="onDialogClose">
    <DialogContent class="sm:max-w-[520px] p-0">
      <DialogHeader class="px-5 pt-5 pb-3">
        <DialogTitle>文件列表 <span class="text-sm font-normal text-muted-foreground">（{{ currentFolderCount }} 个文件夹 {{ currentFileCount }} 个文件）</span></DialogTitle>
      </DialogHeader>

      <div class="flex flex-col max-h-[60vh] min-h-[280px]">
        <!-- Table header -->
        <div class="flex items-center px-5 py-2 border-y border-border text-xs text-muted-foreground">
          <span class="flex-1">名称</span>
          <span class="w-20 text-right">大小</span>
        </div>

        <!-- File list -->
        <div class="flex-1 overflow-y-auto">
        <!-- Back button (when inside a folder) -->
        <div
          v-if="currentPath.length > 0"
          class="flex items-center gap-2 py-2.5 px-5 border-b border-border cursor-pointer hover:bg-muted/50 transition-colors"
          @click="goBack"
        >
          <svg class="w-4 h-4 flex-shrink-0 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
          <span class="text-sm text-muted-foreground">返回上一级</span>
        </div>

        <!-- Folders -->
        <div
          v-for="folder in currentFolders"
          :key="'d-' + folder"
          class="flex items-center gap-2 py-2.5 px-5 border-b border-border cursor-pointer hover:bg-muted/50 transition-colors"
          @click="enterFolder(folder)"
        >
          <svg class="w-4 h-4 flex-shrink-0 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
          </svg>
          <span class="flex-1 min-w-0 text-sm text-foreground break-all line-clamp-2">{{ folder }}</span>
        </div>

        <!-- Files -->
        <div
          v-for="file in currentFiles"
          :key="'f-' + file.id"
          class="flex items-center gap-2 py-2.5 px-5 border-b border-border last:border-b-0 hover:bg-muted/50 transition-colors"
        >
          <svg class="w-4 h-4 flex-shrink-0 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          <span class="flex-1 min-w-0 text-sm text-foreground break-all line-clamp-2">{{ file.filename }}</span>
          <span class="w-20 text-right text-xs text-muted-foreground flex-shrink-0">{{ formatFileSize(file.size) }}</span>
        </div>

        <!-- Empty state -->
        <div v-if="currentFolders.length === 0 && currentFiles.length === 0" class="py-8 text-center text-sm text-muted-foreground">
          此目录为空
        </div>
        </div>

        <!-- Breadcrumb -->
        <div class="px-5 py-2.5 border-t border-border flex items-center gap-1 text-xs text-muted-foreground shrink-0">
          <span
            class="cursor-pointer hover:text-foreground transition-colors"
            @click="navigateToIndex(0)"
          >根目录</span>
          <template v-for="(seg, idx) in currentPath" :key="idx">
            <svg class="w-3 h-3 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
            <span
              class="cursor-pointer hover:text-foreground transition-colors"
              @click="navigateToIndex(idx + 1)"
            >{{ seg }}</span>
          </template>
        </div>
      </div>

      <div class="px-5 pb-4">
        <Button variant="outline" class="w-full" @click="showFileListDialog = false">关闭</Button>
      </div>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { toast } from 'vue-sonner'
import api from '../api'
import { formatFileSize, formatRelativeTime } from '../utils/format'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

interface GroupFile {
  id: number
  filename: string
  relative_path: string
  size: number
  mime_type: string
}

interface FileInfo {
  code: string
  filename?: string
  size?: number
  remaining_downloads: number
  expires_at: string
  status: string
  is_group: boolean
  share_type?: 'single' | 'multi' | 'folder'
  file_count: number
  total_size?: number
  name?: string
  files?: GroupFile[]
}

const route = useRoute()
const code = route.params.code as string

const loading = ref(true)
const downloading = ref(false)
const error = ref('')
const fileInfo = ref<FileInfo | null>(null)
const showFileListDialog = ref(false)
const currentPath = ref<string[]>([])

// Derive folders and files at the current navigation level
const currentFolders = computed(() => {
  if (!fileInfo.value?.files) return []
  const prefix = currentPath.value.length > 0 ? currentPath.value.join('/') + '/' : ''
  const folders = new Set<string>()
  for (const file of fileInfo.value.files) {
    const rel = file.relative_path || file.filename
    if (!rel.startsWith(prefix)) continue
    const rest = rel.slice(prefix.length)
    const slashIdx = rest.indexOf('/')
    if (slashIdx !== -1) {
      folders.add(rest.slice(0, slashIdx))
    }
  }
  return Array.from(folders).sort()
})

const currentFiles = computed(() => {
  if (!fileInfo.value?.files) return []
  const prefix = currentPath.value.length > 0 ? currentPath.value.join('/') + '/' : ''
  return fileInfo.value.files.filter(file => {
    const rel = file.relative_path || file.filename
    if (!rel.startsWith(prefix)) return false
    const rest = rel.slice(prefix.length)
    return !rest.includes('/')
  })
})

const currentFolderCount = computed(() => currentFolders.value.length)
const currentFileCount = computed(() => currentFiles.value.length)

function enterFolder(name: string) {
  currentPath.value.push(name)
}

function goBack() {
  currentPath.value.pop()
}

function navigateToIndex(idx: number) {
  currentPath.value = currentPath.value.slice(0, idx)
}

function onDialogClose() {
  currentPath.value = []
}

onMounted(async () => {
  try {
    const res = await api.get(`/file/${code}/info`)
    fileInfo.value = res.data
  } catch (err: any) {
    error.value = err.response?.status === 404 ? '取件码不存在' : '加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
})

function getGroupZipFilename(): string {
  const info = fileInfo.value
  if (!info) return 'download.zip'
  if (info.share_type === 'folder') {
    return `${info.name || info.code}.zip`
  }
  // multi type
  const firstName = info.files?.[0]?.filename || 'files'
  return `多文件-${firstName}等.zip`
}

async function downloadSingle() {
  downloading.value = true
  try {
    const res = await api.get(`/file/${code}/download`, { responseType: 'blob' })
    const isGroup = fileInfo.value?.is_group
    const filename = isGroup ? getGroupZipFilename() : (fileInfo.value?.filename || 'download')
    triggerDownload(res.data, filename)
    toast.success('下载开始')
    refreshInfo()
  } catch (err: any) {
    toast.error(err.response?.data?.detail || '下载失败')
  } finally {
    downloading.value = false
  }
}

async function downloadAll() {
  downloading.value = true

  try {
    const res = await api.get(`/file/${code}/download`, { responseType: 'blob' })
    triggerDownload(res.data, getGroupZipFilename())
    toast.success('下载开始')
    refreshInfo()
  } catch (err: any) {
    toast.error(err.response?.data?.detail || '下载失败')
  } finally {
    downloading.value = false
  }
}

function triggerDownload(data: Blob, filename: string | undefined) {
  const url = window.URL.createObjectURL(new Blob([data]))
  const a = document.createElement('a')
  a.href = url
  a.download = filename || 'download'
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

async function refreshInfo() {
  try {
    const res = await api.get(`/file/${code}/info`)
    fileInfo.value = res.data
  } catch {}
}
</script>
