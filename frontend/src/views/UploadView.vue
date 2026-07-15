<template>
  <div class="min-h-screen flex flex-col bg-background">
    <!-- Main content area -->
    <div class="flex-1 flex items-center justify-center py-10 px-5">
    <div class="grid grid-cols-1 md:grid-cols-[auto_1fr] w-full md:w-fit overflow-hidden rounded-xl shadow-lg border border-border">
      <!-- Showcase Carousel -->
      <div
        v-if="showcases.length > 0"
        class="w-full aspect-[5/3] bg-muted relative overflow-hidden md:aspect-[1/1]"
      >
          <!-- Loading placeholder -->
          <div v-if="!initialLoaded" class="absolute inset-0 flex items-center justify-center bg-muted z-10">
            <div class="animate-spin rounded-full border-2 border-muted-foreground/20 border-t-primary w-8 h-8"></div>
          </div>
          <!-- Image with fade transition -->
          <img
            :key="showcases[currentShowcaseIndex]?.id"
            :src="showcases[currentShowcaseIndex]?.image_url"
            alt="Showcase"
            class="absolute inset-0 w-full h-full object-cover transition-opacity duration-500"
            :class="initialLoaded ? 'opacity-100' : 'opacity-0'"
            @load="onImageLoad"
          />
          <!-- Carousel dots -->
          <div v-if="showcases.length > 1" class="absolute bottom-2 left-0 right-0 flex justify-center gap-1.5 z-20">
            <button
              v-for="(s, i) in showcases"
              :key="s.id"
              class="w-2 h-2 rounded-full border-none cursor-pointer transition-all duration-300"
              :class="i === currentShowcaseIndex ? 'bg-white' : 'bg-white/40'"
              @click="currentShowcaseIndex = i"
            />
          </div>
        </div>

      <!-- Main Card -->
      <div class="flex-1 min-w-0 md:min-w-[360px] md:max-w-[400px] bg-card p-10">
      <!-- Header -->
      <div class="flex items-center gap-4 mb-8">
        <div class="w-12 h-12 rounded-lg flex items-center justify-center text-primary-foreground bg-primary shrink-0">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
            <polyline points="13 2 13 9 20 9"></polyline>
          </svg>
        </div>
        <div>
          <h1 class="text-xl font-bold m-0 text-foreground leading-tight">文件快跑</h1>
          <p class="text-sm m-0 text-muted-foreground">匿名文件分享，安全快捷</p>
        </div>
      </div>

      <!-- Upload Form -->
      <div v-show="!showPickup">
        <!-- Dropzone -->
        <div
          class="border-2 border-dashed border-border rounded-lg cursor-pointer transition-all duration-200 mb-5"
          :class="selectedFiles.length > 0 ? 'border-solid p-3 cursor-default min-h-0' : 'p-8 min-h-[180px] flex items-center justify-center'"
          :style="isDragging ? 'border-color: var(--color-primary); background: rgba(43,90,220,0.02)' : ''"
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <input
            ref="fileInput"
            type="file"
            class="hidden"
            multiple
            @change="handleFileChange"
          />
          <!-- Empty state: centered -->
          <div v-if="selectedFiles.length === 0" class="text-center">
            <svg class="w-10 h-10 mb-3 mx-auto text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <p class="text-sm mb-2 text-foreground">拖拽文件或文件夹到此处</p>
            <p class="text-[13px] m-0 text-muted-foreground">支持多文件上传，最大 {{ maxsizeLabel }}</p>
          </div>
          <!-- Files selected: compact layout -->
          <div v-else class="w-full">
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4 flex-shrink-0 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
              <span class="text-xs font-medium text-foreground">{{ selectedFiles.length }} 个文件已选择</span>
              <button class="ml-auto flex items-center gap-1 px-2 py-0.5 border-none rounded text-xs cursor-pointer transition-all duration-150 hover:bg-destructive/10 hover:text-destructive bg-transparent text-muted-foreground" @click.stop="clearFiles">
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
                全部清除
              </button>
            </div>
            <p class="text-[11px] text-muted-foreground mt-1 text-left">可点击此处或继续拖拽文件至此处上传</p>
          </div>
        </div>

        <!-- File List (outside dropzone) -->
        <div v-if="selectedFiles.length > 0" class="relative mb-4 rounded-lg border border-border overflow-hidden" style="height: 180px;">
          <div ref="fileListRef" class="h-full overflow-y-auto" @scroll="checkScroll">
            <div v-for="(file, idx) in selectedFiles" :key="idx" class="flex items-center gap-2 py-2 px-3 border-b border-border last:border-b-0 hover:bg-muted/50 transition-colors">
              <svg v-if="file.relativePath && file.relativePath.includes('/')" class="w-4 h-4 flex-shrink-0 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
              </svg>
              <svg v-else class="w-4 h-4 flex-shrink-0 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
              </svg>
              <span class="flex-1 min-w-0 text-[13px] text-foreground truncate" :title="file.name">{{ file.name }}</span>
              <span class="text-[11px] text-muted-foreground flex-shrink-0">{{ formatFileSize(file.size) }}</span>
              <button class="w-5 h-5 flex items-center justify-center border-none rounded bg-transparent text-muted-foreground cursor-pointer hover:bg-destructive/10 hover:text-destructive flex-shrink-0" @click.stop="removeFile(idx)">
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          </div>
          <!-- Gradient mask - inside overflow:hidden, so it won't cover border -->
          <div v-show="!scrolledToBottom" class="absolute bottom-0 left-0 right-0 h-6 bg-gradient-to-t from-card via-card/80 to-transparent pointer-events-none"></div>
        </div>

        <!-- Options -->
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium mb-1.5 text-foreground">有效期</label>
            <Select v-model="selectedExpiry">
              <SelectTrigger class="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="opt in expiryOptions" :key="opt.value" :value="String(opt.value)">
                  {{ opt.label }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1.5 text-foreground">可下载次数</label>
            <Select v-model="selectedDownloadLimit">
              <SelectTrigger class="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="opt in downloadLimitOptions" :key="opt.value" :value="String(opt.value)">
                  {{ opt.label }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <button
          class="w-full py-3 px-5 rounded-md text-sm font-semibold cursor-pointer transition-all duration-200 inline-flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed bg-primary text-primary-foreground"
          :disabled="selectedFiles.length === 0 || uploading"
          @click="doUpload"
        >
          <svg
            v-if="uploading"
            class="w-[18px] h-[18px] flex-shrink-0 animate-spin"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
            <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-linecap="round"></path>
          </svg>
          {{ uploading ? '发送中...' : '发送' }}
        </button>

        <!-- Separator -->
        <div v-show="selectedFiles.length === 0" class="relative my-4">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-border"></div>
          </div>
          <div class="relative flex justify-center text-xs uppercase">
            <span class="bg-card px-2 text-muted-foreground">或</span>
          </div>
        </div>

        <!-- Pickup Button -->
        <button
          v-show="selectedFiles.length === 0"
          class="w-full py-3 px-5 rounded-md text-sm font-semibold cursor-pointer transition-all duration-200 inline-flex items-center justify-center gap-2 border border-border bg-secondary text-secondary-foreground hover:bg-secondary/80"
          @click="showPickup = true"
        >
          <svg class="w-[18px] h-[18px] animate-bounce-down" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          取件
        </button>
      </div>

      <!-- Pickup OTP Section -->
      <div v-show="showPickup" class="text-center py-4 flex flex-col items-center justify-center">
        <h2 class="text-lg font-semibold mb-2 text-foreground">输入取件码</h2>
        <p class="text-sm mb-6 m-0 text-muted-foreground">请输入6位数字取件码以下载文件</p>
        <div class="flex justify-center mb-6">
          <InputOTP v-model="pickupCode" :maxlength="6" auto-focus>
            <InputOTPGroup>
              <InputOTPSlot :index="0" class="w-12 h-14 text-xl font-mono" />
              <InputOTPSlot :index="1" class="w-12 h-14 text-xl font-mono" />
              <InputOTPSlot :index="2" class="w-12 h-14 text-xl font-mono" />
              <InputOTPSlot :index="3" class="w-12 h-14 text-xl font-mono" />
              <InputOTPSlot :index="4" class="w-12 h-14 text-xl font-mono" />
              <InputOTPSlot :index="5" class="w-12 h-14 text-xl font-mono" />
            </InputOTPGroup>
          </InputOTP>
        </div>
        <button
          class="py-2.5 px-5 rounded-md text-sm font-semibold cursor-pointer transition-all duration-200 border border-border bg-secondary text-secondary-foreground hover:bg-secondary/80"
          @click="showPickup = false; pickupCode = ''"
        >
          返回
        </button>
      </div>
    </div>
    </div>
    </div>

    <!-- Footer -->
    <footer class="py-4 text-center text-xs text-muted-foreground border-t border-border">
      &copy; 2024 FileRunner. All rights reserved.
    </footer>
  </div>

  <!-- Rejected Files Dialog -->
  <Dialog v-model:open="showRejectedDialog">
    <DialogContent class="sm:max-w-[420px]">
      <DialogHeader>
        <DialogTitle>部分文件未添加</DialogTitle>
      </DialogHeader>
      <div class="max-h-[200px] overflow-y-auto">
        <div v-for="(item, i) in rejectedFiles" :key="i" class="flex items-start gap-3 py-2 border-b border-border last:border-b-0">
          <svg class="w-4 h-4 flex-shrink-0 mt-0.5 text-destructive" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
          <div class="flex-1 min-w-0">
            <div class="text-sm text-foreground truncate">{{ item.name }}</div>
            <div class="text-xs text-muted-foreground">{{ item.reason }}</div>
          </div>
        </div>
      </div>
      <DialogFooter>
        <Button @click="showRejectedDialog = false">我知道了</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>

  <!-- Result Dialog -->
  <Dialog v-model:open="showResultDialog">
    <DialogContent class="sm:max-w-[380px]">
      <DialogHeader>
        <DialogTitle>上传成功</DialogTitle>
      </DialogHeader>
      <div class="text-center py-4">
        <p class="text-sm text-muted-foreground mb-2">取件码</p>
        <div class="text-[28px] font-bold text-primary tracking-widest">{{ uploadResult?.code }}</div>
      </div>
      <DialogFooter class="gap-2">
        <Button variant="outline" @click="showResultDialog = false">关闭</Button>
        <Button @click="copyUrl">复制链接</Button>
        <Button variant="secondary" @click="copyCode">复制取件码</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import api from '../api'
import { formatFileSize } from '../utils/format'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { InputOTP, InputOTPGroup, InputOTPSlot } from '@/components/ui/input-otp'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

const router = useRouter()

interface FileWithMeta extends File {
  relativePath?: string
}

const fileInput = ref<HTMLInputElement>()
const selectedFiles = ref<FileWithMeta[]>([])
const isDragging = ref(false)
const selectedExpiry = ref<string>('')
const selectedDownloadLimit = ref<string>('')
const uploading = ref(false)
const uploadResult = ref<{ code: string; url: string; is_group: boolean; file_count: number } | null>(null)
const showResultDialog = ref(false)
const fileListRef = ref<HTMLDivElement>()
const scrolledToBottom = ref(false)
const rejectedFiles = ref<{ name: string; reason: string }[]>([])
const showRejectedDialog = ref(false)

const showPickup = ref(false)
const pickupCode = ref('')

const expiryOptions = ref<{ value: number; label: string }[]>([])
const downloadLimitOptions = ref<{ value: number; label: string }[]>([])
const allowedExtensions = ref<string[]>([])
const controlMode = ref<string>('whitelist')
const blockedExtensions = ref<string[]>([])
const maxUploadSize = ref(0)
const maxFilesPerTask = ref(100)
const maxTaskSizeBytes = ref(5368709120)

const showcases = ref<{id: number; name: string; image_url: string}[]>([])
const currentShowcaseIndex = ref(0)
const initialLoaded = ref(false)
let showcaseTimer: ReturnType<typeof setInterval> | null = null

function onImageLoad() {
  initialLoaded.value = true
}

const maxsizeLabel = computed(() => formatFileSize(maxUploadSize.value))
const fullUrl = computed(() => uploadResult.value ? `${window.location.origin}${uploadResult.value.url}` : '')
const displayFiles = computed(() => selectedFiles.value.slice(0, 5))

watch(pickupCode, (val) => {
  if (val.length === 6) {
    router.push(`/get/${val}`)
  }
})

watch(showResultDialog, (val) => {
  if (!val && uploadResult.value) {
    selectedFiles.value = []
    uploadResult.value = null
    if (fileInput.value) fileInput.value.value = ''
  }
})

onMounted(async () => {
  try {
    const res = await api.get('/options')
    expiryOptions.value = res.data.expiry_options
    downloadLimitOptions.value = res.data.download_limit_options
    allowedExtensions.value = res.data.allowed_extensions
    controlMode.value = res.data.control_mode || 'whitelist'
    blockedExtensions.value = res.data.blocked_extensions || []
    maxUploadSize.value = res.data.max_size_bytes
    maxFilesPerTask.value = res.data.max_files_per_task || 100
    maxTaskSizeBytes.value = res.data.max_task_size_bytes || 5368709120
    // Default to the admin-configured default option
    const expiryDefaultIdx = res.data.expiry_default_index ?? 0
    const dlDefaultIdx = res.data.dl_default_index ?? 0
    if (expiryOptions.value.length > 0) {
      selectedExpiry.value = String(expiryOptions.value[expiryDefaultIdx]?.value ?? expiryOptions.value[0].value)
    }
    if (downloadLimitOptions.value.length > 0) {
      selectedDownloadLimit.value = String(downloadLimitOptions.value[dlDefaultIdx]?.value ?? downloadLimitOptions.value[0].value)
    }
    if (res.data.showcases && res.data.showcases.length > 0) {
      showcases.value = res.data.showcases
      showcaseTimer = setInterval(() => {
        currentShowcaseIndex.value = (currentShowcaseIndex.value + 1) % showcases.value.length
      }, 5000)
    }
  } catch { toast.error('加载配置失败') }
})

onUnmounted(() => {
  if (showcaseTimer) clearInterval(showcaseTimer)
})

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files) {
    addFiles(Array.from(input.files))
  }
}

function handleDrop(e: DragEvent) {
  isDragging.value = false
  const items = e.dataTransfer?.items
  if (items) {
    const files: FileWithMeta[] = []
    const promises: Promise<void>[] = []

    for (let i = 0; i < items.length; i++) {
      const item = items[i].webkitGetAsEntry?.()
      if (item) {
        promises.push(traverseEntry(item, '', files))
      }
    }

    Promise.all(promises).then(() => {
      if (files.length > 0) addFiles(files)
    })
  } else if (e.dataTransfer?.files) {
    addFiles(Array.from(e.dataTransfer.files))
  }
}

function traverseEntry(entry: FileSystemEntry, path: string, files: FileWithMeta[]): Promise<void> {
  return new Promise((resolve) => {
    if (entry.isFile) {
      (entry as FileSystemFileEntry).file((file) => {
        const f = file as FileWithMeta
        f.relativePath = path ? `${path}/${file.name}` : file.name
        files.push(f)
        resolve()
      })
    } else if (entry.isDirectory) {
      const dir = entry as FileSystemDirectoryEntry
      const reader = dir.createReader()
      const readEntries = () => {
        reader.readEntries(async (entries) => {
          if (entries.length === 0) {
            resolve()
          } else {
            const subPath = path ? `${path}/${entry.name}` : entry.name
            await Promise.all(entries.map((e) => traverseEntry(e, subPath, files)))
            readEntries()
          }
        })
      }
      readEntries()
    } else {
      resolve()
    }
  })
}

function addFiles(newFiles: FileWithMeta[]) {
  const rejected: { name: string; reason: string }[] = []
  for (const file of newFiles) {
    const ext = file.name.split('.').pop()?.toLowerCase() || ''
    if (controlMode.value === 'whitelist' && allowedExtensions.value.length > 0 && !allowedExtensions.value.includes(ext)) {
      rejected.push({ name: file.name, reason: `不支持的文件类型: .${ext}` })
      continue
    }
    if (controlMode.value === 'blacklist' && blockedExtensions.value.includes(ext)) {
      rejected.push({ name: file.name, reason: `禁止上传的文件类型: .${ext}` })
      continue
    }
    if (maxUploadSize.value && file.size > maxUploadSize.value) {
      rejected.push({ name: file.name, reason: `超过大小限制 (${formatFileSize(maxUploadSize.value)})` })
      continue
    }
    selectedFiles.value.push(file)
  }
  // Check total file count
  if (selectedFiles.value.length > maxFilesPerTask.value) {
    rejected.unshift({ name: '', reason: `最多上传 ${maxFilesPerTask.value} 个文件` })
  }
  // Check total task size
  const totalSize = selectedFiles.value.reduce((sum, f) => sum + f.size, 0)
  if (totalSize > maxTaskSizeBytes.value) {
    rejected.unshift({ name: '', reason: `总大小超过限制 (${formatFileSize(maxTaskSizeBytes.value)})` })
  }
  if (rejected.length > 0) {
    rejectedFiles.value = rejected
    showRejectedDialog.value = true
  }
}

function clearFiles() {
  selectedFiles.value = []
  if (fileInput.value) fileInput.value.value = ''
}

function removeFile(idx: number) {
  selectedFiles.value.splice(idx, 1)
  if (selectedFiles.value.length === 0 && fileInput.value) fileInput.value.value = ''
  scrolledToBottom.value = false
}

function checkScroll() {
  if (!fileListRef.value) return
  const el = fileListRef.value
  scrolledToBottom.value = el.scrollTop + el.clientHeight >= el.scrollHeight - 2
}

async function doUpload() {
  if (selectedFiles.value.length === 0) return

  uploading.value = true
  try {
    const formData = new FormData()

    for (const file of selectedFiles.value) {
      formData.append('files', file)
    }

    const paths = selectedFiles.value.map((f) => f.relativePath || f.name)
    formData.append('relative_paths', JSON.stringify(paths))

    formData.append('expiry', selectedExpiry.value)
    formData.append('download_limit', selectedDownloadLimit.value)

    const res = await api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    uploadResult.value = res.data
    showResultDialog.value = true
    toast.success('上传成功！')
  } catch (err: any) {
    toast.error(err.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

async function copyToClipboard(text: string) {
  // Method 1: Modern Clipboard API (requires HTTPS or localhost)
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text)
      return
    } catch {
      // Fall through to fallback
    }
  }
  // Method 2: textarea + execCommand fallback (works on HTTP)
  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.style.position = 'fixed'
  textarea.style.left = '-9999px'
  textarea.style.top = '-9999px'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.focus()
  textarea.select()
  textarea.setSelectionRange(0, textarea.value.length)
  const ok = document.execCommand('copy')
  document.body.removeChild(textarea)
  if (!ok) throw new Error('copy failed')
}

function copyUrl() {
  copyToClipboard(fullUrl.value)
    .then(() => toast.success('链接已复制'))
    .catch(() => toast.error('复制失败，请手动复制'))
}

function copyCode() {
  if (!uploadResult.value) return
  copyToClipboard(uploadResult.value.code)
    .then(() => toast.success('取件码已复制'))
    .catch(() => toast.error('复制失败，请手动复制'))
}
</script>

<style scoped>
@keyframes bounce-down {
  0% { transform: translateY(0); }
  15% { transform: translateY(6px); }
  30% { transform: translateY(0); }
  45% { transform: translateY(6px); }
  60% { transform: translateY(0); }
  75% { transform: translateY(0); }
  100% { transform: translateY(0); }
}

.animate-bounce-down {
  animation: bounce-down 2.5s ease-in-out infinite;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
