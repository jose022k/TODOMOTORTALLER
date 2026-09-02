const RECONNECT_DELAY = 3000
const PING_INTERVAL = 25000

let ws = null
let reconnectTimer = null
let pingTimer = null
let enabled = false

function getWebSocketUrl() {
  const token = localStorage.getItem('access_token')
  if (!token) return null
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  return `${protocol}//${host}/socket/orders?token=${encodeURIComponent(token)}`
}

function onOpen() {
  clearInterval(pingTimer)
  pingTimer = setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send('ping')
    }
  }, PING_INTERVAL)
}

function onClose() {
  clearInterval(pingTimer)
  if (enabled) {
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
    console.error('[WS] Parse error', e)
  }
}

function doConnect() {
  if (!enabled) return
  const url = getWebSocketUrl()
  if (!url) return
  try {
    ws = new WebSocket(url)
    ws.onopen = onOpen
    ws.onclose = onClose
    ws.onmessage = onMessage
    ws.onerror = () => {}
  } catch (e) {
    reconnectTimer = setTimeout(doConnect, RECONNECT_DELAY)
  }
}

function enable() {
  if (enabled) return
  enabled = true
  doConnect()
}

function disable() {
  enabled = false
  clearTimeout(reconnectTimer)
  clearInterval(pingTimer)
  if (ws) {
    ws.onclose = null
    ws.close()
    ws = null
  }
}

function reconnect() {
  if (ws) {
    ws.onclose = null
    ws.close()
    ws = null
  }
  clearTimeout(reconnectTimer)
  clearInterval(pingTimer)
  if (enabled) {
    doConnect()
  }
}

export default { enable, disable, reconnect }
