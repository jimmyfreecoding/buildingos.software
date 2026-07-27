# 源代码提交页（智能楼宇智慧运营系统 buildingos.ioc）

## 前30页

```typescript
// ============================================================
// 文件: src/api/operations.ts
// 智能楼宇智慧运营系统 - 数据中心（Mock APIs）
// ============================================================

const mock = (data: any) => new Promise<any>((r) => setTimeout(() => r({ code: '200', msg: 'success', data }), 300))

// ==================== 安防看板 ====================

export const getSecurityOverview = () =>
  mock({
    todayAlarms: 23,
    pendingAlarms: 5,
    onlineCameras: 128,
    offlineCameras: 3,
    securityPersonnel: 18,
    patrolRoutes: 12,
  })

export const getAlarmTrend24h = () =>
  mock([
    { hour: '00:00', count: 2, handled: 2 },
    { hour: '01:00', count: 1, handled: 1 },
    { hour: '02:00', count: 0, handled: 0 },
    { hour: '03:00', count: 1, handled: 1 },
    { hour: '04:00', count: 0, handled: 0 },
    { hour: '05:00', count: 2, handled: 1 },
    { hour: '06:00', count: 3, handled: 3 },
    { hour: '07:00', count: 5, handled: 4 },
    { hour: '08:00', count: 8, handled: 7 },
    { hour: '09:00', count: 12, handled: 11 },
    { hour: '10:00', count: 10, handled: 9 },
    { hour: '11:00', count: 7, handled: 7 },
    { hour: '12:00', count: 5, handled: 5 },
    { hour: '13:00', count: 6, handled: 5 },
    { hour: '14:00', count: 9, handled: 8 },
    { hour: '15:00', count: 11, handled: 10 },
    { hour: '16:00', count: 8, handled: 8 },
    { hour: '17:00', count: 6, handled: 6 },
    { hour: '18:00', count: 4, handled: 4 },
    { hour: '19:00', count: 3, handled: 3 },
    { hour: '20:00', count: 2, handled: 2 },
    { hour: '21:00', count: 1, handled: 1 },
    { hour: '22:00', count: 1, handled: 1 },
    { hour: '23:00', count: 0, handled: 0 },
  ])

export const getAlarmTypeDistribution = () =>
  mock([
    { type: '入侵检测', count: 45, color: '#F56C6C' },
    { type: '火灾预警', count: 12, color: '#E6A23C' },
    { type: '门禁异常', count: 38, color: '#409EFF' },
    { type: '视频离线', count: 15, color: '#909399' },
    { type: '周界报警', count: 28, color: '#67C23A' },
    { type: '设备故障', count: 20, color: '#B37FEB' },
  ])

export const getCameraStatusList = () =>
  mock([
    { id: 'c-1', name: 'A栋大厅-东', area: 'A栋1F', status: 'online', lastCheck: '2026-07-11 10:30:15' },
    { id: 'c-2', name: 'A栋大厅-西', area: 'A栋1F', status: 'online', lastCheck: '2026-07-11 10:30:12' },
    { id: 'c-3', name: 'B栋入口', area: 'B栋1F', status: 'online', lastCheck: '2026-07-11 10:30:10' },
    { id: 'c-4', name: 'C栋停车场入口', area: 'C栋B1', status: 'offline', lastCheck: '2026-07-11 08:15:00' },
    { id: 'c-5', name: '园区南门', area: '园区户外', status: 'online', lastCheck: '2026-07-11 10:30:18' },
    { id: 'c-6', name: '园区北门', area: '园区户外', status: 'online', lastCheck: '2026-07-11 10:30:05' },
  ])

export const getRecentSecurityEvents = () =>
  mock([
    { id: 'e-1', time: '2026-07-11 10:28:00', type: '入侵检测', area: 'B栋2F', level: '高', status: '处理中', desc: 'B栋2F消防通道异常闯入' },
    { id: 'e-2', time: '2026-07-11 10:15:00', type: '门禁异常', area: 'A栋3F', level: '中', status: '处理中', desc: 'A栋3F门禁多次刷卡失败' },
    { id: 'e-3', time: '2026-07-11 09:50:00', type: '周界报警', area: '园区南门', level: '低', status: '已处理', desc: '南门周界传感器触发' },
    { id: 'e-4', time: '2026-07-11 09:30:00', type: '设备故障', area: 'C栋B1', level: '中', status: '处理中', desc: 'C栋B1摄像头离线' },
    { id: 'e-5', time: '2026-07-11 09:00:00', type: '火灾预警', area: 'A栋5F', level: '高', status: '已处理', desc: 'A栋5F烟雾传感器告警' },
    { id: 'e-6', time: '2026-07-11 08:30:00', type: '入侵检测', area: 'B栋1F', level: '中', status: '已处理', desc: 'B栋1F非授权人员进入' },
  ])

// ==================== 告警看板 ====================

export const getAlarmOverview = () =>
  mock({
    totalAlarms: 158,
    handledAlarms: 132,
    processingAlarms: 15,
    pendingAlarms: 11,
    responseRate: 94.3,
    avgResponseTime: 3.2,
  })

export const getAlarmTrendWeekly = () =>
  mock([
    { date: '07/05', count: 22, handled: 19 },
    { date: '07/06', count: 18, handled: 16 },
    { date: '07/07', count: 25, handled: 22 },
    { date: '07/08', count: 20, handled: 18 },
    { date: '07/09', count: 28, handled: 25 },
    { date: '07/10', count: 24, handled: 22 },
    { date: '07/11', count: 23, handled: 21 },
  ])

export const getAlarmBySource = () =>
  mock([
    { source: '视频分析', count: 42 },
    { source: '传感器', count: 38 },
    { source: '门禁系统', count: 30 },
    { source: '手动上报', count: 25 },
    { source: '巡检发现', count: 15 },
    { source: '系统自检', count: 8 },
  ])

export const getAlarmByArea = () =>
  mock([
    { area: 'A栋', count: 45 },
    { area: 'B栋', count: 38 },
    { area: 'C栋', count: 32 },
    { area: '园区户外', count: 28 },
    { area: '地下车库', count: 15 },
  ])

export const getAlarmList = (params?: any) => {
  let list = [
    { id: 'al-1', time: '2026-07-11 10:28:00', type: '入侵检测', area: 'B栋2F', source: '视频分析', level: '高', status: '处理中', handler: '张安保', desc: '消防通道异常闯入' },
    { id: 'al-2', time: '2026-07-11 10:15:00', type: '门禁异常', area: 'A栋3F', source: '门禁系统', level: '中', status: '处理中', handler: '李安保', desc: '门禁多次刷卡失败' },
    { id: 'al-3', time: '2026-07-11 09:50:00', type: '周界报警', area: '园区南门', source: '传感器', level: '低', status: '已处理', handler: '王安保', desc: '周界传感器触发' },
    { id: 'al-4', time: '2026-07-11 09:30:00', type: '设备故障', area: 'C栋B1', source: '系统自检', level: '中', status: '处理中', handler: '赵技术', desc: '摄像头离线' },
    { id: 'al-5', time: '2026-07-11 09:00:00', type: '火灾预警', area: 'A栋5F', source: '传感器', level: '高', status: '已处理', handler: '张安保', desc: '烟雾传感器告警' },
    { id: 'al-6', time: '2026-07-11 08:30:00', type: '入侵检测', area: 'B栋1F', source: '视频分析', level: '中', status: '已处理', handler: '李安保', desc: '非授权人员进入' },
    { id: 'al-7', time: '2026-07-11 07:50:00', type: '设备故障', area: 'A栋2F', source: '巡检发现', level: '低', status: '已处理', handler: '赵技术', desc: '门禁读卡器故障' },
    { id: 'al-8', time: '2026-07-10 18:00:00', type: '周界报警', area: '园区北门', source: '传感器', level: '低', status: '已处理', handler: '王安保', desc: '北门异常开启' },
  ]
  if (params?.status) list = list.filter((a) => a.status === params.status)
  if (params?.level) list = list.filter((a) => a.level === params.level)
  if (params?.area) list = list.filter((a) => a.area === params.area)
  if (params?.type) list = list.filter((a) => a.type === params.type)
  const total = list.length
  const start = ((params?.pageNo || 1) - 1) * (params?.pageSize || 10)
  return mock({ list: list.slice(start, start + (params?.pageSize || 10)), total })
}

// ==================== 通行看板 ====================

export const getPassageOverview = () =>
  mock({
    todayVehicleFlow: 1856,
    vehicleFlowChange: 12.5,
    parkingOccupancy: 78,
    parkingTotal: 500,
    parkingAvailable: 110,
    peopleOnSite: 2340,
    peopleDensity: 65,
    todayVisitors: 89,
  })

export const getVehicleTrend = () =>
  mock([
    { hour: '06:00', enter: 20, exit: 5 },
    { hour: '07:00', enter: 85, exit: 20 },
    { hour: '08:00', enter: 180, exit: 35 },
    { hour: '09:00', enter: 120, exit: 60 },
    { hour: '10:00', enter: 60, exit: 65 },
    { hour: '11:00', enter: 45, exit: 55 },
    { hour: '12:00', enter: 55, exit: 70 },
    { hour: '13:00', enter: 65, exit: 50 },
    { hour: '14:00', enter: 40, exit: 45 },
    { hour: '15:00', enter: 35, exit: 40 },
    { hour: '16:00', enter: 50, exit: 80 },
    { hour: '17:00', enter: 30, exit: 160 },
    { hour: '18:00', enter: 15, exit: 120 },
    { hour: '19:00', enter: 10, exit: 55 },
  ])

export const getPeopleDensityByArea = () =>
  mock([
    { area: 'A栋1F', count: 320, density: 85 },
    { area: 'A栋3F', count: 180, density: 60 },
    { area: 'B栋1F', count: 250, density: 72 },
    { area: 'B栋2F', count: 200, density: 58 },
    { area: 'C栋1F', count: 280, density: 78 },
    { area: 'C栋5F', count: 150, density: 45 },
    { area: '餐厅', count: 420, density: 92 },
    { area: '地下车库', count: 180, density: 35 },
  ])

export const getRecentVehicleRecords = () =>
  mock([
    { id: 'vr-1', plate: '京A·12345', type: '临时车', enterTime: '2026-07-11 10:25:00', exitTime: '', area: 'A栋B1', status: '在场' },
    { id: 'vr-2', plate: '京B·67890', type: '月租车', enterTime: '2026-07-11 10:20:00', exitTime: '2026-07-11 10:50:00', area: 'B栋B1', status: '已出场' },
    { id: 'vr-3', plate: '京C·11111', type: '访客车', enterTime: '2026-07-11 10:15:00', exitTime: '', area: 'A栋B1', status: '在场' },
    { id: 'vr-4', plate: '京D·22222', type: '月租车', enterTime: '2026-07-11 10:10:00', exitTime: '', area: 'C栋B1', status: '在场' },
    { id: 'vr-5', plate: '京E·33333', type: 'VIP', enterTime: '2026-07-11 10:05:00', exitTime: '2026-07-11 11:30:00', area: 'A栋B1', status: '已出场' },
  ])

// ==================== 环境看板 ====================

export const getEnvironmentOverview = () =>
  mock({
    avgTemperature: 24.5,
    avgHumidity: 55,
    aqi: 68,
    aqiLevel: '良',
    noiseLevel: 52,
    pm25: 35,
    co2: 580,
    tvoc: 0.08,
  })

export const getTemperatureTrend = () =>
  mock({
    areas: ['A栋', 'B栋', 'C栋'],
    hours: ['06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00'],
    data: {
      A栋: [22, 22.5, 23, 23.5, 24, 24.5, 25, 25.5, 25, 24.5, 24, 23.5, 23, 22.5, 22],
      B栋: [21.5, 22, 22.5, 23, 23.5, 24, 24.5, 25, 24.5, 24, 23.5, 23, 22.5, 22, 21.5],
      C栋: [23, 23, 23.5, 24, 24.5, 25, 25.5, 26, 25.5, 25, 24.5, 24, 23.5, 23, 22.5],
    },
  })

export const getEnvironmentSensors = () =>
  mock([
    { id: 's-1', area: 'A栋1F', temp: 24.2, humidity: 54, pm25: 32, co2: 550, noise: 50, status: 'normal' },
    { id: 's-2', area: 'A栋3F', temp: 24.8, humidity: 56, pm25: 38, co2: 620, noise: 55, status: 'normal' },
    { id: 's-3', area: 'B栋1F', temp: 23.5, humidity: 52, pm25: 30, co2: 500, noise: 48, status: 'normal' },
    { id: 's-4', area: 'B栋2F', temp: 25.1, humidity: 58, pm25: 42, co2: 680, noise: 60, status: 'warning' },
    { id: 's-5', area: 'C栋1F', temp: 24.0, humidity: 53, pm25: 33, co2: 540, noise: 51, status: 'normal' },
    { id: 's-6', area: 'C栋5F', temp: 25.5, humidity: 60, pm25: 45, co2: 720, noise: 62, status: 'warning' },
    { id: 's-7', area: '餐厅', temp: 26.0, humidity: 62, pm25: 40, co2: 850, noise: 70, status: 'warning' },
    { id: 's-8', area: '地下车库', temp: 28.0, humidity: 70, pm25: 55, co2: 950, noise: 45, status: 'abnormal' },
  ])

// ==================== 餐厅看板 ====================

export const getRestaurantOverview = () =>
  mock({
    currentDiners: 420,
    seatingOccupancy: 72,
    totalSeats: 580,
    todayTotalMeals: 1680,
    avgQueueTime: 8,
    peakHours: '11:30-12:30',
  })

export const getDiningTrend = () =>
  mock([
    { hour: '07:00', count: 80 }, { hour: '07:30', count: 150 }, { hour: '08:00', count: 220 },
    { hour: '08:30', count: 180 }, { hour: '09:00', count: 60 }, { hour: '11:00', count: 100 },
    { hour: '11:30', count: 320 }, { hour: '12:00', count: 420 }, { hour: '12:30', count: 350 },
    { hour: '13:00', count: 200 }, { hour: '13:30', count: 80 }, { hour: '17:00', count: 60 },
    { hour: '17:30', count: 160 }, { hour: '18:00', count: 280 }, { hour: '18:30', count: 220 },
    { hour: '19:00', count: 100 },
  ])

export const getDiningAreaDistribution = () =>
  mock([
    { area: '中餐区', count: 220, total: 300, rate: 73 },
    { area: '西餐区', count: 80, total: 120, rate: 67 },
    { area: '面点区', count: 60, total: 80, rate: 75 },
    { area: '饮品区', count: 35, total: 50, rate: 70 },
    { area: '户外区', count: 25, total: 30, rate: 83 },
  ])

export const getWeeklyDiningStats = () =>
  mock([
    { day: '周一', breakfast: 320, lunch: 580, dinner: 280 },
    { day: '周二', breakfast: 350, lunch: 620, dinner: 300 },
    { day: '周三', breakfast: 330, lunch: 600, dinner: 290 },
    { day: '周四', breakfast: 340, lunch: 590, dinner: 310 },
    { day: '周五', breakfast: 310, lunch: 560, dinner: 250 },
    { day: '周六', breakfast: 150, lunch: 200, dinner: 120 },
    { day: '周日', breakfast: 120, lunch: 180, dinner: 100 },
  ])

export const getTodayMenu = () =>
  mock([
    { id: 'menu-1', name: '红烧肉', price: 18, category: '中餐', sales: 120, rating: 4.5 },
    { id: 'menu-2', name: '清蒸鲈鱼', price: 25, category: '中餐', sales: 85, rating: 4.8 },
    { id: 'menu-3', name: '意大利面', price: 22, category: '西餐', sales: 60, rating: 4.3 },
    { id: 'menu-4', name: '牛肉拉面', price: 15, category: '面点', sales: 150, rating: 4.6 },
    { id: 'menu-5', name: '蔬菜沙拉', price: 12, category: '西餐', sales: 45, rating: 4.2 },
    { id: 'menu-6', name: '宫保鸡丁', price: 16, category: '中餐', sales: 110, rating: 4.4 },
  ])

// ==================== 会议看板 ====================

export const getMeetingOverview = () =>
  mock({
    todayMeetings: 48,
    inProgress: 8,
    roomUsageRate: 72.5,
    totalParticipants: 320,
    upcomingMeetings: 15,
    avgMeetingDuration: 65,
  })

export const getRoomUsage = () =>
  mock([
    { room: 'A栋3F-301', capacity: 20, status: 'in_use', meeting: '产品评审会', until: '11:30' },
    { room: 'A栋3F-302', capacity: 10, status: 'in_use', meeting: '周例会', until: '10:30' },
    { room: 'A栋3F-303', capacity: 8, status: 'available', meeting: '', until: '' },
    { room: 'B栋2F-201', capacity: 30, status: 'in_use', meeting: '全员大会', until: '12:00' },
    { room: 'B栋2F-202', capacity: 12, status: 'available', meeting: '', until: '' },
    { room: 'B栋2F-203', capacity: 15, status: 'in_use', meeting: '客户演示', until: '11:00' },
    { room: 'C栋5F-501', capacity: 25, status: 'in_use', meeting: '技术研讨会', until: '12:30' },
    { room: 'C栋5F-502', capacity: 10, status: 'booked', meeting: '面试', until: '14:00' },
    { room: 'C栋5F-503', capacity: 8, status: 'available', meeting: '', until: '' },
    { room: 'A栋1F-101', capacity: 40, status: 'maintenance', meeting: '', until: '' },
  ])

export const getMeetingDeptStats = () =>
  mock([
    { dept: '技术部', count: 15, hours: 32 },
    { dept: '市场部', count: 10, hours: 22 },
    { dept: '产品部', count: 12, hours: 28 },
    { dept: '行政部', count: 5, hours: 8 },
    { dept: '财务部', count: 3, hours: 5 },
    { dept: '人事部', count: 3, hours: 6 },
  ])

export const getCurrentMeetings = () =>
  mock([
    { id: 'cm-1', room: 'A栋3F-301', subject: 'Q3产品评审会', dept: '产品部', host: '张产品', startTime: '09:30', endTime: '11:30', participants: 15 },
    { id: 'cm-2', room: 'A栋3F-302', subject: '技术部周例会', dept: '技术部', host: '李技术', startTime: '09:00', endTime: '10:30', participants: 8 },
    { id: 'cm-3', room: 'B栋2F-201', subject: '全员季度总结', dept: '行政部', host: '赵行政', startTime: '10:00', endTime: '12:00', participants: 30 },
    { id: 'cm-4', room: 'B栋2F-203', subject: '客户方案演示', dept: '市场部', host: '陈市场', startTime: '09:30', endTime: '11:00', participants: 10 },
    { id: 'cm-5', room: 'C栋5F-501', subject: 'AI技术研讨会', dept: '技术部', host: '王技术', startTime: '09:00', endTime: '12:30', participants: 20 },
  ])

export const getMeetingTrendWeekly = () =>
  mock([
    { day: '周一', count: 52, usageRate: 78 },
    { day: '周二', count: 48, usageRate: 72 },
    { day: '周三', count: 55, usageRate: 82 },
    { day: '周四', count: 50, usageRate: 75 },
    { day: '周五', count: 42, usageRate: 65 },
    { day: '周六', count: 8, usageRate: 15 },
    { day: '周日', count: 5, usageRate: 10 },
  ])
```

```vue
<!-- ============================================================
文件: src/views/operate/operations/security/index.vue
智能楼宇智慧运营系统 - 安防看板
============================================================ -->
<template>
  <div class="security-dashboard">
    <!-- Summary Cards Row -->
    <el-row :gutter="16" class="summary-row">
      <el-col v-for="card in summaryCards" :key="card.label" :span="4">
        <div class="summary-card" :style="{ borderLeftColor: card.color }">
          <div class="card-icon" :style="{ color: card.color }" v-html="card.icon" />
          <div class="card-content">
            <div class="card-value" :style="{ color: card.color }">{{ card.value }}</div>
            <div class="card-label">{{ card.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Grid: Left (30%) + Right (70%) -->
    <div class="dashboard-grid">
      <!-- Left Column: Camera Status List -->
      <div class="grid-left">
        <vab-card title="摄像头状态">
          <el-table :data="cameraStatusList" style="width: 100%" size="small" :show-header="true" max-height="320" stripe>
            <el-table-column prop="name" label="名称" min-width="120" />
            <el-table-column prop="area" label="位置" min-width="80" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'online' ? 'success' : 'danger'" size="small" effect="plain">
                  {{ row.status === 'online' ? '在线' : '离线' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="lastCheck" label="最后检测" min-width="130" />
          </el-table>
        </vab-card>
      </div>

      <!-- Right Column -->
      <div class="grid-right">
        <!-- 24h Alarm Trend Chart -->
        <vab-card title="24小时告警趋势">
          <v-chart :option="alarmTrendOption" autoresize style="height: 280px; width: 100%" />
        </vab-card>

        <!-- Bottom Row: Pie + Events (50/50) -->
        <div class="grid-bottom-row">
          <!-- Alarm Type Pie -->
          <vab-card title="告警类型分布">
            <v-chart :option="alarmTypeOption" autoresize style="height: 280px; width: 100%" />
          </vab-card>

          <!-- Recent Events -->
          <vab-card title="最近安全事件">
            <el-table :data="recentSecurityEvents" style="width: 100%" size="small" :show-header="true" max-height="320" stripe>
              <el-table-column prop="time" label="时间" min-width="140" />
              <el-table-column prop="type" label="类型" width="80">
                <template #default="{ row }">
                  <el-tag size="small" effect="plain">{{ row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="area" label="区域" min-width="80" />
              <el-table-column prop="level" label="级别" width="70">
                <template #default="{ row }">
                  <el-tag :type="row.level === '高' ? 'danger' : row.level === '中' ? 'warning' : 'info'" size="small" effect="dark">
                    {{ row.level }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="desc" label="描述" min-width="120" show-overflow-tooltip />
              <el-table-column prop="status" label="状态" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.status === '已处理' ? 'success' : 'warning'" size="small" effect="plain">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </vab-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, inject } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, BarChart, LineChart, PieChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])
import {
  getSecurityOverview,
  getAlarmTrend24h,
  getAlarmTypeDistribution,
  getCameraStatusList,
  getRecentSecurityEvents,
} from '/@/api/operations'
import { ElMessage } from 'element-plus'

defineOptions({
  name: 'OperationsSecurity',
})

const $baseMessage = inject<any>('$baseMessage')

// ── SVG icon strings for summary cards ──
const SVG_ICONS = {
  alarm: '<svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor"><path d="M12 2L1 21h22L12 2zm0 4l7.53 13H4.47L12 6zm-1 8h2v2h-2v-2zm0-6h2v4h-2V8z"/></svg>',
  pending: '<svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
  cameraOnline: '<svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
  cameraOffline: '<svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor"><path d="M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm5 13.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12 17 15.59z"/></svg>',
  personnel: '<svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>',
  patrol: '<svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor"><path d="M15.5 5.5c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zM5 12c-2.8 0-5 2.2-5 5s2.2 5 5 5 5-2.2 5-5-2.2-5-5-5zm0 8.5c-1.9 0-3.5-1.6-3.5-3.5s1.6-3.5 3.5-3.5 3.5 1.6 3.5 3.5-1.6 3.5-3.5 3.5zm9.8-1.8l-3.9-3.9 1.4-1.4 2.5 2.5 5.1-5.9 1.5 1.3-6.6 7.4zM10.9 5.5c-.5-.5-1.1-.8-1.7-.9L9 2h4l-.2 2.6c-.6.1-1.2.4-1.7.9l-2.5 2.5 2.5 2.5c.5.5 1.1.8 1.7.9l.2 2.6H9l.2-2.6c-.6-.1-1.2-.4-1.7-.9l-2.5-2.5 2.5-2.5z"/></svg>',
}

// ── State ──
const summaryCards = ref<{ label: string; value: number; color: string; icon: string }[]>([])
const cameraStatusList = ref<any[]>([])
const recentSecurityEvents = ref<any[]>([])
const alarmTrendOption = ref<any>({})
const alarmTypeOption = ref<any>({})

// ── Load Data ──
const loadData = async () => {
  try {
    const [overviewRes, alarmTrendRes, alarmTypeRes, cameraRes, eventsRes] = await Promise.all([
      getSecurityOverview(),
      getAlarmTrend24h(),
      getAlarmTypeDistribution(),
      getCameraStatusList(),
      getRecentSecurityEvents(),
    ])

    const overview = overviewRes.data ?? overviewRes
    const alarmTrend = alarmTrendRes.data ?? alarmTrendRes
    const alarmType = alarmTypeRes.data ?? alarmTypeRes
    const cameras = cameraRes.data ?? cameraRes
    const events = eventsRes.data ?? eventsRes

    // Populate summary cards
    summaryCards.value = [
      { label: '今日告警', value: overview.todayAlarms, color: '#F56C6C', icon: SVG_ICONS.alarm },
      { label: '待处理', value: overview.pendingAlarms, color: '#E6A23C', icon: SVG_ICONS.pending },
      { label: '在线摄像头', value: overview.onlineCameras, color: '#67C23A', icon: SVG_ICONS.cameraOnline },
      { label: '离线摄像头', value: overview.offlineCameras, color: '#909399', icon: SVG_ICONS.cameraOffline },
      { label: '安保人员', value: overview.securityPersonnel, color: '#409EFF', icon: SVG_ICONS.personnel },
      { label: '巡逻路线', value: overview.patrolRoutes, color: '#B37FEB', icon: SVG_ICONS.patrol },
    ]

    cameraStatusList.value = cameras
    recentSecurityEvents.value = events
    alarmTrendOption.value = buildAlarmTrendOption(alarmTrend)
    alarmTypeOption.value = buildAlarmTypeOption(alarmType)
  } catch (err) {
    const msg = $baseMessage?.error ?? ElMessage.error
    msg('加载安防看板数据失败')
    console.error(err)
  }
}

// ── Build ECharts Options ──
const buildAlarmTrendOption = (data: any[]) => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
  legend: { data: ['告警数', '已处理'], top: 0, left: 'center', icon: 'roundRect', itemWidth: 12, itemHeight: 8 },
  grid: { left: '3%', right: '4%', bottom: '3%', top: '40px', containLabel: true },
  xAxis: { type: 'category', data: data.map((d: any) => d.hour), axisLabel: { fontSize: 10, rotate: 45 } },
  yAxis: { type: 'value', minInterval: 1 },
  series: [
    { name: '告警数', type: 'bar', data: data.map((d: any) => d.count), itemStyle: { color: '#409EFF' }, barMaxWidth: 16 },
    { name: '已处理', type: 'line', data: data.map((d: any) => d.handled), smooth: true, lineStyle: { color: '#67C23A', width: 2 }, itemStyle: { color: '#67C23A' }, symbol: 'circle', symbolSize: 6 },
  ],
})

const buildAlarmTypeOption = (data: any[]) => ({
  tooltip: {
    trigger: 'item',
    formatter: (params: any) => {
      const total = data.reduce((s: number, d: any) => s + d.count, 0)
      const pct = ((params.value / total) * 100).toFixed(1)
      return `${params.name}<br/>数量: ${params.value}<br/>占比: ${pct}%`
    },
  },
  legend: { orient: 'vertical', right: '5%', top: 'center', itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 12 } },
  series: [{
    type: 'pie', radius: ['40%', '70%'], center: ['35%', '50%'], avoidLabelOverlap: false,
    label: { show: true, formatter: '{b}: {d}%', fontSize: 11 },
    emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
    labelLine: { show: true },
    data: data.map((d: any) => ({ name: d.type, value: d.count, itemStyle: { color: d.color } })),
  }],
})

onMounted(() => { loadData() })
</script>

<style scoped lang="scss">
.security-dashboard {
  height: 100vh; width: 100%; padding: 16px; box-sizing: border-box;
  background: #f0f2f5; overflow-y: auto; overflow-x: hidden;

  .summary-row { margin-bottom: 16px; .el-col { padding: 0 6px; } }

  .summary-card {
    display: flex; align-items: center; padding: 16px 14px;
    background: #fff; border-radius: 8px; border-left: 4px solid;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: box-shadow 0.3s;
    &:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
    .card-icon { display: flex; align-items: center; justify-content: center; width: 44px; height: 44px; flex-shrink: 0; margin-right: 12px; border-radius: 8px; background: rgba(0,0,0,0.03); }
    .card-content { flex: 1; min-width: 0; }
    .card-value { font-size: 24px; font-weight: 700; line-height: 1.2; }
    .card-label { font-size: 13px; color: #909399; margin-top: 4px; }
  }

  .dashboard-grid { display: grid; grid-template-columns: 30% 70%; gap: 16px; }
  .grid-left { display: flex; flex-direction: column; }
  .grid-right { display: flex; flex-direction: column; gap: 16px; }
  .grid-bottom-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

  :deep(.el-table) {
    font-size: 12px;
    .el-table__header th { background: #fafafa; font-weight: 600; color: #606266; }
    .el-table__body tr { transition: background 0.2s; }
    .el-tag { --el-tag-font-size: 11px; }
  }
}
</style>
```

```vue
<!-- ============================================================
文件: src/views/operate/operations/alarm/index.vue
智能楼宇智慧运营系统 - 告警看板
============================================================ -->
<template>
  <div class="alarm-dashboard">
    <!-- Filter Bar -->
    <vab-query-form>
      <vab-query-form-top-panel>
        <el-form inline :model="queryForm" @submit.prevent>
          <el-form-item label="日期范围">
            <el-date-picker v-model="queryForm.dateRange" type="daterange" value-format="YYYY-MM-DD"
              range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" clearable />
          </el-form-item>
          <el-form-item label="级别">
            <el-select v-model="queryForm.level" placeholder="全部" clearable style="width: 100px">
              <el-option v-for="item in levelOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="queryForm.status" placeholder="全部" clearable style="width: 110px">
              <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="区域">
            <el-select v-model="queryForm.area" placeholder="全部" clearable style="width: 110px">
              <el-option v-for="item in areaOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="类型">
            <el-select v-model="queryForm.type" placeholder="全部" clearable style="width: 110px">
              <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button :icon="Search" type="primary" :loading="loading" @click="handleQuery">查询</el-button>
            <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </vab-query-form-top-panel>
    </vab-query-form>

    <!-- 6 Summary Cards -->
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col v-for="card in summaryCards" :key="card.label" :span="4">
        <div class="summary-card" :style="{ borderLeftColor: card.color }">
          <div class="card-icon" :style="{ color: card.color, backgroundColor: card.color + '15' }">
            <el-icon :size="24"><component :is="card.icon" /></el-icon>
          </div>
          <div class="card-content">
            <div class="card-value" :style="{ color: card.color }">{{ card.value }}</div>
            <div class="card-label">{{ card.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="8">
        <vab-card title="告警趋势（近7日）">
          <v-chart :option="trendOption" autoresize style="height: 300px; width: 100%" />
        </vab-card>
      </el-col>
      <el-col :span="8">
        <vab-card title="告警来源">
          <v-chart :option="sourceOption" autoresize style="height: 300px; width: 100%" />
        </vab-card>
      </el-col>
      <el-col :span="8">
        <vab-card title="区域分布">
          <v-chart :option="areaOption" autoresize style="height: 300px; width: 100%" />
        </vab-card>
      </el-col>
    </el-row>

    <!-- Alarm Events Table -->
    <div style="margin-top: 16px">
      <vab-card title="告警事件列表">
        <el-table v-loading="tableLoading" :data="tableData" border stripe style="width: 100%">
          <el-table-column prop="time" label="时间" width="170" align="center" />
          <el-table-column prop="type" label="类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="typeTagType(row.type)" size="small" effect="plain">{{ row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="area" label="区域" width="100" align="center" />
          <el-table-column prop="source" label="来源" width="105" align="center" />
          <el-table-column prop="level" label="级别" width="75" align="center">
            <template #default="{ row }">
              <el-tag :type="levelTagType(row.level)" size="small" effect="dark">{{ row.level }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="85" align="center">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="handler" label="处理人" width="85" align="center">
            <template #default="{ row }">{{ row.handler || '-' }}</template>
          </el-table-column>
          <el-table-column prop="desc" label="描述" min-width="200" />
          <template #empty><el-empty class="vab-data-empty" description="暂无数据" /></template>
        </el-table>
        <div style="margin-top: 16px; display: flex; justify-content: flex-end">
          <vab-pagination :current-page="pagination.pageNo" :page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]" :total="total" layout="total, sizes, prev, pager, next, jumper"
            @current-change="handlePageChange" @size-change="handleSizeChange" />
        </div>
      </vab-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, inject } from 'vue'
import { Search, Refresh, WarningFilled, CircleCheckFilled, Clock, CircleCloseFilled, DataAnalysis, Timer } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, BarChart, LineChart, PieChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])
import { getAlarmOverview, getAlarmTrendWeekly, getAlarmBySource, getAlarmByArea, getAlarmList } from '/@/api/operations'

defineOptions({ name: 'OperationsAlarm' })

const baseMessage = inject('$baseMessage', ElMessage)

const overview = ref<any>({})
const trendData = ref<any[]>([])
const sourceData = ref<any[]>([])
const areaData = ref<any[]>([])
const tableData = ref<any[]>([])
const total = ref(0)
const tableLoading = ref(false)
const loading = ref(false)

const queryForm = reactive({ dateRange: null as string[] | null, level: '', status: '', area: '', type: '' })
const pagination = reactive({ pageNo: 1, pageSize: 10 })

const summaryCards = computed(() => [
  { label: '总告警', value: overview.value?.totalAlarms ?? 0, color: '#409EFF', icon: WarningFilled },
  { label: '已处理', value: overview.value?.handledAlarms ?? 0, color: '#67C23A', icon: CircleCheckFilled },
  { label: '处理中', value: overview.value?.processingAlarms ?? 0, color: '#E6A23C', icon: Clock },
  { label: '未处理', value: overview.value?.pendingAlarms ?? 0, color: '#F56C6C', icon: CircleCloseFilled },
  { label: '响应率', value: `${overview.value?.responseRate ?? 0}%`, color: '#B37FEB', icon: DataAnalysis },
  { label: '平均响应', value: `${overview.value?.avgResponseTime ?? 0}min`, color: '#00B4D8', icon: Timer },
])

const levelOptions = [{ value: '高', label: '高' }, { value: '中', label: '中' }, { value: '低', label: '低' }]
const statusOptions = [{ value: '已处理', label: '已处理' }, { value: '处理中', label: '处理中' }, { value: '未处理', label: '未处理' }]
const areaOptions = [{ value: 'A栋', label: 'A栋' }, { value: 'B栋', label: 'B栋' }, { value: 'C栋', label: 'C栋' }, { value: '园区户外', label: '园区户外' }, { value: '地下车库', label: '地下车库' }]
const typeOptions = [{ value: '入侵检测', label: '入侵检测' }, { value: '火灾预警', label: '火灾预警' }, { value: '门禁异常', label: '门禁异常' }, { value: '设备故障', label: '设备故障' }, { value: '周界报警', label: '周界报警' }]

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
  legend: { data: ['总告警数', '已处理数'], top: 0 },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', data: trendData.value.map((d) => d.date), axisLabel: { rotate: 0 } },
  yAxis: { type: 'value', minInterval: 1 },
  series: [
    { name: '总告警数', type: 'bar', data: trendData.value.map((d) => d.count), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] }, barWidth: 22 },
    { name: '已处理数', type: 'line', data: trendData.value.map((d) => d.handled), smooth: true, lineStyle: { color: '#67C23A', width: 3 }, itemStyle: { color: '#67C23A' }, symbol: 'circle', symbolSize: 8 },
  ],
}))

const sourceColors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#B37FEB', '#00B4D8']
const sourceOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { show: false },
  grid: { left: '3%', right: '6%', bottom: '3%', containLabel: true },
  xAxis: { type: 'value', minInterval: 1 },
  yAxis: { type: 'category', data: sourceData.value.map((d) => d.source).reverse(), axisLabel: { fontSize: 12 } },
  series: [{ type: 'bar', data: sourceData.value.map((d, i) => ({ value: d.count, itemStyle: { color: sourceColors[i] } })).reverse(), barWidth: 20, label: { show: true, position: 'right', fontWeight: 'bold' } }],
}))

const areaColors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#B37FEB']
const areaOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { orient: 'vertical', right: '5%', top: 'center', textStyle: { fontSize: 12 } },
  series: [{ type: 'pie', radius: ['40%', '70%'], center: ['42%', '50%'], avoidLabelOverlap: false, label: { show: true, formatter: '{b}\n{d}%', fontSize: 11 }, emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } }, data: areaData.value.map((d, i) => ({ name: d.area, value: d.count, itemStyle: { color: areaColors[i] } })) }],
}))

const typeTagType = (type: string): string => {
  const map: Record<string, string> = { 入侵检测: 'danger', 火灾预警: 'danger', 门禁异常: 'warning', 设备故障: 'info', 周界报警: 'warning' }
  return map[type] || 'info'
}
const levelTagType = (level: string): string => { const map: Record<string, string> = { 高: 'danger', 中: 'warning', 低: 'info' }; return map[level] || 'info' }
const statusTagType = (status: string): string => { const map: Record<string, string> = { 已处理: 'success', 处理中: 'warning', 未处理: 'danger' }; return map[status] || 'info' }

const fetchOverview = async () => { try { const { data } = await getAlarmOverview(); overview.value = data } catch { baseMessage.error('获取告警概览失败') } }
const fetchTrend = async () => { try { const { data } = await getAlarmTrendWeekly(); trendData.value = data } catch { baseMessage.error('获取趋势数据失败') } }
const fetchSource = async () => { try { const { data } = await getAlarmBySource(); sourceData.value = data } catch { baseMessage.error('获取来源数据失败') } }
const fetchArea = async () => { try { const { data } = await getAlarmByArea(); areaData.value = data } catch { baseMessage.error('获取区域数据失败') } }

const fetchAlarmList = async () => {
  tableLoading.value = true
  try {
    const params: Record<string, any> = { pageNo: pagination.pageNo, pageSize: pagination.pageSize }
    if (queryForm.level) params.level = queryForm.level
    if (queryForm.status) params.status = queryForm.status
    if (queryForm.area) params.area = queryForm.area
    if (queryForm.type) params.type = queryForm.type
    const { data } = await getAlarmList(params)
    tableData.value = data.list; total.value = data.total
  } catch { baseMessage.error('获取告警列表失败') } finally { tableLoading.value = false }
}

const fetchAllData = async () => { loading.value = true; await Promise.all([fetchOverview(), fetchTrend(), fetchSource(), fetchArea(), fetchAlarmList()]); loading.value = false }
const handleQuery = () => { pagination.pageNo = 1; fetchAlarmList() }
const handleReset = () => { queryForm.dateRange = null; queryForm.level = ''; queryForm.status = ''; queryForm.area = ''; queryForm.type = ''; pagination.pageNo = 1; pagination.pageSize = 10; fetchAllData() }
const handlePageChange = (page: number) => { pagination.pageNo = page; fetchAlarmList() }
const handleSizeChange = (size: number) => { pagination.pageSize = size; pagination.pageNo = 1; fetchAlarmList() }

onMounted(() => { fetchAllData() })
</script>

<style lang="scss" scoped>
.alarm-dashboard { padding: 16px; height: 100%; overflow-y: auto; background: #f0f2f5; min-height: 100%; }
.summary-card { display: flex; align-items: center; padding: 18px 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-left: 4px solid; background: #fff; transition: transform 0.25s ease, box-shadow 0.25s ease; cursor: default;
  &:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.1); } }
.card-icon { display: flex; align-items: center; justify-content: center; width: 48px; height: 48px; border-radius: 12px; margin-right: 16px; flex-shrink: 0; }
.card-content { flex: 1; min-width: 0; }
.card-value { font-size: 24px; font-weight: 700; line-height: 1.3; font-variant-numeric: tabular-nums; }
.card-label { font-size: 13px; color: #909399; margin-top: 2px; }
</style>
```

## 后30页

```vue
<!-- ============================================================
文件: src/views/operate/operations/passage/index.vue
智能楼宇智慧运营系统 - 通行看板
============================================================ -->
<template>
  <div class="operations-passage-container">
    <!-- 4 Summary Cards -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-card-body">
            <div class="summary-info">
              <div class="summary-label">今日车流量</div>
              <div class="summary-value">{{ overview.todayVehicleFlow }}</div>
              <div class="summary-change" :class="overview.vehicleFlowChange >= 0 ? 'up' : 'down'">
                <vab-icon :icon="overview.vehicleFlowChange >= 0 ? 'arrow-up-s-fill' : 'arrow-down-s-fill'" />
                {{ Math.abs(overview.vehicleFlowChange) }}%
              </div>
            </div>
            <div class="summary-icon vehicle-flow"><vab-icon icon="car-line" /></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-card-body">
            <div class="summary-info">
              <div class="summary-label">车位占用率</div>
              <div class="summary-value">{{ overview.parkingOccupancy }}%</div>
              <div class="summary-sub">{{ overview.parkingAvailable }} 个可用</div>
            </div>
            <div class="summary-icon parking-occ">
              <el-progress type="circle" :percentage="overview.parkingOccupancy" :width="72" :stroke-width="6" color="#F56C6C" />
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-card-body">
            <div class="summary-info">
              <div class="summary-label">在园人数</div>
              <div class="summary-value">{{ overview.peopleOnSite.toLocaleString() }}</div>
              <div class="summary-sub">人员密度 {{ overview.peopleDensity }}%</div>
            </div>
            <div class="summary-icon people"><vab-icon icon="group-line" /></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-card-body">
            <div class="summary-info">
              <div class="summary-label">今日访客</div>
              <div class="summary-value">{{ overview.todayVisitors }}</div>
              <div class="summary-sub">人</div>
            </div>
            <div class="summary-icon visitor"><vab-icon icon="user-add-line" /></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Middle Row: Charts -->
    <el-row :gutter="20" class="section-row">
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>车流量趋势</span>
              <div class="legend-custom">
                <span class="legend-item"><span class="dot enter" />入场</span>
                <span class="legend-item"><span class="dot exit" />出场</span>
              </div>
            </div>
          </template>
          <v-chart :option="vehicleTrendOption" autoresize style="height: 320px; width: 100%" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header><div class="card-header"><span>各区域人员密度</span></div></template>
          <v-chart :option="densityOption" autoresize style="height: 320px; width: 100%" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Bottom Row: Parking Usage + Vehicle Records Table -->
    <el-row :gutter="20" class="section-row">
      <el-col :span="10">
        <el-card class="parking-card" shadow="hover">
          <template #header><div class="card-header"><span>车位使用情况</span></div></template>
          <div class="parking-content">
            <div class="parking-donut">
              <v-chart :option="parkingOption" autoresize style="height: 160px; width: 100%" />
            </div>
            <div class="parking-summary">
              <span class="parking-text">已用 <strong>{{ overview.parkingTotal - overview.parkingAvailable }}</strong> / 总 <strong>{{ overview.parkingTotal }}</strong> 车位</span>
              <el-tag type="success" effect="plain">可用 {{ overview.parkingAvailable }}</el-tag>
            </div>
            <el-divider />
            <div class="parking-areas">
              <div v-for="area in parkingAreas" :key="area.name" class="area-bar-row">
                <span class="area-name">{{ area.name }}</span>
                <el-progress :percentage="area.rate" :stroke-width="14" :color="area.color" :format="() => `${area.used}/${area.total}`" />
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card class="table-card" shadow="hover">
          <template #header><div class="card-header"><span>最近车辆通行记录</span></div></template>
          <el-table v-loading="tableLoading" :data="vehicleRecords" border stripe style="width: 100%">
            <el-table-column label="车牌" prop="plate" min-width="120" align="center" />
            <el-table-column label="类型" prop="type" min-width="90" align="center">
              <template #default="{ row }"><el-tag :type="typeTagMap[row.type] || 'info'" size="small">{{ row.type }}</el-tag></template>
            </el-table-column>
            <el-table-column label="入场时间" prop="enterTime" min-width="170" align="center" />
            <el-table-column label="出场时间" prop="exitTime" min-width="170" align="center">
              <template #default="{ row }">{{ row.exitTime || '--' }}</template>
            </el-table-column>
            <el-table-column label="区域" prop="area" min-width="100" align="center" />
            <el-table-column label="状态" prop="status" min-width="80" align="center">
              <template #default="{ row }"><el-tag :type="row.status === '在场' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag></template>
            </el-table-column>
            <template #empty><el-empty class="vab-data-empty" description="暂无数据" /></template>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, inject } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'

echarts.use([CanvasRenderer, BarChart, LineChart, PieChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])
import { getPassageOverview, getVehicleTrend, getPeopleDensityByArea, getRecentVehicleRecords } from '/@/api/operations'

defineOptions({ name: 'OperationsPassage' })

const $baseMessage = inject<any>('$baseMessage') || ElMessage

interface PassageOverview { todayVehicleFlow: number; vehicleFlowChange: number; parkingOccupancy: number; parkingTotal: number; parkingAvailable: number; peopleOnSite: number; peopleDensity: number; todayVisitors: number }
interface VehicleTrendItem { hour: string; enter: number; exit: number }
interface DensityItem { area: string; count: number; density: number }
interface VehicleRecord { id: string; plate: string; type: string; enterTime: string; exitTime: string; area: string; status: string }
interface ParkingArea { name: string; used: number; total: number; rate: number; color: string }

const loading = ref<boolean>(false)
const tableLoading = ref<boolean>(false)

const overview = ref<PassageOverview>({ todayVehicleFlow: 0, vehicleFlowChange: 0, parkingOccupancy: 0, parkingTotal: 0, parkingAvailable: 0, peopleOnSite: 0, peopleDensity: 0, todayVisitors: 0 })
const vehicleTrend = ref<VehicleTrendItem[]>([])
const densityData = ref<DensityItem[]>([])
const vehicleRecords = ref<VehicleRecord[]>([])

const parkingAreas = computed<ParkingArea[]>(() => {
  const total = overview.value.parkingTotal
  const areaData: ParkingArea[] = [
    { name: 'A栋B1', used: 120, total: 150, rate: 0, color: '#F56C6C' },
    { name: 'B栋B1', used: 100, total: 130, rate: 0, color: '#E6A23C' },
    { name: 'C栋B1', used: 90, total: 120, rate: 0, color: '#67C23A' },
    { name: '地面停车场', used: 80, total: 100, rate: 0, color: '#409EFF' },
  ]
  const scale = total / 500
  return areaData.map((a) => ({ ...a, used: Math.round(a.used * scale), total: Math.round(a.total * scale), rate: Math.round((a.used / a.total) * 100) }))
})

const typeTagMap: Record<string, string> = { 临时车: 'info', 月租车: 'primary', 访客车: 'warning', VIP: 'danger' }

const vehicleTrendOption = computed(() => {
  const data = vehicleTrend.value; if (!data.length) return {}
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any[]) => { const hour = params[0]?.axisValue || ''; let html = `<strong>${hour}</strong><br/>`; params.forEach((p: any) => { html += `${p.marker} ${p.seriesName}: ${p.value} 辆<br/>` }); return html } },
    legend: { data: ['入场', '出场'], top: 0, icon: 'circle', itemWidth: 8, itemHeight: 8 },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: data.map((d: VehicleTrendItem) => d.hour), axisLabel: { fontSize: 11 } },
    yAxis: { type: 'value', name: '辆', nameTextStyle: { fontSize: 11 } },
    series: [
      { name: '入场', type: 'bar', data: data.map((d: VehicleTrendItem) => d.enter), barWidth: '35%', barGap: '20%', itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] } },
      { name: '出场', type: 'bar', data: data.map((d: VehicleTrendItem) => d.exit), barWidth: '35%', itemStyle: { color: '#F56C6C', borderRadius: [4, 4, 0, 0] } },
    ],
  }
})

const densityOption = computed(() => {
  const data = densityData.value; if (!data.length) return {}
  const sorted = [...data].sort((a, b) => a.density - b.density)
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any[]) => { const item = params[0]; if (!item) return ''; const row = sorted[item.dataIndex]; return `<strong>${row.area}</strong><br/>人数: ${row.count} 人<br/>密度: ${row.density}%` } },
    grid: { left: '3%', right: '8%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', name: '密度(%)', nameTextStyle: { fontSize: 11 }, max: 100 },
    yAxis: { type: 'category', data: sorted.map((d: DensityItem) => d.area), axisLabel: { fontSize: 12 } },
    series: [{ type: 'bar', data: sorted.map((d: DensityItem) => ({ value: d.density, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: '#67C23A' }, { offset: 0.5, color: '#E6A23C' }, { offset: 1, color: '#F56C6C' }]), borderRadius: [0, 4, 4, 0] } })), barWidth: 18, label: { show: true, position: 'right', formatter: '{c}%', fontSize: 11, color: '#666' } }],
  }
})

const parkingOption = computed(() => {
  const total = overview.value.parkingTotal; const available = overview.value.parkingAvailable; const used = total - available
  return {
    tooltip: { trigger: 'item', formatter: (params: any) => `${params.name}: ${params.value} 个 (${params.percent}%)` },
    series: [{ type: 'pie', radius: ['55%', '75%'], avoidLabelOverlap: false, padAngle: 2, itemStyle: { borderRadius: 4 }, label: { show: false }, emphasis: { label: { show: false }, scale: false }, data: [{ value: used, name: '已占用', itemStyle: { color: '#F56C6C' } }, { value: available, name: '空闲', itemStyle: { color: '#E8EDF2' } }] }],
  }
})

const fetchData = async () => {
  loading.value = true
  try {
    const [overviewRes, trendRes, densityRes, recordsRes] = await Promise.all([getPassageOverview(), getVehicleTrend(), getPeopleDensityByArea(), getRecentVehicleRecords()])
    overview.value = overviewRes.data; vehicleTrend.value = trendRes.data; densityData.value = densityRes.data; vehicleRecords.value = recordsRes.data
  } catch (error: any) { $baseMessage?.error(error?.msg || '获取通行看板数据失败') } finally { loading.value = false }
}

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.operations-passage-container { width: 100%; padding: 0; .section-row { margin-top: 20px; } }
.summary-card { border-radius: 8px; overflow: hidden; transition: box-shadow 0.25s ease;
  &:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
  :deep(.el-card__body) { padding: 20px; }
  .summary-card-body { display: flex; align-items: center; justify-content: space-between; }
  .summary-info { flex: 1; }
  .summary-label { font-size: 14px; color: #909399; margin-bottom: 8px; }
  .summary-value { font-size: 28px; font-weight: 700; color: #303133; line-height: 1.2; margin-bottom: 6px; }
  .summary-change { font-size: 13px; display: flex; align-items: center; gap: 2px; &.up { color: #f56c6c; } &.down { color: #67c23a; } .vab-icon { font-size: 16px; } }
  .summary-sub { font-size: 13px; color: #909399; }
  .summary-icon { width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    .vab-icon { font-size: 30px; }
    &.vehicle-flow { background: rgba(103,194,58,0.1); color: #67c23a; }
    &.parking-occ { background: transparent; width: auto; height: auto; }
    &.people { background: rgba(64,158,255,0.1); color: #409eff; }
    &.visitor { background: rgba(230,162,60,0.1); color: #e6a23c; } } }
.card-header { display: flex; align-items: center; justify-content: space-between; font-size: 15px; font-weight: 600; color: #303133;
  .legend-custom { display: flex; align-items: center; gap: 16px; font-size: 13px; font-weight: 400; color: #909399;
    .legend-item { display: flex; align-items: center; gap: 5px; }
    .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; &.enter { background: #67c23a; } &.exit { background: #f56c6c; } } } }
.chart-card { border-radius: 8px; overflow: hidden; :deep(.el-card__body) { padding: 12px; } }
.parking-card { border-radius: 8px; overflow: hidden;
  :deep(.el-card__body) { padding: 20px; }
  .parking-content { display: flex; flex-direction: column; }
  .parking-donut { display: flex; justify-content: center; margin-bottom: 12px; }
  .parking-summary { display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 8px;
    .parking-text { font-size: 14px; color: #606266; strong { font-weight: 700; color: #303133; } } }
  .parking-areas { display: flex; flex-direction: column; gap: 12px;
    .area-bar-row { display: flex; align-items: center; gap: 12px;
      .area-name { width: 88px; font-size: 13px; color: #606266; flex-shrink: 0; text-align: right; }
      .el-progress { flex: 1; } } } }
.table-card { border-radius: 8px; overflow: hidden; :deep(.el-card__body) { padding: 12px; } }
.el-divider { margin: 16px 0; }
</style>
```

```vue
<!-- ============================================================
文件: src/views/operate/operations/environment/index.vue
智能楼宇智慧运营系统 - 环境看板
============================================================ -->
<template>
  <div class="environment-dashboard">
    <!-- 8 Summary Gauge Cards -->
    <el-row :gutter="16" class="gauge-row">
      <el-col v-for="card in gaugeCards" :key="card.key" :span="3">
        <el-card shadow="hover" class="gauge-card" :style="{ borderTop: `3px solid ${card.color}` }">
          <div class="gauge-label">{{ card.label }}</div>
          <div class="gauge-value" :style="{ color: card.color }">{{ card.value }}{{ card.unit }}</div>
          <div v-if="card.subText" class="gauge-sub">{{ card.subText }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Temperature Trend Chart -->
    <el-card shadow="hover" class="section-card">
      <template #header><span class="section-title">各区域温度趋势</span></template>
      <v-chart :option="chartOption" class="trend-chart" autoresize />
    </el-card>

    <!-- Sensor Detail Table -->
    <el-card shadow="hover" class="section-card">
      <template #header><span class="section-title">环境传感器详情</span></template>
      <el-table v-loading="tableLoading" :data="sensors" border stripe style="width: 100%">
        <el-table-column label="区域" prop="area" width="140" />
        <el-table-column label="温度" width="110">
          <template #default="{ row }">
            <span :class="{ 'cell-hot': row.temp > 26 }">
              <span class="inline-dot" :style="{ background: row.temp > 26 ? '#F56C6C' : '#409EFF' }" />{{ row.temp }}°C
            </span>
          </template>
        </el-table-column>
        <el-table-column label="湿度" width="100">
          <template #default="{ row }"><span class="inline-dot" style="background: #36d399" />{{ row.humidity }}%</template>
        </el-table-column>
        <el-table-column label="PM2.5" min-width="180">
          <template #default="{ row }">
            <div class="sensor-cell">
              <span class="sensor-value" :class="{ 'cell-warn': row.pm25 > 40 }">{{ row.pm25 }}</span>
              <el-progress :percentage="Math.min(100, Math.round((row.pm25 / 75) * 100))" :color="row.pm25 > 40 ? '#E6A23C' : '#67C23A'" :stroke-width="6" style="flex: 1; margin-left: 8px" />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="CO₂" min-width="180">
          <template #default="{ row }">
            <div class="sensor-cell">
              <span class="sensor-value" :class="{ 'cell-warn': row.co2 > 800 }">{{ row.co2 }}</span>
              <el-progress :percentage="Math.min(100, Math.round((row.co2 / 2000) * 100))" :color="row.co2 > 800 ? '#E6A23C' : '#67C23A'" :stroke-width="6" style="flex: 1; margin-left: 8px" />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="噪音" width="100"><template #default="{ row }">{{ row.noise }}dB</template></el-table-column>
        <el-table-column label="状态" width="110" align="center">
          <template #default="{ row }"><el-tag :type="statusType(row.status)" size="small" effect="plain">{{ statusLabel(row.status) }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import * as echarts from 'echarts'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { getEnvironmentOverview, getTemperatureTrend, getEnvironmentSensors } from '/@/api/operations'

echarts.use([CanvasRenderer, LineChart, TooltipComponent, LegendComponent, GridComponent])

defineOptions({ name: 'OperationsEnvironment' })

interface Overview { avgTemperature: number; avgHumidity: number; aqi: number; aqiLevel: string; noiseLevel: number; pm25: number; co2: number; tvoc: number }
interface TrendData { areas: string[]; hours: string[]; data: Record<string, number[]> }
interface SensorItem { id: string; area: string; temp: number; humidity: number; pm25: number; co2: number; noise: number; status: 'normal' | 'warning' | 'abnormal' }
interface GaugeCard { key: string; label: string; value: string | number; unit: string; subText: string; color: string }

const overview = ref<Overview>({ avgTemperature: 0, avgHumidity: 0, aqi: 0, aqiLevel: '-', noiseLevel: 0, pm25: 0, co2: 0, tvoc: 0 })
const trend = ref<TrendData>({ areas: [], hours: [], data: {} })
const sensors = ref<SensorItem[]>([])
const tableLoading = ref(false)

const gaugeCards = computed<GaugeCard[]>(() => {
  const o = overview.value
  const comfortIndex = computeComfortIndex(o.avgTemperature, o.avgHumidity, o.aqi, o.pm25, o.co2, o.tvoc, o.noiseLevel)
  return [
    { key: 'temp', label: '温度', value: o.avgTemperature, unit: '°C', subText: '', color: '#409EFF' },
    { key: 'humidity', label: '湿度', value: o.avgHumidity, unit: '%', subText: '', color: '#36D399' },
    { key: 'aqi', label: 'AQI', value: o.aqi, unit: '', subText: o.aqiLevel, color: '#67C23A' },
    { key: 'pm25', label: 'PM2.5', value: o.pm25, unit: '', subText: '', color: '#E6A23C' },
    { key: 'co2', label: 'CO₂', value: o.co2, unit: 'ppm', subText: '', color: '#B37FEB' },
    { key: 'tvoc', label: 'TVOC', value: o.tvoc, unit: 'mg/m³', subText: '', color: '#FF6B81' },
    { key: 'noise', label: '噪音', value: o.noiseLevel, unit: 'dB', subText: '', color: '#FFC107' },
    { key: 'comfort', label: '舒适度', value: comfortIndex, unit: '分', subText: comfortLevel(comfortIndex), color: '#5B8FF9' },
  ]
})

const areaColors: Record<string, string> = { A栋: '#409EFF', B栋: '#67C23A', C栋: '#E6A23C' }

const chartOption = computed(() => {
  const t = trend.value
  const series = t.areas.map((area) => ({
    name: area, type: 'line' as const, data: t.data[area] || [], smooth: true,
    lineStyle: { width: 2.5, color: areaColors[area] || '#409EFF' },
    itemStyle: { color: areaColors[area] || '#409EFF' }, symbol: 'circle', symbolSize: 6,
    areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: `${areaColors[area] || '#409EFF'}30` }, { offset: 1, color: `${areaColors[area] || '#409EFF'}05` }]) },
  }))
  return {
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.95)', borderColor: '#e4e7ed', borderWidth: 1,
      formatter(params: any) { if (!params?.length) return ''; let html = `<div style="font-size:13px;font-weight:600;margin-bottom:4px">${params[0].axisValue}</div>`; params.forEach((p: any) => { html += `<div style="display:flex;align-items:center;gap:6px;margin:2px 0"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${p.color}"></span><span>${p.seriesName}：<b>${p.value}°C</b></span></div>` }); return html } },
    legend: { top: 0, data: t.areas, icon: 'circle', itemWidth: 10, itemHeight: 10 },
    grid: { left: 40, right: 30, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: t.hours, boundaryGap: false, axisLine: { lineStyle: { color: '#e4e7ed' } }, axisLabel: { color: '#909399', fontSize: 11 }, axisTick: { show: false } },
    yAxis: { type: 'value', name: '°C', nameTextStyle: { color: '#909399', fontSize: 11 }, splitLine: { lineStyle: { color: '#f0f0f0', type: 'dashed' } }, axisLabel: { color: '#909399', fontSize: 11 } },
    series,
  }
})

function computeComfortIndex(temp: number, humidity: number, aqi: number, pm25: number, co2: number, tvoc: number, noise: number): number {
  const tempScore = Math.max(0, 100 - Math.abs(temp - 22) * 5)
  const humidityScore = Math.max(0, 100 - Math.abs(humidity - 50) * 2)
  const aqiScore = Math.max(0, 100 - aqi * 1.2)
  const pm25Score = Math.max(0, 100 - pm25 * 2)
  const co2Score = Math.max(0, 100 - Math.max(0, co2 - 400) * 0.08)
  const tvocScore = Math.max(0, 100 - tvoc * 500)
  const noiseScore = Math.max(0, 100 - Math.abs(noise - 45) * 2)
  return Math.round((tempScore + humidityScore + aqiScore + pm25Score + co2Score + tvocScore + noiseScore) / 7)
}

function comfortLevel(score: number): string { if (score >= 85) return '舒适'; if (score >= 70) return '良好'; if (score >= 55) return '一般'; return '较差' }
function statusType(status: string): 'success' | 'warning' | 'danger' | 'info' { switch (status) { case 'normal': return 'success'; case 'warning': return 'warning'; case 'abnormal': return 'danger'; default: return 'info' } }
function statusLabel(status: string): string { switch (status) { case 'normal': return '正常'; case 'warning': return '告警'; case 'abnormal': return '异常'; default: return status } }

async function loadData() {
  try {
    const [overviewRes, trendRes, sensorsRes] = await Promise.all([getEnvironmentOverview(), getTemperatureTrend(), getEnvironmentSensors()])
    overview.value = overviewRes.data ?? overviewRes; trend.value = trendRes.data ?? trendRes
    tableLoading.value = true; sensors.value = sensorsRes.data ?? sensorsRes
  } catch { } finally { tableLoading.value = false }
}

onMounted(loadData)
</script>

<style lang="scss" scoped>
.environment-dashboard { padding: 16px; min-height: 100vh; background: #f5f7fa;
  .gauge-row { margin-bottom: 16px; }
  .gauge-card { border-radius: 8px; text-align: center; padding: 4px 0; transition: transform 0.2s, box-shadow 0.2s;
    &:hover { transform: translateY(-2px); }
    .gauge-label { font-size: 13px; color: #909399; margin-bottom: 6px; }
    .gauge-value { font-size: 26px; font-weight: 700; line-height: 1.3; }
    .gauge-sub { font-size: 12px; color: #909399; margin-top: 4px; } }
  .section-card { border-radius: 8px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    :deep(.el-card__header) { border-bottom: 1px solid #ebeef5; padding: 14px 20px; }
    .section-title { font-size: 15px; font-weight: 600; color: #303133; } }
  .trend-chart { width: 100%; height: 380px; }
  .sensor-cell { display: flex; align-items: center; gap: 4px; .sensor-value { font-variant-numeric: tabular-nums; min-width: 32px; } }
  .cell-hot { color: #f56c6c; font-weight: 600; }
  .cell-warn { color: #e6a23c; font-weight: 600; }
  .inline-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; vertical-align: middle; } }
</style>
```

```vue
<!-- ============================================================
文件: src/views/operate/operations/restaurant/index.vue
智能楼宇智慧运营系统 - 餐厅看板
============================================================ -->
<template>
  <div class="restaurant-dashboard">
    <!-- Summary Cards Row -->
    <el-row :gutter="16" class="summary-row">
      <el-col v-for="card in summaryCards" :key="card.label" :span="4">
        <div class="summary-card" :style="{ borderLeftColor: card.color }">
          <div class="card-content">
            <div class="card-value" :style="{ color: card.color }">{{ card.value }}</div>
            <div class="card-label">{{ card.label }}</div>
            <div v-if="card.subLabel" class="card-sublabel">{{ card.subLabel }}</div>
          </div>
          <div v-if="card.showProgress" class="card-progress" :style="{ color: card.color }">
            <svg viewBox="0 0 36 36" width="52" height="52">
              <path class="progress-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#f0f0f0" stroke-width="3" />
              <path class="progress-fill" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" :stroke="card.color" stroke-width="3" stroke-dasharray="100" :stroke-dashoffset="100 - (card.rawValue || 0)" stroke-linecap="round" />
              <text x="18" y="20.5" text-anchor="middle" font-size="8" :fill="card.color" font-weight="bold">{{ card.rawValue || card.progressValue }}%</text>
            </svg>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Middle Grid: Trend + Area + Menu -->
    <div class="dashboard-grid">
      <div class="grid-left">
        <vab-card title="就餐趋势" class="chart-card">
          <v-chart :option="diningTrendOption" autoresize style="height: 340px; width: 100%" />
        </vab-card>
      </div>
      <div class="grid-center">
        <vab-card title="各区域就餐分布" class="chart-card">
          <v-chart :option="areaDistributionOption" autoresize style="height: 340px; width: 100%" />
        </vab-card>
      </div>
      <div class="grid-right">
        <vab-card title="今日菜单" class="menu-card">
          <el-table :data="todayMenu" style="width: 100%" size="small" :show-header="true" max-height="340" stripe @sort-change="onSortChange">
            <el-table-column prop="name" label="菜品名称" min-width="90" show-overflow-tooltip />
            <el-table-column prop="category" label="分类" width="70">
              <template #default="{ row }"><el-tag :type="tagType(row.category)" size="small" effect="plain">{{ row.category }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="price" label="价格" width="65" align="right">
              <template #default="{ row }"><span class="price">&yen;{{ row.price }}</span></template>
            </el-table-column>
            <el-table-column prop="sales" label="销量" width="65" align="right" sortable="custom" />
            <el-table-column prop="rating" label="评分" width="110" align="center">
              <template #default="{ row }">
                <el-rate :model-value="row.rating" disabled size="small" score-template="{value}" show-score text-color="#f39c12" style="display: inline-flex" />
              </template>
            </el-table-column>
          </el-table>
        </vab-card>
      </div>
    </div>

    <!-- Bottom: Weekly Dining Stats -->
    <div class="bottom-row">
      <vab-card title="本周各餐次统计" class="chart-card">
        <v-chart :option="weeklyDiningOption" autoresize style="height: 280px; width: 100%" />
      </vab-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, inject } from 'vue'
import * as echarts from 'echarts'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'

echarts.use([CanvasRenderer, BarChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])
import { getRestaurantOverview, getDiningTrend, getDiningAreaDistribution, getWeeklyDiningStats, getTodayMenu } from '/@/api/operations'
import { ElMessage } from 'element-plus'

defineOptions({ name: 'OperationsRestaurant' })

const $baseMessage = inject<any>('$baseMessage')

const summaryCards = ref<any[]>([])
const todayMenu = ref<any[]>([])
const diningTrendOption = ref<any>({})
const areaDistributionOption = ref<any>({})
const weeklyDiningOption = ref<any>({})

const peakHoursRange = { start: '11:30', end: '12:30' }

const tagType = (category: string): string => { const map: Record<string, string> = { 中餐: 'danger', 西餐: 'warning', 面点: 'success', 饮品: 'primary', 户外: 'info' }; return map[category] || 'info' }

const onSortChange = (sort: { prop: string; order: string }) => {
  if (sort.prop === 'sales' && sort.order) { const sorted = [...todayMenu.value]; sorted.sort((a, b) => (sort.order === 'ascending' ? a.sales - b.sales : b.sales - a.sales)); todayMenu.value = sorted }
}

const inPeakHours = (hour: string): boolean => hour >= peakHoursRange.start && hour <= peakHoursRange.end

const buildDiningTrendOption = (data: any[]) => {
  const hours = data.map((d: any) => d.hour); const counts = data.map((d: any) => d.count)
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' }, formatter: (params: any[]) => { const bar = params.find((p: any) => p.seriesName === '就餐人数'); const line = params.find((p: any) => p.seriesName === '趋势线'); let html = `<strong>${bar?.axisValue || ''}</strong><br/>`; if (bar) html += `就餐人数: ${bar.value}<br/>`; if (line) html += `趋势: ${line.value}`; return html } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '30px', containLabel: true },
    xAxis: { type: 'category', data: hours, axisLabel: { fontSize: 10, rotate: 30 } },
    yAxis: { type: 'value', minInterval: 1, name: '人数', nameTextStyle: { fontSize: 11 } },
    series: [
      { name: '就餐人数', type: 'bar', data: counts.map((count: number, idx: number) => ({ value: count, itemStyle: { color: inPeakHours(hours[idx]) ? new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#f56c6c' }, { offset: 1, color: '#e6a23c' }]) : new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#409eff' }, { offset: 1, color: '#79bbff' }]), borderRadius: [2, 2, 0, 0] } })), barMaxWidth: 22 },
      { name: '趋势线', type: 'line', data: counts, smooth: true, lineStyle: { color: '#67c23a', width: 2 }, itemStyle: { color: '#67c23a' }, symbol: 'circle', symbolSize: 5, z: 2 },
    ],
  }
}

const buildAreaDistributionOption = (data: any[]) => {
  const areas = data.map((d: any) => d.area); const counts = data.map((d: any) => d.count); const rates = data.map((d: any) => d.rate)
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any[]) => { const idx = params[0]?.dataIndex; const item = data[idx]; if (!item) return ''; return `<strong>${item.area}</strong><br/>就餐人数: ${item.count}<br/>餐位总数: ${item.total}<br/>占用率: ${item.rate}%` } },
    legend: { data: ['就餐人数', '占用率'], top: 0, left: 'center', icon: 'roundRect', itemWidth: 12, itemHeight: 8 },
    grid: { left: '3%', right: '8%', bottom: '3%', top: '36px', containLabel: true },
    xAxis: { type: 'value', minInterval: 1, axisLabel: { fontSize: 10 } },
    yAxis: { type: 'category', data: areas, axisLabel: { fontSize: 12 } },
    series: [
      { name: '就餐人数', type: 'bar', data: counts.map((c: number) => ({ value: c, itemStyle: { color: '#409eff', borderRadius: [0, 3, 3, 0] } })), barMaxWidth: 16, label: { show: true, position: 'right', fontSize: 11, fontWeight: 600, color: '#409eff', formatter: (params: any) => `${params.value}人` } },
      { name: '占用率', type: 'bar', data: rates.map((r: number) => ({ value: r, itemStyle: { color: 'rgba(64, 158, 255, 0.25)', borderRadius: [0, 3, 3, 0] } })), barMaxWidth: 16, barGap: '-100%', z: 0, label: { show: true, position: 'right', fontSize: 11, color: '#909399', formatter: (params: any) => `${params.value}%` } },
    ],
  }
}

const buildWeeklyDiningOption = (data: any[]) => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { data: ['早餐', '午餐', '晚餐'], top: 0, left: 'center', icon: 'roundRect', itemWidth: 12, itemHeight: 8 },
  grid: { left: '3%', right: '4%', bottom: '3%', top: '40px', containLabel: true },
  xAxis: { type: 'category', data: data.map((d: any) => d.day), axisLabel: { fontSize: 11 } },
  yAxis: { type: 'value', minInterval: 1, name: '用餐人数', nameTextStyle: { fontSize: 11 } },
  series: [
    { name: '早餐', type: 'bar', data: data.map((d: any) => d.breakfast), itemStyle: { color: '#909399' }, barMaxWidth: 20, barGap: '20%' },
    { name: '午餐', type: 'bar', data: data.map((d: any) => d.lunch), itemStyle: { color: '#409eff' }, barMaxWidth: 20 },
    { name: '晚餐', type: 'bar', data: data.map((d: any) => d.dinner), itemStyle: { color: '#e6a23c' }, barMaxWidth: 20 },
  ],
})

const loadData = async () => {
  try {
    const [overviewRes, trendRes, areaRes, weeklyRes, menuRes] = await Promise.all([getRestaurantOverview(), getDiningTrend(), getDiningAreaDistribution(), getWeeklyDiningStats(), getTodayMenu()])
    const overview = overviewRes.data ?? overviewRes; const trend = trendRes.data ?? trendRes; const area = areaRes.data ?? areaRes; const weekly = weeklyRes.data ?? weeklyRes; const menu = menuRes.data ?? menuRes
    summaryCards.value = [
      { label: '当前就餐人数', value: `${overview.currentDiners}`, rawValue: overview.currentDiners, progressValue: '', color: '#409EFF', showProgress: false },
      { label: '座位占用率', value: `${overview.seatingOccupancy}%`, rawValue: overview.seatingOccupancy, progressValue: overview.seatingOccupancy, color: '#67C23A', showProgress: true },
      { label: '今日用餐总数', value: `${overview.todayTotalMeals}`, rawValue: overview.todayTotalMeals, progressValue: '', color: '#B37FEB', showProgress: false },
      { label: '平均排队时间', value: `${overview.avgQueueTime}min`, rawValue: overview.avgQueueTime, progressValue: '', color: '#E6A23C', showProgress: false },
      { label: '高峰时段', value: `${overview.peakHours}`, rawValue: '', progressValue: '', color: '#F56C6C', showProgress: false, subLabel: '高峰时段' },
      { label: '总座位数', value: `${overview.totalSeats}`, rawValue: overview.totalSeats, progressValue: '', color: '#36CFC9', showProgress: false },
    ]
    todayMenu.value = [...menu].sort((a, b) => b.sales - a.sales)
    diningTrendOption.value = buildDiningTrendOption(trend)
    areaDistributionOption.value = buildAreaDistributionOption(area)
    weeklyDiningOption.value = buildWeeklyDiningOption(weekly)
  } catch (err) { const msg = $baseMessage?.error ?? ElMessage.error; msg('加载餐厅看板数据失败'); console.error(err) }
}

onMounted(() => { loadData() })
</script>

<style scoped lang="scss">
.restaurant-dashboard { height: 100vh; width: 100%; padding: 16px; box-sizing: border-box; background: #f0f2f5; overflow-y: auto; overflow-x: hidden;
  .summary-row { margin-bottom: 16px; .el-col { padding: 0 6px; } }
  .summary-card { display: flex; align-items: center; justify-content: space-between; padding: 16px 14px; background: #fff; border-radius: 8px; border-left: 4px solid; box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: box-shadow 0.3s;
    &:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
    .card-content { flex: 1; min-width: 0; }
    .card-value { font-size: 24px; font-weight: 700; line-height: 1.2; }
    .card-label { font-size: 13px; color: #909399; margin-top: 4px; }
    .card-sublabel { font-size: 11px; color: #c0c4cc; margin-top: 2px; }
    .card-progress { flex-shrink: 0; margin-left: 8px; } }
  .dashboard-grid { display: grid; grid-template-columns: 35% 35% 30%; gap: 16px; margin-bottom: 16px; }
  .grid-left, .grid-center, .grid-right { display: flex; flex-direction: column; }
  .price { font-weight: 600; color: #f56c6c; } }
</style>
```

```vue
<!-- ============================================================
文件: src/views/operate/operations/meeting/index.vue
智能楼宇智慧运营系统 - 会议看板
============================================================ -->
<template>
  <div class="meeting-dashboard">
    <!-- Summary Cards Row -->
    <el-row :gutter="16" class="summary-row">
      <el-col v-for="(card, index) in summaryCards" :key="card.label" :span="4">
        <div class="summary-card" :style="{ borderLeftColor: card.color }">
          <div class="card-content">
            <div class="card-value" :style="{ color: card.color }">
              <span v-if="card.pulse" class="pulse-dot" />{{ card.value }}
              <span v-if="card.unit" class="card-unit">{{ card.unit }}</span>
            </div>
            <div class="card-label">{{ card.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Grid: Left (40%) + Right (60%) -->
    <div class="dashboard-grid">
      <div class="grid-left">
        <vab-card title="会议室实时状态" class="room-card">
          <div class="room-grid">
            <div v-for="room in roomUsageList" :key="room.room" class="room-item" :class="'status-' + room.status">
              <div class="room-header">
                <span class="room-name">{{ room.room }}</span>
                <span class="room-capacity">{{ room.capacity }}人</span>
              </div>
              <div class="room-status-row">
                <span class="status-indicator" :class="room.status" />
                <span class="room-status-text">{{ statusLabel(room.status) }}</span>
              </div>
              <div v-if="room.meeting" class="room-meeting">{{ room.meeting }}<span v-if="room.until">至{{ room.until }}</span></div>
            </div>
          </div>
        </vab-card>
      </div>
      <div class="grid-right">
        <vab-card title="部门会议使用统计" class="chart-card">
          <v-chart :option="deptStatsOption" autoresize style="height: 280px; width: 100%" />
        </vab-card>
        <vab-card title="当前进行会议" class="table-card">
          <el-table :data="currentMeetings" style="width: 100%" size="small" :show-header="true" max-height="240" stripe>
            <el-table-column prop="room" label="会议室" min-width="90" />
            <el-table-column prop="subject" label="会议主题" min-width="120" show-overflow-tooltip />
            <el-table-column prop="dept" label="部门" width="70" />
            <el-table-column prop="host" label="主持人" width="70" />
            <el-table-column label="时间" min-width="110">
              <template #default="{ row }"><el-tag size="small" effect="plain" type="primary" style="font-size: 11px">{{ row.startTime }}-{{ row.endTime }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="participants" label="人数" width="55" align="center" />
          </el-table>
        </vab-card>
      </div>
    </div>

    <!-- Weekly Meeting Trend -->
    <vab-card title="本周会议趋势" class="trend-card">
      <v-chart :option="weeklyTrendOption" autoresize style="height: 240px; width: 100%" />
    </vab-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, inject } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, BarChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])
import { getMeetingOverview, getRoomUsage, getMeetingDeptStats, getCurrentMeetings, getMeetingTrendWeekly } from '/@/api/operations'
import { ElMessage } from 'element-plus'

defineOptions({ name: 'OperationsMeeting' })

const $baseMessage = inject<any>('$baseMessage')

const summaryCards = ref<any[]>([])
const roomUsageList = ref<any[]>([])
const currentMeetings = ref<any[]>([])
const deptStatsOption = ref<any>({})
const weeklyTrendOption = ref<any>({})

const statusLabel = (status: string): string => { const map: Record<string, string> = { in_use: '使用中', available: '空闲', booked: '已预定', maintenance: '维护中' }; return map[status] ?? status }

const loadData = async () => {
  try {
    const [overviewRes, roomUsageRes, deptStatsRes, meetingsRes, weeklyTrendRes] = await Promise.all([getMeetingOverview(), getRoomUsage(), getMeetingDeptStats(), getCurrentMeetings(), getMeetingTrendWeekly()])
    const overview = overviewRes.data ?? overviewRes; const roomUsage = roomUsageRes.data ?? roomUsageRes; const deptStats = deptStatsRes.data ?? deptStatsRes; const meetings = meetingsRes.data ?? meetingsRes; const weeklyTrend = weeklyTrendRes.data ?? weeklyTrendRes
    summaryCards.value = [
      { label: '今日会议数', value: overview.todayMeetings, color: '#409EFF' },
      { label: '进行中', value: overview.inProgress, color: '#67C23A', pulse: true },
      { label: '会议室使用率', value: overview.roomUsageRate, color: '#B37FEB', unit: '%' },
      { label: '参会总人数', value: overview.totalParticipants, color: '#E6A23C' },
      { label: '待开会议', value: overview.upcomingMeetings, color: '#00BCD4' },
      { label: '平均时长', value: overview.avgMeetingDuration, color: '#909399', unit: '分钟' },
    ]
    roomUsageList.value = roomUsage; currentMeetings.value = meetings.slice(0, 5)
    deptStatsOption.value = buildDeptStatsOption(deptStats); weeklyTrendOption.value = buildWeeklyTrendOption(weeklyTrend)
  } catch (err) { const msg = $baseMessage?.error ?? ElMessage.error; msg('加载会议看板数据失败'); console.error(err) }
}

const buildDeptStatsOption = (data: any[]) => {
  const sorted = [...data].reverse()
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['会议次数', '使用时长(小时)'], top: 0, left: 'center', icon: 'roundRect', itemWidth: 12, itemHeight: 8 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '40px', containLabel: true },
    xAxis: { type: 'value', minInterval: 1 },
    yAxis: { type: 'category', data: sorted.map((d: any) => d.dept), axisLabel: { fontSize: 11 } },
    series: [
      { name: '会议次数', type: 'bar', data: sorted.map((d: any) => d.count), itemStyle: { color: '#409EFF' }, barMaxWidth: 18 },
      { name: '使用时长(小时)', type: 'bar', data: sorted.map((d: any) => d.hours), itemStyle: { color: '#E6A23C' }, barMaxWidth: 18 },
    ],
  }
}

const buildWeeklyTrendOption = (data: any[]) => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
  legend: { data: ['会议数量', '使用率(%)'], top: 0, left: 'center', icon: 'roundRect', itemWidth: 12, itemHeight: 8 },
  grid: { left: '3%', right: '4%', bottom: '3%', top: '40px', containLabel: true },
  xAxis: { type: 'category', data: data.map((d: any) => d.day), axisLabel: { fontSize: 11 } },
  yAxis: [{ type: 'value', name: '会议数量', minInterval: 1, nameTextStyle: { fontSize: 10 } }, { type: 'value', name: '使用率(%)', min: 0, max: 100, axisLabel: { formatter: '{value}%' }, nameTextStyle: { fontSize: 10 } }],
  series: [
    { name: '会议数量', type: 'bar', data: data.map((d: any) => d.count), itemStyle: { color: '#409EFF' }, barMaxWidth: 24 },
    { name: '使用率(%)', type: 'line', yAxisIndex: 1, data: data.map((d: any) => d.usageRate), smooth: true, lineStyle: { color: '#67C23A', width: 2 }, itemStyle: { color: '#67C23A' }, symbol: 'circle', symbolSize: 6 },
  ],
})

onMounted(() => { loadData() })
</script>

<style scoped lang="scss">
.meeting-dashboard { height: 100vh; width: 100%; padding: 16px; box-sizing: border-box; background: #f0f2f5; overflow-y: auto; overflow-x: hidden;
  .summary-row { margin-bottom: 16px; .el-col { padding: 0 6px; } }
  .summary-card { display: flex; align-items: center; padding: 16px 14px; background: #fff; border-radius: 8px; border-left: 4px solid; box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: box-shadow 0.3s;
    &:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
    .card-content { flex: 1; min-width: 0; }
    .card-value { display: flex; align-items: center; gap: 6px; font-size: 24px; font-weight: 700; line-height: 1.2; }
    .card-unit { font-size: 13px; font-weight: 400; color: #909399; margin-left: 2px; }
    .card-label { font-size: 13px; color: #909399; margin-top: 4px; } }
  .pulse-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #67c23a; animation: pulse 2s ease-in-out infinite; flex-shrink: 0; }
  @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.8); } }
  .dashboard-grid { display: grid; grid-template-columns: 40% 60%; gap: 16px; margin-bottom: 16px; }
  .grid-left { display: flex; flex-direction: column; }
  .grid-right { display: flex; flex-direction: column; gap: 16px; }
  .room-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .room-item { padding: 12px 10px 10px 14px; background: #fff; border-radius: 6px; border-left: 4px solid #ebeef5; box-shadow: 0 1px 4px rgba(0,0,0,0.04); transition: box-shadow 0.2s;
    &:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
    &.status-in_use { border-left-color: #409eff; .status-indicator { background: #409eff; } }
    &.status-available { border-left-color: #67c23a; .status-indicator { background: #67c23a; } }
    &.status-booked { border-left-color: #e6a23c; .status-indicator { background: #e6a23c; } }
    &.status-maintenance { border-left-color: #909399; .status-indicator { background: #909399; } }
    .room-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
    .room-name { font-size: 13px; font-weight: 600; color: #303133; }
    .room-capacity { font-size: 11px; color: #909399; background: #f5f7fa; padding: 1px 6px; border-radius: 4px; }
    .room-status-row { display: flex; align-items: center; gap: 5px; margin-bottom: 4px; }
    .status-indicator { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #ebeef5; flex-shrink: 0; }
    .room-status-text { font-size: 12px; color: #606266; }
    .room-meeting { font-size: 12px; color: #409eff; line-height: 1.3; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; } } }
</style>
```
