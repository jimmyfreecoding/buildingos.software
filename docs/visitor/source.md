# 源代码提交页（智能楼宇访客系统 buildingos.visitor）

## 提交要求
- 提供源程序的连续前30页与连续后30页；不足60页需提供全部源代码
- 每页不少于50行
- 源代码中不得包含公司名称、个人名称、文件名称
- 源代码总数量需与申请表保持一致

## 前30页
请在此粘贴前30页的连续源代码片段，按照页码顺序组织。

```
<template>
No Content
</template>

<script lang="ts" setup>
defineOptions({
  name: 'Index',
})
</script>

<style lang="scss" scoped>
.index-container {
  :deep() {
    .el-card {
      .el-card__header {
        position: relative;

        .card-header-tag {
          position: absolute;
          top: 15px;
          right: var(--el-margin);
        }

        > div > span {
          display: flex;
          align-items: center;

          i {
            margin-right: 3px;
          }
        }
      }

      .el-card__body {
        position: relative;

        .echarts {
          width: 100%;
          height: 127px;
        }

        .card-footer-tag {
          position: absolute;
          right: var(--el-margin);
          bottom: 15px;
        }
      }
    }
  }
}
</style>
<template>
  <div class="visitor-list-container no-background-container">
    <div class="tabs-wrapper">
      <div class="tab-buttons">
        <el-button type="primary" :icon="Plus" @click="handleAdd">添加访客申请</el-button>
        <el-button :icon="Document" @click="handleDrafts">草稿箱</el-button>
      </div>
      
      <el-tabs v-model="activeTabName" type="border-card" @tab-click="handleTabClick" class="no-background-container">
        <el-tab-pane 
          v-for="tab in tabList" 
          :key="tab.name" 
          :name="tab.name"
        >
          <template #label>
            <span class="custom-tabs-label">
              <span>{{ tab.label }}</span>
              <el-badge v-if="tab.total > 0" :value="tab.total" class="item-badge" type="danger" />
            </span>
          </template>
          <vab-query-form>
            <vab-query-form-top-panel>
              <el-form inline label-width="60px" :model="tab.queryForm" @submit.prevent>
                <el-form-item label="日期">
                  <el-date-picker 
                    v-model="tab.queryForm.date" 
                    value-format="YYYY-MM-DD" 
                    type="date" 
                    placeholder="查询日期"
                  />
                </el-form-item>
                <el-form-item>
                  <el-button :icon="Search" :loading="tab.loading" type="primary" @click="queryData(tab)">查询</el-button>
                </el-form-item>
              </el-form>
            </vab-query-form-top-panel>
          </vab-query-form>

          <div v-loading="tab.loading" class="visitor-card-list">
             <el-empty v-if="tab.data.length === 0" description="暂无数据" />
             <div v-for="item in tab.data" :key="item.id" class="visitor-card">
                 <div class="card-header">
                     <span class="app-no">申请编号: {{ item.application_no }}</span>
                 </div>
                 <div class="card-body">
                     <div class="main-info">
                         <div class="title-row">
                             <el-tag v-if="item.status === 'expired' || item.sub_status === 'expired'" type="info" effect="plain" class="status-tag">已失效</el-tag>
                             <el-tag v-if="item.status === 'abnormal'" type="danger" effect="plain" class="status-tag">异常</el-tag>
                             <el-tag v-if="item.status === 'pending'" type="warning" effect="plain" class="status-tag">待到访</el-tag>
                             <el-tag v-if="item.status === 'arrived'" type="success" effect="plain" class="status-tag">已到访</el-tag>
                             
                             <span class="company-name">{{ item.visitor_name }}</span>
                         </div>
                         
                         <div class="detail-grid">
                             <div class="detail-item">
                                 <el-icon><OfficeBuilding /></el-icon>
                                 <span class="label">访问大厦:</span>
                                 <span class="value">{{ item.location }}</span>
                             </div>
                              <div class="detail-item time-item">
                                 <el-icon><Calendar /></el-icon>
                                 <span class="label">访问时间:</span>
                                 <span class="value">{{ item.visit_time_start }} ~ {{ item.visit_time_end }}</span>
                             </div>
                              <div class="detail-item">
                                 <el-icon><CollectionTag /></el-icon>
                                 <span class="label">访问类别:</span>
                                 <span class="value">{{ item.visit_category }}</span>
                             </div>
                              <div class="detail-item">
                                 <el-icon><User /></el-icon>
                                 <span class="label">对接员工:</span>
                                 <span class="value">{{ item.contact_person }}</span>
                             </div>
                         </div>
                         
                         <div v-if="item.exception_reason" class="exception-row">
                             <span class="label">异常原因:</span>
                             <span class="value">{{ item.exception_reason }}</span>
                         </div>
                     </div>
                     
                     <div class="actions">
                         <el-button size="small">邀请链接</el-button>
                         <el-button size="small" @click="handleDetail(item)">查看详情</el-button>
                     </div>
                 </div>
             </div>
          </div>

          <el-pagination
            background
            :current-page="tab.queryForm.pageNo"
            :layout="layout"
            :page-size="tab.queryForm.pageSize"
            :total="tab.total"
            @current-change="(val) => handleCurrentChange(val, tab)"
            @size-change="(val) => handleSizeChange(val, tab)"
            style="margin-top: 20px; justify-content: flex-end;"
          />
        </el-tab-pane>
      </el-tabs>
    </div>

    <vistor-floow-edit ref="editRef" :record_id="current_rcord" :date="current_date" />
    <visitor-detail ref="detailRef" />
    <visitor-apply ref="applyRef" />
    <visitor-draft ref="draftRef" @edit="handleDraftEdit" />
  </div>
</template>

<script lang="ts" setup>
import type { TabsPaneContext } from 'element-plus'
import VistorFloowEdit from "/@/views/sence/visitor/vabAutoComponents/VistorFloowEdit.vue"
import VisitorDetail from "/@/views/sence/visitor/vabAutoComponents/VisitorDetail.vue"
import VisitorApply from "/@/views/sence/visitor/vabAutoComponents/VisitorApply.vue"
import VisitorDraft from "/@/views/sence/visitor/vabAutoComponents/VisitorDraft.vue"
import { getVisitorList, getVisitorStat } from "/@/api/visitor.ts"
import moment from 'moment'
import { Search, Plus, Document, OfficeBuilding, Calendar, CollectionTag, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

defineOptions({
  name: 'VisitorList',
})

const activeTabName = ref('all')
const editRef = ref<any>(null)
const detailRef = ref<any>(null)
const applyRef = ref<any>(null)
const draftRef = ref<any>(null)
const layout = ref<string>('total, sizes, prev, pager, next, jumper')
const current_rcord = ref('')
const current_date = ref('')

// Tab configuration
const tabList = reactive([
  { label: '全部', name: 'all', type: 0, data: [], total: 0, loading: false, queryForm: { pageNo: 1, pageSize: 20, date: '' } },
  { label: '待到访', name: 'pending', type: 1, data: [], total: 0, loading: false, queryForm: { pageNo: 1, pageSize: 20, date: '' } },
  { label: '已到访', name: 'arrived', type: 2, data: [], total: 0, loading: false, queryForm: { pageNo: 1, pageSize: 20, date: '' } },
  { label: '部分待访', name: 'partial', type: 3, data: [], total: 0, loading: false, queryForm: { pageNo: 1, pageSize: 20, date: '' } },
  { label: '已失效', name: 'expired', type: 4, data: [], total: 0, loading: false, queryForm: { pageNo: 1, pageSize: 20, date: '' } },
  { label: '申请异常', name: 'abnormal', type: 5, data: [], total: 0, loading: false, queryForm: { pageNo: 1, pageSize: 20, date: '' } },
])

const fetchData = async (tab: any) => {
  tab.loading = true
  // For demo purpose, we might not strictly need date
  const queryDate = tab.queryForm.date || moment().format("YYYY-MM-DD")
  tab.queryForm.date = queryDate

  const params = {
    pageNo: tab.queryForm.pageNo,
    pageSize: tab.queryForm.pageSize,
    type: tab.type,
    date: queryDate
  }
  
  try {
      const { data } = await getVisitorList(params)
      tab.data = data.list || []
      tab.total = data.total || 0
      
      // Update badge counts (in real scenario, maybe a separate API or included in response)
      // For demo, we just use the total from the list query if it matches the tab type
      // But ideally we should fetch stats separately or once
      if (tab.name !== 'all') {
          // tab.total is correct for this tab
      }
  } catch (error) {
      console.error(error)
      tab.data = []
      tab.total = 0
  } finally {
      tab.loading = false
  }
}

const fetchAllStats = async () => {
    // Simulate fetching counts for all tabs to show badges
    // In a real app, you might have an API like /visitor/stats
    // For now, we'll just trigger fetches for all tabs or mock it
    
    // Simple way: iterate and fetch (not efficient but works for demo)
    for (const tab of tabList) {
        if (tab.data.length === 0) {
            // Silently fetch to get total count
             const params = {
                pageNo: 1,
                pageSize: 1, // Minimize data
                type: tab.type,
                date: moment().format("YYYY-MM-DD")
            }
            try {
                const { data } = await getVisitorList(params)
                tab.total = data.total || 0
            } catch (e) {}
        }
    }
}

const handleTabClick = (pane: TabsPaneContext) => {
  const tab = tabList.find(t => t.name === pane.paneName)
  if (tab && tab.data.length === 0) {
    fetchData(tab)
  }
}

const queryData = (tab: any) => {
  tab.queryForm.pageNo = 1
  fetchData(tab)
}

const handleSizeChange = (val: number, tab: any) => {
  tab.queryForm.pageSize = val
  tab.queryForm.pageNo = 1
  fetchData(tab)
}

const handleCurrentChange = (val: number, tab: any) => {
  tab.queryForm.pageNo = val
  fetchData(tab)
}

const handleDetail = (row: any) => {
    detailRef.value.show(row.id)
}

const handleAdd = () => {
    applyRef.value.show()
}

const handleDrafts = () => {
    draftRef.value.show()
}

const handleDraftEdit = (item: any) => {
    // Open apply drawer with draft data
    // In a real app, you might pass the item or its ID to load data
    applyRef.value.show(item)
}

onMounted(() => {
    // Load initial tab data
    const activeTab = tabList.find(t => t.name === activeTabName.value)
    if (activeTab) {
        fetchData(activeTab)
    }
    // Fetch stats for badges
    fetchAllStats()
})
</script>

<style lang="scss" scoped>
.visitor-list-container {
    padding: 20px;
}

.tabs-wrapper {
    position: relative;
    
    .tab-buttons {
        position: absolute;
        right: 15px;
        top: -5px;
        z-index: 10;
    }
}

:deep(.el-tabs--border-card) {
    border-radius: 4px;
    box-shadow: none;
    border: none;
    
    .el-tabs__header {
        background-color: transparent;
        border-bottom: 1px solid #e4e7ed;
        margin-bottom: 20px;
    }
    
    .el-tabs__content {
        padding: 0;
        background: transparent;
    }
    
    .el-tabs__item {
        border: none;
        margin-right: 20px;
        height: auto;
        padding-bottom: 10px;
        overflow: visible; // Allow badge to overflow
        &.is-active {
            color: var(--el-color-primary);
            background: transparent;
            font-weight: bold;
            border-bottom: 2px solid var(--el-color-primary);
        }
    }
}

.custom-tabs-label {
    display: flex;
    align-items: center;
    padding-right: 5px; // Add some space for badge
    .item-badge {
        margin-left: 5px;
        margin-top: 5px; // Move badge up slightly
        :deep(.el-badge__content) {
            transform: scale(0.8);
        }
    }
}

.visitor-card-list {
    .visitor-card {
        background: var(--el-bg-color); // Use variable
        border-radius: 4px;
        margin-bottom: 15px;
        padding: 15px 20px;
        position: relative;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        border: 1px solid var(--el-border-color-light); // Use variable
        transition: all 0.3s;
        
        &:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .card-header {
            margin-bottom: 15px;
            .app-no {
                font-size: 12px;
                color: var(--el-text-color-secondary); // Use variable
            }
        }
        
        .card-body {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            
            .main-info {
                flex: 1;
                
                .title-row {
                    display: flex;
                    align-items: center;
                    margin-bottom: 15px;
                    
                    .status-tag {
                        margin-right: 10px;
                        border-radius: 2px;
                    }
                    
                    .company-name {
                        font-size: 18px;
                        font-weight: bold;
                        color: var(--el-text-color-primary); // Use variable
                    }
                }
                
                .detail-grid {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr); // 2 columns
                    gap: 10px 40px;
                    margin-bottom: 10px;
                    
                    .detail-item {
                        display: flex;
                        align-items: center;
                        font-size: 14px;
                        color: var(--el-text-color-regular); // Use variable
                        
                        .el-icon {
                            margin-right: 8px;
                            font-size: 16px;
                            color: var(--el-text-color-secondary); // Use variable
                        }
                        
                        .label {
                            margin-right: 5px;
                        }
                        
                        &.time-item {
                            grid-column: span 1; // Or span 2 if needed
                        }
                    }
                }
                
                .exception-row {
                    margin-top: 10px;
                    font-size: 13px;
                    color: var(--el-color-danger); // Use variable
                    .label {
                        margin-right: 5px;
                    }
                }
            }
            
            .actions {
                display: flex;
                gap: 10px;
                margin-left: 20px;
            }
        }
    }
}
</style>
<template>
  <div class="vistor-setting-form-container no-background-container">
      <el-card>
          <el-form ref="formRef" class="demo-form" label-position="left" label-width="100px" :model="form" >
            <el-form-item label="访客邀请提醒" prop="type">
              <el-checkbox-group v-model="form.type">
                <el-checkbox label="微信" name="type" />
                <el-checkbox label="短信" name="type" />
              </el-checkbox-group>
            </el-form-item>
            <el-form-item label="通知模板" prop="description">
              <el-input v-model="form.description" clearable type="textarea" />
            </el-form-item>
            <el-form-item label="访客到访提醒" prop="type">
              <el-checkbox-group v-model="form.type">
                <el-checkbox label="微信" name="type" />
                <el-checkbox label="短信" name="type" />
              </el-checkbox-group>
            </el-form-item>
            <el-form-item label="通知模板" prop="description">
              <el-input v-model="form.description" clearable type="textarea" />
            </el-form-item>
            <el-form-item label="访客离场通知" prop="type">
              <el-checkbox-group v-model="form.type">
                <el-checkbox label="微信" name="type" />
                <el-checkbox label="短信" name="type" />
              </el-checkbox-group>
            </el-form-item>
            <el-form-item label="通知模板" prop="description">
              <el-input v-model="form.description" clearable type="textarea" />
            </el-form-item>
            <el-form-item label="增值服务" prop="type">
              <el-checkbox-group v-model="form.type">
                <el-checkbox label="代客缴费" name="type" />
                <el-checkbox label="联动预定会议室" name="type" />
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitForm()">确定</el-button>
              <el-button type="danger" @click="resetForm()">重置</el-button>
            </el-form-item>
          </el-form>
      </el-card>
  </div>
</template>

<script lang="ts" setup>
import { getList } from '/@/api/area'

defineOptions({
  name: 'VistorSettingForm',
})

const generateData = () => {
  const data: any[] = []
  const cities = ['上海', '北京', '广州']
  const pinyin = ['shanghai', 'beijing', 'guangzhou']
  cities.forEach((city, index) => {
    data.push({
      label: city,
      key: index,
      pinyin: pinyin[index],
    })
  })
  return data
}

const formRef = ref<any>(null)
const labelPosition = ref<any>('right')
const form = reactive<any>({
  name: '',
  region: '',
  date: '',
  date2: '',
  delivery: false,
  type: [],
  resource: '',
  description: '',
  rate: 0,
  area: [],
  transfer: [],
})
const areaOptions = ref<any>([])
const rules = reactive<any>({
  name: [
    { required: true, message: '请输入活动名称', trigger: 'blur' },
    {
      min: 3,
      max: 5,
      message: '长度在 3 到 5 个字符',
      trigger: 'blur',
    },
  ],
  region: [{ required: true, message: '请选择活动区域', trigger: 'change' }],
  date: [
    {
      type: 'date',
      required: true,
      message: '请选择日期',
      trigger: 'change',
    },
  ],
  type: [
    {
      type: 'array',
      required: true,
      message: '请至少选择一个活动性质',
      trigger: 'change',
    },
  ],
  resource: [{ required: true, message: '请选择活动资源', trigger: 'change' }],
  description: [{ required: true, message: '请填写活动形式', trigger: 'blur' }],
})
const data = ref<any>(generateData())
const $baseMessage = inject<any>('$baseMessage')

const filterMethod = (query: any, item: any) => {
  return item.pinyin.indexOf(query) > -1
}

const fetchData = async () => {
  const { data } = await getList()
  areaOptions.value = data.list
}

const submitForm = () => {
  formRef.value.validate((valid: any) => {
    if (valid) $baseMessage('表单提交成功', 'success', 'hey')
    else $baseMessage('表单提交失败', 'error', 'hey')
  })
}

const resetForm = () => {
  formRef.value.resetFields()
}

onBeforeMount(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.vistor-setting-form-container {
  .demo-form {
    margin-top: 10px;
  }

  :deep() {
    .el-form-item__content {
      .el-rate {
        display: inline-block;
        font-size: 0;
        line-height: 1;
        vertical-align: middle;
      }

      .el-transfer__buttons {
        padding: 10px 10px 0 10px;
      }
    }
  }
}
</style>
<template>
  <div class="vistor-statistic-form-container no-background-container">
    <vab-query-form>
      <vab-query-form-top-panel>
        <el-form inline label-width="60px" :model="queryForm" @submit.prevent>
          <el-form-item label="日期">
            <el-date-picker v-model="queryForm.date" value-format="YYYY-MM-DD" type="date" placeholder="查询日期"/>
          </el-form-item>
          <el-form-item>
            <el-button :icon="Search" :loading="loading" type="primary" @click="fetchStatData">查询</el-button>
          </el-form-item>
        </el-form>
      </vab-query-form-top-panel>
    </vab-query-form>
    <el-row :gutter="20">
      <el-col  :span="8">
        <car-num background="white" percentage="30%"  :countConfig="{endValue:total.invite_total}" icon="account-circle-fill" title="总邀请访客人数">
          <template #tag>
            <el-tag type="danger">{{ queryDate }}</el-tag>
          </template>
          <template #chart>
            <active-users-bar />
          </template>
        </car-num>
      </el-col>
      <el-col  :span="8">
        <car-num background="white" percentage="30%"  :countConfig="{endValue:total.visited_day_total}" icon="account-circle-fill" title="已到访客数量">
          <template #tag>
            <el-tag type="danger">{{ queryDate }}</el-tag>
          </template>
          <template #chart>
            <active-users-bar />
          </template>
        </car-num>
      </el-col>
      <el-col  :span="8">
        <car-num background="white" percentage="30%"  :countConfig="{endValue:total.novisit_day_total}" icon="account-circle-fill" title="未到访人数">
          <template #tag>
            <el-tag type="danger">{{ queryDate }}</el-tag>
          </template>
          <template #chart>
            <active-users-bar />
          </template>
        </car-num>
      </el-col>
    </el-row>
    <el-row style="margin-top: 20px;" :gutter="20">
      <el-col :span="10">
        <vistor-catagory :data="chartsData.category"/>
      </el-col>
      <el-col :span="14">
        <vistor-trand :data="chartsData.flow"/>
      </el-col>
    </el-row>
  </div>
</template>
<script lang="ts" setup>
import { getVisitorStat, getVisitorRange } from "/@/api/visitor.ts";
import { Search } from '@element-plus/icons-vue'
import moment from "moment";
import { map } from 'lodash-es'
import VistorCatagory from './vabAutoComponents/VistorCatagory.vue'
import VistorTrand from './vabAutoComponents/VistorTrand.vue'
defineOptions({
  name: 'VistorStatics',
})
const loading = ref<boolean>(false)
const queryForm = reactive<any>({
  date: ''
})
const queryDate = ref();
const chartsData = reactive<any>({
  category: [],
  flow: [],
})
const total = ref<any>({
  novisit_day_total: 0,
  visited_day_total: 0,
  invite_total_total: 0,
})
const visit_categories:any = {
  visit: '预约访客',
  meeting: '会务邀请'
}
const fetchStatData = async () => {
  queryDate.value = queryForm.date || moment().format("YYYY-MM-DD");
  const { data } = await getVisitorStat({date:queryDate.value})
  total.value = data;
  chartsData.category = map(data.visitor_category, item=> {
    return {
      value: item.value,
      name: visit_categories[item.category]
    }
  })
  const res = await getVisitorRange({date:queryDate.value})
  chartsData.flow = res.data
}

onMounted(() => {
  fetchStatData()
})
</script>

<style lang="scss" scoped>
.vistor-statistic-form-container {
  .demo-form {
    margin-top: 10px;
  }
  :deep() {
    .el-form-item__content {
      .el-rate {
        display: inline-block;
        font-size: 0;
        line-height: 1;
        vertical-align: middle;
      }

      .el-transfer__buttons {
        padding: 10px 10px 0 10px;
      }
    }
  }
}
</style>
<template>
  <el-drawer
    v-model="visible"
    title="编辑访问申请"
    size="80%"
    direction="rtl"
    :before-close="handleClose"
    class="visitor-apply-drawer"
  >
    <div class="apply-container">
      <!-- 基本信息 -->
      <div class="section-title">基本信息</div>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" class="apply-form">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="访客单位" prop="visitorUnit">
              <el-input v-model="form.visitorUnit" placeholder="请输入" maxlength="100" show-word-limit />
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="来访时间" prop="visitTime">
              <el-date-picker
                v-model="form.visitTime"
                type="datetimerange"
                range-separator="→"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="访客区域" prop="visitArea">
              <el-select v-model="form.visitArea" placeholder="请选择" style="width: 100%">
                <el-option label="极企大厦" value="hz_zeekr" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="访客楼层" prop="visitFloor">
              <el-select v-model="form.visitFloor" placeholder="请选择" style="width: 100%">
                <el-option label="27F" value="27F" />
                <el-option label="26F" value="26F" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="访问类别" prop="visitType">
              <el-select v-model="form.visitType" placeholder="请选择" style="width: 100%">
                <el-option label="业务合作" value="business" />
                <el-option label="面试" value="interview" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="对接人" prop="contactPerson">
              <el-select v-model="form.contactPerson" placeholder="请选择" style="width: 100%">
                <el-option label="何铮" value="hezheng" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="是否需要网络" prop="needNetwork">
              <el-radio-group v-model="form.needNetwork">
                <el-radio label="needed">需要</el-radio>
                <el-radio label="not_needed">不需要</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item label="访问事由" prop="reason">
              <el-input v-model="form.reason" type="textarea" placeholder="请输入" maxlength="300" show-word-limit :rows="2" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="含海外访客" prop="hasForeigner">
              <el-radio-group v-model="form.hasForeigner">
                <el-radio label="yes">是</el-radio>
                <el-radio label="no">否</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <!-- 提示信息 -->
      <div class="notice-box">
        <p>1. 访客是否需要通过我司提供的网络，使用电脑访问互联网。（如选“是”，请在下表中输入访客电脑mac地址信息。）</p>
        <p>2. 使用过程中如有疑问，可联系 <span class="highlight">张开 1322342343 kai.Zhang@geeqee.com</span></p>
        <p>3. mac地址获取办法</p>
        <div class="sub-notice">
          <p>a. Win:</p>
          <p class="indent">i. 电脑右下角 网络—WIFI（属性）—下滑找到物理地址（MAC）</p>
          <p class="indent">ii. 电脑同时按 win+R—输入cmd,按enter进入控制台—输入ipconfig /all——找到物理地址</p>
          <p>b. Mac:</p>
          <p class="indent">i. 左上角打开关于本机—系统报告—左侧点开wifi— “en0” 目录下找到MAC地址</p>
          <p class="indent">ii. 打开终端—输入ifconfig—找到en0—ether对应就是mac地址</p>
        </div>
      </div>

      <!-- 访客名单 -->
      <div class="section-title" style="margin-top: 20px;">访客名单</div>
      <div class="visitor-list-toolbar">
        <div class="left">
          <el-button :icon="Upload">导入明细</el-button>
          <el-button :icon="Download">下载明细模板</el-button>
        </div>
        <div class="right">
          <el-button :icon="Delete" @click="handleBatchDelete">批量删除</el-button>
        </div>
      </div>

      <el-table :data="form.visitorList" border style="width: 100%" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column label="* 来宾姓名" min-width="120">
          <template #default="{ row }">
            <el-input v-model="row.name" placeholder="请输入" />
          </template>
        </el-table-column>
        <el-table-column label="来宾职位" min-width="120">
          <template #default="{ row }">
            <el-input v-model="row.title" placeholder="请输入" />
          </template>
        </el-table-column>
        <el-table-column label="* 来宾联系电话" min-width="150">
          <template #default="{ row }">
            <el-input v-model="row.phone" placeholder="请输入" />
          </template>
        </el-table-column>
        <el-table-column label="身份证信息" min-width="180">
          <template #default="{ row }">
            <el-input v-model="row.idCard" placeholder="请输入" />
          </template>
        </el-table-column>
        <el-table-column label="来访车辆车牌号" min-width="150">
          <template #default="{ row }">
            <el-input v-model="row.carPlate" placeholder="+ 添加车牌号" />
          </template>
        </el-table-column>
        <el-table-column label="* 电脑mac地址" min-width="150">
          <template #default="{ row }">
            <el-input v-model="row.macAddress" placeholder="请输入" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center" fixed="right">
          <template #default="{ $index }">
            <el-button type="danger" link @click="removeVisitor($index)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="add-visitor-btn" @click="addVisitor">
        <el-icon><Plus /></el-icon> 添加访客
      </div>
    </div>

    <template #footer>
      <div class="drawer-footer">
        <el-button @click="handleClose">返回</el-button>
        <el-button @click="saveDraft">保存为草稿</el-button>
        <el-button type="primary" @click="submitApply">提交申请</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
import { Plus, Upload, Download, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

defineOptions({
  name: 'VisitorApply',
})

const visible = ref(false)
const formRef = ref<any>(null)
const selectedVisitors = ref<any[]>([])

const form = reactive({
  visitorUnit: '何铮',
  visitTime: [],
  visitArea: 'hz_zeekr',
  visitFloor: '27F',
  visitType: 'business',
  contactPerson: 'hezheng',
  needNetwork: 'needed',
  reason: '',
  hasForeigner: 'no',
  visitorList: [
    { name: '何铮', title: '', phone: '13980554799', idCard: '', carPlate: '', macAddress: '' }
  ]
})

const rules = {
  visitorUnit: [{ required: true, message: '请输入访客单位', trigger: 'blur' }],
  visitTime: [{ required: true, message: '请选择来访时间', trigger: 'change' }],
  visitArea: [{ required: true, message: '请选择访客区域', trigger: 'change' }],
  visitFloor: [{ required: true, message: '请选择访客楼层', trigger: 'change' }],
  visitType: [{ required: true, message: '请选择访问类别', trigger: 'change' }],
  contactPerson: [{ required: true, message: '请选择对接人', trigger: 'change' }],
  needNetwork: [{ required: true, message: '请选择是否需要网络', trigger: 'change' }],
  hasForeigner: [{ required: true, message: '请选择是否含海外访客', trigger: 'change' }],
}

const show = (data?: any) => {
  visible.value = true
  if (data) {
      // Mock loading draft data
      form.visitorUnit = data.visitorName || ''
      // ... populate other fields if available in draft data
      ElMessage.success('已加载草稿数据')
  } else {
      // Reset form if needed or keep default
  }
}

const handleClose = () => {
  visible.value = false
}

const addVisitor = () => {
  form.visitorList.push({ name: '', title: '', phone: '', idCard: '', carPlate: '', macAddress: '' })
}

const removeVisitor = (index: number) => {
  form.visitorList.splice(index, 1)
}

const handleSelectionChange = (val: any[]) => {
  selectedVisitors.value = val
}

const handleBatchDelete = () => {
  if (selectedVisitors.value.length === 0) {
    return ElMessage.warning('请选择要删除的访客')
  }
  form.visitorList = form.visitorList.filter(item => !selectedVisitors.value.includes(item))
  selectedVisitors.value = []
}

const saveDraft = () => {
  ElMessage.success('保存草稿成功')
  handleClose()
}

const submitApply = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success('提交申请成功')
      handleClose()
    }
  })
}

defineExpose({
  show
})
</script>

<style lang="scss" scoped>
.visitor-apply-drawer {
  .apply-container {
    padding: 0 20px 20px;
  }

  .section-title {
    font-size: 16px;
    font-weight: bold;
    color: #303133;
    margin-bottom: 20px;
    border-left: 4px solid var(--el-color-primary);
    padding-left: 10px;
  }

  .notice-box {
    background-color: #f0f9eb; // Light blue/green background similar to image
    border: 1px solid #b3d8ff; // Border color
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 20px;
    font-size: 13px;
    color: #606266;
    line-height: 1.8;

    .highlight {
      font-weight: bold;
      color: #303133;
    }

    .sub-notice {
      padding-left: 20px;
      .indent {
        padding-left: 20px;
      }
    }
  }

  .visitor-list-toolbar {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
  }

  .add-visitor-btn {
    margin-top: 15px;
    border: 1px dashed #dcdfe6;
    text-align: center;
    padding: 10px;
    cursor: pointer;
    color: #606266;
    border-radius: 4px;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;

    &:hover {
      border-color: var(--el-color-primary);
      color: var(--el-color-primary);
    }
  }

  .drawer-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }
}
</style>
<template>
  <el-drawer
    v-model="dialogVisible"
    title="查看详情"
    size="50%"
    direction="rtl"
    :close-on-click-modal="false"
    class="visitor-detail-drawer"
  >
    <div v-loading="loading" class="detail-container">
       <!-- Header Section -->
       <div class="detail-header">
           <div class="app-no">申请编号:{{ detail.application_no }}</div>
           <div class="title-row">
               <el-tag v-if="detail.status === 'expired' || detail.sub_status === 'expired'" type="info" effect="plain" class="status-tag">已失效</el-tag>
               <el-tag v-if="detail.status === 'abnormal'" type="danger" effect="plain" class="status-tag">异常</el-tag>
               <el-tag v-if="detail.status === 'pending'" type="warning" effect="plain" class="status-tag">待到访</el-tag>
               <el-tag v-if="detail.status === 'arrived'" type="success" effect="plain" class="status-tag">已到访</el-tag>
               <span class="visitor-name">{{ detail.visitor_name }}</span>
           </div>
       </div>

       <!-- Info Grid -->
       <div class="info-grid">
           <div class="info-item">
               <el-icon><OfficeBuilding /></el-icon>
               <span class="label">访问大厦:</span>
               <span class="value">{{ detail.location }}</span>
           </div>
           <div class="info-item">
               <el-icon><Calendar /></el-icon>
               <span class="label">访问时间:</span>
               <span class="value">{{ detail.visit_time_start }} ~ {{ detail.visit_time_end }}</span>
           </div>
            <div class="info-item">
               <span class="label">网络使用:</span>
               <span class="value">{{ detail.network_needed }}</span>
           </div>
           <div class="info-item">
               <el-icon><CollectionTag /></el-icon>
               <span class="label">访问类别:</span>
               <span class="value">{{ detail.visit_category }}</span>
           </div>
           <div class="info-item">
               <el-icon><User /></el-icon>
               <span class="label">对接员工:</span>
               <span class="value">{{ detail.contact_person }}</span>
           </div>
           <div class="info-item">
               <el-icon><UserFilled /></el-icon>
               <span class="label">是否含海外访客:</span>
               <span class="value">{{ detail.has_foreign_visitor }}</span>
           </div>
           <div class="info-item full-width">
               <el-icon><Document /></el-icon>
               <span class="label">访问事由:</span>
               <span class="value">{{ detail.visit_reason }}</span>
           </div>
       </div>

       <!-- Exception Reason -->
       <div v-if="detail.exception_reason" class="exception-box">
           <span class="label">异常原因:</span>
           <span class="value">{{ detail.exception_reason }}</span>
       </div>

       <!-- Visitor List Table -->
       <div class="visitor-table-section">
           <h3 class="section-title">访客名单</h3>
           <el-table :data="detail.visitors" border style="width: 100%">
               <el-table-column prop="name" label="姓名" width="120" />
               <el-table-column prop="title" label="来宾职位" width="120" />
               <el-table-column prop="phone" label="来宾联系电话" width="150" />
               <el-table-column prop="id_card" label="身份证信息" width="180" />
               <el-table-column prop="car_info" label="来访车辆信息" />
               <el-table-column label="到访状态" width="100">
                   <template #default="{ row }">
                       <span class="status-dot" :class="row.status"></span>
                       {{ row.status_text }}
                   </template>
               </el-table-column>
               <el-table-column prop="arrive_time" label="到访时间" width="160" />
               <el-table-column label="操作" width="180" fixed="right">
                   <template #default="{ row }">
                       <el-button type="danger" link size="small" @click="handleTrack(row)">访客轨迹</el-button>
                       <el-button type="danger" link size="small" @click="handleEvaluation(row)">评价结果</el-button>
                   </template>
               </el-table-column>
           </el-table>
       </div>
    </div>
  </el-drawer>

  <el-dialog
    v-model="trackVisible"
    title="访客轨迹"
    width="500px"
    :close-on-click-modal="false"
    class="track-dialog"
  >
    <el-timeline>
        <el-timeline-item
          v-for="(activity, index) in trackList"
          :key="index"
          :timestamp="activity.time"
          :type="index === 0 ? 'primary' : ''"
          :hollow="index === 0"
        >
          {{ activity.location }}
        </el-timeline-item>
    </el-timeline>
    <template #footer>
        <el-button @click="trackVisible = false">关闭</el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="evaluationVisible"
    title="评价结果"
    width="400px"
    :close-on-click-modal="false"
    class="evaluation-dialog"
  >
    <div class="evaluation-content">
        <div class="eval-item">
            <div class="label">设备设施满意度:</div>
            <div class="rate-box">
                <el-rate v-model="currentEvaluation.facilityRate" disabled text-color="#999" />
                <span class="text">{{ currentEvaluation.facilityRate ? '' : '暂无评价' }}</span>
            </div>
        </div>
        <div class="eval-item">
            <div class="label">接待人员满意度:</div>
            <div class="rate-box">
                <el-rate v-model="currentEvaluation.receptionRate" disabled text-color="#999" />
                <span class="text">{{ currentEvaluation.receptionRate ? '' : '暂无评价' }}</span>
            </div>
        </div>
        <div class="comment">
            {{ currentEvaluation.comment || '暂无' }}
        </div>
    </div>
    <template #footer>
        <el-button @click="evaluationVisible = false">返回</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { getVistorByID } from '/@/api/visitor'
import { OfficeBuilding, Calendar, CollectionTag, User, Document, UserFilled } from '@element-plus/icons-vue'

defineOptions({
  name: 'VisitorDetail',
})

const dialogVisible = ref(false)
const evaluationVisible = ref(false)
const trackVisible = ref(false)
const loading = ref(false)
const detail = ref<any>({})
const currentEvaluation = ref<any>({})
const trackList = ref<any[]>([])

const show = async (id: number) => {
    dialogVisible.value = true
    loading.value = true
    try {
        const { data } = await getVistorByID({ id })
        detail.value = data || {}
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const handleTrack = (row: any) => {
    // Mock track data (from recent to old)
    trackList.value = [
        { time: '2024-05-20 17:30', location: '离开极企大厦' },
        { time: '2024-05-20 14:10', location: '到达 18F 会议室' },
        { time: '2024-05-20 14:05', location: '通过 1F 闸机' },
        { time: '2024-05-20 13:55', location: '到达极企大堂' }
    ]
    trackVisible.value = true
}

const handleEvaluation = (row: any) => {
    // Mock evaluation data
    currentEvaluation.value = {
        facilityRate: 0,
        receptionRate: 0,
        comment: ''
    }
    evaluationVisible.value = true
}

defineExpose({
    show
})
</script>

<style lang="scss" scoped>
.visitor-detail-drawer {
    .detail-container {
        padding: 0 10px;
    }

    .detail-header {
        margin-bottom: 20px;
        .app-no {
            font-size: 13px;
            color: #909399;
            margin-bottom: 10px;
        }
        .title-row {
            display: flex;
            align-items: center;
            .status-tag {
                margin-right: 10px;
            }
            .visitor-name {
                font-size: 20px;
                font-weight: bold;
                color: #303133;
            }
        }
    }

    .info-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px 30px;
        margin-bottom: 20px;
        
        .info-item {
            display: flex;
            align-items: center;
            font-size: 14px;
            color: #606266;
            
            .el-icon {
                margin-right: 8px;
                font-size: 16px;
                color: #909399;
            }
            .label {
                margin-right: 5px;
                color: #606266;
            }
            .value {
                color: #303133;
                font-weight: 500;
            }
            
            &.full-width {
                grid-column: span 3;
            }
        }
    }

    .exception-box {
        background-color: #fef0f0;
        padding: 10px 15px;
        border-radius: 4px;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        
        .label {
            color: #F56C6C;
            font-weight: bold;
            margin-right: 10px;
        }
        .value {
            color: #F56C6C;
        }
    }

    .visitor-table-section {
        .section-title {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #303133;
        }
        
        .status-dot {
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            margin-right: 5px;
            vertical-align: middle;
            
            &.expired, &.abnormal { background-color: #909399; }
            &.pending { background-color: #E6A23C; }
            &.arrived { background-color: #67C23A; }
        }
    }
}

.track-dialog {
    :deep(.el-dialog__body) {
        padding: 20px 40px;
    }
}

.evaluation-dialog {
    .evaluation-content {
        padding: 10px 20px;
        .eval-item {
            margin-bottom: 20px;
            .label {
                margin-bottom: 10px;
                color: #606266;
            }
            .rate-box {
                display: flex;
                align-items: center;
                .text {
                    margin-left: 10px;
                    color: #999;
                    font-size: 12px;
                }
            }
        }
        .comment {
            margin-top: 20px;
            color: #606266;
        }
    }
}
</style>
<template>
  <el-drawer
    v-model="visible"
    title="草稿箱"
    size="400px"
    direction="rtl"
    :before-close="handleClose"
    class="visitor-draft-drawer"
  >
    <div v-loading="loading" class="draft-container">
      <div v-if="list.length === 0" class="empty-state">
        <el-empty description="暂无草稿" />
      </div>
      
      <div v-else class="draft-list">
        <div v-for="item in list" :key="item.id" class="draft-item">
          <div class="item-header">
            <span class="visitor-name">{{ item.visitorName }}</span>
            <div class="actions">
              <el-button type="danger" link size="small" @click="handleDelete(item)">删除</el-button>
              <el-button type="primary" link size="small" @click="handleEdit(item)">编辑</el-button>
            </div>
          </div>
          <div class="item-info">
            {{ item.visitType }} | {{ item.location }}
          </div>
          <div class="item-time">
            <el-icon><Clock /></el-icon> 保存时间: {{ item.saveTime }}
          </div>
        </div>
        
        <div class="no-more">没有更多了 😴</div>
      </div>
    </div>
  </el-drawer>
</template>

<script lang="ts" setup>
import { Clock } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

defineOptions({
  name: 'VisitorDraft',
})

const visible = ref(false)
const loading = ref(false)
const list = ref<any[]>([])

// Mock data
const mockDrafts = [
  {
    id: 1,
    visitorName: '何铮',
    visitType: '业务合作',
    location: '极企大厦 • 27F',
    saveTime: '2024/12/18 20:24:02'
  },
  {
    id: 2,
    visitorName: '何铮',
    visitType: '业务合作',
    location: '极企大厦 • 27F',
    saveTime: '2024/12/18 20:24:02'
  },
  {
    id: 3,
    visitorName: '立方体',
    visitType: '供应商服务',
    location: '极企大厦 • 24F',
    saveTime: '2024/12/18 20:24:09'
  }
]

const show = () => {
  visible.value = true
  fetchDrafts()
}

const handleClose = () => {
  visible.value = false
}

const fetchDrafts = () => {
  loading.value = true
  // Simulate API call
  setTimeout(() => {
    list.value = [...mockDrafts]
    loading.value = false
  }, 300)
}

const handleDelete = (item: any) => {
  ElMessageBox.confirm('确认删除该草稿?', '提示', {
    type: 'warning'
  }).then(() => {
    list.value = list.value.filter(i => i.id !== item.id)
    ElMessage.success('删除成功')
  })
}

const emit = defineEmits(['edit'])

const handleEdit = (item: any) => {
  handleClose()
  emit('edit', item)
}

defineExpose({
  show
})
</script>

<style lang="scss" scoped>
.visitor-draft-drawer {
  .draft-container {
    padding: 0 20px;
  }

  .draft-item {
    padding: 15px 0;
    border-bottom: 1px solid #ebeef5;
    
    &:last-child {
      border-bottom: none;
    }

    .item-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .visitor-name {
        font-size: 16px;
        font-weight: bold;
        color: #303133;
      }
      
      .actions {
        .el-button {
            padding: 4px 8px;
            background-color: #f4f4f5;
            &.el-button--primary {
                color: #606266;
                &:hover {
                    color: var(--el-color-primary);
                    background-color: #ecf5ff;
                }
            }
            &.el-button--danger {
                color: #f56c6c;
                background-color: #fef0f0;
                &:hover {
                    background-color: #fde2e2;
                }
            }
        }
      }
    }

    .item-info {
      font-size: 14px;
      color: #606266;
      margin-bottom: 8px;
    }

    .item-time {
      font-size: 13px;
      color: #909399;
      display: flex;
      align-items: center;
      
      .el-icon {
        margin-right: 4px;
      }
    }
  }

  .no-more {
    text-align: center;
    color: #909399;
    font-size: 13px;
    margin-top: 20px;
    padding-bottom: 20px;
  }
}
</style>
<template>
  <vab-card :body-style="{ height: '240px' }" skeleton>
    <template #header>
      <vab-icon icon="donut-chart-fill" />
      访客分类
    </template>
      <vab-chart :option="option" />
  </vab-card>
</template>

<script lang="ts" setup>
import { useSettingsStore } from '/@/store/modules/settings'

const settingsStore = useSettingsStore()
const { color } = storeToRefs(settingsStore)

const props = defineProps({
  data: {
    type: Array,
    default: [],
  },
})

const option = reactive<any>({
  tooltip: {
    trigger: 'item',
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: '访客类别',
      type: 'pie',
      radius: ['40%', '80%'],
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2,
      },
      data: props.data,
    },
  ],
})
watch(
  color,
  () => {
    option.color = [color.value]
  },
  { immediate: true }
)
watch(
  () => props.data,
  (d) => {
    if (d) {
      option.series[0].data = d
    }
  },
  { deep: true }
)
</script>
<template>
  <el-dialog
    v-model="dialogFormVisible"
    append-to-body
    :before-close="close"
    width="500px"
    :title="title"
    class="track-dialog"
  >
      <el-row style="display: flex; justify-content: center">
        <el-col :span="24">
          <div class="vistorflowedit-container">
            <div style="font-size:18px; margin-bottom: 20px; font-weight: bold; text-align: center;">
              {{ visitor_name }}
            </div>
            <el-timeline>
              <el-timeline-item 
                v-for="(item, index) in activities" 
                :key="index" 
                :color="item.color" 
                :timestamp="item.timestamp"
                :hollow="index === 0"
                placement="top"
              >
                <div class="track-content">
                  {{ item.content }}
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-col>
      </el-row>
      <template #footer>
        <el-button @click="close">关闭</el-button>
      </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { getVisitTrack } from "/@/api/visitor.ts";
import moment from 'moment/moment'
import { map } from 'lodash-es';
const activities = ref<any>([])
defineOptions({
  name: 'VistorFlowEdit',
})
const props = defineProps({
  record_id: {
    type: String,
    default: '',
  },
  date: {
    type: String,
    default: '',
  }
})
const loading = ref(false);
const emit = defineEmits(['fetch-data'])
const title = ref<string>('通行轨迹')
const dialogFormVisible = ref<boolean>(false)
const visitor_name = ref();
const showEdit = (row: any) => {
  dialogFormVisible.value = true
}

watch(
  () => props.record_id,
  (d) => {
    if (d) {
      fetchTrackData()
    }
  },
  { deep: true }
)
const close = () => {
  dialogFormVisible.value = false
}
const fetchTrackData = async () => {
  loading.value = true
  visitor_name.value = ""
  const { data } = await getVisitTrack(props)
  activities.value = map(data,(item,index:number)=>{
    visitor_name.value = item.visitor_name
    if(index === 0){
      return {
        content: item.door_name,
        timestamp: moment.unix(item.pass_time).format("YYYY-MM-DD HH:mm:ss"),
        color: '#13ce66',
        cardType: 'success',
      }
    }else{
      if(index === (data.length -1 ) && item.pass_direction === 'out'){
        return {
          content: item.door_name,
          timestamp: moment.unix(item.pass_time).format("YYYY-MM-DD HH:mm:ss"),
          color: '#13ce66',
          cardType: 'success',
        }
      }else{
        return {
          content: item.door_name,
          timestamp: moment.unix(item.pass_time).format("YYYY-MM-DD HH:mm:ss"),
        }
      }

    }
  })
  loading.value = false
}
defineExpose({
  showEdit,
})
</script>
<style lang="scss" scoped>
.vistorflowedit-container {
    padding: 0 20px;
    
    .track-content {
        font-size: 14px;
        color: #303133;
        line-height: 1.5;
    }
}
</style>
<template>
  <vab-card :body-style="{ height: '240px' }" skeleton>
    <template #header>
      <vab-icon icon="line-chart-fill" />
      24小时访客量
    </template>
    <vab-chart :option="option" />
  </vab-card>
</template>

<script lang="ts" setup>
import { useSettingsStore } from '/@/store/modules/settings'
import { lightenColor } from '/@/utils/lightenColor'

const settingsStore = useSettingsStore()
const { color } = storeToRefs(settingsStore)
const props = defineProps({
  data: {
    type: Array,
    default: [],
  },
})
const echartData = ref<any>([])
const echartLabel = ref<any>([])
const option = reactive<any>({
  tooltip: {
    trigger: 'axis',
    extraCssText: 'z-index:1',
    formatter(params: any) {
      return `<div style="font-size:12px;line-height:20px;color:#3C3936;">${params[0].seriesName}</div><div style="font-size:14px;color: #FF5800;margin-top:4px;">${params[0].value.toLocaleString() || 0}`
    }
  },
  grid: {
    top: '4%',
    left: '2%',
    right: '2%',
    bottom: '0%',
    containLabel: true,
  },
  xAxis: [
    {
      type: 'category',
      data: echartLabel,
      boundaryGap: false,
    },
  ],
  yAxis: [
    {
      type: 'value',
    },
  ],
  series: [
    {
      name: '到访客户',
      type: 'line',
      data: echartData,
      symbol: 'circle',
      smooth: true,
      yAxisIndex: 0,
      showSymbol: false,
      areaStyle: {
        opacity: 0.8,
      },
    },
  ],
})
watch(
  () => props.data,
  (d) => {
    if (d) {
      echartData.value = []
      echartLabel.value = []
      d.forEach(function (p: any) {
      echartData.value.push(p.total)
      echartLabel.value.push(p.hour)
  })
    }
  },
  { deep: true }
)
watch(
  color,
  () => {
    option.color = [color.value, lightenColor(color.value, 50)]
  },
  { immediate: true }
)
</script>

```

## 后30页
请在此粘贴后30页的连续源代码片段，按照页码顺序组织。

```
export class CreateVisitorGuestDto {
  name: string;
  title?: string;
  phone: string;
  idCard?: string;
  carPlate?: string;
  macAddress?: string;
}

export class CreateVisitorApplicationDto {
  visitorUnit: string;
  visitTime: [string, string]; // [start, end]
  visitArea: string;
  visitFloor: string;
  visitType: string;
  contactPerson: string;
  needNetwork: string; // 'needed' | 'not_needed'
  hasForeigner: string; // 'yes' | 'no'
  reason?: string;
  visitorList: CreateVisitorGuestDto[];
}
export class QueryVisitorDto {
  pageNo?: number;
  pageSize?: number;
  type?: number; // 1:pending, 2:arrived, 4:expired, 5:abnormal
  date?: string; // YYYY-MM-DD
  keyword?: string;
}
import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, OneToMany } from 'typeorm';
import { VisitorGuestEntity } from './visitor-guest.entity';

export enum VisitorStatus {
  PENDING = 'pending',
  ARRIVED = 'arrived',
  EXPIRED = 'expired',
  ABNORMAL = 'abnormal',
  COMPLETED = 'completed',
}

@Entity('visitor_application')
export class VisitorApplicationEntity {
  @PrimaryGeneratedColumn('increment')
  id: number;

  @Column({ name: 'application_no', length: 50 })
  applicationNo: string;

  @Column({ name: 'visitor_unit', length: 100 })
  visitorUnit: string;

  @Column({ name: 'visit_start_time', type: 'datetime' })
  visitStartTime: Date;

  @Column({ name: 'visit_end_time', type: 'datetime' })
  visitEndTime: Date;

  @Column({ name: 'visit_area', length: 50 })
  visitArea: string;

  @Column({ name: 'visit_floor', length: 50 })
  visitFloor: string;

  @Column({ name: 'visit_type', length: 50 })
  visitType: string;

  @Column({ name: 'contact_person', length: 50 })
  contactPerson: string;

  @Column({ name: 'contact_person_name', length: 100, nullable: true })
  contactPersonName: string;

  @Column({ name: 'network_needed', default: false })
  networkNeeded: boolean;

  @Column({ name: 'has_foreigner', default: false })
  hasForeigner: boolean;

  @Column({ name: 'visit_reason', type: 'text', nullable: true })
  visitReason: string;

  @Column({
    type: 'varchar', // SQLite doesn't support enum natively well in TypeORM without extra config, using varchar for safety across DBs
    length: 20,
    default: VisitorStatus.PENDING,
  })
  status: VisitorStatus;

  @Column({ name: 'exception_reason', length: 255, nullable: true })
  exceptionReason: string;

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  @OneToMany(() => VisitorGuestEntity, (guest) => guest.application, {
    cascade: true,
  })
  visitors: VisitorGuestEntity[];
}
import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn } from 'typeorm';
import { VisitorApplicationEntity, VisitorStatus } from './visitor-application.entity';

@Entity('visitor_guest')
export class VisitorGuestEntity {
  @PrimaryGeneratedColumn('increment')
  id: number;

  @Column({ name: 'application_id' })
  applicationId: number;

  @ManyToOne(() => VisitorApplicationEntity, (application) => application.visitors, {
    onDelete: 'CASCADE',
  })
  @JoinColumn({ name: 'application_id' })
  application: VisitorApplicationEntity;

  @Column({ length: 100 })
  name: string;

  @Column({ length: 100, nullable: true })
  title: string;

  @Column({ length: 20 })
  phone: string;

  @Column({ name: 'id_card', length: 50, nullable: true })
  idCard: string;

  @Column({ name: 'car_plate', length: 20, nullable: true })
  carPlate: string;

  @Column({ name: 'mac_address', length: 50, nullable: true })
  macAddress: string;

  @Column({ name: 'check_in_time', type: 'datetime', nullable: true })
  checkInTime: Date;

  @Column({ name: 'check_out_time', type: 'datetime', nullable: true })
  checkOutTime: Date;

  @Column({
    type: 'varchar',
    length: 20,
    default: VisitorStatus.PENDING,
  })
  status: VisitorStatus;
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
}
import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { VisitorController } from './visitor.controller';
import { VisitorMqttController } from './visitor.mqtt.controller';
import { VisitorApplicationEntity } from './entities/visitor-application.entity';
import { VisitorGuestEntity } from './entities/visitor-guest.entity';
import { VisitorService } from './visitor.service';
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
          database: 'apps/visitor/data/visitor.sqlite',
          autoLoadEntities: true,
          synchronize: true,
        };
      },
    }),
    TypeOrmModule.forFeature([VisitorApplicationEntity, VisitorGuestEntity]),
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
            clientId: 'buildingos_microservice_visitor_' + Math.random().toString(16).slice(2, 8),
          },
        }),
      },
    ]),
  ],
  controllers: [VisitorController, VisitorMqttController],
  providers: [VisitorService, HostBridge],
})
export class AppModule {}
import 'reflect-metadata'
import { NestFactory } from '@nestjs/core'
import { AppModule } from './app.module'
import * as swagger from '@nestjs/swagger'
import { Transport, MicroserviceOptions } from '@nestjs/microservices'
import { Logger } from '@nestjs/common'

async function bootstrap() {
  const logger = new Logger('VisitorBootstrap')
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
  const config = new swagger.DocumentBuilder().setTitle("Visitor API").setVersion("1.0").build()
  const doc = swagger.SwaggerModule.createDocument(app, config)
  swagger.SwaggerModule.setup('api', app, doc)
  const port = parseInt(process.env.PORT || '3003', 10)
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
import { Controller, Get, Post, Delete, Body, Query, Param } from '@nestjs/common';
import { VisitorService } from './visitor.service';
import { CreateVisitorApplicationDto } from './dto/create-visitor-application.dto';
import { QueryVisitorDto } from './dto/query-visitor.dto';

@Controller('visitor')
export class VisitorController {
  constructor(private readonly visitorService: VisitorService) {}

  @Get("health")
  health() {
    return { status: "ok" };
  }

  @Post('apply')
  async create(@Body() createVisitorDto: CreateVisitorApplicationDto) {
    const result = await this.visitorService.createApplication(createVisitorDto);
    return { code: 200, data: result };
  }

  @Get('list')
  async findAll(@Query() query: QueryVisitorDto) {
    const result = await this.visitorService.findAll(query);
    return { code: 200, data: result };
  }

  @Get('stat')
  async getStatistics() {
    const result = await this.visitorService.getStatistics();
    return { code: 200, data: result };
  }

  @Get('range-trend')
  async getTrafficTrend(@Query('type') type: string) {
    const result = await this.visitorService.getTrafficTrend(type);
    return { code: 200, data: result };
  }

  @Get('track')
  async getTrack(@Query('visitorId') visitorId: number) {
    const result = await this.visitorService.getTrack(visitorId);
    return { code: 200, data: result };
  }

  @Delete()
  async remove(@Body() body: { ids: number[] }) {
    await this.visitorService.remove(body.ids);
    return { code: 200, message: 'success' };
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    const result = await this.visitorService.findOne(+id);
    return { code: 200, data: result };
  }
}
import { Controller } from '@nestjs/common'
import { MessagePattern, Payload } from '@nestjs/microservices'
@Controller('visitor-mqtt')
export class VisitorMqttController {
  @MessagePattern('visitor/#')
  handle(@Payload() data: any) {
    return { code: 200, data }
  }
}

import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, DataSource, Like, Between, LessThan, MoreThan } from 'typeorm';
import { VisitorApplicationEntity, VisitorStatus } from './entities/visitor-application.entity';
import { VisitorGuestEntity } from './entities/visitor-guest.entity';
import { CreateVisitorApplicationDto } from './dto/create-visitor-application.dto';
import { QueryVisitorDto } from './dto/query-visitor.dto';
import { HostBridge } from './integration/host-bridge.service';

@Injectable()
export class VisitorService implements OnModuleInit {
  private readonly logger = new Logger('VisitorService');

  constructor(
    @InjectRepository(VisitorApplicationEntity)
    private readonly applicationRepo: Repository<VisitorApplicationEntity>,
    @InjectRepository(VisitorGuestEntity)
    private readonly guestRepo: Repository<VisitorGuestEntity>,
    private readonly ds: DataSource,
    private readonly host: HostBridge,
  ) {}

  async onModuleInit() {
    // Basic sync check
    try {
      await this.applicationRepo.count();
    } catch (e) {
      this.logger.warn('Database schema might be missing, attempting sync...');
      await this.ds.synchronize();
    }
  }

  // Generate Application No: HGH-WC-YYYYMMDDHHmmss-RAND
  private generateApplicationNo(): string {
    const now = new Date();
    const timeStr = now.toISOString().replace(/[-T:.Z]/g, '').slice(0, 14);
    const rand = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
    return `HGH-WC-${timeStr}-${rand}`;
  }

  async createApplication(dto: CreateVisitorApplicationDto) {
    const application = new VisitorApplicationEntity();
    application.applicationNo = this.generateApplicationNo();
    application.visitorUnit = dto.visitorUnit;
    application.visitStartTime = new Date(dto.visitTime[0]);
    application.visitEndTime = new Date(dto.visitTime[1]);
    application.visitArea = dto.visitArea;
    application.visitFloor = dto.visitFloor;
    application.visitType = dto.visitType;
    application.contactPerson = dto.contactPerson;
    application.networkNeeded = dto.needNetwork === 'needed';
    application.hasForeigner = dto.hasForeigner === 'yes';
    application.visitReason = dto.reason;
    application.status = VisitorStatus.PENDING;

    // Create guests
    const guests = dto.visitorList.map((g) => {
      const guest = new VisitorGuestEntity();
      guest.name = g.name;
      guest.title = g.title;
      guest.phone = g.phone;
      guest.idCard = g.idCard;
      guest.carPlate = g.carPlate;
      guest.macAddress = g.macAddress;
      guest.status = VisitorStatus.PENDING;
      return guest;
    });

    application.visitors = guests;

    return await this.applicationRepo.save(application);
  }

  async findAll(query: QueryVisitorDto) {
    const pageNo = query.pageNo || 1;
    const pageSize = query.pageSize || 10;
    const skip = (pageNo - 1) * pageSize;

    const qb = this.applicationRepo.createQueryBuilder('app')
      .leftJoinAndSelect('app.visitors', 'visitors')
      .skip(skip)
      .take(pageSize)
      .orderBy('app.createdAt', 'DESC');

    // Status filter
    // 1:pending, 2:arrived, 4:expired, 5:abnormal
    if (query.type) {
      let status: VisitorStatus | undefined;
      switch (Number(query.type)) {
        case 1: status = VisitorStatus.PENDING; break;
        case 2: status = VisitorStatus.ARRIVED; break;
        case 4: status = VisitorStatus.EXPIRED; break;
        case 5: status = VisitorStatus.ABNORMAL; break;
      }
      if (status) {
        qb.andWhere('app.status = :status', { status });
      }
    }

    // Date filter
    if (query.date) {
      const startOfDay = new Date(query.date);
      startOfDay.setHours(0, 0, 0, 0);
      const endOfDay = new Date(query.date);
      endOfDay.setHours(23, 59, 59, 999);
      
      // Filter by visit start time within the day
      qb.andWhere('app.visitStartTime BETWEEN :start AND :end', { start: startOfDay, end: endOfDay });
    }

    // Keyword filter
    if (query.keyword) {
      qb.andWhere('(app.visitorUnit LIKE :keyword OR visitors.name LIKE :keyword OR visitors.phone LIKE :keyword)', { keyword: `%${query.keyword}%` });
    }

    const [list, total] = await qb.getManyAndCount();
    
    return {
      list,
      total,
      pageNo,
      pageSize
    };
  }

  async findOne(id: number) {
    return await this.applicationRepo.findOne({
      where: { id },
      relations: ['visitors'],
    });
  }

  async getStatistics() {
    const todayStart = new Date();
    todayStart.setHours(0, 0, 0, 0);
    const todayEnd = new Date();
    todayEnd.setHours(23, 59, 59, 999);

    const inviteTotal = await this.applicationRepo.count();
    
    // Check guests for actual arrival count today
    const visitedDayTotal = await this.guestRepo.count({
      where: {
        status: VisitorStatus.ARRIVED,
        checkInTime: Between(todayStart, todayEnd),
      }
    });

    const noVisitDayTotal = await this.applicationRepo.count({
      where: {
        status: VisitorStatus.PENDING,
        visitStartTime: Between(todayStart, todayEnd),
      }
    });

    // Category stats
    const categories = await this.applicationRepo
      .createQueryBuilder('app')
      .select('app.visitType', 'category')
      .addSelect('COUNT(app.id)', 'value')
      .groupBy('app.visitType')
      .getRawMany();

    return {
      invite_total: inviteTotal,
      visited_day_total: visitedDayTotal,
      novisit_day_total: noVisitDayTotal,
      visitor_category: categories,
    };
  }

  async getTrafficTrend(type: string = 'day') {
    // Mock implementation for trend
    // In real scenario, we would aggregate by hour/day based on type
    const data = [];
    for (let i = 0; i < 24; i++) {
      data.push(Math.floor(Math.random() * 20));
    }
    return data;
  }

  async getTrack(visitorId: number) {
    // Mock implementation for track
    return [
      { time: '09:00', location: 'Main Gate' },
      { time: '09:05', location: 'Lobby' },
      { time: '09:10', location: 'Elevator' },
      { time: '09:12', location: '27F Reception' },
    ];
  }

  async remove(ids: number[]) {
    await this.guestRepo.delete({ applicationId:  ids[0] }); // Simplify deletion logic for demo
    // Better to use cascade or query builder for multiple delete
    // For SQLite/Simple implementation:
    for (const id of ids) {
       await this.applicationRepo.delete(id);
    }
    return { success: true };
  }
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
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UserController } from './user.controller';
import { UserService } from './user.service';
import { User } from '../entities/User';
import { Department } from '../entities/Department';
import { SystemRole } from '../entities/SystemRole';
import { UserRole } from '../entities/UserRole';
import { UserPcTokens } from '../entities/UserPcTokens';
import { UserZeekrTokens } from '../entities/UserZeekrTokens';
import { Org } from '../entities/Org';
import { CustomerAccount } from '../entities/CustomerAccount';
import { UserTokens } from '../entities/UserTokens';

@Module({
  imports: [
    TypeOrmModule.forFeature([
      Org,
      User,
      Department,
      SystemRole,
      UserRole,
      UserPcTokens,
      UserZeekrTokens,
      CustomerAccount,
      UserTokens
    ]),
  ],
  controllers: [UserController],
  providers: [UserService],
  exports: [UserService],
})
export class UserModule {}
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

