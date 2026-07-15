<template>
  <div class="max-w-3xl mx-auto">
    <!-- Loading state -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full border-3 border-muted border-t-primary w-10 h-10 mx-auto"></div>
    </div>
    <div v-else>
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-foreground mb-1">全局设置</h1>
        <p class="text-sm text-muted-foreground">配置系统参数和上传规则</p>
      </div>

      <!-- Basic Settings -->
      <div class="mb-8">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-md flex items-center justify-center flex-shrink-0 bg-primary/10 text-primary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-5 h-5">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
          </div>
          <div>
            <h2 class="text-base font-semibold text-foreground">基础配置</h2>
            <p class="text-[13px] text-muted-foreground">文件类型和大小限制</p>
          </div>
        </div>

        <div class="bg-card border border-border rounded-lg p-5">
          <!-- Upload Control Mode -->
          <div class="flex items-center justify-between py-3.5 border-b border-border">
            <div class="flex-1">
              <Label class="block text-sm font-medium mb-0.5">上传控制模式</Label>
              <p class="text-[13px] text-muted-foreground">选择文件类型的验证方式</p>
            </div>
            <Select :model-value="uploadControlMode" @update:model-value="(v) => uploadControlMode = String(v)">
              <SelectTrigger class="w-[120px] h-9 px-3"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="whitelist">白名单</SelectItem>
                <SelectItem value="blacklist">黑名单</SelectItem>
                <SelectItem value="none">无控制</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- Extensions (dynamic based on mode) -->
          <div class="flex items-start justify-between py-3.5 border-b border-border">
            <div class="flex-1">
              <Label class="block text-sm font-medium mb-0.5">
                {{ uploadControlMode === 'blacklist' ? '文件类型黑名单' : uploadControlMode === 'whitelist' ? '文件类型白名单' : '文件类型' }}
              </Label>
              <p class="text-[13px] text-muted-foreground">
                {{ uploadControlMode === 'blacklist' ? '禁止上传的文件扩展名，每行一个' : uploadControlMode === 'whitelist' ? '允许上传的文件扩展名，每行一个' : '已关闭文件类型限制，允许上传所有文件' }}
              </p>
            </div>
            <Textarea v-if="uploadControlMode !== 'none'" v-model="extensionsStr" class="w-[260px] h-[120px] resize-y" placeholder="jpg&#10;png&#10;pdf&#10;docx" />
            <span v-else class="text-sm text-muted-foreground self-center">全部允许</span>
          </div>

          <!-- Single file size limit -->
          <div class="flex items-center justify-between py-3.5 border-b border-border">
            <div class="flex-1">
              <Label class="block text-sm font-medium mb-0.5">单文件上传大小上限</Label>
              <p class="text-[13px] text-muted-foreground">单个文件的最大大小</p>
            </div>
            <div class="flex items-center gap-2">
              <Input v-model.number="maxSizeValue" type="number" class="w-[100px] text-center h-9 px-3" :min="1" />
              <Select v-model="maxSizeUnit">
                <SelectTrigger class="w-[80px] h-9 px-3"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">B</SelectItem>
                  <SelectItem value="1024">KB</SelectItem>
                  <SelectItem value="1048576">MB</SelectItem>
                  <SelectItem value="1073741824">GB</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <!-- Task limits -->
          <div class="flex items-center justify-between py-3.5 border-b border-border">
            <div class="flex-1">
              <Label class="block text-sm font-medium mb-0.5">单次分享任务上限</Label>
              <p class="text-[13px] text-muted-foreground">单次上传的文件数量和总大小限制</p>
            </div>
            <div class="flex items-center gap-4">
              <div class="flex items-center gap-2">
                <Input v-model.number="maxFilesPerTask" type="number" class="w-[80px] text-center h-9 px-3" :min="1" />
                <span class="text-[13px] text-muted-foreground">个文件</span>
              </div>
              <div class="flex items-center gap-2">
                <Input v-model.number="maxTaskSizeValue" type="number" class="w-[80px] text-center h-9 px-3" :min="1" />
                <Select v-model="maxTaskSizeUnit">
                  <SelectTrigger class="w-[80px] h-9 px-3"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1048576">MB</SelectItem>
                    <SelectItem value="1073741824">GB</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Frontend Options Config (Expiry + Download Limit) — 50% grid -->
      <div class="mb-8">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-md flex items-center justify-center flex-shrink-0 bg-emerald-500/10 text-emerald-600">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-5 h-5">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
          <div>
            <h2 class="text-base font-semibold text-foreground">前台选项配置</h2>
            <p class="text-[13px] text-muted-foreground">用户上传时可选择的有效期和下载次数</p>
          </div>
        </div>

        <div class="bg-card border border-border rounded-lg p-5">
          <!-- Expiry Options -->
          <div class="flex items-center justify-between py-3.5 border-b border-border">
            <div class="flex-1">
              <Label class="block text-sm font-medium mb-0.5">有效期选项</Label>
              <p class="text-[13px] text-muted-foreground">用户上传时可选择的文件有效期</p>
            </div>
            <Button variant="outline" size="sm" class="h-8 gap-1 shrink-0" @click="showExpiryAdd = !showExpiryAdd">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-3.5 h-3.5">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              添加
            </Button>
          </div>
          <!-- Add form -->
          <div v-if="showExpiryAdd" class="flex items-center gap-2 py-3 border-b border-border bg-muted/30 px-4">
            <Input v-model.number="newExpiryNum" type="number" class="w-[80px] h-8 text-center text-sm" :min="1" />
            <Select v-model="newExpiryUnit">
              <SelectTrigger class="w-[80px] h-8 text-sm"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="minutes">分钟</SelectItem>
                <SelectItem value="hours">小时</SelectItem>
                <SelectItem value="days">天</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="ghost" size="icon" class="w-7 h-7 text-emerald-600 hover:text-emerald-700 hover:bg-emerald-500/10" @click="confirmAddExpiry">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </Button>
            <Button variant="ghost" size="icon" class="w-7 h-7 text-muted-foreground hover:text-foreground" @click="showExpiryAdd = false">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </Button>
          </div>
          <!-- Option list -->
          <div v-if="expiryOptions.length > 0" class="divide-y divide-border">
            <div v-for="(option, index) in expiryOptions" :key="index"
              class="flex items-center gap-2 py-2.5 px-4 group hover:bg-muted/50 transition-colors">
              <div class="flex items-center gap-0.5 shrink-0">
                <Button variant="ghost" size="icon" class="w-5 h-5 text-muted-foreground hover:text-foreground" :disabled="index === 0" @click="moveExpiryOption(index, -1)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3"><polyline points="18 15 12 9 6 15"></polyline></svg>
                </Button>
                <Button variant="ghost" size="icon" class="w-5 h-5 text-muted-foreground hover:text-foreground" :disabled="index === expiryOptions.length - 1" @click="moveExpiryOption(index, 1)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3"><polyline points="6 9 12 15 18 9"></polyline></svg>
                </Button>
              </div>
              <span class="text-sm flex-1">{{ option.label }}</span>
              <div class="h-6 flex items-center shrink-0">
                <span v-if="index === expiryDefaultIndex" class="inline-flex items-center h-5 px-2 rounded-full text-[11px] font-medium bg-primary/10 text-primary">默认选项</span>
                <button v-else class="invisible group-hover:visible text-xs text-primary/50 hover:text-primary cursor-pointer px-1 py-0.5 rounded transition-colors" @click.stop="setDefaultExpiry(index)">设为默认</button>
              </div>
              <Button variant="ghost" size="icon" class="w-5 h-5 text-muted-foreground hover:text-destructive shrink-0" @click="expiryOptions.splice(index, 1)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </Button>
            </div>
          </div>
          <div v-else class="py-3 px-4 text-sm text-muted-foreground">暂无选项</div>

          <!-- Download Limit Options -->
          <div class="flex items-center justify-between py-3.5 border-t border-border">
            <div class="flex-1">
              <Label class="block text-sm font-medium mb-0.5">可下载次数选项</Label>
              <p class="text-[13px] text-muted-foreground">用户上传时可选择的下载次数限制</p>
            </div>
            <Button variant="outline" size="sm" class="h-8 gap-1 shrink-0" @click="showDlAdd = !showDlAdd">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-3.5 h-3.5">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              添加
            </Button>
          </div>
          <!-- Add form -->
          <div v-if="showDlAdd" class="flex items-center gap-2 py-3 border-b border-border bg-muted/30 px-4">
            <Input v-model.number="newDlNum" type="number" class="w-[80px] h-8 text-center text-sm" :min="1" :disabled="newDlUnit === 'unlimited'" />
            <Select v-model="newDlUnit">
              <SelectTrigger class="w-[90px] h-8 text-sm"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="times">次</SelectItem>
                <SelectItem value="unlimited">不限次数</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="ghost" size="icon" class="w-7 h-7 text-emerald-600 hover:text-emerald-700 hover:bg-emerald-500/10" @click="confirmAddDl">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </Button>
            <Button variant="ghost" size="icon" class="w-7 h-7 text-muted-foreground hover:text-foreground" @click="showDlAdd = false">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </Button>
          </div>
          <!-- Option list -->
          <div v-if="dlOptions.length > 0" class="divide-y divide-border">
            <div v-for="(option, index) in dlOptions" :key="index"
              class="flex items-center gap-2 py-2.5 px-4 group hover:bg-muted/50 transition-colors">
              <div class="flex items-center gap-0.5 shrink-0">
                <Button variant="ghost" size="icon" class="w-5 h-5 text-muted-foreground hover:text-foreground" :disabled="index === 0" @click="moveDlOption(index, -1)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3"><polyline points="18 15 12 9 6 15"></polyline></svg>
                </Button>
                <Button variant="ghost" size="icon" class="w-5 h-5 text-muted-foreground hover:text-foreground" :disabled="index === dlOptions.length - 1" @click="moveDlOption(index, 1)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3"><polyline points="6 9 12 15 18 9"></polyline></svg>
                </Button>
              </div>
              <span class="text-sm flex-1">{{ option.value === -1 ? '不限次数' : option.label }}</span>
              <div class="h-6 flex items-center shrink-0">
                <span v-if="index === dlDefaultIndex" class="inline-flex items-center h-5 px-2 rounded-full text-[11px] font-medium bg-primary/10 text-primary">默认选项</span>
                <button v-else class="invisible group-hover:visible text-xs text-primary/50 hover:text-primary cursor-pointer px-1 py-0.5 rounded transition-colors" @click.stop="setDefaultDl(index)">设为默认</button>
              </div>
              <Button variant="ghost" size="icon" class="w-5 h-5 text-muted-foreground hover:text-destructive shrink-0" @click="dlOptions.splice(index, 1)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </Button>
            </div>
          </div>
          <div v-else class="py-3 px-4 text-sm text-muted-foreground">暂无选项</div>
        </div>
      </div>

      <!-- Showcase Tasks Section -->
      <div class="mb-8">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-md flex items-center justify-center flex-shrink-0 bg-blue-500/10 text-blue-600">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-5 h-5">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <circle cx="8.5" cy="8.5" r="1.5"></circle>
              <polyline points="21 15 16 10 5 21"></polyline>
            </svg>
          </div>
          <div>
            <h2 class="text-base font-semibold text-foreground">展示任务</h2>
            <p class="text-[13px] text-muted-foreground">前台页面展示的图片任务</p>
          </div>
        </div>

        <div class="bg-card border border-border rounded-lg p-5">
          <!-- Empty state -->
          <div v-if="showcaseTasks.length === 0" class="text-center py-8">
            <p class="text-sm text-muted-foreground mb-3">暂无展示图片</p>
            <Button variant="outline" size="sm" @click="openShowcaseDialog(null)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-4 h-4 mr-1.5">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              新增展示任务
            </Button>
          </div>

          <!-- Tasks list -->
          <div v-if="showcaseTasks.length > 0" class="divide-y divide-border">
            <div v-for="(task, index) in showcaseTasks" :key="task.id"
              class="flex items-center gap-2 py-2.5 px-4 group hover:bg-muted/50 transition-colors cursor-pointer"
              @click="openShowcaseDialog(task)">
              <div class="flex items-center gap-0.5 shrink-0">
                <Button variant="ghost" size="icon" class="w-5 h-5 text-muted-foreground hover:text-foreground" :disabled="index === 0" @click.stop="moveShowcaseTask(index, -1)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3"><polyline points="18 15 12 9 6 15"></polyline></svg>
                </Button>
                <Button variant="ghost" size="icon" class="w-5 h-5 text-muted-foreground hover:text-foreground" :disabled="index === showcaseTasks.length - 1" @click.stop="moveShowcaseTask(index, 1)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3"><polyline points="6 9 12 15 18 9"></polyline></svg>
                </Button>
              </div>
              <span class="text-sm flex-1">{{ task.name }}</span>
              <span v-if="task.is_active" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-600">生效中</span>
              <span v-else-if="task.valid_from && new Date(task.valid_from) > new Date()" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-600">待生效</span>
              <span v-else class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-muted text-muted-foreground">已失效</span>
            </div>
          </div>
          <div v-else class="py-3 px-4 text-sm text-muted-foreground">暂无展示任务</div>
          <div class="flex items-center justify-end mt-3">
            <Button variant="outline" size="sm" class="h-8 gap-1" @click="openShowcaseDialog(null)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-3.5 h-3.5">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              新增
            </Button>
          </div>
        </div>
      </div>

      <!-- Cleanup Settings -->
      <div class="mb-8">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-md flex items-center justify-center flex-shrink-0 bg-destructive/10 text-destructive">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-5 h-5">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
          </div>
          <div>
            <h2 class="text-base font-semibold text-foreground">清理策略</h2>
            <p class="text-[13px] text-muted-foreground">自动清理过期文件的配置</p>
          </div>
        </div>

        <div class="bg-card border border-border rounded-lg p-5">
          <div class="flex items-center justify-between py-3.5 border-b border-border last:border-0 first:pt-0 last:pb-0">
            <div class="flex-1">
              <Label class="block text-sm font-medium mb-0.5">扫描间隔</Label>
              <p class="text-[13px] text-muted-foreground">检查过期文件的时间间隔</p>
            </div>
            <div class="flex items-center gap-2">
              <Input v-model.number="cleanupInterval" type="number" class="w-[100px] text-center h-9 px-3" :min="1" />
              <span class="text-[13px] text-muted-foreground">分钟</span>
            </div>
          </div>
          <div class="flex items-center justify-between py-3.5 border-b border-border last:border-0 first:pt-0 last:pb-0">
            <div class="flex-1">
              <Label class="block text-sm font-medium mb-0.5">自动深度清理</Label>
              <p class="text-[13px] text-muted-foreground">过期后自动物理删除文件</p>
            </div>
            <Switch v-model:checked="autoDeepClean" />
          </div>
          <div v-if="autoDeepClean" class="flex items-center justify-between py-3.5 border-b border-border last:border-0 first:pt-0 last:pb-0">
            <div class="flex-1">
              <Label class="block text-sm font-medium mb-0.5">延迟删除时间</Label>
              <p class="text-[13px] text-muted-foreground">过期后等待多少分钟再自动删除</p>
            </div>
            <div class="flex items-center gap-2">
              <Input v-model.number="autoDeepCleanDelay" type="number" class="w-[100px] text-center h-9 px-3" :min="0" />
              <span class="text-[13px] text-muted-foreground">分钟</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Save -->
      <div class="mt-8 pt-6 border-t border-border">
        <Button @click="save" :disabled="saving" class="px-7 py-3">
          <span v-if="saving" class="w-4 h-4 border-2 border-primary-foreground/30 rounded-full border-t-primary-foreground animate-spin"></span>
          {{ saving ? '保存中...' : '保存设置' }}
        </Button>
      </div>
    </div>

    <!-- Showcase Task Dialog -->
    <Dialog v-model:open="showcaseDialogOpen">
      <DialogContent class="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{{ editingShowcase ? '编辑展示任务' : '新增展示任务' }}</DialogTitle>
          <DialogDescription>
            {{ editingShowcase ? '修改展示任务信息' : '创建一个新的展示任务' }}
          </DialogDescription>
        </DialogHeader>
        <div class="space-y-4 py-2">
          <div>
            <Label class="text-sm font-medium mb-1.5 block">任务名称</Label>
            <Input v-model="showcaseForm.name" placeholder="输入任务名称" />
          </div>
          <div>
            <Label class="text-sm font-medium mb-1.5 block">展示图片</Label>
            <div v-if="showcaseForm.preview" class="mb-2">
              <img :src="showcaseForm.preview" alt="Preview" class="max-h-[150px] rounded-md object-contain" />
            </div>
            <input
              ref="showcaseFileInputRef"
              type="file"
              accept="image/*"
              class="hidden"
              @change="onShowcaseFileChange"
            />
            <Button variant="outline" size="sm" @click="showcaseFileInputRef?.click()">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-4 h-4 mr-1.5">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
              {{ showcaseForm.file ? '更换图片' : '选择图片' }}
            </Button>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <Label class="text-sm font-medium mb-1.5 block">生效开始日期</Label>
              <Popover>
                <PopoverTrigger as-child>
                  <Button variant="outline" class="w-full justify-start text-left font-normal h-9">
                    <svg class="w-4 h-4 mr-2 shrink-0 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                      <line x1="16" y1="2" x2="16" y2="6"></line>
                      <line x1="8" y1="2" x2="8" y2="6"></line>
                      <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                    <span :class="showcaseForm.valid_from ? '' : 'text-muted-foreground'">{{ showcaseForm.valid_from || '选择日期' }}</span>
                  </Button>
                </PopoverTrigger>
                <PopoverContent class="w-auto p-0" align="start">
                  <Calendar
                    :placeholder="stringToCalendarDate(showcaseForm.valid_from) || stringToCalendarDate(getDefaultValidFrom())"
                    @update:placeholder="(v: any) => { if (v) { showcaseForm.valid_from = calendarDateToString(v) } }"
                    initial-focus
                  />
                </PopoverContent>
              </Popover>
            </div>
            <div>
              <Label class="text-sm font-medium mb-1.5 block">生效结束日期</Label>
              <Popover>
                <PopoverTrigger as-child>
                  <Button variant="outline" class="w-full justify-start text-left font-normal h-9">
                    <svg class="w-4 h-4 mr-2 shrink-0 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                      <line x1="16" y1="2" x2="16" y2="6"></line>
                      <line x1="8" y1="2" x2="8" y2="6"></line>
                      <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                    <span :class="showcaseForm.valid_until ? '' : 'text-muted-foreground'">{{ showcaseForm.valid_until || '选择日期' }}</span>
                  </Button>
                </PopoverTrigger>
                <PopoverContent class="w-auto p-0" align="start">
                  <Calendar
                    :placeholder="stringToCalendarDate(showcaseForm.valid_until) || stringToCalendarDate(getDefaultValidUntil())"
                    @update:placeholder="(v: any) => { if (v) { showcaseForm.valid_until = calendarDateToString(v) } }"
                    initial-focus
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>
          <p class="text-[12px] text-muted-foreground">注：生效时间为全天，开始日期当天0点至结束日期当天24点</p>
        </div>
        <DialogFooter class="gap-2">
          <Button v-if="editingShowcase" variant="destructive" size="sm" @click="deleteShowcaseTask">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-4 h-4 mr-1.5">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
            删除
          </Button>
          <div class="flex-1"></div>
          <Button variant="outline" size="sm" @click="showcaseDialogOpen = false">取消</Button>
          <Button size="sm" :disabled="showcaseSaving" @click="saveShowcaseTask">
            <span v-if="showcaseSaving" class="w-3.5 h-3.5 border-2 border-primary-foreground/30 rounded-full border-t-primary-foreground animate-spin mr-1.5"></span>
            {{ editingShowcase ? '保存' : '创建' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { toast } from 'vue-sonner'
import api from '../../api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { CalendarDate } from '@internationalized/date'

const loading = ref(true)
const saving = ref(false)

const uploadControlMode = ref('whitelist')
const allowedExtensionsStr = ref('')
const blockedExtensionsStr = ref('')
const extensionsStr = computed({
  get: () => uploadControlMode.value === 'blacklist' ? blockedExtensionsStr.value : allowedExtensionsStr.value,
  set: (val: string) => {
    if (uploadControlMode.value === 'blacklist') blockedExtensionsStr.value = val
    else allowedExtensionsStr.value = val
  },
})
const maxSizeValue = ref(1024)
const maxSizeUnit = ref('1073741824')
const maxFilesPerTask = ref(100)
const maxTaskSizeValue = ref(5)
const maxTaskSizeUnit = ref('1073741824')
const expiryOptions = ref<{ value: number; label: string }[]>([])
const dlOptions = ref<{ value: number; label: string }[]>([])
const expiryDefaultIndex = ref(0)
const dlDefaultIndex = ref(0)
const cleanupInterval = ref(10)
const autoDeepClean = ref(false)
const autoDeepCleanDelay = ref(0)

// Showcase tasks state
interface ShowcaseTask {
  id: number
  name: string
  image_url: string
  stored_filename: string
  is_active: boolean
  valid_from: string
  valid_until: string
  sort_order: number
}
const showcaseTasks = ref<ShowcaseTask[]>([])
const showcaseDialogOpen = ref(false)
const showcaseSaving = ref(false)
const editingShowcase = ref<ShowcaseTask | null>(null)
const showcaseFileInputRef = ref<HTMLInputElement | null>(null)
const showcaseForm = reactive({
  name: '',
  file: null as File | null,
  preview: '',
  valid_from: '',
  valid_until: '',
})

// Calendar date helpers
function stringToCalendarDate(dateStr: string): CalendarDate | undefined {
  if (!dateStr) return undefined
  const parts = dateStr.split('-')
  if (parts.length !== 3) return undefined
  return new CalendarDate(parseInt(parts[0]), parseInt(parts[1]), parseInt(parts[2]))
}

function calendarDateToString(cd: CalendarDate): string {
  const y = cd.year
  const m = String(cd.month).padStart(2, '0')
  const d = String(cd.day).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function getDefaultValidFrom(): string {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function getDefaultValidUntil(): string {
  const d = new Date()
  d.setDate(d.getDate() + 30)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

// Add form states for options
const showExpiryAdd = ref(false)
const newExpiryNum = ref(1)
const newExpiryUnit = ref('hours')
const showDlAdd = ref(false)
const newDlNum = ref(1)
const newDlUnit = ref('times')

const UNIT_SECONDS: Record<string, number> = {
  minutes: 60,
  hours: 3600,
  days: 86400,
}

function secondsToLabel(seconds: number): string {
  if (seconds % 86400 === 0) return `${seconds / 86400}天`
  if (seconds % 3600 === 0) return `${seconds / 3600}小时`
  return `${seconds / 60}分钟`
}

function unitToSeconds(numValue: number, unit: string): number {
  return numValue * (UNIT_SECONDS[unit] || 60)
}

function moveExpiryOption(index: number, direction: -1 | 1) {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= expiryOptions.value.length) return
  const temp = expiryOptions.value[index]
  expiryOptions.value[index] = expiryOptions.value[newIndex]
  expiryOptions.value[newIndex] = temp
}

function moveDlOption(index: number, direction: -1 | 1) {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= dlOptions.value.length) return
  const temp = dlOptions.value[index]
  dlOptions.value[index] = dlOptions.value[newIndex]
  dlOptions.value[newIndex] = temp
}

function confirmAddExpiry() {
  if (newExpiryNum.value < 1) {
    toast.warning('请输入有效的数值')
    return
  }
  const seconds = unitToSeconds(newExpiryNum.value, newExpiryUnit.value)
  const label = `${newExpiryNum.value}${newExpiryUnit.value === 'minutes' ? '分钟' : newExpiryUnit.value === 'hours' ? '小时' : '天'}`
  expiryOptions.value.push({ value: seconds, label })
  showExpiryAdd.value = false
  newExpiryNum.value = 1
  newExpiryUnit.value = 'hours'
  toast.success(`已添加: ${label}`)
}

function confirmAddDl() {
  if (newDlUnit.value === 'unlimited') {
    if (dlOptions.value.some(o => o.value === -1)) {
      toast.warning('已存在"不限次数"选项')
      return
    }
    dlOptions.value.push({ value: -1, label: '不限次数' })
  } else {
    if (newDlNum.value < 1) {
      toast.warning('请输入有效的次数')
      return
    }
    dlOptions.value.push({ value: newDlNum.value, label: `${newDlNum.value}次` })
  }
  showDlAdd.value = false
  newDlNum.value = 1
  newDlUnit.value = 'times'
}

function setDefaultExpiry(index: number) {
  const option = expiryOptions.value[index]
  if (!option) return
  expiryDefaultIndex.value = index
  toast.success(`已将 ${option.label} 设为默认`)
}

function setDefaultDl(index: number) {
  const option = dlOptions.value[index]
  if (!option) return
  dlDefaultIndex.value = index
  toast.success(`已将 ${option.value === -1 ? '不限次数' : option.label} 设为默认`)
}

// Showcase task functions
async function loadShowcaseTasks() {
  try {
    const res = await api.get('/admin/showcases')
    showcaseTasks.value = res.data.tasks || []
  } catch {
    showcaseTasks.value = []
  }
}

function openShowcaseDialog(task: ShowcaseTask | null) {
  editingShowcase.value = task
  if (task) {
    showcaseForm.name = task.name
    showcaseForm.file = null
    showcaseForm.preview = task.image_url || ''
    showcaseForm.valid_from = task.valid_from ? task.valid_from.slice(0, 10) : ''
    showcaseForm.valid_until = task.valid_until ? task.valid_until.slice(0, 10) : ''
  } else {
    showcaseForm.name = ''
    showcaseForm.file = null
    showcaseForm.preview = ''
    showcaseForm.valid_from = getDefaultValidFrom()
    showcaseForm.valid_until = getDefaultValidUntil()
  }
  showcaseDialogOpen.value = true
}

function onShowcaseFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  showcaseForm.file = file
  const reader = new FileReader()
  reader.onload = (e) => {
    showcaseForm.preview = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

function moveShowcaseTask(index: number, direction: -1 | 1) {
  const task = showcaseTasks.value[index]
  api.post(`/admin/showcases/${task.id}/sort?direction=${direction}`).then(() => {
    loadShowcaseTasks()
  }).catch(() => {
    toast.error('排序失败')
  })
}

async function saveShowcaseTask() {
  if (!showcaseForm.name.trim()) {
    toast.warning('请输入任务名称')
    return
  }
  showcaseSaving.value = true
  try {
    const formData = new FormData()
    formData.append('name', showcaseForm.name.trim())
    if (showcaseForm.file) {
      formData.append('file', showcaseForm.file)
    }
    if (showcaseForm.valid_from) {
      formData.append('valid_from', showcaseForm.valid_from)
    }
    if (showcaseForm.valid_until) {
      formData.append('valid_until', showcaseForm.valid_until)
    }

    if (editingShowcase.value) {
      await api.put(`/admin/showcases/${editingShowcase.value.id}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      toast.success('任务已更新')
    } else {
      await api.post('/admin/showcases', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      toast.success('任务已创建')
    }
    showcaseDialogOpen.value = false
    await loadShowcaseTasks()
  } catch (err: any) {
    toast.error(err.response?.data?.detail || '操作失败')
  } finally {
    showcaseSaving.value = false
  }
}

async function deleteShowcaseTask() {
  if (!editingShowcase.value) return
  try {
    await api.delete(`/admin/showcases/${editingShowcase.value.id}`)
    toast.success('任务已删除')
    showcaseDialogOpen.value = false
    await loadShowcaseTasks()
  } catch (err: any) {
    toast.error(err.response?.data?.detail || '删除失败')
  }
}

onMounted(async () => {
  try {
    const res = await api.get('/admin/settings')
    const d = res.data
    uploadControlMode.value = d.upload_control_mode || 'whitelist'
    allowedExtensionsStr.value = (d.allowed_extensions || []).join('\n')
    const defaultBlocked = ['exe','msi','bat','cmd','sh','ps1','vbs','com','scr','pif','js','php','asp','jsp','py','rb','pl','dll','sys','drv','ocx','cpl','docm','xlsm','pptm']
    blockedExtensionsStr.value = (d.blocked_extensions && d.blocked_extensions.length > 0) ? d.blocked_extensions.join('\n') : defaultBlocked.join('\n')
    const bytes = d.max_upload_size_bytes
    if (bytes >= 1073741824) { maxSizeValue.value = Math.round(bytes / 1073741824); maxSizeUnit.value = '1073741824' }
    else if (bytes >= 1048576) { maxSizeValue.value = Math.round(bytes / 1048576); maxSizeUnit.value = '1048576' }
    else if (bytes >= 1024) { maxSizeValue.value = Math.round(bytes / 1024); maxSizeUnit.value = '1024' }
    else { maxSizeValue.value = bytes; maxSizeUnit.value = '1' }
    maxFilesPerTask.value = d.max_files_per_task || 100
    const taskBytes = d.max_task_size_bytes || 5368709120
    if (taskBytes >= 1073741824) { maxTaskSizeValue.value = Math.round(taskBytes / 1073741824); maxTaskSizeUnit.value = '1073741824' }
    else { maxTaskSizeValue.value = Math.round(taskBytes / 1048576); maxTaskSizeUnit.value = '1048576' }
    expiryOptions.value = d.expiry_options.map((o: any) => ({ value: o.value, label: o.label }))
    dlOptions.value = d.download_limit_options.map((o: any) => ({ value: o.value, label: o.label }))
    expiryDefaultIndex.value = d.expiry_default_index ?? 0
    dlDefaultIndex.value = d.dl_default_index ?? 0
    cleanupInterval.value = d.cleanup_scan_interval_min
    autoDeepClean.value = d.auto_deep_clean_enabled
    autoDeepCleanDelay.value = d.auto_deep_clean_delay_min
    await loadShowcaseTasks()
  } catch { toast.error('加载设置失败') }
  finally { loading.value = false }
})

async function save() {
  saving.value = true
  try {
    await api.put('/admin/settings', {
      upload_control_mode: uploadControlMode.value,
      allowed_extensions: uploadControlMode.value === 'blacklist' ? [] : allowedExtensionsStr.value.split('\n').map((s) => s.trim()).filter(Boolean),
      blocked_extensions: uploadControlMode.value === 'blacklist' ? blockedExtensionsStr.value.split('\n').map((s) => s.trim()).filter(Boolean) : [],
      max_upload_size_bytes: maxSizeValue.value * Number(maxSizeUnit.value),
      max_files_per_task: maxFilesPerTask.value,
      max_task_size_bytes: maxTaskSizeValue.value * Number(maxTaskSizeUnit.value),
      expiry_options: expiryOptions.value,
      download_limit_options: dlOptions.value,
      cleanup_scan_interval_min: cleanupInterval.value,
      auto_deep_clean_enabled: autoDeepClean.value,
      auto_deep_clean_delay_min: autoDeepCleanDelay.value,
      expiry_default_index: expiryDefaultIndex.value,
      dl_default_index: dlDefaultIndex.value,
      banner_image_url: '',
      banner_valid_from: '',
      banner_valid_until: '',
    })
    toast.success('设置已保存')
  } catch (err: any) { toast.error(err.response?.data?.detail || '保存失败') }
  finally { saving.value = false }
}
</script>
