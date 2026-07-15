export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return (bytes / Math.pow(1024, i)).toFixed(i === 0 ? 0 : 2) + ' ' + units[i]
}

export function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = date.getTime() - now.getTime()
  const diffSec = Math.floor(diffMs / 1000)

  if (diffSec < 0) return '已过期'

  const days = Math.floor(diffSec / 86400)
  const hours = Math.floor((diffSec % 86400) / 3600)
  const minutes = Math.floor((diffSec % 3600) / 60)

  if (days > 0) return `${days}天${hours}小时后过期`
  if (hours > 0) return `${hours}小时${minutes}分钟后过期`
  if (minutes > 0) return `${minutes}分钟后过期`
  return '即将过期'
}

export function formatDateTime(dateStr: string): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', {
    timeZone: 'UTC',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

export function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', {
    timeZone: 'UTC',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

export function formatTime(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleTimeString('zh-CN', {
    timeZone: 'UTC',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

export function formatDateTimeLocal(dateStr: string): string {
  if (!dateStr) return '-'
  // For datetime-local input: format as YYYY-MM-DDTHH:MM
  const d = new Date(dateStr)
  const year = d.getUTCFullYear()
  const month = String(d.getUTCMonth() + 1).padStart(2, '0')
  const day = String(d.getUTCDate()).padStart(2, '0')
  const hours = String(d.getUTCHours()).padStart(2, '0')
  const minutes = String(d.getUTCMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

export function parseUserAgent(ua: string): { browser: string; os: string } {
  if (!ua) return { browser: '-', os: '-' }
  let browser = '-'
  if (ua.includes('Firefox/')) browser = 'Firefox ' + ua.match(/Firefox\/([\d.]+)/)?.[1] || ''
  else if (ua.includes('Edg/')) browser = 'Edge ' + ua.match(/Edg\/([\d.]+)/)?.[1] || ''
  else if (ua.includes('Chrome/')) browser = 'Chrome ' + ua.match(/Chrome\/([\d.]+)/)?.[1] || ''
  else if (ua.includes('Safari/') && ua.includes('Version/')) browser = 'Safari ' + ua.match(/Version\/([\d.]+)/)?.[1] || ''

  let os = '-'
  if (ua.includes('Windows NT 10')) os = 'Windows 10/11'
  else if (ua.includes('Windows NT 6.3')) os = 'Windows 8.1'
  else if (ua.includes('Mac OS X')) os = 'macOS'
  else if (ua.includes('Linux')) os = 'Linux'
  else if (ua.includes('Android')) os = 'Android'
  else if (ua.includes('iPhone') || ua.includes('iPad')) os = 'iOS'

  return { browser, os }
}
