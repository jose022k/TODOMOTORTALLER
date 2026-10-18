const RECONNECT_DELAY = 5000
const MAX_RECONNECT_ATTEMPTS = 5
const PING_INTERVALO = 15000

// Eventos que sí cambian el estado de la lista de órdenes.
// Todo lo demás (mensajes del chat, evidencias, presencia, notificaciones
// de campanita) NO debe recargar el panel.
const ORDER_EVENTS = [
  'orden_creada',
  'orden_en_proceso',
  'orden_completada',
  'orden_cancelada',
  'orden_actualizada',
  'visibility_restore',
]

export function esEventoDeOrden(tipo) {
  return ORDER_EVENTS.includes(tipo)
}

export function ordenIdDe(detalle) {
  // Los eventos de orden traen "order_id"; las notificaciones traen "orden_servicio_id"
  if (!detalle) return null
  return detalle.order_id ?? detalle.orden_servicio_id ?? null
}

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
  }, PING_INTERVALO)
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
    if (!data || !data.tipo) return

    // Notificación de campanita: SOLO alimenta el contador, nunca recarga la lista
    if (data.tipo === 'notificacion_creada') {
      if (data.notificacion) {
        window.dispatchEvent(new CustomEvent('notification-new', { detail: data.notificacion }))
      }
      return
    }

    // Alguien escribió/borró un mensaje o una evidencia en el chat de una orden
    if (data.tipo === 'chat_actualizado') {
      window.dispatchEvent(new CustomEvent('chat-actualizado', { detail: data }))
      return
    }

    // Un usuario se conectó o se desconectó (indicador "En línea")
    if (data.tipo === 'presencia') {
      window.dispatchEvent(new CustomEvent('presence-changed', { detail: data }))
      return
    }

    // Alguien está escribiendo en el chat de una orden
    if (data.tipo === 'escribiendo' || data.tipo === 'dejo_de_escribir') {
      window.dispatchEvent(new CustomEvent('typing', { detail: data }))
      return
    }

    // Eventos de orden: orden_creada, orden_en_proceso, orden_completada, ...
    // A diferencia del resto, éstos SÍ refrescan la lista de órdenes.
    window.dispatchEvent(new CustomEvent('order-updated', { detail: data }))
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

/** Corta el socket sin desactivar el modo "conectado" (se puede reconectar). */
function cerrarSocket() {
  clearTimeout(reconnectTimer)
  clearInterval(pingTimer)
  reconnectAttempts = 0
  if (ws) {
    ws.onclose = null
    ws.onmessage = null
    ws.onerror = null
    try {
      ws.close()
    } catch (e) {
      /* noop */
    }
    ws = null
  }
}

/**
 * Avisa al servidor que alguien está escribiendo (o dejó de escribir) en el
 * chat de una orden. Se manda por el mismo socket, sin ninguna petición HTTP.
 */
export function avisarEscritura(ordenId, escribiendo) {
  if (!ordenId || !ws || ws.readyState !== WebSocket.OPEN) return
  try {
    ws.send(
      JSON.stringify({
        tipo: escribiendo ? 'escribiendo' : 'dejando_de_escribir',
        orden_id: ordenId,
      })
    )
  } catch (e) {
    /* noop */
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
  cerrarSocket()
}

function reconnect() {
  if (!enabled) return
  cerrarSocket()
  doConnect()
}

// ── "En línea" solo mientras el usuario está en el sistema ─────────────────
// Al cerrar la pestaña o la PWA el socket se corta de inmediato, así el
// indicador "En línea" del chat desaparece al instante en los demás equipos.
function alOcultarse() {
  if (!enabled) return
  cerrarSocket()
}

function alVolver() {
  if (enabled) reconnect()
}

if (typeof document !== 'undefined') {
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') alOcultarse()
    else alVolver()
  })
  window.addEventListener('pagehide', alOcultarse)
  window.addEventListener('beforeunload', alOcultarse)
}

export default { enable, disable, reconnect }
