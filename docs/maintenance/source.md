# 源代码提交页（智能楼宇智能维护管理系统 buildingos.maintenance）

## 提交要求
- 提供源程序的连续前30页与连续后30页；不足60页需提供全部源代码
- 每页不少于50行
- 源代码中不得包含公司名称、个人名称、文件名称
- 源代码总数量需与申请表保持一致

## 前30页
请在此粘贴前30页的连续源代码片段，按照页码顺序组织。

```
import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { JwtModule } from '@nestjs/jwt';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { MaintanceController } from './maintance.controller';
import { HostBridge } from './integration/host-bridge.service';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    JwtModule.register({
      secret: process.env.JWT_SECRET || 'BuildingOS',
      signOptions: { expiresIn: '7d' },
    }),
    ClientsModule.registerAsync([
      {
        name: 'HOST_CLIENT',
        imports: [ConfigModule],
        inject: [ConfigService],
        useFactory: (config: ConfigService) => ({
          transport: Transport.MQTT,
          options: {
            url: config.get('MQTT_BROKER_URL') || 'mqtt://localhost:1883',
            username: config.get('MQTT_USERNAME'),
            password: config.get('MQTT_PASSWORD'),
            subscribeOptions: { qos: 1 },
            clientId:
              'buildingos_microservice_maintance_' +
              Math.random().toString(16).slice(2, 8),
          },
        }),
      },
    ]),
  ],
  controllers: [MaintanceController],
  providers: [HostBridge],
})
export class AppModule {}

import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as swagger from '@nestjs/swagger';
import { Transport, MicroserviceOptions } from '@nestjs/microservices';
import { Logger } from '@nestjs/common';

async function bootstrap() {
  const logger = new Logger('MaintanceBootstrap');
  const app = await NestFactory.create(AppModule);
  app.enableCors();

  try {
    const url = process.env.MQTT_BROKER_URL;
    if (url) {
      app.connectMicroservice<MicroserviceOptions>({
        transport: Transport.MQTT,
        options: { url, subscribeOptions: { qos: 1 } },
      });
      await app.startAllMicroservices();
      logger.log(`MQTT microservice started, url=${url}`);
    }
  } catch (e: unknown) {
    const errMsg = e instanceof Error ? e.message : 'MQTT connect failed';
    logger.warn(errMsg);
  }

  const config = new swagger.DocumentBuilder()
    .setTitle('Maintance API')
    .setDescription('报修管理接口文档')
    .setVersion('1.0')
    .addBearerAuth()
    .build();
  const doc = swagger.SwaggerModule.createDocument(app, config);
  swagger.SwaggerModule.setup('maintance/docs', app, doc);

  const port = parseInt(process.env.PORT || '3032', 10);
  await app.listen(port);
  logger.log(`Maintance service running on port ${port}`);
}
void bootstrap();

import { Controller, Get, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { readFileSync } from 'fs';
import { join } from 'path';
import { JwtAuthGuard } from './auth/jwt.guard';
import { Public } from './auth/public.decorator';

@ApiTags('报修管理')
@Controller()
@UseGuards(JwtAuthGuard)
export class MaintanceController {
  @Get('health')
  @Public()
  @ApiOperation({ summary: '健康检查' })
  health() {
    return { status: 'ok' };
  }

  @Get('menu.json')
  @Public()
  @ApiOperation({ summary: '获取菜单' })
  menuJson(): unknown {
    const menuPath = join(__dirname, '..', 'menu.json');
    return JSON.parse(readFileSync(menuPath, 'utf-8')) as unknown;
  }
}

import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { JwtService } from '@nestjs/jwt';
import { Request } from 'express';
import { IS_PUBLIC_KEY } from './public.decorator';

@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(
    private readonly jwtService: JwtService,
    private readonly reflector: Reflector,
  ) {}

  canActivate(context: ExecutionContext): boolean {
    const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    if (isPublic) return true;

    const request = context.switchToHttp().getRequest<Request>();
    const token = this.extractToken(request);
    if (!token) throw new UnauthorizedException('Missing token');
    try {
      const payload = this.jwtService.verify(token, {
        secret: process.env.JWT_SECRET || 'BuildingOS',
      });
      (request as any).user = payload;
      return true;
    } catch {
      throw new UnauthorizedException('Invalid token');
    }
  }

  private extractToken(request: Request): string | undefined {
    const auth = request.headers['authorization'];
    if (!auth) return undefined;
    const [type, token] = auth.split(' ');
    return type === 'Bearer' ? token : undefined;
  }
}

import { SetMetadata } from '@nestjs/common';

export const IS_PUBLIC_KEY = 'isPublic';
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);

import { Injectable, Optional, Inject } from '@nestjs/common';
import { ModuleRef } from '@nestjs/core';
import { ClientProxy } from '@nestjs/microservices';
import { firstValueFrom } from 'rxjs';

@Injectable()
export class HostBridge {
  private readonly isLocal: boolean;

  constructor(
    private readonly moduleRef: ModuleRef,
    @Optional() @Inject('HOST_CLIENT') private readonly client?: ClientProxy,
  ) {
    this.isLocal =
      String(process.env.DEPLOY_MODE || '').toUpperCase() === 'NPM_INSTALL';
  }

  async invoke<T>(
    service: string,
    method: string,
    ...args: unknown[]
  ): Promise<T> {
    if (this.isLocal) {
      const instance: any = this.moduleRef.get(service, { strict: false });
      if (!instance || typeof instance[method] !== 'function')
        throw new Error(`Not found: ${service}.${method}`);
      return await instance[method](...args);
    }
    if (!this.client) throw new Error('HOST_CLIENT not available');
    return await firstValueFrom(
      this.client.send('host-gateway.invoke', { service, method, args }),
    );
  }
}

[
  {
    "path": "/repair",
    "name": "Repair",
    "component": "Layout",
    "meta": { "title": "报修", "icon": "tools-line", "guard": ["Admin"] },
    "children": [
      {
        "path": "workorder",
        "name": "WorkOrder",
        "meta": { "title": "工单管理", "guard": ["Admin"] },
        "children": [
          {
            "path": "list",
            "name": "WorkOrderList",
            "component": "/@/views/workorder/list/index.vue",
            "meta": { "title": "工单列表", "guard": ["Admin"] }
          },
          {
            "path": "process",
            "name": "WorkOrderProcess",
            "component": "/@/views/workorder/process/index.vue",
            "meta": { "title": "工单流程", "guard": ["Admin"] }
          },
          {
            "path": "servicetype",
            "name": "ServiceType",
            "component": "/@/views/workorder/serviceType/index.vue",
            "meta": { "title": "服务类型", "guard": ["Admin"] }
          },
          {
            "path": "sla",
            "name": "WorkOrderSla",
            "component": "/@/views/workorder/sla/index.vue",
            "meta": { "title": "工单时效", "guard": ["Admin"] }
          },
          {
            "path": "statistics",
            "name": "WorkOrderStatistics",
            "component": "/@/views/workorder/statistics/index.vue",
            "meta": { "title": "工单统计", "guard": ["Admin"] }
          },
          {
            "path": "qrcode",
            "name": "WorkOrderQRCode",
            "component": "/@/views/workorder/qrcode/index.vue",
            "meta": { "title": "二维码管理", "guard": ["Admin"] }
          },
          {
            "path": "assignRule",
            "name": "AssignRule",
            "component": "/@/views/workorder/assignRule/index.vue",
            "meta": { "title": "分配规则", "guard": ["Admin"] }
          },
          {
            "path": "inspectionRoute",
            "name": "InspectionRoute",
            "component": "/@/views/workorder/inspectionRoute/index.vue",
            "meta": { "title": "巡检路线", "guard": ["Admin"] }
          }
        ]
      },
      {
        "path": "equipmentManagement",
        "name": "EquipmentManagement",
        "meta": { "title": "设备管理", "guard": ["Admin"] },
        "children": [
          {
            "path": "ledger",
            "name": "EquipmentLedger",
            "component": "/@/views/equipmentManagement/ledger/index.vue",
            "meta": { "title": "设备台账", "guard": ["Admin"] }
          },
          {
            "path": "maintenancePlan",
            "name": "MaintenancePlan",
            "component": "/@/views/equipmentManagement/maintenance/plan/index.vue",
            "meta": { "title": "保养计划", "guard": ["Admin"] }
          },
          {
            "path": "maintenanceTask",
            "name": "MaintenanceTask",
            "component": "/@/views/equipmentManagement/maintenance/task/index.vue",
            "meta": { "title": "保养任务", "guard": ["Admin"] }
          },
          {
            "path": "inspectionPoint",
            "name": "InspectionPoint",
            "component": "/@/views/equipmentManagement/inspection/point/index.vue",
            "meta": { "title": "巡检点", "guard": ["Admin"] }
          },
          {
            "path": "inspectionStandard",
            "name": "InspectionStandard",
            "component": "/@/views/equipmentManagement/inspection/standard/index.vue",
            "meta": { "title": "巡检标准", "guard": ["Admin"] }
          },
          {
            "path": "inspectionPlan",
            "name": "InspectionPlan",
            "component": "/@/views/equipmentManagement/inspection/plan/index.vue",
            "meta": { "title": "巡检计划", "guard": ["Admin"] }
          },
          {
            "path": "inspectionTask",
            "name": "InspectionTask",
            "component": "/@/views/equipmentManagement/inspection/task/index.vue",
            "meta": { "title": "巡检任务", "guard": ["Admin"] }
          }
        ]
      }
    ]
  }
]

<template>
  <div class="work-order-list-container no-background-container">
    <vab-query-form>
      <vab-query-form-top-panel :span="24">
        <el-form :model="queryForm" :inline="true" @submit.prevent>
          <el-form-item label="上报人">
            <el-input v-model="queryForm.reporter" placeholder="请输入上报人" />
          </el-form-item>
          <el-form-item label="报事位置">
            <el-input v-model="queryForm.location" placeholder="请输入报事位置" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="queryForm.status" placeholder="请选择状态" clearable>
              <el-option label="待派发" value="pending_dispatch" />
              <el-option label="待接单" value="pending_accept" />
              <el-option label="处置中" value="handling" />
              <el-option label="待验收" value="pending_verify" />
              <el-option label="已归档" value="archived" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>
          <el-form-item label="紧急程度">
            <el-select v-model="queryForm.urgentLevel" placeholder="请选择紧急程度" clearable>
              <el-option label="一般" value="normal" />
              <el-option label="紧急" value="urgent" />
              <el-option label="非常紧急" value="very_urgent" />
            </el-select>
          </el-form-item>
          <el-form-item label="上报时间">
            <el-date-picker
              v-model="queryForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
            <el-button type="primary" :icon="Plus" @click="handleAdd">新增报事</el-button>
          </el-form-item>
        </el-form>
      </vab-query-form-top-panel>
    </vab-query-form>
    <vab-card class="auto-height-card">
      <el-tabs v-model="activeTab" style="background: var(--el-bg-color); padding: 0 20px" @tab-click="handleTabClick">
        <el-tab-pane label="我的待办" name="todo" />
        <el-tab-pane label="我的已办" name="done" />
        <el-tab-pane label="我发起的" name="created" />
        <el-tab-pane label="抄送我的" name="cc" />
        <el-tab-pane label="全部工单" name="all" />
      </el-tabs>
      <el-table v-loading="listLoading" :data="list" border>
        <el-table-column prop="id" label="工单编号" min-width="150" />
        <el-table-column prop="title" label="标题" min-width="150" show-overflow-tooltip />
        <el-table-column prop="reporter" label="上报人" width="100" />
        <el-table-column label="报修来源" width="90">
          <template #default="{ row }">
            <el-tag v-if="getSourceInfo(row.source)" :type="getSourceInfo(row.source).type" size="small">
              {{ getSourceInfo(row.source).label }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="位置" width="120" />
        <el-table-column label="关联设备" width="130">
          <template #default="{ row }"><span>{{ row.equipmentName || '-' }}</span></template>
        </el-table-column>
        <el-table-column prop="urgentLevel" label="紧急程度" width="100">
          <template #default="{ row }">
            <el-tag :type="row.urgentLevel === 'very_urgent' ? 'danger' : row.urgentLevel === 'urgent' ? 'warning' : 'info'">
              {{ row.urgentLevel === 'very_urgent' ? '非常紧急' : row.urgentLevel === 'urgent' ? '紧急' : '一般' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="当前状态" width="150">
          <template #default="{ row }">
            <div class="status-cell">
              <span v-if="isOverdue(row)" class="blink-dot" title="已超时"></span>
              <el-tag :type="getStatusInfo(row.status).type" :effect="isOverdue(row) ? 'dark' : 'plain'">
                {{ getStatusInfo(row.status).label }}
              </el-tag>
              <el-tag v-if="row.escalated" type="danger" size="small" effect="dark">已升级</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="上报时间" width="160" />
        <el-table-column prop="flowName" label="流程名称" width="120" />
        <el-table-column prop="handler" label="处理人" width="100" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleDetail(row)">详情</el-button>
            <el-button v-if="activeTab === 'todo'" type="primary" text size="small" @click="handleProcess(row)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>
      <vab-pagination
        :current-page="queryForm.pageNo" :page-size="queryForm.pageSize" :total="total"
        @current-change="handleCurrentChange" @size-change="handleSizeChange"
      />
    </vab-card>
    <work-order-edit ref="editRef" @fetch-data="fetchData" />
    <work-order-detail ref="detailRef" @fetch-data="fetchData" />
  </div>
</template>

<script lang="ts" setup>
import { getWorkOrderList } from '/@/api/workOrder'
import WorkOrderEdit from './vabAutoComponents/WorkOrderEdit.vue'
import WorkOrderDetail from './vabAutoComponents/WorkOrderDetail.vue'
import { Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'WorkOrderList' })

const list = ref<any[]>([])
const listLoading = ref(true)
const total = ref(0)
const activeTab = ref('todo')
const editRef = ref<any>(null)
const detailRef = ref<any>(null)

const queryForm = reactive<any>({
  pageNo: 1, pageSize: 20, reporter: '', location: '', status: '', urgentLevel: '', dateRange: [], tab: 'todo',
})

const statusMap: Record<string, { label: string; type: string }> = {
  pending_dispatch: { label: '待派发', type: 'info' },
  pending_accept: { label: '待接单', type: 'warning' },
  handling: { label: '处置中', type: 'primary' },
  pending_verify: { label: '待验收', type: 'warning' },
  archived: { label: '已归档', type: 'success' },
  cancelled: { label: '已取消', type: 'danger' },
}

const statusCompatMap: Record<string, string> = {
  pending: 'pending_dispatch', processing: 'handling', done: 'archived',
}

const sourceMap: Record<string, { label: string; type: string }> = {
  manual: { label: '手动', type: 'info' },
  qrcode: { label: '扫码', type: 'success' },
  alarm: { label: '告警', type: 'danger' },
  inspection: { label: '巡检', type: 'warning' },
}

const getStatusInfo = (status: string) => {
  const mapped = statusCompatMap[status] || status
  return statusMap[mapped] || { label: status || '未知', type: 'info' }
}

const getSourceInfo = (source: string) => { return sourceMap[source] || null }

const isOverdue = (row: any) => {
  if (row.escalated) return true
  if (row.responseTimeout && !['archived', 'cancelled', 'done'].includes(row.status)) {
    const timeField = row.assignTime || row.createTime
    if (timeField) {
      const startTime = new Date(timeField).getTime()
      const now = Date.now()
      const elapsedMinutes = (now - startTime) / 1000 / 60
      return elapsedMinutes > row.responseTimeout
    }
  }
  return false
}

const fetchData = async () => {
  listLoading.value = true
  queryForm.tab = activeTab.value
  const { data } = await getWorkOrderList(queryForm)
  list.value = data.list || []
  total.value = data.total || 0
  listLoading.value = false
}

const handleTabClick = (tab: any) => { activeTab.value = tab.props.name; queryForm.pageNo = 1; fetchData() }
const handleSizeChange = (val: number) => { queryForm.pageSize = val; fetchData() }
const handleCurrentChange = (val: number) => { queryForm.pageNo = val; fetchData() }
const handleAdd = () => { editRef.value.showEdit() }
const handleDetail = (row: any) => { detailRef.value.showDetail(row, false) }
const handleProcess = (row: any) => { detailRef.value.showDetail(row, true) }

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.work-order-list-container { padding: 20px; background: var(--el-bg-color); }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
.blink-dot { display: inline-block; width: 8px; height: 8px; background-color: #f56c6c; border-radius: 50%; animation: blink 1s infinite; flex-shrink: 0; }
.status-cell { display: flex; align-items: center; gap: 6px; }
</style>

<template>
  <el-dialog v-model="dialogVisible" title="工单详情" width="700px">
    <el-descriptions title="基本信息" :column="2" border>
      <el-descriptions-item label="工单编号">{{ detail.id }}</el-descriptions-item>
      <el-descriptions-item label="报事房间">{{ detail.location }}</el-descriptions-item>
      <el-descriptions-item label="上报人">{{ detail.reporter }}</el-descriptions-item>
      <el-descriptions-item label="联系电话">{{ detail.phone }}</el-descriptions-item>
      <el-descriptions-item label="紧急程度">
        <el-tag :type="getUrgentType(detail.urgentLevel)">{{ getUrgentText(detail.urgentLevel) }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="当前状态"><el-tag>{{ detail.status }}</el-tag></el-descriptions-item>
      <el-descriptions-item label="所属流程">{{ detail.flowName }}</el-descriptions-item>
      <el-descriptions-item label="创建时间">{{ detail.createTime }}</el-descriptions-item>
      <el-descriptions-item label="描述" :span="2">{{ detail.description }}</el-descriptions-item>
      <el-descriptions-item label="图片" :span="2">
        <el-image v-for="(img, index) in detail.images" :key="index"
          style="width: 100px; height: 100px; margin-right: 10px" :src="img" :preview-src-list="detail.images" />
      </el-descriptions-item>
    </el-descriptions>
    <div style="margin-top: 20px">
      <h3>处理日志</h3>
      <el-timeline>
        <el-timeline-item v-for="(activity, index) in detail.logs" :key="index" :timestamp="activity.time">
          {{ activity.operator }} 执行了 {{ activity.action }}
        </el-timeline-item>
      </el-timeline>
    </div>
    <template #footer>
      <el-button @click="dialogVisible = false">关闭</el-button>
      <el-button v-if="canHandle" type="primary" @click="handle">处理</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { getWorkOrderDetail, handleWorkOrder } from '/@/api/workOrder'

defineOptions({ name: 'WorkOrderDetail' })

const emit = defineEmits(['fetch-data'])
const dialogVisible = ref(false)
const detail = ref<any>({})
const canHandle = ref(false)

const getUrgentType = (level: string) => {
  switch (level) { case 'urgent': return 'warning'; case 'very_urgent': return 'danger'; default: return 'info' }
}

const getUrgentText = (level: string) => {
  switch (level) { case 'urgent': return '紧急'; case 'very_urgent': return '非常紧急'; default: return '一般' }
}

const showDetail = async (row: any, isHandle: boolean = false) => {
  dialogVisible.value = true
  canHandle.value = isHandle
  const { data } = await getWorkOrderDetail(row.id)
  detail.value = data
}

const handle = async () => {
  await handleWorkOrder({ id: detail.value.id })
  ElMessage.success('处理成功')
  dialogVisible.value = false
  emit('fetch-data')
}

defineExpose({ showDetail })
</script>

<template>
  <el-dialog v-model="dialogFormVisible" :title="title" width="600px" @closed="close">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="报修来源" prop="source">
        <el-select v-model="form.source" placeholder="请选择来源">
          <el-option label="手动报单" value="手动报单" />
          <el-option label="二维码扫码" value="二维码扫码" />
          <el-option label="设备告警" value="设备告警" />
          <el-option label="巡检自动" value="巡检自动" />
        </el-select>
      </el-form-item>
      <el-form-item label="报事房间" prop="location">
        <el-input v-model="form.location" placeholder="请输入房间号" autocomplete="off" />
      </el-form-item>
      <el-form-item label="关联设备" prop="equipmentId">
        <el-select v-model="form.equipmentId" filterable remote clearable
          :remote-method="remoteSearchEquipment" :loading="equipmentLoading" placeholder="搜索并选择设备"
          @change="handleEquipmentChange">
          <el-option v-for="item in equipmentOptions" :key="item.id" :label="`${item.name} (${item.code})`" :value="item.id">
            <span>{{ item.name }}</span>
            <span style="float: right; color: var(--el-text-color-secondary); font-size: 12px; margin-left: 12px">{{ item.code }}</span>
          </el-option>
        </el-select>
        <div v-if="selectedEquipment" class="equipment-info-card">
          <div class="info-row"><span class="info-label">设备名称：</span><span class="info-value">{{ selectedEquipment.name }}</span></div>
          <div class="info-row"><span class="info-label">设备编码：</span><span class="info-value">{{ selectedEquipment.code }}</span></div>
          <div class="info-row"><span class="info-label">型号：</span><span class="info-value">{{ selectedEquipment.type || '-' }}</span></div>
          <div class="info-row"><span class="info-label">位置：</span><span class="info-value">{{ selectedEquipment.location || '-' }}</span></div>
          <div class="info-row"><span class="info-label">状态：</span><span class="info-value">
            <el-tag :type="equipmentStatusTag(selectedEquipment.status)" size="small">{{ equipmentStatusText(selectedEquipment.status) }}</el-tag>
          </span></div>
        </div>
      </el-form-item>
      <el-form-item label="报事流程" prop="flow">
        <el-select v-model="form.flow" placeholder="请选择流程">
          <el-option label="普通维修流程" value="flow1" />
          <el-option label="紧急维修流程" value="flow2" />
        </el-select>
      </el-form-item>
      <el-form-item label="紧急程度" prop="urgentLevel">
        <el-select v-model="form.urgentLevel" placeholder="请选择紧急程度">
          <el-option label="一般" value="normal" />
          <el-option label="紧急" value="urgent" />
          <el-option label="非常紧急" value="very_urgent" />
        </el-select>
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入相关描述" />
      </el-form-item>
      <el-form-item label="图片" prop="images">
        <el-upload action="#" list-type="picture-card" :auto-upload="false" :limit="3" :on-change="handleImageChange">
          <el-icon><plus /></el-icon>
        </el-upload>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogFormVisible = false">取消</el-button>
      <el-button type="primary" @click="save">确定</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { createWorkOrder } from '/@/api/workOrder'
import { getEquipmentList } from '/@/api/equipmentManagement'
import { Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'WorkOrderEdit' })

const emit = defineEmits(['fetch-data'])
const $baseMessage = inject<any>('$baseMessage')
const formRef = ref<any>(null)
const form = reactive<any>({
  location: '', flow: '', urgentLevel: 'normal', description: '', images: [], source: '手动报单', equipmentId: '', equipmentName: '',
})
const title = ref<string>('')
const dialogFormVisible = ref<boolean>(false)
const rules = reactive<any>({
  location: [{ required: true, trigger: 'blur', message: '请输入报事房间' }],
  flow: [{ required: true, trigger: 'change', message: '请选择报事流程' }],
  urgentLevel: [{ required: true, trigger: 'change', message: '请选择紧急程度' }],
  description: [{ required: true, trigger: 'blur', message: '请输入描述' }],
  source: [{ required: true, trigger: 'change', message: '请选择报修来源' }],
})

const equipmentOptions = ref<any[]>([])
const equipmentLoading = ref<boolean>(false)
const selectedEquipment = ref<any>(null)

const equipmentStatusTag = (status: string): string => {
  switch (status) { case 'online': return 'success'; case 'offline': return 'danger'; case 'maintaining': return 'warning'; default: return 'info' }
}

const equipmentStatusText = (status: string): string => {
  switch (status) { case 'online': return '在线'; case 'offline': return '离线'; case 'maintaining': return '维护中'; default: return status || '未知' }
}

const remoteSearchEquipment = async (query: string) => {
  if (!query || query.trim() === '') { equipmentOptions.value = []; return }
  equipmentLoading.value = true
  try {
    const res: any = await getEquipmentList({ keyword: query, page: 1, pageSize: 20 })
    equipmentOptions.value = res.data?.list || []
  } catch { equipmentOptions.value = [] }
  finally { equipmentLoading.value = false }
}

const handleEquipmentChange = (val: string | number | undefined) => {
  if (!val) { selectedEquipment.value = null; form.equipmentName = ''; return }
  const eq = equipmentOptions.value.find((item: any) => item.id === val)
  if (eq) { selectedEquipment.value = eq; form.equipmentName = eq.name }
  else { selectedEquipment.value = null; form.equipmentName = '' }
}

const showEdit = () => {
  dialogFormVisible.value = true
  title.value = '新增工单'
  nextTick(() => {
    form.location = ''; form.flow = ''; form.urgentLevel = 'normal'; form.description = ''; form.images = []
    form.source = '手动报单'; form.equipmentId = ''; form.equipmentName = ''
    selectedEquipment.value = null; equipmentOptions.value = []
  })
}

defineExpose({ showEdit })

const handleImageChange = (file: any, fileList: any) => { form.images = fileList }

const close = () => { formRef.value.clearValidate(); formRef.value.resetFields(); emit('fetch-data') }

const save = () => {
  formRef.value.validate(async (valid: any) => {
    if (valid) {
      const { msg }: any = await createWorkOrder(form)
      if ($baseMessage) { $baseMessage(msg || '操作成功', 'success', 'hey') }
      else { ElMessage.success(msg || '操作成功') }
      close()
      dialogFormVisible.value = false
    }
  })
}
</script>

<style scoped>
.equipment-info-card { margin-top: 8px; padding: 10px 12px; border: 1px solid var(--el-border-color-light); border-radius: var(--el-border-radius-base); background-color: var(--el-color-info-light-9); font-size: 13px; }
.info-row { display: flex; line-height: 1.8; }
.info-label { width: 80px; color: var(--el-text-color-secondary); flex-shrink: 0; }
.info-value { color: var(--el-text-color-primary); flex: 1; }
</style>
```

## 后30页
请在此粘贴后30页的连续源代码片段，按照页码顺序组织。

```
<template>
  <div class="process-container">
    <vab-query-form>
      <vab-query-form-left-panel>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增流程</el-button>
      </vab-query-form-left-panel>
    </vab-query-form>
    <el-table v-loading="loading" :data="list" border>
      <el-table-column prop="name" label="流程名称" />
      <el-table-column label="节点数">
        <template #default="{ row }">{{ row.nodes.length }}</template>
      </el-table-column>
      <el-table-column prop="createTime" label="创建时间" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <process-edit ref="editRef" @fetch-data="fetchData" />
  </div>
</template>

<script lang="ts" setup>
import { getProcessList, deleteProcess } from '/@/api/workOrder'
import ProcessEdit from './vabAutoComponents/ProcessEdit.vue'
import { Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'WorkOrderProcess' })

const list = ref([])
const loading = ref(true)
const editRef = ref<any>(null)

const fetchData = async () => {
  loading.value = true
  const { data } = await getProcessList({})
  list.value = data.list
  loading.value = false
}

const handleAdd = () => { editRef.value.showEdit() }
const handleEdit = (row: any) => { editRef.value.showEdit(row) }

const handleDelete = (row: any) => {
  ElMessageBox.confirm('确认删除该流程?', '提示', { type: 'warning' }).then(async () => {
    await deleteProcess(row.id)
    ElMessage.success('删除成功')
    fetchData()
  })
}

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.process-container { padding: 20px; background: #fff; }
</style>

<template>
  <el-dialog v-model="dialogVisible" :title="title" width="860px" destroy-on-close>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="流程名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入流程名称" />
      </el-form-item>
      <el-form-item label="流程节点">
        <el-table :data="form.nodes" border style="width: 100%">
          <el-table-column label="节点名称" prop="name" width="160">
            <template #default="{ row }"><el-input v-model="row.name" size="small" placeholder="节点名称" /></template>
          </el-table-column>
          <el-table-column label="节点类型" width="140">
            <template #default="{ row }">
              <el-select v-model="row.type" size="small" style="width: 120px" placeholder="选择类型" @change="onNodeTypeChange(row)">
                <el-option v-for="nt in nodeTypes" :key="nt.value" :label="nt.label" :value="nt.value">
                  <span style="display: flex; align-items: center; gap: 6px">
                    <el-tag :type="nt.tagType" size="small" disable-transitions>{{ nt.label }}</el-tag>
                  </span>
                </el-option>
              </el-select>
              <div style="margin-top: 4px">
                <el-tag v-if="row.type" :type="getNodeTagType(row.type)" size="small" effect="plain">{{ getNodeLabel(row.type) }}</el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="处理人" prop="handlers" min-width="200">
            <template #default="{ row }">
              <el-select v-model="row.handlers" multiple placeholder="选择人员" size="small" style="width: 100%">
                <el-option label="张三" value="zhangsan" /><el-option label="李四" value="lisi" />
                <el-option label="王五" value="wangwu" /><el-option label="赵六" value="zhaoliu" />
                <el-option label="系统" value="system" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" fixed="right">
            <template #default="{ $index }"><el-button type="danger" link @click="removeNode($index)">删除</el-button></template>
          </el-table-column>
        </el-table>
        <el-button type="primary" link :icon="Plus" style="margin-top: 10px" @click="addNode">添加节点</el-button>
      </el-form-item>
      <el-form-item label="升级规则">
        <el-collapse v-model="escalationCollapse" style="width: 100%">
          <el-collapse-item title="超时升级规则配置" name="escalation">
            <template #title>
              <div style="display: flex; align-items: center; gap: 8px; font-weight: 600">
                <span>超时升级规则</span>
                <el-tag type="warning" size="small">{{ form.escalationRules.length }} 条规则</el-tag>
              </div>
            </template>
            <el-table :data="form.escalationRules" border style="width: 100%">
              <el-table-column label="关联节点" width="150">
                <template #default="{ row }">
                  <el-select v-model="row.nodeName" size="small" placeholder="选择节点" style="width: 130px">
                    <el-option v-for="node in form.nodes" :key="node.name" :label="node.name" :value="node.name" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="超时时长" width="200">
                <template #default="{ row }">
                  <div style="display: flex; align-items: center; gap: 4px">
                    <el-input-number v-model="row.timeoutMinutes" :min="1" :max="1440" size="small" style="width: 110px" placeholder="时长" />
                    <span style="color: #909399; font-size: 12px; white-space: nowrap">分钟</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="升级对象" min-width="130">
                <template #default="{ row }"><el-input v-model="row.escalateTo" size="small" placeholder="升级对象" /></template>
              </el-table-column>
              <el-table-column label="通知方式" width="200">
                <template #default="{ row }">
                  <el-checkbox-group v-model="row.notifyMethods" size="small">
                    <el-checkbox label="短信" value="短信" /><el-checkbox label="电话" value="电话" /><el-checkbox label="飞书" value="飞书" />
                  </el-checkbox-group>
                </template>
              </el-table-column>
              <el-table-column label="启用" width="70" align="center">
                <template #default="{ row }"><el-switch v-model="row.enabled" size="small" /></template>
              </el-table-column>
              <el-table-column label="操作" width="70" fixed="right">
                <template #default="{ $index }"><el-button type="danger" link @click="removeEscalationRule($index)">删除</el-button></template>
              </el-table-column>
            </el-table>
            <el-button type="primary" link :icon="Plus" style="margin-top: 10px" @click="addEscalationRule">添加升级规则</el-button>
          </el-collapse-item>
        </el-collapse>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="save">保存</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { saveProcess } from '/@/api/workOrder'
import { Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'ProcessEdit' })

interface NodeType { label: string; value: string; tagType: string }
interface Node { name: string; type: string; handlers: string[] }
interface EscalationRule { nodeName: string; timeoutMinutes: number; escalateTo: string; notifyMethods: string[]; enabled: boolean }
interface Form { id: string; name: string; nodes: Node[]; escalationRules: EscalationRule[] }

const nodeTypes: NodeType[] = [
  { label: '派发', value: 'dispatch', tagType: 'primary' },
  { label: '接单', value: 'accept', tagType: 'success' },
  { label: '处置', value: 'handle', tagType: 'warning' },
  { label: '验收', value: 'verify', tagType: 'info' },
  { label: '归档', value: 'archive', tagType: '' },
]

const nodeTypeMap = new Map<string, NodeType>(nodeTypes.map((nt) => [nt.value, nt]))

const getNodeTagType = (type: string): string => { return nodeTypeMap.get(type)?.tagType ?? '' }
const getNodeLabel = (type: string): string => { return nodeTypeMap.get(type)?.label ?? type }

const onNodeTypeChange = (row: Node): void => {
  const label = getNodeLabel(row.type)
  if (label && !row.name) row.name = label
}

const emit = defineEmits(['fetch-data'])
const dialogVisible = ref(false)
const title = ref('')
const formRef = ref<any>(null)
const escalationCollapse = ref(['escalation'])

const form = reactive<Form>({ id: '', name: '', nodes: [], escalationRules: [] })
const rules = { name: [{ required: true, message: '请输入流程名称', trigger: 'blur' }] }

const showEdit = (row?: any): void => {
  dialogVisible.value = true
  escalationCollapse.value = ['escalation']
  if (row) {
    title.value = '编辑流程'
    form.id = row.id || ''; form.name = row.name || ''
    form.nodes = row.nodes ? JSON.parse(JSON.stringify(row.nodes)) : []
    form.escalationRules = row.escalationRules ? JSON.parse(JSON.stringify(row.escalationRules)) : []
  } else {
    title.value = '新增流程'
    form.id = ''; form.name = ''; form.nodes = []; form.escalationRules = []
  }
}

const addNode = (): void => { form.nodes.push({ name: '', type: '', handlers: [] }) }
const removeNode = (index: number): void => { form.nodes.splice(index, 1) }

const addEscalationRule = (): void => {
  form.escalationRules.push({ nodeName: '', timeoutMinutes: 30, escalateTo: '', notifyMethods: ['飞书'], enabled: true })
}

const removeEscalationRule = (index: number): void => { form.escalationRules.splice(index, 1) }

const save = async (): Promise<void> => {
  await formRef.value.validate()
  await saveProcess({ ...form })
  ElMessage.success('保存成功')
  dialogVisible.value = false
  emit('fetch-data')
}

defineExpose({ showEdit })
</script>

<template>
  <div class="service-type-container">
    <vab-query-form>
      <vab-query-form-left-panel>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增模板</el-button>
      </vab-query-form-left-panel>
    </vab-query-form>
    <el-table v-loading="loading" :data="list" border row-key="id" default-expand-all>
      <el-table-column prop="name" label="模板名称/服务名称" />
      <el-table-column prop="project" label="项目名称" />
      <el-table-column prop="scope" label="应用范围" />
      <el-table-column prop="updateTime" label="更新时间" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <template v-if="!row.parentId && row.children">
            <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>
    <service-type-edit ref="editRef" @fetch-data="fetchData" />
  </div>
</template>

<script lang="ts" setup>
import { getServiceTypeList, deleteServiceType } from '/@/api/workOrder'
import ServiceTypeEdit from './vabAutoComponents/ServiceTypeEdit.vue'
import { Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'ServiceType' })

const list = ref([])
const loading = ref(true)
const editRef = ref<any>(null)

const fetchData = async () => {
  loading.value = true
  const { data } = await getServiceTypeList({})
  list.value = data.list
  loading.value = false
}

const handleAdd = () => { editRef.value.showEdit() }
const handleEdit = (row: any) => { editRef.value.showEdit(row) }

const handleDelete = (row: any) => {
  ElMessageBox.confirm('确认删除该模板?', '提示', { type: 'warning' }).then(async () => {
    await deleteServiceType(row.id)
    ElMessage.success('删除成功')
    fetchData()
  })
}

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.service-type-container { padding: 20px; background: #fff; }
</style>

<template>
  <el-dialog v-model="dialogVisible" :title="title" width="700px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="模板名称" prop="name"><el-input v-model="form.name" placeholder="请输入模板名称" /></el-form-item>
      <el-form-item label="项目名称" prop="project"><el-input v-model="form.project" placeholder="请输入项目名称" /></el-form-item>
      <el-form-item label="应用范围" prop="scope">
        <el-select v-model="form.scope" placeholder="请选择应用范围">
          <el-option label="全部" value="all" /><el-option label="部分流程" value="partial" />
        </el-select>
      </el-form-item>
      <div style="margin-bottom: 10px; font-weight: bold">服务类型定义</div>
      <el-table :data="form.children" border row-key="id">
        <el-table-column label="服务名称" prop="name">
          <template #default="{ row }"><el-input v-model="row.name" size="small" /></template>
        </el-table-column>
        <el-table-column label="排序" prop="sort" width="100">
          <template #default="{ row }"><el-input-number v-model="row.sort" size="small" :min="1" /></template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row, $index }">
            <el-button v-if="!row.parentId" type="primary" link @click="addChild(row)">添加子类</el-button>
            <el-button type="danger" link @click="removeType(form.children, $index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-button type="primary" link icon="Plus" style="margin-top: 10px" @click="addParent">添加一级分类</el-button>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="save">保存</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { saveServiceType } from '/@/api/workOrder'
import { uuid } from '/@/utils'

defineOptions({ name: 'ServiceTypeEdit' })

const emit = defineEmits(['fetch-data'])
const dialogVisible = ref(false)
const title = ref('')
const formRef = ref<any>(null)
const form = reactive<any>({ id: '', name: '', project: '', scope: '', children: [] })

const rules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  project: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
}

const showEdit = (row?: any) => {
  dialogVisible.value = true
  if (row) {
    title.value = '编辑服务类型'
    Object.assign(form, JSON.parse(JSON.stringify(row)))
  } else {
    title.value = '新增服务类型'
    form.id = ''; form.name = ''; form.project = ''; form.scope = ''; form.children = []
  }
}

const addParent = () => { form.children.push({ id: uuid(), name: '', sort: 1, children: [] }) }
const addChild = (row: any) => { if (!row.children) row.children = []; row.children.push({ id: uuid(), name: '', sort: 1, parentId: row.id }) }
const removeType = (list: any[], index: number) => { list.splice(index, 1) }

const save = async () => {
  await formRef.value.validate()
  await saveServiceType(form)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  emit('fetch-data')
}

defineExpose({ showEdit })
</script>

<template>
  <div class="sla-container">
    <vab-query-form>
      <vab-query-form-left-panel>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增时效</el-button>
      </vab-query-form-left-panel>
    </vab-query-form>
    <el-table v-loading="loading" :data="list" border>
      <el-table-column prop="name" label="规则名称" />
      <el-table-column label="类型">
        <template #default="{ row }"><el-tag>{{ row.isGlobal ? '全局时效' : '节点时效' }}</el-tag></template>
      </el-table-column>
      <el-table-column label="一般" width="320">
        <template #default="{ row }">
          <div class="sla-triad-cell">
            <span>响应 {{ formatTimeout(row.normal, row.unit) }}</span>
            <span>挂起 {{ formatTimeout(row.normal, row.unit, 'suspend') }}</span>
            <span>完成 {{ formatTimeout(row.normal, row.unit, 'completion') }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="紧急" width="320">
        <template #default="{ row }">
          <div class="sla-triad-cell">
            <span>响应 {{ formatTimeout(row.urgent, row.unit) }}</span>
            <span>挂起 {{ formatTimeout(row.urgent, row.unit, 'suspend') }}</span>
            <span>完成 {{ formatTimeout(row.urgent, row.unit, 'completion') }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="非常紧急" width="320">
        <template #default="{ row }">
          <div class="sla-triad-cell">
            <span>响应 {{ formatTimeout(row.veryUrgent, row.unit) }}</span>
            <span>挂起 {{ formatTimeout(row.veryUrgent, row.unit, 'suspend') }}</span>
            <span>完成 {{ formatTimeout(row.veryUrgent, row.unit, 'completion') }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <sla-edit ref="editRef" @fetch-data="fetchData" />
  </div>
</template>

<script lang="ts" setup>
import { getSlaList, saveSla } from '/@/api/workOrder'
import SlaEdit from './vabAutoComponents/SlaEdit.vue'
import { Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'WorkOrderSla' })

const list = ref([])
const loading = ref(true)
const editRef = ref<any>(null)

const fetchData = async () => {
  loading.value = true
  const { data } = await getSlaList({})
  list.value = data.list
  loading.value = false
}

const getUnitText = (unit: string) => {
  switch (unit) { case 'minute': return '分钟'; case 'hour': return '小时'; case 'day': return '天'; default: return '' }
}

const formatTimeout = (sla: any, unit: string, key: string = 'response') => {
  if (!sla) return '-'
  if (typeof sla === 'number') return `${sla} ${getUnitText(unit)}`
  return `${sla[key] || 0} ${getUnitText(unit)}`
}

const handleAdd = () => { editRef.value.showEdit() }
const handleEdit = (row: any) => { editRef.value.showEdit(row) }

const handleDelete = (row: any) => {
  ElMessageBox.confirm('确认删除该规则?', '提示', { type: 'warning' }).then(async () => {
    ElMessage.success('删除成功')
    fetchData()
  })
}

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.sla-container { padding: 20px; background: #fff; }
.sla-triad-cell { display: flex; flex-direction: column; gap: 2px; font-size: 13px; line-height: 1.6; }
</style>

<template>
  <el-dialog v-model="dialogVisible" :title="title" width="800px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="规则名称" prop="name"><el-input v-model="form.name" placeholder="请输入规则名称" /></el-form-item>
      <el-form-item label="类型">
        <el-radio-group v-model="form.isGlobal">
          <el-radio :label="true">全局流程时效</el-radio>
          <el-radio :label="false">流程节点时效</el-radio>
        </el-radio-group>
      </el-form-item>
      <template v-if="!form.isGlobal">
        <el-form-item label="关联节点" prop="nodeId">
          <el-select v-model="form.nodeId" placeholder="请选择节点">
            <el-option label="接单" value="node1" /><el-option label="处理" value="node2" />
          </el-select>
        </el-form-item>
        <el-form-item label="启用状态"><el-switch v-model="form.enabled" /></el-form-item>
      </template>
      <el-divider>时效设置</el-divider>
      <el-form-item label="时间单位" prop="unit">
        <el-select v-model="form.unit" style="width: 120px">
          <el-option label="分钟" value="minute" /><el-option label="小时" value="hour" /><el-option label="天" value="day" />
        </el-select>
      </el-form-item>
      <div class="sla-triad-grid">
        <div class="sla-triad-header">
          <div class="sla-triad-col-priority">优先级</div>
          <div class="sla-triad-col-field">响应超时</div>
          <div class="sla-triad-col-field">挂起超时</div>
          <div class="sla-triad-col-field">完成超时</div>
        </div>
        <div class="sla-triad-row">
          <div class="sla-triad-col-priority">一般</div>
          <div class="sla-triad-col-field"><el-form-item prop="normal.response"><el-input v-model.number="form.normal.response" placeholder="时长" /></el-form-item></div>
          <div class="sla-triad-col-field"><el-form-item prop="normal.suspend"><el-input v-model.number="form.normal.suspend" placeholder="时长" /></el-form-item></div>
          <div class="sla-triad-col-field"><el-form-item prop="normal.completion"><el-input v-model.number="form.normal.completion" placeholder="时长" /></el-form-item></div>
        </div>
        <div class="sla-triad-row">
          <div class="sla-triad-col-priority">紧急</div>
          <div class="sla-triad-col-field"><el-form-item prop="urgent.response"><el-input v-model.number="form.urgent.response" placeholder="时长" /></el-form-item></div>
          <div class="sla-triad-col-field"><el-form-item prop="urgent.suspend"><el-input v-model.number="form.urgent.suspend" placeholder="时长" /></el-form-item></div>
          <div class="sla-triad-col-field"><el-form-item prop="urgent.completion"><el-input v-model.number="form.urgent.completion" placeholder="时长" /></el-form-item></div>
        </div>
        <div class="sla-triad-row">
          <div class="sla-triad-col-priority">非常紧急</div>
          <div class="sla-triad-col-field"><el-form-item prop="veryUrgent.response"><el-input v-model.number="form.veryUrgent.response" placeholder="时长" /></el-form-item></div>
          <div class="sla-triad-col-field"><el-form-item prop="veryUrgent.suspend"><el-input v-model.number="form.veryUrgent.suspend" placeholder="时长" /></el-form-item></div>
          <div class="sla-triad-col-field"><el-form-item prop="veryUrgent.completion"><el-input v-model.number="form.veryUrgent.completion" placeholder="时长" /></el-form-item></div>
        </div>
      </div>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="save">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { saveSla } from '/@/api/workOrder'

defineOptions({ name: 'SlaEdit' })

const emit = defineEmits(['fetch-data'])
const dialogVisible = ref(false)
const title = ref('')
const formRef = ref<any>(null)

const createEmptySla = () => ({
  id: '', name: '', isGlobal: true, nodeId: '', enabled: true,
  normal: { response: 480, suspend: 960, completion: 1440 },
  urgent: { response: 120, suspend: 240, completion: 480 },
  veryUrgent: { response: 30, suspend: 60, completion: 120 },
  nodes: [], unit: 'minute',
})

const form = reactive<any>(createEmptySla())

const rules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  'normal.response': [{ required: true, message: '请输入响应超时时长', trigger: 'blur' }],
  'normal.suspend': [{ required: true, message: '请输入挂起超时时长', trigger: 'blur' }],
  'normal.completion': [{ required: true, message: '请输入完成超时时长', trigger: 'blur' }],
  'urgent.response': [{ required: true, message: '请输入响应超时时长', trigger: 'blur' }],
  'urgent.suspend': [{ required: true, message: '请输入挂起超时时长', trigger: 'blur' }],
  'urgent.completion': [{ required: true, message: '请输入完成超时时长', trigger: 'blur' }],
  'veryUrgent.response': [{ required: true, message: '请输入响应超时时长', trigger: 'blur' }],
  'veryUrgent.suspend': [{ required: true, message: '请输入挂起超时时长', trigger: 'blur' }],
  'veryUrgent.completion': [{ required: true, message: '请输入完成超时时长', trigger: 'blur' }],
}

const normalizeRow = (row: any) => {
  for (const key of ['normal', 'urgent', 'veryUrgent'] as const) {
    if (row[key] && typeof row[key] === 'number') {
      const val = row[key]
      row[key] = { response: val, suspend: val * 2, completion: val * 4 }
    }
  }
  return row
}

const showEdit = (row?: any) => {
  dialogVisible.value = true
  if (row) {
    title.value = '编辑时效'
    const data = JSON.parse(JSON.stringify(row))
    normalizeRow(data)
    Object.assign(form, data)
  } else {
    title.value = '新增时效'
    Object.assign(form, createEmptySla())
  }
}

const save = async () => {
  await formRef.value.validate()
  await saveSla(form)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  emit('fetch-data')
}

defineExpose({ showEdit })
</script>

<style lang="scss" scoped>
.sla-triad-grid { width: 100%; }
.sla-triad-header { display: flex; background: #f5f7fa; padding: 8px 0; border-radius: 4px; margin-bottom: 8px; font-weight: bold; font-size: 13px; color: #606266; }
.sla-triad-row { display: flex; align-items: flex-start; margin-bottom: 6px; }
.sla-triad-col-priority { width: 80px; text-align: center; flex-shrink: 0; line-height: 32px; font-size: 13px; color: #303133; }
.sla-triad-col-field { flex: 1; padding: 0 4px; }
</style>

<template>
  <div class="assign-rule-container">
    <vab-query-form>
      <vab-query-form-left-panel>
        <el-form inline :model="queryForm" @submit.prevent>
          <el-form-item label="适用区域">
            <el-select v-model="queryForm.area" clearable placeholder="全部区域" @change="onFilterChange">
              <el-option label="全部区域" value="" /><el-option label="A栋" value="A栋" />
              <el-option label="B栋" value="B栋" /><el-option label="C栋" value="C栋" />
            </el-select>
          </el-form-item>
          <el-form-item label="工单类型">
            <el-select v-model="queryForm.typeName" clearable placeholder="全部类型" @change="onFilterChange">
              <el-option label="全部类型" value="" />
              <el-option v-for="t in serviceTypes" :key="t.id" :label="t.name" :value="t.name" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="queryForm.enabled" clearable placeholder="全部" @change="onFilterChange">
              <el-option label="启用" :value="true" /><el-option label="禁用" :value="false" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="Search" @click="fetchData">查询</el-button>
            <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </vab-query-form-left-panel>
      <vab-query-form-right-panel>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增规则</el-button>
      </vab-query-form-right-panel>
    </vab-query-form>
    <el-table v-loading="loading" :data="list" border stripe>
      <el-table-column type="index" label="序号" width="55" align="center" />
      <el-table-column prop="typeName" label="工单类型" width="120" />
      <el-table-column prop="area" label="适用区域" width="90" />
      <el-table-column prop="floor" label="适用楼层" width="90" />
      <el-table-column label="工单等级" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="priorityTagType(row.priorityLevel)" effect="dark" size="small">{{ row.priorityLevel }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="defaultHandler" label="默认处理人" width="100" />
      <el-table-column prop="handlerGroup" label="处理小组" width="100" />
      <el-table-column label="抄送人" width="140" show-overflow-tooltip>
        <template #default="{ row }">{{ row.ccUsers?.length ? row.ccUsers.join(', ') : '—' }}</template>
      </el-table-column>
      <el-table-column prop="confirmer" label="确认人" width="90" />
      <el-table-column label="超时设置(响应/挂起/完成)" min-width="260">
        <template #default="{ row }">
          <span class="timeout-text">
            响应 {{ row.responseTimeout }}{{ getUnitText(row.timeoutUnit) }} / 挂起 {{ row.suspendTimeout }}{{ getUnitText(row.timeoutUnit) }} / 完成 {{ row.completionTimeout }}{{ getUnitText(row.timeoutUnit) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-switch :model-value="row.enabled" :loading="row._toggling" @change="(val) => handleToggle(row, val)" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right" align="center">
        <template #default="{ row }">
          <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination background
      :current-page="queryForm.pageNo" layout="total, sizes, prev, pager, next, jumper"
      :page-size="queryForm.pageSize" :total="total"
      @current-change="(v) => { queryForm.pageNo = v; fetchData() }"
      @size-change="(v) => { queryForm.pageSize = v; queryForm.pageNo = 1; fetchData() }"
    />
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑分配规则' : '新增分配规则'" width="680px" :close-on-click-modal="false" @close="handleDialogClose">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工单类型" prop="typeId">
              <el-select v-model="form.typeId" placeholder="请选择工单类型" style="width: 100%">
                <el-option v-for="t in serviceTypes" :key="t.id" :label="t.name" :value="t.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="适用区域" prop="area">
              <el-select v-model="form.area" placeholder="请选择区域" style="width: 100%">
                <el-option label="全部" value="全部" /><el-option label="A栋" value="A栋" />
                <el-option label="B栋" value="B栋" /><el-option label="C栋" value="C栋" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="适用楼层" prop="floor">
              <el-select v-model="form.floor" placeholder="请选择楼层" style="width: 100%">
                <el-option label="全部" value="全部" /><el-option label="B1" value="B1" />
                <el-option label="1F" value="1F" /><el-option label="2F" value="2F" /><el-option label="3F" value="3F" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工单等级" prop="priorityLevel">
              <el-select v-model="form.priorityLevel" placeholder="请选择等级" style="width: 100%">
                <el-option label="一般" value="一般" /><el-option label="紧急" value="紧急" /><el-option label="非常紧急" value="非常紧急" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="默认处理人" prop="defaultHandler"><el-input v-model="form.defaultHandler" placeholder="请输入处理人姓名" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="处理小组" prop="handlerGroup"><el-input v-model="form.handlerGroup" placeholder="请输入小组名称" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="抄送人" prop="ccUsers">
              <el-select v-model="form.ccUsers" multiple placeholder="请选择抄送人" style="width: 100%">
                <el-option v-for="u in userOptions" :key="u" :label="u" :value="u" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="确认人" prop="confirmer">
              <el-select v-model="form.confirmer" placeholder="请选择确认人" style="width: 100%">
                <el-option v-for="u in userOptions" :key="u" :label="u" :value="u" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider content-position="left">超时设置</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="响应超时" prop="responseTimeout"><el-input-number v-model="form.responseTimeout" :min="0" :max="99999" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="挂起超时" prop="suspendTimeout"><el-input-number v-model="form.suspendTimeout" :min="0" :max="99999" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="完成超时" prop="completionTimeout"><el-input-number v-model="form.completionTimeout" :min="0" :max="99999" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="超时单位" prop="timeoutUnit" style="margin-top: 18px">
          <el-select v-model="form.timeoutUnit" style="width: 200px">
            <el-option label="分钟" value="minute" /><el-option label="小时" value="hour" />
          </el-select>
        </el-form-item>
        <el-divider content-position="left">其他设置</el-divider>
        <el-form-item label="启用"><el-switch v-model="form.enabled" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { getAssignRuleList, saveAssignRule, deleteAssignRule, toggleAssignRule } from '/@/api/workOrder'

defineOptions({ name: 'AssignRule' })

const $baseMessage = inject<any>('$baseMessage')
const $baseConfirm = inject<any>('$baseConfirm')

const loading = ref(false)
const submitting = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<any>(null)

const queryForm = reactive({ area: '', typeName: '', enabled: undefined as boolean | undefined, pageNo: 1, pageSize: 10 })

const serviceTypes = [
  { id: '1-1', name: '强电维修' }, { id: '1-2', name: '弱电维修' },
  { id: '1-3', name: '空调维修' }, { id: '1-4', name: '给排水维修' }, { id: '1-5', name: '土建维修' },
]

const userOptions = ['王经理', '陈经理', '刘经理', '赵主管', '周主管']

const initForm = () => ({
  id: '', typeId: '', typeName: '', area: '', floor: '', defaultHandler: '', handlerGroup: '',
  ccUsers: [] as string[], confirmer: '', priorityLevel: '一般',
  responseTimeout: 30, suspendTimeout: 120, completionTimeout: 240, timeoutUnit: 'minute', enabled: true,
})

const form = ref<any>(initForm())

const rules = {
  typeId: [{ required: true, message: '请选择工单类型', trigger: 'change' }],
  area: [{ required: true, message: '请选择适用区域', trigger: 'change' }],
  priorityLevel: [{ required: true, message: '请选择工单等级', trigger: 'change' }],
}

watch(() => form.value.typeId, (val) => { const type = serviceTypes.find((t) => t.id === val); if (type) form.value.typeName = type.name })

const getUnitText = (unit: string) => { switch (unit) { case 'minute': return '分钟'; case 'hour': return '小时'; default: return '' } }

const priorityTagType = (level: string) => {
  switch (level) { case '一般': return 'success'; case '紧急': return 'warning'; case '非常紧急': return 'danger'; default: return 'info' }
}

const onFilterChange = () => { queryForm.pageNo = 1; fetchData() }

const fetchData = async () => {
  loading.value = true
  try {
    const params: any = { pageNo: queryForm.pageNo, pageSize: queryForm.pageSize }
    if (queryForm.area) params.area = queryForm.area
    if (queryForm.typeName) params.typeName = queryForm.typeName
    if (queryForm.enabled !== undefined) params.enabled = queryForm.enabled
    const { data } = await getAssignRuleList(params)
    list.value = (data.list || []).map((item: any) => ({ ...item, _toggling: false }))
    total.value = data.total || 0
  } catch { $baseMessage?.error('获取分配规则列表失败') }
  finally { loading.value = false }
}

const handleReset = () => { queryForm.area = ''; queryForm.typeName = ''; queryForm.enabled = undefined; queryForm.pageNo = 1; fetchData() }
const handleAdd = () => { isEdit.value = false; form.value = initForm(); dialogVisible.value = true }

const handleEdit = (row: any) => {
  isEdit.value = true
  form.value = {
    id: row.id, typeId: row.typeId, typeName: row.typeName, area: row.area, floor: row.floor,
    defaultHandler: row.defaultHandler, handlerGroup: row.handlerGroup,
    ccUsers: [...(row.ccUsers || [])], confirmer: row.confirmer, priorityLevel: row.priorityLevel,
    responseTimeout: row.responseTimeout, suspendTimeout: row.suspendTimeout,
    completionTimeout: row.completionTimeout, timeoutUnit: row.timeoutUnit || 'minute', enabled: row.enabled,
  }
  dialogVisible.value = true
}

const handleDialogClose = () => { formRef.value?.resetFields() }

const handleSave = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await saveAssignRule({ ...form.value })
    $baseMessage?.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    await fetchData()
  } catch { $baseMessage?.error('保存失败') }
  finally { submitting.value = false }
}

const handleDelete = (row: any) => {
  $baseConfirm?.('确认删除该分配规则？', '删除确认').then(async () => {
    try { await deleteAssignRule(row.id); $baseMessage?.success('删除成功'); await fetchData() }
    catch { $baseMessage?.error('删除失败') }
  }).catch(() => {})
}

const handleToggle = async (row: any, val: boolean) => {
  row._toggling = true
  try { await toggleAssignRule(row.id); row.enabled = val; $baseMessage?.success(val ? '已启用' : '已禁用') }
  catch { row.enabled = !val; $baseMessage?.error('操作失败') }
  finally { row._toggling = false }
}

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.assign-rule-container { padding: 20px; background: #fff; }
.timeout-text { font-size: 13px; white-space: nowrap; }
</style>

<template>
  <div class="inspection-route-container">
    <vab-query-form>
      <vab-query-form-left-panel>
        <el-form :inline="true" @submit.prevent>
          <el-form-item label="适用区域">
            <el-select v-model="queryForm.area" placeholder="全部区域" clearable @change="fetchData">
              <el-option label="全部区域" value="" /><el-option label="A栋" value="A栋" />
              <el-option label="B栋" value="B栋" /><el-option label="C栋" value="C栋" />
            </el-select>
          </el-form-item>
          <el-form-item label="周期状态">
            <el-select v-model="queryForm.status" placeholder="全部" clearable @change="fetchData">
              <el-option label="全部" value="" /><el-option label="已启用" value="enabled" /><el-option label="已停用" value="disabled" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </vab-query-form-left-panel>
      <vab-query-form-right-panel>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增路线</el-button>
      </vab-query-form-right-panel>
    </vab-query-form>
    <el-table v-loading="loading" :data="list" border row-key="id" @expand-change="handleExpandChange">
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="checkpoint-detail">
            <h4>检查点列表</h4>
            <el-table :data="row.checkpoints" border size="small">
              <el-table-column prop="order" label="序号" width="70" />
              <el-table-column prop="name" label="检查点名称" />
              <el-table-column prop="nfcCode" label="NFC编号" />
            </el-table>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="路线名称" min-width="160" />
      <el-table-column prop="area" label="适用区域" width="120" />
      <el-table-column label="检查点数量" width="110" align="center">
        <template #default="{ row }"><el-tag>{{ row.checkpoints?.length || 0 }} 个</el-tag></template>
      </el-table-column>
      <el-table-column label="周期规则" width="200">
        <template #default="{ row }"><span>{{ formatPeriodicRule(row.periodicRule) }}</span></template>
      </el-table-column>
      <el-table-column label="自动生成" width="110" align="center">
        <template #default="{ row }">
          <el-switch v-model="row.autoCreateWorkOrder" :loading="row._toggling" @change="(val) => handleToggleAuto(row, val)" />
        </template>
      </el-table-column>
      <el-table-column label="上次执行" width="170">
        <template #default="{ row }"><span>{{ row.lastRunTime || '-' }}</span></template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑巡检路线' : '新增巡检路线'" width="750px" :close-on-click-modal="false" @close="handleDialogClose">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px" label-position="right">
        <el-form-item label="路线名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入路线名称" maxlength="50" />
        </el-form-item>
        <el-form-item label="适用区域" prop="area">
          <el-select v-model="form.area" placeholder="请选择适用区域" style="width: 100%">
            <el-option label="A栋" value="A栋" /><el-option label="B栋" value="B栋" /><el-option label="C栋" value="C栋" />
          </el-select>
        </el-form-item>
        <el-form-item label="检查点" prop="checkpoints">
          <div class="checkpoint-table-wrapper">
            <el-table :data="form.checkpoints" border size="small" empty-text="暂无检查点，请添加">
              <el-table-column label="序号" width="60" type="index" />
              <el-table-column label="检查点名称" min-width="180">
                <template #default="{ row }"><el-input v-model="row.name" placeholder="请输入检查点名称" size="small" /></template>
              </el-table-column>
              <el-table-column label="NFC编号" min-width="180">
                <template #default="{ row }"><el-input v-model="row.nfcCode" placeholder="请输入NFC编号" size="small" /></template>
              </el-table-column>
              <el-table-column label="操作" width="80" align="center">
                <template #default="{ $index }"><el-button type="danger" text size="small" @click="removeCheckpoint($index)">删除</el-button></template>
              </el-table-column>
            </el-table>
            <el-button type="primary" text size="small" style="margin-top: 8px" @click="addCheckpoint">+ 新增检查点</el-button>
          </div>
        </el-form-item>
        <el-divider content-position="left">周期规则</el-divider>
        <el-form-item label="周期类型" prop="periodicRule.type">
          <el-select v-model="form.periodicRule.type" placeholder="请选择周期类型" style="width: 100%">
            <el-option label="每天" value="daily" /><el-option label="每周" value="weekly" /><el-option label="每月" value="monthly" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行时间" prop="periodicRule.time">
          <el-time-picker v-model="periodicTimeValue" placeholder="选择执行时间" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item v-if="form.periodicRule.type === 'weekly'" label="执行周几" prop="periodicRule.dayOfWeek">
          <el-select v-model="form.periodicRule.dayOfWeek" placeholder="请选择" style="width: 100%">
            <el-option v-for="d in weekDays" :key="d.value" :label="d.label" :value="d.value" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.periodicRule.type === 'monthly'" label="执行日期" prop="periodicRule.dayOfMonth">
          <el-input-number v-model="form.periodicRule.dayOfMonth" :min="1" :max="28" style="width: 100%" />
        </el-form-item>
        <el-divider content-position="left">工单设置</el-divider>
        <el-form-item label="自动生成工单"><el-switch v-model="form.autoCreateWorkOrder" /></el-form-item>
        <el-form-item v-if="form.autoCreateWorkOrder" label="关联工单类型" prop="workOrderType">
          <el-input v-model="form.workOrderType" placeholder="请输入工单类型名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { Plus } from '@element-plus/icons-vue'
import { getInspectionRouteList, saveInspectionRoute, deleteInspectionRoute, togglePeriodicGeneration } from '/@/api/workOrder'

defineOptions({ name: 'InspectionRoute' })

const $baseMessage = inject<any>('$baseMessage')
const $baseConfirm = inject<any>('$baseConfirm')

const list = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<any>(null)

const queryForm = reactive({ area: '', status: '' })

const weekDays = [
  { label: '周一', value: 1 }, { label: '周二', value: 2 }, { label: '周三', value: 3 },
  { label: '周四', value: 4 }, { label: '周五', value: 5 }, { label: '周六', value: 6 }, { label: '周日', value: 7 },
]

const initForm = () => ({
  id: '', name: '', area: '', checkpoints: [] as any[],
  periodicRule: { type: 'daily', time: '08:00', enabled: true, dayOfWeek: 1, dayOfMonth: 1 },
  autoCreateWorkOrder: false, workOrderType: '巡检工单', createTime: '', lastRunTime: '',
})

const form = ref<any>(initForm())

const periodicTimeValue = computed({
  get: () => form.value.periodicRule?.time || '08:00',
  set: (val) => { form.value.periodicRule.time = val },
})

const rules = {
  name: [{ required: true, message: '请输入路线名称', trigger: 'blur' }],
  area: [{ required: true, message: '请选择适用区域', trigger: 'change' }],
  checkpoints: [{
    validator: (_rule: any, value: any[], callback: Function) => {
      if (!value || value.length === 0) { callback(new Error('请至少添加一个检查点')) }
      else { const hasEmpty = value.some((cp) => !cp.name || !cp.nfcCode); hasEmpty ? callback(new Error('请填写完整的检查点信息')) : callback() }
    },
    trigger: 'change',
  }],
  'periodicRule.type': [{ required: true, message: '请选择周期类型', trigger: 'change' }],
}

const fetchData = async () => {
  loading.value = true
  try {
    const { data } = await getInspectionRouteList({ area: queryForm.area || undefined, status: queryForm.status || undefined })
    list.value = (data.list || []).map((item: any) => ({ ...item, _toggling: false }))
  } catch { $baseMessage?.error('获取巡检路线列表失败') }
  finally { loading.value = false }
}

const handleReset = () => { queryForm.area = ''; queryForm.status = ''; fetchData() }
const handleExpandChange = () => {}

const formatPeriodicRule = (rule: any) => {
  if (!rule) return '-'
  const { type, time, dayOfWeek, dayOfMonth } = rule
  switch (type) {
    case 'daily': return `每天 ${time || ''}`
    case 'weekly': { const dayLabel = weekDays.find((d) => d.value === dayOfWeek)?.label || ''; return `每周${dayLabel} ${time || ''}` }
    case 'monthly': return `每月${dayOfMonth}号 ${time || ''}`
    default: return '-'
  }
}

const addCheckpoint = () => { form.value.checkpoints.push({ id: `cp-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`, name: '', nfcCode: '', order: form.value.checkpoints.length + 1 }) }
const removeCheckpoint = (index: number) => { form.value.checkpoints.splice(index, 1); form.value.checkpoints.forEach((cp: any, i: number) => { cp.order = i + 1 }) }

const handleAdd = () => { isEdit.value = false; form.value = initForm(); dialogVisible.value = true }
const handleEdit = (row: any) => { isEdit.value = true; form.value = JSON.parse(JSON.stringify(row)); dialogVisible.value = true }
const handleDialogClose = () => { formRef.value?.resetFields() }

const handleSave = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    await saveInspectionRoute({ ...form.value, periodicRule: { ...form.value.periodicRule, enabled: form.value.autoCreateWorkOrder } })
    $baseMessage?.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    await fetchData()
  } catch { $baseMessage?.error('保存失败') }
  finally { saving.value = false }
}

const handleDelete = (row: any) => {
  $baseConfirm?.('确认删除该巡检路线？删除后不可恢复。', '删除确认').then(async () => {
    try { await deleteInspectionRoute(row.id); $baseMessage?.success('删除成功'); await fetchData() }
    catch { $baseMessage?.error('删除失败') }
  })
}

const handleToggleAuto = async (row: any, val: boolean) => {
  row._toggling = true
  try { await togglePeriodicGeneration(row.id); $baseMessage?.success(val ? '已启用自动生成' : '已停用自动生成') }
  catch { row.autoCreateWorkOrder = !val; $baseMessage?.error('操作失败') }
  finally { row._toggling = false }
}

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.inspection-route-container { padding: 20px; background: #fff; }
.checkpoint-detail { padding: 12px 16px; }
.checkpoint-detail h4 { margin: 0 0 8px; font-size: 14px; color: var(--el-text-color-secondary); }
.checkpoint-table-wrapper { width: 100%; }
</style>

<template>
  <div class="no-background-container table-auto-height">
    <vab-query-form>
      <vab-query-form-top-panel>
        <el-form :inline="true" :model="queryForm" @submit.prevent>
          <el-form-item label="区域">
            <el-select v-model="queryForm.area" clearable placeholder="全部区域" style="width: 140px">
              <el-option label="A栋" value="A栋" /><el-option label="B栋" value="B栋" /><el-option label="C栋" value="C栋" />
            </el-select>
          </el-form-item>
          <el-form-item label="楼层">
            <el-select v-model="queryForm.floor" clearable placeholder="全部楼层" style="width: 120px">
              <el-option label="B1" value="B1" /><el-option label="1F" value="1F" />
              <el-option label="2F" value="2F" /><el-option label="3F" value="3F" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
            <el-button @click="resetQuery">重置</el-button>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="Plus" @click="openGenerateDialog">生成二维码</el-button>
          </el-form-item>
        </el-form>
      </vab-query-form-top-panel>
    </vab-query-form>
    <el-table v-loading="listLoading" :data="list" border>
      <el-table-column align="center" label="序号" type="index" width="60" />
      <el-table-column label="区域" prop="area" width="100" />
      <el-table-column label="楼层" prop="floor" width="80" />
      <el-table-column label="房间" prop="room" min-width="140" />
      <el-table-column label="二维码链接" min-width="260">
        <template #default="{ row }">
          <div style="display: flex; align-items: center; gap: 8px">
            <el-tooltip :content="row.url" placement="top">
              <span style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 12px; color: var(--el-text-color-secondary)">{{ row.url }}</span>
            </el-tooltip>
            <el-button text size="small" type="primary" @click="copyUrl(row.url)">复制</el-button>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="扫描次数" prop="scanCount" width="90" align="center" />
      <el-table-column label="创建时间" prop="createTime" width="170" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button text size="small" type="primary" @click="viewScanRecords(row)">扫描记录</el-button>
          <el-button text size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination background
      :current-page="queryForm.pageNo" :page-size="queryForm.pageSize" :total="total"
      layout="total, sizes, prev, pager, next, jumper"
      @current-change="(v) => { queryForm.pageNo = v; fetchData() }"
      @size-change="(v) => { queryForm.pageSize = v; queryForm.pageNo = 1; fetchData() }"
    />
    <el-dialog v-model="generateVisible" title="生成二维码" width="520px" :close-on-click-modal="false">
      <el-form ref="generateFormRef" :model="generateForm" :rules="generateRules" label-width="80px">
        <el-form-item label="区域" prop="area">
          <el-select v-model="generateForm.area" placeholder="请选择区域" style="width: 100%">
            <el-option label="A栋" value="A栋" /><el-option label="B栋" value="B栋" /><el-option label="C栋" value="C栋" />
          </el-select>
        </el-form-item>
        <el-form-item label="楼层" prop="floor">
          <el-select v-model="generateForm.floor" placeholder="请选择楼层" style="width: 100%">
            <el-option label="B1" value="B1" /><el-option label="1F" value="1F" />
            <el-option label="2F" value="2F" /><el-option label="3F" value="3F" />
          </el-select>
        </el-form-item>
        <el-form-item label="房间" prop="room"><el-input v-model="generateForm.room" placeholder="请输入房间名称，如 101会议室" /></el-form-item>
      </el-form>
      <template v-if="generatedQR">
        <el-divider />
        <div style="text-align: center">
          <div style="font-weight: bold; margin-bottom: 12px; font-size: 14px">生成的二维码</div>
          <div style="display: inline-flex; align-items: center; justify-content: center; width: 160px; height: 160px; background: #fff; border: 2px dashed var(--el-border-color); border-radius: 8px; padding: 8px; margin-bottom: 12px">
            <div style="text-align: center">
              <div style="display: grid; grid-template-columns: repeat(11, 1fr); gap: 2px; width: 140px; height: 140px; padding: 4px">
                <div v-for="i in 121" :key="i" :style="{ width: '100%', aspectRatio: '1', backgroundColor: qrPattern[i - 1] ? '#000' : '#fff', borderRadius: '1px' }" />
              </div>
              <div style="font-size: 11px; color: var(--el-text-color-secondary); margin-top: 4px">{{ generatedQR.room }}</div>
            </div>
          </div>
          <div style="font-size: 12px; color: var(--el-text-color-secondary); word-break: break-all; margin-bottom: 8px; padding: 0 16px">链接：{{ generatedQR.url }}</div>
          <el-button type="primary" text @click="copyUrl(generatedQR.url)">复制链接</el-button>
        </div>
      </template>
      <template #footer>
        <el-button @click="closeGenerateDialog">取消</el-button>
        <el-button type="primary" :loading="generating" @click="submitGenerate">{{ generatedQR ? '重新生成' : '生成' }}</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="scanRecordVisible" title="扫描记录" width="700px" :close-on-click-modal="false">
      <div v-if="scanRecordRoom" style="margin-bottom: 16px; font-size: 14px; color: var(--el-text-color-secondary)">位置：{{ scanRecordRoom }}</div>
      <el-table v-loading="scanLoading" :data="scanRecordList" border>
        <el-table-column align="center" label="序号" type="index" width="60" />
        <el-table-column label="扫描人" prop="scanner" width="100" />
        <el-table-column label="房间" prop="room" min-width="140" />
        <el-table-column label="扫描时间" prop="scanTime" width="170" />
        <el-table-column label="结果" prop="result" min-width="200" show-overflow-tooltip />
      </el-table>
      <el-pagination background
        :current-page="scanQuery.pageNo" :page-size="scanQuery.pageSize" :total="scanTotal"
        layout="total, prev, pager, next" style="margin-top: 16px"
        @current-change="(v) => { scanQuery.pageNo = v; fetchScanRecords() }"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { getQRCodeList, generateQRCode, getScanRecordList, deleteQRCode } from '/@/api/workOrder'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref, reactive, computed, onMounted } from 'vue'

defineOptions({ name: 'WorkOrderQRCode' })

const queryForm = reactive({ area: '', floor: '', pageNo: 1, pageSize: 20 })
const list = ref<any[]>([])
const total = ref(0)
const listLoading = ref(false)

const resetQuery = () => { queryForm.area = ''; queryForm.floor = ''; queryForm.pageNo = 1; queryForm.pageSize = 20; fetchData() }

const fetchData = async () => {
  listLoading.value = true
  try {
    const params: Record<string, any> = { pageNo: queryForm.pageNo, pageSize: queryForm.pageSize }
    if (queryForm.area) params.area = queryForm.area
    if (queryForm.floor) params.floor = queryForm.floor
    const { data } = await getQRCodeList(params)
    list.value = data.list || []
    total.value = data.total || 0
  } catch { /* */ }
  finally { listLoading.value = false }
}

const copyUrl = async (url: string) => {
  try { await navigator.clipboard.writeText(url); ElMessage.success('链接已复制到剪贴板') }
  catch {
    const textarea = document.createElement('textarea'); textarea.value = url
    textarea.style.position = 'fixed'; textarea.style.opacity = '0'
    document.body.appendChild(textarea); textarea.select()
    document.execCommand('copy'); document.body.removeChild(textarea)
    ElMessage.success('链接已复制到剪贴板')
  }
}

const generateVisible = ref(false)
const generating = ref(false)
const generateFormRef = ref<any>(null)
const generatedQR = ref<any>(null)

const qrPattern = computed(() => {
  const pattern: boolean[] = []
  for (let i = 0; i < 121; i++) {
    const row = Math.floor(i / 11); const col = i % 11
    if (row < 3 && col < 3) { pattern.push(row === 0 || row === 2 || col === 0 || col === 2); continue }
    if (row < 3 && col > 7) { pattern.push(row === 0 || row === 2 || col === 8 || col === 10); continue }
    if (row > 7 && col < 3) { pattern.push(row === 8 || row === 10 || col === 0 || col === 2); continue }
    pattern.push((row * 7 + col * 13 + 3) % 5 !== 0)
  }
  return pattern
})

const generateForm = reactive({ area: '', floor: '', room: '' })
const generateRules = {
  area: [{ required: true, message: '请选择区域', trigger: 'change' }],
  floor: [{ required: true, message: '请选择楼层', trigger: 'change' }],
  room: [{ required: true, message: '请输入房间名称', trigger: 'blur' }],
}

const openGenerateDialog = () => { generateForm.area = ''; generateForm.floor = ''; generateForm.room = ''; generatedQR.value = null; generateVisible.value = true }
const closeGenerateDialog = () => { generateVisible.value = false; generatedQR.value = null }

const submitGenerate = async () => {
  const valid = await generateFormRef.value?.validate().catch(() => false)
  if (!valid) return
  generating.value = true
  try {
    const { data } = await generateQRCode({ area: generateForm.area, floor: generateForm.floor, room: generateForm.room })
    generatedQR.value = { ...data, room: `${generateForm.area} ${generateForm.floor} ${generateForm.room}` }
    ElMessage.success('二维码生成成功')
    fetchData()
  } catch { /* */ }
  finally { generating.value = false }
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定删除 "${row.area} ${row.floor} ${row.room}" 的二维码吗？`, '删除确认', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning',
  }).then(async () => { try { await deleteQRCode(row.id); ElMessage.success('删除成功'); fetchData() } catch { /* */ } }).catch(() => {})
}

const scanRecordVisible = ref(false)
const scanLoading = ref(false)
const scanRecordRoom = ref('')
const currentQRCodeId = ref('')
const scanRecordList = ref<any[]>([])
const scanTotal = ref(0)
const scanQuery = reactive({ pageNo: 1, pageSize: 10 })

const viewScanRecords = (row: any) => {
  currentQRCodeId.value = row.id
  scanRecordRoom.value = `${row.area} ${row.floor} ${row.room}`
  scanQuery.pageNo = 1
  scanRecordVisible.value = true
  fetchScanRecords()
}

const fetchScanRecords = async () => {
  scanLoading.value = true
  try {
    const { data } = await getScanRecordList({ qrCodeId: currentQRCodeId.value, pageNo: scanQuery.pageNo, pageSize: scanQuery.pageSize })
    scanRecordList.value = data.list || []
    scanTotal.value = data.total || 0
  } catch { /* */ }
  finally { scanLoading.value = false }
}

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.no-background-container { :deep(.vab-query-form) { .el-form-item:last-child { margin-right: 0; } } }
</style>

<template>
  <div class="workorder-statistics-container no-background-container">
    <vab-query-form>
      <vab-query-form-top-panel :span="24">
        <el-form :inline="true" @submit.prevent>
          <el-form-item label="日期范围">
            <el-date-picker v-model="dateRange" type="daterange" range-separator="至"
              start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" />
          </el-form-item>
          <el-form-item label="来源类型">
            <el-select v-model="sourceFilter" placeholder="全部来源" clearable>
              <el-option label="全部来源" value="" /><el-option label="二维码扫码" value="二维码扫码" />
              <el-option label="手动报单" value="手动报单" /><el-option label="设备告警" value="设备告警" />
              <el-option label="巡检自动" value="巡检自动" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </vab-query-form-top-panel>
    </vab-query-form>
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col v-for="(card, index) in summaryCards" :key="index" :span="4">
        <vab-card>
          <div class="summary-card" :style="{ borderTop: '3px solid ' + card.color }">
            <div class="value" :style="{ color: card.color }">{{ card.value }}</div>
            <div class="label">{{ card.label }}</div>
          </div>
        </vab-card>
      </el-col>
    </el-row>
    <vab-card title="工单趋势" style="margin-bottom: 20px">
      <v-chart class="chart" :option="trendOption" autoresize />
    </vab-card>
    <el-row :gutter="20">
      <el-col :span="12">
        <vab-card title="按来源统计">
          <el-table :data="stats.bySource" border stripe size="small">
            <el-table-column prop="source" label="来源" show-overflow-tooltip />
            <el-table-column prop="count" label="数量" width="80" align="center" />
            <el-table-column prop="satisfaction" label="满意度%" width="100" align="center">
              <template #default="{ row }">{{ formatPercent(row.satisfaction) }}</template>
            </el-table-column>
            <el-table-column prop="responseRate" label="响应率%" width="100" align="center">
              <template #default="{ row }">{{ formatPercent(row.responseRate) }}</template>
            </el-table-column>
            <el-table-column prop="completionRate" label="完成率%" width="100" align="center">
              <template #default="{ row }">{{ formatPercent(row.completionRate) }}</template>
            </el-table-column>
            <el-table-column prop="manualRatio" label="手动占比%" width="110" align="center">
              <template #default="{ row }">{{ formatPercent(row.manualRatio) }}</template>
            </el-table-column>
          </el-table>
        </vab-card>
      </el-col>
      <el-col :span="12">
        <vab-card title="按类型统计">
          <el-table :data="stats.byType" border stripe size="small">
            <el-table-column prop="typeName" label="类型" show-overflow-tooltip />
            <el-table-column prop="count" label="数量" width="80" align="center" />
            <el-table-column prop="satisfaction" label="满意度%" width="100" align="center">
              <template #default="{ row }">{{ formatPercent(row.satisfaction) }}</template>
            </el-table-column>
            <el-table-column prop="responseRate" label="响应率%" width="100" align="center">
              <template #default="{ row }">{{ formatPercent(row.responseRate) }}</template>
            </el-table-column>
            <el-table-column prop="completionRate" label="完成率%" width="100" align="center">
              <template #default="{ row }">{{ formatPercent(row.completionRate) }}</template>
            </el-table-column>
            <el-table-column prop="manualRatio" label="手动占比%" width="110" align="center">
              <template #default="{ row }">{{ formatPercent(row.manualRatio) }}</template>
            </el-table-column>
          </el-table>
        </vab-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, inject } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getWorkOrderStats } from '/@/api/workOrder'

use([CanvasRenderer, BarChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

defineOptions({ name: 'WorkOrderStatistics' })

const $baseMessage = inject<any>('$baseMessage')

const dateRange = ref<[string, string] | null>(null)
const sourceFilter = ref<string>('')

const stats = reactive({
  summary: { totalNew: 0, satisfactionRate: 0, responseRate: 0, completionRate: 0, manualRatio: 0 },
  bySource: [] as any[], byType: [] as any[], trend: [] as any[],
})

const summaryCards = computed(() => [
  { label: '新增工单', value: stats.summary.totalNew, color: '#4e88f3' },
  { label: '满意度', value: formatPercent(stats.summary.satisfactionRate), color: '#67c23a' },
  { label: '响应率', value: formatPercent(stats.summary.responseRate), color: '#e6a23c' },
  { label: '完成率', value: formatPercent(stats.summary.completionRate), color: '#4e88f3' },
  { label: '手动报单占比', value: formatPercent(stats.summary.manualRatio), color: '#9c27b0' },
])

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['新增工单', '已完成'] },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', data: stats.trend.map((t) => t.date), boundaryGap: true },
  yAxis: { type: 'value' },
  series: [
    { name: '新增工单', type: 'bar', barWidth: '35%', data: stats.trend.map((t) => t.newCount), itemStyle: { color: '#4e88f3' } },
    { name: '已完成', type: 'line', smooth: true, data: stats.trend.map((t) => t.completed), itemStyle: { color: '#67c23a' }, lineStyle: { width: 3 }, symbol: 'circle', symbolSize: 8 },
  ],
}))

function formatPercent(val: number): string { if (val == null) return '0.0%'; return `${Number(val).toFixed(1)}%` }

async function fetchData() {
  try {
    const params: Record<string, any> = {}
    if (dateRange.value) { params.startDate = dateRange.value[0]; params.endDate = dateRange.value[1] }
    if (sourceFilter.value) params.source = sourceFilter.value
    const res = await getWorkOrderStats(params)
    if (res.code === 200 || res.code === 0) {
      stats.summary = res.data.summary; stats.bySource = res.data.bySource
      stats.byType = res.data.byType; stats.trend = res.data.trend
    } else { $baseMessage?.error(res.msg || '获取统计数据失败') }
  } catch { $baseMessage?.error('获取统计数据失败') }
}

function resetFilter() { dateRange.value = null; sourceFilter.value = ''; fetchData() }

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.workorder-statistics-container { padding: 20px; }
.summary-card { text-align: center; padding: 16px 0 12px; }
.summary-card .value { font-size: 28px; font-weight: bold; margin-bottom: 6px; line-height: 1.2; }
.summary-card .label { font-size: 13px; color: #909399; }
.chart { width: 100%; height: 360px; }
</style>
```
