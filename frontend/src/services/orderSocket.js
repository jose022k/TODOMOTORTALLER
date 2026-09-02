const RECONNECT_DELAY = 5000
const MAX_RECONNECT_ATTEMPTS = 5

let ws = null
let reconnectTimer = null
let pingTimer = null
let enabled = false
let reconnectAttempts = 0

function getWebSocketUrl() {
  const token = localStorage.getItem('access_token')
  if (!token) return null
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  return `${protocol}//${host}/socket/orders?token=${encodeURIComponent(token)}`
}

function onOpen() {
  reconnectAttempts = 0
  clearInterval(pingTimer)
  pingTimer = setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send('ping')
    }
  }, 25000)
}

function onClose(event) {
  clearInterval(pingTimer)
  // Code 4001 or 4003 means auth rejected by backend → stop reconnecting
  if (event && (event.code === 4001 || event.code === 4003)) {
    enabled = false
    return
  }
  if (enabled && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
    reconnectAttempts++
    clearTimeout(reconnectTimer)
    reconnectTimer = setTimeout(doConnect, RECONNECT_DELAY)
  }
}

function onMessage(event) {
  if (event.data === 'pong') return
  try {
    const data = JSON.parse(event.data)
    if (data && data.tipo === 'notificacion_creada' && data.notificacion) {
      window.dispatchEvent(new CustomEvent('notification-new', { detail: data.notificacion }))
      window.dispatchEvent(new CustomEvent('order-updated', { detail: data.notificacion }))
    } else if (data) {
      window.dispatchEvent(new CustomEvent('order-updated', { detail: data }))
    }
  } catch (e) {
    /* ignore parse error */
  }
}

function doConnect() {
  if (!enabled) return
  if (ws && (ws.readyState === WebSocket.CONNECTING || ws.readyState === WebSocket.OPEN)) {
    return
  }
  const url = getWebSocketUrl()
  if (!url) return
  try {
    ws = new WebSocket(url)
    ws.onopen = onOpen
    ws.onclose = onClose
    ws.onmessage = onMessage
    ws.onerror = () => {}
  } catch (e) {
    if (enabled && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++
      clearTimeout(reconnectTimer)
      reconnectTimer = setTimeout(doConnect, RECONNECT_DELAY)
    }
  }
}

function enable() {
  if (enabled && ws && (ws.readyState === WebSocket.CONNECTING || ws.readyState === WebSocket.OPEN)) return
  enabled = true
  reconnectAttempts = 0
  doConnect()
}

function disable() {
  enabled = false
  reconnectAttempts = 0
  clearTimeout(reconnectTimer)
  clearInterval(pingTimer)
  if (ws) {
    ws.onclose = null
    ws.close()
    ws = null
  }
}

function reconnect() {
  if (ws && ws.readyState === WebSocket.OPEN) return
  disable()
  enabled = true
  reconnectAttempts = 0
  doConnect()
}

export default { enable, disable, reconnect }
