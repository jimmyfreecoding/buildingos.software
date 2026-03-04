# 源代码提交页（智能楼宇空间预约系统 buildingos.reservation）

## 提交要求
- 连续前30页与后30页，每页≥50行
- 不得包含公司、个人、文件名称
- 数量与申请表一致

## 前30页
```
<template>
  <div class="shared-booking-container no-background-container">
    <vab-card class="auto-height-card">
      <el-tabs v-model="activeTab">
          <el-tab-pane label="在线预定" name="booking">
              <div class="booking-panel">
                  <vab-query-form>
                    <vab-query-form-top-panel :span="24">
                      <el-form :inline="true">
                         <el-form-item label="日期">
                             <el-date-picker v-model="bookingDate" type="date" placeholder="选择日期" />
                         </el-form-item>
                         <el-form-item>
                             <el-button type="primary" @click="fetchWorkstations">查询可用工位</el-button>
                         </el-form-item>
                      </el-form>
                    </vab-query-form-top-panel>
                  </vab-query-form>
                  
                  <el-row :gutter="20">
                      <el-col :span="6" v-for="ws in workstations" :key="ws.id">
                          <el-card shadow="hover" class="ws-card" :class="ws.status">
                              <div class="ws-header">
                                  <span>{{ ws.code }}</span>
                                  <el-tag size="small" :type="ws.status === 'available' ? 'success' : 'info'">
                                      {{ ws.status === 'available' ? '空闲' : '已预定' }}
                                  </el-tag>
                              </div>
                              <div class="ws-info">
                                  <p>{{ ws.location }}</p>
                                  <div class="features">
                                      <el-tag v-for="f in ws.features" :key="f" size="small" effect="plain" style="margin-right: 5px">{{ f }}</el-tag>
                                  </div>
                              </div>
                              <div class="ws-action">
                                  <el-button v-if="ws.status === 'available'" type="primary" size="small" @click="handleBook(ws)">预定</el-button>
                                  <span v-else class="next-time">下次可用: {{ ws.nextAvailable }}</span>
                              </div>
                          </el-card>
                      </el-col>
                  </el-row>
              </div>
          </el-tab-pane>
          <el-tab-pane label="预定管理" name="management">
              <vab-query-form>
                <vab-query-form-top-panel :span="24">
                  <el-form :inline="true">
                    <el-form-item label="预定人">
                      <el-input v-model="queryForm.user" placeholder="姓名" />
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="fetchBookings">查询</el-button>
                    </el-form-item>
                  </el-form>
                </vab-query-form-top-panel>
              </vab-query-form>
              
              <el-table :data="bookingList" border>
                  <el-table-column prop="id" label="订单号" width="150" />
                  <el-table-column prop="workstation" label="工位" width="100" />
                  <el-table-column prop="user" label="预定人" width="100" />
                  <el-table-column prop="department" label="部门" width="120" />
                  <el-table-column prop="startTime" label="开始时间" width="160" />
                  <el-table-column prop="endTime" label="结束时间" width="160" />
                  <el-table-column prop="status" label="状态" width="100">
                      <template #default="{ row }">
                          <el-tag :type="row.status === 'active' ? 'primary' : 'info'">{{ row.status }}</el-tag>
                      </template>
                  </el-table-column>
                  <el-table-column label="操作" width="100" fixed="right">
                      <template #default="{ row }">
                          <el-button v-if="row.status === 'active'" type="danger" text size="small" @click="handleCancel(row)">取消</el-button>
                      </template>
                  </el-table-column>
              </el-table>
          </el-tab-pane>
      </el-tabs>

      <booking-dialog ref="bookingDialogRef" @success="fetchWorkstations" />
    </vab-card>
  </div>
</template>

<script lang="ts" setup>
import { getSharedWorkstations, getBookingList } from '/@/api/workstation'
import BookingDialog from './vabAutoComponents/BookingDialog.vue'

defineOptions({
  name: 'SharedBooking',
})

const activeTab = ref('booking')
const bookingDate = ref(new Date())
const workstations = ref<any[]>([])
const bookingList = ref<any[]>([])
const bookingDialogRef = ref<any>(null)

const queryForm = reactive({
    user: ''
})

const fetchWorkstations = async () => {
    const { data } = await getSharedWorkstations({})
    workstations.value = data.list || []
}

const fetchBookings = async () => {
    const { data } = await getBookingList(queryForm)
    bookingList.value = data.list || []
}

const handleBook = (ws: any) => {
    bookingDialogRef.value.show(ws)
}

const handleCancel = (row: any) => {
    ElMessage.success('取消成功')
    fetchBookings()
}

onMounted(() => {
    fetchWorkstations()
    fetchBookings()
})
</script>

<style lang="scss" scoped>
.shared-booking-container {
    padding: 20px;
    
    .ws-card {
        margin-bottom: 20px;
        background-color: var(--el-bg-color); // Use variable
        border: 1px solid var(--el-border-color-light); // Use variable
        color: var(--el-text-color-primary); // Use variable

        .ws-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .ws-info {
            font-size: 13px;
            color: var(--el-text-color-regular); // Use variable
            margin-bottom: 15px;
            .features {
                margin-top: 5px;
            }
        }
        .ws-action {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            .next-time {
                font-size: 12px;
                color: var(--el-text-color-secondary); // Use variable
            }
        }
        
        &.available {
            border-top: 3px solid var(--el-color-success); // Use variable
        }
        &.booked {
            border-top: 3px solid var(--el-text-color-secondary); // Use variable
            background-color: var(--el-fill-color-light); // Use variable for background
        }
    }
}
</style>
<template>
  <el-dialog v-model="dialogVisible" title="预定工位" width="500px">
    <el-form ref="formRef" :model="form" label-width="80px">
      <el-form-item label="工位">
        <span>{{ form.workstationCode }}</span>
      </el-form-item>
      <el-form-item label="时间段">
          <el-time-select
            v-model="form.startTime"
            start="08:00"
            step="00:30"
            end="20:00"
            placeholder="开始时间"
            style="width: 150px; margin-right: 10px;"
          />
          <el-time-select
            v-model="form.endTime"
            start="08:00"
            step="00:30"
            end="20:00"
            placeholder="结束时间"
            style="width: 150px;"
          />
      </el-form-item>
      <el-form-item label="预定人">
          <el-input v-model="form.user" placeholder="预定人姓名" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="confirm">确定预定</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
defineOptions({
  name: 'BookingDialog',
})

const emit = defineEmits(['success'])
const dialogVisible = ref(false)
const form = reactive({
    workstationId: '',
    workstationCode: '',
    startTime: '',
    endTime: '',
    user: ''
})

const show = (ws: any) => {
    form.workstationId = ws.id
    form.workstationCode = ws.code
    form.startTime = ''
    form.endTime = ''
    form.user = ''
    dialogVisible.value = true
}

const confirm = () => {
    if (!form.startTime || !form.endTime || !form.user) {
        ElMessage.warning('请填写完整信息')
        return
    }
    // Mock submit
    ElMessage.success('预定成功')
    dialogVisible.value = false
    emit('success')
}

defineExpose({
  show
})
</script>
<template>
  <div class="fixed-allocation-container no-background-container">
    <vab-card class="auto-height-card">
      <vab-query-form>
        <vab-query-form-top-panel :span="24">
          <el-form :model="queryForm" :inline="true" @submit.prevent>
            <el-form-item label="工位编号">
              <el-input v-model="queryForm.code" placeholder="请输入编号" />
            </el-form-item>
            <el-form-item label="部门">
              <el-input v-model="queryForm.department" placeholder="请输入部门" />
            </el-form-item>
             <el-form-item label="状态">
               <el-select v-model="queryForm.status" placeholder="状态" clearable>
                   <el-option label="已占用" value="occupied" />
                   <el-option label="空闲" value="vacant" />
               </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
              <el-button type="primary" @click="handleBatchAllocate">批量分配</el-button>
            </el-form-item>
          </el-form>
        </vab-query-form-top-panel>
      </vab-query-form>

      <el-table v-loading="loading" :data="list" border @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="code" label="工位编号" width="120" />
        <el-table-column prop="location" label="位置" />
        <el-table-column prop="department" label="所属部门" width="150" />
        <el-table-column prop="user" label="使用人" width="120" />
        <el-table-column prop="status" label="状态" width="100">
           <template #default="{ row }">
              <el-tag :type="row.status === 'occupied' ? 'warning' : 'success'">
                  {{ row.status === 'occupied' ? '已占用' : '空闲' }}
              </el-tag>
           </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleAllocate(row)">分配</el-button>
            <el-button v-if="row.status === 'occupied'" type="danger" text size="small" @click="handleRelease(row)">收回</el-button>
          </template>
        </el-table-column>
      </el-table>

      <allocation-dialog ref="allocationRef" @fetch-data="fetchData" />
    </vab-card>
  </div>
</template>

<script lang="ts" setup>
import { getFixedWorkstations } from '/@/api/workstation'
import AllocationDialog from './vabAutoComponents/AllocationDialog.vue'

defineOptions({
  name: 'FixedAllocation',
})

const list = ref([])
const loading = ref(true)
const allocationRef = ref<any>(null)
const selectedRows = ref<any[]>([])

const queryForm = reactive({
  code: '',
  department: '',
  status: ''
})

const fetchData = async () => {
  loading.value = true
  const { data } = await getFixedWorkstations(queryForm)
  list.value = data.list || []
  loading.value = false
}

const handleSelectionChange = (val: any[]) => {
    selectedRows.value = val
}

const handleAllocate = (row: any) => {
  allocationRef.value.show(row)
}

const handleBatchAllocate = () => {
    if (selectedRows.value.length === 0) {
        ElMessage.warning('请选择要分配的工位')
        return
    }
    allocationRef.value.showBatch(selectedRows.value)
}

const handleRelease = (row: any) => {
  ElMessageBox.confirm('确认收回该工位?', '提示', {
    type: 'warning'
  }).then(async () => {
    ElMessage.success('收回成功')
    fetchData()
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.fixed-allocation-container {
    padding: 20px;
}
</style>
<template>
  <el-dialog v-model="dialogVisible" :title="title" width="500px">
    <el-form ref="formRef" :model="form" label-width="80px">
      <el-form-item label="部门">
        <el-input v-model="form.department" placeholder="请输入部门" />
      </el-form-item>
      <el-form-item label="使用人">
        <el-input v-model="form.user" placeholder="请输入使用人" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="save">确定</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { allocateWorkstation } from '/@/api/workstation'

defineOptions({
  name: 'AllocationDialog',
})

const emit = defineEmits(['fetch-data'])
const dialogVisible = ref(false)
const title = ref('')
const form = reactive<any>({
  department: '',
  user: '',
  ids: []
})

const show = (row: any) => {
  title.value = '分配工位: ' + row.code
  form.ids = [row.id]
  form.department = row.department
  form.user = row.user
  dialogVisible.value = true
}

const showBatch = (rows: any[]) => {
    title.value = `批量分配 (${rows.length}个)`
    form.ids = rows.map(r => r.id)
    form.department = ''
    form.user = ''
    dialogVisible.value = true
}

const save = async () => {
    await allocateWorkstation(form)
    ElMessage.success('分配成功')
    dialogVisible.value = false
    emit('fetch-data')
}

defineExpose({
  show,
  showBatch
})
</script>
<template>
  <div class="map-management-container no-background-container">
    <vab-card class="auto-height-card">
      <vab-query-form>
        <vab-query-form-top-panel :span="24">
          <el-form :model="queryForm" :inline="true" @submit.prevent>
            <el-form-item label="地图名称">
              <el-input v-model="queryForm.name" placeholder="请输入名称" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
              <el-button type="primary" :icon="Plus" @click="handleAdd">新增地图</el-button>
            </el-form-item>
          </el-form>
        </vab-query-form-top-panel>
      </vab-query-form>

      <el-table v-loading="loading" :data="list" border>
        <el-table-column prop="name" label="地图名称" />
        <el-table-column prop="building" label="所属楼宇" width="120" />
        <el-table-column prop="floor" label="楼层" width="100" />
        <el-table-column prop="workstationCount" label="工位数量" width="100" />
        <el-table-column prop="updateTime" label="更新时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
           <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                  {{ row.status === 'active' ? '启用' : '停用' }}
              </el-tag>
           </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" text size="small" @click="handleDesign(row)">设计地图</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <map-edit ref="editRef" @fetch-data="fetchData" />
    </vab-card>
  </div>
</template>

<script lang="ts" setup>
import { getMapList, deleteMap } from '/@/api/workstation'
import MapEdit from './vabAutoComponents/MapEdit.vue'
import { Plus } from '@element-plus/icons-vue'

defineOptions({
  name: 'MapManagement',
})

const list = ref([])
const loading = ref(true)
const editRef = ref<any>(null)

const queryForm = reactive({
  name: ''
})

const fetchData = async () => {
  loading.value = true
  const { data } = await getMapList(queryForm)
  list.value = data.list || []
  loading.value = false
}

const handleAdd = () => {
  editRef.value.showEdit()
}

const handleEdit = (row: any) => {
  editRef.value.showEdit(row)
}

const handleDesign = (row: any) => {
    ElMessage.info('进入地图设计器: ' + row.name)
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm('确认删除?', '提示', {
    type: 'warning'
  }).then(async () => {
    await deleteMap(row.id)
    ElMessage.success('删除成功')
    fetchData()
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.map-management-container {
    padding: 20px;
}
</style>
<template>
  <el-dialog v-model="dialogVisible" :title="title" width="600px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="地图名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入名称" />
      </el-form-item>
      <el-form-item label="所属楼宇" prop="building">
        <el-input v-model="form.building" placeholder="请输入楼宇" />
      </el-form-item>
      <el-form-item label="楼层" prop="floor">
        <el-input v-model="form.floor" placeholder="请输入楼层" />
      </el-form-item>
      <el-form-item label="状态">
         <el-switch v-model="form.status" active-value="active" inactive-value="inactive" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="save">保存</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { saveMap } from '/@/api/workstation'

defineOptions({
  name: 'MapEdit',
})

const emit = defineEmits(['fetch-data'])
const dialogVisible = ref(false)
const title = ref('')
const formRef = ref<any>(null)
const form = reactive<any>({
  id: '',
  name: '',
  building: '',
  floor: '',
  status: 'active'
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

const showEdit = (row?: any) => {
  dialogVisible.value = true
  if (row) {
    title.value = '编辑地图'
    Object.assign(form, JSON.parse(JSON.stringify(row)))
  } else {
    title.value = '新增地图'
    form.id = ''
    form.name = ''
    form.building = ''
    form.floor = ''
    form.status = 'active'
  }
}

const save = async () => {
    await formRef.value.validate()
    await saveMap(form)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    emit('fetch-data')
}

defineExpose({
  showEdit,
})
</script>
<template>
  <div class="status-screen-container no-background-container">
    <el-row :gutter="20">
       <el-col :span="16">
           <vab-card title="办公空间实时状态 (3D/2.5D Mock)" class="map-card">
               <div class="mock-map">
                   <!-- Placeholder for 3D/2.5D map engine -->
                   <div class="map-placeholder">
                       <el-icon :size="50"><MapLocation /></el-icon>
                       <p>2.5D地图引擎加载区域</p>
                       <p>展示工位占用及空闲状态信息</p>
                   </div>
                   
                   <div class="legend">
                       <div class="item"><span class="dot free"></span>空闲</div>
                       <div class="item"><span class="dot busy"></span>占用</div>
                       <div class="item"><span class="dot mine"></span>我的预定</div>
                   </div>
               </div>
           </vab-card>
       </el-col>
       <el-col :span="8">
           <vab-card title="快速预定">
               <div class="quick-book">
                   <p>当前可用工位: <span class="highlight">12</span> 个</p>
                   <el-button type="primary" size="large" style="width: 100%; margin-top: 20px;">一键预定最近工位</el-button>
               </div>
           </vab-card>
           <vab-card title="区域概况" style="margin-top: 20px;">
               <div class="area-stats">
                   <div class="stat-row">
                       <span>总工位</span>
                       <span>120</span>
                   </div>
                   <div class="stat-row">
                       <span>当前占用</span>
                       <span>85</span>
                   </div>
                   <el-progress :percentage="70" :format="format" />
               </div>
           </vab-card>
       </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { MapLocation } from '@element-plus/icons-vue'

defineOptions({
  name: 'StatusScreen',
})

const format = (percentage: number) => (percentage === 100 ? '满' : `${percentage}%`)
</script>

<style lang="scss" scoped>
.status-screen-container {
    padding: 20px;
    
    .map-card {
        height: 600px;
        .mock-map {
            height: 100%;
            background-color: #f0f2f5;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
            
            .map-placeholder {
                text-align: center;
                color: #909399;
                p { margin: 10px 0; }
            }
            
            .legend {
                position: absolute;
                bottom: 20px;
                right: 20px;
                background: rgba(255,255,255,0.9);
                padding: 10px;
                border-radius: 4px;
                .item {
                    display: flex;
                    align-items: center;
                    margin: 5px 0;
                    font-size: 12px;
                    .dot {
                        width: 10px;
                        height: 10px;
                        border-radius: 50%;
                        margin-right: 5px;
                        &.free { background: #67C23A; }
                        &.busy { background: #F56C6C; }
                        &.mine { background: #409EFF; }
                    }
                }
            }
        }
    }
    
    .quick-book {
        text-align: center;
        padding: 20px;
        .highlight {
            font-size: 24px;
            color: #67C23A;
            font-weight: bold;
        }
    }
    
    .area-stats {
        padding: 10px;
        .stat-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 14px;
        }
    }
}
</style>
<template>
  <div class="statistics-container no-background-container">
    <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
            <vab-card>
                <div class="stat-item">
                    <div class="title">总工位</div>
                    <div class="value">{{ data.realtime?.total || 0 }}</div>
                </div>
            </vab-card>
        </el-col>
        <el-col :span="6">
            <vab-card>
                <div class="stat-item">
                    <div class="title">当前占用</div>
                    <div class="value">{{ data.realtime?.occupied || 0 }}</div>
                </div>
            </vab-card>
        </el-col>
        <el-col :span="6">
            <vab-card>
                 <div class="stat-item">
                    <div class="title">今日预定</div>
                    <div class="value">{{ data.bookingTrend ? data.bookingTrend[data.bookingTrend.length-1].count : 0 }}</div>
                </div>
            </vab-card>
        </el-col>
        <el-col :span="6">
            <vab-card>
                 <div class="stat-item">
                    <div class="title">今日感应释放</div>
                    <div class="value">{{ data.realtime?.releaseCount || 0 }}</div>
                </div>
            </vab-card>
        </el-col>
    </el-row>

    <el-row :gutter="20">
        <el-col :span="12">
            <vab-card title="工位预定趋势">
                <div class="chart-container" ref="trendChartRef"></div>
            </vab-card>
        </el-col>
        <el-col :span="12">
             <vab-card title="部门使用分布">
                <div class="chart-container" ref="deptChartRef"></div>
            </vab-card>
        </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import * as echarts from 'echarts'
import { getWorkstationStats } from '/@/api/workstation'

defineOptions({
  name: 'WorkstationStatistics',
})

const trendChartRef = ref<HTMLElement | null>(null)
const deptChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let deptChart: echarts.ECharts | null = null

const data = reactive<any>({})

const initCharts = () => {
    if (trendChartRef.value) {
        trendChart = echarts.init(trendChartRef.value)
        const dates = (data.bookingTrend || []).map((i: any) => i.date)
        const counts = (data.bookingTrend || []).map((i: any) => i.count)
        
        trendChart.setOption({
            tooltip: { trigger: 'axis' },
            xAxis: { type: 'category', data: dates },
            yAxis: { type: 'value' },
            series: [{ data: counts, type: 'line', smooth: true, areaStyle: {} }]
        })
    }
    
    if (deptChartRef.value) {
        deptChart = echarts.init(deptChartRef.value)
        
         deptChart.setOption({
            tooltip: { trigger: 'item' },
            legend: { top: '5%', left: 'center' },
            series: [
                {
                    name: '部门分布',
                    type: 'pie',
                    radius: ['40%', '70%'],
                    itemStyle: {
                        borderRadius: 10,
                        borderColor: '#fff',
                        borderWidth: 2
                    },
                    data: data.departmentUsage || []
                }
            ]
        })
    }
}

const fetchData = async () => {
    const res = await getWorkstationStats()
    Object.assign(data, res.data)
    nextTick(() => {
        initCharts()
    })
}

onMounted(() => {
    fetchData()
})

onBeforeUnmount(() => {
    trendChart?.dispose()
    deptChart?.dispose()
})
</script>

<style lang="scss" scoped>
.statistics-container {
    padding: 20px;
    
    .stat-item {
        text-align: center;
        padding: 20px 0;
        .title {
            font-size: 14px;
            color: #909399;
            margin-bottom: 10px;
        }
        .value {
            font-size: 24px;
            font-weight: bold;
            color: #303133;
        }
    }
    
    .chart-container {
        width: 100%;
        height: 300px;
    }
}
</style>
<template>
  <div class="workstation-container no-background-container auto-height-container">
    <el-row :gutter="20">
      <el-col :lg="5" :md="24" :sm="24" :xl="4" :xs="24">
        <vab-card class="auto-height-card1">
          <el-tree
            ref="treeRef"
            v-loading="treeLoading"
            :data="spacedata"
            default-expand-all
            :highlight-current="true"
            node-key="id"
            :props="defaultProps"
            @node-click="handleNodeClick"
          />
        </vab-card>
      </el-col>
      <el-col :lg="19" :md="24" :sm="24" :xl="20" :xs="24">
        <vab-card class="auto-height-card">
          <vab-query-form>
            <vab-query-form-top-panel>
              <el-form inline label-width="49px" :model="queryForm" @submit.prevent>
                <el-form-item label="名称">
                  <el-input v-model="queryForm.title" clearable placeholder="请输入区域名称" />
                </el-form-item>
                <el-form-item>
                  <el-button :icon="Search" :loading="listLoading" native-type="submit" type="primary" @click="queryData">查询</el-button>
                </el-form-item>
              </el-form>
            </vab-query-form-top-panel>
            <vab-query-form-left-panel>
              <el-breadcrumb :separator-icon="ArrowRight">
                <el-breadcrumb-item v-for="(item, index) in crumblist" :key="index">
                  {{ item }}
                </el-breadcrumb-item>
              </el-breadcrumb>
            </vab-query-form-left-panel>
            <vab-query-form-right-panel>
              <div class="custom-table-right-tools">
                <el-button :icon="Plus" type="primary" @click="handleAdd">新增</el-button>
              </div>
            </vab-query-form-right-panel>
          </vab-query-form>
          <el-table
            ref="tableRef"
            v-loading="listLoading"
            :border="border"
            :data="list"
            :size="lineHeight"
            :stripe="stripe"
            @selection-change="setSelectRows"
          >
            <el-table-column type="selection" width="38" />
            <el-table-column align="center" label="ID" :min-width="80" prop="id" show-overflow-tooltip :sortable="true" />
            <el-table-column align="center" label="Code" :min-width="80" prop="code" show-overflow-tooltip :sortable="true" />
            <el-table-column align="center" label="名称" :min-width="80" prop="name" show-overflow-tooltip :sortable="true" />
<!--            <el-table-column align="center" label="状态" :min-width="80" prop="deleteFlag" show-overflow-tooltip :sortable="true">-->
<!--              <template #default="{ row }">-->
<!--                <span>-->
<!--                  <el-switch v-model="row.deleteFlag" active-text="启用" disabled inactive-text="未启用" inline-prompt />-->
<!--                </span>-->
<!--              </template>-->
<!--            </el-table-column>-->
            <el-table-column align="center" :fixed="fixed" label="操作" width="150">
              <template #header>
                <el-checkbox v-model="fixed" label="操作" true-value="right" />
              </template>
              <template #default="{ row }">
                <el-button text type="primary" @click="handleEdit(row)">详细</el-button>
                <el-button text type="primary" @click="handleDelete(row)">删除</el-button>

              </template>
            </el-table-column>
            <template #empty>
              <el-empty class="vab-data-empty" description="暂无数据" />
            </template>
          </el-table>
          <vab-pagination
            :current-page="queryForm.pageNo"
            :page-size="queryForm.pageSize"
            :total="total"
            @current-change="handleCurrentChange"
            @size-change="handleSizeChange"
          />
        </vab-card>
      </el-col>
    </el-row>
    <workstation-edit ref="editRef" :data="queryForm" @fetch-data="fetchData" />
  </div>
</template>

<script lang="ts" setup>
import { Plus, Search } from '@element-plus/icons-vue'
import { getWorkstationList,doWorkstationDelete } from '/@/api/space.ts'
import { ArrowRight } from '@element-plus/icons-vue'
import { getTreeByFloor } from '/@/api/spaceManagement'
import { ElTree } from 'element-plus'
import { ref } from 'vue'
const $baseConfirm = inject<any>('$baseConfirm')
const $baseMessage = inject<any>('$baseMessage')
defineOptions({
  name: 'WorkstationTable',
})
const crumblist = ref<any>([])
const tableRef = ref<any>(null)
const editRef = ref<any>(null)
const border = ref<boolean>(true)
const stripe = ref<boolean>(false)
const lineHeight = ref<any>('default')
const list = ref<any>([])
const listLoading = ref<boolean>(true)
const treeLoading = ref<boolean>(true)
const total = ref<any>(0)
const selectRows = ref<any>([])
const queryForm = reactive<any>({
  spaceCode: '',
  floorAreaCode: '',
  floorCode: '',
  areaCode: '',
  areaType: '',
  pageNo: 1,
  pageSize: 50,
  title: '',
  type: 'all',
})
//tree node start
const treeRef = ref<InstanceType<typeof ElTree>>()
const spacedata = ref<any>([])
const handleNodeClick = (treenode: any) => {
  queryForm.spaceCode = ''
  queryForm.floorAreaCode = ''
  queryForm.floorCode = ''
  queryForm.areaCode = ''
  queryForm.areaType = ''
  if (treenode.spaceCode) {
    queryForm.spaceCode = treenode.spaceCode
  }
  if (treenode.floorAreaCode) {
    queryForm.floorAreaCode = treenode.floorAreaCode
  }
  if (treenode.floorCode) {
    queryForm.floorCode = treenode.floorCode
  }
  if (treenode.areaCode) {
    queryForm.areaCode = treenode.areaCode
  }
  if (treenode.areaType) {
    queryForm.areaType = treenode.areaType
  }

  if (treenode.floorCode) {
    //只有选择到了区域才进行查询
    crumblist.value = treenode.crumblist
    fetchData()
  }
}
const defaultProps = {
  children: 'children',
  label: 'label',
}
//tree node end
const fixed = ref<string>('right')
const fetchData = async () => {
  listLoading.value = true
  const { data } = await getWorkstationList(queryForm)
  console.info(data.list)
  list.value = data.list
  total.value = data.total
  listLoading.value = false
}

const fetchSpaceData = async () => {
  treeLoading.value = true
  const { data } = await getTreeByFloor()
  spacedata.value = data.floorTree
  treeLoading.value = false
  return spacedata.value
}

const handleSizeChange = (value: number) => {
  queryForm.pageNo = 1
  queryForm.pageSize = value
  fetchData()
}

const handleCurrentChange = (value: number) => {
  queryForm.pageNo = value
  fetchData()
}

const queryData = () => {
  queryForm.pageNo = 1
  fetchData()
}

const setSelectRows = (value: any) => {
  selectRows.value = value
}
const handleEdit = (row: any) => {
  editRef.value.showEdit(row)
}

onActivated(() => {
  tableRef.value.doLayout()
})
const getFirstArea = (arr: any) => {
  for (let i = 0; i < arr.length; i++) {
    if (arr[i].type == 'floor') {
      return arr[i].id
    }
    if (arr[i].children) {
      return getFirstArea(arr[i].children)
    }
  }
  return ''
}
const handleAdd = () => {
  editRef.value.showEdit()
}
const handleDelete = (row: any) => {
  if (row.id) {
    $baseConfirm('您确定要删除当前项吗', null, async () => {
      const { msg }: any = await doWorkstationDelete({ ids: row.id })
      $baseMessage(msg, 'success', 'hey')
      await fetchData()
    })
  }
}
onBeforeMount(() => {
  const returnTreeData = fetchSpaceData()
  returnTreeData.then(() => {
    const firstAreaId = getFirstArea(spacedata.value)
    treeRef.value.setCurrentKey(firstAreaId)
    // console.info(treeRef.value.getNode('33333').data)
    handleNodeClick(treeRef.value.getNode(firstAreaId).data)
  })
})
</script>

<style lang="scss" scoped>
.workstation-container {
  width: 100%;
  :deep() {
    .el-card {
      margin-bottom: 0;
    }
  }
}
</style>
<template>
  <vab-dialog v-model="dialogFormVisible" append-to-body :title="title" width="500px" @close="close">
    <el-form ref="formRef" label-width="80px" :model="form" :rules="rules">
      <el-form-item label="名称" prop="name">
        <el-input v-model.trim="form.name" clearable />
      </el-form-item>
      <el-form-item label="工位编码" prop="code">
        <el-input v-model.trim="form.code" clearable />
      </el-form-item>
<!--      <el-form-item label="启用状态" prop="datetime">-->
<!--        <el-switch v-model="form.deleteFlag" active-text="启用"  inactive-text="未启用" inline-prompt />-->
<!--      </el-form-item>-->
    </el-form>
    <template #footer>
      <el-button type="primary" @click="save">保存</el-button>
    </template>
  </vab-dialog>
</template>

<script lang="ts" setup>
import { doWorkstationEdit } from '/@/api/space.ts'

defineOptions({
  name: 'WorkstationTableEdit',
})

const emit = defineEmits(['fetch-data'])
const $baseMessage = inject<any>('$baseMessage')
const formRef = ref<any>(null)
const title = ref<string>('')
const dialogFormVisible = ref<boolean>(false)
const form = reactive<any>({
  areaCode: '',
  code: '',
  deleteFlag: false,
  floorAreaCode: '',
  floorCode: '',
  id: '',
  name: '',
  sortOrder: 1,
  spaceCode: '',
})
const rules = reactive<any>({
  name: [{ required: true, trigger: 'blur', message: '请输入名称' }],
  code: [{ required: true, trigger: 'blur', message: '请输入编码' }],
})

const showEdit = (row: any) => {
  dialogFormVisible.value = true
  nextTick(() => {
    if (!row) {
      title.value = '添加'
      form.spaceCode = props.data.spaceCode
      form.floorCode = props.data.floorCode
      form.floorAreaCode = props.data.floorAreaCode
    } else {
      console.info(row)
      title.value = '编辑'
      Object.assign(form, row)
    }
  })
}
const props = defineProps({
  data: {
    type: Object,
    default: () => {
      return {
        spaceCode: '',
        floorAreaCode: '',
        floorCode: '',
        areaCode: '',
        areaType: '',
        pageNo: 1,
        pageSize: 50,
        title: '',
        type: 'all',
      }
    },
  },
})
defineExpose({
  showEdit,
})

const close = () => {
  formRef.value.clearValidate()
  formRef.value.resetFields()
  emit('fetch-data')
}

const save = () => {
  formRef.value.validate(async (valid: any) => {
    if (valid) {
      const { msg }: any = await doWorkstationEdit(form)
      await $baseMessage(msg, 'success', 'hey')
      await close()
      dialogFormVisible.value = false
    }
  })
}
</script>

```

## 后30页
```
import { IsNotEmpty, IsString, IsArray, IsOptional } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class AllocateWorkstationDto {
  @ApiProperty({ description: '工位ID列表', example: ['ws_001', 'ws_002'] })
  @IsArray()
  @IsNotEmpty()
  ids!: string[];

  @ApiProperty({ description: '所属部门', example: '研发部' })
  @IsString()
  @IsNotEmpty()
  department!: string;

  @ApiProperty({ description: '使用人', required: false, example: '张三' })
  @IsString()
  @IsOptional()
  user?: string;
}
import { IsNotEmpty, IsString, IsDateString } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateBookingDto {
  @ApiProperty({ description: '工位ID', example: 'ws_001' })
  @IsNotEmpty()
  workstationId!: string | number;

  @ApiProperty({ description: '预定开始时间', example: '2023-10-27T09:00:00Z' })
  @IsDateString()
  @IsNotEmpty()
  startTime!: string;

  @ApiProperty({ description: '预定结束时间', example: '2023-10-27T18:00:00Z' })
  @IsDateString()
  @IsNotEmpty()
  endTime!: string;

  @ApiProperty({ description: '预定人', example: '李四' })
  @IsString()
  @IsNotEmpty()
  user!: string;
}
import { IsOptional, IsString } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class QueryBookingDto {
  @ApiProperty({ description: '预定人', required: false })
  @IsOptional()
  @IsString()
  user?: string;

  @ApiProperty({ description: '日期 (YYYY-MM-DD)', required: false })
  @IsOptional()
  @IsString()
  date?: string;

  @ApiProperty({ description: '页码', required: false, default: 1 })
  @IsOptional()
  page?: number;

  @ApiProperty({ description: '每页数量', required: false, default: 10 })
  @IsOptional()
  pageSize?: number;
}
import { IsOptional, IsString } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class QueryWorkstationDto {
  @ApiProperty({ description: '工位编号', required: false })
  @IsOptional()
  @IsString()
  code?: string;

  @ApiProperty({ description: '所属部门', required: false })
  @IsOptional()
  @IsString()
  department?: string;

  @ApiProperty({ description: '状态: vacant(空闲), occupied(占用), maintenance(维护中)', required: false })
  @IsOptional()
  @IsString()
  status?: string;

  @ApiProperty({ description: '类型: fixed(固定), shared(共享)', required: false })
  @IsOptional()
  @IsString()
  type?: string;

  @ApiProperty({ description: '页码', required: false, default: 1 })
  @IsOptional()
  page?: number;

  @ApiProperty({ description: '每页数量', required: false, default: 10 })
  @IsOptional()
  pageSize?: number;
}
import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, ManyToOne, JoinColumn } from 'typeorm';
import { WorkstationEntity } from './workstation.entity';

@Entity('workstation_booking')
export class WorkstationBookingEntity {
  @PrimaryGeneratedColumn()
  id!: number;

  @Column({ name: 'workstation_id' })
  workstationId!: number;

  @ManyToOne(() => WorkstationEntity)
  @JoinColumn({ name: 'workstation_id' })
  workstation!: WorkstationEntity;

  @Column({ name: 'user_id', length: 100 })
  userId!: string;

  @Column({ name: 'user_dept', length: 100, nullable: true })
  userDept?: string;

  @Column({ name: 'start_time', type: 'datetime' })
  startTime!: Date;

  @Column({ name: 'end_time', type: 'datetime' })
  endTime!: Date;

  @Column({ length: 20, default: 'active' })
  status!: string; // active, completed, cancelled

  @Column({ name: 'check_in_time', type: 'datetime', nullable: true })
  checkInTime?: Date;

  @Column({ name: 'release_type', length: 20, nullable: true })
  releaseType?: string; // manual, auto

  @CreateDateColumn({ name: 'created_at' })
  createdAt!: Date;
}
import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity('workstation')
export class WorkstationEntity {
  @PrimaryGeneratedColumn()
  id!: number;

  @Column({
    type: 'varchar',
    length: 50,
    unique: true,
    comment: '工位编号',
  })
  code!: string;

  @Column({
    type: 'varchar',
    length: 255,
    comment: '位置描述',
    nullable: true,
  })
  locationDesc?: string;

  @Column({
    type: 'varchar',
    length: 20,
    comment: '类型: fixed(固定), shared(共享)',
  })
  type!: string;

  @Column({
    type: 'varchar',
    length: 20,
    comment: '状态: vacant(空闲), occupied(占用), maintenance(维护中)',
    default: 'vacant',
  })
  status!: string;

  @Column({
    type: 'json',
    nullable: true,
    comment: '标签/设施',
  })
  features?: string[];

  @Column({
    name: 'department_id',
    type: 'varchar',
    length: 100,
    nullable: true,
    comment: '所属部门',
  })
  departmentId?: string | null;

  @Column({
    name: 'user_id',
    type: 'varchar',
    length: 100,
    nullable: true,
    comment: '当前使用人',
  })
  userId?: string | null;

  @Column({
    name: 'space_code',
    type: 'varchar',
    length: 50,
    nullable: true,
    comment: '所属空间',
  })
  spaceCode?: string;

  @Column({
    name: 'area_code',
    type: 'varchar',
    length: 50,
    nullable: true,
    comment: '所属空间区域',
  })
  areaCode?: string;

  @Column({
    name: 'floor_code',
    type: 'varchar',
    length: 50,
    nullable: true,
    comment: '所属楼层',
  })
  floorCode?: string;

  @Column({
    name: 'floor_area_code',
    type: 'varchar',
    length: 50,
    nullable: true,
    comment: '所属楼层区域',
  })
  floorAreaCode?: string;

  @Column({
    name: 'pos_x',
    type: 'varchar',
    length: 50,
    nullable: true,
    comment: 'posX',
  })
  posX?: string;

  @Column({
    name: 'pos_y',
    type: 'varchar',
    length: 50,
    nullable: true,
    comment: 'posY',
  })
  posY?: string;

  @Column({
    name: 'pos_z',
    type: 'varchar',
    length: 50,
    nullable: true,
    comment: 'posZ',
  })
  posZ?: string;
}
import { Injectable, Optional, Inject } from '@nestjs/common'
import { ModuleRef } from '@nestjs/core'
import { ClientProxy } from '@nestjs/microservices'
import { firstValueFrom } from 'rxjs'

@Injectable()
export class HostBridge {
  private readonly isLocal: boolean
  constructor(
    private readonly moduleRef: ModuleRef,
    @Optional() @Inject('HOST_CLIENT') private readonly client?: ClientProxy
  ) {
    this.isLocal = String(process.env.DEPLOY_MODE || '').toUpperCase() === 'NPM_INSTALL'
  }
  async invoke<T>(service: string, method: string, ...args: any[]): Promise<T> {
    if (this.isLocal) {
      const instance: any = this.moduleRef.get(service, { strict: false })
      if (!instance || typeof instance[method] !== "function") throw new Error(`Not found: ${service}.${method}`)
      return await instance[method](...args)
    }
    if (!this.client) throw new Error("HOST_CLIENT not available")
    return await firstValueFrom(this.client.send('host-gateway.invoke', { service, method, args }))
  }
}import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { WorkstationController } from './workstation.controller';
import { WorkstationMqttController } from './workstation.mqtt.controller';
import { WorkstationEntity } from './entities/workstation.entity';
import { WorkstationBookingEntity } from './entities/workstation-booking.entity';
import { WorkstationService } from './workstation.service';
import { HostBridge } from './integration/host-bridge.service';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    TypeOrmModule.forRootAsync({
      useFactory: () => {
        const dbType = (process.env.DB_TYPE || 'postgres').toLowerCase();
        if (dbType === "mysql") {
          return {
            type: 'mysql' as const,
            host: process.env.DB_HOST || 'localhost',
            port: parseInt(process.env.DB_PORT || '3306', 10),
            username: process.env.DB_USER || 'root',
            password: process.env.DB_PASSWORD || '',
            database: process.env.DB_NAME || 'buildingos',
            autoLoadEntities: true,
            synchronize: false,
          };
        }
        if (dbType === "postgres") {
          return {
            type: 'postgres' as const,
            host: process.env.DB_HOST || 'localhost',
            port: parseInt(process.env.DB_PORT || '5432', 10),
            username: process.env.DB_USER || 'postgres',
            password: process.env.DB_PASSWORD || 'buildingos',
            database: process.env.DB_NAME || 'buildingos',
            autoLoadEntities: true,
            synchronize: false,
          };
        }
        return {
          type: 'sqlite' as const,
          database: 'apps/workstation/data/workstation.sqlite',
          autoLoadEntities: true,
          synchronize: true,
        };
      },
    }),
    TypeOrmModule.forFeature([WorkstationEntity, WorkstationBookingEntity]),
    ClientsModule.registerAsync([
      {
        name: 'HOST_CLIENT',
        imports: [ConfigModule],
        inject: [ConfigService],
        useFactory: (config: ConfigService) => ({
          transport: Transport.MQTT,
          options: {
            url: config.get("MQTT_BROKER_URL") || "mqtt://localhost:1883",
            username: config.get("MQTT_USERNAME"),
            password: config.get("MQTT_PASSWORD"),
            subscribeOptions: { qos: 1 },
            clientId: 'buildingos_microservice_workstation_' + Math.random().toString(16).slice(2, 8),
          },
        }),
      },
    ]),
  ],
  controllers: [WorkstationController, WorkstationMqttController],
  providers: [WorkstationService, HostBridge],
})
export class AppModule {}
import 'reflect-metadata'
import { NestFactory } from '@nestjs/core'
import { AppModule } from './app.module'
import * as swagger from '@nestjs/swagger'
import { Transport, MicroserviceOptions } from '@nestjs/microservices'
import { Logger } from '@nestjs/common'

async function bootstrap() {
  const logger = new Logger('WorkstationBootstrap')
  const app = await NestFactory.create(AppModule)
  try {
    const url = process.env.MQTT_BROKER_URL
    if (url) {
      await app.connectMicroservice<MicroserviceOptions>({
        transport: Transport.MQTT,
        options: { url, subscribeOptions: { qos: 1 } },
      })
      await app.startAllMicroservices()
      logger.log(`nest microservice started, mqtt=${url}`)
    }
  } catch {}
  const config = new swagger.DocumentBuilder().setTitle("Workstation API").setVersion("1.0").build()
  const doc = swagger.SwaggerModule.createDocument(app, config)
  swagger.SwaggerModule.setup('api', app, doc)
  const port = parseInt(process.env.PORT || '3004', 10)
  await app.listen(port)
}
bootstrap()
import { NestFactory } from '@nestjs/core'
import { AppModule } from './app.module'
import { Transport, MicroserviceOptions } from '@nestjs/microservices'

async function startMicro() {
  const app = await NestFactory.create(AppModule)
  const url = process.env.MQTT_BROKER_URL || "mqtt://localhost:1883"
  await app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.MQTT,
    options: { url, subscribeOptions: { qos: 1 } },
  })
  await app.startAllMicroservices()
}
startMicro()
import { Controller, Get, Post, Body, Query, Param } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBody, ApiQuery } from '@nestjs/swagger';
import { WorkstationService } from './workstation.service';
import { QueryWorkstationDto } from './dto/query-workstation.dto';
import { AllocateWorkstationDto } from './dto/allocate-workstation.dto';
import { CreateBookingDto } from './dto/create-booking.dto';
import { QueryBookingDto } from './dto/query-booking.dto';

@ApiTags('工位管理')
@Controller('workstation')
export class WorkstationController {
  constructor(private readonly service: WorkstationService) {}

  @Get("health")
  @ApiOperation({ summary: '健康检查' })
  health() {
    return { status: "ok" };
  }

  @Get("menu.json")
  @ApiOperation({ summary: '获取菜单' })
  async menu() {
    try {
      const fs = await import('fs');
      const path = await import('path');
      const fp = path.join(process.cwd(), 'menu.json');
      if (fs.existsSync(fp)) {
        const txt = fs.readFileSync(fp, 'utf8');
        const arr = JSON.parse(txt);
        if (Array.isArray(arr)) return arr;
      }
    } catch {}
    return [];
  }

  // --- Fixed ---
  @Get('fixed')
  @ApiOperation({ summary: '查询固定工位列表' })
  async findAll(@Query() query: QueryWorkstationDto) {
    const result = await this.service.findAll(query);
    return { code: 200, data: result };
  }

  @Post('fixed/allocate')
  @ApiOperation({ summary: '批量分配固定工位' })
  async allocate(@Body() dto: AllocateWorkstationDto) {
    await this.service.allocate(dto);
    return { code: 200, message: 'success' };
  }

  @Post('fixed/release')
  @ApiOperation({ summary: '释放固定工位' })
  @ApiBody({ schema: { type: 'object', properties: { id: { type: 'string', description: '工位ID或编号' } } } })
  async release(@Body() body: { id: string | number }) {
    await this.service.release(body.id);
    return { code: 200, message: 'success' };
  }

  // --- Shared ---
  @Get('shared/available')
  @ApiOperation({ summary: '查询可用共享工位' })
  @ApiQuery({ name: 'date', required: true, description: '日期 (YYYY-MM-DD)' })
  @ApiQuery({ name: 'startTime', required: false, description: '开始时间' })
  @ApiQuery({ name: 'endTime', required: false, description: '结束时间' })
  async findAvailable(@Query('date') date: string, @Query('startTime') startTime?: string, @Query('endTime') endTime?: string) {
    const result = await this.service.findAvailable(date, startTime, endTime);
    return { code: 200, data: result };
  }

  @Post('booking')
  @ApiOperation({ summary: '预定共享工位' })
  async createBooking(@Body() dto: CreateBookingDto) {
    const result = await this.service.createBooking(dto);
    return { code: 200, data: result };
  }

  @Get('bookings')
  @ApiOperation({ summary: '查询预定记录' })
  async findBookings(@Query() query: QueryBookingDto) {
    const result = await this.service.findBookings(query);
    return { code: 200, data: result };
  }

  @Post('booking/cancel')
  @ApiOperation({ summary: '取消预定' })
  @ApiBody({ schema: { type: 'object', properties: { id: { type: 'string', description: '预定记录ID' } } } })
  async cancelBooking(@Body() body: { id: string | number }) {
    await this.service.cancelBooking(body.id);
    return { code: 200, message: 'success' };
  }

  // --- Stats ---
  @Get('stats')
  @ApiOperation({ summary: '获取工位统计数据' })
  async getStatistics() {
    const result = await this.service.getStatistics();
    return { code: 200, data: result };
  }
}
import { Controller } from '@nestjs/common'
import { MessagePattern, Payload } from '@nestjs/microservices'
@Controller('workstation-mqtt')
export class WorkstationMqttController {
  @MessagePattern('workstation/#')
  handle(@Payload() data: any) {
    return { code: 200, data }
  }
}import { Injectable, Logger, OnModuleInit, BadRequestException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, DataSource, Between, LessThan, MoreThan, In, Not } from 'typeorm';
import { WorkstationEntity } from './entities/workstation.entity';
import { WorkstationBookingEntity } from './entities/workstation-booking.entity';
import { QueryWorkstationDto } from './dto/query-workstation.dto';
import { AllocateWorkstationDto } from './dto/allocate-workstation.dto';
import { CreateBookingDto } from './dto/create-booking.dto';
import { QueryBookingDto } from './dto/query-booking.dto';
import { HostBridge } from './integration/host-bridge.service';

@Injectable()
export class WorkstationService implements OnModuleInit {
  private readonly logger = new Logger('WorkstationService');

  constructor(
    @InjectRepository(WorkstationEntity)
    private readonly workstationRepo: Repository<WorkstationEntity>,
    @InjectRepository(WorkstationBookingEntity)
    private readonly bookingRepo: Repository<WorkstationBookingEntity>,
    private readonly ds: DataSource,
    private readonly host: HostBridge,
  ) {}

  async onModuleInit() {
    try {
      await this.workstationRepo.count();
    } catch (e) {
      this.logger.warn('Database schema might be missing, attempting sync...');
      await this.ds.synchronize();
    }
  }

  // --- Fixed Workstation Management ---

  async findAll(query: QueryWorkstationDto) {
    const page = query.page || 1;
    const pageSize = query.pageSize || 10;
    const skip = (page - 1) * pageSize;

    const qb = this.workstationRepo.createQueryBuilder('ws');

    if (query.code) {
      qb.andWhere('ws.code LIKE :code', { code: `%${query.code}%` });
    }
    if (query.department) {
      qb.andWhere('ws.departmentId LIKE :dept', { dept: `%${query.department}%` });
    }
    if (query.status) {
      qb.andWhere('ws.status = :status', { status: query.status });
    }
    if (query.type) {
      qb.andWhere('ws.type = :type', { type: query.type });
    }

    qb.skip(skip).take(pageSize);

    const [list, total] = await qb.getManyAndCount();
    return { list, total, page, pageSize };
  }

  async allocate(dto: AllocateWorkstationDto) {
    // Check if IDs exist (support code or numeric string)
    const workstations = await this.workstationRepo.findBy({
        code: In(dto.ids)
    });

    if (workstations.length === 0) {
        // Try IDs as numbers
        const numericIds = dto.ids.map(id => parseInt(id)).filter(n => !isNaN(n));
        if (numericIds.length > 0) {
            const byId = await this.workstationRepo.findBy({ id: In(numericIds) });
            workstations.push(...byId);
        }
    }
    
    // Remove duplicates
    const uniqueWs = Array.from(new Set(workstations.map(w => w.id)))
        .map(id => workstations.find(w => w.id === id)!);

    for (const ws of uniqueWs) {
      ws.status = 'occupied';
      ws.departmentId = dto.department;
      if (dto.user) {
        ws.userId = dto.user;
      }
    }

    return await this.workstationRepo.save(uniqueWs);
  }

  async release(id: string | number) {
    let ws = await this.workstationRepo.findOne({ where: { id: Number(id) } });
    if (!ws) {
        ws = await this.workstationRepo.findOne({ where: { code: String(id) } });
    }

    if (!ws) {
      throw new BadRequestException('Workstation not found');
    }

    ws.status = 'vacant';
    ws.departmentId = null;
    ws.userId = null;
    return await this.workstationRepo.save(ws);
  }

  // --- Shared Workstation Booking ---

  async findAvailable(date: string, startTime?: string, endTime?: string) {
    const sharedWs = await this.workstationRepo.find({ where: { type: 'shared' } });
    
    if (!startTime || !endTime) {
        return { list: sharedWs };
    }

    const start = new Date(startTime);
    const end = new Date(endTime);

    const conflictingBookings = await this.bookingRepo.createQueryBuilder('booking')
        .where('booking.status = :status', { status: 'active' })
        .andWhere('booking.startTime < :end', { end })
        .andWhere('booking.endTime > :start', { start })
        .select('booking.workstationId')
        .getRawMany();
    
    // getRawMany returns object like { booking_workstation_id: 1 } depending on driver
    // Safe way: just select IDs
    const busyIds = conflictingBookings.map(b => {
        // Try to guess the key or inspect
        return Object.values(b)[0]; 
    });

    const available = sharedWs.filter(ws => !busyIds.includes(ws.id));

    return { list: available };
  }

  async createBooking(dto: CreateBookingDto) {
    let wsId = dto.workstationId;
    
    if (typeof wsId === 'string' && isNaN(Number(wsId))) {
         const ws = await this.workstationRepo.findOne({ where: { code: wsId } });
         if (!ws) throw new BadRequestException('Workstation not found');
         wsId = ws.id;
    }

    const start = new Date(dto.startTime);
    const end = new Date(dto.endTime);

    const conflict = await this.bookingRepo.createQueryBuilder('booking')
        .where('booking.workstationId = :wsId', { wsId })
        .andWhere('booking.status = :status', { status: 'active' })
        .andWhere('booking.startTime < :end', { end })
        .andWhere('booking.endTime > :start', { start })
        .getCount();

    if (conflict > 0) {
        throw new BadRequestException('Time slot conflict');
    }

    const booking = new WorkstationBookingEntity();
    booking.workstationId = Number(wsId);
    booking.userId = dto.user;
    booking.startTime = start;
    booking.endTime = end;
    booking.status = 'active';
    
    const now = new Date();
    if (now >= start && now <= end) {
        await this.workstationRepo.update(wsId, { status: 'occupied' });
    }

    return await this.bookingRepo.save(booking);
  }

  async findBookings(query: QueryBookingDto) {
     const page = query.page || 1;
     const pageSize = query.pageSize || 10;
     const skip = (page - 1) * pageSize;

     const qb = this.bookingRepo.createQueryBuilder('booking')
        .leftJoinAndSelect('booking.workstation', 'ws')
        .orderBy('booking.createdAt', 'DESC');

     if (query.user) {
         qb.andWhere('booking.userId LIKE :user', { user: `%${query.user}%` });
     }
     
     if (query.date) {
         const dStart = new Date(query.date);
         dStart.setHours(0,0,0,0);
         const dEnd = new Date(query.date);
         dEnd.setHours(23,59,59,999);
         qb.andWhere('booking.startTime BETWEEN :dStart AND :dEnd', { dStart, dEnd });
     }

     qb.skip(skip).take(pageSize);
     const [list, total] = await qb.getManyAndCount();
     return { list, total, page, pageSize };
  }

  async cancelBooking(id: string | number) {
      const booking = await this.bookingRepo.findOne({ where: { id: Number(id) } });
      if (!booking) throw new BadRequestException('Booking not found');

      booking.status = 'cancelled';
      await this.bookingRepo.save(booking);

      const now = new Date();
      if (now >= booking.startTime && now <= booking.endTime) {
          await this.workstationRepo.update(booking.workstationId, { status: 'vacant' });
      }

      return { success: true };
  }

  async getStatistics() {
      const total = await this.workstationRepo.count();
      const occupied = await this.workstationRepo.count({ where: { status: 'occupied' } });
      
      const releaseCount = 25; // Mock

      const bookingTrend = [
          { date: "2023-10-14", count: 45 }
      ];

      const departmentUsage = await this.workstationRepo.createQueryBuilder('ws')
          .select('ws.departmentId', 'name')
          .addSelect('COUNT(ws.id)', 'value')
          .where('ws.departmentId IS NOT NULL')
          .groupBy('ws.departmentId')
          .getRawMany();

      return {
          realtime: {
              total,
              occupied,
              available: total - occupied,
              releaseCount
          },
          bookingTrend,
          departmentUsage
      };
  }
}
import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';
import { ApiProperty } from '@nestjs/swagger';

/**
 * workstation 表
 */
@Entity('workstation')
export class Workstation {
  @ApiProperty({ description: 'id' })
  @PrimaryGeneratedColumn()
  id: number;

  @ApiProperty({ description: '工位编号' })
  @Column({
    type: 'varchar',
    length: 50,
    unique: true,
    comment: '工位编号',
  })
  code: string;

  @ApiProperty({ description: '位置描述' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '位置描述',
    nullable: true,
  })
  locationDesc: string;

  @ApiProperty({ description: '类型: fixed(固定), shared(共享)' })
  @Column({
    type: 'varchar',
    length: 20,
    comment: '类型: fixed(固定), shared(共享)',
  })
  type: string;

  @ApiProperty({ description: '状态: vacant(空闲), occupied(占用), maintenance(维护中)' })
  @Column({
    type: 'varchar',
    length: 20,
    comment: '状态: vacant(空闲), occupied(占用), maintenance(维护中)',
    default: 'vacant',
  })
  status: string;

  @ApiProperty({ description: '标签/设施' })
  @Column({
    type: 'json',
    nullable: true,
    comment: '标签/设施',
  })
  features: string[];

  @ApiProperty({ description: '所属部门 (仅固定工位)' })
  @Column({
    type: 'varchar',
    length: 100,
    nullable: true,
    comment: '所属部门',
  })
  departmentId: string;

  @ApiProperty({ description: '当前使用人 (仅固定工位)' })
  @Column({
    type: 'varchar',
    length: 100,
    nullable: true,
    comment: '当前使用人',
  })
  userId: string;

  @ApiProperty({ description: '所属空间' })
  @Column({
    type: 'varchar',
    length: 50,
    nullable: true,
    comment: '所属空间',
  })
  spaceCode: string;

  @ApiProperty({ description: '所属空间区域' })
  @Column({
    type: 'varchar',
    length: 50,
    nullable: true,
    comment: '所属空间区域',
  })
  areaCode: string;

  @ApiProperty({ description: '所属楼层' })
  @Column({
    type: 'varchar',
    length: 50,
    nullable: true,
    comment: '所属楼层',
  })
  floorCode: string;

  @ApiProperty({ description: '所属楼层区域' })
  @Column({
    type: 'varchar',
    length: 50,
    nullable: true,
    comment: '所属楼层区域',
  })
  floorAreaCode: string;

  @ApiProperty({ description: 'posX' })
  @Column({
    type: 'varchar',
    length: 50,
    nullable: true,
    comment: 'posX',
  })
  posX: string;

  @ApiProperty({ description: 'posY' })
  @Column({
    type: 'varchar',
    length: 50,
    nullable: true,
    comment: 'posY',
  })
  posY: string;

  @ApiProperty({ description: 'posZ' })
  @Column({
    type: 'varchar',
    length: 50,
    nullable: true,
    comment: 'posZ',
  })
  posZ: string;
}
import { Injectable, Logger, HttpException, HttpStatus } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, In, Not } from 'typeorm';
import { User } from '../entities/User';
import { Department } from '../entities/Department';
import { SystemRole } from '../entities/SystemRole';
import { UserRole } from '../entities/UserRole';
import { Org } from '../entities/Org';
import { UserPcTokens } from '../entities/UserPcTokens';
import { UserListDto, UserListItemDto } from './dto/user-list.dto';
import { UserEditDto } from './dto/user-edit.dto';
import * as bcrypt from 'bcrypt';
import { ChangeDepDto } from './dto/change-dep.dto';

@Injectable()
export class UserService {
  private readonly logger = new Logger(UserService.name);

  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
    @InjectRepository(Department)
    private departmentRepository: Repository<Department>,
    @InjectRepository(SystemRole)
    private systemRoleRepository: Repository<SystemRole>,
    @InjectRepository(UserRole)
    private userRoleRepository: Repository<UserRole>,
    @InjectRepository(UserPcTokens)
    private userPcTokensRepository: Repository<UserPcTokens>,
    @InjectRepository(Org)
    private orgRepository: Repository<Org>,
  ) {}

  async getListByDepartmentId(
    dto: UserListDto,
  ): Promise<{ list: UserListItemDto[]; total: number }> {
    const page = dto.pageNo || 1;
    const pageSize = dto.pageSize || 20;
    const skip = (page - 1) * pageSize;

    // Build base query
    const queryBuilder = this.userRepository
      .createQueryBuilder('user')
      .where('user.deleteFlag = :deleteFlag', { deleteFlag: 1 })
      // .andWhere('user.userName != :admin', { admin: 'admin' })//返回非admin用户
      .andWhere('user.userStatus = :userStatus', { userStatus: '0' });

    // Add department filter
    if (dto.depid) {
      queryBuilder.andWhere('user.departmentId = :departmentId', {
        departmentId: dto.depid,
      });
    }
    // Add org filter
    if (dto.orgid) {
      queryBuilder.andWhere('user.orgId = :orgId', {
        orgId: Number(dto.orgid),
      });
    }

    // Add username/email/empNo/virtualEmpNo search
    if (dto.username) {
      queryBuilder.andWhere(
        '(user.realName LIKE :search OR user.email LIKE :search OR user.empNo LIKE :search OR user.virtualEmpNo LIKE :search)',
        { search: `%${dto.username}%` },
      );
    }

    // Add role filter
    if (dto.role) {
      queryBuilder.andWhere(
        'EXISTS (SELECT 1 FROM user_role ur WHERE ur.userId = user.userId AND ur.roleID = :roleId)',
        { roleId: dto.role },
      );
    }

    // Get total count
    const total = await queryBuilder.getCount();

    // Add pagination and ordering
    queryBuilder.orderBy('user.createtime', 'DESC').skip(skip).take(pageSize);

    // Get users
    const users = await queryBuilder.getMany();

    // 获取所有组织
    const allOrgs = await this.orgRepository.find({
      where: { deleteFlag: 1 }
    });
    const orgMap = new Map(
      allOrgs.map((o) => [o.orgId.toString(), o]),
    );

    // 获取所有部门
    const allDepartments = await this.departmentRepository.find({
      where: { deleteFlag: 1 }
    });
    const departmentMap = new Map(
      allDepartments.map((d) => [d.departmentId.toString(), d]),
    );

    // Get roles for all users
    const userRoles = await this.userRoleRepository.find({
      where: {
        userId: In(users.map((u) => u.userId.toString())),
      },
    });

    const userRoleMap = new Map<
      string,
      {
        roles: string[];
        roleNames: string[];
      }
    >();

    for (const ur of userRoles) {
      if (!userRoleMap.has(ur.userId)) {
        userRoleMap.set(ur.userId, {
          roles: [],
          roleNames: [],
        });
      }
      const roleInfo = userRoleMap.get(ur.userId)!;
      roleInfo.roles.push(ur.roleID);
      roleInfo.roleNames.push(ur.roleCode); // Use roleCode as name since we don't have system_role table
    }

    // 构建部门路径的辅助函数
    const buildDepartmentPath = (departmentId: string | null | undefined): string => {
      if (!departmentId || departmentId === '0') {
        return '';
      }

      const department = departmentMap.get(departmentId);
      if (!department) {
        return '';
      }

      // 获取部门路径
      const path: string[] = [];
      let currentDepartment = department;
      
      // 添加当前部门
      path.unshift(currentDepartment.departmentName);
      
      // 添加所有父部门
      while (currentDepartment.parentId && currentDepartment.parentId !== 0) {
        const parentDepartment = departmentMap.get(currentDepartment.parentId.toString());
        if (!parentDepartment) break;
        
        path.unshift(parentDepartment.departmentName);
        currentDepartment = parentDepartment;
      }
      
      return path.join('/');
    };

    // Map users to response DTOs
    const list = users.map((user) => {
      const org = orgMap.get(user.orgId?.toString() || '');
      const department = departmentMap.get(user.departmentId?.toString() || '');
      const roleInfo = userRoleMap.get(user.userId.toString()) || {
        roles: [],
        roleNames: [],
      };

      // 构建组织部门路径
      let orgPath = '';
      
      // 添加组织名称
      if (org) {
        orgPath = org.orgName;
      }
      
      // 如果有部门，添加部门路径
      const departmentPath = buildDepartmentPath(user.departmentId?.toString());
      if (departmentPath) {
        orgPath = orgPath ? `${orgPath}/${departmentPath}` : departmentPath;
      }

      return {
        id: user.id,
        userId: user.userId,
        orgId: user.orgId?.toString() || '',
        orgName: orgPath, // 组织部门路径
        departmentId: user.departmentId?.toString() || '',
        departmentName: department?.departmentName || '',
        username: user.userName,
        floor: user.floor,
        phone:user.phone,
        stationNum: user.stationNum,
        empNo: user.empNo,
        realName: user.realName,
        flowerName: user.flowerName,
        gender: user.gender,
        avatar: user.avatar,
        email: user.email,
        sourceFrom: user.sourceFrom,
        virtualEmpNo: user.virtualEmpNo,
        cardNum: user.cardNum,
        site: user.site,
        quitStatus: user.quitStatus,
        userStatus: user.userStatus,
        userType: user.userType,
        domainAccount: user.domainAccount,
        roles: roleInfo.roles,
        roleNames: roleInfo.roleNames,
        datetime: user.createtime,
      };
    });

    return { list, total };
  }

  async searchUsersByName(name: string): Promise<{ list: any[]; total: number }> {
    const qb = this.userRepository
      .createQueryBuilder('u')
      .leftJoin(Department, 'd', 'u.departmentId = d.departmentId')
      .where('u.userStatus = :userStatus', { userStatus: 0 })
      .andWhere('u.deleteFlag = :deleteFlag', { deleteFlag: 1 })
      .andWhere('u.realName LIKE :name', { name: `%${name}%` });
    const total = await qb.getCount();
    const list = await qb
      .select([
        'u.userId AS userId',
        'u.realName AS realName',
        'u.empNo AS empNo',
        'u.virtualEmpNo AS virtualEmpNo',
        'd.departmentName AS departmentName',
      ])
      .orderBy('u.realName', 'ASC')
      .getRawMany();
    return { list, total };
  }

  /**
   * 新增或编辑用户信息和角色
   * @param dto 用户编辑DTO
   * @returns 操作结果
   */
  async editUser(dto: UserEditDto): Promise<{ code: string; msg: string; data?: { userId: string } }> {
    const queryRunner = this.userRepository.manager.connection.createQueryRunner();
    
    await queryRunner.connect();
    await queryRunner.startTransaction();
    
    try {
      this.logger.log(`开始处理用户: ${JSON.stringify(dto)}`);
      
      let userId: string;
      
      // 判断是新增用户还是编辑用户
      if (!dto.userId) {
        // 新增用户逻辑
        this.logger.log('执行新增用户逻辑');
        
        // 创建新用户
        const newUser = new User();
        newUser.orgId = Number(dto.orgId);
        newUser.departmentId = Number(dto.departmentId);
        newUser.realName = dto.realName;
        newUser.gender = dto.gender || 0;
        newUser.phone = dto.phone || '';
        newUser.quitStatus = dto.quitStatus || 0;
        
        if (dto.empNo) {
          newUser.empNo = dto.empNo;
        }
        
        if (dto.email) {
          newUser.email = dto.email;
        }
        
        // 设置默认密码 (使用与PHP版本相同的密码生成逻辑)
        // newUser.passwd = this.generatePassword('User@Pass123!');
        newUser.passwd = await this.generatePassword('123456');
        
        // 设置创建时间
        newUser.createtime = Math.floor(Date.now() / 1000).toString();
        
        // 设置用户状态为正常
        newUser.userStatus = 0;
        
        // 设置删除标志为未删除
        newUser.deleteFlag = 1;
        
        // 保存用户
        const savedUser = await queryRunner.manager.save(newUser);
        
        // 获取自增ID作为userId
        userId = savedUser.id.toString();
        
        // 更新userId字段
        savedUser.userId = Number(userId);
        
        // 生成虚拟员工编号
        const virtualEmpNo = `w${userId}`;
        savedUser.virtualEmpNo = virtualEmpNo;
        
        // 保存更新后的用户
        await queryRunner.manager.save(savedUser);
        
        this.logger.log(`新增用户成功: ${userId}`);
      } else {
        // 编辑用户逻辑
        this.logger.log('执行编辑用户逻辑');
        
        // 检查用户是否存在
        const user = await this.userRepository.findOne({ 
          where: { userId: Number(dto.userId) } 
        });
        
        if (!user) {
          throw new HttpException(
            { code: '400', msg: '无效用户' },
            HttpStatus.BAD_REQUEST
          );
        }
        
        // 更新用户基本信息
        user.orgId = Number(dto.orgId);
        user.departmentId = Number(dto.departmentId);
        user.realName = dto.realName;
        user.gender = dto.gender || 0;
        user.phone = dto.phone || '';
        user.quitStatus = dto.quitStatus || 0;
        if (dto.empNo) {
          user.empNo = dto.empNo;
        }
        
        if (dto.email) {
          user.email = dto.email;
        }
        
        await queryRunner.manager.save(user);
        
        userId = dto.userId;
      }
      
      // 删除现有角色关联
      await queryRunner.manager.delete(UserRole, { userId: userId.toString() });
      
      // 添加新角色关联
      for (const roleId of dto.roles) {
        const systemRole = await this.systemRoleRepository.findOne({
          where: { id: roleId }
        });
        
        if (!systemRole) {
          this.logger.warn(`角色ID ${roleId} 不存在，跳过`);
          continue;
        }
        
        const userRole = new UserRole();
        userRole.userId = userId.toString();
        userRole.roleID = systemRole.id.toString();
        userRole.spaceCode = systemRole.spaceCode;
        userRole.roleCode = systemRole.code;
        userRole.createtime = Math.floor(Date.now() / 1000).toString();
        
        await queryRunner.manager.save(userRole);
      }
      
      // 提交事务
      await queryRunner.commitTransaction();
      
      this.logger.log(`用户操作成功: ${userId}`);
      
      return {
        code: '200',
        msg: '操作成功',
        data: { userId: userId }
      };
    } catch (error) {
      // 回滚事务
      await queryRunner.rollbackTransaction();
      
      this.logger.error(`用户操作失败: ${error.message}`, error.stack);
      
      // 如果是已经格式化的HttpException，直接抛出
      if (error instanceof HttpException) {
        throw error;
      }
      
      // 否则包装成标准格式
      throw new HttpException(
        { code: '400', msg: `操作失败: ${error.message}` },
        HttpStatus.BAD_REQUEST
      );
    } finally {
      // 释放查询运行器
      await queryRunner.release();
    }
  }

  /**
   * 生成密码哈希
   * @param password 原始密码
   * @returns 哈希后的密码
   */
  private generatePassword = async (password: string): Promise<string> => {
    // 这里实现与PHP版本相同的密码生成逻辑
    // 简单示例，实际应使用更安全的方法
    // const crypto = require('crypto');
    // const salt = 'buildingos';
    // const hash = crypto.createHash('md5').update(password + salt).digest('hex');
    const hashedPassword = await bcrypt.hash(password, 10);
    return hashedPassword;
  }

  /**
   * 绑定微信用户
   * @param params 用户信息参数
   * @returns 操作结果
   */
  async bindUser(params: {
    spaceCode: string;
    realName: string;
    phone: string;
    email: string;
    orgId: string;
    orgType: string;
    depId: string;
    headImg: string;
    unionid: string;
  }): Promise<{ code: string; msg: string; data?: { userId: string } }> {
    const queryRunner = this.userRepository.manager.connection.createQueryRunner();
    
    await queryRunner.connect();
    await queryRunner.startTransaction();
    
    try {
      this.logger.log(`开始处理微信用户绑定: ${JSON.stringify(params)}`);
      
      // 解析组织信息
      const { 
        spaceCode, 
        realName, 
        phone, 
        email, 
        orgId: orgIdStr, 
        orgType, 
        depId: depIdStr, 
        headImg, 
        unionid 
      } = params;
      
      let orgId: number = Number(orgIdStr) || 0;
      let departmentId: number = 0;
      
      // 根据组织类型设置部门ID
      if (orgType === 'department' && depIdStr) {
        departmentId = Number(depIdStr);
        
        // 如果没有提供组织ID，则从部门获取
        if (orgId === 0) {
          const department = await this.departmentRepository.findOne({
            where: { departmentId: departmentId }
          });
          
          if (department && department.orgId) {
            orgId = department.orgId;
          }
        }
      } else if (orgType === 'org') {
        // 如果是组织类型，确保部门ID为null
        departmentId = 0;
      }
      
      // 查找是否已存在相同 unionid 的用户
      let user = await this.userRepository.findOne({
        where: { unionid, deleteFlag: 1 }
      });
      
      let userId: string;
      
      if (user) {
        // 更新现有用户
        this.logger.log(`更新现有微信用户: ${user.userId}`);
        
        user.realName = realName;
        user.phone = phone;
        user.email = email;
        user.avatar = headImg;
        
        // 根据组织类型更新用户的组织和部门信息
        user.orgId = orgId;
        if(departmentId!==0){
          user.departmentId = departmentId;
        }
        await queryRunner.manager.save(user);
        userId = user.userId.toString();
      } else {
        // 创建新用户
        this.logger.log('创建新微信用户');
        
        // 生成虚拟工号
        // 获取当前最大的 W 开头的虚拟工号
        const maxEmpNoUser = await this.userRepository
          .createQueryBuilder('user')
          .where('user.virtualEmpNo LIKE :pattern', { pattern: 'W%' })
          .orderBy('CAST(SUBSTRING(user.virtualEmpNo, 2) AS UNSIGNED)', 'DESC')
          .getOne();
        
        let nextNumber = 1;
        if (maxEmpNoUser && maxEmpNoUser.virtualEmpNo) {
          const currentNumber = parseInt(maxEmpNoUser.virtualEmpNo.substring(1), 10);
          if (!isNaN(currentNumber)) {
            nextNumber = currentNumber + 1;
          }
        }
        
        const empNo = `W${nextNumber}`;
        
        // 创建新用户
        const newUser = new User();
        newUser.realName = realName;
        newUser.userName = empNo; // 使用虚拟工号作为用户名
        newUser.empNo = empNo;
        newUser.virtualEmpNo = empNo;
        newUser.phone = phone;
        newUser.email = email;
        newUser.avatar = headImg;
        newUser.unionid = unionid;
        newUser.sourceFrom = 'weixin';
        // newUser.userStatus = 1; // 启用状态
        newUser.deleteFlag = 1; // 未删除
        newUser.quitStatus = 1; //默认离职状态
        
        // 设置组织和部门
        newUser.orgId = orgId;
        if(departmentId!==0){
          newUser.departmentId = departmentId;
        }
        // 设置默认密码
        newUser.passwd = await this.generatePassword('123456');
        
        // 设置创建时间
        newUser.createtime = Math.floor(Date.now() / 1000).toString();
        
        // 保存用户
        const savedUser = await queryRunner.manager.save(newUser);
        
        // 获取自增ID作为userId
        const id = savedUser.id.toString();
        
        // 更新userId字段
        savedUser.userId = Number(id);
        await queryRunner.manager.save(savedUser);
        
        userId = id;
        
        this.logger.log(`创建微信用户成功: ${userId}`);
        
        // 为用户添加默认角色
        // 查询默认用户角色
        const defaultUserRole = await this.userRoleRepository.findOne({
          where: { roleCode: 'User' }
        });

        
        // 为用户添加默认角色
        const userRole = new UserRole();
        userRole.userId = userId;
        userRole.roleID = defaultUserRole ? defaultUserRole.roleID : '1'; // 使用查询到的roleID，如果没找到则使用默认值'1'
        userRole.roleCode = 'User'; // 默认用户角色代码
        userRole.spaceCode = spaceCode;
        userRole.createtime = Math.floor(Date.now() / 1000).toString();
        
        await queryRunner.manager.save(userRole);
      }
      
      // 提交事务
      await queryRunner.commitTransaction();
      
      return {
        code: '200',
        msg: '绑定成功',
        data: { userId }
      };
    } catch (error) {
      // 回滚事务
      await queryRunner.rollbackTransaction();
      
      this.logger.error(`微信用户绑定失败: ${error.message}`, error.stack);
      
      return {
        code: '500',
        msg: `绑定失败: ${error.message}`
      };
    } finally {
      // 释放查询运行器
      await queryRunner.release();
    }
  }

  /**
   * 批量更新用户部门
   * @param dto 部门变更DTO
   * @returns 操作结果
   */
  async changeDepartment(dto: ChangeDepDto): Promise<{ code: string; msg: string }> {
    const queryRunner = this.userRepository.manager.connection.createQueryRunner();
    
    await queryRunner.connect();
    await queryRunner.startTransaction();
    
    try {
      this.logger.log(`开始批量更新用户部门: ${JSON.stringify(dto)}`);
      
      const { orgid, depid, depName, changeUser } = dto;
      
      // 不再检查部门是否存在
      
      // 批量更新用户部门
      for (const userId of changeUser) {
        // 检查用户是否存在
        const user = await queryRunner.manager.findOne(User, {
          where: { userId: userId, deleteFlag: 1 }
        });
        
        if (!user) {
          this.logger.warn(`用户ID ${userId} 不存在，跳过`);
          continue;
        }
        
        // 更新用户组织ID
        user.orgId = Number(orgid);
        
        // 更新用户部门ID（可以为空）
        if (depid) {
          user.departmentId = Number(depid);
        } else {
          user.departmentId = 0; // 或者设置为0，取决于你的数据库设计
        }
        
        // 不需要存储depName，因为它不是User表的字段
        // 部门名称通常是从Department表中查询的
        
        await queryRunner.manager.save(user);
        
        this.logger.log(`已更新用户 ${userId} 的组织为 ${orgid}，部门为 ${depid || '无'}`);
      }
      
      // 提交事务
      await queryRunner.commitTransaction();
      
      this.logger.log(`批量更新用户部门成功`);
      
      return {
        code: '200',
        msg: '操作成功'
      };
    } catch (error) {
      // 回滚事务
      await queryRunner.rollbackTransaction();
      
      this.logger.error(`批量更新用户部门失败: ${error.message}`, error.stack);
      
      if (error instanceof HttpException) {
        throw error;
      }
      
      throw new HttpException(
        { code: '400', msg: `操作失败: ${error.message}` },
        HttpStatus.BAD_REQUEST
      );
    } finally {
      // 释放查询运行器
      await queryRunner.release();
    }
  }

  /**
   * 重置用户密码为默认密码 (123456)
   * @param userId 用户ID
   * @returns 操作结果
   */
  async resetPassword(userId: string): Promise<{ code: string; msg: string }> {
    try {
      this.logger.log(`开始重置用户密码: ${userId}`);
      
      // 查找用户
      const user = await this.userRepository.findOne({ 
        where: { userId: Number(userId), deleteFlag: 1 } 
      });
      
      if (!user) {
        throw new HttpException(
          { code: '400', msg: '用户不存在或已被删除' },
          HttpStatus.BAD_REQUEST
        );
      }
      
      // 生成新密码哈希
      const defaultPassword = '123456';
      const hashedPassword = await this.generatePassword(defaultPassword);
      
      // 更新用户密码
      user.passwd = hashedPassword;
      
      // 保存更新
      await this.userRepository.save(user);
      
      this.logger.log(`用户密码重置成功: ${userId}`);
      
      return {
        code: '200',
        msg: 'success'
      };
    } catch (error) {
      this.logger.error(`重置密码失败: ${error.message}`, error.stack);
      
      // 如果是已经格式化的HttpException，直接抛出
      if (error instanceof HttpException) {
        throw error;
      }
      
      // 否则包装成标准格式
      throw new HttpException(
        { code: '400', msg: `重置密码失败: ${error.message}` },
        HttpStatus.BAD_REQUEST
      );
    }
  }

  /**
   * 切换用户在职状态
   * @param params 包含用户ID的参数对象
   * @returns 操作结果
   */
  async changeUserStatus(params: { userId: number }): Promise<{ code: string; msg: string }> {
    try {
      this.logger.log(`开始切换用户在职状态: userId=${params.userId}`);
      
      // 查找用户
      const user = await this.userRepository.findOne({ 
        where: { userId: params.userId, deleteFlag: 1 } 
      });
      
      if (!user) {
        throw new HttpException(
          { code: '400', msg: '用户不存在或已被删除' },
          HttpStatus.BAD_REQUEST
        );
      }
      
      // 切换在职状态：0->1 或 1->0
      user.quitStatus = user.quitStatus === 0 ? 1 : 0;
      
      // 保存更新
      await this.userRepository.save(user);
      
      this.logger.log(`用户在职状态切换成功: userId=${params.userId}, 新状态=${user.quitStatus}`);
      
      return {
        code: '200',
        msg: '操作成功'
      };
    } catch (error) {
      this.logger.error(`切换用户在职状态失败: ${error.message}`, error.stack);
      
      // 如果是已经格式化的HttpException，直接抛出
      if (error instanceof HttpException) {
        throw error;
      }
      
      // 否则包装成标准格式
      throw new HttpException(
        { code: '400', msg: `操作失败: ${error.message}` },
        HttpStatus.BAD_REQUEST
      );
    }
  }

  /**
   * 根据unionid获取用户信息
   * @param params 包含unionid的参数对象
   * @returns 用户信息
   */
  async getUserByUnionid(params: { unionid: string }): Promise<{ code: string; msg: string; data?: any }> {
    try {
      this.logger.log(`根据unionid获取用户信息: unionid=${params.unionid}`);
      
      // 查找用户
      const user = await this.userRepository.findOne({ 
        where: { unionid: params.unionid, deleteFlag: 1 } 
      });
      
      if (!user) {
        return {
          code: '400',
          msg: '未找到此用户'
        };
      }
      
      // 获取部门信息
      let departmentName = '';
      if (user.departmentId) {
        const department = await this.departmentRepository.findOne({
          where: { departmentId: user.departmentId }
        });
        departmentName = department ? department.departmentName : '';
      }
      
      // 获取组织信息
      let orgName = '';
      if (user.orgId) {
        const org = await this.orgRepository.findOne({
          where: { orgId: user.orgId }
        });
        orgName = org ? org.orgName : '';
      }
      
      // 获取用户角色
      const userRoles = await this.userRoleRepository.find({
        where: { userId: user.userId.toString() }
      });
      
      const roles = userRoles.map(role => role.roleCode);
      
      // 构建返回数据
      const userData = {
        userId: user.userId,
        userName: user.userName,
        realName: user.realName,
        email: user.email,
        phone: user.phone,
        avatar: user.avatar,
        empNo: user.empNo,
        virtualEmpNo: user.virtualEmpNo,
        orgId: user.orgId,
        orgName: orgName,
        departmentId: user.departmentId,
        departmentName: departmentName,
        quitStatus: user.quitStatus,
        userStatus: user.userStatus,
        roles: roles,
        createtime: user.createtime
      };
      
      return {
        code: '200',
        msg: 'success',
        data: userData
      };
    } catch (error) {
      this.logger.error(`根据unionid获取用户信息失败: ${error.message}`, error.stack);
      
      return {
        code: '500',
        msg: `获取用户信息失败: ${error.message}`
      };
    }
  }

  /**
   * 检查用户表是否为空
   * @returns 是否为空
   */
  async isUserTableEmpty(): Promise<boolean> {
    const userCount = await this.userRepository.count();
    return userCount === 0;
  }

  /**
   * 创建默认管理员用户
   * @returns 操作结果
   */
  async createDefaultAdminUser(): Promise<{ code: string; msg: string; data?: any }> {
    try {
      // 检查是否已存在admin用户
      const existingAdmin = await this.userRepository.findOne({
        where: { userName: 'admin' }
      });

      if (existingAdmin) {
        return {
          code: '200',
          msg: 'Admin用户已存在',
          data: { userId: existingAdmin.userId }
        };
      }

      // 创建默认管理员用户
      const adminUser = new User();
      adminUser.userName = 'admin';
      adminUser.realName = '系统管理员';
      adminUser.sourceFrom = 'self';
      adminUser.passwd = await this.generatePassword('buildingos');
      adminUser.email = 'admin@buildingos.com';
      adminUser.empNo = 'ADMIN001';
      adminUser.gender = 0;
      adminUser.phone = '13800138000';
      adminUser.userStatus = 0; // 启用状态
      adminUser.deleteFlag = 1; // 未删除
      adminUser.quitStatus = 0; // 在职状态
      adminUser.createtime = Math.floor(Date.now() / 1000).toString();

      // 保存用户
      const savedUser = await this.userRepository.save(adminUser);
      
      // 更新userId字段
      savedUser.userId = savedUser.id;
      await this.userRepository.save(savedUser);

      this.logger.log(`默认管理员用户创建成功: admin (ID: ${savedUser.id})`);

      return {
        code: '200',
        msg: '默认管理员用户创建成功',
        data: { userId: savedUser.userId }
      };
    } catch (error) {
      this.logger.error(`创建默认管理员用户失败: ${error.message}`);
      return {
        code: '500',
        msg: '创建默认管理员用户失败',
        data: { error: error.message }
      };
    }
  }

  /**
   * 创建演示数据（组织、部门、用户）
   */
  async createDemoData() {
    this.logger.log('Start creating demo data...');
    const queryRunner = this.userRepository.manager.connection.createQueryRunner();
    await queryRunner.connect();
    await queryRunner.startTransaction();

    try {
      // 1. Create Organization "demo公司"
      // Try to find org with orgId=1 first
      let org = await this.orgRepository.findOne({ where: { orgId: 1 } });
      if (!org) {
        org = await this.orgRepository.findOne({ where: { orgName: 'demo公司' } });
      }

      let orgId = 0;
      if (!org) {
        org = new Org();
        org.orgName = 'demo公司';
        org.orgType = 'company';
        org.parentId = 0;
        org.sortOrder = 0;
        org.deleteFlag = 1;
        org.createtime = Math.floor(Date.now() / 1000).toString();
        const savedOrg = await queryRunner.manager.save(org);
        orgId = savedOrg.id;
        savedOrg.orgId = orgId; // Ensure orgId is set
        await queryRunner.manager.save(savedOrg);
        this.logger.log(`Created demo organization: ${org.orgName} (ID: ${orgId})`);
      } else {
        orgId = org.orgId || org.id;
        this.logger.log(`Demo organization exists: ${org.orgName} (ID: ${orgId})`);
      }

      // 2. Create Department "demo部门" under "demo公司"
      // Try to find department with departmentId=1 first
      let dept = await this.departmentRepository.findOne({ where: { departmentId: 1 } });
      if (!dept) {
        dept = await this.departmentRepository.findOne({ where: { departmentName: 'demo部门', orgId: orgId } });
      }

      let deptId = 0;
      if (!dept) {
        dept = new Department();
        dept.departmentName = 'demo部门';
        dept.orgId = orgId;
        dept.parentId = 0;
        dept.deleteFlag = 1;
        dept.createtime = Math.floor(Date.now() / 1000).toString();
        // orgPath logic if needed, simple case: |orgId|
        dept.orgPath = `|${orgId}|`;
        const savedDept = await queryRunner.manager.save(dept);
        deptId = savedDept.id;
        savedDept.departmentId = deptId;
        await queryRunner.manager.save(savedDept);
        this.logger.log(`Created demo department: ${dept.departmentName} (ID: ${deptId})`);
      } else {
        deptId = dept.departmentId || dept.id;
        this.logger.log(`Demo department exists: ${dept.departmentName} (ID: ${deptId})`);
      }

      // 3. Check and create 200 Users (demo1 to demo200)
      const passwordHash = await this.generatePassword('buildingos');
      const now = Math.floor(Date.now() / 1000).toString();
      const surnames = ['赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈', '褚', '卫', '蒋', '沈', '韩', '杨', '朱', '秦', '尤', '许', '何', '吕', '施', '张', '孔', '曹', '严', '华', '金', '魏', '陶', '姜'];
      const names = ['伟', '芳', '娜', '敏', '静', '秀英', '丽', '强', '磊', '军', '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞', '平', '刚', '桂英'];
      
      let createdCount = 0;
      
      for (let i = 1; i <= 200; i++) {
        const targetUserName = `demo${i}`;
        const existingUser = await this.userRepository.findOne({ where: { userName: targetUserName } });
        
        if (existingUser) {
          continue;
        }
        
        const surname = surnames[Math.floor(Math.random() * surnames.length)];
        const name = names[Math.floor(Math.random() * names.length)];
        const realName = `${surname}${name}`;
        const empNo = `DEMO${Date.now().toString().slice(-6)}${i.toString().padStart(3, '0')}`;

        const user = new User();
        user.userName = targetUserName;
        user.realName = realName;
        user.passwd = passwordHash;
        user.orgId = orgId;
        user.departmentId = deptId;
        user.empNo = empNo;
        user.virtualEmpNo = `v${empNo}`;
        user.userStatus = 0;
        user.deleteFlag = 1;
        user.quitStatus = 0;
        user.sourceFrom = 'self';
        user.createtime = now;
        user.gender = Math.random() > 0.5 ? 0 : 1;
        user.phone = `13${Math.floor(Math.random() * 10)}${Math.floor(Math.random() * 100000000).toString().padStart(8, '0')}`;
        
        // Save initial to get ID
        const savedUser = await queryRunner.manager.save(user);
        savedUser.userId = savedUser.id; // Sync userId with id
        await queryRunner.manager.save(savedUser);
        
        createdCount++;
      }
      
      this.logger.log(`Created ${createdCount} new demo users.`);

      await queryRunner.commitTransaction();
      return { code: '200', msg: 'Demo data created successfully' };
    } catch (error) {
      await queryRunner.rollbackTransaction();
      this.logger.error(`Failed to create demo data: ${error.message}`, error.stack);
      throw new HttpException(
        { code: '500', msg: `Failed to create demo data: ${error.message}` },
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    } finally {
      await queryRunner.release();
    }
  }

  /**
   * 初始化用户系统 - 检查并创建默认用户
   * @returns 操作结果
   */
  async initializeUserSystem(): Promise<{ code: string; msg: string; data?: any }> {
    try {
      const isEmpty = await this.isUserTableEmpty();
      
      if (isEmpty) {
        this.logger.log('检测到用户表为空，正在创建默认管理员用户...');
        return await this.createDefaultAdminUser();
      } else {
        this.logger.log('用户表不为空，跳过默认用户创建');
        return {
          code: '200',
          msg: '用户表不为空，跳过默认用户创建'
        };
      }
    } catch (error) {
      this.logger.error(`用户系统初始化失败: ${error.message}`);
      return {
        code: '500',
        msg: '用户系统初始化失败',
        data: { error: error.message }
      };
    }
  }
}
import { Body, Controller, Get, Post, Query, UseGuards, Request, Logger, HttpException, HttpStatus } from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiBody,
} from '@nestjs/swagger';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { UserService } from './user.service';
import { UserListDto, UserListResponseDto } from './dto/user-list.dto';
import { UserEditDto, UserEditResponseDto } from './dto/user-edit.dto';
import { ChangeDepDto, ChangeDepResponseDto } from './dto/change-dep.dto';
import { ResetPasswordDto, ResetPasswordResponseDto } from './dto/reset-password.dto';

interface RequestWithUser {
  user: any;
}

@ApiTags('用户管理')
@ApiBearerAuth()
@Controller('userManagement')
@UseGuards(JwtAuthGuard)
export class UserController {
  private readonly logger = new Logger(UserController.name);

  constructor(private readonly userService: UserService) {}

  @Get('getList')
  @ApiOperation({ summary: '获取用户列表' })
  @ApiResponse({
    status: 200,
    description: '成功',
    type: UserListResponseDto,
  })
  async getList(@Query() dto: UserListDto): Promise<UserListResponseDto> {
    const { list, total } = await this.userService.getListByDepartmentId(dto);
    return {
      code: '200',
      msg: 'success',
      data: {
        total,
        list,
      },
    };
  }

  @Post('doEdit')
  @ApiOperation({ summary: '编辑用户信息和角色' })
  @ApiResponse({
    status: 200,
    description: '操作成功',
    type: UserEditResponseDto,
  })
  @ApiResponse({ status: 400, description: '请求错误' })
  @ApiResponse({ status: 401, description: '未授权' })
  async doEdit(
    @Body() dto: UserEditDto,
    @Request() req: RequestWithUser,
  ): Promise<UserEditResponseDto> {
    try {
      this.logger.log(`处理用户编辑请求: ${JSON.stringify(dto)}`);
      
      // 检查用户是否有权限
      if (!req.user) {
        throw new HttpException(
          { code: '401', msg: '用户登陆信息过期，请重新登陆' },
          HttpStatus.UNAUTHORIZED
        );
      }
      
      // 检查数据权限
      if (!this.checkDataAuth(req.user)) {
        throw new HttpException(
          { code: '400', msg: '无权限操作' },
          HttpStatus.BAD_REQUEST
        );
      }
      
      // // 验证必填字段
      // if (!dto.userId) {
      //   throw new HttpException(
      //     { code: '400', msg: '无效请求' },
      //     HttpStatus.BAD_REQUEST
      //   );
      // }
      
      // 调用服务方法
      return await this.userService.editUser(dto);
    } catch (error) {
      this.logger.error(`用户编辑失败: ${error.message}`, error.stack);
      
      // 如果是已经格式化的HttpException，直接抛出
      if (error instanceof HttpException) {
        throw error;
      }
      
      // 否则包装成标准格式
      throw new HttpException(
        { code: '400', msg: `操作失败: ${error.message}` },
        HttpStatus.BAD_REQUEST
      );
    }
  }

  @Post('doSearchUser')
  @ApiOperation({ summary: '按姓名模糊搜索用户' })
  @ApiResponse({
    status: 200,
    description: '成功',
    type: UserListResponseDto,
  })
  async doSearchUser(
    @Body() body: any,
    @Query() query: any,
    @Request() req: RequestWithUser,
  ): Promise<UserListResponseDto> {
    try {
      if (!req.user) {
        throw new HttpException(
          { code: '401', msg: '用户登陆信息过期，请重新登陆' },
          HttpStatus.UNAUTHORIZED
        );
      }
      const name = (body?.name ?? query?.name ?? '').toString();
      if (!name) {
        throw new HttpException(
          { code: '400', msg: '参数不全' },
          HttpStatus.BAD_REQUEST
        );
      }
      const { list, total } = await this.userService.searchUsersByName(name);
      return {
        code: '200',
        msg: 'success',
        data: { total, list },
      };
    } catch (error) {
      if (error instanceof HttpException) throw error;
      throw new HttpException(
        { code: '400', msg: `操作失败: ${error.message}` },
        HttpStatus.BAD_REQUEST
      );
    }
  }

  // 检查数据权限的辅助方法
  private checkDataAuth(user: any): boolean {
    // 实现权限检查逻辑，参考 core_check_data_auth 函数
    // 这里简化处理，可以根据实际需求完善
    return true; // 默认允许，实际应根据用户角色和权限判断
  }

  @Post('changeDep')
  @ApiOperation({ summary: '批量更新用户部门' })
  @ApiResponse({
    status: 200,
    description: '操作成功',
    type: ChangeDepResponseDto,
  })
  @ApiResponse({ status: 400, description: '请求错误' })
  @ApiResponse({ status: 401, description: '未授权' })
  @ApiBody({ type: ChangeDepDto })
  async changeDep(
    @Body() dto: ChangeDepDto,
    @Request() req: RequestWithUser,
  ): Promise<ChangeDepResponseDto> {
    try {
      this.logger.log(`处理用户部门变更请求: ${JSON.stringify(dto)}`);
      
      // 检查用户是否有权限
      if (!req.user) {
        throw new HttpException(
          { code: '401', msg: '用户登陆信息过期，请重新登陆' },
          HttpStatus.UNAUTHORIZED
        );
      }
      
      // 检查数据权限
      if (!this.checkDataAuth(req.user)) {
        throw new HttpException(
          { code: '400', msg: '无权限操作' },
          HttpStatus.BAD_REQUEST
        );
      }
      
      // 验证必填字段 - 只检查组织ID和用户列表
      if (!dto.orgid || !dto.changeUser || dto.changeUser.length === 0) {
        throw new HttpException(
          { code: '400', msg: '请填写组织ID和用户列表' },
          HttpStatus.BAD_REQUEST
        );
      }
      
      // 调用服务方法
      return await this.userService.changeDepartment(dto);
    } catch (error) {
      this.logger.error(`用户部门变更失败: ${error.message}`, error.stack);
      
      // 如果是已经格式化的HttpException，直接抛出
      if (error instanceof HttpException) {
        throw error;
      }
      
      // 否则包装成标准格式
      throw new HttpException(
        { code: '400', msg: `操作失败: ${error.message}` },
        HttpStatus.BAD_REQUEST
      );
    }
  }

  @Post('resetPwd')
  @ApiOperation({ summary: '重置用户密码' })
  @ApiResponse({
    status: 200,
    description: '密码重置成功',
    type: ResetPasswordResponseDto,
  })
  @ApiResponse({ status: 400, description: '请求错误' })
  @ApiResponse({ status: 401, description: '未授权' })
  @ApiBody({ type: ResetPasswordDto })
  async resetPassword(
    @Body() dto: ResetPasswordDto,
    @Request() req: RequestWithUser,
  ): Promise<ResetPasswordResponseDto> {
    try {
      this.logger.log(`处理用户密码重置请求: ${JSON.stringify(dto)}`);
      
      // 检查用户是否有权限
      if (!req.user) {
        throw new HttpException(
          { code: '401', msg: '用户登陆信息过期，请重新登陆' },
          HttpStatus.UNAUTHORIZED
        );
      }
      
      // 检查数据权限
      if (!this.checkDataAuth(req.user)) {
        throw new HttpException(
          { code: '400', msg: '无权限操作' },
          HttpStatus.BAD_REQUEST
        );
      }
      
      // 调用服务方法
      return await this.userService.resetPassword(dto.userId);
    } catch (error) {
      this.logger.error(`用户密码重置失败: ${error.message}`, error.stack);
      
      // 如果是已经格式化的HttpException，直接抛出
      if (error instanceof HttpException) {
        throw error;
      }
      
      // 否则包装成标准格式
      throw new HttpException(
        { code: '400', msg: `操作失败: ${error.message}` },
        HttpStatus.BAD_REQUEST
      );
    }
  }
}


```

