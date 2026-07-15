<template>
  <div class="max-w-[1200px]">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-foreground mb-1">存取日志</h1>
      <p class="text-sm text-muted-foreground">查看所有文件下载记录</p>
    </div>

    <!-- Filters -->
    <div class="flex gap-2 items-center mb-4 flex-wrap">
      <input v-model="filterCode" type="text" class="h-8 px-3 text-sm bg-card border border-border rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-ring" placeholder="取件码" @keyup.enter="loadLogs" />
      <Popover v-model:open="shareTypeOpen">
        <PopoverTrigger as-child>
          <Button variant="outline" class="h-8 px-3 text-sm">
            {{ shareTypeFilter.length === 0 ? '全部类型' : `已选 ${shareTypeFilter.length} 项` }}
          </Button>
        </PopoverTrigger>
        <PopoverContent class="w-[180px] p-2" align="start">
          <div class="space-y-1">
            <label
              v-for="opt in shareTypeOptions"
              :key="opt.value"
              class="flex items-center gap-2 rounded-sm px-2 py-1.5 text-sm cursor-pointer hover:bg-muted"
            >
              <input
                type="checkbox"
                class="w-4 h-4 rounded border-border accent-primary"
                :checked="shareTypeFilter.includes(opt.value)"
                @change="toggleShareType(opt.value)"
              />
              {{ opt.label }}
            </label>
          </div>
        </PopoverContent>
      </Popover>
      <DatePicker v-model="startTime" placeholder="开始日期" />
      <span class="text-muted-foreground text-xs">至</span>
      <DatePicker v-model="endTime" placeholder="结束日期" />
      <Button size="sm" @click="loadLogs">搜索</Button>
    </div>

    <!-- Table -->
    <div class="bg-card border border-border rounded-lg overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-16">
        <div class="w-6 h-6 border-2 border-muted border-t-primary rounded-full animate-spin"></div>
      </div>
      <div v-else-if="logs.length === 0" class="py-16 text-center text-muted-foreground text-sm">暂无日志数据</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full border-collapse">
          <thead>
            <tr>
              <th class="py-3 px-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted border-b border-border whitespace-nowrap">时间</th>
              <th class="py-3 px-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted border-b border-border whitespace-nowrap">取件码</th>
              <th class="py-3 px-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted border-b border-border">分享任务</th>
              <th class="py-3 px-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted border-b border-border whitespace-nowrap">IP 地址</th>
              <th class="py-3 px-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted border-b border-border whitespace-nowrap">结果</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in logs"
              :key="row.id"
              class="hover:bg-muted/50 cursor-pointer transition-colors"
              @click="openDetail(row)"
            >
              <td class="py-3 px-4 border-b border-border whitespace-nowrap">
                <div class="text-xs leading-tight">{{ formatDate(row.download_time) }}</div>
                <div class="text-xs text-muted-foreground leading-tight">{{ formatTime(row.download_time) }}</div>
              </td>
              <td class="py-3 px-4 border-b border-border whitespace-nowrap">
                <span class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary">{{ row.code }}</span>
              </td>
              <td class="py-3 px-4 text-sm border-b border-border">
                <div class="max-w-[260px] line-clamp-2 break-all">{{ shareName(row) }}</div>
              </td>
              <td class="py-3 px-4 text-sm border-b border-border font-mono whitespace-nowrap">{{ row.ip }}</td>
              <td class="py-3 px-4 border-b border-border whitespace-nowrap">
                <span v-if="row.success" class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600">成功</span>
                <span v-else class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-destructive/10 text-destructive">失败</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="flex items-center justify-between px-5 py-3 border-t border-border">
        <span class="text-xs text-muted-foreground">共 {{ total }} 条</span>
        <div class="flex items-center gap-2">
          <Button variant="outline" size="icon" class="h-8 w-8" :disabled="page <= 1" @click="changePage(page - 1)">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"></polyline></svg>
          </Button>
          <span class="min-w-[32px] h-8 flex items-center justify-center bg-primary text-primary-foreground rounded-md text-xs font-semibold">{{ page }}</span>
          <Button variant="outline" size="icon" class="h-8 w-8" :disabled="page * pageSize >= total" @click="changePage(page + 1)">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </Button>
        </div>
        <Select :model-value="String(pageSize)" @update:model-value="(v) => { pageSize = Number(v); loadLogs() }">
          <SelectTrigger class="w-[100px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="20">20条/页</SelectItem>
            <SelectItem value="50">50条/页</SelectItem>
            <SelectItem value="100">100条/页</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>

    <!-- Detail Dialog -->
    <Dialog v-model:open="detailOpen">
      <DialogContent class="sm:max-w-[520px]">
        <DialogHeader>
          <DialogTitle>日志详情</DialogTitle>
        </DialogHeader>
        <div v-if="detailRow" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <div class="text-xs text-muted-foreground mb-1">分享任务</div>
              <div class="text-sm font-medium break-all">{{ shareName(detailRow) }}</div>
            </div>
            <div>
              <div class="text-xs text-muted-foreground mb-1">取件码</div>
              <span class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary">{{ detailRow.code }}</span>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <div class="text-xs text-muted-foreground mb-1">时间</div>
              <div class="text-sm font-medium">{{ formatDate(detailRow.download_time) }} {{ formatTime(detailRow.download_time) }}</div>
            </div>
            <div>
              <div class="text-xs text-muted-foreground mb-1">结果</div>
              <span v-if="detailRow.success" class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600">成功</span>
              <span v-else class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-destructive/10 text-destructive">失败</span>
            </div>
          </div>

          <div v-if="detailRow.reason">
            <div class="text-xs text-muted-foreground mb-1">失败原因</div>
            <div class="text-sm font-medium text-destructive">{{ detailRow.reason }}</div>
          </div>

          <div>
            <div class="text-xs text-muted-foreground mb-1">IP 地址</div>
            <div class="text-sm font-medium font-mono">{{ detailRow.ip }}</div>
          </div>

          <div>
            <div class="text-xs text-muted-foreground mb-1">User-Agent</div>
            <div class="text-xs font-mono text-muted-foreground break-all leading-relaxed bg-muted/50 rounded p-2.5">{{ detailRow.user_agent }}</div>
          </div>

          <div v-if="uaInfo">
            <div class="text-xs text-muted-foreground mb-2">解析信息</div>
            <div class="grid grid-cols-3 gap-3">
              <div>
                <div class="text-[11px] text-muted-foreground mb-0.5">浏览器</div>
                <div class="text-xs font-medium">{{ uaInfo.browser }}</div>
              </div>
              <div>
                <div class="text-[11px] text-muted-foreground mb-0.5">操作系统</div>
                <div class="text-xs font-medium">{{ uaInfo.os }}</div>
              </div>
              <div>
                <div class="text-[11px] text-muted-foreground mb-0.5">设备类型</div>
                <div class="text-xs font-medium">{{ uaInfo.device }}</div>
              </div>
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="detailOpen = false">关闭</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { toast } from 'vue-sonner'
import api from '../../api'
import { formatDate, formatTime } from '../../utils/format'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import DatePicker from '@/components/DatePicker.vue'

const loading = ref(true)
const logs = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filterCode = ref('')
const startTime = ref('')
const endTime = ref('')
const shareTypeFilter = ref<string[]>([])
const shareTypeOpen = ref(false)
const detailOpen = ref(false)
const detailRow = ref<any>(null)

const shareTypeOptions = [
  { value: 'single', label: '单文件' },
  { value: 'multi', label: '多文件' },
  { value: 'folder', label: '文件夹' },
]

function toggleShareType(val: string) {
  const idx = shareTypeFilter.value.indexOf(val)
  if (idx >= 0) {
    shareTypeFilter.value.splice(idx, 1)
  } else {
    shareTypeFilter.value.push(val)
  }
  loadLogs()
}

function shareName(row: any): string {
  if (row.is_group) {
    if (row.share_type === 'folder' && row.group_name) return `文件夹-${row.group_name}`
    return `多文件-${row.filename || '未知'}等`
  }
  return row.filename || '-'
}

function parseUserAgent(ua: string) {
  if (!ua) return null

  let browser = '未知'
  if (ua.includes('Firefox/')) browser = 'Firefox ' + (ua.match(/Firefox\/([\d.]+)/)?.[1] || '')
  else if (ua.includes('Edg/')) browser = 'Edge ' + (ua.match(/Edg\/([\d.]+)/)?.[1] || '')
  else if (ua.includes('OPR/')) browser = 'Opera ' + (ua.match(/OPR\/([\d.]+)/)?.[1] || '')
  else if (ua.includes('Chrome/')) browser = 'Chrome ' + (ua.match(/Chrome\/([\d.]+)/)?.[1] || '')
  else if (ua.includes('Safari/') && ua.includes('Version/')) browser = 'Safari ' + (ua.match(/Version\/([\d.]+)/)?.[1] || '')

  let os = '未知'
  if (ua.includes('Windows NT 10')) os = 'Windows 10/11'
  else if (ua.includes('Windows NT 6.3')) os = 'Windows 8.1'
  else if (ua.includes('Windows NT 6.1')) os = 'Windows 7'
  else if (ua.includes('Mac OS X')) os = 'macOS ' + (ua.match(/Mac OS X ([\d_]+)/)?.[1]?.replace(/_/g, '.') || '')
  else if (ua.includes('Android')) os = 'Android ' + (ua.match(/Android ([\d.]+)/)?.[1] || '')
  else if (ua.includes('iPhone') || ua.includes('iPad')) os = 'iOS ' + (ua.match(/OS ([\d_]+)/)?.[1]?.replace(/_/g, '.') || '')
  else if (ua.includes('Linux')) os = 'Linux'

  let device = '桌面端'
  if (ua.includes('Mobile') || ua.includes('Android')) device = '移动端'
  else if (ua.includes('iPad') || ua.includes('Tablet')) device = '平板'

  return { browser, os, device }
}

const uaInfo = computed(() => {
  if (!detailRow.value?.user_agent) return null
  return parseUserAgent(detailRow.value.user_agent)
})

function openDetail(row: any) {
  detailRow.value = row
  detailOpen.value = true
}

onMounted(() => loadLogs())

async function loadLogs() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (filterCode.value) params.code = filterCode.value
    if (startTime.value) params.start_time = startTime.value
    if (endTime.value) params.end_time = endTime.value
    if (shareTypeFilter.value.length > 0) params.share_type = shareTypeFilter.value.join(',')
    const res = await api.get('/admin/logs', { params })
    logs.value = res.data.logs
    total.value = res.data.total
  } catch { toast.error('加载日志失败') }
  finally { loading.value = false }
}

function changePage(newPage: number) { page.value = newPage; loadLogs() }
</script>
