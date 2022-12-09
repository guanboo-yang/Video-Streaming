export const getRelativeTime = (date: string) => {
  const formatter = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })
  const diff = Date.now() - new Date(date).getTime()
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  const weeks = Math.floor(days / 7)
  const months = Math.floor(days / 30)
  const years = Math.floor(months / 12)
  if (years) return formatter.format(-years, 'year')
  if (months) return formatter.format(-months, 'month')
  if (weeks) return formatter.format(-weeks, 'week')
  if (days) return formatter.format(-days, 'day')
  if (hours) return formatter.format(-hours, 'hour')
  if (minutes) return formatter.format(-minutes, 'minute')
  return formatter.format(-seconds, 'second')
}
