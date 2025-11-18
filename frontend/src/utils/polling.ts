import { onBeforeUnmount, ref } from "vue"

export function usePolling(callback: () => void | Promise<void>, interval = 3000) {
  const timerId = ref<number | null>(null)
  const isActive = ref(false)
  let running = false

  const tick = async () => {
    if (running) return
    running = true
    try {
      await callback()
    } finally {
      running = false
    }
  }

  const start = () => {
    if (timerId.value !== null) return
    timerId.value = window.setInterval(tick, interval)
    isActive.value = true
  }

  const stop = () => {
    if (timerId.value === null) return
    clearInterval(timerId.value)
    timerId.value = null
    isActive.value = false
  }

  onBeforeUnmount(stop)

  return {
    start,
    stop,
    isActive,
  }
}