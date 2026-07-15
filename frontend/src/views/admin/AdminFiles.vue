<template>
  <div class="max-w-[1200px]">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-foreground mb-1">分享管理</h1>
      <p class="text-sm text-muted-foreground">管理所有分享任务</p>
    </div>

    <!-- Filters -->
    <div class="flex gap-2 items-center mb-4 flex-wrap">
      <Select :model-value="filterStatus" @update:model-value="(v: any) => { filterStatus = String(v || ''); loadFiles() }">
        <SelectTrigger class="w-[140px] h-8 text-sm">
          <SelectValue placeholder="全部状态" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">全部状态</SelectItem>
          <SelectItem value="active">有效</SelectItem>
          <SelectItem value="expired">已过期</SelectItem>
          <SelectItem value="deleted">已删除</SelectItem>
        </SelectContent>
      </Select>
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
      <div class="relative flex-1">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input v-model="filterSearch" type="text" class="w-full h-8 pl-9 pr-3 text-sm bg-card border border-border rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-ring" placeholder="搜索取件码或文件名..." @keyup.enter="loadFiles" />
      </div>
      <Button size="sm" @click="loadFiles">搜索</Button>
    </div>

    <!-- Batch bar -->
    <div v-if="selectedCodes.length > 0" class="flex items-center justify-between px-5 py-3.5 bg-primary/10 border border-primary/20 rounded-lg mb-4 text-sm text-primary">
      <span>已选择 <strong>{{ selectedCodes.length }}</strong> 个分享任务</span>
      <div class="flex items-center gap-2">
        <Button v-if="allSelectedActive" variant="outline" size="sm" @click="batchExpire">批量过期</Button>
        <Button variant="destructive" size="sm" @click="batchDeepClean">批量深度清理</Button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-card border border-border rounded-lg overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-16">
        <div class="w-6 h-6 border-2 border-muted border-t-primary rounded-full animate-spin"></div>
      </div>
      <div v-else-if="displayFiles.length === 0" class="py-16 text-center text-muted-foreground text-sm">暂无文件数据</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full border-collapse">
          <thead>
            <tr>
              <th class="w-10 text-center py-3 px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted border-b border-border">
                <input type="checkbox" class="w-4 h-4 cursor-pointer accent-primary" :checked="allSelected" @change="toggleAll" />
              </th>
              <th class="py-3 px-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted border-b border-border">分享任务名称</th>
              <th class="py-3 px-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted border-b border-border whitespace-nowrap">类型</th>
              <th class="py-3 px-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted border-b border-border whitespace-nowrap">大小</th>
              <th class="py-3 px-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted border-b border-border whitespace-nowrap">取件码</th>
              <th class="py-3 px-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted border-b border-border whitespace-nowrap">上传时间</th>
              <th class="py-3 px-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted border-b border-border whitespace-nowrap">状态</th>
              <th class="py-3 px-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted border-b border-border whitespace-nowrap">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in displayFiles"
              :key="row.code"
              class="hover:bg-muted/50 cursor-pointer transition-colors"
              @click="openDetail(row)"
            >
              <td class="text-center py-3 px-3 text-sm border-b border-border" @click.stop>
                <input type="checkbox" class="w-4 h-4 cursor-pointer accent-primary" :checked="selectedCodes.includes(row.code)" :disabled="!canSelect(row)" @change="toggleSelect(row.code)" />
              </td>
              <td class="py-3 px-4 text-sm border-b border-border">
                <div class="max-w-[240px] line-clamp-2 break-all">{{ shareName(row) }}</div>
              </td>
              <td class="py-3 px-4 border-b border-border whitespace-nowrap">
                <span :class="['inline-block px-2 py-0.5 rounded-full text-xs font-semibold', shareTypeBadgeClass(row)]">{{ shareTypeBadge(row) }}</span>
              </td>
              <td class="py-3 px-4 text-sm border-b border-border whitespace-nowrap">{{ formatFileSize(row.file_size) }}</td>
              <td class="py-3 px-4 border-b border-border whitespace-nowrap">
                <span class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary">{{ row.code }}</span>
              </td>
              <td class="py-3 px-4 border-b border-border whitespace-nowrap">
                <div class="text-xs leading-tight">{{ formatDate(row.upload_time) }}</div>
                <div class="text-xs text-muted-foreground leading-tight">{{ formatTime(row.upload_time) }}</div>
              </td>
              <td class="py-3 px-4 border-b border-border whitespace-nowrap">
                <span v-if="row.status === 'active'" class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary">{{ statusLabel(row.status) }}</span>
                <span v-else-if="row.status === 'expired'" class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-secondary text-secondary-foreground">{{ statusLabel(row.status) }}</span>
                <span v-else class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-muted text-muted-foreground">{{ statusLabel(row.status) }}</span>
              </td>
              <td class="py-3 px-4 border-b border-border whitespace-nowrap" @click.stop>
                <div class="flex items-center gap-1">
                  <Button variant="ghost" size="icon" class="h-8 w-8" @click="openDetail(row)" title="详情">
                    <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                  </Button>
                  <Button variant="ghost" size="icon" class="h-8 w-8" :disabled="row.status === 'deleted'" @click="downloadFile(row)" title="下载">
                    <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                  </Button>
                  <Button v-if="row.status === 'expired' && !row.is_deep_cleaned" variant="ghost" size="icon" class="h-8 w-8 text-destructive hover:text-destructive" @click="deepClean(row)" title="深度清理">
                    <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                  </Button>
                </div>
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
        <Select :model-value="String(pageSize)" @update:model-value="(v) => { pageSize = Number(v); loadFiles() }">
          <SelectTrigger class="w-[100px]">
            <SelectValue placeholder="20条/页" />
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
      <DialogContent :class="detailRow?.is_group ? 'sm:max-w-[880px]' : 'sm:max-w-[560px]'">
        <DialogHeader>
          <DialogTitle>{{ detailRow?.is_group ? '分享任务详情' : '文件详情' }}</DialogTitle>
        </DialogHeader>
        <div v-if="detailRow">
          <!-- ===== SINGLE FILE: keep original layout ===== -->
          <div v-if="!detailRow.is_group" class="space-y-4">
            <div>
              <div class="text-xs text-muted-foreground mb-1">文件名</div>
              <div class="text-sm font-medium break-all">{{ detailRow.original_filename }}</div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <div class="text-xs text-muted-foreground mb-1">文件大小</div>
                <div class="text-sm font-medium">{{ formatFileSize(detailRow.file_size) }}</div>
              </div>
              <div>
                <div class="text-xs text-muted-foreground mb-1">MIME 类型</div>
                <div class="text-sm font-medium">{{ detailRow.mime_type }}</div>
              </div>
              <div>
                <div class="text-xs text-muted-foreground mb-1">取件码</div>
                <div class="text-sm font-medium font-mono">{{ detailRow.code }}</div>
              </div>
              <div>
                <div class="text-xs text-muted-foreground mb-1">状态</div>
                <div>
                  <span v-if="detailRow.status === 'active'" class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary">{{ statusLabel(detailRow.status) }}</span>
                  <span v-else-if="detailRow.status === 'expired'" class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-secondary text-secondary-foreground">{{ statusLabel(detailRow.status) }}</span>
                  <span v-else class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-muted text-muted-foreground">{{ statusLabel(detailRow.status) }}</span>
                </div>
              </div>
              <div>
                <div class="text-xs text-muted-foreground mb-1">上传 IP</div>
                <div class="text-sm font-medium font-mono">{{ detailRow.upload_ip }}</div>
              </div>
              <div>
                <div class="text-xs text-muted-foreground mb-1">下载限制</div>
                <div class="text-sm font-medium">{{ detailRow.download_limit === -1 ? '无限次' : detailRow.download_limit + ' 次' }}</div>
              </div>
              <div>
                <div class="text-xs text-muted-foreground mb-1">剩余次数</div>
                <div class="text-sm font-medium">{{ detailRow.remaining_downloads === -1 ? '无限' : detailRow.remaining_downloads }}</div>
              </div>
              <div>
                <div class="text-xs text-muted-foreground mb-1">是否深度清理</div>
                <div class="text-sm font-medium">{{ detailRow.is_deep_cleaned ? '是' : '否' }}</div>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <div class="text-xs text-muted-foreground mb-1">上传时间</div>
                <div class="text-sm font-medium">{{ formatDate(detailRow.upload_time) }}</div>
                <div class="text-xs text-muted-foreground">{{ formatTime(detailRow.upload_time) }}</div>
              </div>
              <div>
                <div class="text-xs text-muted-foreground mb-1">过期时间</div>
                <div class="text-sm font-medium">{{ formatDate(detailRow.expires_at) }}</div>
                <div class="text-xs text-muted-foreground">{{ formatTime(detailRow.expires_at) }}</div>
              </div>
            </div>
            <!-- Recent downloads -->
            <div v-if="detailRow.recent_downloads?.length">
              <div class="text-xs text-muted-foreground mb-2">最近下载记录（{{ detailRow.recent_downloads.length }} 条）</div>
              <div class="border border-border rounded-md max-h-[200px] overflow-y-auto">
                <table class="w-full border-collapse text-xs">
                  <thead>
                    <tr class="bg-muted">
                      <th class="px-3 py-2 text-left font-semibold text-muted-foreground">时间</th>
                      <th class="px-3 py-2 text-left font-semibold text-muted-foreground">IP</th>
                      <th class="px-3 py-2 text-left font-semibold text-muted-foreground">结果</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(log, i) in detailRow.recent_downloads" :key="i" class="border-t border-border">
                      <td class="px-3 py-2 whitespace-nowrap">{{ formatDateTime(log.download_time) }}</td>
                      <td class="px-3 py-2 font-mono whitespace-nowrap">{{ log.ip }}</td>
                      <td class="px-3 py-2 whitespace-nowrap">
                        <span v-if="log.success" class="text-emerald-600">成功</span>
                        <span v-else class="text-destructive">失败 {{ log.reason ? `(${log.reason})` : '' }}</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ===== MULTI-FILE / FOLDER: LEFT-RIGHT layout ===== -->
          <div v-else class="flex gap-5">
            <!-- LEFT: task info -->
            <div class="w-[260px] min-w-[16rem] flex-shrink-0 space-y-3 overflow-y-auto">
              <div>
                <div class="text-xs text-muted-foreground mb-1">任务名称</div>
                <div class="text-sm font-medium break-all">{{ detailRow.group_name || detailRow.original_filename }}</div>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <div class="text-xs text-muted-foreground mb-1">类型</div>
                  <span :class="['inline-block px-2 py-0.5 rounded-full text-xs font-semibold', detailShareTypeClass]">{{ detailShareTypeLabel }}</span>
                </div>
                <div>
                  <div class="text-xs text-muted-foreground mb-1">总大小</div>
                  <div class="text-sm font-medium">{{ formatFileSize(detailRow.group_total_size || detailRow.file_size) }}</div>
                </div>
                <div>
                  <div class="text-xs text-muted-foreground mb-1">取件码</div>
                  <div class="text-sm font-medium font-mono">{{ detailRow.code }}</div>
                </div>
                <div>
                  <div class="text-xs text-muted-foreground mb-1">状态</div>
                  <div>
                    <span v-if="detailRow.status === 'active'" class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary">{{ statusLabel(detailRow.status) }}</span>
                    <span v-else-if="detailRow.status === 'expired'" class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-secondary text-secondary-foreground">{{ statusLabel(detailRow.status) }}</span>
                    <span v-else class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-muted text-muted-foreground">{{ statusLabel(detailRow.status) }}</span>
                  </div>
                </div>
                <div>
                  <div class="text-xs text-muted-foreground mb-1">上传 IP</div>
                  <div class="text-sm font-medium font-mono">{{ detailRow.upload_ip }}</div>
                </div>
                <div>
                  <div class="text-xs text-muted-foreground mb-1">下载限制</div>
                  <div class="text-sm font-medium">{{ detailRow.download_limit === -1 ? '无限次' : detailRow.download_limit + ' 次' }}</div>
                </div>
                <div>
                  <div class="text-xs text-muted-foreground mb-1">剩余次数</div>
                  <div class="text-sm font-medium">{{ detailRow.remaining_downloads === -1 ? '无限' : detailRow.remaining_downloads }}</div>
                </div>
                <div>
                  <div class="text-xs text-muted-foreground mb-1">是否深度清理</div>
                  <div class="text-sm font-medium">{{ detailRow.is_deep_cleaned ? '是' : '否' }}</div>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <div class="text-xs text-muted-foreground mb-1">上传时间</div>
                  <div class="text-sm font-medium">{{ formatDate(detailRow.upload_time) }}</div>
                  <div class="text-xs text-muted-foreground">{{ formatTime(detailRow.upload_time) }}</div>
                </div>
                <div>
                  <div class="text-xs text-muted-foreground mb-1">过期时间</div>
                  <div class="text-sm font-medium">{{ formatDate(detailRow.expires_at) }}</div>
                  <div class="text-xs text-muted-foreground">{{ formatTime(detailRow.expires_at) }}</div>
                </div>
              </div>
            </div>

            <!-- RIGHT: file list browser -->
            <div class="flex-1 min-w-0 flex flex-col border border-border rounded-md overflow-hidden">
              <!-- Header with count -->
              <div class="px-4 py-2.5 border-b border-border text-xs text-muted-foreground bg-muted/30">
                文件列表 <span class="text-xs font-normal text-muted-foreground">（{{ detailFolderCount }} 个文件夹 {{ detailFileCount }} 个文件）</span>
              </div>

              <!-- Table header -->
              <div class="flex items-center px-4 py-1.5 border-b border-border text-xs text-muted-foreground">
                <span class="flex-1">名称</span>
                <span class="w-20 text-right">大小</span>
              </div>

              <!-- File list -->
              <div class="flex-1 overflow-y-auto">
                <!-- Back button -->
                <div
                  v-if="detailCurrentPath.length > 0"
                  class="flex items-center gap-2 py-2 px-4 border-b border-border cursor-pointer hover:bg-muted/50 transition-colors"
                  @click="detailGoBack"
                >
                  <svg class="w-4 h-4 flex-shrink-0 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <polyline points="15 18 9 12 15 6"></polyline>
                  </svg>
                  <span class="text-sm text-muted-foreground">返回上一级</span>
                </div>

                <!-- Folders -->
                <div
                  v-for="folder in detailCurrentFolders"
                  :key="'d-' + folder"
                  class="flex items-center gap-2 py-2 px-4 border-b border-border cursor-pointer hover:bg-muted/50 transition-colors"
                  @click="detailEnterFolder(folder)"
                >
                  <svg class="w-4 h-4 flex-shrink-0 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                  </svg>
                  <span class="flex-1 min-w-0 text-sm text-foreground break-all line-clamp-2">{{ folder }}</span>
                </div>

                <!-- Files -->
                <div
                  v-for="f in detailCurrentFiles"
                  :key="'f-' + f.id"
                  class="flex items-center gap-2 py-2 px-4 border-b border-border last:border-b-0 hover:bg-muted/50 transition-colors"
                >
                  <svg class="w-4 h-4 flex-shrink-0 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                  </svg>
                  <span class="flex-1 min-w-0 text-sm text-foreground break-all line-clamp-2">{{ f.filename }}</span>
                  <span class="w-20 text-right text-xs text-muted-foreground flex-shrink-0">{{ formatFileSize(f.size) }}</span>
                </div>

                <!-- Empty -->
                <div v-if="detailCurrentFolders.length === 0 && detailCurrentFiles.length === 0" class="py-8 text-center text-sm text-muted-foreground">
                  无文件记录
                </div>
              </div>

              <!-- Breadcrumb -->
              <div class="px-4 py-2 border-t border-border flex items-center gap-1 text-xs text-muted-foreground bg-muted/20">
                <span class="cursor-pointer hover:text-foreground transition-colors" @click="detailNavigateToIndex(0)">根目录</span>
                <template v-for="(seg, idx) in detailCurrentPath" :key="idx">
                  <svg class="w-3 h-3 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"></polyline>
                  </svg>
                  <span class="cursor-pointer hover:text-foreground transition-colors" @click="detailNavigateToIndex(idx + 1)">{{ seg }}</span>
                </template>
              </div>
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="detailOpen = false">关闭</Button>
          <Button v-if="detailRow && detailRow.status === 'active'" variant="outline" class="text-destructive border-destructive/30 hover:bg-destructive/10" @click="expireSingle(detailRow)">立即过期</Button>
          <Button v-if="detailRow && detailRow.status !== 'deleted'" @click="downloadFile(detailRow)">{{ detailRow?.is_group ? '下载全部' : '下载文件' }}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { toast } from 'vue-sonner'
import api from '../../api'
import { formatFileSize, formatDateTime, formatDate, formatTime } from '../../utils/format'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'

const loading = ref(true)
const files = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filterStatus = ref('')
const filterSearch = ref('')
const shareTypeFilter = ref<string[]>([])
const shareTypeOpen = ref(false)
const selectedCodes = ref<string[]>([])
const detailOpen = ref(false)
const detailRow = ref<any>(null)
const detailCurrentPath = ref<string[]>([])

const shareTypeOptions = [
  { value: 'single', label: '单文件' },
  { value: 'multi', label: '多文件' },
  { value: 'folder', label: '文件夹' },
]

const displayFiles = computed(() => {
  const map = new Map<string, any>()
  for (const f of files.value) {
    if (!map.has(f.code)) {
      map.set(f.code, { ...f, _groupFiles: [f] })
    } else {
      map.get(f.code)._groupFiles.push(f)
    }
  }
  return Array.from(map.values())
})

const selectedFileIds = computed(() => {
  const ids: number[] = []
  for (const code of selectedCodes.value) {
    for (const f of files.value.filter(f => f.code === code)) {
      ids.push(f.id)
    }
  }
  return ids
})

const allSelected = computed(() => {
  const s = displayFiles.value.filter((r) => canSelect(r))
  return s.length > 0 && s.every((r) => selectedCodes.value.includes(r.code))
})

onMounted(() => loadFiles())

async function loadFiles() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (filterStatus.value && filterStatus.value !== 'all') params.status = filterStatus.value
    if (filterSearch.value) params.search = filterSearch.value
    if (shareTypeFilter.value.length > 0) params.share_type = shareTypeFilter.value.join(',')
    const res = await api.get('/admin/files', { params })
    files.value = res.data.files
    total.value = res.data.total
  } catch { toast.error('加载文件列表失败') }
  finally { loading.value = false }
}

function toggleSelect(code: string) {
  const idx = selectedCodes.value.indexOf(code)
  if (idx >= 0) selectedCodes.value.splice(idx, 1)
  else selectedCodes.value.push(code)
}

function toggleShareType(val: string) {
  const idx = shareTypeFilter.value.indexOf(val)
  if (idx >= 0) {
    shareTypeFilter.value.splice(idx, 1)
  } else {
    shareTypeFilter.value.push(val)
  }
  loadFiles()
}

function toggleAll() {
  if (allSelected.value) selectedCodes.value = []
  else selectedCodes.value = displayFiles.value.filter((r) => canSelect(r)).map((r) => r.code)
}

function canSelect(row: any) {
  if (row.is_group && row._groupFiles) {
    return row._groupFiles.some((f: any) => f.status === 'expired' && !f.is_deep_cleaned)
  }
  return row.status === 'expired' && !row.is_deep_cleaned
}

const allSelectedActive = computed(() => {
  if (selectedCodes.value.length === 0) return false
  return displayFiles.value
    .filter(r => selectedCodes.value.includes(r.code))
    .every(r => r.status === 'active')
})
function changePage(p: number) { page.value = p; loadFiles() }

async function openDetail(row: any) {
  try {
    const res = await api.get(`/admin/files/${row.id}`)
    detailRow.value = res.data
    detailCurrentPath.value = []
    detailOpen.value = true
  } catch { toast.error('加载文件详情失败') }
}

async function downloadFile(row: any) {
  try {
    const res = await api.get(`/file/${row.code}/download`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a'); a.href = url; a.download = row.original_filename
    document.body.appendChild(a); a.click(); window.URL.revokeObjectURL(url); document.body.removeChild(a)
  } catch { toast.error('下载失败') }
}

async function deepClean(row: any) {
  if (!window.confirm(`确定深度清理 "${row.original_filename}" 吗？`)) return
  try {
    await api.delete(`/admin/files/${row.id}/deep-clean`)
    toast.success('深度清理完成'); loadFiles()
  } catch {}
}

async function batchDeepClean() {
  if (!window.confirm(`确定深度清理选中的 ${selectedCodes.value.length} 个分享任务吗？`)) return
  try {
    await api.post('/admin/files/batch-deep-clean', { ids: selectedFileIds.value })
    toast.success('批量深度清理完成'); selectedCodes.value = []; loadFiles()
  } catch {}
}

async function expireSingle(row: any) {
  if (!window.confirm(`确定立即使 "${row.original_filename || row.code}" 过期吗？`)) return
  try {
    await api.post(`/admin/files/${row.code}/expire`)
    toast.success('已标记过期')
    detailOpen.value = false
    loadFiles()
  } catch {}
}

async function batchExpire() {
  if (!window.confirm(`确定立即使选中的 ${selectedCodes.value.length} 个分享任务过期吗？`)) return
  try {
    await api.post('/admin/files/batch-expire', { codes: selectedCodes.value })
    toast.success('批量过期完成'); selectedCodes.value = []; loadFiles()
  } catch {}
}

function statusLabel(s: string) {
  if (s === 'active') return '有效'
  if (s === 'expired') return '已过期'
  return '已删除'
}

function shareTypeBadge(row: any) {
  const t = row.share_type
  if (t === 'folder') return '文件夹'
  if (t === 'multi') return '多文件'
  return '单文件'
}

function shareTypeBadgeClass(row: any) {
  const t = row.share_type
  if (t === 'folder') return 'bg-accent text-accent-foreground'
  if (t === 'multi') return 'bg-secondary text-secondary-foreground'
  return 'bg-muted text-muted-foreground'
}

function shareName(row: any): string {
  if (row.share_type === 'single') return row.original_filename
  if (row.share_type === 'folder') return `文件夹-${row.original_filename}`
  return `多文件-${row.original_filename}`
}

const detailShareTypeLabel = computed(() => {
  if (!detailRow.value) return ''
  const t = detailRow.value.share_type
  if (t === 'folder') return '文件夹'
  if (t === 'multi') return '多文件'
  return '单文件'
})

const detailShareTypeClass = computed(() => {
  if (!detailRow.value) return ''
  const t = detailRow.value.share_type
  if (t === 'folder') return 'bg-accent text-accent-foreground'
  if (t === 'multi') return 'bg-secondary text-secondary-foreground'
  return 'bg-muted text-muted-foreground'
})

// Folder navigation for detail dialog
const detailCurrentFolders = computed(() => {
  if (!detailRow.value?.files) return []
  const prefix = detailCurrentPath.value.length > 0 ? detailCurrentPath.value.join('/') + '/' : ''
  const folders = new Set<string>()
  for (const file of detailRow.value.files) {
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

const detailCurrentFiles = computed(() => {
  if (!detailRow.value?.files) return []
  const prefix = detailCurrentPath.value.length > 0 ? detailCurrentPath.value.join('/') + '/' : ''
  return detailRow.value.files.filter((file: any) => {
    const rel = file.relative_path || file.filename
    if (!rel.startsWith(prefix)) return false
    const rest = rel.slice(prefix.length)
    return !rest.includes('/')
  })
})

const detailFolderCount = computed(() => detailCurrentFolders.value.length)
const detailFileCount = computed(() => detailCurrentFiles.value.length)

function detailEnterFolder(name: string) {
  detailCurrentPath.value.push(name)
}

function detailGoBack() {
  detailCurrentPath.value.pop()
}

function detailNavigateToIndex(idx: number) {
  detailCurrentPath.value = detailCurrentPath.value.slice(0, idx)
}

</script>
