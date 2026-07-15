<script lang="ts" setup>
import { ref, watch } from 'vue'
import { getLocalTimeZone, today, toCalendarDateTime, ZonedDateTime } from '@internationalized/date'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Button } from '@/components/ui/button'

const props = withDefaults(defineProps<{
  modelValue?: string
  placeholder?: string
  granularity?: 'day' | 'hour' | 'minute'
}>(), {
  placeholder: '选择日期',
  granularity: 'day',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const open = ref(false)
const selectedDate = ref<any>(null)

// Parse initial value
function parseDate(val: string): any {
  if (!val) return null
  try {
    // Parse as UTC date
    const match = val.match(/^(\d{4})-(\d{2})-(\d{2})/)
    if (!match) return null
    return today(getLocalTimeZone()).set({
      year: parseInt(match[1]),
      month: parseInt(match[2]),
      day: parseInt(match[3]),
    })
  } catch { return null }
}

selectedDate.value = parseDate(props.modelValue || '')

function formatDisplay(): string {
  if (!selectedDate.value) return props.placeholder
  // Use UTC methods to match the stored date
  const y = selectedDate.value.year
  const m = String(selectedDate.value.month).padStart(2, '0')
  const d = String(selectedDate.value.day).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function onSelect(date: any) {
  selectedDate.value = date
  if (date) {
    // Use UTC to avoid timezone offset
    const iso = `${date.year}-${String(date.month).padStart(2, '0')}-${String(date.day).padStart(2, '0')}T00:00:00Z`
    emit('update:modelValue', iso)
  } else {
    emit('update:modelValue', '')
  }
  open.value = false
}

watch(() => props.modelValue, (val) => {
  selectedDate.value = parseDate(val || '')
})
</script>

<template>
  <Popover v-model:open="open">
    <PopoverTrigger as-child>
      <Button variant="outline" class="w-[160px] justify-start text-left font-normal h-10">
        <svg class="w-4 h-4 mr-2 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        <span :class="selectedDate ? '' : 'text-muted-foreground'">{{ formatDisplay() }}</span>
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-auto p-0" align="start">
      <Calendar
        :model-value="selectedDate"
        @update:model-value="onSelect"
        initial-focus
      />
    </PopoverContent>
  </Popover>
</template>
