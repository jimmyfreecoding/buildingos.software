# 源代码提交页（智能楼宇智能卫生间系统 buildingos.toilet）

## 提交要求
- 连续前30页与后30页，每页≥50行
- 不得包含公司、个人、文件名称
- 数量与申请表一致

## 前30页
```
<template>
  <div class="toilet-card-wrapper" v-for="toilet in filteredToilets" :key="toilet.id">
    <div class="toilet-card">
      <div class="card-header">
        <span class="floor-title">{{ floor }}</span>
        <span class="toilet-type">{{ toilet.name }}</span>
      </div>
      
      <div class="cubicles">
        <div 
          v-for="cubicle in toilet.cubicles" 
          :key="cubicle.id" 
          class="indicator"
          :class="cubicle.status"
        ></div>
      </div>

      <div class="env-info" v-if="toilet.env">
        <div class="env-item">
          <div class="item-header">
            <span class="label">温度</span>
            <span class="status">{{ toilet.env.temperature.status }}</span>
          </div>
          <div class="item-value">{{ toilet.env.temperature.value }} {{ toilet.env.temperature.unit }}</div>
          <el-progress :percentage="50" :show-text="false" :stroke-width="4" color="#409eff" />
        </div>
        
        <div class="env-item">
          <div class="item-header">
            <span class="label">湿度</span>
            <span class="status">{{ toilet.env.humidity.status }}</span>
          </div>
          <div class="item-value">{{ toilet.env.humidity.value }}{{ toilet.env.humidity.unit }}</div>
          <el-progress :percentage="60" :show-text="false" :stroke-width="4" color="#409eff" />
        </div>

        <div class="env-item">
          <div class="item-header">
            <span class="label">硫化氢</span>
            <span class="status">{{ toilet.env.h2s.status }}</span>
          </div>
          <div class="item-value">{{ toilet.env.h2s.value }} {{ toilet.env.h2s.unit }}</div>
          <el-progress :percentage="10" :show-text="false" :stroke-width="4" color="#409eff" />
        </div>

        <div class="env-item">
          <div class="item-header">
            <span class="label">PM2.5</span>
            <span class="status">{{ toilet.env.pm25.status }}</span>
          </div>
          <div class="item-value">{{ toilet.env.pm25.value }} {{ toilet.env.pm25.unit }}</div>
          <el-progress :percentage="20" :show-text="false" :stroke-width="4" color="#409eff" />
        </div>

        <div class="env-item">
          <div class="item-header">
            <span class="label">氨气</span>
            <span class="status">{{ toilet.env.nh3.status }}</span>
          </div>
          <div class="item-value">{{ toilet.env.nh3.value }} {{ toilet.env.nh3.unit }}</div>
          <el-progress :percentage="5" :show-text="false" :stroke-width="4" color="#409eff" />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
const props = defineProps({
  floor: {
    type: String,
    required: true
  },
  toilets: {
    type: Array,
    default: () => []
  },
  filterType: {
    type: String,
    default: 'all' // all, male, female
  }
})

const filteredToilets = computed(() => {
  if (props.filterType === 'all') {
    return props.toilets
  }
  return props.toilets.filter((t: any) => t.type === props.filterType)
})
</script>

<style lang="scss" scoped>
.toilet-card-wrapper {
  margin-bottom: 20px;
  grid-column: span 2; // Make it span 2 columns in grid
}

.toilet-card {
  background-color: var(--el-bg-color);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  border: 1px solid var(--el-border-color-light);
  transition: all 0.3s;
  min-width: 600px; // Double the minimum width
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }
  
  .card-header {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    gap: 10px;
    
    .floor-title {
      color: var(--el-text-color-primary);
      font-size: 20px;
      font-weight: bold;
    }
    
    .toilet-type {
      font-size: 16px;
      color: var(--el-text-color-regular);
      background: var(--el-fill-color-light);
      padding: 2px 8px;
      border-radius: 4px;
    }
  }

  .cubicles {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 25px;
    
    .indicator {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      
      &.vacant {
        background-color: var(--el-color-success);
        box-shadow: 0 0 5px rgba(103, 194, 58, 0.5);
      }
      
      &.occupied {
        background-color: var(--el-color-danger);
        box-shadow: 0 0 5px rgba(245, 108, 108, 0.5);
      }
    }
  }

  .env-info {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    border-top: 1px solid var(--el-border-color-light);
    padding-top: 20px;

    .env-item {
      background-color: var(--el-bg-color-overlay); // Changed to white background
      border-radius: 6px;
      padding: 10px;
      color: var(--el-text-color-primary); // Dark text
      border: 1px solid var(--el-border-color-lighter); // Add border

      .item-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
        font-size: 12px;

        .label {
          color: var(--el-text-color-secondary); // Gray text
          display: flex;
          align-items: center;
          gap: 4px;
          &::before {
            content: '';
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: var(--el-color-success);
          }
        }
        
        .status {
          color: var(--el-color-success);
        }
      }

      .item-value {
        font-size: 14px;
        margin-bottom: 8px;
        font-weight: 500;
        color: var(--el-text-color-primary);
      }
      
      :deep(.el-progress-bar__outer) {
        background-color: var(--el-fill-color); // Lighter background for progress bar
      }
    }
  }
}
</style>
<template>
  <div class="toilet-container no-background-container">
    <div class="header-actions">
      <el-button-group>
        <el-button :type="filterType === 'male' ? 'primary' : 'default'" @click="filterType = 'male'">男卫生间</el-button>
        <el-button :type="filterType === 'female' ? 'primary' : 'default'" @click="filterType = 'female'">女卫生间</el-button>
        <el-button :type="filterType === 'all' ? 'primary' : 'default'" @click="filterType = 'all'">全部</el-button>
      </el-button-group>
    </div>
    
    <div v-loading="loading" class="toilet-grid">
      <toilet-card 
        v-for="floor in floorList" 
        :key="floor.id" 
        :floor="floor.floor" 
        :toilets="floor.toilets"
        :filter-type="filterType"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { getToiletStatus } from '/@/api/toilet'
import ToiletCard from './components/ToiletCard.vue'

defineOptions({
  name: 'Toilet',
})

const loading = ref(true)
const floorList = ref<any[]>([])
const filterType = ref('all')

const fetchData = async () => {
  loading.value = true
  try {
    const { data } = await getToiletStatus()
    floorList.value = data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  // Refresh every 30 seconds
  setInterval(fetchData, 30000)
})
</script>

<style lang="scss" scoped>
.toilet-container {
  padding: 20px;
  height: calc(100vh - 100px);
  overflow-y: auto;
  
  .header-actions {
    margin-bottom: 20px;
  }

  .toilet-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); // Adjusted min width for wider cards
    gap: 20px;
  }
}
</style>
<template>
  <vab-dialog v-model="dialogFormVisible" append-to-body :title="title" width="500px" @close="close">
    <el-form ref="formRef" label-width="120px" :model="form" :rules="rules">
      <el-form-item label="名称" prop="name">
        <el-input v-model.trim="form.name" clearable />
      </el-form-item>
      <el-form-item label="卫生间编码" prop="code">
        <el-input v-model.trim="form.code" clearable />
      </el-form-item>
      <el-form-item label="卫生间类型" prop="type">
        <el-select-v2
          v-model="form.type"
          :options="options"
          placeholder="请选择卫生间类型"
          style="width: 100%"
        />
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
import { doToiletEdit } from '/@/api/space.ts'
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
defineOptions({
  name: 'ToiletTableEdit',
})
const options = ref( [
  {label:'男卫生间',value:'man'},
  {label:'女卫生间',value:'woman'},
  {label:'VIP男卫生间',value:'manvip'},
  {label:'VIP女卫生间',value:'womanvip'}
])
const emit = defineEmits(['fetch-data'])
const $baseMessage = inject<any>('$baseMessage')
const formRef = ref<any>(null)
const title = ref<string>('')
const dialogFormVisible = ref<boolean>(false)
const form = reactive<any>({
  areaCode: '',
  code: '',
  type:'',
  deleteFlag: false,
  floorAreaCode: '',
  floorCode: '',
  id: 0,
  name: '',
  sortOrder: 1,
  spaceCode: '',
})
const rules = reactive<any>({
  name: [{ required: true, trigger: 'blur', message: '请输入名称' }],
  code: [{ required: true, trigger: 'blur', message: '请输入编码' }],
  type: [{ required: true, trigger: 'blur', message: '请选择卫生间类型' }],
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
      console.info(form)
      const { msg }: any = await doToiletEdit(form)
      await $baseMessage(msg, 'success', 'hey')
      await close()
      dialogFormVisible.value = false
    }
  })
}
</script>
<template>
  <vab-dialog v-model="dialogFormVisibleRoom" append-to-body :title="title" width="700px" @close="close">
    <el-table v-loading="listLoading" :data="list">
      <el-table-column align="center" label="ID" :min-width="50" prop="id" show-overflow-tooltip />
      <el-table-column align="center" label="排序" :min-width="80" prop="sortOrder" show-overflow-tooltip />
      <el-table-column align="center" label="名称" :min-width="80" prop="name" show-overflow-tooltip />
      <el-table-column align="center" label="编码" :min-width="80" prop="code" show-overflow-tooltip />
      <el-table-column align="center" label="类型" :min-width="80" prop="type" show-overflow-tooltip :sortable="true">
        <template #default="{ row }">
          <el-image v-if="row.type == 0" :src="dunweiImg" style="width: 25px; height: auto" />
          <el-image v-if="row.type == 1" :src="zuoweiiImg" style="width: 25px; height: auto" />
        </template>
      </el-table-column>

      <el-table-column align="center" label="传感器" :min-width="80" prop="sensorIndex" show-overflow-tooltip />

      <!--            <el-table-column align="center" label="状态" :min-width="80" prop="deleteFlag" show-overflow-tooltip :sortable="true">-->
      <!--              <template #default="{ row }">-->
      <!--                <span>-->
      <!--                  <el-switch v-model="row.deleteFlag" active-text="启用" disabled inactive-text="未启用" inline-prompt />-->
      <!--                </span>-->
      <!--              </template>-->
      <!--            </el-table-column>-->
      <el-table-column align="center" label="操作" width="250">
        <template #default="{ row }">
          <el-button text type="primary" @click="editToiletRoom(row)">编辑</el-button>
          <el-button text type="primary" @click="deleteToiletRoom(row)">删除</el-button>
        </template>
      </el-table-column>
      <template #empty>
        <el-empty class="vab-data-empty" description="暂无数据" />
      </template>
    </el-table>

    <template #footer>
      <el-button type="primary" @click="addToileRoom">新增</el-button>
    </template>
  </vab-dialog>
  <toilet-room-edit ref="editRef" :data="queryForm" @fetch-data="fetchData" />
</template>

<script lang="ts" setup>
import { doToiletRoomDelete, getToiletRoomList } from '/@/api/space.ts'
import { ref } from 'vue'
import dunweiImg from '/@/assets/space_images/dunwei.png'
import zuoweiiImg from '/@/assets/space_images/zuowei.png'
const $baseConfirm = inject<any>('$baseConfirm')
const $baseMessage = inject<any>('$baseMessage')
const list = ref<any>([])
const listLoading = ref<boolean>(true)
const title = ref<string>('')
const total = ref<any>(0)
const editRef = ref<any>(null)
const dialogFormVisibleRoom = ref<boolean>(false)
const emit = defineEmits(['fetch-data'])
const queryForm = reactive<any>({
  toiletId: 1,
  pageNo: 1,
  pageSize: 50,
})
const form = reactive<any>({
  toiletId: '',
})
const showEdit = (row: any) => {
  dialogFormVisibleRoom.value = true
  nextTick(() => {
    console.info(row)
    title.value = '编辑'
    Object.assign(form, row)
    console.info('showEdit')
    fetchData()
  })
}
defineExpose({
  showEdit,
})
const fetchData = async () => {
  console.info('fetchData')
  listLoading.value = true
  const { data } = await getToiletRoomList({ toiletId: form.id })
  console.info(data.list)
  list.value = data.list
  total.value = data.total
  listLoading.value = false
}
const addToileRoom = () => {
  editRef.value.showEdit({ id: '', toiletId: form.id })
}
const editToiletRoom = (row: any) => {
  editRef.value.showEdit(row)
}
const deleteToiletRoom = (row: any) => {
  if (row.id) {
    $baseConfirm('您确定要删除当前项吗', null, async () => {
      const { msg }: any = await doToiletRoomDelete({ ids: row.id })
      $baseMessage(msg, 'success', 'hey')
      await fetchData()
    })
  }
}
// onMounted(() => {
//
// })
const close = () => {
  emit('fetch-data')
}
</script>
<template>
  <vab-dialog v-model="dialogFormVisible" append-to-body :title="title" width="500px" @close="close">
    <el-form ref="formRef" label-width="120px" :model="form" :rules="rules">
      <el-form-item label="名称" prop="name">
        <el-input v-model.trim="form.name" clearable />
      </el-form-item>
      <el-form-item label="厕位编码" prop="code">
        <el-input v-model.trim="form.code" clearable />
      </el-form-item>
      <el-form-item label="传感器编号" prop="code">
        <el-input v-model.trim="form.sensorIndex" clearable />
      </el-form-item>
      <el-form-item label="厕位序号" prop="code">
        <el-input v-model.trim="form.sortOrder" clearable />
      </el-form-item>
      <el-form-item label="厕位类型" prop="type">
        <el-select-v2 v-model="form.type" :options="options" placeholder="请选择厕位类型" style="width: 100%" />
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
import { s } from 'vite/dist/node/types.d-aGj9QkWt'
import { doToiletRoomEdit } from '/@/api/space.ts'
const props = defineProps({
  data: {
    type: Object,
    default: () => {
      return {
        pageNo: 1,
        pageSize: 50,
        title: '',
        type: 'all',
      }
    },
  },
})
defineOptions({
  name: 'ToiletRoomTableEdit',
})
const options = ref([
  { label: '蹲式', value: '0' },
  { label: '坐式', value: '1' },
])
const emit = defineEmits(['fetch-data'])
const $baseMessage = inject<any>('$baseMessage')
const formRef = ref<any>(null)
const title = ref<string>('')
const dialogFormVisible = ref<boolean>(false)
const form = reactive<any>({
  code: '',
  type: '',
  id: 0,
  name: '',
  toiletId: '',
  sortOrder: "1", 
  sensorIndex: "1",
})
const blankform = reactive<any>({
  code: '',
  type: '',
  id: 0,
  name: '',
  toiletId: '',
  sortOrder: "1", 
  sensorIndex: "1",
})
const rules = reactive<any>({
  name: [{ required: true, trigger: 'blur', message: '请输入名称' }],
  code: [{ required: true, trigger: 'blur', message: '请输入编码' }],
  type: [{ required: true, trigger: 'blur', message: '请选择厕位类型' }],
})

const showEdit = (row: any) => {
  dialogFormVisible.value = true
  console.info(props.data)
  nextTick(() => {
    if (row.id === '') {
      title.value = '添加'
      Object.assign(form, blankform)
      form.toiletId = row.toiletId
    } else {
      console.info(row)
      title.value = '编辑'
      Object.assign(form, row)
    }
  })
}

defineExpose({
  showEdit,
})

const close = () => {
  formRef.value.clearValidate()
  formRef.value.resetFields()
  emit('fetch-data')
}

const save = () => {
  console.info(form)
  formRef.value.validate(async (valid: any) => {
    if (valid) {
      console.log(form)
      const { msg }: any = await doToiletRoomEdit(form)
      await $baseMessage(msg, 'success', 'hey')
      await close()
      dialogFormVisible.value = false
    }
  })
}
</script>
<template>
  <div class="toilet-container no-background-container auto-height-container">
    <el-row :gutter="20">
      <el-col :lg="5" :md="24" :sm="24" :xl="4" :xs="24">
        <vab-card class="auto-height-card1">
          <el-tree
            ref="treeRef"
            v-loading="treeLoading"
            default-expand-all
            :data="spacedata"
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
            <el-table-column align="center" label="ID" :min-width="50" prop="id" show-overflow-tooltip :sortable="true" />
            <el-table-column align="center" label="名称" :min-width="80" prop="name" show-overflow-tooltip :sortable="true" />
            <el-table-column align="center" label="编码" :min-width="80" prop="code" show-overflow-tooltip :sortable="true" />
            <el-table-column align="center" label="类型" :min-width="80" prop="type" show-overflow-tooltip :sortable="true" />
            <el-table-column align="center" label="厕位" :min-width="200" prop="rooms" show-overflow-tooltip :sortable="true">
              <template #default="{ row }">
                <el-tag v-for="(room, index) in row.rooms" :key="index" style="margin-left: 10px" type="info">
                  {{ room.type }}（room.sortOrder）
                </el-tag>
              </template>
            </el-table-column>

            <!--            <el-table-column align="center" label="状态" :min-width="80" prop="deleteFlag" show-overflow-tooltip :sortable="true">-->
            <!--              <template #default="{ row }">-->
            <!--                <span>-->
            <!--                  <el-switch v-model="row.deleteFlag" active-text="启用" disabled inactive-text="未启用" inline-prompt />-->
            <!--                </span>-->
            <!--              </template>-->
            <!--            </el-table-column>-->
            <el-table-column align="center" :fixed="fixed" label="操作" width="250">
              <template #header>
                <el-checkbox v-model="fixed" label="操作" true-value="right" />
              </template>
              <template #default="{ row }">
                <el-button link type="primary" @click="hendleEditToiletRoom(row)">厕位</el-button>
                <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
                <el-button link type="primary" @click="handleSelect(row)">{{row.posX==null?"打标":"地图"}}</el-button>
                <el-button link type="primary" @click="handleDelete(row)">删除</el-button>
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
    <toilet-room ref="roomEditRef" :data="queryForm" @fetch-data="fetchData" />
    <toilet-edit ref="editRef" :data="queryForm" @fetch-data="fetchData" />
    <el-dialog v-model="mapDialogVisible" append-to-body draggable :title="currentItem.name" width="80%" @close="closeMap">
      <div v-loading="mapLoading" class="map-panel-container">
        <div id="map" class="mapcontainer"></div>
      </div>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { Plus, Search } from '@element-plus/icons-vue'
import { getToiletList, doToiletDelete, setMapPosition } from '/@/api/space.ts'
import { ArrowRight } from '@element-plus/icons-vue'
import { getTreeByFloor } from '/@/api/spaceManagement'
import { ElMessage, ElMessageBox, ElTree } from 'element-plus'
import icon from '/@/assets/marker.png'
import { getServiceUrl } from '~/src/utils'
const $baseConfirm = inject<any>('$baseConfirm')
const $baseMessage = inject<any>('$baseMessage')
defineOptions({
  name: 'ToiletTable',
})
const currentMarker = ref<any>()
const currentNode = ref<any>()
const crumblist = ref<any>([])
const tableRef = ref<any>(null)
const editRef = ref<any>(null)
const map = ref<any>(null)
const roomEditRef = ref<any>(null)
const border = ref<boolean>(true)
const stripe = ref<boolean>(false)
const mapDialogVisible = ref<boolean>(false)
const lineHeight = ref<any>('default')
const list = ref<any>([])
const listLoading = ref<boolean>(false)
const treeLoading = ref<boolean>(false)
const mapLoading = ref<boolean>(false)
const total = ref<any>(0)
const currentItem = ref<any>({})
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
  currentNode.value = treenode
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
  const { data } = await getToiletList(queryForm)
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
const closeMap = () => {
  currentItem.value = {}
  mapDialogVisible.value = false
  if(map.value!=null){map.value.dispose()}
  map.value = null
}
function handleDefaultClick(e) {
  console.log(e)
  if (e.target.isMesh) {
    e.target.active()
  }
  ElMessageBox.confirm('是否确认为当前区域添加坐标?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      // new AirocovMap.covers.ImageMarker({
      //   name: 'device',
      //   imgSrc: icon,
      //   size: 14,
      //   position: {
      //     x: Number(e.target.info.center[0]),
      //     y: 1,
      //     z: Number(e.target.info.center[1]),
      //   },
      //   canvasHeight: map.value.dom.offsetHeight,
      //   fontSize: 70,
      //   info: e.target.info.name,
      //   callback: function (marker) {
      //     marker.material.depthTest = false
      //     map.value.addToMap({
      //       object: marker,
      //       floorName: queryForm.floorCode,
      //       layerName: 'device',
      //       isClick: true, // 标记为可点击
      //     })
      //   },
      // })
      if(currentMarker.value){
        currentMarker.value.remove()
      }
      addMark(e.position.x,e.position.z)
      const res = await setMapPosition({
        id: currentItem.value.id,
        type: "toilet",
        posX: e.position.x,
        posY: 1,
        posZ: e.position.z,
      })
      if (res.code === '200') {
        ElMessage.success('添加成功')
        closeMap()
        handleNodeClick(currentNode.value)
      } else {
        ElMessage.error(res.msg)
      }
    })
    .catch(() => {})
}
const handleSelect = (selection: any) => {
  currentItem.value = selection
  mapDialogVisible.value = true
  mapLoading.value = true
  setTimeout(() => {
    map.value = new AirocovMap.Map({
      container: document.getElementById('map'),
      mapUrl: `${getServiceUrl()}/${selection.floorCode}.acmap`,
      themeUrl: '/os/static/theme/theme.json',
      floorSwitch: { show: false },
      opacity: 0.6,
      mergeModels: ['wall', 'plane', 'door'],
      clickModels: ['floor', 'plane', 'room', 'area', 'wall', 'logo'],
      key: 'KMED1W0N50YIWIYJCUNLYPMJ49JDLASE',
      defaultFloorIndex: 0,
      showAllFloor: false,
      maxPolarAngle: 90,
      pointScale: 1.4,
      zoom: 0.8,
      bgColor: 'transparent',
      showViewMode: '2D',
      clickIntoBuilding: false,
      font: {
        fontscale: 200,
        iconScale: 5,
        indent: 100,
      },
      pointscale: 5,
      onReady: function () {
        // map.render.camera.control.autoRotate = true;
        if(selection.posX!=null){
          addMark(selection.posX,selection.posZ)
        }
      },
    })
    new AirocovMap.controls.ModeSwitch(map.value, {
      left: '10px', //控件与容器左侧距离，或添加right属性，设置与容器右侧距离
      bottom: '40px', //控件与容器底部距离，或添加top属性，设置与容器顶部距离
      //点击按钮的回调方法,返回type表示按钮类型,value表示对应的功能值
      clickCallBack: function (type) {
        //console.log(type);
        //console.log(map.render.camera.object)
      },
    })
    new AirocovMap.controls.Compass(map.value, {
      width: '48px', //指北针大小
      left: '10px', //控件与容器左侧距离，或添加right属性，设置与容器右侧距离
      bottom: '130px', //控件与容器顶部距离，或添加bottom属性，设置与容器底部距离
    })
    map.value.event.on('click', handleDefaultClick)
    mapLoading.value = false
  }, 1000)
}
const setSelectRows = (value: any) => {
  selectRows.value = value
}
const handleEdit = (row: any) => {
  editRef.value.showEdit(row)
}
const hendleEditToiletRoom = (row: any) => {
  roomEditRef.value.showEdit(row)
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
      const { msg }: any = await doToiletDelete({ ids: row.id })
      $baseMessage(msg, 'success', 'hey')
      await fetchData()
    })
  }
}
// onBeforeMount(() => {
//   const returnTreeData = fetchSpaceData()
//   returnTreeData.then(() => {
//     // const firstAreaId = getFirstArea(spacedata.value)
//     // treeRef.value.setCurrentKey(firstAreaId)
//     // // console.info(treeRef.value.getNode('33333').data)
//     // handleNodeClick(treeRef.value.getNode(firstAreaId).data)
//   })
// })
function addMark(x,z){
  new AirocovMap.covers.ImageMarker({
        name: 'device',
        imgSrc: icon,
        size: 32,
        position: {
          x: Number(x),
          y: 1,
          z: Number(z),
        },
        canvasHeight: map.value.dom.offsetHeight,
        fontSize: 70,
        // info: currentItem.value.floorCode+"_"+currentItem.value.name,
        callback: function (marker:any) {
          currentMarker.value = marker
          marker.material.depthTest = false
          map.value.addToMap({
            object: marker,
            floorName:currentItem.value.floorCode,
            layerName: 'device',
            isClick: true, // 标记为可点击
          })
        },
      })
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
onUnmounted(() => {
  if(map.value!=null)map.value.dispose()
  map.value = null
})
</script>

<style lang="scss" scoped>
.toilet-container {
  width: 100%;
  :deep() {
    .el-card {
      margin-bottom: 0;
    }
  }
}
.map-panel-container {
  :deep() {
    .mapcontainer {
      padding-top: 20px;
      height: calc(var(--el-container-height) - var(--el-padding) - 52px) !important;
    }
    .airocovFloorSwitch {
      top: 80px !important;
      left: 20px !important;
    }
  }
}
</style>
import request from '/@/utils/request'

// Mock data helper
const mockResponse = (data: any) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        code: 200,
        msg: 'success',
        data
      })
    }, 300)
  })
}

// Generate mock data for toilets
const generateToiletData = () => {
  const floors = []
  for (let i = 1; i <= 10; i++) { // Mock 10 floors for example
    const floorNum = 40 + i
    floors.push({
      floor: `${floorNum}F`,
      id: `F${floorNum}`,
      toilets: [
        {
          id: `F${floorNum}-M`,
          name: '男厕',
          type: 'male',
          cubicles: [
            { id: 1, status: Math.random() > 0.5 ? 'occupied' : 'vacant' },
            { id: 2, status: Math.random() > 0.5 ? 'occupied' : 'vacant' },
            { id: 3, status: Math.random() > 0.5 ? 'occupied' : 'vacant' },
            { id: 4, status: Math.random() > 0.5 ? 'occupied' : 'vacant' },
            { id: 5, status: Math.random() > 0.5 ? 'occupied' : 'vacant' },
          ],
          env: {
            temperature: { value: 26.2, unit: '℃', status: '舒适' },
            humidity: { value: 63, unit: '%', status: '舒适' },
            h2s: { value: 0.001, unit: 'mg/m³', status: '正常' },
            pm25: { value: 18, unit: 'μg/m³', status: '优' },
            nh3: { value: 0.000, unit: 'mg/m³', status: '安全' }
          }
        },
        {
          id: `F${floorNum}-F`,
          name: '女厕',
          type: 'female',
          cubicles: [
            { id: 1, status: Math.random() > 0.5 ? 'occupied' : 'vacant' },
            { id: 2, status: Math.random() > 0.5 ? 'occupied' : 'vacant' },
            { id: 3, status: Math.random() > 0.5 ? 'occupied' : 'vacant' },
            { id: 4, status: Math.random() > 0.5 ? 'occupied' : 'vacant' },
            { id: 5, status: Math.random() > 0.5 ? 'occupied' : 'vacant' },
          ],
          env: {
            temperature: { value: 25.8, unit: '℃', status: '舒适' },
            humidity: { value: 60, unit: '%', status: '舒适' },
            h2s: { value: 0.002, unit: 'mg/m³', status: '正常' },
            pm25: { value: 20, unit: 'μg/m³', status: '优' },
            nh3: { value: 0.001, unit: 'mg/m³', status: '安全' }
          }
        }
      ]
    })
  }
  return floors
}

export function getToiletStatus() {
  return mockResponse(generateToiletData())
}

```

## 后30页
```
import { ApiProperty } from '@nestjs/swagger';
import { IsString, IsNotEmpty } from 'class-validator';

export class ToiletDeleteDto {
  @ApiProperty({
    description: '要删除的卫生间ID列表，以逗号分隔',
    example: '1,2,3',
  })
  @IsNotEmpty({ message: '请选择要删除的卫生间' })
  @IsString()
  ids: string;
}
import { ApiProperty } from '@nestjs/swagger';
import { IsOptional, IsString, IsNumber } from 'class-validator';

export class ToiletEditDto {
  @ApiProperty({ description: 'ID', required: false })
  @IsOptional()
  @IsNumber()
  id?: number;

  @ApiProperty({ description: '类型', required: true })
  @IsString()
  type: string;

  @ApiProperty({ description: '编码', required: true })
  @IsString()
  code: string;

  @ApiProperty({ description: '名称', required: true })
  @IsString()
  name: string;

  @ApiProperty({ description: '空间编码', required: false })
  @IsOptional()
  @IsString()
  spaceCode?: string;

  @ApiProperty({ description: '区域编码', required: true })
  @IsString()
  floorAreaCode: string;

  @ApiProperty({ description: '楼层编码', required: true })
  @IsString()
  floorCode: string;
}
import { ApiProperty } from '@nestjs/swagger';
import { IsOptional, IsString } from 'class-validator';

export class ToiletListDto {
  @ApiProperty({ description: '页码', default: 1 })
  @IsOptional()
  pageNo?: number;

  @ApiProperty({ description: '每页数量', default: 20 })
  @IsOptional()
  pageSize?: number;

  @ApiProperty({ description: '空间编码', required: false })
  @IsOptional()
  @IsString()
  spaceCode?: string;

  @ApiProperty({ description: '区域编码', required: false })
  @IsOptional()
  @IsString()
  floorAreaCode?: string;

  @ApiProperty({ description: '楼层编码', required: false })
  @IsOptional()
  @IsString()
  floorCode?: string;

  @ApiProperty({ description: '名称搜索', required: false })
  @IsOptional()
  @IsString()
  title?: string;
}

export interface ToiletRoomItem {
  id: number;
  code: string;
  name: string;
  sortOrder: number;
  toiletId: number;
}

export interface ToiletListItem {
  id: number;
  type: string;
  code: string;
  name: string;
  sortOrder: number;
  spaceCode: string;
  floorAreaCode: string;
  floorCode: string;
  rooms: ToiletRoomItem[];
}

export interface ToiletListResponse {
  total: number;
  list: ToiletListItem[];
}
import { ApiProperty } from '@nestjs/swagger';
import { IsOptional, IsNumber } from 'class-validator';

export class ToiletRoomListDto {
  @ApiProperty({ description: '页码', default: 1 })
  @IsOptional()
  pageNo?: number;

  @ApiProperty({ description: '每页数量', default: 20 })
  @IsOptional()
  pageSize?: number;

  @ApiProperty({ description: '卫生间ID', required: true })
  @IsNumber()
  toiletId: number;
}

export interface ToiletRoomListItem {
  id: number;
  code: string;
  name: string;
  sortOrder: number;
  toiletId: number;
  deleteFlag: number;
  createtime: string;
}

export interface ToiletRoomListResponse {
  total: number;
  list: ToiletRoomListItem[];
}
import {
  Controller,
  Post,
  Body,
  UseGuards,
  Request,
  Get,
  Query,
  BadRequestException,
  UseInterceptors,
  UploadedFile,
  Param,
  Res,
} from '@nestjs/common';
import { Response } from 'express';
import { FileInterceptor } from '@nestjs/platform-express';
import { ApiOperation, ApiTags, ApiResponse, ApiBody, ApiConsumes } from '@nestjs/swagger';
import { SpaceService } from './space.service';
import { UserService } from '../user/user.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { WorkstationEditDto } from './dto/workstation-edit.dto';
import { WorkstationDeleteDto } from './dto/workstation-delete.dto';
import { DeleteFloorDto,DeleteFloorResponseDto } from './dto/floor-delete.dto';
import { FloorListDto, FloorListResponseDto } from './dto/floor-list.dto';
import { AreaEditDto, AreaEditResponseDto } from './dto/area-edit.dto';
// import { RoomEditDto } from './dto/room-edit.dto';
import { MroomListDto, MroomListResponseDto } from './dto/mroom-list.dto';
// import { PublicAreaDeleteDto } from './dto/public-area-delete.dto';
// import {
//   PublicAreaListDto,
//   PublicAreaListResponseDto,
// } from './dto/public-area-list.dto';
import { SpaceEditDto } from './dto/space-edit.dto';
import { SpaceDeleteDto } from './dto/space-delete.dto';
import { SpaceListDto } from './dto/space-list.dto';
import {
  SelectSpaceRequestDto,
  SelectSpaceResponseDto,
} from './dto/select-space.dto';
import { GetSpaceFloorListDto } from './dto/get-space-floor-list.dto';
import { SpaceFloorResponseDto } from './dto/space-floor-response.dto';
import { SaveFloorRequestDto,SaveFloorResponseDto } from './dto/save-floor.dto';
import { ObjectResponseDto } from './dto/object.dto';
import { FloorAreaDeteleDto, FloorAreaEditDto } from './dto/floorArea.dto';
import { FloorTreeResponseData,ApiObjectResponse, GetRoomListParams, RoomListResponseData, RoomEditResponseData,RoomEditDto, DeteleDto, GetAreaListParams, AreaListResponseData, AreaFloorEditDto,  PublicAreaListResponseData, GetPublicAreaListParams, EditResponseData ,PublicAreaEditDto, MeetingroomListResponseData, GetMeetingRoomListParams, ToiletListResponseData, GetToiletListParams, MeetingroomEditDto, ToiletEditDto, GetToiletRoomListParams, ToiletRoomListResponseData,ToiletRoomEditDto} from './dto/space.dto';
import { GetSpaceTreeRequestDto, SpaceTreeResponseDto } from './dto/space-tree.dto';
import { GetNewTreeRequestDto, NewTreeResponseDto } from './dto/get-new-tree.dto';
import { GetSpaceAreasDto, SpaceAreasResponseDto } from './dto/space-areas.dto';

import { Public } from '../auth/decorators/public.decorator';

interface MulterFile {
  fieldname: string;
  originalname: string;
  encoding: string;
  mimetype: string;
  size: number;
  destination: string;
  filename: string;
  path: string;
  buffer: Buffer;
}

interface RequestWithUser extends Request {
  user: {
    userId: number;
    realName: string;
    spaceCode?: string;
  };
}

@ApiTags('空间管理')
@UseGuards(JwtAuthGuard)
@Controller('space')
export class SpaceController {
  constructor(
    private readonly spaceService: SpaceService,
    private readonly userService: UserService
  ) {}

  @Post('createDemo')
  @ApiOperation({ summary: '创建演示空间' })
  async createDemo() {
    const demoData = {
      "space": {
        "code": "JQDS",
        "name": "极企大厦"
      },
      "areas": [
        {
          "code": "QQ",
          "name": "全区",
          "spaceCode": "JQDS"
        }
      ],
      "floors": [
        {
          "code": "Q01F",
          "name": "1F",
          "areaCode": "QQ"
        },
        {
          "code": "Q02F",
          "name": "2F",
          "areaCode": "QQ"
        },
        {
          "code": "Q03F",
          "name": "3F",
          "areaCode": "QQ"
        },
        {
          "code": "Q04F",
          "name": "4F",
          "areaCode": "QQ"
        },
        {
          "code": "Q05F",
          "name": "5F",
          "areaCode": "QQ"
        },
        {
          "code": "Q06F",
          "name": "6F",
          "areaCode": "QQ"
        },
        {
          "code": "Q07F",
          "name": "7F",
          "areaCode": "QQ"
        },
        {
          "code": "Q08F",
          "name": "8F",
          "areaCode": "QQ"
        },
        {
          "code": "Q09F",
          "name": "9F",
          "areaCode": "QQ"
        },
        {
          "code": "Q10F",
          "name": "10F",
          "areaCode": "QQ"
        },
        {
          "code": "Q11F",
          "name": "11F",
          "areaCode": "QQ"
        },
        {
          "code": "Q12F",
          "name": "12F",
          "areaCode": "QQ"
        },
        {
          "code": "Q13F",
          "name": "13F",
          "areaCode": "QQ"
        },
        {
          "code": "Q14F",
          "name": "14F",
          "areaCode": "QQ"
        },
        {
          "code": "Q15F",
          "name": "15F",
          "areaCode": "QQ"
        },
        {
          "code": "Q16F",
          "name": "16F",
          "areaCode": "QQ"
        },
        {
          "code": "Q17F",
          "name": "17F",
          "areaCode": "QQ"
        },
        {
          "code": "Q18F",
          "name": "18F",
          "areaCode": "QQ"
        },
        {
          "code": "Q19F",
          "name": "19F",
          "areaCode": "QQ"
        },
        {
          "code": "Q20F",
          "name": "20F",
          "areaCode": "QQ"
        }
      ],
      "floorAreas": [
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q01F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q01F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q02F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q02F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q03F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q03F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q04F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q04F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q05F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q05F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q06F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q06F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q07F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q07F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q08F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q08F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q09F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q09F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q10F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q10F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q11F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q11F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q12F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q12F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q13F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q13F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q14F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q14F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q15F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q15F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q16F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q16F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q17F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q17F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q18F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q18F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q19F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q19F"
        },
        {
          "code": "CSJ",
          "name": "茶水间",
          "floorCode": "Q20F"
        },
        {
          "code": "ZL",
          "name": "走廊",
          "floorCode": "Q20F"
        }
      ],
      "officeAreas": [
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q01F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q01F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q01F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q01F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q02F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q02F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q02F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q02F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q03F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q03F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q03F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q03F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q04F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q04F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q04F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q04F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q05F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q05F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q05F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q05F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q06F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q06F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q06F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q06F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q07F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q07F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q07F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q07F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q08F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q08F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q08F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q08F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q09F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q09F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q09F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q09F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q10F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q10F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q10F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q10F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q11F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q11F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q11F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q11F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q12F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q12F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q12F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q12F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q13F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q13F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q13F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q13F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q14F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q14F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q14F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q14F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q15F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q15F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q15F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q15F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q16F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q16F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q16F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q16F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q17F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q17F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q17F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q17F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q18F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q18F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q18F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q18F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q19F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q19F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q19F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q19F"
        },
        {
          "code": "AQ",
          "name": "A区",
          "floorCode": "Q20F"
        },
        {
          "code": "BQ",
          "name": "B区",
          "floorCode": "Q20F"
        },
        {
          "code": "CQ",
          "name": "C区",
          "floorCode": "Q20F"
        },
        {
          "code": "DQ",
          "name": "D区",
          "floorCode": "Q20F"
        }
      ],
      "meetings": [
        {
          "code": "M0101",
          "name": "0101",
          "floorCode": "Q01F"
        },
        {
          "code": "M0102",
          "name": "0102",
          "floorCode": "Q01F"
        },
        {
          "code": "M0201",
          "name": "0201",
          "floorCode": "Q02F"
        },
        {
          "code": "M0202",
          "name": "0202",
          "floorCode": "Q02F"
        },
        {
          "code": "M0301",
          "name": "0301",
          "floorCode": "Q03F"
        },
        {
          "code": "M0302",
          "name": "0302",
          "floorCode": "Q03F"
        },
        {
          "code": "M0401",
          "name": "0401",
          "floorCode": "Q04F"
        },
        {
          "code": "M0402",
          "name": "0402",
          "floorCode": "Q04F"
        },
        {
          "code": "M0501",
          "name": "0501",
          "floorCode": "Q05F"
        },
        {
          "code": "M0502",
          "name": "0502",
          "floorCode": "Q05F"
        },
        {
          "code": "M0601",
          "name": "0601",
          "floorCode": "Q06F"
        },
        {
          "code": "M0602",
          "name": "0602",
          "floorCode": "Q06F"
        },
        {
          "code": "M0701",
          "name": "0701",
          "floorCode": "Q07F"
        },
        {
          "code": "M0702",
          "name": "0702",
          "floorCode": "Q07F"
        },
        {
          "code": "M0801",
          "name": "0801",
          "floorCode": "Q08F"
        },
        {
          "code": "M0802",
          "name": "0802",
          "floorCode": "Q08F"
        },
        {
          "code": "M0901",
          "name": "0901",
          "floorCode": "Q09F"
        },
        {
          "code": "M0902",
          "name": "0902",
          "floorCode": "Q09F"
        },
        {
          "code": "M1001",
          "name": "1001",
          "floorCode": "Q10F"
        },
        {
          "code": "M1002",
          "name": "1002",
          "floorCode": "Q10F"
        },
        {
          "code": "M1101",
          "name": "1101",
          "floorCode": "Q11F"
        },
        {
          "code": "M1102",
          "name": "1102",
          "floorCode": "Q11F"
        },
        {
          "code": "M1201",
          "name": "1201",
          "floorCode": "Q12F"
        },
        {
          "code": "M1202",
          "name": "1202",
          "floorCode": "Q12F"
        },
        {
          "code": "M1301",
          "name": "1301",
          "floorCode": "Q13F"
        },
        {
          "code": "M1302",
          "name": "1302",
          "floorCode": "Q13F"
        },
        {
          "code": "M1401",
          "name": "1401",
          "floorCode": "Q14F"
        },
        {
          "code": "M1402",
          "name": "1402",
          "floorCode": "Q14F"
        },
        {
          "code": "M1501",
          "name": "1501",
          "floorCode": "Q15F"
        },
        {
          "code": "M1502",
          "name": "1502",
          "floorCode": "Q15F"
        },
        {
          "code": "M1601",
          "name": "1601",
          "floorCode": "Q16F"
        },
        {
          "code": "M1602",
          "name": "1602",
          "floorCode": "Q16F"
        },
        {
          "code": "M1701",
          "name": "1701",
          "floorCode": "Q17F"
        },
        {
          "code": "M1702",
          "name": "1702",
          "floorCode": "Q17F"
        },
        {
          "code": "M1801",
          "name": "1801",
          "floorCode": "Q18F"
        },
        {
          "code": "M1802",
          "name": "1802",
          "floorCode": "Q18F"
        },
        {
          "code": "M1901",
          "name": "1901",
          "floorCode": "Q19F"
        },
        {
          "code": "M1902",
          "name": "1902",
          "floorCode": "Q19F"
        },
        {
          "code": "M2001",
          "name": "2001",
          "floorCode": "Q20F"
        },
        {
          "code": "M2002",
          "name": "2002",
          "floorCode": "Q20F"
        }
      ],
      "rooms": [
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q01F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q01F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q01F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q01F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q02F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q02F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q02F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q02F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q03F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q03F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q03F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q03F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q04F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q04F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q04F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q04F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q05F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q05F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q05F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q05F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q06F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q06F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q06F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q06F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q07F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q07F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q07F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q07F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q08F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q08F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q08F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q08F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q09F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q09F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q09F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q09F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q10F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q10F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q10F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q10F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q11F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q11F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q11F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q11F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q12F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q12F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q12F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q12F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q13F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q13F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q13F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q13F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q14F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q14F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q14F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q14F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q15F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q15F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q15F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q15F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q16F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q16F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q16F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q16F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q17F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q17F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q17F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q17F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q18F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q18F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q18F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q18F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q19F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q19F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q19F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q19F"
        },
        {
          "code": "JL1",
          "name": "经理办公室1",
          "floorCode": "Q20F"
        },
        {
          "code": "JL2",
          "name": "经理办公室2",
          "floorCode": "Q20F"
        },
        {
          "code": "KF",
          "name": "库房",
          "floorCode": "Q20F"
        },
        {
          "code": "JF",
          "name": "机房",
          "floorCode": "Q20F"
        }
      ],
      "toilets": [
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q01F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q01F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q02F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q02F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q03F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q03F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q04F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q04F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q05F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q05F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q06F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q06F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q07F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q07F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q08F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q08F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q09F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q09F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q10F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q10F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q11F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q11F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q12F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q12F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q13F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q13F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q14F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q14F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q15F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q15F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q16F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q16F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q17F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q17F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q18F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q18F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q19F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q19F"
        },
        {
          "code": "TMAN",
          "name": "男卫生间",
          "floorCode": "Q20F"
        },
        {
          "code": "TWOMEN",
          "name": "女卫生间",
          "floorCode": "Q20F"
        }
      ],
      "devices": []
    };

    const exists = await this.spaceService.isSpaceCodeExists(demoData.space.code);
    
    let result: any = { space: 0, areas: 0, floors: 0, floorAreas: 0, meetings: 0, rooms: 0, toilets: 0, errors: [] };

    if (!exists) {
      result = await this.spaceService.ingestSpaceInfoTx(demoData);
    }

    // Create demo organization and users
    await this.userService.createDemoData();

    if (result.errors && result.errors.length > 0) {
      return { code: '400', msg: 'fail', data: { result } };
    }

    return { code: '200', msg: 'success', data: { result } };
  }

  @Post('edit')
  @ApiOperation({ summary: '新建/编辑空间' })
  @ApiResponse({
    status: 200,
    description: '成功',
    schema: {
      type: 'object',
      properties: {
        code: { type: 'string', example: '200' },
        msg: { type: 'string', example: 'success' },
      },
    },
  })
  async doSpaceEdit(
    @Request() req: RequestWithUser,
    @Body() dto: SpaceEditDto,
  ): Promise<{ code: string; msg: string }> {
    await this.spaceService.editSpace(
      dto,
      req.user.userId.toString(),
      req.user.realName,
    );
    return {
      code: '200',
      msg: 'success',
    };
  }

  @Post('delete')
  doSpaceDelete(@Body() _dto: SpaceDeleteDto) {
    // TODO: 使用dto实现空间删除逻辑
    throw new Error('doSpaceDelete方法未实现');
    return { code: 200, msg: 'success' };
  }

  @Get('getList')
  async getSpaceList(@Query() dto: SpaceListDto) {
    const { list, total } = await this.spaceService.getSpaceList(dto);
    return {
      code: '200',
      msg: 'success',
      data: {
        total,
        list,
      },
    };
  }

  @Post('selectSpace')
  @ApiOperation({ summary: '选择/切换空间' })
  @ApiResponse({
    status: 200,
    description: '成功',
    type: SelectSpaceResponseDto,
  })
  @ApiResponse({ status: 400, description: '无效空间' })
  @ApiResponse({ status: 401, description: '未登录' })
  async selectSpace(
    @Request() req: RequestWithUser,
    @Body() dto: SelectSpaceRequestDto,
  ): Promise<SelectSpaceResponseDto> {
    return this.spaceService.selectSpace(req.user.userId.toString(), dto);
  }

  // // Public Area endpoints
  // @Post('public-area/edit')
  // doPublicAreaEdit(@Body() _dto: PublicAreaEditDto) {
  //   // TODO: 实现公共区域编辑逻辑
  //   throw new Error('doPublicAreaEdit方法未实现');
  // }

  // @Post('public-area/delete')
  // doPublicAreaDelete(@Body() _dto: PublicAreaDeleteDto) {
  //   // TODO: 实现公共区域删除逻辑
  //   throw new Error('doPublicAreaDelete方法未实现');
  // }

  // @Get('public-area/list')
  // getPublicAreaList(
  //   @Query() _dto: PublicAreaListDto,
  // ): Promise<PublicAreaListResponseDto[]> {
  //   // TODO: 实现获取公共区域列表逻辑
  //   return Promise.resolve([]);
  // }

  // Meeting Room endpoints
  // @Post('mroom/edit')
  // doMroomEdit(@Body() _dto: MroomEditDto) {
  //   // TODO: 实现会议室编辑逻辑
  //   throw new Error('doMroomEdit方法未实现');
  // }

  // @Post('mroom/delete')
  // doMroomDelete(@Body() _dto: MroomDeleteDto) {
  //   // TODO: 实现会议室删除逻辑
  //   throw new Error('doMroomDelete方法未实现');
  // }

  @Get('mroom/list')
  getMroomList(@Query() _dto: MroomListDto): Promise<MroomListResponseDto[]> {
    // TODO: 实现获取会议室列表逻辑
    return Promise.resolve([]);
  }

  // // Room endpoints
  // @Post('room/edit')
  // doRoomEdit(@Body() _dto: RoomEditDto) {
  //   // TODO: 实现房间编辑逻辑
  //   throw new Error('doRoomEdit方法未实现');
  // }

  // @Post('room/delete')
  // doRoomDelete(@Body() _dto: RoomDeleteDto) {
  //   // TODO: 实现房间删除逻辑
  //   throw new Error('doRoomDelete方法未实现');
  // }

  // @Get('room/list')
  // getRoomList(@Query() _dto: RoomListDto): Promise<RoomListResponseDto[]> {
  //   // TODO: 实现获取房间列表逻辑
  //   return Promise.resolve([]);
  // }

  // Area endpoints
  // @Post('area/edit')
  // doAreaEdit(@Body() _dto: AreaEditDto) {
  //   // TODO: 实现区域编辑逻辑
  //   throw new Error('doAreaEdit方法未实现');
  // }

  // @Post('area/delete')
  // doAreaDelete(@Body() _dto: AreaDeleteDto) {
  //   // TODO: 实现区域删除逻辑
  //   throw new Error('doAreaDelete方法未实现');
  // }

  // @Get('area/list')
  // getAreaList(@Query() _dto: AreaListDto): Promise<AreaListResponseDto[]> {
  //   // TODO: 实现获取区域列表逻辑
  //   return Promise.resolve([]);
  // }

  // Floor endpoints
  @Post('saveFloor')
  @ApiOperation({ summary: '保存楼层信息', description: '创建或更新楼层信息' })
  @ApiBody({ type: SaveFloorRequestDto })
  @ApiResponse({ status: 200, type: SaveFloorResponseDto })
  async saveFloor(@Body() dto: SaveFloorRequestDto): Promise<SaveFloorResponseDto> {
    return this.spaceService.handleSaveFloor(dto);
  }

  @Post('uploadFloorMap')
  @ApiOperation({ summary: '上传楼层地图', description: '上传楼层平面图' })
  @ApiConsumes('multipart/form-data')
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        floorID: { type: 'string' },
        spaceCode: { type: 'string' },
        file: {
          type: 'string',
          format: 'binary',
        },
      },
    },
  })
  @UseInterceptors(FileInterceptor('file'))
  async uploadFloorMap(
    @UploadedFile() file: MulterFile,
    @Body() body: { floorID: string; spaceCode?: string },
    @Request() req: RequestWithUser,
  ) {
    if (!file) {
        throw new BadRequestException('未上传文件');
    }
    return this.spaceService.uploadFloorMap(
      body.floorID,
      file,
      body.spaceCode,
      req.user?.spaceCode
    );
  }

  @Post('deleteFloor')
  @ApiOperation({ summary: '删除楼层', description: '将指定楼层标记为已删除' })
  @ApiBody({ type: DeleteFloorDto })
  @ApiResponse({ status: 200, type: DeleteFloorResponseDto })
  @ApiResponse({ status: 400, description: '无效楼层' })
  async deleteFloor(
    @Request() req: RequestWithUser,
    @Body() dto: DeleteFloorDto
  ): Promise<DeleteFloorResponseDto> {
    // 如果没有提供spaceCode，使用用户当前的spaceCode
    if (!dto.spaceCode && req.user?.spaceCode) {
      dto.spaceCode = req.user.spaceCode;
    }
    return this.spaceService.deleteFloor(dto);
  }

  @Public()
  @Get('getFloorMap/:spaceCode/:filename')
  @ApiOperation({ summary: '获取楼层地图文件' })
  async getFloorMap(
    @Param('spaceCode') spaceCode: string,
    @Param('filename') filename: string,
    @Res() res: Response
  ) {
    const file = await this.spaceService.getFloorMap(filename, spaceCode);
    res.setHeader('Content-Type', 'application/octet-stream');
    res.send(file);
  }


  @Get('floor/list')
  getFloorList(@Query() _dto: FloorListDto): Promise<FloorListResponseDto[]> {
    // TODO: 实现获取楼层列表逻辑
    return Promise.resolve([]);
  }

  // // Toilet endpoints
  // @Post('toilet-room/edit')
  // doToiletRoomEdit(@Body() _dto: ToiletRoomEditDto) {
  //   // TODO: 实现卫生间编辑逻辑
  //   throw new Error('doToiletRoomEdit方法未实现');
  // }

  // @Post('toilet/delete')
  // doToiletDelete(@Body() _dto: ToiletDeleteDto) {
  //   // TODO: 实现卫生间删除逻辑
  //   throw new Error('doToiletDelete方法未实现');
  // }

  // @Post('toilet-room/delete')
  // doToiletRoomDelete(@Body() _dto: ToiletRoomDeleteDto) {
  //   // TODO: 实现卫生间房间删除逻辑
  //   throw new Error('doToiletRoomDelete方法未实现');
  // }

  // Workstation endpoints
  @Post('workstation/edit')
  doWorkstationEdit(
    @Request() _req: RequestWithUser,
    @Body() _dto: WorkstationEditDto,
  ) {
    // TODO: 实现工位编辑逻辑
    throw new Error('doWorkstationEdit方法未实现');
  }

  @Post('workstation/delete')
  doWorkstationDelete(@Body() _dto: WorkstationDeleteDto) {
    // TODO: 实现工位删除逻辑
    throw new Error('doWorkstationDelete方法未实现');
  }


  @Get('getSpaceFloorList')
  @ApiOperation({
    summary: '获取空间楼层列表',
    description: '根据空间编码获取楼层及区域信息'
  })
  @ApiResponse({
    status: 200,
    description: '成功获取空间楼层数据',
    type: SpaceFloorResponseDto
  })
  @ApiResponse({ 
    status: 400,
    description: '参数验证失败' 
  })
  async getSpaceFloorList(
    @Query() params: GetSpaceFloorListDto
  ): Promise<SpaceFloorResponseDto> {
    return this.spaceService.getSpaceFloorList(params)
  }
  
  @Post('addFloorArea')
  @ApiOperation({ summary: '添加楼层区域', description: '创建新的楼层区域' })
  @ApiResponse({ 
    status: 200, 
    description: '区域创建成功',
    type: AreaEditDto
  })
  @ApiResponse({ 
    status: 400, 
    description: '区域编码已存在' 
  })
  async createFloorArea(
    @Body() dto: AreaEditDto
  ): Promise<AreaEditResponseDto> {
    return this.spaceService.createFloorArea(dto);
  }


  @Post('modifyAreaName')
  @ApiOperation({ summary: '编辑楼层区域', description: '编辑楼层区域如：1栋，1单元，A区' })
  @ApiResponse({ 
    status: 200, 
    description: '区域创建成功',
    type: ObjectResponseDto
  })
  async modifyAreaName(
    @Body() dto: FloorAreaEditDto
  ): Promise<ObjectResponseDto> {
    return this.spaceService.modifyAreaName(dto);
  }


  @Post('doDeleteFloorArea')
  @ApiOperation({ summary: '删除楼层区域', description: '删除后该楼层分区下的楼层将自动移动到全部楼层中' })
  @ApiResponse({ 
    status: 200, 
    description: '区域删除成功',
    type: ObjectResponseDto
  })
  async doDeleteFloorArea(
    @Request() req: RequestWithUser,
    @Body() dto: FloorAreaDeteleDto
  ): Promise<ObjectResponseDto> {
    return this.spaceService.doDeleteFloorArea(
      dto,
      req.user.userId
    );
  }

 /**
   * GET /space/getTreeByFloor
   * Retrieves the hierarchical tree structure (Space -> Area -> Floor).
   * @param spaceCode Optional query parameter to specify the space.
   * @param req Optional request object (if user info is needed for default spaceCode)
   * @returns Promise<ApiResponse<FloorTreeResponseData>>
   */

 @Get('getTreeByFloor')
 // @UseGuards(AuthGuard) // Uncomment this line if authentication is required for this endpoint
 @ApiOperation({ summary: '获取空间楼层树结构', description: '根据spaceCode，获取空间楼层树结构' })
 @ApiResponse({ 
   status: 200, 
   description: '获取空间楼层树结构成功',
   type: ObjectResponseDto
 })
 async getTreeByFloor(
   @Request() req: RequestWithUser,
   @Query('spaceCode') requestedSpaceCode?: string, // Get spaceCode from query params (?spaceCode=...)
   // @Req() req?: any, // Uncomment if you need user info from the request (e.g., req.user)
 ): Promise<ApiObjectResponse<FloorTreeResponseData>> {
   try {
     // --- Optional: Logic to get default spaceCode from user if needed ---
     // let targetSpaceCode = requestedSpaceCode;
     // if (!targetSpaceCode && req?.user?.spaceCode) { // Example: Check request user
     //   targetSpaceCode = req.user.spaceCode;
     // }
     // --- End Optional Logic ---

     // Call the service method
     // Pass the determined space code (prioritizing the query parameter as per PHP logic)
     const result = await this.spaceService.getTreeByFloor(req.user,requestedSpaceCode);
     return result; // The service already formats the response { code, msg, data }

   } catch (error) {
     // Catch specific exceptions thrown by the service (like NotFoundException or BadRequestException)
     // NestJS's built-in exception filter will handle these and format the response.
     // If you need custom handling or logging here, you can add it.
     // For example, if the service throws NotFoundException, NestJS will automatically
     // send a 404 response. If it throws BadRequestException, it sends a 400.
     // The ExceptionFilter should ideally format it into your standard ApiResponse structure.
     throw error; // Re-throw the error to let the global exception filter handle it
   }
 }
 @Get('getRoomList')
 @ApiOperation({ summary: '获取独立房间列表', description: '根据空间编码、楼层区域、楼层编码等条件获取房间列表' })
 @ApiResponse({ 
   status: 200, 
   description: '成功获取房间列表',
   type: ObjectResponseDto
 })
 async getRoomList(
   @Query() params: GetRoomListParams
 ): Promise<ApiObjectResponse<RoomListResponseData>> {
   return this.spaceService.getRoomList(params);
 }

/**
   * POST /space/doRoomEdit
   * Creates a new room or updates an existing one.
   * @param roomDto The room data from the request body.
   * @param req The request object (used to potentially extract user info).
   * @returns Promise<ApiObjectResponse<RoomEditResponseData | null>>
   */
  @Post('doRoomEdit')
  @ApiOperation({ summary: '编辑独立房间信息', description: '编辑独立房间信息，传入ID为编辑，ID空为新建' })
  @ApiBody({ type: RoomEditDto })
  @ApiResponse({ 
    status: 200, 
    description: '成功编辑房间列表',
    type: ObjectResponseDto
  })
  async doRoomEdit(
    @Body() roomDto: RoomEditDto, // Validate and bind request body to RoomEditDto
    @Request() req: RequestWithUser,
  ): Promise<ApiObjectResponse<RoomEditResponseData | null>> {
    try {
      // Extract user info if needed (adjust based on your auth setup)
      const userId = req?.user?.userId; // Example: Assuming user ID is on req.user
      const userName = req?.user?.realName; // Example: Assuming username is on req.user
      // Call the service method with DTO and optional user info
      const result = await this.spaceService.doRoomEdit(roomDto, userId.toString(), userName);
      return result; // Service returns the standard response object
    } catch (error) {
      // console.log(error)
      // Catch specific exceptions if needed for controller-level logic,
      // otherwise let the global exception filter handle them.
      // Example:
      // if (error instanceof ConflictException) {
      //   // Specific logging or handling for conflicts
      // }
      throw error; // Re-throw for the global filter
    }
  }


  @Post('doRoomDelete')
  @ApiOperation({ summary: '删除独立房间', description: '删除独立房间' })
  @ApiResponse({ 
    status: 200, 
    description: '删除独立房间成功',
    type: ObjectResponseDto
  })
  async doRoomDelete(
    @Request() req: RequestWithUser,
    @Body() dto: DeteleDto
  ): Promise<ObjectResponseDto> {
    return this.spaceService.doRoomDelete(
      dto,
      req.user.userId
    );
  }
 /**
   * Get /space/getAreaList
   * Retrieves a paginated list of areas based on specified filters.
   * Accepts filters and pagination via the request body.
   * @param params The filter and pagination parameters from the request body.
   * @returns Promise<ApiObjectResponse<AreaListResponseData>>
   */
 @Get('getAreaList') // Use Get decorator
 @ApiOperation({ summary: '获取区域列表', description: '根据空间编码、区域名称、区域编码等条件获取区域列表' })
 @ApiResponse({ 
   status: 200, 
   description: '成功获取区域列表',
   type: ObjectResponseDto
 })
 async getAreaList(
  @Query() params: GetAreaListParams // Bind and validate request body to GetAreaListParams DTO
   // @Req() req?: any, // Uncomment if you need user info (e.g., for default spaceCode if not in body)
 ): Promise<ApiObjectResponse<AreaListResponseData>> {
   try {
     // --- Optional: Handle default spaceCode if needed ---
     // if (!params.spaceCode && req?.user?.spaceCode) {
     //   params.spaceCode = req.user.spaceCode;
     // }
     // --- End Optional Logic ---
    // Call the service method with the parameters from the body
    const result = await this.spaceService.getAreaList(params);
    return result; // Service returns the standard response object

   } catch (error) {
     // Let the global exception filter handle errors thrown by the service
     throw error;
   }
 }

  @Post('doAreaEdit')
  @ApiOperation({ summary: '编辑办公区域信息', description: '编辑办公区域信息，传入ID为编辑，ID空为新建' })
  @ApiBody({ type: AreaFloorEditDto })
  @ApiResponse({ 
    status: 200, 
    description: '成功编辑办公区域',
    type: ObjectResponseDto
  })
  async doAreaEdit(
    @Body() areaFloorEditDto: AreaFloorEditDto, // Validate and bind request body to AreaFloorEditDto
    @Request() req: RequestWithUser,
  ): Promise<ApiObjectResponse<EditResponseData | null>> {
    try {
      // Extract user info if needed (adjust based on your auth setup)
      const userId = req?.user?.userId; // Example: Assuming user ID is on req.user
      const userName = req?.user?.realName; // Example: Assuming username is on req.user
      // Call the service method with DTO and optional user info
      const result = await this.spaceService.doAreaEdit(areaFloorEditDto, userId.toString(), userName);
      return result; // Service returns the standard response object
    } catch (error) {
      // console.log(error)
      // Catch specific exceptions if needed for controller-level logic,
      // otherwise let the global exception filter handle them.
      // Example:
      // if (error instanceof ConflictException) {
      //   // Specific logging or handling for conflicts
      // }
      throw error; // Re-throw for the global filter
    }
  }

  @Post('doAreaDelete')
  @ApiOperation({ summary: '删除办公空间', description: '删除办公空间' })
  @ApiResponse({ 
    status: 200, 
    description: '删除办公空间成功',
    type: ObjectResponseDto
  })
  async doAreaDelete(
    @Request() req: RequestWithUser,
    @Body() dto: DeteleDto
  ): Promise<ObjectResponseDto> {
    return this.spaceService.doAreaDelete(
      dto,
      req.user.userId
    );
  }

 /**
   * Get /space/getAreaList
   * Retrieves a paginated list of areas based on specified filters.
   * Accepts filters and pagination via the request body.
   * @param params The filter and pagination parameters from the request body.
   * @returns Promise<ApiObjectResponse<AreaListResponseData>>
   */
 @Get('getPublicAreaList') // Use Get decorator
 @ApiOperation({ summary: '获取公共区域列表', description: '根据空间编码、区域名称、区域编码等条件获取公共区域列表' })
 @ApiResponse({ 
   status: 200, 
   description: '成功获取公共区域列表',
   type: ObjectResponseDto
 })
 async getPublicAreaList(
  @Query() params: GetPublicAreaListParams // Bind and validate request body to GetAreaListParams DTO
   // @Req() req?: any, // Uncomment if you need user info (e.g., for default spaceCode if not in body)
 ): Promise<ApiObjectResponse<PublicAreaListResponseData>> {
   try {
     // --- Optional: Handle default spaceCode if needed ---
     // if (!params.spaceCode && req?.user?.spaceCode) {
     //   params.spaceCode = req.user.spaceCode;
     // }
     // --- End Optional Logic ---
    // Call the service method with the parameters from the body
    const result = await this.spaceService.getPublicAreaList(params);
    return result; // Service returns the standard response object

   } catch (error) {
     // Let the global exception filter handle errors thrown by the service
     throw error;
   }
 }




 @Post('doPublicAreaEdit')
 @ApiOperation({ summary: '编辑办公区域信息', description: '编辑办公区域信息，传入ID为编辑，ID空为新建' })
 @ApiBody({ type: PublicAreaEditDto })
 @ApiResponse({ 
   status: 200, 
   description: '成功编辑办公区域',
   type: ObjectResponseDto
 })
 async doPublicAreaEdit(
   @Body() publicAreaEditDto: PublicAreaEditDto, // Validate and bind request body to AreaFloorEditDto
   @Request() req: RequestWithUser,
 ): Promise<ApiObjectResponse<EditResponseData | null>> {
   try {
     // Extract user info if needed (adjust based on your auth setup)
     const userId = req?.user?.userId; // Example: Assuming user ID is on req.user
     const userName = req?.user?.realName; // Example: Assuming username is on req.user
     // Call the service method with DTO and optional user info
     const result = await this.spaceService.doPublicAreaEdit(publicAreaEditDto, userId.toString(), userName);
     return result; // Service returns the standard response object
   } catch (error) {
     // console.log(error)
     // Catch specific exceptions if needed for controller-level logic,
     // otherwise let the global exception filter handle them.
     // Example:
     // if (error instanceof ConflictException) {
     //   // Specific logging or handling for conflicts
     // }
     throw error; // Re-throw for the global filter
   }
 }

 @Post('doPublicAreaDelete')
 @ApiOperation({ summary: '删除公共空间', description: '删除公共空间' })
 @ApiResponse({ 
   status: 200, 
   description: '删除公共空间成功',
   type: ObjectResponseDto
 })
 async doPublicAreaDelete(
   @Request() req: RequestWithUser,
   @Body() dto: DeteleDto
 ): Promise<ObjectResponseDto> {
   return this.spaceService.doPublicAreaDelete(
     dto,
     req.user.userId
   );
 }
 
 /**
   * Get /space/getMRoomList
   * Retrieves a paginated list of meetingrooms based on specified filters.
   * Accepts filters and pagination via the request body.
   * @param params The filter and pagination parameters from the request body.
   * @returns Promise<ApiObjectResponse<MeetingroomListResponseData>>
   */
 @Get('getMRoomList') // Use Get decorator
 @ApiOperation({ summary: '获取会议室列表', description: '根据空间编码、区域名称、区域编码等条件获取会议室列表' })
 @ApiResponse({ 
   status: 200, 
   description: '成功获取会议室列表',
   type: ObjectResponseDto
 })
 async getMRoomList(
  @Query() params: GetMeetingRoomListParams // Bind and validate request body to GetAreaListParams DTO
   // @Req() req?: any, // Uncomment if you need user info (e.g., for default spaceCode if not in body)
 ): Promise<ApiObjectResponse<MeetingroomListResponseData>> {
   try {
     // --- Optional: Handle default spaceCode if needed ---
     // if (!params.spaceCode && req?.user?.spaceCode) {
     //   params.spaceCode = req.user.spaceCode;
     // }
     // --- End Optional Logic ---
    // Call the service method with the parameters from the body
    const result = await this.spaceService.getMRoomList(params);
    return result; // Service returns the standard response object

   } catch (error) {
     // Let the global exception filter handle errors thrown by the service
     throw error;
   }
 }
 /**
   * Get /space/getToiletList
   * Retrieves a paginated list of meetingrooms based on specified filters.
   * Accepts filters and pagination via the request body.
   * @param params The filter and pagination parameters from the request body.
   * @returns Promise<ApiObjectResponse<MeetingroomListResponseData>>
   */
 @Get('getToiletList') // Use Get decorator
 @ApiOperation({ summary: '获取卫生间列表', description: '根据空间编码、区域名称、区域编码等条件获取会议室列表' })
 @ApiResponse({ 
   status: 200, 
   description: '成功获取卫生间列表',
   type: ObjectResponseDto
 })
 async getToiletList(
  @Query() params: GetToiletListParams // Bind and validate request body to GetAreaListParams DTO
   // @Req() req?: any, // Uncomment if you need user info (e.g., for default spaceCode if not in body)
 ): Promise<ApiObjectResponse<ToiletListResponseData>> {
   try {
     // --- Optional: Handle default spaceCode if needed ---
     // if (!params.spaceCode && req?.user?.spaceCode) {
     //   params.spaceCode = req.user.spaceCode;
     // }
     // --- End Optional Logic ---
    // Call the service method with the parameters from the body
    const result = await this.spaceService.getToiletList(params);
    return result; // Service returns the standard response object

   } catch (error) {
     // Let the global exception filter handle errors thrown by the service
     throw error;
   }
 }

 @Post('doMroomEdit')
 @ApiOperation({ summary: '编辑会议室信息', description: '编辑会议室信息，传入ID为编辑，ID空为新建' })
 @ApiBody({ type: MeetingroomEditDto })
 @ApiResponse({ 
   status: 200, 
   description: '成功编辑会议室信息',
   type: ObjectResponseDto
 })
 async doMroomEdit(
  @Body() meetingroomEditDto: MeetingroomEditDto, // Validate and bind request body to AreaFloorEditDto
  @Request() req: RequestWithUser,
): Promise<ApiObjectResponse<EditResponseData | null>> {
  try {
    // Extract user info if needed (adjust based on your auth setup)
    const userId = req?.user?.userId; // Example: Assuming user ID is on req.user
    const userName = req?.user?.realName; // Example: Assuming username is on req.user
    // Call the service method with DTO and optional user info
    const result = await this.spaceService.doMroomEdit(meetingroomEditDto, userId.toString(), userName);
    return result; // Service returns the standard response object
  } catch (error) {
    // console.log(error)
    // Catch specific exceptions if needed for controller-level logic,
    // otherwise let the global exception filter handle them.
    // Example:
    // if (error instanceof ConflictException) {
    //   // Specific logging or handling for conflicts
    // }
    throw error; // Re-throw for the global filter
  }
}

 @Post('doMroomDelete')
 @ApiOperation({ summary: '删除会议室', description: '删除会议室' })
 @ApiResponse({ 
   status: 200, 
   description: '删除会议室成功',
   type: ObjectResponseDto
 })
 async doMroomDelete(
   @Request() req: RequestWithUser,
   @Body() dto: DeteleDto
 ): Promise<ObjectResponseDto> {
   return this.spaceService.doMroomDelete(
     dto,
     req.user.userId
   );
 }
 

  @Post('doToiletEdit')
  @ApiOperation({ summary: '编辑卫生间信息', description: '编辑卫生间信息，传入ID为编辑，ID空为新建' })
  @ApiBody({ type: ToiletEditDto })
  @ApiResponse({ 
    status: 200, 
    description: '成功编辑卫生间信息',
    type: ObjectResponseDto
  })
  async doToiletEdit(
    @Body() toiletEditDto: ToiletEditDto, // Validate and bind request body to AreaFloorEditDto
    @Request() req: RequestWithUser,
  ): Promise<ApiObjectResponse<EditResponseData | null>> {
    try {
      // Extract user info if needed (adjust based on your auth setup)
      const userId = req?.user?.userId; // Example: Assuming user ID is on req.user
      const userName = req?.user?.realName; // Example: Assuming username is on req.user
      // Call the service method with DTO and optional user info
      const result = await this.spaceService.doToiletEdit(toiletEditDto, userId.toString(), userName);
      return result; // Service returns the standard response object
    } catch (error) {
      // console.log(error)
      // Catch specific exceptions if needed for controller-level logic,
      // otherwise let the global exception filter handle them.
      // Example:
      // if (error instanceof ConflictException) {
      //   // Specific logging or handling for conflicts
      // }
      throw error; // Re-throw for the global filter
    }
  }


  @Post('doToiletDelete')
  @ApiOperation({ summary: '删除卫生间', description: '删除卫生间' })
  @ApiResponse({ 
    status: 200, 
    description: '删除卫生间成功',
    type: ObjectResponseDto
  })
  async doToiletDelete(
    @Request() req: RequestWithUser,
    @Body() dto: DeteleDto
  ): Promise<ObjectResponseDto> {
    return this.spaceService.doToiletDelete(
      dto,
      req.user.userId
    );
  }




  @Get('getToiletRoomList') // Use Get decorator
  @ApiOperation({ summary: '获取卫生间内厕位列表', description: '根据空间编码、区域名称、区域编码等条件获取卫生间内厕位列表' })
  @ApiResponse({ 
    status: 200, 
    description: '成功获取卫生间内厕位列表',
    type: ObjectResponseDto
  })
  async getToiletRoomList(
    @Query() params: GetToiletRoomListParams // Bind and validate request body to GetAreaListParams DTO
      // @Req() req?: any, // Uncomment if you need user info (e.g., for default spaceCode if not in body)
    ): Promise<ApiObjectResponse<ToiletRoomListResponseData>> {
      try {
        const result = await this.spaceService.getToiletRoomList(params);
        return result; // Service returns the standard response object
      } catch (error) {
        throw error;
      }
  }

  @Post('doToiletRoomEdit')
  @ApiOperation({ summary: '编辑卫生间厕位信息', description: '编辑卫生间厕位信息，传入ID为编辑，ID空为新建' })
  @ApiBody({ type: ToiletRoomEditDto })
  @ApiResponse({ 
    status: 200, 
    description: '成功编辑卫生间厕位信息',
    type: ObjectResponseDto
  })
  async doToiletRoomEdit(
    @Body() toiletEditRoomDto: ToiletRoomEditDto, // Validate and bind request body to AreaFloorEditDto
    @Request() req: RequestWithUser,
  ): Promise<ApiObjectResponse<EditResponseData | null>> {
    try {
      // Extract user info if needed (adjust based on your auth setup)
      const userId = req?.user?.userId; // Example: Assuming user ID is on req.user
      const userName = req?.user?.realName; // Example: Assuming username is on req.user
      // Call the service method with DTO and optional user info
      const result = await this.spaceService.doToiletRoomEdit(toiletEditRoomDto, userId.toString(), userName);
      return result; // Service returns the standard response object
    } catch (error) {
      // console.log(error)
      // Catch specific exceptions if needed for controller-level logic,
      // otherwise let the global exception filter handle them.
      // Example:
      // if (error instanceof ConflictException) {
      //   // Specific logging or handling for conflicts
      // }
      throw error; // Re-throw for the global filter
    }
  }
    
  @Post('doToiletRoomDelete')
  @ApiOperation({ summary: '删除卫生间厕位', description: '删除卫生间厕位' })
  @ApiResponse({ 
    status: 200, 
    description: '删除卫生间厕位成功',
    type: ObjectResponseDto
  })
  async doToiletRoomDelete(
    @Request() req: RequestWithUser,
    @Body() dto: DeteleDto
  ): Promise<ObjectResponseDto> {
    return this.spaceService.doToiletRoomDelete(
      dto,
      req.user.userId
    );
  }
    // 在 SpaceController 类中添加以下方法
  @Get('getTree')
  // @ApiBearerAuth()
  @ApiOperation({ summary: '获取空间树结构', description: '获取空间的完整树结构，包括区域、楼层、房间等' })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    type: SpaceTreeResponseDto,
  })
  async getTree(
    @Request() req: RequestWithUser,
    @Query() query: GetSpaceTreeRequestDto,
  ): Promise<SpaceTreeResponseDto> {
    return this.spaceService.getTree(req.user, query);
  }

  @Get('getNewTree')
  @ApiOperation({ summary: '获取新空间树结构' })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    type: NewTreeResponseDto,
  })
  async getNewTree(
    @Request() req: RequestWithUser,
    @Query() query: GetNewTreeRequestDto,
  ): Promise<NewTreeResponseDto> {
    return this.spaceService.getNewTree(req.user, query);
  }

  @Get('/getSpaceAreas')
  @ApiOperation({ summary: '获取空间区域列表', description: '根据空间编码获取区域列表' })
  @ApiResponse({
    status: 200,
    description: '成功获取空间区域列表',
    type: SpaceAreasResponseDto
  })
  async getSpaceAreas(@Query() dto: GetSpaceAreasDto): Promise<SpaceAreasResponseDto> {
    try {
      const spacetree = await this.spaceService.getSpaceAreas(dto.spaceCode);
      return {
        code: '200',
        msg: 'success',
        data: {
          spacetree
        }
      };
    } catch (error) {
      throw new BadRequestException({
        code: '400',
        msg: error.message
      });
    }
  }
}

@UseGuards(JwtAuthGuard)
@Controller('ai')
export class AiController {
  constructor(private readonly spaceService: SpaceService) {}

  @Post('getToiletSensorStatus')
  async getToiletSensorStatus(
    @Request() req: RequestWithUser,
    @Body() body: any,
    @Query() query: any,
  ): Promise<{ code: string; msg: string; data?: any }> {
    // Merge body and query to mimic PHP's $_REQUEST behavior
    const spaceCode = body?.spaceCode ?? query?.spaceCode;
    const gender = body?.gender ?? query?.gender;
    const floorCode = body?.floorCode ?? query?.floorCode;

    // 参数校验
    if (!spaceCode || !gender) {
      return { code: '400', msg: '缺少必要参数' };
    }
    if (gender !== 'TMAN' && gender !== 'TWOMAN') {
      return { code: '400', msg: '参数格式不正确' };
    }

    // 调用服务层逻辑，保持返回结构一致
    return await this.spaceService.getToiletSensorStatus(req.user.userId, {
      spaceCode,
      gender,
      floorCode,
    });
  }
}
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { SpaceController, AiController } from './space.controller';
import { SpaceService } from './space.service';
import { Space } from '../entities/Space';
import { Floor } from '../entities/Floor';
import { Area } from '../entities/Area';
import { FloorArea } from '../entities/FloorArea';
import { FloorMroom } from '../entities/FloorMroom';
import { FloorRoom } from '../entities/FloorRoom';
import { SystemRole } from '../entities/SystemRole';
import { FloorPubArea } from '../entities/FloorPubArea';
import { FloorToilet } from '../entities/FloorToilet';
import { FloorToiletRoom } from '../entities/FloorToiletRoom';
import { FloorWorkstation } from '../entities/FloorWorkstation';
import { UserCurrentSpace } from '../entities/UserCurrentSpace';
import { User } from '../entities/User';
import { IotGateway } from '../entities/IotGateway';
import { IotDevice } from '../entities/IotDevice';
import { UserRole } from '../entities/UserRole';
import { SpaceRole } from '../entities/SpaceRole';
import { ZeekrMeetRoom } from '../entities/ZeekrMeetRoom';
import { SpaceHead } from '../entities/SpaceHead';
import { UserModule } from '../user/user.module';

@Module({
  imports: [
    UserModule,
    TypeOrmModule.forFeature([
      Space,
      SystemRole,
      Floor,
      Area,
      FloorArea,
      FloorMroom,
      FloorRoom,
      FloorPubArea,
      FloorToilet,
      FloorToiletRoom,
      FloorWorkstation,
      UserCurrentSpace,
      User,
      IotGateway,
      IotDevice,
      UserRole,
      SpaceRole,
      ZeekrMeetRoom,
      SpaceHead
    ]),
  ],
  controllers: [SpaceController, AiController],
  providers: [SpaceService],
  exports: [SpaceService],
})
export class SpaceModule {}
import { Injectable, BadRequestException, HttpStatus, HttpException, Inject, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, ILike,In, Like, FindOptionsWhere, Not, DataSource } from 'typeorm';
import * as fs from 'fs';
import * as path from 'path';
import { Space } from '../entities/Space';
import { UserCurrentSpace } from '../entities/UserCurrentSpace';
import { Area } from '../entities/Area';
import { Floor } from '../entities/Floor';
import { FloorArea } from '../entities/FloorArea';
import { FloorMroom } from '../entities/FloorMroom';
import { FloorPubArea } from '../entities/FloorPubArea';
import { FloorRoom } from '../entities/FloorRoom';
import { FloorToilet } from '../entities/FloorToilet';
import { FloorWorkstation } from '../entities/FloorWorkstation';
import { IotGateway } from '../entities/IotGateway';
import { IotDevice } from '../entities/IotDevice';
import {
  SelectSpaceRequestDto,
  SelectSpaceResponseDto,
} from './dto/select-space.dto';
import { SpaceListDto } from './dto/space-list.dto';
import { SpaceEditDto } from './dto/space-edit.dto';
import { SpaceFloorListDto } from './dto/space-floor-list.dto';
import { SpaceFloorResponseDto } from './dto/space-floor-response.dto';
import { AreaEditDto, AreaEditResponseDto } from './dto/area-edit.dto';
import { SaveFloorRequestDto } from './dto/save-floor.dto';
import { DeleteFloorDto,DeleteFloorResponseDto } from './dto/floor-delete.dto';
import { FloorAreaDeteleDto, FloorAreaEditDto } from './dto/floorArea.dto';
import { ObjectResponseDto } from './dto/object.dto';
import { FloorTreeNode,AreaTreeNode,SpaceTreeNode,FloorTreeResponseData,ApiObjectResponse,GetRoomListParams,RoomListItem,RoomListResponseData, ApiListResponse, RoomEditDto, RoomEditResponseData, DeteleDto, GetAreaListParams, AreaListResponseData, AreaListItem, AreaFloorEditDto, GetPublicAreaListParams, PublicAreaListResponseData, PublicAreaListItem, PublicAreaEditDto, EditResponseData, GetMeetingRoomListParams, MeetingroomListResponseData, MeetingroomListItem, ToiletListResponseData, GetToiletListParams, MeetingroomEditDto, ToiletEditDto, GetToiletRoomListParams, ToiletRoomListResponseData, ToiletRoomListItem,ToiletRoomEditDto } from './dto/space.dto'
import { FloorToiletRoom } from '@server/entities/FloorToiletRoom';
import { 
  GetSpaceTreeRequestDto, 
  SpaceTreeResponseDto, 
  SpaceTreeNodeDto,
  FloorAreaTreeNodeDto,
  FloorTreeNodeDto,
  AreaTreeNodeDto,
  RoomTreeNodeDto,
  PubAreaTreeNodeDto,
  MroomTreeNodeDto,
  ToiletTreeNodeDto
} from './dto/space-tree.dto';
import { GetNewTreeRequestDto, NewTreeResponseDto } from './dto/get-new-tree.dto';
import { SystemRole } from '../entities/SystemRole';
import { UserRole } from '../entities/UserRole';
import { User } from '../entities/User';
import { SpaceRole } from '../entities/SpaceRole';

interface MulterFile {
  fieldname: string;
  originalname: string;
  encoding: string;
  mimetype: string;
  size: number;
  destination: string;
  filename: string;
  path: string;
  buffer: Buffer;
}

@Injectable()
export class SpaceService {
  private readonly logger = new Logger(SpaceService.name);

  constructor(
    @InjectRepository(Space)
    private spaceRepository: Repository<Space>,
    @InjectRepository(UserCurrentSpace)
    private userCurrentSpaceRepository: Repository<UserCurrentSpace>,
    @InjectRepository(Area)
    private areaRepository: Repository<Area>,
    @InjectRepository(Floor)
    private floorRepository: Repository<Floor>,
    @InjectRepository(FloorArea)
    private floorAreaRepository: Repository<FloorArea>,
    @InjectRepository(FloorMroom)
    private floorMroomRepository: Repository<FloorMroom>,
    @InjectRepository(FloorPubArea)
    private floorPubAreaRepository: Repository<FloorPubArea>,
    @InjectRepository(FloorRoom)
    private floorRoomRepository: Repository<FloorRoom>,
    @InjectRepository(FloorToilet)
    private floorToiletRepository: Repository<FloorToilet>,
    @InjectRepository(FloorToiletRoom)
    private floorToiletRoomRepository: Repository<FloorToiletRoom>,
    @InjectRepository(FloorWorkstation)
    private floorWorkstationRepository: Repository<FloorWorkstation>,
    @InjectRepository(IotGateway)
    private iotGatewayRepository: Repository<IotGateway>,
    @InjectRepository(IotDevice)
    private iotDeviceRepository: Repository<IotDevice>,
    @InjectRepository(UserCurrentSpace)
    private UserCurrentSpaceRepository: Repository<UserCurrentSpace>,
    @InjectRepository(SystemRole)
    private systemRoleRepository: Repository<SystemRole>,
    @InjectRepository(UserRole)
    private userRoleRepository: Repository<UserRole>,
    @InjectRepository(User)
    private userRepository: Repository<User>,
    @InjectRepository(SpaceRole)
    private spaceRoleRepository: Repository<SpaceRole>,
    private readonly dataSource: DataSource,
  ) {}
  async isSpaceCodeExists(code: string): Promise<boolean> {
    if (!code) return false
    const existing = await this.spaceRepository.findOne({ where: { code, deleteFlag: 1 } })
    return !!existing
  }
  async ingestSpaceInfoTx(spaceInfo: any) {
    const result = { space: 0, areas: 0, floors: 0, floorAreas: 0, meetings: 0, rooms: 0, toilets: 0, errors: [] as any[] }
    const qr = this.dataSource.createQueryRunner()
    await qr.connect()
    await qr.startTransaction()
    try {
      const spaceRepo = qr.manager.getRepository(Space)
      const areaRepo = qr.manager.getRepository(Area)
      const floorAreaRepo = qr.manager.getRepository(FloorArea)
      const floorRepo = qr.manager.getRepository(Floor)
      const pubRepo = qr.manager.getRepository(FloorPubArea)
      const mroomRepo = qr.manager.getRepository(FloorMroom)
      const roomRepo = qr.manager.getRepository(FloorRoom)
      const toiletRepo = qr.manager.getRepository(FloorToilet)
      let nSpace = 0
      let nAreas = 0
      let nFloors = 0
      let nFloorAreas = 0
      let nMeetings = 0
      let nRooms = 0
      let nToilets = 0
      const spaceCode: string = spaceInfo?.space?.code || ''
      const spaceName: string = spaceInfo?.space?.name || ''
      if (!spaceCode || !spaceName) throw new Error('invalid_space_fields')
      const existed = await spaceRepo.findOne({ where: { code: spaceCode, deleteFlag: 1 } })
      if (existed) throw new Error('space_code_exists')
      await spaceRepo.save({
        code: spaceCode,
        name: spaceName,
        sortOrder: 0,
        deleteFlag: 1,
        createtime: Math.floor(Date.now() / 1000).toString(),
      } as any)
      nSpace++
      const areas: any[] = Array.isArray(spaceInfo?.areas) ? spaceInfo.areas : []
      for (const a of areas) {
        const dup = await areaRepo.findOne({ where: { code: a.code, spaceCode, deleteFlag: 1 } })
        if (dup) throw new Error(`area_exists:${a.code}`)
        await areaRepo.save({ code: a.code, name: a.name, spaceCode, sortOrder: 0, deleteFlag: 1, createtime: Math.floor(Date.now() / 1000).toString() } as any)
        nAreas++
      }
      const floors: any[] = Array.isArray(spaceInfo?.floors) ? spaceInfo.floors : []
      for (const f of floors) {
        const dup = await floorRepo.findOne({ where: { code: f.code, spaceCode, deleteFlag: 1 } })
        if (dup) throw new Error(`floor_exists:${f.code}`)
        await floorRepo.save({ code: f.code, name: f.name, spaceCode, areaCode: f.areaCode || '', sortOrder: 0, deleteFlag: 1, createtime: Math.floor(Date.now() / 1000).toString() } as any)
        nFloors++
      }
      const floorAreaMap = new Map<string, string>()
      for (const f of floors) {
        const ac = ((f?.areaCode ?? '') as string).trim()
        if (ac) floorAreaMap.set(f.code, ac)
      }
      const pubs: any[] = Array.isArray(spaceInfo?.floorAreas) ? spaceInfo.floorAreas : []
      for (const p of pubs) {
        const dup = await pubRepo.findOne({ where: { code: p.code, spaceCode, floorCode: p.floorCode, deleteFlag: 1 } })
        if (dup) throw new Error(`pub_exists:${p.code}:${p.floorCode}`)
        const mapped = floorAreaMap.get(p.floorCode)
        if (!mapped) {
          result.errors.push({ entity: 'pub', code: p.code, floorCode: p.floorCode, msg: 'missing_areaCode' })
          continue
        }
        await pubRepo.save({ code: p.code, name: p.name, spaceCode, floorCode: p.floorCode, areaCode: mapped, sortOrder: 0, deleteFlag: 1, createtime: Math.floor(Date.now() / 1000).toString() } as any)
        nFloorAreas++
      }
      const officeAreas: any[] = Array.isArray(spaceInfo?.officeAreas) ? spaceInfo.officeAreas : []
      for (const o of officeAreas) {
        const dup = await floorAreaRepo.findOne({ where: { code: o.code, spaceCode, floorCode: o.floorCode, deleteFlag: 1 } })
        if (dup) throw new Error(`office_exists:${o.code}:${o.floorCode}`)
        const mapped = floorAreaMap.get(o.floorCode)
        if (!mapped) {
          result.errors.push({ entity: 'officeArea', code: o.code, floorCode: o.floorCode, msg: 'missing_areaCode' })
          continue
        }
        await floorAreaRepo.save({ code: o.code, name: o.name, spaceCode, floorCode: o.floorCode, areaCode: mapped, sortOrder: 0, deleteFlag: 1, createtime: Math.floor(Date.now() / 1000).toString() } as any)
        nFloorAreas++
      }
      const meetings: any[] = Array.isArray(spaceInfo?.meetings) ? spaceInfo.meetings : []
      for (const m of meetings) {
        const dup = await mroomRepo.findOne({ where: { code: m.code, spaceCode, floorCode: m.floorCode, deleteFlag: 1 } })
        if (dup) throw new Error(`mroom_exists:${m.code}:${m.floorCode}`)
        const mapped = floorAreaMap.get(m.floorCode)
        if (!mapped) {
          result.errors.push({ entity: 'meeting', code: m.code, floorCode: m.floorCode, msg: 'missing_areaCode' })
          continue
        }
        await mroomRepo.save({ code: m.code, name: m.name, spaceCode, floorCode: m.floorCode, areaCode: mapped, sortOrder: 0, deleteFlag: 1, createtime: Math.floor(Date.now() / 1000).toString() } as any)
        nMeetings++
      }
      const rooms: any[] = Array.isArray(spaceInfo?.rooms) ? spaceInfo.rooms : []
      for (const r of rooms) {
        const dup = await roomRepo.findOne({ where: { code: r.code, spaceCode, floorCode: r.floorCode, deleteFlag: 1 } })
        if (dup) throw new Error(`room_exists:${r.code}:${r.floorCode}`)
        const mapped = floorAreaMap.get(r.floorCode)
        if (!mapped) {
          result.errors.push({ entity: 'room', code: r.code, floorCode: r.floorCode, msg: 'missing_areaCode' })
          continue
        }
        await roomRepo.save({ code: r.code, name: r.name, spaceCode, floorCode: r.floorCode, areaCode: mapped, sortOrder: 0, deleteFlag: 1, createtime: Math.floor(Date.now() / 1000).toString() } as any)
        nRooms++
      }
      const toilets: any[] = Array.isArray(spaceInfo?.toilets) ? spaceInfo.toilets : []
      for (const t of toilets) {
        let type = t.type || ''
        if (!type) {
          const nm: string = t.name || ''
          if (nm.includes('男')) type = 'man'
          else if (nm.includes('女')) type = 'woman'
        }
        const dup = await toiletRepo.findOne({ where: { code: t.code, spaceCode, floorCode: t.floorCode, deleteFlag: 1 } })
        if (dup) throw new Error(`toilet_exists:${t.code}:${t.floorCode}`)
        const mapped = floorAreaMap.get(t.floorCode)
        if (!mapped) {
          result.errors.push({ entity: 'toilet', code: t.code, floorCode: t.floorCode, msg: 'missing_areaCode' })
          continue
        }
        await toiletRepo.save({ code: t.code, name: t.name, type, spaceCode, floorCode: t.floorCode, areaCode: mapped, sortOrder: 0, deleteFlag: 1, createtime: Math.floor(Date.now() / 1000).toString() } as any)
        nToilets++
      }
      result.space = nSpace
      result.areas = nAreas
      result.floors = nFloors
      result.floorAreas = nFloorAreas
      result.meetings = nMeetings
      result.rooms = nRooms
      result.toilets = nToilets
      await qr.commitTransaction()
    } catch (e: any) {
      try { await qr.rollbackTransaction() } catch {}
      result.errors.push({ msg: e?.message || String(e) })
    } finally {
      try { await qr.release() } catch {}
    }
    return result
  }
  async getSpaceList(dto: SpaceListDto) {
    const page = dto.page || 1;
    const pageSize = dto.pageSize || 10;

    const [spaces, total] = await this.spaceRepository.findAndCount({
      where: {
        deleteFlag: 1,
        ...(dto.title ? { name: ILike(`%${dto.title}%`) } : {}),
      },
      skip: (page - 1) * pageSize,
      take: pageSize,
      order: { sortOrder: 'ASC' },
    });

    const list = spaces.map((space) => ({
      id: space.id,
      code: space.code,
      name: space.name,
      title: space.name,
      serialNumber: space.serialNumber,
      sortOrder: space.sortOrder,
      deleteFlag: space.deleteFlag,
      sourceSpaceId: space.sourceSpaceId,
      sourceSpaceName: space.sourceSpaceName,
      orgCode: space.orgCode,
      createtime: space.createtime,
      floors: [], // TODO: Implement floor list
      createUserId: space.createUserId,
      createUserName: space.createUserName,
      shortName: space.shortName,
    }));

    return { list, total };
  }
  async editSpace(
    dto: SpaceEditDto,
    userId: string,
    userName: string,
  ): Promise<void> {
    if (!dto.title || !dto.code) {
      throw new BadRequestException('请填写完整信息');
    }

    const space = dto.id
      ? await this.spaceRepository.findOne({ where: { id: parseInt(dto.id) } })
      : null;

    const spaceData = {
      code: dto.code,
      name: dto.title,
      shortName: dto.shortName || '',
      serialNumber: dto.serialNumber || '',
      desc: dto.desc || '',
      sortOrder: 0,
      address: dto.address || '',
      province: dto.province || '',
      city: dto.city || '',
      district: dto.district || '',
      postcode: dto.postcode || '',
      longitude: dto.longitude || '',
      latitude: dto.latitude || '',
      floorArea: dto.floorArea || '',
      officeArea: dto.buildingInfo?.area || '',
      officeUserNum: dto.buildingInfo?.personNum || '',
      floorCount: dto.floorCount || '',
      meetingRoomNum: dto.spaceInfo?.meetingRoomNum || '',
      elevatorNum: dto.spaceInfo?.elevatorNum || '',
      packingNum: dto.spaceInfo?.packingNum || '',
      restAreaNum: dto.spaceInfo?.restAreaNum || '',
      restaurantStallNum: dto.spaceInfo?.restaurantStallNum || '',
      workstationNum: dto.spaceInfo?.workstationNum || '',
      createUserId: parseInt(userId),
      createUserName: userName,
      createtime: Math.floor(Date.now() / 1000).toString(),
    };

    if (!space) {
      // Create new space
      await this.spaceRepository.save(spaceData);
    } else {
      // Update existing space
      // If space code changed, update related tables
      if (space.code !== dto.code) {
        await Promise.all([
          this.areaRepository.update(
            { spaceCode: space.code },
            { spaceCode: dto.code },
          ),
          this.floorRepository.update(
            { spaceCode: space.code },
            { spaceCode: dto.code },
          ),
          this.floorAreaRepository.update(
            { spaceCode: space.code },
            { spaceCode: dto.code },
          ),
          this.floorMroomRepository.update(
            { spaceCode: space.code },
            { spaceCode: dto.code },
          ),
          this.floorRoomRepository.update(
            { spaceCode: space.code },
            { spaceCode: dto.code },
          ),
          this.floorToiletRepository.update(
            { spaceCode: space.code },
            { spaceCode: dto.code },
          ),
          this.floorWorkstationRepository.update(
            { spaceCode: space.code },
            { spaceCode: dto.code },
          ),
          this.iotGatewayRepository.update(
            { spaceCode: space.code },
            { spaceCode: dto.code },
          ),
          this.iotDeviceRepository.update(
            { spaceCode: space.code },
            { spaceCode: dto.code },
          ),
          this.userCurrentSpaceRepository.update(
            { spaceCode: space.code },
            { spaceCode: dto.code },
          ),
          this.systemRoleRepository.update(
            { spaceCode: space.code },
            { spaceCode: dto.code },
          ),
        ]);
      }

      // If space name changed, update related tables
      if (space.name !== dto.title) {
        await Promise.all([
          this.iotGatewayRepository.update(
            { spaceCode: dto.code },
            { spaceName: dto.title },
          ),
          this.iotDeviceRepository.update(
            { spaceCode: dto.code },
            { spaceName: dto.title },
          ),
          this.userCurrentSpaceRepository.update(
            { spaceCode: dto.code },
            { spaceName: dto.title },
          ),
        ]);
      }

      await this.spaceRepository.update(space.id, spaceData);
    }
  }
  async selectSpace(
    userId: string,
    dto: SelectSpaceRequestDto,
  ): Promise<SelectSpaceResponseDto> {
    // Validate space exists
    const space = await this.spaceRepository.findOne({
      where: { code: dto.spaceCode },
    });

    if (!space) {
      return {
        code: '400',
        msg: '无效空间',
        data: {
          spaceCode: '',
          spaceName: '',
        },
      };
    }

    // Check if user already has a current space
    const currentSpace = await this.userCurrentSpaceRepository.findOne({
      where: { userId },
    });

    if (currentSpace) {
      // Update existing record
      await this.userCurrentSpaceRepository.update(currentSpace.id, {
        spaceId: space.id.toString(),
        spaceCode: space.code,
        spaceName: space.name,
      });
    } else {
      // Create new record
      const newSpace = new UserCurrentSpace();
      newSpace.userId = userId;
      newSpace.spaceId = space.id.toString();
      newSpace.spaceCode = space.code;
      newSpace.spaceName = space.name;
      // 使用时间戳格式而不是ISO格式
      newSpace.createtime = Math.floor(Date.now() / 1000).toString();
      await this.userCurrentSpaceRepository.save(newSpace);
    }

    return {
      code: '200',
      msg: 'success',
      data: {
        spaceCode: space.code,
        spaceName: space.name,
      },
  }}
  async getSpaceFloorList(params: SpaceFloorListDto): Promise<SpaceFloorResponseDto> {
    // 查询楼层数据
    // console.log("查询楼层数据",params.spaceCode)
    const floors = await this.floorRepository.find({
      where: { spaceCode: params.spaceCode },
      select: ['id', 'code', 'name', 'areaCode', 'floorArea','officeArea'],
      order: { sortOrder: 'ASC' }
    });

    // 查询关联区域数据
    // const areaCodes = [...new Set(floors.map(f => f.areaCode))];

    const areas = await this.areaRepository.find({
      where: { spaceCode: params.spaceCode,deleteFlag:1 },
      select: ['id','code', 'name']
    });
    // console.log("SpaceFloorList",floors)
    areas.unshift({
      id: 0,
      code: '0',
      name: '全部楼层',
      serialNumber: '',
      sortOrder: 0,
      deleteFlag: 0,
      spaceCode: params.spaceCode?params.spaceCode:'',
      createtime: ''
    });
    return {
      data: {
        SpaceFloorList: floors.map(f => ({
          id: f.id,
          floorNum: f.code,
          floorCode: f.code,
          floorName: f.name,
          areaCode: f.areaCode,
          floorSquare: f.floorArea,
          areaId:f.areaCode,
          officeArea:f.officeArea,
          floorArea: f.floorArea
        })),
        SpaceFloorAreaList: areas.map(a => ({
          areaId: a.id,
          areaCode: a.code,
          areaName: a.name
        }))
      }
    };
  }
  async createFloorArea(dto: AreaEditDto): Promise<AreaEditResponseDto> {
    try {
      // 检查区域编码是否已存在
      const existingArea = await this.areaRepository.findOne({ 
        where: { code: dto.floorAreaCode, spaceCode: dto.spaceCode, deleteFlag: 1 }
      });
      
      if (existingArea) {
        throw new BadRequestException('区域编码已存在');
      }

      // 创建新区域
    const newArea = this.areaRepository.create({
        code: dto.floorAreaCode,
        name: dto.floorAreaName,
        spaceCode: dto.spaceCode,
        createtime: Math.floor(Date.now() / 1000).toString()
    });

      const savedArea = await this.areaRepository.save(newArea);

      return {
        code: '200',
        msg: 'success',
        data: {
          spaceCode: dto.spaceCode,
          areaCode:savedArea.spaceCode
        }
      };
    } catch (error) {
      if (error instanceof BadRequestException) {
        throw error;
      }
      throw new BadRequestException('区域创建失败');
    }
  }
  async handleSaveFloor(dto: SaveFloorRequestDto) {
    try {
      const floorData = JSON.parse(dto.floor);
      const { floorName, floorNum, areaCode, floorSquare,floorSort, id } = floorData;
      const spaceCode = dto.spaceCode;

      // 参数校验
      if (!floorName || !floorNum || !areaCode) {
        throw new BadRequestException('请填写完整信息');
      }

      if (id) {
        // 更新逻辑
        const existingFloor = await this.floorRepository.findOne({ 
          where: { id, spaceCode }
        });

        if (!existingFloor) {
          throw new BadRequestException('无效楼层信息');
        }

        // 更新关联表
        // console.log("floorNum",floorNum,"existingFloor.code",existingFloor.code,"areaCode",areaCode,"existingFloor.areaCode",existingFloor.areaCode)
        if (floorNum !== existingFloor.code || areaCode !== existingFloor.areaCode) {
          await this.updateRelatedTables({
            oldFloorCode: existingFloor.code,
            newFloorCode: floorNum,
            spaceCode,
            areaCode: existingFloor.areaCode,
            newAreaCode: areaCode
          });
        }

        // 更新楼层名称
        if (floorName !== existingFloor.name) {
          await this.updateFloorNameInDevices({
            floorCode: floorNum,
            spaceCode,
            areaCode: existingFloor.areaCode,
            floorName
          });
        }

        // 更新楼层信息
        await this.floorRepository.update(id, {
          code: floorNum,
          sortOrder:floorSort,
          name: floorName,
          areaCode:areaCode,
          floorArea: floorSquare || 0
        });

      } else {
        // 创建逻辑
        const existing = await this.floorRepository.findOne({
          where: { code: floorNum, spaceCode , deleteFlag:1}
        });

        if (existing) {
          throw new BadRequestException('楼层编码已存在');
        }

        const newFloor = this.floorRepository.create({
          code: floorNum,
          name: floorName,
          sortOrder:floorSort,
          areaCode: areaCode,
          spaceCode,
          floorArea: floorSquare || 0,
          createtime: Math.floor(Date.now() / 1000).toString()
        });

        await this.floorRepository.save(newFloor);
      }

      return { code: '200', msg: '操作成功' };
    } catch (error) {
      if (error instanceof BadRequestException) {
        throw error;
      }
      console.log(error)
      throw new BadRequestException('楼层保存失败');
    }
  }
  private async updateRelatedTables({ oldFloorCode, newFloorCode, spaceCode, areaCode, newAreaCode }) {
    // console.log("updateRelatedTables",oldFloorCode,newFloorCode,spaceCode,areaCode,newAreaCode)
    // const tables = [
    //   this.floorAreaRepository,
    //   this.floorMroomRepository,
    //   this.floorRoomRepository,
    //   this.floorToiletRepository,
    //   this.floorWorkstationRepository,
    //   this.iotGatewayRepository,
    //   this.iotDeviceRepository,
    // ];

    // await Promise.all(tables.map(repo => 
    //   repo.update(
    //     { spaceCode, areaCode, floorCode: oldFloorCode },
    //     { floorCode: newFloorCode }
    //   )
    // ));
    // if(areaCode == 0 ){ areaCode = ''}
    // if(newAreaCode == 0 ){ newAreaCode = '' }
    // console.log("updateRelatedTables",oldFloorCode,newFloorCode,spaceCode,areaCode,newAreaCode)
    await Promise.all([
      this.floorAreaRepository.update(
        { spaceCode,   floorCode: oldFloorCode },
        { floorCode: newFloorCode ,areaCode:newAreaCode}
      ),
       this.floorPubAreaRepository.update(
        { spaceCode,   floorCode: oldFloorCode },
        { floorCode: newFloorCode ,areaCode:newAreaCode}
      ),
      this.floorMroomRepository.update(
        { spaceCode,  floorCode: oldFloorCode },
        { floorCode: newFloorCode ,areaCode:newAreaCode}
      ),
      this.floorRoomRepository.update(
        { spaceCode,  floorCode: oldFloorCode },
        { floorCode: newFloorCode ,areaCode:newAreaCode}
      ),
      this.floorToiletRepository.update(
        { spaceCode,  floorCode: oldFloorCode },
        { floorCode: newFloorCode ,areaCode:newAreaCode}
      ),
      this.floorWorkstationRepository.update(
        { spaceCode,  floorCode: oldFloorCode },
        { floorCode: newFloorCode ,areaCode:newAreaCode}
      ),
      this.iotGatewayRepository.update(
        { spaceCode,  floorCode: oldFloorCode },
        { floorCode: newFloorCode ,areaCode:newAreaCode}
      ),
      this.iotDeviceRepository.update(
        { spaceCode,  floorCode: oldFloorCode },
        { floorCode: newFloorCode ,areaCode:newAreaCode}
      ),
    ]);


  }
  private async updateFloorNameInDevices({ floorCode, spaceCode, areaCode, floorName }) {
    await Promise.all([
      this.iotGatewayRepository.update(
        { spaceCode, areaCode, floorCode },
        { floorName }
      ),
      this.iotDeviceRepository.update(
        { spaceCode, areaCode, floorCode },
        { floorName }
      )
    ]);
  }
  async deleteFloor(dto: DeleteFloorDto): Promise<DeleteFloorResponseDto> {
    try {
      const { floorNum, spaceCode } = dto;
      // 查找楼层
      const floor = await this.floorRepository.findOne({
        where: { code: floorNum, spaceCode }
      });
      if (!floor) {
        throw new BadRequestException('无效楼层');
      }
      // 更新删除标识为0
      //  await this.floorRepository.update(floor.id, { deleteFlag: 0 });
      // await this.floorRepository.delete({})
        await this.floorRepository.delete({code:floorNum})
      return {
        code: '200',
        msg: '操作成功'
      };
    } catch (error) {
      if (error instanceof BadRequestException) {
        throw error;
      }
      throw new BadRequestException('删除楼层失败');
    }
  }
  async modifyAreaName(dto: FloorAreaEditDto): Promise<ObjectResponseDto> {
    try {
      const { floorAreaCode, floorAreaName, floorAreaID, spaceCode } = dto;

      if (!floorAreaCode || !floorAreaName || !floorAreaID || !spaceCode) {
        throw new BadRequestException('请填写完整信息');
      }

      // 根据spaceCode和floorAreaID（原区域code）查询区域
      const area = await this.areaRepository.findOne({
        where: { 
          id: floorAreaID // 确保类型匹配
        }
      });

      if (!area) {
        throw new BadRequestException('无效楼层区域');
      }

      // 区域代码发生变化时更新关联表
      if (area.code !== floorAreaCode) {
        await Promise.all([
          this.floorRepository.update(
            { spaceCode, areaCode: area.code },
            { areaCode: floorAreaCode }
          ),
          this.floorAreaRepository.update(
            { spaceCode, areaCode: area.code },
            { areaCode: floorAreaCode }
          ),
          this.floorMroomRepository.update(
            { spaceCode, areaCode: area.code },
            { areaCode: floorAreaCode }
          ),
          this.floorRoomRepository.update(
            { spaceCode, areaCode: area.code },
            { areaCode: floorAreaCode }
          ),
          this.floorToiletRepository.update(
            { spaceCode, areaCode: area.code },
            { areaCode: floorAreaCode }
          ),
          this.floorWorkstationRepository.update(
            { spaceCode, areaCode: area.code },
            { areaCode: floorAreaCode }
          ),
          this.iotGatewayRepository.update(
            { spaceCode, areaCode: area.code },
            { areaCode: floorAreaCode }
          ),
          this.iotDeviceRepository.update(
            { spaceCode, areaCode: area.code },
            { areaCode: floorAreaCode }
          )
        ]);
      }

      // 区域名称变化时更新设备表
      if (area.name !== floorAreaName) {
        await Promise.all([
          this.iotGatewayRepository.update(
            { spaceCode, areaCode: floorAreaCode },
            { areaName: floorAreaName }
          ),
          this.iotDeviceRepository.update(
            { spaceCode, areaCode: floorAreaCode },
            { areaName: floorAreaName }
          )
        ]);
      }

      // 更新区域基础信息
      await this.areaRepository.update(
        { id: area.id }, // 根据ID更新
        { code: floorAreaCode, name: floorAreaName }
      );
      return {
        code: '200',
        msg: '操作成功'
      };
    } catch (error) {
      console.log(error)
      if (error instanceof BadRequestException) {
        throw error;
      }
      throw new BadRequestException('编辑楼层区域失败');
    }
  }
  async doDeleteFloorArea(
    dto: FloorAreaDeteleDto,
    userId: number
  ): Promise<ObjectResponseDto> {
    const userCurrentSpace = await this.UserCurrentSpaceRepository.findOne({
      where: { userId: userId.toString() },
    });
    // console.log("spaceCode",userCurrentSpace?.spaceCode)

      try {
        const { ids } = dto;
        // console.log("ids",ids)

        if (!ids) {
          throw new BadRequestException('请填写完整信息');
        }
        if (!userCurrentSpace) {
          throw new BadRequestException('丢失当前空间信息');
        }
        // 根据spaceCode和floorAreaID（原区域code）查询区域
        const area = await this.areaRepository.findOne({
          where: { 
            code: ids, // 确保类型匹配
            spaceCode:userCurrentSpace?.spaceCode
          }
        });

        if (!area) {
          throw new BadRequestException('无效楼层区域');
        }
        // 更新区域基础信息
        await this.areaRepository.update(
          { id: area.id }, // 根据ID更新
          { deleteFlag: 0 }
        );


        await this.floorRepository.update(
          { areaCode: area.code }, // 根据ID更新
          { areaCode: "0" }
        );

        return {
          code: '200',
          msg: '操作成功'
        };
      } catch (error) {
        console.log(error)
        if (error instanceof BadRequestException) {
          throw error;
        }
        throw new BadRequestException('删除楼层区域失败');
      }

  }
  /**
     * Retrieves the hierarchical tree structure (Space -> Area -> Floor)
     * for a given space code.
     * Replicates the logic from getTreeByFloor.do PHP script.
     *
     * @param requestedSpaceCode The space code provided in the request.
     * @param user Authenticated user object, potentially containing a default spaceCode.
     *             (Modify signature based on how you pass user info)
     * @returns Promise<ApiResponse<FloorTreeResponseData>> The structured tree data or an error response.
     */
  async getTreeByFloor(
    user: any,
    requestedSpaceCode?: string,
    // User?: User // Example: uncomment and use if needed for default spaceCode fallback
  ): Promise<ApiObjectResponse<FloorTreeResponseData>> {
    const userCurrentSpace = await this.UserCurrentSpaceRepository.findOne({
      where: { userId: user.userId.toString() },
    });
    // Determine the target space code. Prioritize the requested code.
    // Add fallback logic using 'user.spaceCode' if required by your application rules.
    const spaceCode = requestedSpaceCode?requestedSpaceCode:userCurrentSpace?.spaceCode; // Simplified based on PHP prioritizing $_REQUEST

    if (!spaceCode) {
        // Consider throwing BadRequestException if spaceCode is mandatory
        // For now, mirroring PHP's dependency on it being set somehow before this point
         throw new BadRequestException('Space code is required.'); // Or BadRequestException
    }

    // 1. Fetch the root Space
    const space = await this.spaceRepository.findOne({
        where: {
            code: spaceCode,
            deleteFlag: 1, // Assuming 1 means not deleted
        },
    });

    if (!space) {
        // Throwing NestJS exception, which can be caught by an ExceptionFilter
        // to format the standard {code, msg} response.
        // The PHP script returned {code: 400}, but NotFound (404) seems more appropriate.
        // Adjust if 400 is strictly required.
        throw new BadRequestException(`无效空间 (Space code: ${spaceCode})`);
        // If you need the exact PHP error structure immediately:
        // return { code: '400', msg: '无效空间' };
    }

    // 2. Initialize the root structure
    const spaceStructure: SpaceTreeNode = {
        type: 'space',
        spaceCode: space.code,
        id: space.code,
        value: space.code,
        name: space.name,
        label: space.name,
        crumblist: [space.name],
        children: [],
    };

    // 3. Fetch all Areas for the Space
    const areas = await this.areaRepository.find({
        where: {
            spaceCode: space.code,
            deleteFlag: 1,
        },
        order: {
            sortOrder: 'ASC', // Match PHP's ordering
        },
    });

    // 4. Fetch all Floors for the Space (more efficient than querying per area)
    const floors = await this.floorRepository.find({
        where: {
            spaceCode: space.code,
            deleteFlag: 1,
        },
        order: {
            // Order by areaCode first if floors might be mixed, then by sortOrder
            // areaCode: 'ASC', // Add if necessary
            sortOrder: 'ASC', // Match PHP's ordering
        },
    });

    // 5. Map floors by their areaCode for efficient lookup
    const floorsByArea = new Map<string, Floor[]>();
    // const floorsNoArea = new Map<string, Floor[]>();

    for (const floor of floors) {
        const areaFloors = floorsByArea.get(floor.areaCode) || [];
        areaFloors.push(floor);
        floorsByArea.set(floor.areaCode, areaFloors);
    }

    // for (const floor of floors) {
    //   const areaFloors = floorsByArea.get("") || [];
    //   areaFloors.push(floor);
    //   floorsNoArea.set("default", areaFloors);
    // }
    for (const floor of floors) {
      // console.log(floor)
      if(floor.areaCode=='0'){//为分配楼层区域的楼层
        const floorCrumblist = [space.name, floor.name];
        const floorItemForRoot: AreaTreeNode = {
          type: 'floor',
          spaceCode: space.code,
          floorAreaCode: "",
          id: floor.code,
          floorCode: floor.code,
          parentId: space.code, // Area's parent is the Space
          value: floor.code,
          name: floor.name,
          label: floor.name,
          crumblist: floorCrumblist,
          children: [],
        };
        spaceStructure.children.push(floorItemForRoot);
      }
    }
    // 6. Build the Area and Floor hierarchy
    for (const area of areas) {
        const areaCrumblist = [...spaceStructure.crumblist, area.name];
        const areaItem: AreaTreeNode = {
            type: 'floorArea',
            spaceCode: space.code,
            floorCode: "",
            floorAreaCode: area.code,
            id: area.code,
            parentId: space.code, // Area's parent is the Space
            value: area.code,
            name: area.name,
            label: area.name,
            crumblist: areaCrumblist,
            children: [],
        };

        // Get floors for the current area from the map
        const currentAreaFloors = floorsByArea.get(area.code) || [];
        for (const floor of currentAreaFloors) {
             const floorCrumblist = [...areaCrumblist, floor.name];
             const floorItem: FloorTreeNode = {
                type: 'floor',
                spaceCode: space.code,
                floorAreaCode: area.code,
                floorCode: floor.code,
                id: floor.code,
                parentId: area.code, // Floor's parent is the Area
                value: floor.code,
                name: floor.name,
                label: floor.name,
                crumblist: floorCrumblist,
                children: [], // Floors are leaf nodes here
             };
             areaItem.children.push(floorItem);
        }

        spaceStructure.children.push(areaItem);
    }

    // 7. Format the final result according to the PHP structure
    const result: SpaceTreeNode[] = [spaceStructure];
    const responseData: FloorTreeResponseData = { floorTree: result };

    return {
        code: '200',
        msg: 'success',
        data: responseData,
    };
  } 
  /**
     * Retrieves a paginated list of rooms based on specified filters.
     * Replicates the logic from getRoomList.do PHP script.
     *
     * @param params Parameters including pagination and filters.
     * @returns Promise<ApiResponse<RoomListResponseData>> Paginated list of rooms or error response.
     */
  async getRoomList(
    params: GetRoomListParams,
  ): Promise<ApiObjectResponse<RoomListResponseData>> {
      const {
          pageNo = 1, // Default to page 1 if not provided
          pageSize = 20, // Default to 20 items per page if not provided
          spaceCode,
          floorAreaCode,
          floorCode,
          title,
      } = params;

      // Basic validation for pagination parameters
      const page = Math.max(1, pageNo);
      const limit = Math.max(1, pageSize);
      const offset = (page - 1) * limit;

      // Ensure spaceCode is provided (controller should handle default/user logic)
      if (!spaceCode) {
          // This check might be redundant if the controller ensures spaceCode exists
          throw new BadRequestException('Space code is required.');
      }

      // Build the WHERE conditions for the TypeORM query
      const where: FindOptionsWhere<FloorRoom> = {
          deleteFlag: 1, // Filter for active records
          spaceCode: spaceCode, // Mandatory space filter
      };

      if (floorAreaCode) {
          // Assuming the entity property name is 'areaCode' matching the DB column
          where.areaCode = floorAreaCode;
      }
      if (floorCode) {
          where.floorCode = floorCode;
      }
      if (title) {
          // Use TypeORM's Like operator for partial matching (case-sensitive by default, depends on DB collation)
          where.name = Like(`%${title}%`);
      }

      try {
          // Use findAndCount to get both the data and the total count efficiently
          const [floorRooms, total] = await this.floorRoomRepository.findAndCount({
              where,
              order: {
                  sortOrder: 'DESC', // Order by sortOrder descending as in PHP
              },
              skip: offset, // Offset for pagination
              take: limit,  // Limit for pagination
          });

          // Map the TypeORM entities to the desired response structure
          const list: RoomListItem[] = floorRooms.map(room => ({
              id: room.id,
              code: room.code,
              name: room.name,
              sortOrder: room.sortOrder,
              spaceCode: room.spaceCode,
              // Map entity's 'areaCode' to 'floorAreaCode' for the response
              floorAreaCode: room.areaCode,
              floorCode: room.floorCode,
          }));

          const responseData: RoomListResponseData = {
              total,
              list,
          };

          return {
              code: '200',
              msg: 'success',
              data: responseData,
          };

      } catch (error) {
          console.log(`Failed to get room list for space ${spaceCode}: ${error.message}`, error.stack);
          // Re-throw the error to be handled by a global exception filter
          // This allows for consistent error response formatting
          throw error;
          // Or, if you need to return the specific format directly:
          // return { code: '500', msg: 'Failed to retrieve room list' };
      }
  }
 /**
     * Creates or updates a room record.
     * Mimics the logic expected from a doRoomEdit.do script.
     *
     * @param dto The room data transfer object containing details.
     * @param userId Optional: ID of the user performing the action (for auditing).
     * @param userName Optional: Name of the user performing the action (for auditing).
     * @returns Promise<ApiObjectResponse<RoomEditResponseData | null>> Response indicating success or failure.
     */
  async doRoomEdit(
    dto: RoomEditDto,
    userId?: string, // Pass user info if needed for create/update user fields
    userName?: string,
  ): Promise<ApiObjectResponse<RoomEditResponseData | null>> {
    const { id, code, name, sortOrder, spaceCode, floorAreaCode, floorCode } = dto;

    // --- Validation: Check if code already exists (within the same scope) ---
    const existingCodeCondition: FindOptionsWhere<FloorRoom> = {
        code: code,
        spaceCode: spaceCode,
        areaCode: floorAreaCode, // Map DTO's floorAreaCode to entity's areaCode
        floorCode: floorCode,
        deleteFlag: 1, // Only check against active rooms
        ...(id ? { id: Not(id) } : {}), // If updating, exclude the current room ID
    };

    const roomWithSameCode = await this.floorRoomRepository.findOne({ where: existingCodeCondition });

    if (roomWithSameCode) {
        console.log(`Room code conflict: Code '${code}' already exists in space '${spaceCode}', area '${floorAreaCode}', floor '${floorCode}'.`);
        throw new BadRequestException(`房间编码 '${code}' 在当前楼层已存在`);
    }

    // --- Determine Create or Update ---
    const floorOfRoom = await this.floorRepository.findOne({ where: { code: floorCode, spaceCode, deleteFlag: 1 } })
    const resolvedAreaCode = floorOfRoom?.areaCode ?? floorAreaCode
    if (id!=0) {
      // --- Update Existing Room ---
      const existingRoom = await this.floorRoomRepository.findOne({
          where: { id: id, deleteFlag: 1 } // Ensure we're updating an active room
      });

        if (!existingRoom) {
          console.log(`Room not found for update: ID '${id}'`);
         throw new BadRequestException(`无效房间信息 (ID: ${id})`);
        }

      // Prepare update data
      existingRoom.code = code;
      existingRoom.name = name;
      existingRoom.sortOrder = sortOrder ?? existingRoom.sortOrder; // Keep existing if null/undefined
      existingRoom.spaceCode = spaceCode;
      existingRoom.areaCode = resolvedAreaCode;
      existingRoom.floorCode = floorCode;
        // Add audit fields if your entity has them
        // existingRoom.updateUserId = userId;
        // existingRoom.updateUserName = userName;
        // existingRoom.updateTime = new Date();

        try {
            const updatedRoom = await this.floorRoomRepository.save(existingRoom);
            console.log(`Room updated successfully: ID ${updatedRoom.id}, Code ${updatedRoom.code}`);
            return {
                code: '200',
                msg: 'success',
                data: { id: updatedRoom.id, code: updatedRoom.code }, // Return minimal data
            };
        } catch (error) {
          console.log(`Failed to update room ID ${id}: ${error.message}`, error.stack);
            throw new BadRequestException('房间更新失败'); // Or a more specific error
        }

    } else {
      // --- Create New Room ---
      const newRoom = this.floorRoomRepository.create({
          code: code,
          name: name,
          sortOrder: sortOrder,
          spaceCode: spaceCode,
          areaCode: resolvedAreaCode,
          floorCode: floorCode,
          deleteFlag: 1, // Default to active
          // Add audit fields if your entity has them
          // createUserId: userId,
          // createUserName: userName,
          createtime: Math.floor(Date.now() / 1000).toString(), // Match PHP timestamp style if needed, otherwise use new Date()
      });

        try {
            const savedRoom = await this.floorRoomRepository.save(newRoom);
            console.log(`Room created successfully: ID ${savedRoom.id}, Code ${savedRoom.code}`);
            return {
                code: '200',
                msg: 'success',
                data: { id: savedRoom.id, code: savedRoom.code }, // Return minimal data
            };
        } catch (error) {
            console.log(`Failed to create room: ${error.message}`, error.stack);
            throw new BadRequestException('房间创建失败'); // Or a more specific error
        }
    }
  }
  async doRoomDelete(
    dto: DeteleDto,
    userId: number
  ): Promise<ObjectResponseDto> {
    const userCurrentSpace = await this.UserCurrentSpaceRepository.findOne({
      where: { userId: userId.toString() },
    });
      try {
        const { ids } = dto;
        if (!ids) {
          throw new BadRequestException('请填写完整信息');
        }
        if (!userCurrentSpace) {
          throw new BadRequestException('丢失当前空间信息');
        }
        // 根据spaceCode和floorAreaID（原区域code）查询区域
        const room = await this.floorRoomRepository.findOne({
          where: { 
            id: ids, // 确保类型匹配
            spaceCode:userCurrentSpace?.spaceCode
          }
        });

        if (!room) {
          throw new BadRequestException('无效独立房间');
        }
        // 更新区域基础信息
        await this.floorRoomRepository.update(
          { id: room.id }, // 根据ID更新
          { deleteFlag: 0 }
        );
        return {
          code: '200',
          msg: '操作成功'
        };
      } catch (error) {
        console.log(error)
        if (error instanceof BadRequestException) {
          throw error;
        }
        throw new BadRequestException('删除独立房间失败');
      }

  }
  /**
     * Retrieves a paginated list of areas based on specified filters.
     * Assumed logic based on getRoomList.do and typical requirements.
     *
     * @param params Parameters including pagination and filters (spaceCode, title).
     * @returns Promise<ApiObjectResponse<AreaListResponseData>> Paginated list of areas or error response.
     */
  async getAreaList(
      params: GetAreaListParams,
  ): Promise<ApiObjectResponse<AreaListResponseData>> {
      const {
          pageNo = 1,
          pageSize = 20,
          spaceCode,
          floorCode,
          title,
      } = params;

      // console.info(`Getting area list for spaceCode: ${spaceCode}, page: ${pageNo}, size: ${pageSize}, title: ${title}`);
      // Validate pagination
      const page = Math.max(1, pageNo);
      const limit = Math.max(1, pageSize);
      const offset = (page - 1) * limit;
      // Ensure spaceCode is provided
      if (!spaceCode) {
        // console.log('getAreaList called without spaceCode.');
          throw new BadRequestException('Space code is required.');
      }

      // Build WHERE conditions
      const where: FindOptionsWhere<FloorArea> = {
          deleteFlag: 1, // Only active areas
          floorCode: floorCode,
          spaceCode: spaceCode, // Filter by space
      };

      if (title) {
          // Use ILike for case-insensitive search (if supported and desired)
          // Otherwise, use Like for case-sensitive (depends on DB collation)
          where.name = ILike(`%${title}%`);
          // where.name = Like(`%${title}%`); // Alternative
      }

      try {
          // Fetch areas and total count
          const [areas, total] = await this.floorAreaRepository.findAndCount({
              where,
              order: {
                  sortOrder: 'ASC', // Or 'DESC' depending on requirements
                  // You might want a secondary sort key, e.g., name: 'ASC'
              },
              skip: offset,
              take: limit,
          });

          // Map entities to response DTO
          const list: AreaListItem[] = areas.map(area => ({
              id: area.id,
              code: area.code,
              name: area.name,
              sortOrder: area.sortOrder,
              spaceCode: area.spaceCode,
              // Map other fields as needed
          }));

          const responseData: AreaListResponseData = {
              total,
              list,
          };

          // console.log(`Found ${total} areas for spaceCode: ${spaceCode}`);
          return {
              code: '200',
              msg: 'success',
              data: responseData,
          };

      } catch (error) {
          console.log(`Failed to get area list for space ${spaceCode}: ${error.message}`, error.stack);
          // Re-throw for global exception filter
          throw error;
          // Or return specific error structure:
          // throw new InternalServerErrorException('Failed to retrieve area list');
      }
  }
  /**
     * Creates or updates an Area record.
     * Handles code/name changes and updates related tables.
     *
     * @param dto The area data transfer object.
     * @param userId Optional user ID for auditing.
     * @param userName Optional user name for auditing.
     * @returns Promise<ApiObjectResponse<EditResponseData | null>>
     */
  async doAreaEdit(
    dto: AreaFloorEditDto,
    userId?: string, // For potential audit fields
    userName?: string,
  ): Promise<ApiObjectResponse<EditResponseData | null>> {
    const { id, code, name, spaceCode,floorCode,floorAreaCode, sortOrder } = dto;

    console.log(`Attempting to edit area: ${dto}`,dto);

    // --- Validation: Check if code already exists within the same space ---
    const existingCodeCondition: FindOptionsWhere<FloorArea> = {
        code: code,
        floorCode:floorCode,
        areaCode:floorAreaCode,
        spaceCode: spaceCode,
        deleteFlag: 1, // Only check against active areas
        ...(id ? { id: Not(id) } : {}), // If updating, exclude the current area ID
    };

    const areaWithSameCode = await this.floorAreaRepository.findOne({ where: existingCodeCondition });

    if (areaWithSameCode) {
        console.log(`Area code conflict: Code '${code}' already exists in space '${spaceCode}'.`,code);
        throw new BadRequestException(`区域编码 '${code}' 在当前办公区域已存在`);
    }

    // --- Determine Create or Update ---
    if (id!=0) {
        // --- Update Existing Area ---
        console.log(`Updating area with ID: ${id}`);
        const existingArea = await this.floorAreaRepository.findOne({
            where: { id: id, deleteFlag: 1 } // Ensure we're updating an active area
        });

        if (!existingArea) {
            console.log(`Area not found for update: ID '${id}'`);
            throw new BadRequestException(`无效区域信息 (ID: ${id})`);
        }

        const oldCode = existingArea.code;
        const oldName = existingArea.name;

        // Prepare update data
        existingArea.code = code;
        existingArea.name = name;
        existingArea.spaceCode = spaceCode; // Should generally not change during edit, but included for completeness
        existingArea.sortOrder = sortOrder ?? existingArea.sortOrder;
        // Add audit fields if your entity has them
        // existingArea.updateUserId = userId;
        // existingArea.updateUserName = userName;
        // existingArea.updateTime = new Date();

        try {
            // --- Update Related Tables BEFORE saving the area itself ---
            // This ensures constraints or lookups use the new code/name if needed immediately after.
            // However, it's often safer to update the primary record first, then related ones.
            // Let's update related tables *after* the main save, assuming no immediate dependency.

            // Save the main area record
            const updatedArea = await this.floorAreaRepository.save(existingArea);
            console.log(`Area record updated for ID: ${id}`);

            // Update related tables if code or name changed
            if (oldCode !== code) {
                console.log(`Area code changed from ${oldCode} to ${code}. Updating related tables.`);
                await this.updateRelatedTablesForAreaCodeChange(spaceCode, oldCode, code);
            }
            if (oldName !== name) {
                console.log(`Area name changed. Updating related device names.`);
                // Pass the *new* code in case it also changed
                await this.updateRelatedTablesForAreaNameChange(spaceCode, code, name);
            }

            console.log(`Area updated successfully: ID ${updatedArea.id}, Code ${updatedArea.code}`);
            return {
                code: '200',
                msg: 'success',
                data: { id: updatedArea.id, code: updatedArea.code },
            };
        } catch (error) {
            console.log(`Failed to update area ID ${id}: ${error.message}`, error.stack);
            // Consider more specific error handling or re-throwing
            throw new BadRequestException('区域更新失败');
        }

    } else {
        // --- Create New Area ---
        console.log(`Creating new area with code: ${code}`);
        const newArea = this.floorAreaRepository.create({
            code: code,
            name: name,
            floorCode:floorCode,
            areaCode:floorAreaCode,
            spaceCode: spaceCode,
            sortOrder: sortOrder,
            deleteFlag: 1, // Default to active
            // Add audit fields if your entity has them
            // createUserId: userId,
            // createUserName: userName,
            createtime: Math.floor(Date.now() / 1000).toString(), // Or use new Date()
        });

        try {
            const savedArea = await this.floorAreaRepository.save(newArea);
            console.log(`Area created successfully: ID ${savedArea.id}, Code ${savedArea.code}`);
            return {
                code: '200',
                msg: 'success',
                data: { id: savedArea.id, code: savedArea.code },
            };
        } catch (error) {
            console.log(`Failed to create area: ${error.message}`, error.stack);
            throw new BadRequestException('区域创建失败');
        }
    }
  }
  /**
     * Helper method to update related tables when an Area's code changes.
     */
  private async updateRelatedTablesForAreaCodeChange(spaceCode: string, oldAreaCode: string, newAreaCode: string): Promise<void> {
    console.log(`Updating areaCode from ${oldAreaCode} to ${newAreaCode} in related tables for space ${spaceCode}`);
    // Update all tables that have both spaceCode and areaCode
    await Promise.all([
        this.floorRepository.update({ spaceCode, areaCode: oldAreaCode }, { areaCode: newAreaCode }),
        this.floorAreaRepository.update({ spaceCode, areaCode: oldAreaCode }, { areaCode: newAreaCode }),
        this.floorMroomRepository.update({ spaceCode, areaCode: oldAreaCode }, { areaCode: newAreaCode }),
        this.floorRoomRepository.update({ spaceCode, areaCode: oldAreaCode }, { areaCode: newAreaCode }),
        this.floorToiletRepository.update({ spaceCode, areaCode: oldAreaCode }, { areaCode: newAreaCode }),
        this.floorWorkstationRepository.update({ spaceCode, areaCode: oldAreaCode }, { areaCode: newAreaCode }),
        this.iotGatewayRepository.update({ spaceCode, areaCode: oldAreaCode }, { areaCode: newAreaCode }),
        this.iotDeviceRepository.update({ spaceCode, areaCode: oldAreaCode }, { areaCode: newAreaCode }),
        // Add any other relevant repositories here
    ]);
    console.log(`Finished updating related tables for areaCode change.`);
  }
  /**
   * Helper method to update related tables (like devices) when an Area's name changes.
   */
  private async updateRelatedTablesForAreaNameChange(spaceCode: string, areaCode: string, newAreaName: string): Promise<void> {
      console.log(`Updating areaName to ${newAreaName} in related device tables for space ${spaceCode}, area ${areaCode}`);
      // Update only tables that store the area name redundantly (typically devices)
      await Promise.all([
          this.iotGatewayRepository.update({ spaceCode, areaCode: areaCode }, { areaName: newAreaName }),
          this.iotDeviceRepository.update({ spaceCode, areaCode: areaCode }, { areaName: newAreaName }),
          // Add any other relevant repositories here
      ]);
      console.log(`Finished updating related tables for areaName change.`);
  }
  async doAreaDelete(
    dto: DeteleDto,
    userId: number
  ): Promise<ObjectResponseDto> {
    const userCurrentSpace = await this.UserCurrentSpaceRepository.findOne({
      where: { userId: userId.toString() },
    });
      try {
        const { ids } = dto;
        if (!ids) {
          throw new BadRequestException('请填写完整信息');
        }
        if (!userCurrentSpace) {
          throw new BadRequestException('丢失当前空间信息');
        }
        // 根据spaceCode和floorAreaID（原区域code）查询区域
        const floorArea = await this.floorAreaRepository.findOne({
          where: { 
            id: ids, // 确保类型匹配
            spaceCode:userCurrentSpace?.spaceCode
          }
        });

        if (!floorArea) {
          throw new BadRequestException('无效办公空间');
        }
        // 更新区域基础信息
        await this.floorAreaRepository.update(
          { id: floorArea.id }, // 根据ID更新
          { deleteFlag: 0 }
        );
        return {
          code: '200',
          msg: '操作成功'
        };
      } catch (error) {
        console.log(error)
        if (error instanceof BadRequestException) {
          throw error;
        }
        throw new BadRequestException('删除办公空间失败');
      }

  }
  /**
     * Retrieves a paginated list of public areas based on specified filters.
     * Assumed logic based on getPublicAreaList.do and typical requirements.
     *
     * @param params Parameters including pagination and filters (spaceCode, title).
     * @returns Promise<ApiObjectResponse<PublicAreaListResponseData>> Paginated list of areas or error response.
     */
  async getPublicAreaList(
    params: GetPublicAreaListParams,
  ): Promise<ApiObjectResponse<PublicAreaListResponseData>> {
      const {
          pageNo = 1,
          pageSize = 20,
          spaceCode,
          floorCode,
          title,
      } = params;

      // console.info(`Getting area list for spaceCode: ${spaceCode}, page: ${pageNo}, size: ${pageSize}, title: ${title}`);
      // Validate pagination
      const page = Math.max(1, pageNo);
      const limit = Math.max(1, pageSize);
      const offset = (page - 1) * limit;
      // Ensure spaceCode is provided
      if (!spaceCode) {
        // console.log('getAreaList called without spaceCode.');
          throw new BadRequestException('Space code is required.');
      }

      // Build WHERE conditions
      const where: FindOptionsWhere<FloorArea> = {
          deleteFlag: 1, // Only active areas
          floorCode: floorCode,
          spaceCode: spaceCode, // Filter by space
      };

      if (title) {
          // Use ILike for case-insensitive search (if supported and desired)
          // Otherwise, use Like for case-sensitive (depends on DB collation)
          where.name = ILike(`%${title}%`);
          // where.name = Like(`%${title}%`); // Alternative
      }

      try {
          // Fetch areas and total count
          const [areas, total] = await this.floorPubAreaRepository.findAndCount({
              where,
              order: {
                  sortOrder: 'ASC', // Or 'DESC' depending on requirements
                  // You might want a secondary sort key, e.g., name: 'ASC'
              },
              skip: offset,
              take: limit,
          });

          // Map entities to response DTO
          const list: PublicAreaListItem[] = areas.map(area => ({
              id: area.id,
              code: area.code,
              name: area.name,
              sortOrder: area.sortOrder,
              spaceCode: area.spaceCode,
              // Map other fields as needed
          }));

          const responseData: PublicAreaListResponseData = {
              total,
              list,
          };

          // console.log(`Found ${total} areas for spaceCode: ${spaceCode}`);
          return {
              code: '200',
              msg: 'success',
              data: responseData,
          };

      } catch (error) {
          console.log(`Failed to get area list for space ${spaceCode}: ${error.message}`, error.stack);
          // Re-throw for global exception filter
          throw error;
          // Or return specific error structure:
          // throw new InternalServerErrorException('Failed to retrieve area list');
      }
  }
  async doPublicAreaEdit(
    dto: PublicAreaEditDto,
    userId?: string, // For potential audit fields
    userName?: string,
  ): Promise<ApiObjectResponse<EditResponseData | null>> {
      const { id, code, name, spaceCode,floorCode,floorAreaCode, sortOrder } = dto;

      console.log(`Attempting to edit area: ${dto}`,dto);

      // --- Validation: Check if code already exists within the same space ---
      const existingCodeCondition: FindOptionsWhere<FloorArea> = {
          code: code,
          floorCode:floorCode,
          areaCode:floorAreaCode,
          spaceCode: spaceCode,
          deleteFlag: 1, // Only check against active areas
          ...(id ? { id: Not(id) } : {}), // If updating, exclude the current area ID
      };

      const areaWithSameCode = await this.floorPubAreaRepository.findOne({ where: existingCodeCondition });

      if (areaWithSameCode) {
          console.log(`Area code conflict: Code '${code}' already exists in space '${spaceCode}'.`,code);
          throw new BadRequestException(`区域编码 '${code}' 在当前办公区域已存在`);
      }

      // --- Determine Create or Update ---
      const floorEntity = await this.floorRepository.findOne({ where: { code: floorCode, spaceCode, deleteFlag: 1 } })
      const resolvedAreaCode = floorEntity?.areaCode ?? floorAreaCode
      if (id!=0) {
          // --- Update Existing Area ---
          console.log(`Updating area with ID: ${id}`);
          const existingArea = await this.floorPubAreaRepository.findOne({
              where: { id: id, deleteFlag: 1 } // Ensure we're updating an active area
          });

          if (!existingArea) {
              console.log(`Area not found for update: ID '${id}'`);
              throw new BadRequestException(`无效区域信息 (ID: ${id})`);
          }

          const oldCode = existingArea.code;
          const oldName = existingArea.name;

          // Prepare update data
          existingArea.code = code;
          existingArea.name = name;
          existingArea.spaceCode = spaceCode; // Should generally not change during edit, but included for completeness
          existingArea.sortOrder = sortOrder ?? existingArea.sortOrder;
          existingArea.areaCode = resolvedAreaCode;
          // Add audit fields if your entity has them
          // existingArea.updateUserId = userId;
          // existingArea.updateUserName = userName;
          // existingArea.updateTime = new Date();

          try {
              // --- Update Related Tables BEFORE saving the area itself ---
              // This ensures constraints or lookups use the new code/name if needed immediately after.
              // However, it's often safer to update the primary record first, then related ones.
              // Let's update related tables *after* the main save, assuming no immediate dependency.

              // Save the main area record
              const updatedArea = await this.floorPubAreaRepository.save(existingArea);
              console.log(`Area record updated for ID: ${id}`);

              // Update related tables if code or name changed
              if (oldCode !== code) {
                  console.log(`Area code changed from ${oldCode} to ${code}. Updating related tables.`);
                  // await this.updateRelatedTablesForAreaCodeChange(spaceCode, oldCode, code);
                  await Promise.all([
                    this.iotGatewayRepository.update({ spaceCode, floorAreaCode: oldCode }, { floorAreaCode: code }),
                    this.iotDeviceRepository.update({ spaceCode, floorAreaCode: oldCode }, { floorAreaCode: code }),
                    // Add any other relevant repositories here
                ]);
              }
              if (oldName !== name) {
                  console.log(`Area name changed. Updating related device names.`);
                  // Pass the *new* code in case it also changed
                  // await this.updateRelatedTablesForAreaNameChange(spaceCode, code, name);
                  await Promise.all([
                    this.iotGatewayRepository.update({ spaceCode, floorAreaCode: code }, { floorAreaName: name }),
                    this.iotDeviceRepository.update({ spaceCode, floorAreaCode: code }, { floorAreaName: name }),
                  ]);
              }

              console.log(`Area updated successfully: ID ${updatedArea.id}, Code ${updatedArea.code}`);
              return {
                  code: '200',
                  msg: 'success',
                  data: { id: updatedArea.id, code: updatedArea.code },
              };
          } catch (error) {
              console.log(`Failed to update area ID ${id}: ${error.message}`, error.stack);
              // Consider more specific error handling or re-throwing
              throw new BadRequestException('公共区域更新失败');
          }

      } else {
          // --- Create New Area ---
          console.log(`Creating new area with code: ${code}`);
          const newArea = this.floorPubAreaRepository.create({
              code: code,
              name: name,
              floorCode:floorCode,
              areaCode:resolvedAreaCode,
              spaceCode: spaceCode,
              sortOrder: sortOrder,
              deleteFlag: 1, // Default to active
              // Add audit fields if your entity has them
              // createUserId: userId,
              // createUserName: userName,
              createtime: Math.floor(Date.now() / 1000).toString(), // Or use new Date()
          });

          try {
              const savedArea = await this.floorPubAreaRepository.save(newArea);
              console.log(`Area created successfully: ID ${savedArea.id}, Code ${savedArea.code}`);
              return {
                  code: '200',
                  msg: 'success',
                  data: { id: savedArea.id, code: savedArea.code },
              };
          } catch (error) {
              console.log(`Failed to create area: ${error.message}`, error.stack);
              throw new BadRequestException('区域创建失败');
          }
      }
  }
  async doPublicAreaDelete(
    dto: DeteleDto,
    userId: number
  ): Promise<ObjectResponseDto> {
    const userCurrentSpace = await this.UserCurrentSpaceRepository.findOne({
      where: { userId: userId.toString() },
    });
      try {
        const { ids } = dto;
        if (!ids) {
          throw new BadRequestException('请填写完整信息');
        }
        if (!userCurrentSpace) {
          throw new BadRequestException('丢失当前空间信息');
        }
        // 根据spaceCode和floorAreaID（原区域code）查询区域
        const floorArea = await this.floorPubAreaRepository.findOne({
          where: { 
            id: ids, // 确保类型匹配
            spaceCode:userCurrentSpace?.spaceCode
          }
        });

        if (!floorArea) {
          throw new BadRequestException('无效办公空间');
        }
        // 更新区域基础信息
        await this.floorPubAreaRepository.update(
          { id: floorArea.id }, // 根据ID更新
          { deleteFlag: 0 }
        );
        return {
          code: '200',
          msg: '操作成功'
        };
      } catch (error) {
        console.log(error)
        if (error instanceof BadRequestException) {
          throw error;
        }
        throw new BadRequestException('删除办公空间失败');
      }

  }
  async getMRoomList(
    params: GetMeetingRoomListParams,
  ): Promise<ApiObjectResponse<MeetingroomListResponseData>> {
      const {
          pageNo = 1,
          pageSize = 20,
          spaceCode,
          floorCode,
          floorAreaCode,
          areaCode,
          title,
      } = params;

      // Validate pagination
      const page = Math.max(1, pageNo);
      const limit = Math.max(1, pageSize);
      const offset = (page - 1) * limit;
      
      // Ensure spaceCode is provided
      if (!spaceCode) {
          throw new BadRequestException('Space code is required.');
      }

      // Build WHERE conditions
      const where: FindOptionsWhere<FloorMroom> = {
          deleteFlag: 1, // Only active areas
          spaceCode: spaceCode, // Filter by space
      };

      // Only add these filters if they are provided and not empty strings
      if (floorCode && floorCode.trim() !== '') {
          where.floorCode = floorCode;
      }
      
      if (floorAreaCode && floorAreaCode.trim() !== '') {
          where.areaCode = floorAreaCode;
      }
      
      if (areaCode && areaCode.trim() !== '') {
          where.floorAreaCode = areaCode;
      }

      if (title) {
          where.name = ILike(`%${title}%`);
      }
      try {
          // Fetch areas and total count
          const [meetingrooms, total] = await this.floorMroomRepository.findAndCount({
              where,
              order: {
                  sortOrder: 'ASC',
              },
              skip: offset,
              take: limit,
          });

          // Map entities to response DTO with added floorCode property
          const list: MeetingroomListItem[] = meetingrooms.map(meetingroom => ({
              id: meetingroom.id,
              code: meetingroom.code,
              name: meetingroom.name,
              sortOrder: meetingroom.sortOrder,
              spaceCode: meetingroom.spaceCode,
              floorCode: meetingroom.floorCode, // Added floorCode property
              // Map other fields as needed
          }));

          const responseData: MeetingroomListResponseData = {
              total,
              list,
          };

          return {
              code: '200',
              msg: 'success',
              data: responseData,
          };

      } catch (error) {
          console.log(`Failed to get meeting room list for space ${spaceCode}: ${error.message}`, error.stack);
          throw error;
      }
  }
  async doMroomEdit(
    dto: MeetingroomEditDto,
    userId?: string, // For potential audit fields
    userName?: string,
  ): Promise<ApiObjectResponse<EditResponseData | null>> {
      const { id, code, name, spaceCode,floorCode,floorAreaCode,sortOrder } = dto;

      // console.log(`Attempting to edit area: ${dto}`,dto);

      // --- Validation: Check if code already exists within the same space ---
      const existingCodeCondition: FindOptionsWhere<FloorMroom> = {
          code: code,
          floorCode:floorCode,
          areaCode:floorAreaCode,
          spaceCode: spaceCode,
          deleteFlag: 1, // Only check against active areas
          ...(id ? { id: Not(id) } : {}), // If updating, exclude the current area ID
      };

      const areaWithSameCode = await this.floorMroomRepository.findOne({ where: existingCodeCondition });

      if (areaWithSameCode) {
          console.log(`Area code conflict: Code '${code}' already exists in space '${spaceCode}'.`,code);
          throw new BadRequestException(`区域编码 '${code}' 在当前会议室已存在`);
      }

      // --- Determine Create or Update ---
      const floorEntity = await this.floorRepository.findOne({ where: { code: floorCode, spaceCode, deleteFlag: 1 } })
      const resolvedAreaCode = floorEntity?.areaCode ?? floorAreaCode
      if (id!=0) {
          // --- Update Existing Area ---
          // console.log(`Updating area with ID: ${id}`);
          const existingMeetingroom = await this.floorMroomRepository.findOne({
              where: { id: id, deleteFlag: 1 } // Ensure we're updating an active area
          });

          if (!existingMeetingroom) {
              console.log(`Area not found for update: ID '${id}'`);
              throw new BadRequestException(`无效区域信息 (ID: ${id})`);
          }

          const oldCode = existingMeetingroom.code;
          const oldName = existingMeetingroom.name;

          // Prepare update data
          existingMeetingroom.code = code;
          existingMeetingroom.name = name;
          existingMeetingroom.spaceCode = spaceCode; // Should generally not change during edit, but included for completeness
          existingMeetingroom.sortOrder = sortOrder ?? existingMeetingroom.sortOrder;
          existingMeetingroom.areaCode = resolvedAreaCode;
          // Add audit fields if your entity has them
          // existingArea.updateUserId = userId;
          // existingArea.updateUserName = userName;
          // existingArea.updateTime = new Date();

          try {
              // --- Update Related Tables BEFORE saving the area itself ---
              // This ensures constraints or lookups use the new code/name if needed immediately after.
              // However, it's often safer to update the primary record first, then related ones.
              // Let's update related tables *after* the main save, assuming no immediate dependency.

              // Save the main area record
              const updatedMeetingroom = await this.floorMroomRepository.save(existingMeetingroom);
              // console.log(`Area record updated for ID: ${id}`);

              // Update related tables if code or name changed
              if (oldCode !== code) {
                  console.log(`Area code changed from ${oldCode} to ${code}. Updating related tables.`);
                  // await this.updateRelatedTablesForAreaCodeChange(spaceCode, oldCode, code);
                  await Promise.all([
                    this.iotGatewayRepository.update({ spaceCode, floorAreaCode: oldCode }, { floorAreaCode: code }),
                    this.iotDeviceRepository.update({ spaceCode, floorAreaCode: oldCode }, { floorAreaCode: code }),
                    // Add any other relevant repositories here
                ]);
              }
              if (oldName !== name) {
                  console.log(`Area name changed. Updating related device names.`);
                  // Pass the *new* code in case it also changed
                  // await this.updateRelatedTablesForAreaNameChange(spaceCode, code, name);
                  await Promise.all([
                    this.iotGatewayRepository.update({ spaceCode, floorAreaCode: code }, { floorAreaName: name }),
                    this.iotDeviceRepository.update({ spaceCode, floorAreaCode: code }, { floorAreaName: name }),
                  ]);
              }

              console.log(`Area updated successfully: ID ${updatedMeetingroom.id}, Code ${updatedMeetingroom.code}`);
              return {
                  code: '200',
                  msg: 'success',
                  data: { id: updatedMeetingroom.id, code: updatedMeetingroom.code },
              };
          } catch (error) {
              console.log(`Failed to update area ID ${id}: ${error.message}`, error.stack);
              // Consider more specific error handling or re-throwing
              throw new BadRequestException('会议室更新失败');
          }

      } else {
          // --- Create New Area ---
          console.log(`Creating new area with code: ${code}`);
          const newMeetingroom = this.floorMroomRepository.create({
              code: code,
              name: name,
              floorCode:floorCode,
              areaCode:resolvedAreaCode,
              spaceCode: spaceCode,
              sortOrder: sortOrder,
              deleteFlag: 1, // Default to active
              // Add audit fields if your entity has them
              // createUserId: userId,
              // createUserName: userName,
              createtime: Math.floor(Date.now() / 1000).toString(), // Or use new Date()
          });

          try {
              const savedMeetingroom = await this.floorMroomRepository.save(newMeetingroom);
              console.log(`MeeringRoom created successfully: ID ${savedMeetingroom.id}, Code ${savedMeetingroom.code}`);
              return {
                  code: '200',
                  msg: 'success',
                  data: { id: savedMeetingroom.id, code: savedMeetingroom.code },
              };
          } catch (error) {
              console.log(`Failed to create Meetingroom: ${error.message}`, error.stack);
              throw new BadRequestException('会议室创建失败');
          }
      }
  }
  async doMroomDelete(
    dto: DeteleDto,
    userId: number
  ): Promise<ObjectResponseDto> {
    const userCurrentSpace = await this.UserCurrentSpaceRepository.findOne({
      where: { userId: userId.toString() },
    });
      try {
        const { ids } = dto;
        if (!ids) {
          throw new BadRequestException('请填写完整信息');
        }
        if (!userCurrentSpace) {
          throw new BadRequestException('丢失当前空间信息');
        }
        // 根据spaceCode和floorAreaID（原区域code）查询区域
        const meetingroom = await this.floorMroomRepository.findOne({
          where: { 
            id: ids, // 确保类型匹配
            spaceCode:userCurrentSpace?.spaceCode
          }
        });

        if (!meetingroom) {
          throw new BadRequestException('无效办公空间');
        }
        // 更新区域基础信息
        await this.floorMroomRepository.update(
          { id: meetingroom.id }, // 根据ID更新
          { deleteFlag: 0 }
        );
        return {
          code: '200',
          msg: '操作成功'
        };
      } catch (error) {
        console.log(error)
        if (error instanceof BadRequestException) {
          throw error;
        }
        throw new BadRequestException('删除会议室失败');
      }
  }
  async getToiletList(
    params: GetToiletListParams,
  ): Promise<ApiObjectResponse<ToiletListResponseData>> {
      const {
          pageNo = 1,
          pageSize = 20,
          spaceCode,
          floorCode,
          title,
      } = params;

      // console.info(`Getting toilet list for spaceCode: ${spaceCode}, page: ${pageNo}, size: ${pageSize}, title: ${title}`);
      // Validate pagination
      const page = Math.max(1, pageNo);
      const limit = Math.max(1, pageSize);
      const offset = (page - 1) * limit;
      // Ensure spaceCode is provided
      if (!spaceCode) {
        // console.log('getAreaList called without spaceCode.');
          throw new BadRequestException('Space code is required.');
      }

      // Build WHERE conditions
      const where: FindOptionsWhere<FloorToilet> = {
          deleteFlag: 1, // Only active areas
          floorCode: floorCode,
          spaceCode: spaceCode, // Filter by space
      };

      if (title) {
          // Use ILike for case-insensitive search (if supported and desired)
          // Otherwise, use Like for case-sensitive (depends on DB collation)
          where.name = ILike(`%${title}%`);
          // where.name = Like(`%${title}%`); // Alternative
      }

      try {
          // Fetch areas and total count
          const [toilets, total] = await this.floorToiletRepository.findAndCount({
              where,
              order: {
                  sortOrder: 'ASC', // Or 'DESC' depending on requirements
                  // You might want a secondary sort key, e.g., name: 'ASC'
              },
              skip: offset,
              take: limit,
          });
       
          // Map entities to response DTO
          const list: MeetingroomListItem[] = toilets.map(toilet => ({
              id: toilet.id,
              code: toilet.code,
              name: toilet.name,
              type: toilet.type,
              sortOrder: toilet.sortOrder,
              spaceCode: toilet.spaceCode,
              rooms:[{
                type:1
              },{
                type:2
              },{
                type:3
              }
            ]

              // Map other fields as needed
          }));

          const responseData: MeetingroomListResponseData = {
              total,
              list,
          };

          // console.log(`Found ${total} areas for spaceCode: ${spaceCode}`);
          return {
              code: '200',
              msg: 'success',
              data: responseData,
          };

      } catch (error) {
          console.log(`Failed to get area list for space ${spaceCode}: ${error.message}`, error.stack);
          // Re-throw for global exception filter
          throw error;
          // Or return specific error structure:
          // throw new InternalServerErrorException('Failed to retrieve toilet list');
      }
  }
  async doToiletEdit(
    dto: ToiletEditDto,
    userId?: string, // For potential audit fields
    userName?: string,
  ): Promise<ApiObjectResponse<EditResponseData | null>> {
      const { id, code, name, spaceCode,floorCode,floorAreaCode,sortOrder,type } = dto;

      console.log(`Attempting to edit Toilet: ${dto}`,dto);

      // --- Validation: Check if code already exists within the same space ---
      const existingCodeCondition: FindOptionsWhere<FloorToilet> = {
          code: code,
          floorCode:floorCode,
          areaCode:floorAreaCode,
          spaceCode: spaceCode,
          deleteFlag: 1, // Only check against active areas
          ...(id ? { id: Not(id) } : {}), // If updating, exclude the current area ID
      };

      const toilettoiletWithSameCode = await this.floorToiletRepository.findOne({ where: existingCodeCondition });

      if (toilettoiletWithSameCode) {
          console.log(`Area code conflict: Code '${code}' already exists in space '${spaceCode}'.`,code);
          throw new BadRequestException(`区域编码 '${code}' 在当前卫生间已存在`);
      }

      // --- Determine Create or Update ---
      const floorEntity = await this.floorRepository.findOne({ where: { code: floorCode, spaceCode, deleteFlag: 1 } })
      const resolvedAreaCode = floorEntity?.areaCode ?? floorAreaCode
      if (id!=0) {
          // --- Update Existing Toilet ---
          console.log(`Updating tolite with ID: ${id}`);
          const existingToilet = await this.floorToiletRepository.findOne({
              where: { id: id, deleteFlag: 1 } // Ensure we're updating an active area
          });

          if (!existingToilet) {
              console.log(`Area not found for update: ID '${id}'`);
              throw new BadRequestException(`无效区域信息 (ID: ${id})`);
          }

          const oldCode = existingToilet.code;
          const oldName = existingToilet.name;

          // Prepare update data
          existingToilet.code = code;
          existingToilet.name = name;
          existingToilet.type = type;
          existingToilet.spaceCode = spaceCode; // Should generally not change during edit, but included for completeness
          existingToilet.sortOrder = sortOrder ?? existingToilet.sortOrder;
          existingToilet.areaCode = resolvedAreaCode;
          // Add audit fields if your entity has them
          // existingArea.updateUserId = userId;
          // existingArea.updateUserName = userName;
          // existingArea.updateTime = new Date();

          try {
              // --- Update Related Tables BEFORE saving the area itself ---
              // This ensures constraints or lookups use the new code/name if needed immediately after.
              // However, it's often safer to update the primary record first, then related ones.
              // Let's update related tables *after* the main save, assuming no immediate dependency.

              // Save the main area record
              const updatedToilet = await this.floorToiletRepository.save(existingToilet);
              console.log(`Toilet record updated for ID: ${id}`);

              // Update related tables if code or name changed
              if (oldCode !== code) {
                  console.log(`Area code changed from ${oldCode} to ${code}. Updating related tables.`);
                  // await this.updateRelatedTablesForAreaCodeChange(spaceCode, oldCode, code);
                  await Promise.all([
                    this.iotGatewayRepository.update({ spaceCode, floorAreaCode: oldCode }, { floorAreaCode: code }),
                    this.iotDeviceRepository.update({ spaceCode, floorAreaCode: oldCode }, { floorAreaCode: code }),
                    // Add any other relevant repositories here
                ]);
              }
              if (oldName !== name) {
                  console.log(`Area name changed. Updating related device names.`);
                  // Pass the *new* code in case it also changed
                  // await this.updateRelatedTablesForAreaNameChange(spaceCode, code, name);
                  await Promise.all([
                    this.iotGatewayRepository.update({ spaceCode, floorAreaCode: code }, { floorAreaName: name }),
                    this.iotDeviceRepository.update({ spaceCode, floorAreaCode: code }, { floorAreaName: name }),
                  ]);
              }

              console.log(`Toilet updated successfully: ID ${existingToilet.id}, Code ${existingToilet.code}`);
              return {
                  code: '200',
                  msg: 'success',
                  data: { id: existingToilet.id, code: existingToilet.code },
              };
          } catch (error) {
              console.log(`Failed to update Toilet ID ${id}: ${error.message}`, error.stack);
              // Consider more specific error handling or re-throwing
              throw new BadRequestException('卫生间更新失败');
          }

      } else {
          // --- Create New Area ---
          console.log(`Creating new Toilet with code: ${code}`);
          const newToilet = this.floorToiletRepository.create({
              code: code,
              name: name,
              floorCode:floorCode,
              areaCode:resolvedAreaCode,
              spaceCode: spaceCode,
              sortOrder: sortOrder,
              type:type,
              deleteFlag: 1, // Default to active
              // Add audit fields if your entity has them
              // createUserId: userId,
              // createUserName: userName,
              createtime: Math.floor(Date.now() / 1000).toString(), // Or use new Date()
          });

          try {
              const savedToilet = await this.floorToiletRepository.save(newToilet);
              console.log(`Toilet created successfully: ID ${savedToilet.id}, Code ${savedToilet.code}`);
              return {
                  code: '200',
                  msg: 'success',
                  data: { id: savedToilet.id, code: savedToilet.code },
              };
          } catch (error) {
              console.log(`Failed to create Toilet: ${error.message}`, error.stack);
              throw new BadRequestException('卫生间创建失败');
          }
      }
  }
  async doToiletDelete(
    dto: DeteleDto,
    userId: number
  ): Promise<ObjectResponseDto> {
    const userCurrentSpace = await this.UserCurrentSpaceRepository.findOne({
      where: { userId: userId.toString() },
    });
      try {
        const { ids } = dto;
        if (!ids) {
          throw new BadRequestException('请填写完整信息');
        }
        if (!userCurrentSpace) {
          throw new BadRequestException('丢失当前空间信息');
        }
        // 根据spaceCode和floorAreaID（原区域code）查询区域
        const toilet = await this.floorToiletRepository.findOne({
          where: { 
            id: ids, // 确保类型匹配
            spaceCode:userCurrentSpace?.spaceCode
          }
        });

        if (!toilet) {
          throw new BadRequestException('无效办公空间');
        }
        // 更新区域基础信息
        await this.floorToiletRepository.update(
          { id: toilet.id }, // 根据ID更新
          { deleteFlag: 0 }
        );
        return {
          code: '200',
          msg: '操作成功'
        };
      } catch (error) {
        console.log(error)
        if (error instanceof BadRequestException) {
          throw error;
        }
        throw new BadRequestException('删除卫生间失败');
      }
  }


  // getToiletRoomList?toiletId=2
  async getToiletRoomList(
    params: GetToiletRoomListParams,
  ): Promise<ApiObjectResponse<ToiletRoomListResponseData>> {
      const {
        toiletId = 1,
      } = params;

     try {
          const [toiletrooms, total] = await this.floorToiletRoomRepository.findAndCount({
              where:{
                toiletId:toiletId.toString(),
              },
              order: {
                  sortOrder: 'ASC', // Or 'DESC' depending on requirements
              },
          });
          const list: ToiletRoomListItem[] = toiletrooms.map(toiletroom => ({
              id: toiletroom.id,
              toiletId:toiletroom.toiletId.toString(),
              code: toiletroom.code,
              name: toiletroom.name,
              type: toiletroom.type,
              sensorIndex:toiletroom.sensorIndex.toString(),
              sortOrder: toiletroom.sortOrder.toString(),
          }));
          const responseData: ToiletRoomListResponseData = {
              total,
              list,
          };

          return {
              code: '200',
              msg: 'success',
              data: responseData,
          };

      } catch (error) {
          throw error;
      }

  }


  // doToiletRoomEdit
  // code: "21"
  // id: ""
  // name: "121"
  // sensorIndex: "212"
  // sortOrder: 1
  // toiletId: 3
  // type: "0"
  async doToiletRoomEdit(
    dto: ToiletRoomEditDto,
    userId?: string, // For potential audit fields
    userName?: string,
  ): Promise<ApiObjectResponse<EditResponseData | null>> {
    const { id, code, name, toiletId,sensorIndex,sortOrder,type } = dto;
    const existingCodeCondition: FindOptionsWhere<FloorToiletRoom> = {
      code: code,
      toiletId:toiletId.toString(),
      type:type,
      ...(id ? { id: Not(id) } : {}), // If updating, exclude the current toiletroom ID
    };
    const toiletroomWithSameCode = await this.floorToiletRoomRepository.findOne({ where: existingCodeCondition });

    if (toiletroomWithSameCode) {
        throw new BadRequestException(`区域编码 '${code}' 在当前卫生间厕位已存在`);
    }
      // --- Determine Create or Update ---
      if (id!=0) {
        // --- Update Existing Toilet ---
        console.log(`Updating tolite with ID: ${id}`);
        const existingToiletRoom = await this.floorToiletRoomRepository.findOne({
            where: { id: id} // Ensure we're updating an active area
        });

        if (!existingToiletRoom) {
            console.log(`Area not found for update: ID '${id}'`);
            throw new BadRequestException(`无效厕位信息 (ID: ${id})`);
        }

        
  // doToiletRoomEdit
  // code: "21"
  // id: ""
  // name: "121"
  // sensorIndex: "212"
  // sortOrder: 1
  // toiletId: 3
  // type: "0"
        existingToiletRoom.code = code;
        existingToiletRoom.name = name;
        existingToiletRoom.type = type;
        existingToiletRoom.toiletId = toiletId.toString();
        existingToiletRoom.sensorIndex = Number(sensorIndex);
        existingToiletRoom.sortOrder = Number(sortOrder) ?? existingToiletRoom.sortOrder;

        try {
            // Save the main area record
            const updatedToilet = await this.floorToiletRoomRepository.save(existingToiletRoom);
            console.log(`ToiletRoom record updated for ID: ${id}`);
            return {
                code: '200',
                msg: 'success',
                data: { id: updatedToilet.id, code: updatedToilet.code },
            };
        } catch (error) {
            console.log(`Failed to update Toilet ID ${id}: ${error.message}`, error.stack);
            throw new BadRequestException('卫生间更新失败');
        }

    } else {
        // --- Create New Area ---
        console.log(`Creating new ToiletRoom with code: ${code}`);
        const newToiletRoom = this.floorToiletRoomRepository.create({
            code: code,
            name: name,
            type:type,
            toiletId:toiletId.toString(),
            sensorIndex:Number(sensorIndex),
            sortOrder: Number(sortOrder),
            createtime: Math.floor(Date.now() / 1000).toString(), // Or use new Date()
        });

        try {
            const savedToiletRoom = await this.floorToiletRoomRepository.save(newToiletRoom);
            console.log(`Toilet created successfully: ID ${savedToiletRoom.id}, Code ${savedToiletRoom.code}`);
            return {
                code: '200',
                msg: 'success',
                data: { id: savedToiletRoom.id, code: savedToiletRoom.code },
            };
        } catch (error) {
            console.log(`Failed to create ToiletRoom: ${error.message}`, error.stack);
            throw new BadRequestException('卫生间厕位创建失败');
        }
    }
  }

  
  async doToiletRoomDelete(
    dto: DeteleDto,
    userId: number
  ): Promise<ObjectResponseDto> {
      try {
        const { ids } = dto;
        if (!ids) {
          throw new BadRequestException('请填写完整信息');
        }
        // 根据spaceCode和floorAreaID（原区域code）查询区域
        const toiletroom = await this.floorToiletRoomRepository.findOne({
          where: { 
            id: ids, // 确保类型匹配
          }
        });
        if (!toiletroom) {
          throw new BadRequestException('无效厕位');
        }
        // 更新区域基础信息
        await this.floorToiletRoomRepository.delete(
          { id: toiletroom.id }, // 根据ID删除
        );
        return {
          code: '200',
          msg: '操作成功'
        };
      } catch (error) {
        console.log(error)
        if (error instanceof BadRequestException) {
          throw error;
        }
        throw new BadRequestException('删除卫生间厕位失败');
      }
  }




// 在 SpaceService 类中添加以下方法
/**
 * 获取空间树结构
 * 参考 PHP 脚本 spaceManagement/getTree.do
 */
async getTree(
  user: any = null, // 设置默认值为 null
  params: GetSpaceTreeRequestDto | { spaceCode: string }, // 接受简单对象或DTO
): Promise<SpaceTreeResponseDto> {
  try {
    // 获取空间编码，优先使用请求中的
    let spaceCode = params.spaceCode;
    
    // 只有在有用户信息且没有提供 spaceCode 时才尝试获取用户默认空间
    if (!spaceCode && user && user.userId) {
      const userCurrentSpace = await this.UserCurrentSpaceRepository.findOne({
        where: { userId: user.userId }
      });
      spaceCode = userCurrentSpace?.spaceCode;
    }
    // console.log(`getTree spaceCode: ${spaceCode}`);
    // console.log(`getTree user: ${JSON.stringify(user)}`);
    this.logger.log(`getTree spaceCode: ${spaceCode}`);
    this.logger.log(`getTree user: ${JSON.stringify(user)}`);
    
    // 如果仍然没有spaceCode，返回错误
    if (!spaceCode) {
      return {
        code: '400',
        msg: '请指定空间编码'
      };
    }

    // 验证空间是否存在
    const space = await this.spaceRepository.findOne({
      where: { code: spaceCode, deleteFlag: 1 }
    });

    if (!space) {
      return {
        code: '400',
        msg: '无效空间'
      };
    }

    // 构建空间树结构
    const spaceStructure: SpaceTreeNodeDto = {
      type: 'space',
      spaceCode: space.code,
      id: space.code,
      value: space.code,
      name: space.name,
      label: space.name,
      children: [],
      crumblist: [space.name]
    };

    // 获取并构建区域
    await this.buildSpaceAreas(space.code, spaceStructure.children, spaceStructure.crumblist);
    
    // 获取不属于任何区域的楼层（areaCode='' 或 areaCode='0'）
    const floorsWithoutArea = await this.floorRepository.find({
      where: [
        { spaceCode, areaCode: '', deleteFlag: 1 },
        { spaceCode, areaCode: '0', deleteFlag: 1 }
      ],
      order: { sortOrder: 'ASC' }
    });

    // 构建不属于任何区域的楼层节点，直接添加到空间的子节点中
    for (const floor of floorsWithoutArea) {
      const floorCrumblist = [...spaceStructure.crumblist, floor.name];
      const floorItem: FloorTreeNodeDto = {
        type: 'floor',
        spaceCode,
        floorAreaCode: '',
        floorCode: floor.code,
        id: floor.code,
        parentId: space.code, // 楼层的父节点是空间
        value: floor.code,
        name: floor.name,
        label: floor.name,
        children: [],
        crumblist: floorCrumblist
      };

      // 递归构建楼层下的各种区域
      await this.buildSpaceAreaFloorAreas(spaceCode, '', floor.code, floorItem.children as any, floorCrumblist);
      await this.buildSpaceAreaFloorRooms(spaceCode, '', floor.code, floorItem.children as any, floorCrumblist);
      await this.buildSpaceAreaFloorPubAreas(spaceCode, '', floor.code, floorItem.children as any, floorCrumblist);
      await this.buildSpaceAreaFloorMrooms(spaceCode, '', floor.code, floorItem.children as any, floorCrumblist);
      await this.buildSpaceAreaFloorToilets(spaceCode, '', floor.code, floorItem.children as any, floorCrumblist);
      
      // 添加到空间的子节点
      spaceStructure.children.push(floorItem as any);
    }

    // 根据用户权限过滤空间树
    let filteredSpaceTree = spaceStructure;
    
    // 只有当有用户信息时才进行权限过滤
    if (user && user.userId) {
      // 检查用户是否有系统角色
      // const userRoles = await this.userRoleRepository.find({
      //   where: { userId: user.userId.toString() }
      // });
      
      // // 获取用户的角色代码
      // const userRoleCodes = userRoles.map(role => role.roleCode);

      // 检查是否是管理员
      const isAdmin = user.roles.includes('Admin');
      
      // 如果不是管理员，则根据权限过滤空间树
      if (!isAdmin) {
        // 获取用户有权限的空间区域
        const permittedAreas = await this.checkUserSpacePermission(user.userId, spaceCode);
        // console.log(`用户 ${user.userId} 在空间 ${spaceCode} 有权限的区域数量: ${permittedAreas.length}`);
        
        if (permittedAreas.length > 0) {
          filteredSpaceTree = this.filterTreeByPermission(spaceStructure, permittedAreas, `/${spaceCode}`);
          
          // 如果过滤后没有任何节点，返回原始空间但没有子节点
          if (!filteredSpaceTree) {
            filteredSpaceTree = {
              ...spaceStructure,
              children: []
            };
          }
        } else {
          // 如果没有任何权限区域，返回空的子节点
          filteredSpaceTree = {
            ...spaceStructure,
            children: []
          };
        }
      }
    }

    // 返回结果
    return {
      code: '200',
      msg: 'success',
      data: {
        spacetree: [filteredSpaceTree]
      }
    };
  } catch (error) {
    console.log(`获取空间树失败: ${error.message}`, error.stack);
    return {
      code: '500',
      msg: `获取空间树失败: ${error.message}`
    };
  }
}

/**
 * 获取新空间树结构
 * 参考 PHP 脚本 spaceManagement/getNewTree.do
 */
async getNewTree(
  user: any,
  dto: GetNewTreeRequestDto,
): Promise<NewTreeResponseDto> {
  try {
    // 获取空间编码，优先使用请求中的，否则使用用户默认的
    let spaceCode = dto.spaceCode;
    if (!spaceCode) {
      const userCurrentSpace = await this.UserCurrentSpaceRepository.findOne({
        where: { userId: user.userId }
      });
      spaceCode = userCurrentSpace?.spaceCode;
    }

    // 如果仍然没有spaceCode，返回错误
    if (!spaceCode) {
      return {
        code: '400',
        msg: '请指定空间编码',
        data: { spacetree: [] }
      };
    }

    // 验证空间是否存在
    const space = await this.spaceRepository.findOne({
      where: { code: spaceCode, deleteFlag: 1 }
    });

    if (!space) {
      return {
        code: '400',
        msg: '无效空间',
        data: { spacetree: [] }
      };
    }

    // 构建空间树结构
    const spaceStructure: SpaceTreeNodeDto = {
      type: 'space',
      spaceCode: space.code,
      id: space.code,
      value: space.code,
      name: space.name,
      label: space.name,
      children: [],
      crumblist: [space.name]
    };

    // 获取并构建区域
    await this.buildSpaceAreas(space.code, spaceStructure.children, spaceStructure.crumblist);
    
    // 返回结果
    return {
      code: '200',
      msg: 'success',
      data: {
        spacetree: [spaceStructure]
      }
    };
  } catch (error) {
    console.log(`获取新空间树结构失败: ${error.message}`, error.stack);
    throw new HttpException(
      { code: '400', msg: `获取失败: ${error.message}` },
      HttpStatus.BAD_REQUEST,
    );
  }
}


/**
 * 获取空间树结构
 * 参考 PHP 脚本 spaceManagement/getSpaceAreas.do
 */
async getSpaceAreas(spaceCode: string): Promise<SpaceTreeNodeDto[]> {
  try {
    // 验证空间是否存在
    const space = await this.spaceRepository.findOne({
      where: { code: spaceCode, deleteFlag: 1 }
    });

    if (!space) {
      throw new BadRequestException('无效空间');
    }

    // 构建空间树结构
    const spaceStructure: SpaceTreeNodeDto = {
      type: 'space',
      spaceCode: space.code,
      id: space.code,
      value: space.code,
      name: space.name,
      label: space.name,
      children: [],
      crumblist: [space.name]
    };

    // 获取并构建区域
    await this.buildSpaceAreas(space.code, spaceStructure.children, spaceStructure.crumblist);
    
    // 返回结果
    return [spaceStructure];
  } catch (error) {
    if (error instanceof BadRequestException) {
      throw error;
    }
    throw new BadRequestException(`获取空间树结构失败: ${error.message}`);
  }
}

/**
 * 构建空间区域
 */
private async buildSpaceAreas(
  spaceCode: string, 
  children: FloorAreaTreeNodeDto[], 
  crumblist: string[]
): Promise<void> {
  // 获取区域列表
  const areas = await this.areaRepository.find({
    where: { spaceCode, deleteFlag: 1 },
    order: { sortOrder: 'ASC' }
  });

  // 构建每个区域节点
  for (const area of areas) {
    const item: FloorAreaTreeNodeDto = {
      type: 'floorArea',
      spaceCode,
      floorAreaCode: area.code,
      id: area.code,
      parentId: spaceCode,
      value: area.code,
      name: area.name,
      label: area.name,
      children: [],
      crumblist: [...crumblist, area.name]
    };

    // 递归构建楼层
    await this.buildSpaceAreaFloors(spaceCode, area.code, item.children, item.crumblist);
    
    // 添加到父节点
    children.push(item);
  }
}

/**
 * 构建区域楼层
 */
private async buildSpaceAreaFloors(
  spaceCode: string, 
  areaCode: string, 
  children: FloorTreeNodeDto[], 
  crumblist: string[]
): Promise<void> {
  // 获取楼层列表
  const floors = await this.floorRepository.find({
    where: { spaceCode, areaCode, deleteFlag: 1 },
    order: { sortOrder: 'ASC' }
  });

  // 构建每个楼层节点
  for (const floor of floors) {
    const item: FloorTreeNodeDto = {
      type: 'floor',
      spaceCode,
      floorAreaCode: areaCode,
      floorCode: floor.code,
      id: floor.code,
      parentId: areaCode,
      value: floor.code,
      name: floor.name,
      label: floor.name,
      children: [],
      crumblist: [...crumblist, floor.name]
    };

    // 递归构建楼层下的各种区域
    await this.buildSpaceAreaFloorAreas(spaceCode, areaCode, floor.code, item.children as any, item.crumblist);
    await this.buildSpaceAreaFloorRooms(spaceCode, areaCode, floor.code, item.children as any, item.crumblist);
    await this.buildSpaceAreaFloorPubAreas(spaceCode, areaCode, floor.code, item.children as any, item.crumblist);
    await this.buildSpaceAreaFloorMrooms(spaceCode, areaCode, floor.code, item.children as any, item.crumblist);
    await this.buildSpaceAreaFloorToilets(spaceCode, areaCode, floor.code, item.children as any, item.crumblist);
    
    // 添加到父节点
    children.push(item);
  }
}

/**
 * 构建楼层区域
 */
private async buildSpaceAreaFloorAreas(
  spaceCode: string, 
  areaCode: string, 
  floorCode: string, 
  children: AreaTreeNodeDto[], 
  crumblist: string[]
): Promise<void> {
  // 获取楼层区域列表
  const floorAreas = await this.floorAreaRepository.find({
    where: { spaceCode, areaCode, floorCode, deleteFlag: 1 },
    order: { sortOrder: 'ASC' }
  });

  // 构建每个楼层区域节点
  for (const floorArea of floorAreas) {
    const item: AreaTreeNodeDto = {
      type: 'area',
      spaceCode,
      floorAreaCode: areaCode,
      floorCode,
      areaType: 'area',
      areaCode: floorArea.code,
      id: floorArea.code,
      parentId: floorCode,
      value: floorArea.code,
      name: floorArea.name,
      label: floorArea.name,
      children: [],
      crumblist: [...crumblist, floorArea.name]
    };
    
    // 添加到父节点
    children.push(item);
  }
}

/**
 * 构建楼层房间
 */
private async buildSpaceAreaFloorRooms(
  spaceCode: string, 
  areaCode: string, 
  floorCode: string, 
  children: RoomTreeNodeDto[], 
  crumblist: string[]
): Promise<void> {
  // 获取楼层房间列表
  const floorRooms = await this.floorRoomRepository.find({
    where: { spaceCode, areaCode, floorCode, deleteFlag: 1 },
    order: { sortOrder: 'ASC' }
  });

  // 构建每个楼层房间节点
  for (const floorRoom of floorRooms) {
    const item: RoomTreeNodeDto = {
      type: 'room',
      spaceCode,
      floorAreaCode: areaCode,
      floorCode,
      areaType: 'room',
      areaCode: floorRoom.code,
      id: floorRoom.code,
      parentId: floorCode,
      value: floorRoom.code,
      name: floorRoom.name,
      label: floorRoom.name,
      children: [],
      crumblist: [...crumblist, floorRoom.name]
    };
    
    // 添加到父节点
    children.push(item);
  }
}

/**
 * 构建楼层公共区域
 */
private async buildSpaceAreaFloorPubAreas(
  spaceCode: string, 
  areaCode: string, 
  floorCode: string, 
  children: PubAreaTreeNodeDto[], 
  crumblist: string[]
): Promise<void> {
  // 获取楼层公共区域列表
  const floorPubAreas = await this.floorPubAreaRepository.find({
    where: { spaceCode, areaCode, floorCode, deleteFlag: 1 },
    order: { sortOrder: 'ASC' }
  });

  // 构建每个楼层公共区域节点
  for (const floorPubArea of floorPubAreas) {
    const item: PubAreaTreeNodeDto = {
      type: 'pubArea',
      spaceCode,
      floorAreaCode: areaCode,
      floorCode,
      areaType: 'pubArea',
      areaCode: floorPubArea.code,
      id: floorPubArea.code,
      parentId: floorCode,
      value: floorPubArea.code,
      name: floorPubArea.name,
      label: floorPubArea.name,
      children: [],
      crumblist: [...crumblist, floorPubArea.name]
    };
    
    // 添加到父节点
    children.push(item);
  }
}

/**
 * 构建楼层会议室
 */
private async buildSpaceAreaFloorMrooms(
  spaceCode: string, 
  areaCode: string, 
  floorCode: string, 
  children: MroomTreeNodeDto[], 
  crumblist: string[]
): Promise<void> {
  // 获取楼层会议室列表
  const floorMrooms = await this.floorMroomRepository.find({
    where: { spaceCode, areaCode, floorCode, deleteFlag: 1 },
    order: { sortOrder: 'ASC' }
  });

  // 构建每个楼层会议室节点
  for (const floorMroom of floorMrooms) {
    const item: MroomTreeNodeDto = {
      type: 'mroom',
      spaceCode,
      floorAreaCode: areaCode,
      floorCode,
      areaType: 'mroom',
      areaCode: floorMroom.code,
      id: floorMroom.code,
      parentId: floorCode,
      value: floorMroom.code,
      name: floorMroom.name,
      label: floorMroom.name,
      children: [],
      crumblist: [...crumblist, floorMroom.name]
    };
    
    // 添加到父节点
    children.push(item);
  }
}

/**
 * 构建楼层卫生间
 */
private async buildSpaceAreaFloorToilets(
  spaceCode: string, 
  areaCode: string, 
  floorCode: string, 
  children: ToiletTreeNodeDto[], 
  crumblist: string[]
): Promise<void> {
  // 获取楼层卫生间列表
  const floorToilets = await this.floorToiletRepository.find({
    where: { spaceCode, areaCode, floorCode, deleteFlag: 1 },
    order: { sortOrder: 'ASC' }
  });

  // 构建每个楼层卫生间节点
  for (const floorToilet of floorToilets) {
    const item: ToiletTreeNodeDto = {
      type: 'toilet',
      spaceCode,
      floorAreaCode: areaCode,
      floorCode,
      areaType: 'toilet',
      areaCode: floorToilet.code,
      id: floorToilet.code,
      parentId: floorCode,
      value: floorToilet.code,
      name: floorToilet.name,
      label: floorToilet.name,
      children: [],
      crumblist: [...crumblist, floorToilet.name]
    };
    
    // 添加到父节点
    children.push(item);
  }
}

/**
 * 检查用户空间权限
 * @param userId 用户ID
 * @param spaceCode 空间编码
 * @returns 用户有权限的区域信息数组
 */
private async checkUserSpacePermission(userId: number, spaceCode: string): Promise<any[]> {
  try {
    // 1. 查询用户信息
    const user = await this.userRepository.findOne({
      where: { userId, deleteFlag: 1 }
    });
    
    if (!user) {
      console.log(`用户不存在: userId=${userId}`);
      return [];
    }

    // console.log(`检查用户权限: userId=${userId}, orgId=${user.orgId}, departmentId=${user.departmentId}`);
    
    const permittedAreas: any[] = [];

    // 2. 检查用户个人权限
    const userSpaceRoles = await this.spaceRoleRepository.find({
      where: {
        roleType: 'user',
        roleId: user.userId.toString()
      }
    });
    
    // console.log(`用户个人权限: 找到 ${userSpaceRoles.length} 条记录`);
    
    // 收集用户个人权限区域
    for (const role of userSpaceRoles) {
      try {
        const roleAreas = JSON.parse(role.roleArea || '[]');
        // console.log(`用户个人权限区域: ${JSON.stringify(roleAreas)}`);
        
        // 只保留与请求的 spaceCode 匹配的权限
        const filteredAreas = roleAreas.filter(area => area.spaceCode === spaceCode);
        // console.log(`过滤后的用户个人权限区域: ${JSON.stringify(filteredAreas)}`);
        
        permittedAreas.push(...filteredAreas);
      } catch (e) {
        console.log(`解析用户权限失败: ${e.message}`);
      }
    }

    // 3. 检查用户部门权限
    if (user.departmentId) {
      const departmentSpaceRoles = await this.spaceRoleRepository.find({
        where: {
          roleType: 'department',
          roleId: user.departmentId.toString()
        }
      });
      
      // console.log(`用户部门权限: 找到 ${departmentSpaceRoles.length} 条记录`);
      
      for (const role of departmentSpaceRoles) {
        try {
          const roleAreas = JSON.parse(role.roleArea || '[]');
          // console.log(`用户部门权限区域: ${JSON.stringify(roleAreas)}`);
          
          // 只保留与请求的 spaceCode 匹配的权限
          const filteredAreas = roleAreas.filter(area => area.spaceCode === spaceCode);
          // console.log(`过滤后的用户部门权限区域: ${JSON.stringify(filteredAreas)}`);
          
          permittedAreas.push(...filteredAreas);
        } catch (e) {
          console.log(`解析部门权限失败: ${e.message}`);
        }
      }
    }

    // 4. 检查用户公司权限
    if (user.orgId) {
      const orgSpaceRoles = await this.spaceRoleRepository.find({
        where: {
          roleType: 'org',
          roleId: user.orgId.toString()
        }
      });
      
      // console.log(`用户公司权限: 找到 ${orgSpaceRoles.length} 条记录, orgId=${user.orgId}`);
      
      for (const role of orgSpaceRoles) {
        try {
          // console.log(`处理组织角色: ${JSON.stringify(role)}`);
          const roleAreas = JSON.parse(role.roleArea || '[]');
          // console.log(`用户公司权限区域: ${JSON.stringify(roleAreas)}`);
          
          // 只保留与请求的 spaceCode 匹配的权限
          const filteredAreas = roleAreas.filter(area => area.spaceCode === spaceCode);
          // console.log(`过滤后的用户公司权限区域: ${JSON.stringify(filteredAreas)}`);
          
          permittedAreas.push(...filteredAreas);
        } catch (e) {
          console.log(`解析组织权限失败: ${e.message}, roleArea=${role.roleArea}`);
        }
      }
    }

    // console.log(`用户 ${userId} 在空间 ${spaceCode} 的权限区域数量: ${permittedAreas.length}`);
    return permittedAreas;
  } catch (error) {
    console.log(`检查用户空间权限失败: ${error.message}`, error.stack);
    return [];
  }
}

/**
 * 根据权限过滤空间树
 * @param node 空间树节点
 * @param permittedAreas 用户有权限的区域数组
 * @param currentPath 当前节点路径
 * @returns 过滤后的节点，如果没有权限则返回null
 */
private filterTreeByPermission(
  node: SpaceTreeNodeDto | FloorAreaTreeNodeDto | FloorTreeNodeDto | AreaTreeNodeDto | any,
  permittedAreas: any[],
  currentPath: string
): any {
  // 如果是空间节点，始终保留
  if (node.type === 'space') {
    // 递归过滤子节点
    if (node.children && node.children.length > 0) {
      const filteredChildren = node.children
        .map(child => this.filterTreeByPermission(child, permittedAreas, `${currentPath}/${child.id}`))
        .filter(Boolean);
      
      return {
        ...node,
        children: filteredChildren
      };
    }
    return node;
  }
  
  // 检查当前节点是否在权限列表中
  const hasDirectPermission = permittedAreas.some(area => {
    // 检查节点类型和ID是否匹配
    if (node.type === 'floorArea' && area.floorAreaCode === node.floorAreaCode) {
      return true;
    }
    if (node.type === 'floor' && area.floorCode === node.floorCode) {
      return true;
    }
    if (['area', 'room', 'pubArea', 'mroom', 'toilet'].includes(node.type) && 
        area.areaCode === node.areaCode && 
        area.floorCode === node.floorCode) {
      return true;
    }
    return false;
  });
  
  // 检查是否是上级节点（需要保留以维持树结构）
  const isParentNode = permittedAreas.some(area => {
    if (node.type === 'floorArea') {
      return area.floorAreaCode === node.floorAreaCode;
    }
    if (node.type === 'floor') {
      return area.floorCode === node.floorCode;
    }
    return false;
  });
  
  if (hasDirectPermission || isParentNode) {
    // 递归过滤子节点
    if (node.children && node.children.length > 0) {
      const filteredChildren = node.children
        .map(child => this.filterTreeByPermission(child, permittedAreas, `${currentPath}/${child.id}`))
        .filter(Boolean);
      
      return {
        ...node,
        children: filteredChildren
      };
    }
    return node;
  }
  
  return null;
}

  async uploadFloorMap(
    floorID: string,
    file: MulterFile,
    requestSpaceCode?: string,
    userSpaceCode?: string
  ) {
    if (!floorID) {
      throw new BadRequestException('缺少必要参数: floorID');
    }

    // Determine spaceCode
    const spaceCode = requestSpaceCode || userSpaceCode;
    if (!spaceCode) {
      throw new BadRequestException('未指定空间编码');
    }

    // Find Floor
    const floor = await this.floorRepository.findOne({
      where: { id: parseInt(floorID) }
    });

    if (!floor) {
      throw new BadRequestException('无效楼层信息');
    }

    // Validate extension - allow images and acmap
    const ext = path.extname(file.originalname).replace('.', '').toLowerCase();
    
    // Directory paths
    // Using process.cwd() + '/data/maps' as requested
    const dataDir = path.join(process.cwd(), 'data');
    const mapsDir = path.join(dataDir, 'maps');
    const spaceDir = path.join(mapsDir, spaceCode);
    const webPath = path.join(process.cwd(), 'src', 'server', 'web', 'maps');

    try {
      if (!fs.existsSync(spaceDir)) {
        fs.mkdirSync(spaceDir, { recursive: true });
      }

      // Filename: floorNum.ext (floorNum maps to floor.code)
      // The user requested to use floorNum queried by floorID, not floorCode.
      // In this system, floorNum is stored in the 'code' column.
      const filename = `${floor.code}.${ext}`;
      const filePath = path.join(spaceDir, filename);

      // Write file
      fs.writeFileSync(filePath, file.buffer);
      
      // Try to handle the symlink logic if possible/needed, or at least ensure web dir structure
      // But for now, we just save to data/maps as requested.

      return { code: '200', msg: 'success' };
    } catch (e) {
      this.logger.error(`Failed to upload floor map: ${e.message}`, e.stack);
      throw new BadRequestException('上传失败: ' + e.message);
    }
  }

  async getFloorMap(filename: string, userSpaceCode?: string): Promise<Buffer> {
    if (!filename) {
      throw new BadRequestException('文件名不能为空');
    }

    const spaceCode = userSpaceCode;
    if (!spaceCode) {
      throw new BadRequestException('未指定空间编码');
    }

    // Try to find the file in the space directory
    const dataDir = path.join(process.cwd(), 'data');
    const mapsDir = path.join(dataDir, 'maps');
    const spaceDir = path.join(mapsDir, spaceCode);
    
    // The filename comes in as "1.acmap" (or whatever floorCode.acmap)
    // We should check if the exact file exists
    let filePath = path.join(spaceDir, filename);

    if (!fs.existsSync(filePath)) {
      // Fallback logic: check if it's an image file but requested as .acmap?
      // Or maybe the user uploaded as .png but requests as .acmap?
      // Based on upload logic: filename = `${floor.code}.${ext}`.
      // If user requests `1.acmap`, they expect `1.acmap`.
      
      // Let's also support looking up by floorCode if filename is just "1" (unlikely given the route)
      // or if the extension doesn't match what's on disk.
      
      // If the file doesn't exist, try to find any file with the same base name (floorCode)
      const baseName = path.basename(filename, path.extname(filename)); // e.g. "1" from "1.acmap"
      let found = false;

      if (fs.existsSync(spaceDir)) {
        const files = fs.readdirSync(spaceDir);
        const matchingFile = files.find(f => {
          const fBase = path.basename(f, path.extname(f));
          return fBase === baseName;
        });
        
        if (matchingFile) {
          filePath = path.join(spaceDir, matchingFile);
          found = true;
        }
      } 
      
      if (!found) {
        // Fallback to demo.acmap
        const demoPath = path.join(process.cwd(), 'data', 'demo.acmap');
        if (fs.existsSync(demoPath)) {
          filePath = demoPath;
        } else {
          if (fs.existsSync(spaceDir)) {
             throw new BadRequestException('文件不存在');
          } else {
            throw new BadRequestException('空间目录不存在');
          }
        }
      }
    }

    try {
      return fs.readFileSync(filePath);
    } catch (e) {
      this.logger.error(`Failed to read floor map: ${e.message}`, e.stack);
      throw new BadRequestException('读取文件失败');
    }
  }

  async getToiletSensorStatus(
    userId: number,
    params: { spaceCode: string; gender: 'TMAN' | 'TWOMAN'; floorCode?: string }
  ): Promise<{ code: string; msg: string; data?: any }> {
    const { spaceCode, gender, floorCode } = params;

    // 权限校验：仅允许用户在有权限的 spaceCode 下访问
    const permittedAreas = await this.checkUserSpacePermission(userId, spaceCode);
    if (!permittedAreas || permittedAreas.length === 0) {
      return { code: '400', msg: '属地未授权' };
    }

    // 根据 floorCode 决定查询条件
    const where: any = {
      spaceCode,
      deleteFlag: 1,
      type: 'wcsensor',
      floorAreaCode: In([gender, `${gender}1`, `${gender}2`]),
    };
    if (floorCode) {
      where.floorCode = floorCode;
    }

    const devices = await this.iotDeviceRepository.find({
      where,
      order: { floorCode: 'ASC' },
    });

    const currentTime = Math.floor(Date.now() / 1000);
    const result: Record<string, Array<{ toilet: string; name: string; status: number }>> = {};

    for (const d of devices) {
      if (!result[d.floorCode]) result[d.floorCode] = [];
      let statusNum = 2; // 默认离线
      const uptime = parseInt(d.statusUptime || '0', 10);
      if (currentTime - uptime <= 180) {
        try {
          const parsed = d.status ? JSON.parse(d.status) : null;
          if (parsed && parsed.status === '0') statusNum = 0; // 空闲
          else statusNum = 1; // 占用
        } catch (e) {
          statusNum = 1;
        }
      }
      result[d.floorCode].push({
        toilet: d.floorAreaName,
        name: d.name,
        status: statusNum,
      });
    }

    return { code: '200', msg: 'success', data: result };
  }

}

```

