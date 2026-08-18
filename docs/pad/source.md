# 源代码提交页（智能屏系统 buildingos.pad）

## 提交要求
- 提供源程序的连续前30页与连续后30页；不足60页需提供全部源代码
- 每页不少于50行
- 源代码中不得包含公司名称、个人名称、文件名称
- 源代码总数量需与申请表保持一致

## 前30页
以下为前30页的连续源代码片段（核心通信与状态管理逻辑）。

```
import mqtt from 'mqtt'
import { ref, type Ref } from 'vue'
import { MqttRouter, type MqttMessageHandler } from './mqttRouter'
import { getMqttConfig, isMockMode } from '@/config/servers'
import { topics, type SpaceContext } from './mqttTopics'

const router = new MqttRouter()
let client: mqtt.MqttClient | null = null

const subscribedTopics = new Set<string>()
const connectListeners: Array<() => void> = []
const disconnectListeners: Array<() => void> = []

export const isConnected: Ref<boolean> = ref(false)

function resolveClientId(): string | undefined {
  try {
    const raw = localStorage.getItem('initData')
    if (!raw) return undefined
    const data = JSON.parse(raw)
    const ctx: Partial<SpaceContext> = {
      spaceCode: data.spaceId || data.code,
      floorAreaCode: data.floorAreaCode,
      floorCode: data.floorCode,
      deviceCode: data.roomCode || data.roomId,
    }
    if (!ctx.spaceCode || !ctx.floorAreaCode || !ctx.floorCode) return undefined
    return `mroom_${ctx.spaceCode}_${ctx.floorAreaCode}_${ctx.floorCode}_${ctx.deviceCode ?? 'unbound'}`
  } catch {
    return undefined
  }
}

function doConnect(): void {
  const cfg = getMqttConfig()
  if (!cfg.url) {
    console.warn('[MQTT] No broker URL configured — running in mock mode')
    return
  }

  const clientId = resolveClientId()

  client = mqtt.connect(cfg.url, {
    clean: true,
    connectTimeout: 4000,
    reconnectPeriod: 1000,
    username: cfg.username || undefined,
    password: cfg.password || undefined,
  })

  client.on('error', (err: Error) => {
    console.error('[MQTT] Connection error:', err.message)
  })

  client.on('connect', () => {
    console.log('[MQTT] Connected, clientId:', client!.options.clientId)
    isConnected.value = true

    if (subscribedTopics.size > 0) {
      const topicList = Array.from(subscribedTopics)
      console.log('[MQTT] Re-subscribe topics:', topicList)
      client!.subscribe(topicList, (err) => {
        if (err) console.error('[MQTT] Re-subscribe error:', err)
        else console.log('[MQTT] Re-subscribe OK:', topicList.join(', '))
      })
    } else {
      console.log('[MQTT] Connected but no topics registered yet')
    }

    connectListeners.forEach((fn) => fn())
  })

  client.on('close', () => {
    console.log('[MQTT] Disconnected')
    isConnected.value = false
    disconnectListeners.forEach((fn) => fn())
  })

  client.on('offline', () => {
    console.log('[MQTT] Offline')
    isConnected.value = false
  })

  client.on('message', (topic: string, payload: Buffer) => {
    const raw = payload.toString()
    const matched = router.dispatch(topic, payload)
    console.log(`[MQTT] Message${matched ? '' : ' (NO HANDLER)'} ${topic}:`, raw.length > 300 ? `${raw.slice(0, 300)}…` : raw)
  })
}

export function connectMqtt(): void {
  if (client) return
  if (isMockMode()) {
    console.log('[MQTT] connectMqtt skipped — mock mode (no broker URL)')
    return
  }
  console.log('[MQTT] connectMqtt — connecting to', getMqttConfig().url)
  doConnect()
}

export function disconnectMqtt(): void {
  if (client) {
    // Set client to null first so the close handler doesn't auto-reconnect
    const c = client
    client = null
    c.end(true)
    subscribedTopics.clear()
    router.clear()
    isConnected.value = false
  }
}

export function subscribe(topic: string): void {
  if (isMockMode()) {
    console.log('[MQTT] subscribe skipped (mock mode):', topic)
    return
  }
  if (subscribedTopics.has(topic)) {
    console.log('[MQTT] subscribe skipped (duplicate):', topic)
    return
  }
  subscribedTopics.add(topic)

  if (client && isConnected.value) {
    client.subscribe(topic, (err) => {
      if (err) console.error(`[MQTT] Subscribe error for ${topic}:`, err)
      else console.log('[MQTT] Subscribe OK:', topic)
    })
  } else {
    console.log('[MQTT] subscribe queued (not connected yet):', topic)
  }
}

export function unsubscribe(topic: string): void {
  if (!subscribedTopics.has(topic)) {
    console.log('[MQTT] unsubscribe skipped (not subscribed):', topic)
    return
  }
  subscribedTopics.delete(topic)
  console.log('[MQTT] unsubscribe:', topic)

  if (client && isConnected.value) {
    client.unsubscribe(topic, undefined, (err) => {
      if (err) console.error(`[MQTT] Unsubscribe error for ${topic}:`, err)
      else console.log('[MQTT] Unsubscribe OK:', topic)
    })
  }
}

export function publish(topic: string, message: string | object): void {
  if (isMockMode() || !client) {
    console.log('[MQTT Mock] publish:', topic, message)
    return
  }
  const payload = typeof message === 'string' ? message : JSON.stringify(message)
  console.log('[MQTT] Publish:', topic, payload)
  client.publish(topic, payload, { qos: 0 }, (err) => {
    if (err) console.error(`[MQTT] Publish error for ${topic}:`, err)
  })
}

export function onMessage(topic: string, handler: MqttMessageHandler): () => void {
  return router.on(topic, handler)
}

export function offMessage(topic: string, handler: MqttMessageHandler): void {
  router.off(topic, handler)
}

export function onConnect(fn: () => void): () => void {
  connectListeners.push(fn)
  return () => {
    const idx = connectListeners.indexOf(fn)
    if (idx !== -1) connectListeners.splice(idx, 1)
  }
}

export function onDisconnect(fn: () => void): () => void {
  disconnectListeners.push(fn)
  return () => {
    const idx = disconnectListeners.indexOf(fn)
    if (idx !== -1) disconnectListeners.splice(idx, 1)
  }
}

export { topics }
export type { SpaceContext }

export type MqttMessageHandler = (payload: unknown, topic: string, raw: string) => void

function wildcardToRegex(topic: string): RegExp {
  // MQTT '#' matches zero or more levels, including the parent.
  // e.g. "sport/tennis/#" must match "sport/tennis" AND "sport/tennis/score".
  if (topic === '#') return /^.*$/

  const segments = topic.split('/')
  const escapeRegExp = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

  // # must be the final segment — handle it separately so the slash
  // before it becomes optional (zero levels = match the parent topic).
  if (segments[segments.length - 1] === '#') {
    const prefix = segments.slice(0, -1).map((seg) => {
      if (seg === '+') return '[^/]+'
      return escapeRegExp(seg)
    }).join('/')
    return new RegExp(`^${prefix}(?:/.*)?$`)
  }

  // No # wildcard — only single-level + wildcards possible.
  const regexStr = segments.map((seg) => {
    if (seg === '+') return '[^/]+'
    return escapeRegExp(seg)
  }).join('/')
  return new RegExp(`^${regexStr}$`)
}

export class MqttRouter {
  private exact = new Map<string, Set<MqttMessageHandler>>()
  private wildcards: Array<{ pattern: RegExp; handler: MqttMessageHandler }> = []

  on(topic: string, handler: MqttMessageHandler): () => void {
    if (topic.includes('#') || topic.includes('+')) {
      const entry = { pattern: wildcardToRegex(topic), handler }
      this.wildcards.push(entry)
      return () => {
        const idx = this.wildcards.indexOf(entry)
        if (idx !== -1) this.wildcards.splice(idx, 1)
      }
    }

    let handlers = this.exact.get(topic)
    if (!handlers) {
      handlers = new Set()
      this.exact.set(topic, handlers)
    }
    handlers.add(handler)
    return () => {
      handlers?.delete(handler)
      if (handlers && handlers.size === 0) this.exact.delete(topic)
    }
  }

  off(topic: string, handler: MqttMessageHandler): void {
    if (topic.includes('#') || topic.includes('+')) {
      this.wildcards = this.wildcards.filter(
        (w) => w.handler !== handler
      )
      return
    }

    const handlers = this.exact.get(topic)
    if (handlers) {
      handlers.delete(handler)
      if (handlers.size === 0) this.exact.delete(topic)
    }
  }

  dispatch(topic: string, raw: string | Buffer): boolean {
    const rawStr = typeof raw === 'string' ? raw : raw.toString()
    let payload: unknown = rawStr
    try {
      payload = JSON.parse(rawStr)
    } catch {
      // non-JSON payload, keep as string
    }

    let matched = false

    const exactHandlers = this.exact.get(topic)
    if (exactHandlers) {
      exactHandlers.forEach((h) => h(payload, topic, rawStr))
      matched = true
    }

    for (const { pattern, handler } of this.wildcards) {
      if (pattern.test(topic)) {
        handler(payload, topic, rawStr)
        matched = true
      }
    }

    return matched
  }

  clear(): void {
    this.exact.clear()
    this.wildcards.length = 0
  }
}

export interface SpaceContext {
  spaceCode: string
  floorAreaCode: string
  floorCode: string
  deviceCode: string
}

const IOT_STATUS = '/iot/status'
const IOT_ACTION = '/iot/action'

export const topics = {
  // --- Lighting ---
  lightStatus: (c: SpaceContext) =>
    `${IOT_STATUS}/light/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}/#`,
  lightAction: (c: SpaceContext) =>
    `${IOT_ACTION}/light/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}`,

  // --- Air Conditioner ---
  acStatus: (c: SpaceContext) =>
    `${IOT_STATUS}/airconditioning/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}/#`,
  acAction: (c: SpaceContext) =>
    `${IOT_ACTION}/airconditioning/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}`,

  // --- Air Quality Sensor ---
  airSensor: (c: SpaceContext) =>
    `${IOT_STATUS}/airsensor/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}/#`,
  // Legacy backend publishes to exact topic (no sub-path), no wildcard
  areaAirSensor: (c: SpaceContext) =>
    `${IOT_STATUS}/areaairsensor/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}`,
  // Outdoor weather
  outdoorWeather: () => '/wallpad/outside',

  // --- WC Occupancy Sensor ---
  wcSensor: (c: SpaceContext, room: string) =>
    `${IOT_STATUS}/wcsensor/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${room}/#`,

  // --- Human Presence Sensor (meeting rooms, per floor) ---
  humanSensorStatus: (c: SpaceContext) =>
    `${IOT_STATUS}/humensensor/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/#`,

  // --- Blinds / Curtains ---
  blindStatus: (c: SpaceContext) =>
    `${IOT_STATUS}/blind/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}/#`,
  blindAction: (c: SpaceContext) =>
    `${IOT_ACTION}/blind/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}`,

  // --- Fresh Air ---
  freshAirStatus: (c: SpaceContext) =>
    `${IOT_STATUS}/freshair/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}/#`,
  freshAirAction: (c: SpaceContext) =>
    `${IOT_ACTION}/freshair/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}`,

  // --- Socket / Power ---
  socketStatus: (c: SpaceContext) =>
    `${IOT_STATUS}/socket/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}/#`,
  socketAction: (c: SpaceContext) =>
    `${IOT_ACTION}/socket/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}`,

  // --- Door ---
  doorStatus: (c: SpaceContext) =>
    `${IOT_STATUS}/door/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}/#`,
  doorAction: (c: SpaceContext) =>
    `${IOT_ACTION}/door/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}`,

  // --- Screen / Display ---
  screenStatus: (c: SpaceContext) =>
    `${IOT_STATUS}/screen/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}/#`,
  screenAction: (c: SpaceContext) =>
    `${IOT_ACTION}/screen/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}`,

  // --- Camera ---
  cameraStatus: (c: SpaceContext) =>
    `${IOT_STATUS}/camera/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}/#`,
  cameraAction: (c: SpaceContext) =>
    `${IOT_ACTION}/camera/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}`,

  // --- Audio ---
  audioStatus: (c: SpaceContext) =>
    `${IOT_STATUS}/audio/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}/#`,
  audioAction: (c: SpaceContext) =>
    `${IOT_ACTION}/audio/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}`,

  // --- Matrix / Signal Switch ---
  matrixStatus: (c: SpaceContext) =>
    `${IOT_STATUS}/matrix/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}/#`,
  matrixAction: (c: SpaceContext) =>
    `${IOT_ACTION}/matrix/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}`,

  // --- Cleaning ---
  cleaningAction: (c: SpaceContext) =>
    `${IOT_ACTION}/cleaning/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}`,

  // --- Pad (device discovery / management) ---
  padAction: (c: SpaceContext) =>
    `${IOT_ACTION}/pad/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}`,

  // --- Device config (original protocol) ---
  deviceConfigGet: () => '/iot/setting/get/device',
  deviceConfigResponse: (c: SpaceContext) =>
    `/iot/setting/device/${c.spaceCode}/${c.floorAreaCode}/${c.floorCode}/${c.deviceCode}`,
} as const

import { onScopeDispose } from 'vue'
import {
  isConnected,
  subscribe as mqSubscribe,
  unsubscribe as mqUnsubscribe,
  publish as mqPublish,
  onMessage as mqOnMessage,
  offMessage as mqOffMessage,
  connectMqtt,
} from './mqtt'
import type { MqttMessageHandler } from './mqttRouter'

export function useMqtt() {
  const handlerPairs: Array<{ topic: string; handler: MqttMessageHandler }> = []
  const subscribedTopics = new Set<string>()

  connectMqtt()

  const subscribe = (topic: string): void => {
    subscribedTopics.add(topic)
    mqSubscribe(topic)
  }

  const unsubscribe = (topic: string): void => {
    subscribedTopics.delete(topic)
    mqUnsubscribe(topic)
  }

  const onMessage = (topic: string, handler: MqttMessageHandler): (() => void) => {
    mqOnMessage(topic, handler)
    const pair = { topic, handler }
    handlerPairs.push(pair)

    return () => {
      mqOffMessage(topic, handler)
      const idx = handlerPairs.indexOf(pair)
      if (idx !== -1) handlerPairs.splice(idx, 1)
    }
  }

  const offMessage = (topic: string, handler: MqttMessageHandler) => {
    mqOffMessage(topic, handler)
    const idx = handlerPairs.findIndex((p) => p.topic === topic && p.handler === handler)
    if (idx !== -1) handlerPairs.splice(idx, 1)
  }

  onScopeDispose(() => {
    for (const { topic, handler } of handlerPairs) {
      mqOffMessage(topic, handler)
    }
    handlerPairs.length = 0

    for (const topic of subscribedTopics) {
      mqUnsubscribe(topic)
    }
    subscribedTopics.clear()
  })

  return {
    isConnected,
    subscribe,
    unsubscribe,
    publish: mqPublish,
    onMessage,
    offMessage,
    connect: connectMqtt,
  }
}

import { publish, onMessage } from './mqtt'

interface PendingCommand {
  resolve: (value: unknown) => void
  reject: (reason: Error) => void
  timeout: ReturnType<typeof setTimeout>
}

const pending = new Map<string, PendingCommand>()

let correlationCounter = 0

export function sendCommand(
  topic: string,
  payload: Record<string, unknown>,
  responseTopic: string,
  { timeoutMs = 10_000 }: { timeoutMs?: number } = {}
): Promise<unknown> {
  const correlationId = `cmd_${Date.now()}_${++correlationCounter}`
  const data = { ...payload, correlationId }

  const unsubscribe = onMessage(responseTopic, (parsed, _topic) => {
    const msg = parsed as Record<string, unknown>
    if (msg.correlationId === correlationId) {
      const entry = pending.get(correlationId)
      if (entry) {
        clearTimeout(entry.timeout)
        pending.delete(correlationId)
        unsubscribe()
        entry.resolve(msg)
      }
    }
  })

  const promise = new Promise<unknown>((resolve, reject) => {
    const timeout = setTimeout(() => {
      pending.delete(correlationId)
      unsubscribe()
      reject(new Error(`Command timeout for ${topic}`))
    }, timeoutMs)

    pending.set(correlationId, { resolve, reject, timeout })
  })

  publish(topic, data)
  return promise
}

import axios from 'axios'
import { stringify } from 'qs'
import { ElMessage } from 'element-plus'
import { getServerConfig } from '@/config/servers'

const contentType = 'application/json;charset=UTF-8'
const timeout = 60000

const CODE_MESSAGE: Record<number, string> = {
  200: '服务器成功返回请求数据',
  201: '新建或修改数据成功',
  202: '一个请求已经进入后台排队(异步任务)',
  204: '删除数据成功',
  400: '发出信息有误',
  401: '用户没有权限(令牌失效、用户名、密码错误、登录过期)',
  402: '令牌过期',
  403: '用户得到授权，但是访问是被禁止的',
  404: '访问资源不存在',
  406: '请求格式不可得',
  410: '请求资源被永久删除，且不会被看到',
  500: '服务器发生错误',
  502: '网关错误',
  503: '服务不可用，服务器暂时过载或维护',
  504: '网关超时',
}

const instance = axios.create({
  timeout,
  headers: {
    'Content-Type': contentType,
  },
})

// Request Interceptor — resolve baseURL lazily per request
instance.interceptors.request.use(
  (config: any) => {
    if (!config.baseURL) {
      config.baseURL = getServerConfig().apiBaseUrl
    }
    if (config.data && config.headers['Content-Type'] === 'application/x-www-form-urlencoded;charset=UTF-8') {
      config.data = stringify(config.data)
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response Interceptor
instance.interceptors.response.use(
  (response) => {
    const { data } = response
    return data
  },
  (error) => {
    const { response } = error
    console.error('Request Error:', error)

    if (response && response.status) {
      const errorText = CODE_MESSAGE[response.status] || response.statusText
      const { status, url } = response

      ElMessage.error({
        message: `请求错误 ${status}: ${url}`,
        grouping: true,
        duration: 5000
      })

      if (CODE_MESSAGE[status]) {
         ElMessage.error({
             message: CODE_MESSAGE[status],
             grouping: true
         })
      }
    } else if (!response) {
      ElMessage.error('您的网络发生异常，无法连接服务器')
    }

    if (response === undefined) {
      console.error('Network Error: No response received')
      return Promise.reject(new Error('Network Error'))
    }
    return Promise.reject(response.data || error)
  }
)

export default instance

import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import type {
  LightDevice,
  LightState,
  AcState,
  AirSensorData,
  WcSensorData,
  HumanSensorData,
  BlindState,
  FreshAirState,
  SocketState,
  DoorState,
  ScreenState,
  CameraState,
  AudioState,
  MatrixState,
} from '@/types/device'
import {
  DEFAULT_LIGHT,
  DEFAULT_AC,
  DEFAULT_AIR_SENSOR,
  DEFAULT_BLIND,
  DEFAULT_FRESH_AIR,
} from '@/types/device'

export type DeviceDomain =
  | 'light'
  | 'ac'
  | 'airsensor'
  | 'wcsensor'
  | 'humansensor'
  | 'blind'
  | 'freshair'
  | 'socket'
  | 'door'
  | 'screen'
  | 'camera'
  | 'audio'
  | 'matrix'

function makeKey(ctx: { spaceCode: string; floorAreaCode: string; floorCode: string; deviceCode: string }, domain: DeviceDomain, sub?: string): string {
  const base = `${ctx.spaceCode}/${ctx.floorAreaCode}/${ctx.floorCode}/${ctx.deviceCode}/${domain}`
  return sub ? `${base}/${sub}` : base
}

export const useDeviceStore = defineStore('device', () => {
  // --- Ref counters ---
  const refCounts = reactive<Record<string, number>>({})

  function acquire(key: string): void {
    if (!(key in refCounts)) {
      refCounts[key] = 0
    }
    refCounts[key]++
  }

  function release(key: string): void {
    if (key in refCounts) {
      refCounts[key]--
      if (refCounts[key] <= 0) {
        delete refCounts[key]
        // Remove cached state
        lightMap.delete(key)
        acMap.delete(key)
        airSensorMap.delete(key)
        wcSensorMap.delete(key)
        humanSensorMap.delete(key)
        blindMap.delete(key)
        freshAirMap.delete(key)
      }
    }
  }

  function isAcquired(key: string): boolean {
    return (refCounts[key] ?? 0) > 0
  }

  // --- Domain State Caches ---
  const lightMap = reactive<Map<string, LightState>>(new Map())
  const acMap = reactive<Map<string, AcState>>(new Map())
  const airSensorMap = reactive<Map<string, AirSensorData>>(new Map())
  const wcSensorMap = reactive<Map<string, WcSensorData[]>>(new Map())
  const humanSensorMap = reactive<Map<string, HumanSensorData[]>>(new Map())
  const blindMap = reactive<Map<string, BlindState>>(new Map())
  const freshAirMap = reactive<Map<string, FreshAirState>>(new Map())
  const socketMap = reactive<Map<string, SocketState[]>>(new Map())
  const doorMap = reactive<Map<string, DoorState[]>>(new Map())

  // --- Getters (return reactive state, with mock fallback) ---
  function getLights(key: string) {
    if (!lightMap.has(key)) {
      lightMap.set(key, { ...DEFAULT_LIGHT, devices: [] })
    }
    return computed(() => lightMap.get(key)!)
  }

  function getAc(key: string) {
    if (!acMap.has(key)) {
      acMap.set(key, { ...DEFAULT_AC })
    }
    return computed(() => {
      const s = acMap.get(key)!
      if (!s.devices) s.devices = []
      return s
    })
  }

  function getAirSensor(key: string) {
    if (!airSensorMap.has(key)) {
      airSensorMap.set(key, { ...DEFAULT_AIR_SENSOR })
    }
    return computed(() => airSensorMap.get(key)!)
  }

  function getWcSensors(key: string) {
    if (!wcSensorMap.has(key)) {
      wcSensorMap.set(key, [])
    }
    return computed(() => wcSensorMap.get(key)!)
  }

  function getHumanSensors(key: string) {
    if (!humanSensorMap.has(key)) {
      humanSensorMap.set(key, [])
    }
    return computed(() => humanSensorMap.get(key)!)
  }

  function getBlind(key: string) {
    if (!blindMap.has(key)) {
      blindMap.set(key, { ...DEFAULT_BLIND })
    }
    return computed(() => {
      const s = blindMap.get(key)!
      if (!s.devices) s.devices = []
      return s
    })
  }

  function getFreshAir(key: string) {
    if (!freshAirMap.has(key)) {
      freshAirMap.set(key, { ...DEFAULT_FRESH_AIR })
    }
    return computed(() => freshAirMap.get(key)!)
  }

  function getSockets(key: string) {
    if (!socketMap.has(key)) {
      socketMap.set(key, [])
    }
    return computed(() => socketMap.get(key)!)
  }

  function getDoors(key: string) {
    if (!doorMap.has(key)) {
      doorMap.set(key, [])
    }
    return computed(() => doorMap.get(key)!)
  }

  // --- Write path (called from MQTT handlers) ---
  function applyLightState(key: string, data: Partial<LightState>): void {
    const current = lightMap.get(key) || { ...DEFAULT_LIGHT, devices: [] }
    lightMap.set(key, { ...current, ...data })
  }

  function applyAcState(key: string, data: Partial<AcState>): void {
    const current = acMap.get(key) || { ...DEFAULT_AC }
    acMap.set(key, { ...current, ...data })
  }

  function applyAirSensor(key: string, data: Partial<AirSensorData>): void {
    const current = airSensorMap.get(key) || { ...DEFAULT_AIR_SENSOR }
    airSensorMap.set(key, { ...current, ...data })
  }

  function applyWcSensor(key: string, data: WcSensorData[]): void {
    wcSensorMap.set(key, data)
  }

  function applyHumanSensors(key: string, data: HumanSensorData[]): void {
    humanSensorMap.set(key, data)
  }

  function applyBlindState(key: string, data: Partial<BlindState>): void {
    const current = blindMap.get(key) || { ...DEFAULT_BLIND }
    blindMap.set(key, { ...current, ...data })
  }

  function applyFreshAirState(key: string, data: Partial<FreshAirState>): void {
    const current = freshAirMap.get(key) || { ...DEFAULT_FRESH_AIR }
    freshAirMap.set(key, { ...current, ...data })
  }

  function applySockets(key: string, data: SocketState[]): void {
    socketMap.set(key, data)
  }

  function applyDoors(key: string, data: DoorState[]): void {
    doorMap.set(key, data)
  }

  return {
    refCounts,
    makeKey,
    acquire,
    release,
    isAcquired,
    getLights,
    getAc,
    getAirSensor,
    getWcSensors,
    getHumanSensors,
    getBlind,
    getFreshAir,
    getSockets,
    getDoors,
    applyLightState,
    applyAcState,
    applyAirSensor,
    applyWcSensor,
    applyHumanSensors,
    applyBlindState,
    applyFreshAirState,
    applySockets,
    applyDoors,
  }
})

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCockpitStore = defineStore('cockpit', () => {
  // --- UI State (always local) ---
  const background = ref<{ type: 'image' | 'video'; src: string }>({
    type: 'video',
    src: '/pad/video/snow.mp4',
  })

  const brightness = ref(80)

  const setBackground = (type: 'image' | 'video', src: string) => {
    background.value = { type, src }
  }

  // --- Device Mock Data (fallback when no MQTT backend) ---
  const lights = ref([
    { id: 'living', name: 'Living Room', isOn: true, icon: 'Lamp' },
    { id: 'kitchen', name: 'Kitchen', isOn: false, icon: 'ChefHat' },
    { id: 'office', name: 'Office', isOn: true, icon: 'Monitor' },
    { id: 'hall', name: 'Hallway', isOn: false, icon: 'Footprints' },
  ])

  const climate = ref({
    temperature: 24,
    isOn: true,
    mode: 'cool' as 'cool' | 'heat' | 'auto',
  })

  const environment = ref({
    indoorTemp: 23.5,
    humidity: 45,
    co2: 450,
    pm25: 12,
  })

  const toggleLight = (id: string) => {
    const light = lights.value.find((l) => l.id === id)
    if (light) light.isOn = !light.isOn
  }

  return {
    background,
    brightness,
    lights,
    climate,
    environment,
    setBackground,
    toggleLight,
  }
})

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getSpaceData } from '@/api/space'
import type { Space } from '@/types/space'
import type { SpaceContext } from '@/utils/mqttTopics'

export const useSpaceStore = defineStore('space', () => {
  const structure = ref<Space[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadStructure(): Promise<void> {
    if (structure.value.length > 0) return
    loading.value = true
    error.value = null
    try {
      structure.value = await getSpaceData()
    } catch (e: any) {
      error.value = e?.message ?? 'Failed to load structure'
      console.error('[SpaceStore] loadStructure failed:', e)
    } finally {
      loading.value = false
    }
  }

  const boundSpace = computed(() => {
    try {
      const raw = localStorage.getItem('initData')
      if (!raw) return null
      return JSON.parse(raw)
    } catch {
      return null
    }
  })

  const hasBinding = computed(() => {
    return !!(boundSpace.value?.spaceName && boundSpace.value?.padType)
  })

  const spaceContext = computed<SpaceContext | null>(() => {
    const b = boundSpace.value
    if (!b?.code && !b?.spaceId) return null
    return {
      spaceCode: b.code || String(b.spaceId),
      floorAreaCode: b.floorAreaCode || '',
      floorCode: b.floorCode || '',
      deviceCode: b.roomCode || String(b.roomId || ''),
    }
  })

  function bindSpace(config: Record<string, unknown>): void {
    const raw = localStorage.getItem('initData')
    const existing = raw ? JSON.parse(raw) : {}
    const merged = { ...existing, ...config }
    localStorage.setItem('initData', JSON.stringify(merged))
  }

  function clearBinding(): void {
    localStorage.removeItem('initData')
  }

  return {
    structure,
    loading,
    error,
    boundSpace,
    hasBinding,
    spaceContext,
    loadStructure,
    bindSpace,
    clearBinding,
  }
})

import request from '@/utils/request'
import type { Space } from '@/types/space'

export function getSpaceData(data: Record<string, unknown> = {}): Promise<Space[]> {
  return request({
    url: '/iot/setting/get/structure',
    method: 'post',
    data,
  })
}

import request from '@/utils/request'

export interface DeviceControlLog {
  spaceId?: string | number
  floorAreaId?: string | number
  floorId?: string | number
  deviceId?: string | number
  deviceType?: string
  action?: string
  value?: unknown
}

export function addDeviceControlLog(params: DeviceControlLog): Promise<void> {
  return request({
    url: '/api/device/doAddDeviceControlLog',
    method: 'post',
    data: params,
  })
}

export interface MqttConfig {
  url: string
  username: string
  password: string
}

export interface ServerConfig {
  apiBaseUrl: string
  mqtt: MqttConfig
}

function buildConfig(): ServerConfig {
  const mqttUrl = window.config?.VITE_MQTT_URL ?? import.meta.env.VITE_MQTT_URL ?? ''
  const mqttUser = window.config?.VITE_MQTT_USERNAME ?? import.meta.env.VITE_MQTT_USERNAME ?? ''
  const mqttPass = window.config?.VITE_MQTT_PASSWORD ?? import.meta.env.VITE_MQTT_PASSWORD ?? ''

  return {
    apiBaseUrl: window.config?.VITE_APP_BASE_URL ?? import.meta.env.VITE_APP_BASE_URL ?? '',
    mqtt: {
      url: mqttUrl,
      username: mqttUser,
      password: mqttPass,
    },
  }
}

let _config: ServerConfig | null = null

export function getServerConfig(): ServerConfig {
  if (!_config) {
    _config = buildConfig()
  }
  return _config
}

export function getMqttConfig(): MqttConfig {
  return getServerConfig().mqtt
}

export function isMockMode(): boolean {
  return !getServerConfig().mqtt.url
}

```

## 后30页
以下为后30页的连续源代码片段（页面组件）。

```
<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getSpaceData } from '@/api/space'
import { getTemplates } from '@/templates/registry'
import type { Space } from '@/types/space'

const router = useRouter()

const version = __APP_VERSION__

// ====== Password gate ======
const authenticated = ref(false)
const pwValue = ref('')
const pwError = ref('')

function derivePassword(): string {
  try {
    const raw = localStorage.getItem('initData')
    if (!raw) return '0000'
    const data = JSON.parse(raw)
    let pwd = (data.floorName || '').replace(/[^0-9]/g, '') || '00'
    if (pwd.length > 2) pwd = pwd.slice(0, 2)
    if (pwd.length === 1) pwd = '0' + pwd
    const code = data.code || ''
    const areaMap: Record<string, string> = { A: '01', B: '02', C: '03', D: '04' }
    let area = areaMap[code] || '00'
    if (data.type === 'tolite') area = '00'
    return pwd + area
  } catch { return '0000' }
}

watch(pwValue, (v) => {
  if (v.length === 4) {
    if (v === derivePassword()) { authenticated.value = true }
    else { pwError.value = '密码错误'; pwValue.value = '' }
  } else { pwError.value = '' }
})

const onNumClick = (d: string) => { if (pwValue.value.length < 4) pwValue.value += d }
const onNumDelete = () => { pwValue.value = pwValue.value.slice(0, -1) }

const kbKeys = [['1','2','3'],['4','5','6'],['7','8','9'],['','0','del']]

// --- Step state ---
const step = ref<'basic' | 'binding' | 'template'>('basic')

// --- Step 1: Basic config ---
const padType = ref('wallPad')
const ratio = ref('16:9')

const padTypes = [
  { label: 'Wall Pad (墙面中控)', value: 'wallPad' },
  { label: 'Tolite Pad (卫生间中控)', value: 'tolitePad' },
  { label: 'Room Control (独立房间中控)', value: 'roomControl' },
  { label: 'Meeting Control (会议室中控)', value: 'meetingControl' },
  { label: 'Door Pad (独立房间门屏)', value: 'doorPad' },
  { label: 'Digital Twin Screen (数字孪生大屏)', value: 'twins' },
  { label: 'Switch Pad (开关屏)', value: 'switchPad' },
]

const ratios = [
  { label: '16:9 (1920x1080)', value: '16:9' },
  { label: '16:10 (1920x1200)', value: '16:10' },
  { label: '16:9 (4K - 3840x2160)', value: '4k' },
  { label: '1:1 (640x640)', value: '1:1' },
]

const typeOptions = computed(() => {
  switch (padType.value) {
    case 'wallPad': return [{ label: '办公区域', value: 'area' }]
    case 'tolitePad': return [{ label: '卫生间', value: 'tolite' }]
    case 'roomControl':
    case 'doorPad': return [{ label: '独立房间', value: 'room' }]
    case 'switchPad': return [
      { label: '独立房间', value: 'room' },
      { label: '会议室', value: 'meetingRoom' },
    ]
    case 'meetingControl': return [{ label: '会议室', value: 'meetingRoom' }]
    default: return [
      { label: '会议室', value: 'meetingRoom' },
      { label: '独立房间', value: 'room' },
      { label: '办公区域', value: 'area' },
      { label: '卫生间', value: 'tolite' },
    ]
  }
})

// --- Step 2: Space binding ---
const spaceObj = ref<Space[]>([])
const loading = ref(false)
const errorMsg = ref('')

const form = reactive({
  spaceIndex: null as number | null,
  floorareaIndex: null as number | null,
  floorIndex: null as number | null,
  type: '',
  meetingRoomIndex: null as number | null,
  roomIndex: null as number | null,
  areaIndex: null as number | null,
  toiletIndex: null as number | null,
  companyName: '',
})

const canSave = computed(() => form.spaceIndex !== null)

const currentSpace = computed(() => {
  if (form.spaceIndex === null) return null
  return spaceObj.value[form.spaceIndex] ?? null
})

const currentFloorArea = computed(() => {
  if (!currentSpace.value || form.floorareaIndex === null) return null
  return currentSpace.value.floorArea[form.floorareaIndex] ?? null
})

const currentFloor = computed(() => {
  if (!currentFloorArea.value || form.floorIndex === null) return null
  return currentFloorArea.value.floor[form.floorIndex] ?? null
})

const goToBinding = async () => {
  step.value = 'binding'
  loading.value = true
  errorMsg.value = ''
  try {
    const data = await getSpaceData({})
    if (Array.isArray(data)) {
      spaceObj.value = data
      if (data.length === 1) {
        form.spaceIndex = 0
      }
    }
  } catch (e: any) {
    errorMsg.value = e?.message || '获取空间数据失败，请检查网络连接'
    console.error('[InitPage] Failed to fetch structure:', e)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  step.value = 'basic'
}

const handleSubmit = () => {
  const config: Record<string, unknown> = {
    padType: padType.value,
    ratio: ratio.value,
  }

  if (form.spaceIndex !== null && spaceObj.value[form.spaceIndex]) {
    const space = spaceObj.value[form.spaceIndex]
    config.spaceId = space.id
    config.spaceName = space.name
    config.code = space.code

    if (form.floorareaIndex !== null && space.floorArea[form.floorareaIndex]) {
      const floorArea = space.floorArea[form.floorareaIndex]
      config.floorAreaId = floorArea.id
      config.floorAreaName = floorArea.name
      config.floorAreaCode = floorArea.code

      if (form.floorIndex !== null && floorArea.floor[form.floorIndex]) {
        const floor = floorArea.floor[form.floorIndex]
        config.floorId = floor.id
        config.floorName = floor.name
        config.floorCode = floor.code
        config.type = form.type

        const roomKey = form.type === 'meetingRoom' ? 'mettingRoom' : form.type
        const roomIndex = form.type === 'meetingRoom' ? form.meetingRoomIndex
          : form.type === 'room' ? form.roomIndex
          : form.type === 'area' ? form.areaIndex
          : form.type === 'tolite' ? form.toiletIndex
          : null

        const roomList = (floor as any)[roomKey]
        if (roomIndex !== null && roomList?.[roomIndex]) {
          const room = roomList[roomIndex]
          config.roomId = room.id
          config.roomName = room.name
          config.roomCode = room.code
        }

        if (form.type === 'room' && form.companyName) {
          config.companyName = form.companyName
        }
      }
    }
  }

  localStorage.setItem('initData', JSON.stringify(config))
  step.value = 'template'
}

// --- Step 3: Template selection ---
const selectedTemplate = ref('default')
const templateList = computed(() => getTemplates(padType.value))

const handleConfirmTemplate = () => {
  try {
    const raw = localStorage.getItem('initData')
    const data = raw ? JSON.parse(raw) : {}
    data.template = selectedTemplate.value
    localStorage.setItem('initData', JSON.stringify(data))
  } catch { /* ignore */ }
  router.push('/' + padType.value)
}
</script>

<template>
  <div class="w-full h-full flex items-center justify-center bg-black text-white">
    <!-- Password gate -->
    <div v-if="!authenticated" class="w-[450px] bg-[#1a1a1a] p-8 rounded-2xl border border-white/10">
      <div class="pw-title">系统管理</div>
      <div class="pw-label">输入管理员密码：</div>
      <div class="pw-input-row">
        <div v-for="i in 4" :key="i" class="pw-dot" :class="{ active: pwValue.length >= i, error: pwError }"></div>
      </div>
      <div class="pw-error">{{ pwError }}</div>
      <div class="pw-keyboard">
        <div v-for="(row, ri) in kbKeys" :key="ri" class="pw-kb-row">
          <div v-for="key in row" :key="key" class="pw-kb-key" :class="{ empty: !key, del: key === 'del' }"
            @click="key === 'del' ? onNumDelete() : key ? onNumClick(key) : null">
            <template v-if="key === 'del'">
              <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 4H8l-7 8 7 8h13a2 2 0 002-2V6a2 2 0 00-2-2z"/><line x1="18" y1="9" x2="12" y2="15"/><line x1="12" y1="9" x2="18" y2="15"/></svg>
            </template>
            <template v-else>{{ key }}</template>
          </div>
        </div>
      </div>
      <div class="mt-4 text-center text-gray-500 text-xs">v{{ version }}</div>
    </div>

    <!-- Init content -->
    <template v-else>
    <!-- Step 1: Basic -->
    <div v-if="step === 'basic'" class="w-[500px] bg-[#1a1a1a] p-8 rounded-2xl border border-white/10">
      <h2 class="text-2xl font-bold mb-6 text-center">初始化平板设置</h2>

      <el-form label-position="top">
        <el-form-item label="平板场景类型">
          <el-select v-model="padType" placeholder="请选择场景类型" class="w-full">
            <el-option
              v-for="item in padTypes"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="屏幕比例">
          <el-radio-group v-model="ratio">
            <el-radio
              v-for="item in ratios"
              :key="item.value"
              :value="item.value"
              border
              class="!mr-4 !mb-2"
            >
              {{ item.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <div class="mt-8">
          <el-button type="primary" size="large" @click="goToBinding" class="w-full">
            下一步：绑定空间
          </el-button>
        </div>
      </el-form>

      <div class="mt-4 text-center text-gray-500 text-xs">v{{ version }}</div>
    </div>

    <!-- Step 2: Space Binding -->
    <div v-else-if="step === 'binding'" class="w-[600px] bg-[#1a1a1a] p-8 rounded-2xl border border-white/10 max-h-[90vh] overflow-y-auto">
      <h2 class="text-2xl font-bold mb-2 text-center">绑定空间位置</h2>
      <p class="text-gray-400 text-sm text-center mb-6">选择本设备所在的物理空间</p>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-12">
        <el-icon class="is-loading text-3xl text-blue-400"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg></el-icon>
      </div>

      <!-- Error -->
      <div v-else-if="errorMsg" class="text-center py-8">
        <p class="text-red-400 mb-4">{{ errorMsg }}</p>
        <el-button @click="goBack">返回上一步</el-button>
        <el-button @click="goToBinding">重试</el-button>
      </div>

      <!-- Cascading Selectors -->
      <el-form v-else :model="form" label-position="top">
        <el-form-item label="属地">
          <el-select v-model="form.spaceIndex" placeholder="选择属地" class="w-full">
            <el-option :label="s.name" :value="i" v-for="(s, i) in spaceObj" :key="i" />
          </el-select>
        </el-form-item>

        <el-form-item label="楼层区域" v-if="currentSpace">
          <el-select v-model="form.floorareaIndex" placeholder="选择楼层区域" class="w-full">
            <el-option :label="fa.name" :value="i" v-for="(fa, i) in currentSpace.floorArea" :key="i" />
          </el-select>
        </el-form-item>

        <el-form-item label="楼层" v-if="currentFloorArea">
          <el-select v-model="form.floorIndex" placeholder="选择楼层" class="w-full">
            <el-option :label="f.name" :value="i" v-for="(f, i) in currentFloorArea.floor" :key="i" />
          </el-select>
        </el-form-item>

        <el-form-item label="绑定类型" v-if="currentFloor">
          <el-select v-model="form.type" placeholder="选择类型" class="w-full">
            <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>

        <!-- Meeting Room -->
        <el-form-item label="绑定会议室" v-if="currentFloor && form.type === 'meetingRoom' && currentFloor.mettingRoom?.length">
          <el-select v-model="form.meetingRoomIndex" placeholder="选择会议室" class="w-full">
            <el-option :label="r.name" :value="i" v-for="(r, i) in currentFloor.mettingRoom" :key="i" />
          </el-select>
        </el-form-item>

        <!-- Room -->
        <el-form-item label="绑定房间" v-if="currentFloor && form.type === 'room' && currentFloor.room?.length">
          <el-select v-model="form.roomIndex" placeholder="选择房间" class="w-full">
            <el-option :label="r.name" :value="i" v-for="(r, i) in currentFloor.room" :key="i" />
          </el-select>
        </el-form-item>

        <el-form-item label="绑定公司" v-if="currentFloor && form.type === 'room' && currentSpace?.company?.length && form.roomIndex !== null">
          <el-select v-model="form.companyName" placeholder="选择公司" class="w-full">
            <el-option :label="c.orgName" :value="c.orgName" v-for="(c, i) in currentSpace.company" :key="i" />
          </el-select>
        </el-form-item>

        <!-- Area -->
        <el-form-item label="绑定区域" v-if="currentFloor && form.type === 'area' && currentFloor.area?.length">
          <el-select v-model="form.areaIndex" placeholder="选择区域" class="w-full">
            <el-option :label="a.name" :value="i" v-for="(a, i) in currentFloor.area" :key="i" />
          </el-select>
        </el-form-item>

        <!-- Toilet -->
        <el-form-item label="绑定卫生间" v-if="currentFloor && form.type === 'tolite' && currentFloor.toilet?.length">
          <el-select v-model="form.toiletIndex" placeholder="选择卫生间" class="w-full">
            <el-option :label="t.name" :value="i" v-for="(t, i) in currentFloor.toilet" :key="i" />
          </el-select>
        </el-form-item>

        <div class="flex gap-4 mt-8">
          <el-button size="large" @click="goBack" class="flex-1">返回</el-button>
          <el-button type="primary" size="large" @click="handleSubmit" class="flex-1" :disabled="!canSave">
            确认并进入系统
          </el-button>
        </div>
      </el-form>

      <div class="mt-4 text-center text-gray-500 text-xs">v{{ version }}</div>
    </div>

    <!-- Step 3: Template Selection -->
    <div v-else-if="step === 'template'" class="w-[700px] bg-[#1a1a1a] p-8 rounded-2xl border border-white/10">
      <h2 class="text-2xl font-bold mb-2 text-center">选择界面模板</h2>
      <p class="text-gray-400 text-sm text-center mb-6">为 {{ padType }} 选择一个界面模板</p>

      <div v-if="templateList.length === 0" class="text-center py-8 text-gray-400">
        该类型暂无可用模板
      </div>

      <div v-else class="grid grid-cols-2 gap-4 mb-6">
        <div
          v-for="tpl in templateList"
          :key="tpl.id"
          class="bg-[#2a2a2a] rounded-xl p-5 cursor-pointer border-2 transition-all hover:border-white/30"
          :class="selectedTemplate === tpl.id ? 'border-blue-500' : 'border-transparent'"
          @click="selectedTemplate = tpl.id"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-lg font-medium">{{ tpl.manifest.name }}</span>
            <div
              class="w-5 h-5 rounded-full border-2 flex items-center justify-center"
              :class="selectedTemplate === tpl.id ? 'border-blue-500 bg-blue-500' : 'border-white/20'"
            >
              <div v-if="selectedTemplate === tpl.id" class="w-2 h-2 rounded-full bg-white"></div>
            </div>
          </div>
          <p class="text-sm text-gray-400">{{ tpl.manifest.description || '暂无描述' }}</p>
          <p v-if="tpl.manifest.version" class="text-xs text-gray-500 mt-2">v{{ tpl.manifest.version }}</p>
        </div>
      </div>

      <div class="flex gap-4">
        <el-button size="large" @click="step = 'binding'" class="flex-1">返回</el-button>
        <el-button type="primary" size="large" @click="handleConfirmTemplate" class="flex-1">
          确认并进入系统
        </el-button>
      </div>

      <div class="mt-4 text-center text-gray-500 text-xs">v{{ version }}</div>
    </div>
    </template>
  </div>
</template>

<style scoped>
:deep(.el-form-item__label) {
  color: rgba(255, 255, 255, 0.9);
}
:deep(.el-radio__label) {
  color: rgba(255, 255, 255, 0.9);
}

/* ====== 密码键盘 ====== */
.pw-title { font-size: 24px; font-weight: 700; text-align: center; margin-bottom: 24px; }
.pw-label { font-size: 18px; text-align: center; margin-bottom: 16px; opacity: 0.8; }
.pw-input-row { display: flex; justify-content: center; gap: 20px; margin-bottom: 8px; }
.pw-dot { width: 48px; height: 48px; border-radius: 50%; background: rgba(255,255,255,0.1); transition: background 0.2s; }
.pw-dot.active { background: #ED8733; }
.pw-dot.error { background: #ff5443; }
.pw-error { text-align: center; color: #ff5443; font-size: 16px; margin-top: 8px; height: 24px; }
.pw-keyboard { width: 360px; margin: 20px auto 0; }
.pw-kb-row { display: flex; justify-content: center; gap: 8px; margin-bottom: 8px; }
.pw-kb-key { width: 80px; height: 56px; border-radius: 8px; background: rgba(255,255,255,0.08); display: flex; align-items: center; justify-content: center; font-size: 24px; cursor: pointer; user-select: none; transition: background 0.15s; }
.pw-kb-key:hover { background: rgba(255,255,255,0.18); }
.pw-kb-key:active { background: rgba(255,255,255,0.25); }
.pw-kb-key.empty { background: transparent; cursor: default; }
.pw-kb-key.del { background: rgba(255,255,255,0.05); }
</style>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AppConfig } from '../config'
import { useCockpitStore } from '../stores/cockpit'
import AppBackground from '../components/AppBackground.vue'
import SmartBuildingPage from './SmartBuilding.vue'
import ControlPage from './Control.vue'
import LightPage from './Light.vue'
import SpacePage from './Space.vue'
import EnergyPage from './Energy.vue'
import OutAirPage from './OutAir.vue'
import InAirPage from './InAir.vue'
import ServicePage from './Service.vue'
import AppLogo from '../components/AppLogo.vue'
import TimeWidget from '../components/TimeWidget.vue'
import QualityCard from '../components/QualityCard.vue'
import { 
  Zap, Fan, Lightbulb, 
  Droplet, Thermometer,CircleEllipsis,
  UserRound, Building2,Siren
} from 'lucide-vue-next'
import VScaleScreen from 'v-scale-screen'

const router = useRouter()
const store = useCockpitStore()

const controlDrawer = ref(false)
const lightDrawer = ref(false)
const spaceDrawer = ref(false)
const smartBuildingDrawer = ref(false)
const energyDrawer = ref(false)
const outAirDrawer = ref(false)
const inAirDrawer = ref(false)
const serviceDrawer = ref(false)
const showSOSDialog = ref(false)

// Outdoor Temp Variable
const outdoorTemp = ref(20.2)
const outdoorTempInt = computed(() => Math.floor(outdoorTemp.value))
const outdoorTempDec = computed(() => (outdoorTemp.value % 1).toFixed(1).substring(1))

// Indoor Temp Variable
const indoorTemp = ref(23.7)
const indoorTempInt = computed(() => Math.floor(indoorTemp.value))
const indoorTempDec = computed(() => (indoorTemp.value % 1).toFixed(1).substring(1))

// Bottom Dock Items
const dockItems = computed(() => [
  { icon: Zap, label: 'Charge' }, // 1. 能耗统计
  { icon: Lightbulb, label: 'Light' }, // 2. 照明控制
  { icon: CircleEllipsis, label: 'Seat' }, // 3. 空间占用 (Updated Icon)
  { text: indoorTemp.value.toString(), label: 'AirQualityL', action: 'inAir' }, // 4. 空气质量 (Temp L -> AirQualityL)
  { icon: Fan, label: 'Climate', active: true,  spin: true }, // 5. 温控界面
  { text: outdoorTemp.value.toString(), label: 'AirQualityR', action: 'outAir' }, // 6. 空气质量 (Temp R -> AirQualityR)
  { icon: UserRound, label: 'Service', action: 'service' }, // 7. 服务页面
  { icon: Siren, label: 'Emergency', action: 'sos' }, // 8. 应急呼叫
  { icon: Building2, label: 'SmartInfo', action: 'smartBuilding' }, // 9. 智能化介绍
])

const handleDockClick = (item: any) => {
  if (item.label === 'Climate') {
    controlDrawer.value = true
  } else if (item.label === 'Light') {
    lightDrawer.value = true
  } else if (item.label === 'Seat') {
    spaceDrawer.value = true
  } else if (item.action === 'smartBuilding') {
    smartBuildingDrawer.value = true
  } else if (item.label === 'Charge') {
    energyDrawer.value = true
  } else if (item.action === 'outAir') {
    outAirDrawer.value = true
  } else if (item.action === 'inAir') {
    inAirDrawer.value = true
  } else if (item.action === 'service') {
    serviceDrawer.value = true
  } else if (item.action === 'sos') {
    showSOSDialog.value = true
  }
}

</script>

<template>
  <VScaleScreen :width="AppConfig.design.width" :height="AppConfig.design.height" :fullScreen="true">
    <!-- Background Layer -->
    <AppBackground :type="store.background.type" :src="store.background.src" />

    <!-- Main Container -->
    <div class="relative z-10 w-full h-full text-white overflow-hidden flex flex-col">
      
      <!-- Top Header -->
      <header class="flex justify-between items-start pt-8 px-10">
        <!-- Logo -->
        <AppLogo />
        
        <!-- Date/Time -->
        <TimeWidget />
      </header>

      <!-- Center Content (Two Columns) -->
      <div class="flex-1 w-full flex items-center relative">
        
        <!-- Vertical Divider -->
        <div class="absolute left-1/2 top-10 bottom-10 w-px bg-gradient-to-b from-transparent via-white/20 to-transparent"></div>

        <!-- Left Panel: Indoor (Takes up left 50%) -->
        <div class="flex-1 h-full flex flex-col justify-between px-16 py-10">
           
           <!-- Center Group -->
           <div class="flex flex-col gap-8 my-auto">
              <!-- Header -->
              <div class="flex items-center gap-2 text-white/80 text-2xl">
                  <Thermometer class="w-6 h-6" />
                  <span>42F B区 室内</span>
              </div>
              
              <!-- Big Temp & Humidity Row -->
              <div class="flex items-end gap-12">
                  <!-- Temp -->
                  <div class="flex items-baseline leading-none">
                    <span class="text-[12rem] font-bold tracking-tighter">{{ indoorTempInt }}</span>
                    <span class="text-[6rem] font-medium mb-4">{{ indoorTempDec }}</span>
                    <span class="text-4xl font-light mb-12 ml-2">°C</span>
                  </div>
                  
                  <!-- Humidity -->
                  <div class="flex flex-col gap-2 mb-8 pl-8 border-l border-white/10">
                    <div class="flex items-center gap-2 text-white/60">
                        <Droplet class="w-5 h-5" />
                        <span>湿度</span>
                    </div>
                    <div class="flex items-baseline gap-3">
                        <span class="text-5xl font-medium">55<span class="text-2xl">.9%</span></span>
                        <span class="text-green-400 text-xl">舒适</span>
                    </div>
                  </div>
              </div>
           </div>

           <!-- Cards Row -->
           <div class="grid grid-cols-3 gap-6">
              <QualityCard 
                 title="甲醛" 
                 status="安全" 
                 value="0.012" 
                 unit="mg/m³" 
                 :progress="12" 
               />
              <QualityCard 
                title="CO₂" 
                status="清新" 
                value="558" 
                unit="ppm" 
                :progress="30"
              />
              <QualityCard 
                title="PM2.5" 
                status="优" 
                value="10" 
                unit="mg/m³" 
                :progress="10"
              />
           </div>
        </div>

        <!-- Right Panel: Outdoor (Takes up right 50%) -->
        <div class="flex-1 h-full flex flex-col justify-between px-16 py-10">
           
           <!-- Center Group -->
           <div class="flex flex-col gap-8 my-auto">
              <!-- Header -->
              <div class="flex items-center gap-2 text-white/80 text-2xl">
                  <Thermometer class="w-6 h-6" />
                  <span>室外</span>
              </div>
              
              <!-- Big Temp & Weather Row -->
              <div class="flex items-end gap-8">
                  <!-- Temp -->
                  <div class="flex items-baseline leading-none">
                    <span class="text-[12rem] font-bold tracking-tighter">{{ outdoorTempInt }}</span>
                    <span class="text-[6rem] font-medium mb-4">{{ outdoorTempDec }}</span>
                    <span class="text-4xl font-light mb-12 ml-2">°C</span>
                  </div>
                  
                  <!-- Weather -->
                  <div class="flex flex-col gap-2 mb-10">
                    <div class="text-3xl font-light tracking-wide text-white/90">小雨转晴</div>
                  </div>
              </div>
           </div>

           <!-- Cards Row -->
           <div class="grid grid-cols-3 gap-6">
              <QualityCard 
                title="AQI" 
                status="清新" 
                value="26" 
                :progress="26"
              />
              <QualityCard 
                title="气压" 
                status="正常" 
                value="1016" 
                unit="hPa" 
                :progress="66"
              />
              <QualityCard 
                title="PM2.5" 
                status="优" 
                value="18" 
                unit="μg/m³" 
                :progress="18"
              />
           </div>
        </div>

      </div>

      <!-- Bottom Dock -->
      <div class="h-28 bg-black/40 backdrop-blur-md flex justify-center items-center gap-20 px-10">
         <template v-for="(item, index) in dockItems" :key="index">
            <div 
               class="flex flex-col items-center justify-center gap-1 opacity-90 hover:opacity-100 cursor-pointer"
               @click="handleDockClick(item)"
            >
               <!-- Icon or Text or Image -->
               <img 
                 v-if="'image' in item && typeof item.image === 'string'" 
                 :src="item.image" 
                 class="w-8 h-8 object-contain"
               />
               <component 
                 v-else-if="'icon' in item" 
                 :is="item.icon" 
                 :class="{
                   'w-14 h-14': item.label === 'Climate',
                   'w-8 h-8': item.label !== 'Climate',
                   'text-white': !item.active, 
                   'text-white fill-white': item.active && 'caption' in item && item.caption,
                   'animate-spin-slow': item.spin
                 }"
               />
               <span v-else class="text-2xl font-medium">{{ item.text }}</span>

               <!-- Caption (e.g. for Fan) -->
               <span v-if="'caption' in item" class="text-xs font-light mt-1">{{ item.caption }}</span>
            </div>
         </template>
      </div>

    </div>

    <!-- Control Drawer -->
    <el-drawer
      v-model="controlDrawer"
      :modal="false"
      direction="btt"
      :with-header="false"
      size="100%"
      class="!bg-black/10 !text-white backdrop-blur-xl"
    >
      <ControlPage @close="controlDrawer = false" />
    </el-drawer>

    <!-- Light Drawer -->
    <el-drawer
      v-model="lightDrawer"
      :modal="false"
      direction="btt"
      :with-header="false"
      size="100%"
      class="!bg-black/10 !text-white backdrop-blur-xl"
    >
      <LightPage @close="lightDrawer = false" />
    </el-drawer>

    <!-- Space Drawer -->
    <el-drawer
      v-model="spaceDrawer"
      :modal="false"
      direction="btt"
      :with-header="false"
      size="100%"
      class="!bg-black/10 !text-white backdrop-blur-xl"
    >
      <SpacePage @close="spaceDrawer = false" />
    </el-drawer>

    <!-- Smart Building Drawer -->
    <el-drawer
      v-model="smartBuildingDrawer"
      :modal="false"
      direction="btt"
      :with-header="false"
      size="100%"
      class="!bg-black/10 !text-white backdrop-blur-xl"
    >
      <SmartBuildingPage @close="smartBuildingDrawer = false" />
    </el-drawer>

    <!-- Energy Drawer -->
    <el-drawer
      v-model="energyDrawer"
      :modal="false"
      direction="btt"
      :with-header="false"
      size="100%"
      class="!bg-black/10 !text-white backdrop-blur-xl"
    >
      <EnergyPage @close="energyDrawer = false" />
    </el-drawer>

    <!-- OutAir Drawer -->
    <el-drawer
      v-model="outAirDrawer"
      :modal="false"
      direction="btt"
      :with-header="false"
      size="100%"
      class="!bg-black/10 !text-white backdrop-blur-xl"
    >
      <OutAirPage @close="outAirDrawer = false" />
    </el-drawer>

    <!-- InAir Drawer -->
    <el-drawer
      v-model="inAirDrawer"
      :modal="false"
      direction="btt"
      :with-header="false"
      size="100%"
      class="!bg-black/10 !text-white backdrop-blur-xl"
    >
      <InAirPage @close="inAirDrawer = false" />
    </el-drawer>

    <!-- Service Drawer -->
    <el-drawer
      v-model="serviceDrawer"
      :modal="false"
      direction="btt"
      :with-header="false"
      size="100%"
      class="!bg-black/10 !text-white backdrop-blur-xl"
    >
      <ServicePage @close="serviceDrawer = false" />
    </el-drawer>

    <!-- SOS Dialog -->
    <div v-if="showSOSDialog" class="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div class="w-[500px] bg-white rounded-3xl p-8 relative overflow-hidden shadow-2xl animate-fade-in-up">
         <!-- Subtle Pink Gradient -->
         <div class="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-red-100/50 to-transparent pointer-events-none"></div>

         <div class="relative z-10 flex flex-col items-center text-center">
            <h2 class="text-[#8B0000] text-2xl font-bold mb-6 tracking-wide">SOS紧急呼叫</h2>
            
            <p class="text-[#333333] text-lg leading-relaxed text-left w-full mb-6">
               当您处于紧急情况下可点击立即呼叫，系统将发送当前位置的求助信息至安保值班室
            </p>
            
            <p class="text-[#999999] text-base text-left w-full mb-10">
               7*24小时安保电话：(0571) 28098488
            </p>

            <div class="flex gap-6 w-full">
               <button 
                 @click="showSOSDialog = false"
                 class="flex-1 h-14 rounded-full border border-[#CCCCCC] text-[#333333] text-lg font-medium hover:bg-gray-50 active:scale-95 transition-all"
               >
                 取消
               </button>
               <button 
                 @click="showSOSDialog = false"
                 class="flex-1 h-14 rounded-full bg-[#FF5C4D] text-white text-lg font-medium shadow-lg hover:bg-[#FF4C3D] active:scale-95 transition-all"
               >
                 确认
               </button>
            </div>
         </div>
      </div>
    </div>
  </VScaleScreen>
</template>

<style scoped>
.animate-spin-slow {
  animation: spin 3s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translate3d(0, 20px, 0);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 0.3s ease-out forwards;
}

:deep(.el-drawer) {
  background: rgba(0, 0, 0, 0.85) !important;
  backdrop-filter: blur(20px);
  border-top-left-radius: 0;
  border-top-right-radius: 0;
  box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.5);
}

:deep(.el-drawer__body) {
  padding: 0;
  overflow: hidden;
}
</style>

<script setup lang="ts">
import { computed, ref } from 'vue'
import BaseCard from '../components/BaseCard.vue'
import AppLogo from '../components/AppLogo.vue'
import TimeWidget from '../components/TimeWidget.vue'
import { Lightbulb, Home } from 'lucide-vue-next'
import { useLightMqtt } from '@/composables/useLightMqtt'

const emit = defineEmits(['close'])

const { lights, toggleLight, setAll } = useLightMqtt()

const devices = computed(() => lights.value.devices)
const isDeviceOn = (d: { status?: Record<string, any> }) => d.status?.status === 'on' || d.status?.status === 1
const isAllOn = computed(() => devices.value.length > 0 && devices.value.every(isDeviceOn))
const isAllOff = computed(() => devices.value.length > 0 && devices.value.every((d) => !isDeviceOn(d)))

// Confirm dialog
const confirmVisible = ref(false)
const confirmTitle = ref('')
const pendingDevice = ref<{ id: string; name: string; status: Record<string, any> } | null>(null)

const handleLightClick = (device: { id: string; name: string; status: Record<string, any> }) => {
  pendingDevice.value = device
  const isOn = device.status?.status === 'on'
  confirmTitle.value = (isOn ? '关闭' : '打开') + ' ' + device.name
  confirmVisible.value = true
}

const handleConfirm = () => {
  if (pendingDevice.value) {
    toggleLight(pendingDevice.value.id)
    confirmVisible.value = false
    pendingDevice.value = null
  }
}

const handleCancel = () => {
  confirmVisible.value = false
  pendingDevice.value = null
}

const handleAllOff = () => setAll(false)
const handleAllOn = () => setAll(true)

// Map Markers
const mapMarkers = [
  { id: 1, label: '过道照明 1', x: 30, y: 40, active: true },
  { id: 2, label: '照明 1', x: 50, y: 35, active: true },
  { id: 3, label: '过道照明 2', x: 25, y: 55, active: true },
  { id: 4, label: '照明 2', x: 45, y: 50, active: true },
  { id: 5, label: '照明 3', x: 40, y: 65, active: true },
  { id: 6, label: '照明 4', x: 35, y: 80, active: true },
]
</script>

<template>
  <div class="relative w-full h-full p-8 text-white overflow-hidden flex flex-col bg-black/90">

    <header class="flex justify-between items-center mb-6 px-2">
      <AppLogo @click="emit('close')" />
      <TimeWidget />
    </header>

    <div class="grid grid-cols-12 gap-6 flex-1 min-h-0">

      <!-- Left Column (Controls) -->
      <div class="col-span-8 flex flex-col gap-6">

        <div class="flex-1 flex flex-col gap-4">
          <div class="text-xl font-bold tracking-wide">照明控制</div>

          <BaseCard className="flex-1 !border-white/5 !bg-white/5 !rounded-3xl p-6 flex flex-col gap-6">
            <!-- Light Grid -->
            <div class="grid grid-cols-6 gap-4 overflow-y-auto pr-2">
              <div
                v-for="device in devices"
                :key="device.id"
                @click="handleLightClick(device)"
                class="aspect-[4/4] rounded-xl flex flex-col items-center justify-center gap-2 cursor-pointer transition-all active:scale-95"
                :class="device.status?.status === 'on' ? 'bg-white/20 hover:bg-white/25' : 'bg-white/5 hover:bg-white/10'"
              >
                 <Lightbulb
                   class="w-8 h-8"
                   :class="device.status?.status === 'on' ? 'text-white fill-white' : 'text-white/40'"
                 />
                 <span class="text-xs text-center px-2 truncate w-full text-white/80">{{ device.name }}</span>
              </div>

              <!-- Empty state -->
              <div v-if="devices.length === 0" class="col-span-6 flex items-center justify-center h-full text-white/40 text-lg">
                暂无照明设备
              </div>
            </div>

            <!-- Bottom: All-On / All-Off segmented control -->
            <div class="flex rounded-2xl overflow-hidden border border-white/10">
              <button
                @click="handleAllOff"
                class="flex-1 py-4 text-center text-lg font-bold transition-colors"
                :class="isAllOff ? 'bg-white/20 text-white' : 'bg-white/5 text-white/50 hover:bg-white/10'"
              >
                全关
              </button>
              <button
                @click="handleAllOn"
                class="flex-1 py-4 text-center text-lg font-bold transition-colors border-l border-white/10"
                :class="isAllOn ? 'bg-white/20 text-white' : 'bg-white/5 text-white/50 hover:bg-white/10'"
              >
                全开
              </button>
            </div>
          </BaseCard>

        </div>

      </div>

      <!-- Right Column (Map) -->
      <div class="col-span-4 h-full">
         <BaseCard className="h-full !border-white/5 !bg-white/5 !rounded-3xl p-0 overflow-hidden relative">
            <div class="absolute inset-0 bg-[#1a1a1a] flex items-center justify-center">
               <div class="w-[80%] h-[70%] border-2 border-white/10 rounded-3xl transform rotate-12 relative">
                  <div class="absolute top-0 right-0 w-1/3 h-full border-l-2 border-white/10 bg-white/5"></div>
                  <div class="absolute bottom-10 left-10 text-white/20 text-4xl font-bold rotate-[-12deg]">2604会议室</div>
               </div>
            </div>

            <div
              v-for="marker in mapMarkers"
              :key="marker.id"
              class="absolute transform -translate-x-1/2 -translate-y-full cursor-pointer hover:scale-110 transition-transform z-10"
              :style="{ left: `${marker.x + 20}%`, top: `${marker.y + 10}%` }"
            >
               <div class="flex flex-col items-center">
                  <div class="bg-white text-black text-xs font-bold px-3 py-1.5 rounded-full flex items-center gap-1 shadow-lg whitespace-nowrap">
                     <Lightbulb class="w-3 h-3 text-orange-500 fill-orange-500" />
                     {{ marker.label }}
                  </div>
                  <div class="w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[8px] border-t-white"></div>
               </div>
            </div>

            <div class="absolute top-6 left-6 flex flex-col gap-2">
               <div class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center backdrop-blur-md border border-white/10">
                  <span class="text-xs">1F</span>
               </div>
            </div>
         </BaseCard>
      </div>

    </div>

    <div class="flex justify-center mt-6 shrink-0">
       <button
         @click="emit('close')"
         class="bg-[#2a2a2a] hover:bg-[#333] text-white px-8 py-3 rounded-full flex items-center gap-3 transition-colors border border-white/10"
       >
         <Home class="w-5 h-5" />
         <span class="text-lg">返回首页</span>
       </button>
    </div>

    <!-- Confirm Dialog -->
    <Teleport to="body">
      <div
        v-if="confirmVisible"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
        @click.self="handleCancel"
      >
        <div class="w-[400px] bg-[#1e1e1e] rounded-2xl p-6 border border-white/10 shadow-2xl">
          <div class="text-white text-lg text-center mb-6">{{ confirmTitle }}</div>
          <div class="flex justify-center gap-4">
            <button
              @click="handleCancel"
              class="px-8 py-2.5 rounded-xl bg-white/10 text-white/70 hover:bg-white/20 transition-colors text-base"
            >
              取消
            </button>
            <button
              @click="handleConfirm"
              class="px-8 py-2.5 rounded-xl bg-white text-black hover:bg-white/90 transition-colors text-base font-medium"
            >
              确认
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useCockpitStore } from '../stores/cockpit'
import BaseCard from '../components/BaseCard.vue'
import AppLogo from '../components/AppLogo.vue'
import TimeWidget from '../components/TimeWidget.vue'
import { 
  Fan, Power,  
  ArrowUp, ArrowDown, Wind, Home,
  Snowflake, Sun as SunIcon
} from 'lucide-vue-next'

// Define Emits
const emit = defineEmits(['close'])

const handleHome = () => {
  emit('close')
}

const fanSpeed = ref('mid') // 'low', 'mid', 'high'

const setFanSpeed = (speed: string) => {
  fanSpeed.value = speed
}

const acMode = ref('cool') // 'vent', 'cool', 'heat'

const setAcMode = (mode: string) => {
  acMode.value = mode
}

const isAcOn = ref(true)

const toggleAcPower = () => {
  isAcOn.value = !isAcOn.value
}

// Mock Data for new Layout
const lightingList = [
  { id: 'office', label: '办公室灯光', isOn: true },
  { id: 'meeting', label: '会议室灯光', isOn: false },
  { id: 'office2', label: '办公室灯光', isOn: true },
]

</script>

<template>
  <!-- Main Container -->
  <div class="relative w-full h-full p-8 text-white overflow-hidden flex flex-col">
    
    <!-- Top Header -->
    <header class="flex justify-between items-center mb-6 px-2">
      <AppLogo @click="emit('close')" />
      <TimeWidget />
    </header>

    <!-- Main Grid Content -->
    <div class="grid grid-cols-12 gap-6 flex-1 min-h-0 mb-8">

      <!-- Column 2: Climate Control (Span 4) -->
      <div class="col-span-8 h-full">
         <BaseCard className="h-full !border-white/5 !rounded-3xl p-6 flex flex-col gap-4">
            <div class="text-xl font-bold tracking-wide mb-2">空调控制</div>
            <!-- Status Bar -->
            <div class="h-16 bg-white/10 rounded-full flex items-center justify-between px-8">
               <span class="text-lg text-white/80">当前温度：17°C</span>
               <span class="text-lg text-white/80">空调模式：制冷</span>
            </div>

            <!-- Controls Area -->
            <div class="flex-1 flex gap-6">
               <!-- Temp Control -->
               <div class="flex-1 bg-black/20 rounded-3xl flex flex-col items-center justify-between py-8">
                  <button class="p-4 hover:bg-white/5 rounded-full"><ArrowUp class="w-8 h-8" /></button>
                  <div class="text-6xl font-light">26<span class="text-2xl">°C</span></div>
                  <button class="p-4 hover:bg-white/5 rounded-full"><ArrowDown class="w-8 h-8" /></button>
               </div>
               <!-- Fan Control -->
               <div class="flex-1 bg-black/20 rounded-3xl flex flex-col items-center justify-between py-4 px-4 gap-2">
                  <!-- High -->
                  <div 
                    @click="setFanSpeed('high')"
                    class="w-full flex-1 rounded-2xl flex flex-col items-center justify-center transition-all cursor-pointer"
                    :class="fanSpeed === 'high' ? 'bg-white/20 text-white' : 'hover:bg-white/5 text-white/40'"
                  >
                     <div class="flex gap-1">
                        <Fan class="w-5 h-5 " />
                        <Fan class="w-5 h-5 " />
                        <Fan class="w-5 h-5 " />
                     </div>
                     <span class="text-2xl mt-1">高风</span>
                  </div>

                  <!-- Mid -->
                  <div 
                    @click="setFanSpeed('mid')"
                    class="w-full flex-1 rounded-2xl flex flex-col items-center justify-center transition-all cursor-pointer"
                    :class="fanSpeed === 'mid' ? 'bg-white/20 text-white' : 'hover:bg-white/5 text-white/40'"
                  >
                     <div class="flex gap-1">
                        <Fan class="w-5 h-5 " />
                        <Fan class="w-5 h-5 " />
                     </div>
                     <span class="text-2xl mt-1">中风</span>
                  </div>

                  <!-- Low -->
                  <div 
                    @click="setFanSpeed('low')"
                    class="w-full flex-1 rounded-2xl flex flex-col items-center justify-center transition-all cursor-pointer"
                    :class="fanSpeed === 'low' ? 'bg-white/20 text-white' : 'hover:bg-white/5 text-white/40'"
                  >
                     <Fan class="w-5 h-5 " />
                     <span class="text-2xl mt-1">低风</span>
                  </div>
               </div>

               <!-- Mode Control -->
               <div class="flex-1 bg-black/20 rounded-3xl flex flex-col items-center justify-between py-4 px-4 gap-2">
                  <!-- Vent -->
                  <div 
                    @click="setAcMode('vent')"
                    class="w-full flex-1 rounded-2xl flex flex-col items-center justify-center transition-all cursor-pointer"
                    :class="acMode === 'vent' ? 'bg-white/20 text-white' : 'hover:bg-white/5 text-white/40'"
                  >
                     <Wind class="w-6 h-6" />
                     <span class="text-2xl mt-1">换气</span>
                  </div>

                  <!-- Cool -->
                  <div 
                    @click="setAcMode('cool')"
                    class="w-full flex-1 rounded-2xl flex flex-col items-center justify-center transition-all cursor-pointer"
                    :class="acMode === 'cool' ? 'bg-white/20 text-white' : 'hover:bg-white/5 text-white/40'"
                  >
                     <Snowflake class="w-6 h-6" />
                     <span class="text-2xl mt-1">制冷</span>
                  </div>

                  <!-- Heat -->
                  <div 
                    @click="setAcMode('heat')"
                    class="w-full flex-1 rounded-2xl flex flex-col items-center justify-center transition-all cursor-pointer"
                    :class="acMode === 'heat' ? 'bg-white/20 text-white' : 'hover:bg-white/5 text-white/40'"
                  >
                     <SunIcon class="w-6 h-6" />
                     <span class="text-2xl mt-1">制热</span>
                  </div>
               </div>
            </div>

            <!-- Bottom Power Button -->
            <button 
              @click="toggleAcPower"
              class="power-btn"
              :class="isAcOn ? 'power-btn-on' : 'power-btn-off'"
            >
               <Power class="w-8 h-8" />
            </button>
         </BaseCard>
      </div>

      <!-- Column 3: Environment (Span 4) -->
      <div class="col-span-4 h-full">
         <BaseCard className="h-full !border-white/5 !rounded-3xl p-6 flex flex-col gap-4">
            <div class="text-xl font-bold tracking-wide mb-2">室内环境</div>
            <!-- Top Row: Temp & Humidity -->
            <div class="grid grid-cols-2 gap-4 h-40">
               <div class="bg-white/5 rounded-3xl p-5 flex flex-col justify-between">
                  <span class="text-white/60">温度</span>
                  <div>
                     <div class="text-5xl font-light mb-2">23<span class="text-lg">°C</span></div>
                     <div class="h-1 w-full bg-gradient-to-r from-blue-500 via-green-400 to-orange-500 rounded-full"></div>
                  </div>
               </div>
               <div class="bg-white/5 rounded-3xl p-5 flex flex-col justify-between">
                  <span class="text-white/60">湿度</span>
                  <div>
                     <div class="text-5xl font-light mb-2">50<span class="text-lg">%</span></div>
                     <div class="h-1 w-full bg-gradient-to-r from-blue-400 to-cyan-300 rounded-full"></div>
                  </div>
               </div>
            </div>

            <!-- Stacked Metrics -->
            <div class="flex-1 flex flex-col gap-4">
               <div class="flex-1 bg-white/5 rounded-3xl p-5 flex flex-col justify-center">
                  <span class="text-white/60 text-sm mb-1">PM2.5</span>
                  <div class="text-3xl font-light mb-2">8<span class="text-base text-white/60 ml-1">μg/m³</span></div>
                  <div class="h-1 w-full bg-gradient-to-r from-green-400 to-yellow-400 rounded-full opacity-60"></div>
               </div>
               <div class="flex-1 bg-white/5 rounded-3xl p-5 flex flex-col justify-center">
                  <span class="text-white/60 text-sm mb-1">CO₂</span>
                  <div class="text-3xl font-light mb-2">564<span class="text-base text-white/60 ml-1">ppm</span></div>
                  <div class="h-1 w-full bg-gradient-to-r from-green-400 to-yellow-400 rounded-full opacity-60"></div>
               </div>
               <div class="flex-1 bg-white/5 rounded-3xl p-5 flex flex-col justify-center">
                  <span class="text-white/60 text-sm mb-1">TVOC</span>
                  <div class="text-3xl font-light mb-2">0.085<span class="text-base text-white/60 ml-1">mg/m³</span></div>
                  <div class="h-1 w-full bg-gradient-to-r from-green-400 to-orange-400 rounded-full opacity-60"></div>
               </div>
            </div>
         </BaseCard>
      </div>

    </div>

    <!-- Bottom Nav -->
    <div class="flex justify-center mt-6 shrink-0">
       <button 
         @click="handleHome"
         class="bg-[#2a2a2a] hover:bg-[#333] text-white px-8 py-3 rounded-full flex items-center gap-3 transition-colors border border-white/10"
       >
         <Home class="w-5 h-5" />
         <span class="text-lg">返回首页</span>
       </button>
    </div>

  </div>
</template>

<style scoped>
.animate-spin-slow {
  animation: spin 3s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>

<script setup lang="ts">
import { ref } from 'vue'
import BaseCard from '../components/BaseCard.vue'
import AppLogo from '../components/AppLogo.vue'
import TimeWidget from '../components/TimeWidget.vue'
import { User, Users, Home } from 'lucide-vue-next'

// Define Emits
const emit = defineEmits(['close'])

const handleHome = () => {
  emit('close')
}

// Mock Data for Meeting Rooms
const rooms = [
  { id: '2601', name: '2601', status: 'free' },
  { id: '2602', name: '2602', status: 'free' },
  { id: '2603', name: '2603', status: 'busy' },
  { id: '2604', name: '2604', status: 'free' },
  { id: '2605', name: '2605', status: 'free' },
  { id: '2606', name: '2606', status: 'free' },
  { id: '2607', name: '2607', status: 'free' },
  { id: '2608', name: '2608', status: 'free' },
]

// Mock Data for Map Areas (simplified representation)
const mapAreas = [
  { id: 'female-wc', label: '女卫', status: 'busy', sub: '全满', type: 'wc-f', x: 30, y: 30, w: 20, h: 15 },
  { id: 'male-wc', label: '男卫', status: 'partial', sub: '可用 2', type: 'wc-m', x: 60, y: 30, w: 20, h: 15 },
  { id: '2606', label: '2606会议室', status: 'free', sub: '空闲', type: 'room', x: 25, y: 70, w: 15, h: 15 },
  { id: '2605', label: '2605会议室', status: 'free', sub: '空闲', type: 'room', x: 45, y: 70, w: 15, h: 15 },
  { id: '2604', label: '2604会议室', status: 'busy', sub: '使用中', type: 'room', x: 65, y: 70, w: 15, h: 15 },
]

const getStatusColor = (status: string) => {
  if (status === 'busy') return 'bg-[#ef4444] text-white' // Red
  if (status === 'partial') return 'bg-[#3b82f6]/80 text-white' // Blueish
  return 'bg-[#3b82f6]/40 text-white' // Light Blue
}

const getCardColor = (status: string) => {
  if (status === 'busy') return 'bg-[#ef4444] text-white border-transparent'
  return 'bg-white/10 text-white/90 border-transparent hover:bg-white/15'
}

</script>

<template>
  <div class="relative w-full h-full p-8 text-white overflow-hidden flex flex-col bg-black/90">
    
    <!-- Top Header -->
    <header class="flex justify-between items-center mb-6 px-2">
      <AppLogo @click="emit('close')" />
      <TimeWidget />
    </header>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-12 gap-6 flex-1 min-h-0">
      
      <!-- Left Column (Room List) -->
      <div class="col-span-8 h-full flex flex-col gap-4">
        <div class="text-xl font-bold tracking-wide pl-2">会议室实时状态</div>
        
        <BaseCard className="flex-1 !border-white/5 !bg-white/5 !rounded-3xl p-8 overflow-y-auto">
          <div class="grid grid-cols-2 gap-6">
            <div 
              v-for="room in rooms" 
              :key="room.id"
              class="h-24 rounded-2xl flex items-center justify-between px-8 text-xl font-medium transition-all cursor-pointer active:scale-[0.98]"
              :class="getCardColor(room.status)"
            >
              <span>{{ room.name }}</span>
              <span>{{ room.status === 'busy' ? '使用中' : '空闲' }}</span>
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- Right Column (Map) -->
      <div class="col-span-4 h-full">
         <BaseCard className="h-full !border-white/5 !bg-white/5 !rounded-3xl p-0 overflow-hidden relative flex items-center justify-center">
            <!-- Map Container -->
            <div class="relative w-[90%] aspect-square bg-[#1a1a1a] rounded-full border-4 border-white/5 flex items-center justify-center overflow-hidden">
               <!-- Octagonal Base Shape (CSS Clip Path) -->
               <div class="absolute inset-4 bg-white/5 clip-octagon"></div>

               <!-- Areas -->
               <div 
                  v-for="area in mapAreas"
                  :key="area.id"
                  class="absolute flex flex-col items-center justify-center text-center p-2 rounded-lg transition-all cursor-pointer hover:brightness-110"
                  :class="getStatusColor(area.status)"
                  :style="{ 
                    left: `${area.x}%`, 
                    top: `${area.y}%`, 
                    width: `${area.w}%`, 
                    height: `${area.h}%` 
                  }"
               >
                  <div class="flex items-center gap-1 mb-1" v-if="area.type.startsWith('wc')">
                     <User class="w-4 h-4" />
                     <span class="text-sm font-bold">{{ area.label }}</span>
                  </div>
                  <span v-else class="text-xs font-bold mb-1">{{ area.label }}</span>
                  
                  <span class="text-xs opacity-90">{{ area.sub }}</span>

                  <!-- Red dots for male WC -->
                  <div v-if="area.id === 'male-wc'" class="flex gap-1 mt-1 justify-center">
                     <div class="w-1.5 h-1.5 rounded-full bg-red-500"></div>
                     <div class="w-1.5 h-1.5 rounded-full bg-red-500"></div>
                  </div>
               </div>
               
               <!-- Center Hub -->
               <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1/4 h-1/4 bg-white/5 rounded-xl border border-white/10"></div>
            </div>
         </BaseCard>
      </div>

    </div>

    <!-- Bottom Nav -->
    <div class="flex justify-center mt-6 shrink-0">
       <button 
         @click="handleHome"
         class="bg-[#2a2a2a] hover:bg-[#333] text-white px-8 py-3 rounded-full flex items-center gap-3 transition-colors border border-white/10"
       >
         <Home class="w-5 h-5" />
         <span class="text-lg">返回首页</span>
       </button>
    </div>
  </div>
</template>

<style scoped>
.clip-octagon {
  clip-path: polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%);
}
</style>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Zap, Activity, X, Home } from 'lucide-vue-next'
import * as echarts from 'echarts'

const emit = defineEmits(['close'])

const handleHome = () => {
  emit('close')
}

const activeTab = ref('日')
const tabs = ['日', '周', '月']

const chartRef = ref<HTMLElement | null>(null)
let myChart: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  myChart = echarts.init(chartRef.value)

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      textStyle: {
        color: '#000'
      },
      padding: [8, 12],
      formatter: function (params: any) {
        const val = params[0].value
        return `用电量: ${val}kwh`
      },
      extraCssText: 'border-radius: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border: none;'
    },
    grid: {
      top: '15%',
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: Array.from({ length: 24 }, (_, i) => `${i}:00`),
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.4)',
        fontSize: 10,
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.05)'
        }
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.4)',
        fontSize: 10
      }
    },
    series: [
      {
        name: '用电量',
        type: 'bar',
        barWidth: '25%',
        itemStyle: {
          color: '#00e5ff',
          borderRadius: [2, 2, 0, 0]
        },
        data: [
          0.6, 1.2, 1.5, 1.5, 1.6, 1.8, 2.6, 3.2, 5.5, 6.2, 
          6.3, 6.6, 7.0, 6.1, 7.6, 7.4, 6.5, 6.8, 5.6, 4.6, 
          5.1, 4.2, 2.8, 1.6
        ],
        markPoint: {
            symbol: 'circle',
            symbolSize: 1,
            label: {
                show: false
            },
            data: [
                { type: 'max', name: 'Max' }
            ]
        },
        // Highlight logic can be done via itemStyle callback or visualMap, 
        // but for simplicity we'll just stick to the cyan color for now
        // or customize specific bars if needed.
      }
    ]
  }

  myChart.setOption(option)
}

onMounted(() => {
  nextTick(() => {
    initChart()
    window.addEventListener('resize', handleResize)
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  myChart?.dispose()
})

const handleResize = () => {
  myChart?.resize()
}

</script>

<template>
  <div class="w-full h-full flex flex-col p-8 relative">

    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div class="flex flex-col gap-4">
        <h1 class="text-2xl font-medium text-white">26F 能耗数据</h1>
        
        <!-- Tabs -->
        <div class="flex bg-slate-800/50 rounded-full p-1 w-fit">
          <button 
            v-for="tab in tabs" 
            :key="tab"
            @click="activeTab = tab"
            class="px-8 py-1.5 rounded-full text-sm transition-all duration-300"
            :class="activeTab === tab ? 'bg-slate-700 text-white shadow-lg' : 'text-white/40 hover:text-white/70'"
          >
            {{ tab }}
          </button>
        </div>
      </div>
    </div>

    <!-- Top Cards -->
    <div class="grid grid-cols-2 gap-6 mb-6">
      <!-- Card 1 -->
      <div class="bg-slate-800/40 rounded-2xl p-6 flex items-center gap-6 border border-white/5">
        <div class="w-12 h-12 rounded-full bg-slate-700/50 flex items-center justify-center shrink-0">
          <Zap class="w-6 h-6 text-white" />
        </div>
        <div class="flex flex-col gap-1">
          <span class="text-white/40 text-sm">今日总用电量 (2024.05.13)</span>
          <div class="flex items-baseline gap-2">
            <span class="text-4xl font-bold text-white">55.96</span>
            <span class="text-white/40 text-sm">kwh</span>
          </div>
          <span class="text-green-400 text-xs font-medium">+2.4%</span>
        </div>
      </div>

      <!-- Card 2 -->
      <div class="bg-slate-800/40 rounded-2xl p-6 flex items-center gap-6 border border-white/5">
        <div class="w-12 h-12 rounded-full bg-slate-700/50 flex items-center justify-center shrink-0">
          <Activity class="w-6 h-6 text-white" />
        </div>
        <div class="flex flex-col gap-1">
          <span class="text-white/40 text-sm">实时功率</span>
          <div class="flex items-baseline gap-2">
            <span class="text-4xl font-bold text-white">4140.8</span>
            <span class="text-white/40 text-sm">w</span>
          </div>
          <span class="text-green-400 text-xs font-medium">+2.4%</span>
        </div>
      </div>
    </div>

    <!-- Main Chart Section -->
    <div class="flex-1 bg-slate-800/40 rounded-2xl p-6 border border-white/5 flex flex-col min-h-0">
      <div class="text-white/40 text-sm mb-4">日用电量(kwh)</div>
      <div ref="chartRef" class="flex-1 w-full h-full min-h-[300px]"></div>
    </div>

    <!-- Bottom Nav -->
    <div class="flex justify-center mt-6 shrink-0">
       <button 
         @click="handleHome"
         class="bg-[#2a2a2a] hover:bg-[#333] text-white px-8 py-3 rounded-full flex items-center gap-3 transition-colors border border-white/10"
       >
         <Home class="w-5 h-5" />
         <span class="text-lg">返回首页</span>
       </button>
    </div>
  </div>
</template>

<style scoped>
/* Custom scrollbar if needed */
</style>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { AppConfig } from '../config'
import { useCockpitStore } from '../stores/cockpit'
import AppBackground from '../components/AppBackground.vue'
import BaseCard from '../components/BaseCard.vue'
import AppLogo from '../components/AppLogo.vue'
import TimeWidget from '../components/TimeWidget.vue'
import VScaleScreen from 'v-scale-screen'
import QualityCard from '../components/QualityCard.vue'
import { Home } from 'lucide-vue-next'

const router = useRouter()
const store = useCockpitStore()

const handleHome = () => {
  emit('close')
}

const emit = defineEmits(['close'])

const tempLevels = [
  { label: '偏冷', color: 'bg-blue-500' },
  { label: '适宜', color: 'bg-green-400' },
  { label: '偏热', color: 'bg-orange-400' },
]
const humidityLevels = [
  { label: '干燥', color: 'bg-yellow-400' },
  { label: '适宜', color: 'bg-green-400' },
  { label: '微湿', color: 'bg-teal-400' },
  { label: '高湿', color: 'bg-blue-500' },
]

const pm25Levels = [
  { label: '<35, 优', color: 'bg-green-500' },
  { label: '>35 且≤75, 良', color: 'bg-yellow-400' },
  { label: '>75 且≤115, 轻度污染', color: 'bg-orange-400' },
  { label: '>115 且≤150, 中度污染', color: 'bg-red-500' },
  { label: '>150 且≤250, 重度污染', color: 'bg-purple-500' },
  { label: '>250, 严重污染', color: 'bg-rose-900' },
]

const co2Levels = [
  { label: '<=500, 非常清新', color: 'bg-green-500' },
  { label: '>500 且≤800, 清新', color: 'bg-green-300' },
  { label: '>800 且≤1000, 较清新', color: 'bg-yellow-200' },
  { label: '>1000 且≤1500, 较污染', color: 'bg-orange-300' },
  { label: '>1500 且≤2000, 污染', color: 'bg-red-400' },
  { label: '>2000, 非常污浊', color: 'bg-red-700' },
]

const pm10Levels = [
  { label: '<= 0.5 正常', color: 'bg-green-500' },
  { label: '> 0.5 异常', color: 'bg-red-500' },
]

const tvocLevels = [
  { label: '<= 0.5 正常', color: 'bg-green-500' },
  { label: '> 0.5 异常', color: 'bg-red-500' },
]

const hchoLevels = [
  { label: '<= 0.08 正常', color: 'bg-green-500' },
  { label: '> 0.08 超标', color: 'bg-red-500' },
]

const aqiTable = [
  { range: '0 - 50', level: '一级（优）', desc: '空气质量令人满意，基本无空气污染', action: '各类人群可正常活动', color: 'bg-green-500' },
  { range: '51 - 100', level: '二级（良）', desc: '空气质量可接受，但某些污染物可能对极少数异常敏感人群健康有较弱影响', action: '极少数异常敏感人群应减少户外活动', color: 'bg-yellow-400' },
  { range: '101 - 150', level: '三级（轻度污染）', desc: '易感人群症状有轻度加剧，健康人群出现刺激症状', action: '儿童、老年人及心脏病、呼吸系统疾病患者应减少长时间、高强度的户外锻炼', color: 'bg-orange-400' },
  { range: '151 - 200', level: '四级（中度污染）', desc: '进一步加剧易感人群症状，可能对健康人群心脏、呼吸系统有影响', action: '儿童、老年人及心脏病、呼吸系统疾病患者避免长时间、高强度的户外锻炼，一般人适量减少户外运动', color: 'bg-red-500' },
  { range: '201 - 300', level: '五级（重度污染）', desc: '心脏病和肺病患者症状显著加剧，运动耐受力降低，健康人群普遍出现症状', action: '儿童、老年人及心脏病、肺病患者应停留在室内，停止户外运动，一般人群减少户外运动', color: 'bg-purple-600' },
  { range: '>300', level: '六级（严重污染）', desc: '健康人群运动耐受力降低，有明显强烈症状，提前出现某些疾病', action: '儿童、老年人及病人应停留在室内，避免体力消耗，一般人避免户外活动', color: 'bg-red-900' },
]

</script>

<template>

    <div class="relative z-10 w-full h-full text-white flex flex-col p-8 overflow-hidden">
      <!-- Header -->
      <header class="flex justify-between items-start mb-6 shrink-0">
        <AppLogo />
        <TimeWidget />
      </header>

      <!-- Main Grid -->
      <div class="flex-1 overflow-y-auto pr-2 pb-2">
        <!-- Top Row: Indicators -->
        <div class="grid grid-cols-3 gap-4 mb-6">
           <QualityCard title="温度" status="舒适" value="23.7" unit="°C" :progress="40" />
           <QualityCard title="湿度" status="舒适" value="55.9" unit="%" :progress="56" />
           <QualityCard title="甲醛" status="安全" value="0.012" unit="mg/m³" :progress="12" />
           <QualityCard title="CO₂" status="清新" value="558" unit="ppm" :progress="30" />
           <QualityCard title="PM2.5" status="优" value="10" unit="μg/m³" :progress="10" />
           <QualityCard title="TVOC" status="正常" value="0.1" unit="mg/m³" :progress="20" />
        </div>

        <!-- Explanation Rows -->
        <div class="grid grid-cols-2 gap-6">

           <!-- Environmental Colors -->
           <BaseCard class="col-span-2 bg-[#1e1e1e]/60 border-white/5 flex flex-col !p-6">
              <div class="text-lg font-medium mb-6">环境指标用色</div>
              <div class="grid grid-cols-6 gap-8">
                 <!-- Temperature -->
                 <div>
                    <div class="text-sm font-medium mb-3">温度</div>
                    <div class="flex flex-col gap-2">
                       <div v-for="(item, idx) in tempLevels" :key="idx" class="flex items-center gap-2 text-xs text-white/80">
                          <div class="w-2 h-2 rounded-full shrink-0" :class="item.color"></div>
                          <span>{{ item.label }}</span>
                       </div>
                    </div>
                 </div>

                 <!-- Humidity -->
                 <div>
                    <div class="text-sm font-medium mb-3">湿度</div>
                    <div class="flex flex-col gap-2">
                       <div v-for="(item, idx) in humidityLevels" :key="idx" class="flex items-center gap-2 text-xs text-white/80">
                          <div class="w-2 h-2 rounded-full shrink-0" :class="item.color"></div>
                          <span>{{ item.label }}</span>
                       </div>
                    </div>
                 </div>

                 <!-- PM2.5 -->
                 <div>
                    <div class="text-sm font-medium mb-3">PM2.5</div>
                    <div class="flex flex-col gap-2">
                       <div v-for="(item, idx) in pm25Levels" :key="idx" class="flex items-center gap-2 text-xs text-white/80">
                          <div class="w-2 h-2 rounded-full shrink-0" :class="item.color"></div>
                          <span>{{ item.label }}</span>
                       </div>
                    </div>
                 </div>
                 
                 <!-- CO2 -->
                 <div>
                    <div class="text-sm font-medium mb-3">CO2</div>
                    <div class="flex flex-col gap-2">
                       <div v-for="(item, idx) in co2Levels" :key="idx" class="flex items-center gap-2 text-xs text-white/80">
                          <div class="w-2 h-2 rounded-full shrink-0" :class="item.color"></div>
                          <span>{{ item.label }}</span>
                       </div>
                    </div>
                 </div>

                 <!-- Others Group -->
                 <div class="grid grid-cols-2 gap-8">
                    <!-- PM10 -->
                    <div>
                       <div class="text-sm font-medium mb-3">PM10</div>
                       <div class="flex flex-col gap-2">
                           <div v-for="(item, idx) in pm10Levels" :key="idx" class="flex items-center gap-2 text-xs text-white/80">
                              <div class="w-2 h-2 rounded-full shrink-0" :class="item.color"></div>
                              <span>{{ item.label }}</span>
                           </div>
                       </div>
                    </div>
                    <!-- TVOC -->
                    <div>
                       <div class="text-sm font-medium mb-3">TVOC</div>
                       <div class="flex flex-col gap-2">
                           <div v-for="(item, idx) in tvocLevels" :key="idx" class="flex items-center gap-2 text-xs text-white/80">
                              <div class="w-2 h-2 rounded-full shrink-0" :class="item.color"></div>
                              <span>{{ item.label }}</span>
                           </div>
                       </div>
                    </div>
                    <!-- HCHO -->
                    <div>
                       <div class="text-sm font-medium mb-3">甲醛</div>
                       <div class="flex flex-col gap-2">
                           <div v-for="(item, idx) in hchoLevels" :key="idx" class="flex items-center gap-2 text-xs text-white/80">
                              <div class="w-2 h-2 rounded-full shrink-0" :class="item.color"></div>
                              <span>{{ item.label }}</span>
                           </div>
                       </div>
                    </div>
                 </div>
              </div>
           </BaseCard>
        </div>
      </div>

      <!-- Bottom Nav -->
      <div class="flex justify-center mt-6 shrink-0">
         <button 
           @click="handleHome"
           class="bg-[#2a2a2a] hover:bg-[#333] text-white px-8 py-3 rounded-full flex items-center gap-3 transition-colors border border-white/10"
         >
           <Home class="w-5 h-5" />
           <span class="text-lg">返回首页</span>
         </button>
      </div>

    </div>
</template>

<style scoped>
/* Custom scrollbar for table if needed */
::-webkit-scrollbar {
  width: 4px;
  height: 4px;
}
::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}
</style>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { AppConfig } from '../config'
import { useCockpitStore } from '../stores/cockpit'
import AppBackground from '../components/AppBackground.vue'
import BaseCard from '../components/BaseCard.vue'
import AppLogo from '../components/AppLogo.vue'
import TimeWidget from '../components/TimeWidget.vue'
import VScaleScreen from 'v-scale-screen'
import { 
  Home, Wind, Thermometer, Droplet, Sun, Moon, 
  CloudRain, Eye, Gauge, Activity
} from 'lucide-vue-next'

const router = useRouter()
const store = useCockpitStore()

const handleHome = () => {
  // If used in a drawer, emitting an event or just closing might be handled by parent
  // But here we can also emit 'close' if this component is used inside a drawer
  emit('close')
}

const emit = defineEmits(['close'])

</script>

<template>
    <!-- Main Container -->
    <div class="relative z-10 w-full h-full text-white flex flex-col p-8 overflow-hidden">
      
      <!-- Header -->
      <header class="flex justify-between items-start mb-6 shrink-0">
        <AppLogo />
        <TimeWidget />
      </header>

      <!-- Grid Content -->
      <div class="flex-1 grid grid-cols-4 grid-rows-3 gap-6 min-h-0">
        
        <!-- Row 1 -->
        <!-- Temperature -->
        <BaseCard class="bg-[#1e1e1e]/60 border-white/5 flex flex-col justify-between !p-5">
           <div class="flex items-center gap-2 text-white/60 text-sm">
             <Thermometer class="w-4 h-4" /> 温度
           </div>
           <div class="flex items-baseline mt-2">
             <span class="text-6xl font-medium">12</span>
             <span class="text-2xl text-white/60">°</span>
           </div>
           <div class="mt-auto">
             <div class="text-lg mb-1">下降 ↘</div>
             <div class="text-xs text-white/60 leading-relaxed">
               持续降温，将于 下午11:00 达到最低气温 9°。上午 3:00 达到夜间最低 8°。
             </div>
           </div>
        </BaseCard>

        <!-- Feels Like -->
        <BaseCard class="bg-[#1e1e1e]/60 border-white/5 flex flex-col justify-between !p-5">
           <div class="flex items-center gap-2 text-white/60 text-sm">
             <Thermometer class="w-4 h-4" /> 体感温度
           </div>
           <div class="flex items-baseline mt-2">
             <span class="text-6xl font-medium">15</span>
             <span class="text-2xl text-white/60">°</span>
           </div>
           <div class="text-sm text-white/60">温度 12°</div>
           <div class="mt-auto">
             <div class="text-lg mb-1">舒适 ↘</div>
             <div class="text-xs text-white/60 leading-relaxed">
               由于湿度原因，感觉比实际温度更暖和。
             </div>
           </div>
        </BaseCard>

        <!-- Wind -->
        <BaseCard class="col-span-2 bg-[#1e1e1e]/60 border-white/5 flex flex-col !p-5">
           <div class="flex items-center gap-2 text-white/60 text-sm mb-4">
             <Wind class="w-4 h-4" /> 风速
           </div>
           <div class="flex justify-between items-start mb-4">
              <div class="flex flex-col">
                 <div class="flex items-baseline gap-2">
                   <span class="text-5xl font-medium">3</span>
                   <span class="text-sm text-white/60">公里/小时</span>
                 </div>
                 <div class="text-xs text-white/60 mt-1">风向: WSW</div>
              </div>
              <div class="flex flex-col text-right">
                 <div class="flex items-baseline gap-2 justify-end">
                   <span class="text-5xl font-medium">8</span>
                   <span class="text-sm text-white/60">公里/小时</span>
                 </div>
                 <div class="text-xs text-white/60 mt-1">阵风</div>
              </div>
              <!-- Compass Graphic Placeholder -->
              <div class="w-24 h-24 rounded-full border border-white/10 flex items-center justify-center relative">
                 <div class="absolute top-1 text-[10px] text-white/60">北</div>
                 <div class="absolute bottom-1 text-[10px] text-white/60">南</div>
                 <div class="absolute left-1 text-[10px] text-white/60">西</div>
                 <div class="absolute right-1 text-[10px] text-white/60">东</div>
                 <Wind class="w-8 h-8 text-white/40" />
              </div>
           </div>
           <div class="mt-auto border-t border-white/10 pt-3">
             <div class="text-lg mb-1">风力：1 (软风) ~</div>
             <div class="text-xs text-white/60 leading-relaxed">
               风力稳定，西南偏南 风预计到夜间保持平均风速 2 公里/小时 (阵风风速为 8)。
             </div>
           </div>
        </BaseCard>

        <!-- Row 2 -->
        <!-- Precipitation -->
        <BaseCard class="bg-[#1e1e1e]/60 border-white/5 flex flex-col justify-between !p-5">
           <div class="flex items-center gap-2 text-white/60 text-sm">
             <CloudRain class="w-4 h-4" /> 降水
           </div>
           <div class="flex items-baseline mt-2">
             <span class="text-6xl font-medium">0</span>
             <span class="text-sm text-white/60 ml-2">毫米</span>
           </div>
           <div class="text-xs text-white/60">接下来 24 小时</div>
           <div class="mt-auto">
             <div class="text-lg mb-1">无降水 ~</div>
             <div class="text-xs text-white/60 leading-relaxed">
               未来 24 小时没有降水。
             </div>
           </div>
        </BaseCard>

        <!-- Humidity -->
        <BaseCard class="bg-[#1e1e1e]/60 border-white/5 flex flex-col justify-between !p-5 relative">
           <div class="flex items-center gap-2 text-white/60 text-sm">
             <Droplet class="w-4 h-4" /> 湿度
           </div>
           <div class="flex items-baseline mt-2">
             <span class="text-6xl font-medium">71</span>
             <span class="text-2xl text-white/60">%</span>
           </div>
           <!-- Simple Gauge -->
           <div class="absolute top-6 right-6 w-16 h-16 rounded-full border-4 border-white/10 border-t-blue-400 transform rotate-45"></div>

           <div class="mt-auto">
             <div class="text-lg mb-1">普通 ↗</div>
             <div class="text-xs text-white/60 leading-relaxed">
               持续升高，在 下午7:00 达到 82% 的最高值。
             </div>
           </div>
        </BaseCard>

        <!-- UV Index -->
        <BaseCard class="bg-[#1e1e1e]/60 border-white/5 flex flex-col justify-between !p-5 relative">
           <div class="flex items-center gap-2 text-white/60 text-sm">
             <Sun class="w-4 h-4" /> 紫外线
           </div>
           <div class="flex items-baseline mt-2">
             <span class="text-6xl font-medium">1</span>
           </div>
           <!-- Simple Gauge -->
           <div class="absolute top-6 right-6 w-16 h-16 rounded-full border-4 border-white/10 border-l-yellow-400"></div>

           <div class="mt-auto">
             <div class="text-lg mb-1">低 ~</div>
             <div class="text-xs text-white/60 leading-relaxed">
               今天的最大紫外线照射量较低，预计出现在 下午 4:15。
             </div>
           </div>
        </BaseCard>

        <!-- AQI -->
        <BaseCard class="bg-[#1e1e1e]/60 border-white/5 flex flex-col justify-between !p-5 relative">
           <div class="flex items-center gap-2 text-white/60 text-sm">
             <Activity class="w-4 h-4" /> AQI
           </div>
           <div class="flex items-baseline mt-2">
             <span class="text-6xl font-medium">58</span>
           </div>
           <!-- Simple Gauge -->
           <div class="absolute top-6 right-6 w-16 h-16 rounded-full border-4 border-white/10 border-r-green-400"></div>

           <div class="mt-auto">
             <div class="text-lg mb-1">良 ↘</div>
             <div class="text-xs text-white/60 leading-relaxed">
               空气质量有恶化趋势，主要污染物：PM2.5 6.4 μg/m³。
             </div>
           </div>
        </BaseCard>

        <!-- Row 3 -->
        <!-- Visibility -->
        <BaseCard class="bg-[#1e1e1e]/60 border-white/5 flex flex-col justify-between !p-5">
           <div class="flex items-center gap-2 text-white/60 text-sm">
             <Eye class="w-4 h-4" /> 能见度
           </div>
           <div class="flex items-baseline mt-2">
             <span class="text-6xl font-medium">16</span>
             <span class="text-sm text-white/60 ml-2">公里</span>
           </div>
           <div class="mt-auto">
             <div class="text-lg mb-1">极好 ↘</div>
             <div class="text-xs text-white/60 leading-relaxed">
               能见度不断降低，预计在 下午4:15 达到最低值 16 公里。
             </div>
           </div>
        </BaseCard>

        <!-- Pressure -->
        <BaseCard class="bg-[#1e1e1e]/60 border-white/5 flex flex-col justify-between !p-5 relative">
           <div class="flex items-center gap-2 text-white/60 text-sm">
             <Gauge class="w-4 h-4" /> 气压
           </div>
           <div class="flex items-baseline mt-2">
             <span class="text-5xl font-medium">1023</span>
             <span class="text-sm text-white/60 ml-1">hPa</span>
           </div>
           <!-- Simple Gauge -->
           <div class="absolute top-8 right-6 w-12 h-8 border-t-2 border-white/20 rounded-t-full"></div>

           <div class="mt-auto">
             <div class="text-lg mb-1">缓慢下降 ↘</div>
             <div class="text-xs text-white/60 leading-relaxed">
               在过去 3 小时内缓慢下降。预计在接下来的 3 小时内将下降。
             </div>
           </div>
        </BaseCard>

        <!-- Sun -->
        <BaseCard class="bg-[#1e1e1e]/60 border-white/5 flex flex-col justify-between !p-5">
           <div class="flex items-center gap-2 text-white/60 text-sm">
             <Sun class="w-4 h-4" /> 太阳
           </div>
           <!-- Sun Graph Placeholder -->
           <div class="flex-1 flex items-center justify-center relative my-2">
              <div class="w-full h-16 border-t border-white/20 rounded-t-[50%] relative overflow-hidden">
                 <div class="absolute bottom-0 left-0 w-full h-full bg-gradient-to-t from-yellow-500/10 to-transparent"></div>
                 <div class="absolute top-0 left-1/4 w-3 h-3 bg-yellow-400 rounded-full shadow-[0_0_10px_rgba(250,204,21,0.5)]"></div>
              </div>
              <div class="absolute bottom-0 text-xs text-white/60">10 小时 25 分钟</div>
           </div>
           <div class="flex justify-between items-end">
              <div>
                <div class="text-2xl font-medium">07:18</div>
                <div class="text-xs text-white/60">日出</div>
              </div>
              <div class="text-right">
                <div class="text-2xl font-medium">17:44</div>
                <div class="text-xs text-white/60">日落</div>
              </div>
           </div>
        </BaseCard>

        <!-- Moon -->
        <BaseCard class="bg-[#1e1e1e]/60 border-white/5 flex flex-col justify-between !p-5">
           <div class="flex items-center gap-2 text-white/60 text-sm">
             <Moon class="w-4 h-4" /> 月亮
           </div>
           <!-- Moon Graph Placeholder -->
           <div class="flex-1 flex items-center justify-center relative my-2">
              <div class="w-full h-16 border-t border-white/20 rounded-t-[50%] relative overflow-hidden">
                 <div class="absolute bottom-0 left-0 w-full h-full bg-gradient-to-t from-blue-500/10 to-transparent"></div>
                 <div class="absolute top-0 left-3/4 w-3 h-3 bg-gray-300 rounded-full"></div>
              </div>
              <div class="absolute bottom-0 text-xs text-white/60">10 小时 6 分钟</div>
           </div>
           <div class="flex justify-between items-end">
              <div>
                <div class="text-2xl font-medium">04:01</div>
                <div class="text-xs text-white/60">月出</div>
              </div>
              <div class="text-right">
                <div class="text-2xl font-medium">14:07</div>
                <div class="text-xs text-white/60">月落</div>
              </div>
           </div>
        </BaseCard>

        <!-- Moon Phase (Small extra card, merging with Moon or as separate? Image shows 4 columns, let's stick to grid) -->
        <!-- Note: Image actually has 4 cards in last row, but grid is 4 columns. 
             Wait, image row 3 has: Visibility, Pressure, Sun, Moon. 
             Bottom row left is Moon Phase. 
             It seems the grid is flexible. Let's add Moon Phase as a 5th item in row 3 or separate row?
             The image shows 3 rows.
             Row 1: Temp, FeelsLike, Wind (2 cols) -> Total 4 cols.
             Row 2: Precip, Humid, UV, AQI -> Total 4 cols.
             Row 3: Vis, Press, Sun, Moon -> Total 4 cols.
             Row 4 (Bottom-left): Moon Phase.
             Let's add a 4th row for Moon Phase if needed or fit it. 
             The image description says "Bottom row, middle-right card: Moon", "Bottom row, left card: Moon Phase".
             Actually looking at image_1 description again:
             Third row: Visibility, Pressure, Sun. (3 cards)
             Bottom row: Moon Phase, Moon.
             
             Let's re-examine the image crop/layout visually from description.
             Row 1: Temp, Feels Like, Wind(wide?) -> Wind looks wide in description "Left value... Right value...". Yes, Wind takes 2 cols.
             Row 2: Precip, Humid, UV, AQI. (4 cols)
             Row 3: Vis, Press, Sun, Moon. (4 cols)
             Row 4: Moon Phase? 
             
             Let's stick to a standard grid. I will put Moon Phase in a new row or alongside others.
             Let's assume a 4-column grid.
             Row 1: Temp(1), Feels(1), Wind(2)
             Row 2: Precip(1), Humid(1), UV(1), AQI(1)
             Row 3: Vis(1), Press(1), Sun(1), Moon(1)
             Row 4: Moon Phase(1)
        -->
        
      </div>

      <!-- Bottom Nav -->
      <div class="flex justify-center mt-6 shrink-0">
         <button 
           @click="handleHome"
           class="bg-[#2a2a2a] hover:bg-[#333] text-white px-8 py-3 rounded-full flex items-center gap-3 transition-colors border border-white/10"
         >
           <Home class="w-5 h-5" />
           <span class="text-lg">返回首页</span>
         </button>
      </div>

    </div>
</template>

<style scoped>
</style>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { AppConfig } from '../config'
import { useCockpitStore } from '../stores/cockpit'
import AppBackground from '../components/AppBackground.vue'
import BaseCard from '../components/BaseCard.vue'
import AppLogo from '../components/AppLogo.vue'
import TimeWidget from '../components/TimeWidget.vue'
import VScaleScreen from 'v-scale-screen'
import { 
  Home, FileText, User, Cloud
} from 'lucide-vue-next'

// Mock QR Code Image (Replace with actual QR code resource if available)
const qrCodeUrl = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=ServiceRequest'

const router = useRouter()
const store = useCockpitStore()

const handleHome = () => {
  emit('close')
}

const emit = defineEmits(['close'])

const serviceCards = [
  {
    title: '报事报修',
    subtitle: 'Scan for admin service',
    desc: '故障/清洁/维修“码上报单”',
    icon: FileText,
    bgIcon: 'document'
  },
    {
    title: '保洁服务',
    subtitle: 'Scan for admin service',
    desc: '故障/清洁/维修“码上报单”',
    icon: FileText,
    bgIcon: 'document'
  },
  {
    title: '楼层管家',
    subtitle: 'floor butler',
    desc: '有问题直接找楼长 Tel: 130000000',
    icon: User,
    bgIcon: 'person'
  },
  {
    title: '行政服务',
    subtitle: 'administrative services',
    desc: '行政服务咨询 Tel：130000000',
    icon: Cloud,
    bgIcon: 'cloud'
  }
]

</script>

<template>

    <!-- Main Container -->
    <div class="relative z-10 w-full h-full text-white overflow-hidden flex flex-col p-8 bg-black/90">
      
      <!-- Top Header -->
      <header class="flex justify-between items-start mb-10 px-2">
        <div class="flex items-center gap-4">
           <AppLogo />
           <div class="h-8 w-px bg-white/20"></div>
           <h1 class="text-2xl font-bold tracking-wide">综合服务</h1>
        </div>
        <TimeWidget />
      </header>

      <!-- Content Grid -->
      <div class="flex-1 grid grid-cols-2 gap-8 px-10 pb-10 min-h-0">
         
         <!-- Left Column -->
         <div class="flex flex-col gap-8">
            <BaseCard 
              v-for="(card, index) in serviceCards.slice(0, 2)" 
              :key="index"
              className="flex-1 !bg-[#1e1e1e] !border-none !rounded-2xl relative overflow-hidden group"
            >
               <div class="absolute right-0 top-0 bottom-0 w-1/3 bg-white/5 rounded-l-full transform translate-x-1/4 scale-150 opacity-20 group-hover:scale-125 transition-transform duration-700"></div>
               <div class="absolute right-10 top-1/2 -translate-y-1/2 text-white/5">
                  <component :is="card.icon" class="w-40 h-40" />
               </div>

               <div class="h-full flex items-center p-10 gap-8 relative z-10">
                  <!-- QR Code -->
                  <div class="w-40 h-40 bg-white rounded-xl p-2 shrink-0 flex items-center justify-center shadow-lg">
                     <img :src="qrCodeUrl" class="w-full h-full object-contain" />
                  </div>
                  
                  <!-- Text Info -->
                  <div class="flex flex-col h-full justify-center gap-2">
                     <div>
                        <h2 class="text-4xl font-bold mb-1">{{ card.title }}</h2>
                        <p class="text-[#FF5C4D] text-sm">{{ card.subtitle }}</p>
                     </div>
                     <p class="text-white/60 text-xl mt-2">{{ card.desc }}</p>
                     <p class="text-white/30 text-xs mt-auto">请使用企业微信扫描二维码</p>
                  </div>
               </div>
            </BaseCard>
         </div>

         <!-- Right Column -->
         <div class="flex flex-col justify-start gap-8">
            <BaseCard 
              v-for="(card, index) in serviceCards.slice(2)" 
              :key="index"
              className="h-[48%] !bg-[#1e1e1e] !border-none !rounded-2xl relative overflow-hidden group"
            >
               <div class="absolute right-0 top-0 bottom-0 w-1/3 bg-white/5 rounded-l-full transform translate-x-1/4 scale-150 opacity-20 group-hover:scale-125 transition-transform duration-700"></div>
               <div class="absolute right-10 top-1/2 -translate-y-1/2 text-white/5">
                  <component :is="card.icon" class="w-40 h-40" />
               </div>

               <div class="h-full flex items-center p-10 gap-8 relative z-10">
                  <!-- QR Code -->
                  <div class="w-40 h-40 bg-white rounded-xl p-2 shrink-0 flex items-center justify-center shadow-lg">
                     <img :src="qrCodeUrl" class="w-full h-full object-contain" />
                  </div>
                  
                  <!-- Text Info -->
                  <div class="flex flex-col h-full justify-center gap-2">
                     <div>
                        <h2 class="text-4xl font-bold mb-1">{{ card.title }}</h2>
                        <p class="text-[#FF5C4D] text-sm">{{ card.subtitle }}</p>
                     </div>
                     <p class="text-white/60 text-xl mt-2">{{ card.desc }}</p>
                     <p class="text-white/30 text-xs mt-auto">请使用企业微信扫描二维码</p>
                  </div>
               </div>
            </BaseCard>
         </div>

      </div>

      <!-- Bottom Nav -->
      <div class="flex justify-center mt-6 shrink-0">
         <button 
           @click="handleHome"
           class="bg-[#2a2a2a] hover:bg-[#333] text-white px-8 py-3 rounded-full flex items-center gap-3 transition-colors border border-white/10"
         >
           <Home class="w-5 h-5" />
           <span class="text-lg">返回首页</span>
         </button>
      </div>

    </div>
</template>

<style scoped>
</style>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Brain, Check, Home } from 'lucide-vue-next'

const levels = [
  { level: 4, label: '感知控制', active: true },
  { level: 3, label: '理解控制', active: true },
  { level: 2, label: '定时控制', active: true },
  { level: 1, label: '远程运维', active: true }
]

const leftCards = [
  {
    title: 'AI算法控制',
    content: '极氪智慧楼宇按照智能化L5级标准建设，通过物联网数据中台向业务和60余的数据存储、清洗对接建模机制等，不断优化AI算法来完成L5级楼宇智能。'
  },
  {
    title: '配置场景数：65种',
    content: '配置场景条件进行智能化控制，如迎宾场景联动等应用'
  },
  {
    title: '可落地物联数：5个',
    content: '过程进行运维管理，避免运维难题'
  }
]

const rightCards = [
  {
    title: '工作传感器数：342个',
    content: '上万个传感器可对楼宇的空气、环境、能耗指标实时监测和调控'
  },
  {
    title: '运行策略数：13个',
    content: '通过AI洞察设备自动进行调节，确保制冷与耗能和体验的最佳平衡点'
  }
]

const emit = defineEmits<{
  (e: 'close'): void
}>()

const handleHome = () => {
  emit('close')
}
</script>

<template>
  <div class="relative w-full h-full bg-[#0a0f16] text-white p-8 overflow-hidden flex flex-col">
    <!-- Close Button -->
    <div class="absolute top-8 right-8 z-50 cursor-pointer" @click="emit('close')">
      <div class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-colors">
        <span class="text-xl">×</span>
      </div>
    </div>

    <!-- Title -->

    <div class="flex-1 relative flex">
      <!-- Left Column: Levels -->
      <div class="w-64 flex flex-col gap-8 relative z-10">
        <!-- Level 5 (Active) -->
        <div class="flex flex-col gap-2">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-orange-500 flex items-center justify-center">
              <Brain class="w-5 h-5 text-white" />
            </div>
            <span class="text-lg font-bold">智能化等级 Lv.5</span>
          </div>
          <span class="text-white/60 text-sm pl-11">自我学习控制</span>
        </div>

        <!-- Vertical Line -->
        <div class="absolute left-4 top-10 bottom-0 w-[1px] border-l border-dashed border-white/20"></div>

        <!-- Other Levels -->
        <div class="flex flex-col gap-8 mt-2">
          <div v-for="lvl in levels" :key="lvl.level" class="flex flex-col gap-2">
            <div class="flex items-center gap-3 relative">
              <div class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center z-10">
                <Check class="w-4 h-4 text-white/60" />
              </div>
              <span class="text-lg font-bold text-white/60">智能化等级 Lv.{{ lvl.level }}</span>
            </div>
            <span class="text-white/40 text-sm pl-11">{{ lvl.label }}</span>
          </div>
        </div>
      </div>

      <!-- Center Area with Building and Cards -->
      <div class="flex-1 relative flex justify-center items-center -mt-20 z-0">
        <!-- Building Image -->
        <div class="relative w-[600px] h-[1200px] flex items-center justify-center z-0 pointer-events-none">
           <!-- Inline SVG Building -->
           <svg width="100%" height="100%" viewBox="0 0 1447 949" fill="none" xmlns="http://www.w3.org/2000/svg" class="opacity-80 scale-150">
             <path d="M697 948.406L753.5 16.4064L111 464.906L0 928.406L697 948.406Z" fill="#2C2C2C"/>
             <path d="M119.5 457.906L112.5 462.406L40 774.406L46 772.906L119.5 457.906Z" fill="#444444"/>
             <path d="M108.5 462.906L101.5 467.906L28.5 775.906H34L108.5 462.906Z" fill="#444444"/>
             <path d="M146.5 438.406L139 443.406L63 770.406L70 769.406L146.5 438.406Z" fill="#444444"/>
             <path d="M179 414.906L168.5 422.406L89 765.906L98 764.406L179 414.906Z" fill="#444444"/>
             <path d="M212.5 390.906L201.5 398.906L122 760.906L131 759.906L212.5 390.906Z" fill="#444444"/>
             <path d="M247.5 366.906L238 371.406L156.5 755.406L166 753.906L247.5 366.906Z" fill="#444444"/>
             <path d="M288 336.906L276.5 344.906L195.5 749.406L207.5 747.406L288 336.906Z" fill="#444444"/>
             <path d="M335 303.406L321 313.406L241 741.906L254.5 739.906L335 303.406Z" fill="#444444"/>
             <path d="M387.5 265.906L373 276.406L294 733.406L309 730.906L387.5 265.906Z" fill="#444444"/>
             <path d="M447 222.406L431.5 233.906L355 723.906L373.5 720.906L447 222.406Z" fill="#444444"/>
             <path d="M519.5 171.406L501 185.406L427 712.906L449.5 708.406L519.5 171.406Z" fill="#444444"/>
             <path d="M601 111.906L578 128.406L536 510.406L561.5 502.906L601 111.906Z" fill="#444444"/>
             <path d="M698.5 41.4064L672.5 60.4064L640 474.406L669.5 464.906L698.5 41.4064Z" fill="#444444"/>
             <path d="M113.5 459.906L106.5 464.406L34 776.406L40 774.906L113.5 459.906Z" fill="#626262"/>
             <path d="M102.5 464.906L95.5 469.906L22.5 777.906H28L102.5 464.906Z" fill="#626262"/>
             <path d="M140.5 440.406L133 445.406L57 772.406L64 771.406L140.5 440.406Z" fill="#626262"/>
             <path d="M173 416.906L162.5 424.406L83 767.906L92 766.406L173 416.906Z" fill="#626262"/>
             <path d="M206.5 392.906L195.5 400.906L116 762.906L125 761.906L206.5 392.906Z" fill="#626262"/>
             <path d="M241.5 368.906L232 373.406L150.5 757.406L160 755.906L241.5 368.906Z" fill="#626262"/>
             <path d="M282 338.906L270.5 346.906L189.5 751.406L201.5 749.406L282 338.906Z" fill="#626262"/>
             <path d="M329 305.406L315 315.406L235 743.906L248.5 741.906L329 305.406Z" fill="#626262"/>
             <path d="M381.5 267.906L367 278.406L288 735.406L303 732.906L381.5 267.906Z" fill="#626262"/>
             <path d="M441 224.406L425.5 235.906L349 725.906L367.5 722.906L441 224.406Z" fill="#626262"/>
             <path d="M513.5 173.406L495 187.406L421 714.906L443.5 710.406L513.5 173.406Z" fill="#626262"/>
             <path d="M595 113.906L572 130.406L530 512.406L555.5 504.906L595 113.906Z" fill="#626262"/>
             <path d="M692.5 43.4064L666.5 62.4064L634 476.406L663.5 466.906L692.5 43.4064Z" fill="#626262"/>
             <path d="M1379.5 459.406L755 18.4064L695 947.906H1442L1379.5 459.406Z" fill="#202020"/>
             <path d="M754.5 0.406403L34.5 516.406" stroke="#FA6262"/>
             <path d="M754.5 0.406403L714.5 28.4064L646.5 946.406L697 948.406L754.5 0.406403Z" fill="#626262"/>
             <path d="M794.5 28.4064L754 0.406403L696.5 947.906H748.5L794.5 28.4064Z" fill="#434343"/>
             <path d="M1365 442.906L1376 450.906L1439.5 946.406L1428.5 946.906L1365 442.906Z" fill="black"/>
             <path d="M1329 416.906L1338.5 421.406L1398 946.906H1389.5L1329 416.906Z" fill="black"/>
             <path d="M1285 386.906L1296.5 394.906L1354 947.406H1343L1285 386.906Z" fill="black"/>
             <path d="M1236.5 352.906L1250.5 362.906L1289.5 766.906L1271 765.906L1236.5 352.906Z" fill="black"/>
             <path d="M1179 312.906L1193.5 323.406L1220.5 639.906L1204 634.406L1179 312.906Z" fill="black"/>
             <path d="M1117 268.906L1133.5 280.906L1154.5 615.406L1135 608.906L1117 268.906Z" fill="black"/>
             <path d="M1042 215.906L1063.5 230.906L1077.5 587.906L1057 580.406L1042 215.906Z" fill="black"/>
             <path d="M960.5 156.406L983.5 172.906L989.5 555.906L963.5 546.906L960.5 156.406Z" fill="black"/>
             <path d="M863 85.9064L889 104.906L883.5 516.406L853 505.406L863 85.9064Z" fill="black"/>
             <path d="M1372 442.906L1383 450.906L1446.5 946.406L1435.5 946.906L1372 442.906Z" fill="#434343"/>
             <path d="M1336 416.906L1345.5 421.406L1405 946.906H1396.5L1336 416.906Z" fill="#434343"/>
             <path d="M1292 386.906L1303.5 394.906L1361 947.406H1350L1292 386.906Z" fill="#434343"/>
             <path d="M1243.5 352.906L1257.5 362.906L1296.5 766.906L1278 765.906L1243.5 352.906Z" fill="#434343"/>
             <path d="M1186 312.906L1200.5 323.406L1227.5 639.906L1211 634.406L1186 312.906Z" fill="#434343"/>
             <path d="M1124 268.906L1140.5 280.906L1161.5 615.406L1142 608.906L1124 268.906Z" fill="#434343"/>
             <path d="M1049 215.906L1070.5 230.906L1084.5 587.906L1064 580.406L1049 215.906Z" fill="#434343"/>
             <path d="M967.5 156.406L990.5 172.906L996.5 555.906L970.5 546.906L967.5 156.406Z" fill="#434343"/>
             <path d="M870 85.9064L896 104.906L890.5 516.406L860 505.406L870 85.9064Z" fill="#434343"/>
           </svg>
        </div>

        <!-- Left Cards -->
        <div class="absolute left-0 top-0 bottom-0 flex flex-col justify-center gap-16 w-80 z-10 pointer-events-none">
          <div v-for="(card, idx) in leftCards" :key="idx" 
               class="bg-[#1a2332]/90 backdrop-blur-md p-6 rounded-r-lg border-l-4 border-orange-500 relative group pointer-events-auto">
            <h3 class="font-bold text-lg mb-2">{{ card.title }}</h3>
            <p class="text-sm text-white/60 leading-relaxed">{{ card.content }}</p>
            
            <!-- Connector Line (Left) -->
            <div class="absolute right-0 top-1/2 w-24 h-[1px] border-t border-dashed border-blue-400/50 translate-x-full hidden lg:block">
              <div class="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-blue-400"></div>
            </div>
          </div>
        </div>

        <!-- Right Cards -->
        <div class="absolute right-0 top-0 bottom-0 flex flex-col justify-center gap-32 w-80 z-10 pointer-events-none">
          <div v-for="(card, idx) in rightCards" :key="idx" 
               class="bg-[#1a2332]/90 backdrop-blur-md p-6 rounded-l-lg border-r-4 border-orange-500 relative group text-right pointer-events-auto">
            <h3 class="font-bold text-lg mb-2">{{ card.title }}</h3>
            <p class="text-sm text-white/60 leading-relaxed">{{ card.content }}</p>

            <!-- Connector Line (Right) -->
            <div class="absolute left-0 top-1/2 w-24 h-[1px] border-t border-dashed border-blue-400/50 -translate-x-full hidden lg:block">
              <div class="absolute left-0 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-blue-400"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom scrollbar if needed */
::-webkit-scrollbar {
  width: 0px;
}
</style>

```

