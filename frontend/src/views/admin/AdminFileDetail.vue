<template>
  <div class="max-w-4xl mx-auto p-6">
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
    </div>

    <template v-else>
      <Button variant="outline" class="mb-6 gap-2" @click="router.back()">
        <ArrowLeft class="w-4 h-4" />
        返回文件管理
      </Button>

      <template v-if="detail">
        <h1 class="text-2xl font-bold text-foreground mb-6">分享详情</h1>

        <Card class="mb-4">
          <CardHeader class="pb-4">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <FileIcon class="w-6 h-6 text-primary" />
              </div>
              <div class="flex-1 min-w-0">
                <h2 class="text-xl font-semibold text-foreground truncate mb-2">
                  {{ detail.is_group ? detail.name : detail.original_filename }}
                </h2>
                <div class="flex gap-2 flex-wrap">
                  <Badge variant="secondary" class="rounded-full">{{ detail.code }}</Badge>
                  <Badge 
                    :variant="statusVariant(detail.status)" 
                    class="rounded-full"
                  >
                    {{ statusLabel(detail.status) }}
                  </Badge>
                  <Badge v-if="detail.is_group" variant="outline" class="rounded-full">
                    {{ detail.file_count }} 个文件
                  </Badge>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div class="space-y-1">
                <p class="text-sm text-muted-foreground">文件大小</p>
                <p class="text-sm font-medium">{{ formatFileSize(detail.file_size) }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-sm text-muted-foreground">MIME 类型</p>
                <p class="text-sm font-medium">{{ detail.mime_type }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-sm text-muted-foreground">上传 IP</p>
                <p class="text-sm font-medium font-mono">{{ detail.upload_ip }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-sm text-muted-foreground">上传时间</p>
                <p class="text-sm font-medium">{{ formatDateTime(detail.upload_time) }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-sm text-muted-foreground">过期时间</p>
                <p class="text-sm font-medium">{{ formatDateTime(detail.expires_at) }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-sm text-muted-foreground">下载限制</p>
                <p class="text-sm font-medium">{{ detail.download_limit === -1 ? '无限次' : detail.download_limit + ' 次' }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-sm text-muted-foreground">剩余次数</p>
                <p class="text-sm font-medium">{{ detail.remaining_downloads === -1 ? '无限' : detail.remaining_downloads }}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- File list for groups -->
        <Card v-if="detail.is_group && detail.files?.length" class="mb-4">
          <CardHeader class="pb-3">
            <CardTitle class="text-base">文件列表 <span class="text-sm font-normal text-muted-foreground">（{{ folderCount }} 个文件夹 {{ fileCount }} 个文件）</span></CardTitle>
          </CardHeader>
          <CardContent class="p-0">
            <div class="flex flex-col max-h-[60vh] min-h-[280px]">
              <!-- Table header -->
              <div class="flex items-center px-4 py-2 border-b border-border text-xs text-muted-foreground">
                <span class="flex-1">名称</span>
                <span class="w-20 text-right">大小</span>
              </div>

              <!-- File list -->
              <div class="flex-1 overflow-y-auto">
              <!-- Back button -->
              <div
                v-if="currentPath.length > 0"
                class="flex items-center gap-2 py-2.5 px-4 border-b border-border cursor-pointer hover:bg-muted/50 transition-colors"
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
                class="flex items-center gap-2 py-2.5 px-4 border-b border-border cursor-pointer hover:bg-muted/50 transition-colors"
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
                class="flex items-center gap-2 py-2.5 px-4 border-b border-border last:border-b-0 hover:bg-muted/50 transition-colors"
              >
                <svg class="w-4 h-4 flex-shrink-0 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <span class="flex-1 min-w-0 text-sm text-foreground break-all line-clamp-2">{{ file.filename }}</span>
                <span class="w-20 text-right text-xs text-muted-foreground flex-shrink-0">{{ formatFileSize(file.size) }}</span>
              </div>

              <!-- Empty -->
              <div v-if="currentFolders.length === 0 && currentFiles.length === 0" class="py-8 text-center text-sm text-muted-foreground">
                此目录为空
              </div>
              </div>

              <!-- Breadcrumb -->
              <div class="px-4 py-2.5 border-t border-border flex items-center gap-1 text-xs text-muted-foreground bg-muted/20 shrink-0">
                <span class="cursor-pointer hover:text-foreground transition-colors" @click="navigateToIndex(0)">根目录</span>
                <template v-for="(seg, idx) in currentPath" :key="idx">
                  <svg class="w-3 h-3 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"></polyline>
                  </svg>
                  <span class="cursor-pointer hover:text-foreground transition-colors" @click="navigateToIndex(idx + 1)">{{ seg }}</span>
                </template>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="pb-3">
            <div class="flex items-center justify-between">
              <CardTitle class="text-base">下载记录</CardTitle>
              <span class="text-sm text-muted-foreground">{{ detail.recent_downloads?.length || 0 }} 条</span>
            </div>
          </CardHeader>
          <CardContent class="p-0">
            <div v-if="detail.recent_downloads?.length">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>时间</TableHead>
                    <TableHead>IP 地址</TableHead>
                    <TableHead>User-Agent</TableHead>
                    <TableHead>结果</TableHead>
                    <TableHead>原因</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow v-for="(log, i) in detail.recent_downloads" :key="i">
                    <TableCell class="whitespace-nowrap">{{ formatDateTime(log.download_time) }}</TableCell>
                    <TableCell class="font-mono text-sm">{{ log.ip }}</TableCell>
                    <TableCell class="max-w-[300px]">
                      <span class="block truncate text-sm text-muted-foreground" :title="log.user_agent">{{ log.user_agent }}</span>
                    </TableCell>
                    <TableCell>
                      <Badge :variant="log.success ? 'default' : 'destructive'" class="rounded-full">
                        {{ log.success ? '成功' : '失败' }}
                      </Badge>
                    </TableCell>
                    <TableCell>{{ log.reason || '-' }}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
            <div v-else class="py-10 text-center text-muted-foreground text-sm">
              暂无下载记录
            </div>
          </CardContent>
        </Card>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import api from '../../api'
import { formatFileSize, formatDateTime } from '../../utils/format'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ArrowLeft } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const detail = ref<any>(null)
const currentPath = ref<string[]>([])

// Folder navigation
const currentFolders = computed(() => {
  if (!detail.value?.files) return []
  const prefix = currentPath.value.length > 0 ? currentPath.value.join('/') + '/' : ''
  const folders = new Set<string>()
  for (const file of detail.value.files) {
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
  if (!detail.value?.files) return []
  const prefix = currentPath.value.length > 0 ? currentPath.value.join('/') + '/' : ''
  return detail.value.files.filter((file: any) => {
    const rel = file.relative_path || file.filename
    if (!rel.startsWith(prefix)) return false
    const rest = rel.slice(prefix.length)
    return !rest.includes('/')
  })
})

const folderCount = computed(() => currentFolders.value.length)
const fileCount = computed(() => currentFiles.value.length)

function enterFolder(name: string) {
  currentPath.value.push(name)
}

function goBack() {
  currentPath.value.pop()
}

function navigateToIndex(idx: number) {
  currentPath.value = currentPath.value.slice(0, idx)
}

onMounted(async () => {
  try {
    const res = await api.get(`/admin/files/${route.params.id}`)
    detail.value = res.data
  } catch { toast.error('加载文件详情失败') }
  finally { loading.value = false }
})

function statusLabel(s: string) {
  if (s === 'active') return '有效'
  if (s === 'expired') return '已过期'
  return '已删除'
}

function statusVariant(s: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  if (s === 'active') return 'default'
  if (s === 'expired') return 'destructive'
  return 'secondary'
}
</script>