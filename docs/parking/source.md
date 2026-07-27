# 源代码提交页（智能楼宇智能停车管理系统 buildingos.parking）

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
import { ParkingController } from './parking.controller';
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
              'buildingos_microservice_parking_' +
              Math.random().toString(16).slice(2, 8),
          },
        }),
      },
    ]),
  ],
  controllers: [ParkingController],
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
  const logger = new Logger('ParkingBootstrap');
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
    .setTitle('Parking API')
    .setDescription('停车管理接口文档')
    .setVersion('1.0')
    .addBearerAuth()
    .build();
  const doc = swagger.SwaggerModule.createDocument(app, config);
  swagger.SwaggerModule.setup('parking/docs', app, doc);

  const port = parseInt(process.env.PORT || '3030', 10);
  await app.listen(port);
  logger.log(`Parking service running on port ${port}`);
}
void bootstrap();

import { Controller, Get, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { readFileSync } from 'fs';
import { join } from 'path';
import { JwtAuthGuard } from './auth/jwt.guard';
import { Public } from './auth/public.decorator';

@ApiTags('停车管理')
@Controller()
@UseGuards(JwtAuthGuard)
export class ParkingController {
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
    "path": "/parking",
    "name": "Parking",
    "component": "Layout",
    "meta": {
      "title": "停车",
      "icon": "car-line",
      "guard": ["Admin"]
    },
    "children": [
      {
        "path": "/parking/resource",
        "name": "ParkingResource",
        "meta": { "title": "资源管理", "icon": "layout-grid-line" },
        "children": [
          {
            "path": "area",
            "name": "ParkingArea",
            "component": "/@/views/parking/resource/area/index.vue",
            "meta": { "title": "区域管理", "guard": ["Admin"] }
          },
          {
            "path": "spot",
            "name": "ParkingSpot",
            "component": "/@/views/parking/resource/spot/index.vue",
            "meta": { "title": "车位管理", "guard": ["Admin"] }
          }
        ]
      },
      {
        "path": "/parking/vehicle",
        "name": "ParkingVehicle",
        "meta": { "title": "车辆管理", "icon": "car-fill" },
        "children": [
          {
            "path": "registration",
            "name": "VehicleRegistration",
            "component": "/@/views/parking/vehicle/registration/index.vue",
            "meta": { "title": "车辆登记", "guard": ["Admin"] }
          },
          {
            "path": "whitelist",
            "name": "WhiteList",
            "component": "/@/views/parking/vehicle/whitelist/index.vue",
            "meta": { "title": "白名单", "guard": ["Admin"] }
          },
          {
            "path": "blacklist",
            "name": "BlackList",
            "component": "/@/views/parking/vehicle/blacklist/index.vue",
            "meta": { "title": "黑名单", "guard": ["Admin"] }
          },
          {
            "path": "vip",
            "name": "VipAccess",
            "component": "/@/views/parking/vehicle/vip/index.vue",
            "meta": { "title": "VIP管理", "guard": ["Admin"] }
          }
        ]
      },
      {
        "path": "/parking/application",
        "name": "ParkingApplication",
        "meta": { "title": "车位申请", "icon": "file-list-3-line" },
        "children": [
          {
            "path": "apply",
            "name": "SpotApplication",
            "component": "/@/views/parking/application/apply/index.vue",
            "meta": { "title": "申请记录", "guard": ["Admin"] }
          },
          {
            "path": "review",
            "name": "AssignmentReview",
            "component": "/@/views/parking/application/review/index.vue",
            "meta": { "title": "审核分配", "guard": ["Admin"] }
          }
        ]
      },
      {
        "path": "/parking/access",
        "name": "ParkingAccess",
        "meta": { "title": "进出管理", "icon": "door-open-line" },
        "children": [
          {
            "path": "record",
            "name": "EntryExitRecords",
            "component": "/@/views/parking/access/record/index.vue",
            "meta": { "title": "进出记录", "guard": ["Admin"] }
          },
          {
            "path": "violation",
            "name": "ViolationControl",
            "component": "/@/views/parking/access/violation/index.vue",
            "meta": { "title": "违规管控", "guard": ["Admin"] }
          },
          {
            "path": "visitorLinkage",
            "name": "VisitorLinkage",
            "component": "/@/views/parking/access/visitorLinkage/index.vue",
            "meta": { "title": "访客联动", "guard": ["Admin"] }
          }
        ]
      },
      {
        "path": "/parking/stats",
        "name": "ParkingStats",
        "meta": { "title": "运营统计", "icon": "bar-chart-2-line" },
        "children": [
          {
            "path": "dashboard",
            "name": "RealTimeDashboard",
            "component": "/@/views/parking/stats/dashboard/index.vue",
            "meta": { "title": "实时看板", "guard": ["Admin"] }
          },
          {
            "path": "usage",
            "name": "ParkingUsage",
            "component": "/@/views/parking/stats/usage/index.vue",
            "meta": { "title": "车位使用", "guard": ["Admin"] }
          },
          {
            "path": "statistics",
            "name": "ParkingStatistics",
            "component": "/@/views/parking/stats/statistics/index.vue",
            "meta": { "title": "停车统计", "guard": ["Admin"] }
          }
        ]
      },
      {
        "path": "charging",
        "name": "ChargingStatus",
        "component": "/@/views/parking/charging/index.vue",
        "meta": { "title": "充电桩状态", "icon": "battery-charge-line", "guard": ["Admin"] }
      }
    ]
  }
]

<template>
  <div class="parking-entry">
    <vab-card>
      <el-empty description="请从左侧菜单选择停车管理功能模块" />
    </vab-card>
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'ParkingIndex' })
</script>

<style scoped>
.parking-entry {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}
</style>

<template>
  <div class="parking-area-container no-background-container">
    <vab-card class="auto-height-card">
      <vab-query-form>
        <vab-query-form-top-panel :span="24">
          <el-form :model="queryForm" :inline="true" @submit.prevent>
            <el-form-item label="楼层">
              <el-select v-model="queryForm.floor" placeholder="请选择楼层" clearable>
                <el-option label="B1" value="B1" />
                <el-option label="B2" value="B2" />
                <el-option label="B3" value="B3" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="queryForm.status" placeholder="请选择状态" clearable>
                <el-option label="启用" value="active" />
                <el-option label="停用" value="inactive" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
              <el-button type="primary" :icon="Plus" @click="handleAdd">新增区域</el-button>
            </el-form-item>
          </el-form>
        </vab-query-form-top-panel>
      </vab-query-form>
      <el-table v-loading="loading" :data="list" border>
        <el-table-column prop="name" label="区域名称" min-width="150" />
        <el-table-column prop="floor" label="楼层" width="100" />
        <el-table-column prop="totalSpots" label="总车位" width="100" />
        <el-table-column label="平面图" width="100" align="center">
          <template #default="{ row }">
            <photo-viewer :src="row.floorPlanUrl" :width="40" :height="40" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <status-badge :status="row.status" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <vab-pagination
        :current-page="queryForm.pageNo"
        :page-size="queryForm.pageSize"
        :total="total"
        @current-change="handleCurrentChange"
        @size-change="handleSizeChange"
      />
    </vab-card>
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="区域名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入区域名称" />
        </el-form-item>
        <el-form-item label="楼层" prop="floor">
          <el-select v-model="form.floor" placeholder="请选择楼层" style="width: 100%">
            <el-option label="B1" value="B1" />
            <el-option label="B2" value="B2" />
            <el-option label="B3" value="B3" />
          </el-select>
        </el-form-item>
        <el-form-item label="总车位" prop="totalSpots">
          <el-input-number v-model="form.totalSpots" :min="1" :max="9999" style="width: 100%" />
        </el-form-item>
        <el-form-item label="平面图">
          <floor-plan-upload v-if="form.id" :area-id="form.id" :current-url="form.floorPlanUrl" @uploaded="handleFloorPlanUploaded" />
          <div v-else class="upload-tip">请先保存区域基本信息后再上传平面图</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { getParkingAreaList, saveParkingArea, deleteParkingArea } from '/@/api/parking'
import StatusBadge from '../../common/StatusBadge.vue'
import PhotoViewer from '../../common/PhotoViewer.vue'
import FloorPlanUpload from './vabAutoComponents/FloorPlanUpload.vue'
import { Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'ParkingArea' })

const $baseMessage = inject<any>('$baseMessage')
const $baseConfirm = inject<any>('$baseConfirm')

const list = ref<any[]>([])
const loading = ref(true)
const total = ref(0)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const saving = ref(false)
const formRef = ref<any>(null)

const queryForm = reactive({
  pageNo: 1, pageSize: 20, floor: '', status: '',
})

const form = reactive<any>({
  id: '', name: '', floor: '', totalSpots: 100, floorPlanUrl: '', status: 'active',
})

const rules = {
  name: [{ required: true, message: '请输入区域名称', trigger: 'blur' }],
  floor: [{ required: true, message: '请选择楼层', trigger: 'change' }],
  totalSpots: [{ required: true, message: '请输入总车位数', trigger: 'blur' }],
}

const fetchData = async () => {
  loading.value = true
  const { data } = await getParkingAreaList(queryForm)
  list.value = data.list || []
  total.value = data.total || 0
  loading.value = false
}

const resetForm = () => {
  form.id = ''; form.name = ''; form.floor = ''; form.totalSpots = 100; form.floorPlanUrl = ''; form.status = 'active'
}

const handleAdd = () => { resetForm(); dialogTitle.value = '新增区域'; dialogVisible.value = true }
const handleEdit = (row: any) => { dialogTitle.value = '编辑区域'; Object.assign(form, JSON.parse(JSON.stringify(row))); dialogVisible.value = true }
const handleFloorPlanUploaded = (url: string) => { form.floorPlanUrl = url }

const handleDelete = async (row: any) => {
  try {
    await $baseConfirm('确认删除该区域及其所有车位?', '删除确认')
    await deleteParkingArea(row.id)
    $baseMessage.success('删除成功')
    fetchData()
  } catch { /* User cancelled or deletion failed */ }
}

const save = async () => {
  try {
    await formRef.value.validate()
    saving.value = true
    await saveParkingArea(form)
    $baseMessage.success('保存成功')
    dialogVisible.value = false
    fetchData()
  } catch { /* Validation failed */ }
  finally { saving.value = false }
}

const handleSizeChange = (val: number) => { queryForm.pageSize = val; fetchData() }
const handleCurrentChange = (val: number) => { queryForm.pageNo = val; fetchData() }

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.parking-area-container { padding: 20px; }
.upload-tip { color: var(--el-text-color-secondary); font-size: 13px; padding: 8px 0; }
</style>

<template>
  <div class="parking-spot-container no-background-container">
    <vab-card class="auto-height-card">
      <vab-query-form>
        <vab-query-form-top-panel :span="24">
          <el-form :model="queryForm" :inline="true" @submit.prevent>
            <el-form-item label="所属区域">
              <el-select v-model="queryForm.areaId" placeholder="请选择区域" clearable filterable style="width: 160px">
                <el-option v-for="item in areaOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="类型">
              <el-select v-model="queryForm.type" placeholder="全部类型" clearable style="width: 130px">
                <el-option label="普通车位" value="flat" />
                <el-option label="新能源" value="new_energy" />
                <el-option label="大型车位" value="large" />
                <el-option label="紧凑车位" value="compact" />
              </el-select>
            </el-form-item>
            <el-form-item label="用途">
              <el-select v-model="queryForm.purpose" placeholder="全部用途" clearable style="width: 130px">
                <el-option label="普通" value="normal" />
                <el-option label="访客" value="visitor" />
                <el-option label="VIP" value="vip" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="queryForm.status" placeholder="全部状态" clearable style="width: 130px">
                <el-option label="空闲" value="vacant" />
                <el-option label="已占用" value="occupied" />
                <el-option label="已预约" value="reserved" />
                <el-option label="维护中" value="maintenance" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
            </el-form-item>
          </el-form>
        </vab-query-form-top-panel>
      </vab-query-form>
      <div class="toolbar">
        <el-dropdown v-if="selectedIds.length > 0" @command="handleBatchCommand">
          <el-button type="warning">
            批量操作 ({{ selectedIds.length }})
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="maintenance">批量设为维护</el-dropdown-item>
              <el-dropdown-item command="vacant">批量设为空闲</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <el-table v-loading="loading" :data="list" border @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="code" label="车位编号" min-width="150" />
        <el-table-column prop="areaName" label="所属区域" width="120" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="typeTagType(row.type)" size="small">{{ typeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="purpose" label="用途" width="100">
          <template #default="{ row }">
            <el-tag :type="purposeTagType(row.purpose)" size="small">{{ purposeLabel(row.purpose) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }"><status-badge :status="row.status" /></template>
        </el-table-column>
        <el-table-column prop="currentPlate" label="当前车牌" min-width="130" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <vab-pagination
        :current-page="queryForm.pageNo" :page-size="queryForm.pageSize" :total="total"
        @current-change="handleCurrentChange" @size-change="handleSizeChange"
      />
    </vab-card>
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="车位编号"><el-input v-model="form.code" disabled /></el-form-item>
        <el-form-item label="所属区域"><el-input v-model="form.areaName" disabled /></el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="普通车位" value="flat" />
            <el-option label="新能源" value="new_energy" />
            <el-option label="大型车位" value="large" />
            <el-option label="紧凑车位" value="compact" />
          </el-select>
        </el-form-item>
        <el-form-item label="用途" prop="purpose">
          <el-select v-model="form.purpose" placeholder="请选择用途" style="width: 100%">
            <el-option label="普通" value="normal" />
            <el-option label="访客" value="visitor" />
            <el-option label="VIP" value="vip" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="空闲" value="vacant" />
            <el-option label="已占用" value="occupied" />
            <el-option label="已预约" value="reserved" />
            <el-option label="维护中" value="maintenance" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { getParkingAreaList, getParkingSpotList, saveParkingSpot, deleteParkingSpot, batchUpdateSpotStatus } from '/@/api/parking'
import StatusBadge from '../../common/StatusBadge.vue'
import { ArrowDown } from '@element-plus/icons-vue'

defineOptions({ name: 'ParkingSpot' })

const $baseMessage = inject<any>('$baseMessage')
const $baseConfirm = inject<any>('$baseConfirm')

const list = ref<any[]>([])
const loading = ref(true)
const total = ref(0)
const areaOptions = ref<any[]>([])
const selectedIds = ref<string[]>([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const saving = ref(false)
const formRef = ref<any>(null)

const queryForm = reactive({
  pageNo: 1, pageSize: 20, areaId: '', type: '', purpose: '', status: '',
})

const form = reactive<any>({
  id: '', code: '', areaName: '', areaId: '', type: 'flat', purpose: 'normal', status: 'vacant', currentPlate: '',
})

const rules = {
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  purpose: [{ required: true, message: '请选择用途', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

const typeTagType = (type: string) => {
  const map: Record<string, string> = { flat: '', new_energy: 'success', large: 'warning', compact: 'info' }
  return map[type] || ''
}
const typeLabel = (type: string) => {
  const map: Record<string, string> = { flat: '普通车位', new_energy: '新能源', large: '大型车位', compact: '紧凑车位' }
  return map[type] || type
}
const purposeTagType = (purpose: string) => {
  const map: Record<string, string> = { normal: '', visitor: 'warning', vip: 'danger' }
  return map[purpose] || ''
}
const purposeLabel = (purpose: string) => {
  const map: Record<string, string> = { normal: '普通', visitor: '访客', vip: 'VIP' }
  return map[purpose] || purpose
}

const fetchAreas = async () => { const { data } = await getParkingAreaList(); areaOptions.value = data.list || [] }

const fetchData = async () => {
  loading.value = true
  const { data } = await getParkingSpotList(queryForm)
  list.value = data.list || []
  total.value = data.total || 0
  loading.value = false
}

const handleSelectionChange = (rows: any[]) => { selectedIds.value = rows.map((r) => r.id) }

const handleBatchCommand = async (command: string) => {
  if (selectedIds.value.length === 0) return
  const statusLabel = command === 'maintenance' ? '维护' : '空闲'
  try {
    await $baseConfirm(`确认将选中的 ${selectedIds.value.length} 个车位设为${statusLabel}?`, '批量操作')
    await batchUpdateSpotStatus({ ids: selectedIds.value, status: command })
    $baseMessage.success(`已成功将 ${selectedIds.value.length} 个车位设为${statusLabel}`)
    selectedIds.value = []
    fetchData()
  } catch { /* User cancelled */ }
}

const handleEdit = (row: any) => { dialogTitle.value = '编辑车位'; Object.assign(form, JSON.parse(JSON.stringify(row))); dialogVisible.value = true }

const handleDelete = async (row: any) => {
  try {
    await $baseConfirm('确认删除该车位?', '删除确认')
    await deleteParkingSpot(row.id)
    $baseMessage.success('删除成功')
    fetchData()
  } catch { /* User cancelled */ }
}

const save = async () => {
  try {
    await formRef.value.validate()
    saving.value = true
    await saveParkingSpot(form)
    $baseMessage.success('保存成功')
    dialogVisible.value = false
    fetchData()
  } catch { /* Validation failed */ }
  finally { saving.value = false }
}

const handleSizeChange = (val: number) => { queryForm.pageSize = val; fetchData() }
const handleCurrentChange = (val: number) => { queryForm.pageNo = val; fetchData() }

onMounted(() => { fetchAreas(); fetchData() })
</script>

<style lang="scss" scoped>
.parking-spot-container { padding: 20px; }
.toolbar { margin-bottom: 16px; min-height: 32px; }
</style>
```

## 后30页
请在此粘贴后30页的连续源代码片段，按照页码顺序组织。

```
<template>
  <div class="vehicle-registration-container no-background-container">
    <vab-card class="auto-height-card">
      <vab-query-form>
        <vab-query-form-top-panel :span="24">
          <el-form :model="queryForm" :inline="true" @submit.prevent>
            <el-form-item label="车牌号">
              <el-input v-model="queryForm.plateNumber" placeholder="请输入车牌号" />
            </el-form-item>
            <el-form-item label="类型">
              <el-select v-model="queryForm.type" placeholder="全部" clearable style="width: 120px">
                <el-option label="员工" value="employee" />
                <el-option label="访客" value="visitor" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="queryForm.status" placeholder="全部" clearable style="width: 120px">
                <el-option label="启用" value="active" />
                <el-option label="停用" value="inactive" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
              <el-button type="primary" :icon="Plus" @click="handleAdd">新增车辆</el-button>
            </el-form-item>
          </el-form>
        </vab-query-form-top-panel>
      </vab-query-form>
      <el-table v-loading="loading" :data="list" border>
        <el-table-column prop="plateNumber" label="车牌号" width="120" />
        <el-table-column prop="ownerName" label="车主姓名" width="100" />
        <el-table-column prop="ownerPhone" label="电话" width="130" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="vehicleModel" label="车型" width="140" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'employee' ? 'primary' : 'warning'">
              {{ row.type === 'employee' ? '员工' : '访客' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }"><status-badge :status="row.status" /></template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <vab-pagination
        :current-page="queryForm.pageNo" :page-size="queryForm.pageSize" :total="total"
        @current-change="handleCurrentChange" @size-change="handleSizeChange"
      />
      <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
        <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
          <el-form-item label="车牌号" prop="plateNumber">
            <plate-input v-model="form.plateNumber" />
          </el-form-item>
          <el-form-item label="车主姓名" prop="ownerName">
            <el-input v-model="form.ownerName" placeholder="请输入车主姓名" />
          </el-form-item>
          <el-form-item label="电话" prop="ownerPhone">
            <el-input v-model="form.ownerPhone" placeholder="请输入联系电话" />
          </el-form-item>
          <el-form-item label="部门" prop="department">
            <el-input v-model="form.department" placeholder="请输入所属部门" />
          </el-form-item>
          <el-form-item label="类型" prop="type">
            <el-select v-model="form.type" placeholder="请选择类型" style="width: 100%">
              <el-option label="员工" value="employee" />
              <el-option label="访客" value="visitor" />
            </el-select>
          </el-form-item>
          <el-form-item label="车型" prop="vehicleModel">
            <el-input v-model="form.vehicleModel" placeholder="请输入车型" />
          </el-form-item>
          <el-form-item label="车辆颜色" prop="vehicleColor">
            <el-select v-model="form.vehicleColor" placeholder="请选择颜色" style="width: 100%">
              <el-option label="黑色" value="黑色" /><el-option label="白色" value="白色" />
              <el-option label="银色" value="银色" /><el-option label="灰色" value="灰色" />
              <el-option label="蓝色" value="蓝色" /><el-option label="红色" value="红色" />
              <el-option label="绿色" value="绿色" /><el-option label="棕色" value="棕色" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave">保存</el-button>
        </template>
      </el-dialog>
    </vab-card>
  </div>
</template>

<script lang="ts" setup>
import { getVehicleRegistrationList, saveVehicleRegistration, deleteVehicleRegistration } from '/@/api/parking'
import PlateInput from '../../common/PlateInput.vue'
import StatusBadge from '../../common/StatusBadge.vue'
import { Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'VehicleRegistration' })

const $baseMessage = inject<any>('$baseMessage')
const $baseConfirm = inject<any>('$baseConfirm')

const list = ref<any[]>([])
const loading = ref(true)
const total = ref(0)
const dialogVisible = ref(false)
const dialogTitle = ref('新增车辆')
const formRef = ref<any>(null)

const queryForm = reactive({ pageNo: 1, pageSize: 20, plateNumber: '', type: '', status: '' })

const form = reactive({
  id: '', plateNumber: '', ownerName: '', ownerPhone: '',
  department: '', type: 'employee', vehicleModel: '', vehicleColor: '',
})

const rules = {
  plateNumber: [{ required: true, message: '请输入车牌号', trigger: 'blur' }],
  ownerName: [{ required: true, message: '请输入车主姓名', trigger: 'blur' }],
  ownerPhone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
}

const fetchData = async () => {
  loading.value = true
  const { data } = await getVehicleRegistrationList(queryForm)
  list.value = data.list || []
  total.value = data.total || 0
  loading.value = false
}

const handleAdd = () => {
  dialogTitle.value = '新增车辆'
  Object.assign(form, { id: '', plateNumber: '', ownerName: '', ownerPhone: '', department: '', type: 'employee', vehicleModel: '', vehicleColor: '' })
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  dialogTitle.value = '编辑车辆'
  Object.assign(form, {
    id: row.id, plateNumber: row.plateNumber, ownerName: row.ownerName,
    ownerPhone: row.ownerPhone, department: row.department, type: row.type,
    vehicleModel: row.vehicleModel, vehicleColor: row.vehicleColor,
  })
  dialogVisible.value = true
}

const handleSave = async () => {
  await formRef.value.validate()
  await saveVehicleRegistration({ ...form })
  $baseMessage.success('保存成功')
  dialogVisible.value = false
  fetchData()
}

const handleDelete = (row: any) => {
  $baseConfirm('确认删除该车辆登记?', '提示').then(async () => {
    await deleteVehicleRegistration(row.id)
    $baseMessage.success('删除成功')
    fetchData()
  })
}

const handleSizeChange = (val: number) => { queryForm.pageSize = val; fetchData() }
const handleCurrentChange = (val: number) => { queryForm.pageNo = val; fetchData() }

onBeforeMount(() => { fetchData() })
</script>

<style lang="scss" scoped>
.vehicle-registration-container { padding: 20px; }
</style>

<template>
  <div class="whitelist-container no-background-container">
    <vab-card class="auto-height-card">
      <vab-query-form>
        <vab-query-form-top-panel :span="24">
          <el-form :model="queryForm" :inline="true" @submit.prevent>
            <el-form-item label="车牌号">
              <el-input v-model="queryForm.plateNumber" placeholder="请输入车牌号" />
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="queryForm.status" placeholder="全部" clearable style="width: 120px">
                <el-option label="启用" value="active" />
                <el-option label="已过期" value="expired" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
              <el-button type="primary" :icon="Plus" @click="handleAdd">新增白名单</el-button>
            </el-form-item>
          </el-form>
        </vab-query-form-top-panel>
      </vab-query-form>
      <el-table v-loading="loading" :data="list" border>
        <el-table-column prop="plateNumber" label="车牌号" width="120" />
        <el-table-column prop="ownerName" label="车主姓名" width="120" />
        <el-table-column prop="reason" label="原因" min-width="200" />
        <el-table-column label="有效期" width="300">
          <template #default="{ row }">
            <span :class="{ 'expired-text': row.status === 'expired' }">{{ row.validFrom }} ~ {{ row.validUntil }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }"><status-badge :status="row.status" /></template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <vab-pagination
        :current-page="queryForm.pageNo" :page-size="queryForm.pageSize" :total="total"
        @current-change="handleCurrentChange" @size-change="handleSizeChange"
      />
      <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
        <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
          <el-form-item label="车牌号" prop="plateNumber"><plate-input v-model="form.plateNumber" /></el-form-item>
          <el-form-item label="车主姓名" prop="ownerName"><el-input v-model="form.ownerName" placeholder="请输入车主姓名" /></el-form-item>
          <el-form-item label="原因" prop="reason"><el-input v-model="form.reason" type="textarea" placeholder="请输入加入白名单原因" /></el-form-item>
          <el-form-item label="开始日期" prop="validFrom">
            <el-date-picker v-model="form.validFrom" type="date" placeholder="选择开始日期" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
          <el-form-item label="截止日期" prop="validUntil">
            <el-date-picker v-model="form.validUntil" type="date" placeholder="选择截止日期" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave">保存</el-button>
        </template>
      </el-dialog>
    </vab-card>
  </div>
</template>

<script lang="ts" setup>
import { getWhitelist, saveWhitelistItem, deleteWhitelistItem } from '/@/api/parking'
import PlateInput from '../../common/PlateInput.vue'
import StatusBadge from '../../common/StatusBadge.vue'
import { Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'WhitelistManagement' })

const $baseMessage = inject<any>('$baseMessage')
const $baseConfirm = inject<any>('$baseConfirm')

const list = ref<any[]>([])
const loading = ref(true)
const total = ref(0)
const dialogVisible = ref(false)
const dialogTitle = ref('新增白名单')
const formRef = ref<any>(null)

const queryForm = reactive({ pageNo: 1, pageSize: 20, plateNumber: '', status: '' })

const form = reactive({ id: '', plateNumber: '', ownerName: '', reason: '', validFrom: '', validUntil: '' })

const rules = {
  plateNumber: [{ required: true, message: '请输入车牌号', trigger: 'blur' }],
  ownerName: [{ required: true, message: '请输入车主姓名', trigger: 'blur' }],
  reason: [{ required: true, message: '请输入原因', trigger: 'blur' }],
  validFrom: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  validUntil: [{ required: true, message: '请选择截止日期', trigger: 'change' }],
}

const fetchData = async () => {
  loading.value = true
  const { data } = await getWhitelist(queryForm)
  list.value = data.list || []
  total.value = data.total || 0
  loading.value = false
}

const handleAdd = () => {
  dialogTitle.value = '新增白名单'
  Object.assign(form, { id: '', plateNumber: '', ownerName: '', reason: '', validFrom: '', validUntil: '' })
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  dialogTitle.value = '编辑白名单'
  Object.assign(form, { id: row.id, plateNumber: row.plateNumber, ownerName: row.ownerName, reason: row.reason, validFrom: row.validFrom, validUntil: row.validUntil })
  dialogVisible.value = true
}

const handleSave = async () => {
  await formRef.value.validate()
  await saveWhitelistItem({ ...form })
  $baseMessage.success('保存成功')
  dialogVisible.value = false
  fetchData()
}

const handleDelete = (row: any) => {
  $baseConfirm('确认删除该白名单?', '提示').then(async () => {
    await deleteWhitelistItem(row.id)
    $baseMessage.success('删除成功')
    fetchData()
  })
}

const handleSizeChange = (val: number) => { queryForm.pageSize = val; fetchData() }
const handleCurrentChange = (val: number) => { queryForm.pageNo = val; fetchData() }

onBeforeMount(() => { fetchData() })
</script>

<style lang="scss" scoped>
.whitelist-container { padding: 20px; }
.expired-text { color: #f56c6c; }
</style>

<template>
  <div class="blacklist-container no-background-container">
    <vab-card class="auto-height-card">
      <vab-query-form>
        <vab-query-form-top-panel :span="24">
          <el-form :model="queryForm" :inline="true" @submit.prevent>
            <el-form-item label="车牌号">
              <el-input v-model="queryForm.plateNumber" placeholder="请输入车牌号" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
              <el-button type="primary" :icon="Plus" @click="handleAdd">新增黑名单</el-button>
            </el-form-item>
          </el-form>
        </vab-query-form-top-panel>
      </vab-query-form>
      <el-table v-loading="loading" :data="list" border>
        <el-table-column prop="plateNumber" label="车牌号" width="120" />
        <el-table-column prop="ownerName" label="车主姓名" width="120" />
        <el-table-column prop="reason" label="限制原因" min-width="200" />
        <el-table-column prop="restriction" label="限制类型" width="120">
          <template #default="{ row }">
            <el-tag :type="restrictionTagType(row.restriction)">
              {{ restrictionLabel(row.restriction) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="录入时间" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <vab-pagination
        :current-page="queryForm.pageNo" :page-size="queryForm.pageSize" :total="total"
        @current-change="handleCurrentChange" @size-change="handleSizeChange"
      />
      <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
        <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
          <el-form-item label="车牌号" prop="plateNumber">
            <plate-input v-model="form.plateNumber" />
          </el-form-item>
          <el-form-item label="车主姓名" prop="ownerName">
            <el-input v-model="form.ownerName" placeholder="请输入车主姓名" />
          </el-form-item>
          <el-form-item label="限制原因" prop="reason">
            <el-input v-model="form.reason" type="textarea" placeholder="请输入限制原因" />
          </el-form-item>
          <el-form-item label="限制类型" prop="restriction">
            <el-select v-model="form.restriction" placeholder="请选择限制类型" style="width: 100%">
              <el-option label="禁止驶入" value="no_entry" />
              <el-option label="限时通行" value="limited_hours" />
              <el-option label="罚款待处理" value="fine_pending" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave">保存</el-button>
        </template>
      </el-dialog>
    </vab-card>
  </div>
</template>

<script lang="ts" setup>
import { getBlacklist, saveBlacklistItem, deleteBlacklistItem } from '/@/api/parking'
import PlateInput from '../../common/PlateInput.vue'
import { Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'BlacklistManagement' })

const $baseMessage = inject<any>('$baseMessage')
const $baseConfirm = inject<any>('$baseConfirm')

const list = ref<any[]>([])
const loading = ref(true)
const total = ref(0)
const dialogVisible = ref(false)
const dialogTitle = ref('新增黑名单')
const formRef = ref<any>(null)

const queryForm = reactive({ pageNo: 1, pageSize: 20, plateNumber: '' })

const form = reactive({ id: '', plateNumber: '', ownerName: '', reason: '', restriction: 'no_entry' })

const rules = {
  plateNumber: [{ required: true, message: '请输入车牌号', trigger: 'blur' }],
  ownerName: [{ required: true, message: '请输入车主姓名', trigger: 'blur' }],
  reason: [{ required: true, message: '请输入限制原因', trigger: 'blur' }],
  restriction: [{ required: true, message: '请选择限制类型', trigger: 'change' }],
}

const restrictionTagType = (type: string): string => {
  const map: Record<string, string> = { no_entry: 'danger', limited_hours: 'warning', fine_pending: 'info' }
  return map[type] || 'info'
}

const restrictionLabel = (type: string): string => {
  const map: Record<string, string> = { no_entry: '禁止驶入', limited_hours: '限时通行', fine_pending: '罚款待处理' }
  return map[type] || type
}

const fetchData = async () => {
  loading.value = true
  const { data } = await getBlacklist(queryForm)
  list.value = data.list || []
  total.value = data.total || 0
  loading.value = false
}

const handleAdd = () => {
  dialogTitle.value = '新增黑名单'
  form.id = ''; form.plateNumber = ''; form.ownerName = ''; form.reason = ''; form.restriction = 'no_entry'
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  dialogTitle.value = '编辑黑名单'
  Object.assign(form, { id: row.id, plateNumber: row.plateNumber, ownerName: row.ownerName, reason: row.reason, restriction: row.restriction })
  dialogVisible.value = true
}

const handleSave = async () => {
  await formRef.value.validate()
  await saveBlacklistItem({ ...form })
  $baseMessage.success('保存成功')
  dialogVisible.value = false
  fetchData()
}

const handleDelete = (row: any) => {
  $baseConfirm('确认删除该黑名单?', '提示').then(async () => {
    await deleteBlacklistItem(row.id)
    $baseMessage.success('删除成功')
    fetchData()
  })
}

const handleSizeChange = (val: number) => { queryForm.pageSize = val; fetchData() }
const handleCurrentChange = (val: number) => { queryForm.pageNo = val; fetchData() }

onBeforeMount(() => { fetchData() })
</script>

<style lang="scss" scoped>
.blacklist-container { padding: 20px; }
</style>

<template>
  <div class="vip-access-container no-background-container">
    <vab-card class="auto-height-card">
      <vab-query-form>
        <vab-query-form-top-panel :span="24">
          <el-form :model="queryForm" :inline="true" @submit.prevent>
            <el-form-item label="VIP姓名">
              <el-input v-model="queryForm.name" placeholder="请输入姓名" />
            </el-form-item>
            <el-form-item label="车牌号">
              <el-input v-model="queryForm.plateNumber" placeholder="请输入车牌号" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
              <el-button type="primary" :icon="Plus" @click="handleAdd">新增VIP</el-button>
            </el-form-item>
          </el-form>
        </vab-query-form-top-panel>
      </vab-query-form>
      <el-table v-loading="loading" :data="list" border>
        <el-table-column prop="name" label="VIP姓名" width="120" />
        <el-table-column prop="plateNumber" label="车牌号" width="120" />
        <el-table-column prop="phone" label="联系电话" width="150" />
        <el-table-column prop="remindTarget" label="提醒对象" width="120" />
        <el-table-column prop="remindPhone" label="提醒电话" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }"><status-badge :status="row.status" /></template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <vab-pagination
        :current-page="queryForm.pageNo" :page-size="queryForm.pageSize" :total="total"
        @current-change="handleCurrentChange" @size-change="handleSizeChange"
      />
      <vip-edit ref="editRef" @fetch-data="fetchData" />
    </vab-card>
  </div>
</template>

<script lang="ts" setup>
import { getVipList, deleteVip } from '/@/api/parking'
import VipEdit from './vabAutoComponents/VipEdit.vue'
import StatusBadge from '../../common/StatusBadge.vue'
import { Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'VipAccess' })

const list = ref([])
const loading = ref(true)
const total = ref(0)
const editRef = ref<any>(null)

const queryForm = reactive({ pageNo: 1, pageSize: 20, name: '', plateNumber: '' })

const fetchData = async () => {
  loading.value = true
  const { data } = await getVipList(queryForm)
  list.value = data.list || []
  total.value = data.total || 0
  loading.value = false
}

const handleAdd = () => { editRef.value.showEdit() }
const handleEdit = (row: any) => { editRef.value.showEdit(row) }

const handleDelete = (row: any) => {
  ElMessageBox.confirm('确认删除该VIP?', '提示', { type: 'warning' }).then(async () => {
    await deleteVip(row.id)
    ElMessage.success('删除成功')
    fetchData()
  })
}

const handleSizeChange = (val: number) => { queryForm.pageSize = val; fetchData() }
const handleCurrentChange = (val: number) => { queryForm.pageNo = val; fetchData() }

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.vip-access-container { padding: 20px; }
</style>

<template>
  <el-dialog v-model="dialogVisible" :title="title" width="600px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="VIP姓名" prop="name"><el-input v-model="form.name" placeholder="请输入姓名" /></el-form-item>
      <el-form-item label="车牌号" prop="plateNumber"><el-input v-model="form.plateNumber" placeholder="请输入车牌号" /></el-form-item>
      <el-form-item label="联系电话" prop="phone"><el-input v-model="form.phone" placeholder="请输入电话" /></el-form-item>
      <el-form-item label="提醒对象" prop="remindTarget"><el-input v-model="form.remindTarget" placeholder="请输入提醒对象姓名" /></el-form-item>
      <el-form-item label="提醒电话" prop="remindPhone"><el-input v-model="form.remindPhone" placeholder="请输入提醒对象电话" /></el-form-item>
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
import { saveVip } from '/@/api/parking'

defineOptions({ name: 'VipEdit' })

const emit = defineEmits(['fetch-data'])
const dialogVisible = ref(false)
const title = ref('')
const formRef = ref<any>(null)
const form = reactive<any>({ id: '', name: '', plateNumber: '', phone: '', remindTarget: '', remindPhone: '', status: 'active' })

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  plateNumber: [{ required: true, message: '请输入车牌号', trigger: 'blur' }],
}

const showEdit = (row?: any) => {
  dialogVisible.value = true
  if (row) {
    title.value = '编辑VIP'
    Object.assign(form, JSON.parse(JSON.stringify(row)))
  } else {
    title.value = '新增VIP'
    form.id = ''; form.name = ''; form.plateNumber = ''; form.phone = ''; form.remindTarget = ''; form.remindPhone = ''; form.status = 'active'
  }
}

const save = async () => {
  await formRef.value.validate()
  await saveVip(form)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  emit('fetch-data')
}

defineExpose({ showEdit })
</script>

<template>
  <div class="parking-apply-container no-background-container">
    <vab-card class="auto-height-card">
      <vab-query-form>
        <vab-query-form-top-panel :span="24">
          <el-form :model="queryForm" :inline="true" @submit.prevent>
            <el-form-item>
              <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
              <el-button type="primary" @click="handleCreate">新建申请</el-button>
            </el-form-item>
          </el-form>
        </vab-query-form-top-panel>
      </vab-query-form>
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="待处理" name="pending" />
        <el-tab-pane label="已通过" name="approved" />
        <el-tab-pane label="已拒绝" name="rejected" />
        <el-tab-pane label="已分配" name="assigned" />
      </el-tabs>
      <el-table v-loading="loading" :data="list" border>
        <el-table-column prop="applicationNo" label="申请编号" width="160" />
        <el-table-column prop="applicant" label="申请人" width="120" />
        <el-table-column prop="plateNumber" label="车牌号" width="120" />
        <el-table-column prop="vehicleModel" label="车型" min-width="120" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === '长期' ? 'primary' : 'warning'" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="申请时间" width="170" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }"><status-badge :status="row.status" /></template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleDetail(row)">查看详情</el-button>
            <el-button v-if="row.status === 'pending'" type="danger" text size="small" @click="handleCancel(row)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
      <vab-pagination
        :current-page="queryForm.pageNo" :page-size="queryForm.pageSize" :total="total"
        @current-change="handleCurrentChange" @size-change="handleSizeChange"
      />
    </vab-card>
    <el-dialog v-model="detailVisible" title="申请详情" width="600px" :close-on-click-modal="false">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="申请编号">{{ detailRow?.applicationNo }}</el-descriptions-item>
        <el-descriptions-item label="申请人">{{ detailRow?.applicant }}</el-descriptions-item>
        <el-descriptions-item label="车牌号">{{ detailRow?.plateNumber }}</el-descriptions-item>
        <el-descriptions-item label="车型">{{ detailRow?.vehicleModel }}</el-descriptions-item>
        <el-descriptions-item label="车辆颜色">{{ detailRow?.vehicleColor }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ detailRow?.type }}</el-descriptions-item>
        <el-descriptions-item label="偏好区域">{{ detailRow?.areaPreference }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ detailRow?.phone }}</el-descriptions-item>
        <el-descriptions-item label="申请时间">{{ detailRow?.createdAt }}</el-descriptions-item>
        <el-descriptions-item label="状态"><status-badge :status="detailRow?.status" /></el-descriptions-item>
        <el-descriptions-item v-if="detailRow?.reviewRemark" label="审核备注" :span="2">{{ detailRow?.reviewRemark }}</el-descriptions-item>
        <el-descriptions-item v-if="detailRow?.assignedSpot" label="分配车位" :span="2">{{ detailRow?.assignedSpot }}</el-descriptions-item>
      </el-descriptions>
      <template #footer><el-button @click="detailVisible = false">关闭</el-button></template>
    </el-dialog>
    <el-dialog v-model="createVisible" title="新建申请" width="600px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="车牌号" prop="plateNumber"><plate-input v-model="form.plateNumber" /></el-form-item>
        <el-form-item label="车型" prop="vehicleModel"><el-input v-model="form.vehicleModel" placeholder="请输入车型" /></el-form-item>
        <el-form-item label="车辆颜色" prop="vehicleColor"><el-input v-model="form.vehicleColor" placeholder="请输入车辆颜色" /></el-form-item>
        <el-form-item label="偏好区域" prop="areaPreference">
          <el-select v-model="form.areaPreference" placeholder="请选择偏好区域" clearable style="width: 100%">
            <el-option v-for="area in areaList" :key="area.id" :label="area.name" :value="area.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="长期" value="长期" /><el-option label="临时" value="临时" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系电话" prop="phone"><el-input v-model="form.phone" placeholder="请输入联系电话" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitCreate">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { getParkingApplicationList, createParkingApplication, getParkingAreaList } from '/@/api/parking'
import PlateInput from '../../common/PlateInput.vue'
import StatusBadge from '../../common/StatusBadge.vue'

defineOptions({ name: 'ParkingApply' })

const $baseMessage = inject<any>('$baseMessage')
const $baseConfirm = inject<any>('$baseConfirm')

const list = ref<any[]>([])
const loading = ref(true)
const total = ref(0)
const activeTab = ref('all')
const detailVisible = ref(false)
const detailRow = ref<any>(null)
const createVisible = ref(false)
const saving = ref(false)
const formRef = ref<any>(null)
const areaList = ref<any[]>([])

const queryForm = reactive({ pageNo: 1, pageSize: 20, status: '' })

const form = reactive({ plateNumber: '', vehicleModel: '', vehicleColor: '', areaPreference: '', type: '', phone: '' })

const rules = {
  plateNumber: [{ required: true, message: '请输入车牌号', trigger: 'blur' }],
  vehicleModel: [{ required: true, message: '请输入车型', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
}

const fetchData = async () => {
  loading.value = true
  const params = { ...queryForm }
  if (activeTab.value !== 'all') params.status = activeTab.value
  const { data } = await getParkingApplicationList(params)
  list.value = data.list || []
  total.value = data.total || 0
  loading.value = false
}

const handleTabChange = () => { queryForm.pageNo = 1; fetchData() }

const handleDetail = (row: any) => { detailRow.value = row; detailVisible.value = true }

const handleCancel = async (row: any) => {
  try {
    await $baseConfirm('确认取消该申请?', '取消确认')
    $baseMessage.success('已取消')
    fetchData()
  } catch { /* User cancelled */ }
}

const handleCreate = async () => {
  form.plateNumber = ''; form.vehicleModel = ''; form.vehicleColor = ''; form.areaPreference = ''; form.type = ''; form.phone = ''
  const { data } = await getParkingAreaList({ pageNo: 1, pageSize: 9999 })
  areaList.value = data.list || []
  createVisible.value = true
}

const submitCreate = async () => {
  try {
    await formRef.value.validate()
    saving.value = true
    await createParkingApplication(form)
    $baseMessage.success('提交成功')
    createVisible.value = false
    fetchData()
  } catch { /* Validation failed */ }
  finally { saving.value = false }
}

const handleSizeChange = (val: number) => { queryForm.pageSize = val; fetchData() }
const handleCurrentChange = (val: number) => { queryForm.pageNo = val; fetchData() }

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.parking-apply-container { padding: 20px; }
</style>

<template>
  <div class="parking-review-container no-background-container">
    <vab-card class="auto-height-card">
      <vab-query-form>
        <vab-query-form-top-panel :span="24">
          <el-form :model="queryForm" :inline="true" @submit.prevent>
            <el-form-item>
              <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
              <el-button type="primary" @click="handleAutoRules">自动分配规则</el-button>
            </el-form-item>
          </el-form>
        </vab-query-form-top-panel>
      </vab-query-form>
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="待处理" name="pending" />
        <el-tab-pane label="已通过" name="approved" />
        <el-tab-pane label="已拒绝" name="rejected" />
        <el-tab-pane label="已分配" name="assigned" />
      </el-tabs>
      <el-table v-loading="loading" :data="list" border>
        <el-table-column prop="applicationNo" label="申请编号" width="160" />
        <el-table-column prop="applicant" label="申请人" width="120" />
        <el-table-column prop="plateNumber" label="车牌号" width="120" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === '长期' ? 'primary' : 'warning'" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="提交时间" width="170" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }"><status-badge :status="row.status" /></template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button type="primary" text size="small" @click="handleReview(row)">审核</el-button>
              <el-button type="success" text size="small" @click="handleAutoAssign(row)">自动分配</el-button>
            </template>
            <span v-else>--</span>
          </template>
        </el-table-column>
      </el-table>
      <vab-pagination
        :current-page="queryForm.pageNo" :page-size="queryForm.pageSize" :total="total"
        @current-change="handleCurrentChange" @size-change="handleSizeChange"
      />
    </vab-card>
    <el-dialog v-model="assignVisible" title="审核申请" width="700px" :close-on-click-modal="false">
      <el-descriptions :column="2" border style="margin-bottom: 20px">
        <el-descriptions-item label="申请编号">{{ currentRow?.applicationNo }}</el-descriptions-item>
        <el-descriptions-item label="申请人">{{ currentRow?.applicant }}</el-descriptions-item>
        <el-descriptions-item label="车牌号">{{ currentRow?.plateNumber }}</el-descriptions-item>
        <el-descriptions-item label="车型">{{ currentRow?.vehicleModel }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ currentRow?.type }}</el-descriptions-item>
        <el-descriptions-item label="偏好区域">{{ currentRow?.areaPreference }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentRow?.phone }}</el-descriptions-item>
      </el-descriptions>
      <el-form ref="assignFormRef" :model="assignForm" label-width="120px">
        <el-form-item label="分配区域" prop="areaId">
          <el-select v-model="assignForm.areaId" placeholder="请选择区域" clearable style="width: 100%" @change="handleAreaChange">
            <el-option v-for="area in areaList" :key="area.id" :label="area.name" :value="area.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="指定车位" prop="spotId">
          <el-select v-model="assignForm.spotId" placeholder="请选择车位" clearable style="width: 100%">
            <el-option v-for="spot in spotList" :key="spot.id" :label="spot.label" :value="spot.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="驳回原因" prop="rejectReason">
          <el-input v-model="assignForm.rejectReason" type="textarea" :rows="3" placeholder="驳回时请填写原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignVisible = false">取消</el-button>
        <el-button type="danger" :loading="saving" @click="handleReject">驳回</el-button>
        <el-button type="primary" :loading="saving" @click="handleApprove">通过并分配</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="autoRulesVisible" title="自动分配规则" width="700px" :close-on-click-modal="false">
      <el-table :data="autoRules" border>
        <el-table-column prop="areaName" label="区域名称" min-width="120" />
        <el-table-column prop="quota" label="分配配额" width="160">
          <template #default="{ row }">
            <el-slider v-model="row.quota" :min="0" :max="100" :step="1" show-input style="padding: 0 10px" />
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="120">
          <template #default="{ row }">
            <el-input-number v-model="row.priority" :min="1" :max="99" size="small" style="width: 80px" />
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="启用" width="80" align="center">
          <template #default="{ row }"><el-switch v-model="row.enabled" /></template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="autoRulesVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingRules" @click="saveAutoRules">保存规则</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import {
  getParkingApplicationList, reviewParkingApplication, autoAssignSpot,
  getAutoAssignRules, saveAutoAssignRules, getParkingAreaList, getParkingSpotList,
} from '/@/api/parking'
import StatusBadge from '../../common/StatusBadge.vue'

defineOptions({ name: 'ParkingReview' })

const $baseMessage = inject<any>('$baseMessage')
const $baseConfirm = inject<any>('$baseConfirm')

const list = ref<any[]>([])
const loading = ref(true)
const total = ref(0)
const activeTab = ref('all')
const assignVisible = ref(false)
const currentRow = ref<any>(null)
const saving = ref(false)
const assignFormRef = ref<any>(null)
const areaList = ref<any[]>([])
const spotList = ref<any[]>([])
const autoRulesVisible = ref(false)
const autoRules = ref<any[]>([])
const savingRules = ref(false)

const assignForm = reactive({ areaId: '', spotId: '', rejectReason: '' })
const queryForm = reactive({ pageNo: 1, pageSize: 20, status: '' })

const fetchData = async () => {
  loading.value = true
  const params = { ...queryForm }
  if (activeTab.value !== 'all') params.status = activeTab.value
  const { data } = await getParkingApplicationList(params)
  list.value = data.list || []
  total.value = data.total || 0
  loading.value = false
}

const handleTabChange = () => { queryForm.pageNo = 1; fetchData() }

const handleReview = async (row: any) => {
  currentRow.value = row
  assignForm.areaId = ''; assignForm.spotId = ''; assignForm.rejectReason = ''
  spotList.value = []
  const { data } = await getParkingAreaList({ pageNo: 1, pageSize: 9999 })
  areaList.value = data.list || []
  assignVisible.value = true
}

const handleAreaChange = async (areaId: string) => {
  assignForm.spotId = ''
  if (!areaId) { spotList.value = []; return }
  const { data } = await getParkingSpotList({ areaId, pageNo: 1, pageSize: 9999 })
  spotList.value = data.list || []
}

const handleApprove = async () => {
  try {
    saving.value = true
    await reviewParkingApplication({ id: currentRow.value.id, action: 'approved', areaId: assignForm.areaId, spotId: assignForm.spotId })
    $baseMessage.success('审核通过并分配成功')
    assignVisible.value = false
    fetchData()
  } catch { /* Failed */ }
  finally { saving.value = false }
}

const handleReject = async () => {
  if (!assignForm.rejectReason) { $baseMessage.warning('请填写驳回原因'); return }
  try {
    saving.value = true
    await reviewParkingApplication({ id: currentRow.value.id, action: 'rejected', rejectReason: assignForm.rejectReason })
    $baseMessage.success('已驳回')
    assignVisible.value = false
    fetchData()
  } catch { /* Failed */ }
  finally { saving.value = false }
}

const handleAutoAssign = async (row: any) => {
  try {
    await $baseConfirm('确认自动分配车位?', '自动分配')
    await autoAssignSpot(row.id)
    $baseMessage.success('自动分配完成')
    fetchData()
  } catch { /* User cancelled or failed */ }
}

const handleAutoRules = async () => {
  const { data } = await getAutoAssignRules()
  autoRules.value = data.list || []
  autoRulesVisible.value = true
}

const saveAutoRules = async () => {
  try {
    savingRules.value = true
    await saveAutoAssignRules({ rules: autoRules.value })
    $baseMessage.success('保存成功')
    autoRulesVisible.value = false
  } catch { /* Failed */ }
  finally { savingRules.value = false }
}

const handleSizeChange = (val: number) => { queryForm.pageSize = val; fetchData() }
const handleCurrentChange = (val: number) => { queryForm.pageNo = val; fetchData() }

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.parking-review-container { padding: 20px; }
</style>

<template>
  <div class="entry-exit-container no-background-container">
    <vab-card class="auto-height-card">
      <vab-query-form>
        <vab-query-form-top-panel :span="24">
          <el-form :model="queryForm" :inline="true" @submit.prevent>
            <el-form-item label="车牌号">
              <el-input v-model="queryForm.plateNumber" placeholder="请输入车牌号" />
            </el-form-item>
            <el-form-item label="入场时间">
              <el-date-picker v-model="queryForm.entryTime" type="datetime" placeholder="选择入场时间" value-format="YYYY-MM-DD HH:mm:ss" />
            </el-form-item>
            <el-form-item label="出场时间">
              <el-date-picker v-model="queryForm.exitTime" type="datetime" placeholder="选择出场时间" value-format="YYYY-MM-DD HH:mm:ss" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
            </el-form-item>
          </el-form>
        </vab-query-form-top-panel>
      </vab-query-form>
      <el-table v-loading="loading" :data="list" border>
        <el-table-column prop="plateNumber" label="车牌号" width="120" />
        <el-table-column prop="vehicleName" label="车辆名称" width="120" />
        <el-table-column prop="type" label="车辆类型" width="110">
          <template #default="{ row }">
            <el-tag :type="typeTagType(row.type)">{{ typeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="照片" width="80" align="center">
          <template #default="{ row }">
            <photo-viewer :src="row.entryPhoto" :width="40" :height="40" />
          </template>
        </el-table-column>
        <el-table-column label="被访人信息" min-width="150">
          <template #default="{ row }">
            <span v-if="row.type === 'visitor'">{{ row.visitorName }} ({{ row.visitorDept }})</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="entryTime" label="入场时间" width="160" />
        <el-table-column prop="exitTime" label="出场时间" width="160" />
        <el-table-column prop="duration" label="停车时长" width="120" />
        <el-table-column prop="location" label="通道" width="120" />
      </el-table>
      <vab-pagination
        :current-page="queryForm.pageNo" :page-size="queryForm.pageSize" :total="total"
        @current-change="handleCurrentChange" @size-change="handleSizeChange"
      />
    </vab-card>
  </div>
</template>

<script lang="ts" setup>
import { getEntryExitRecords } from '/@/api/parking'
import PhotoViewer from '../../common/PhotoViewer.vue'

defineOptions({ name: 'AccessRecord' })

const list = ref([])
const loading = ref(true)
const total = ref(0)

const queryForm = reactive({ pageNo: 1, pageSize: 20, plateNumber: '', entryTime: '', exitTime: '' })

const typeTagType = (type: string): string => {
  const map: Record<string, string> = { staff: 'primary', visitor: 'warning', vip: 'success' }
  return map[type] || 'info'
}

const typeLabel = (type: string): string => {
  const map: Record<string, string> = { staff: '员工车辆', visitor: '访客车辆', vip: 'VIP车辆' }
  return map[type] || type
}

const fetchData = async () => {
  loading.value = true
  const { data } = await getEntryExitRecords(queryForm)
  list.value = data.list || []
  total.value = data.total || 0
  loading.value = false
}

const handleSizeChange = (val: number) => { queryForm.pageSize = val; fetchData() }
const handleCurrentChange = (val: number) => { queryForm.pageNo = val; fetchData() }

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.entry-exit-container { padding: 20px; }
</style>

<template>
  <div class="violation-container no-background-container">
    <vab-card class="auto-height-card">
      <vab-query-form>
        <vab-query-form-top-panel :span="24">
          <el-form :model="queryForm" :inline="true" @submit.prevent>
            <el-form-item>
              <el-button type="primary" native-type="submit" @click="fetchData">查询</el-button>
              <el-button type="primary" @click="handleRuleDialog">违规规则</el-button>
            </el-form-item>
          </el-form>
        </vab-query-form-top-panel>
      </vab-query-form>
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="待审核" name="pending_review" />
        <el-tab-pane label="已确认" name="confirmed" />
        <el-tab-pane label="已撤销" name="overturned" />
      </el-tabs>
      <el-table v-loading="loading" :data="list" border>
        <el-table-column prop="plateNumber" label="车牌号" width="120" />
        <el-table-column prop="violationType" label="违规类型" width="120">
          <template #default="{ row }">
            <el-tag :type="violationTypeMap[row.violationType] || 'info'" size="small">
              {{ row.violationTypeLabel || row.violationType }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="detectedAt" label="检测时间" width="170" />
        <el-table-column label="照片" width="100" align="center">
          <template #default="{ row }"><photo-viewer :src="row.photoUrl" :width="50" :height="50" /></template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }"><status-badge :status="row.status" /></template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending_review'">
              <el-button type="primary" text size="small" @click="handleReview(row)">审核</el-button>
            </template>
            <span v-else>--</span>
          </template>
        </el-table-column>
      </el-table>
      <vab-pagination
        :current-page="queryForm.pageNo" :page-size="queryForm.pageSize" :total="total"
        @current-change="handleCurrentChange" @size-change="handleSizeChange"
      />
    </vab-card>
    <el-dialog v-model="reviewVisible" title="违规审核" width="600px" :close-on-click-modal="false">
      <div style="text-align: center; margin-bottom: 16px">
        <photo-viewer :src="currentRow?.photoUrl" :width="200" :height="150" />
      </div>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="车牌号">{{ currentRow?.plateNumber }}</el-descriptions-item>
        <el-descriptions-item label="违规类型">{{ currentRow?.violationTypeLabel || currentRow?.violationType }}</el-descriptions-item>
        <el-descriptions-item label="描述">{{ currentRow?.description }}</el-descriptions-item>
        <el-descriptions-item label="检测时间">{{ currentRow?.detectedAt }}</el-descriptions-item>
      </el-descriptions>
      <el-form ref="reviewFormRef" :model="reviewForm" label-width="100px" style="margin-top: 16px">
        <el-form-item label="审核备注" prop="reviewNote">
          <el-input v-model="reviewForm.reviewNote" type="textarea" :rows="3" placeholder="请填写审核备注（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button type="success" :loading="saving" @click="handleOverturn">撤销</el-button>
        <el-button type="danger" :loading="saving" @click="handleConfirm">确认违规</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="ruleVisible" title="违规规则配置" width="600px" :close-on-click-modal="false">
      <el-form ref="ruleFormRef" :model="ruleForm" label-width="140px">
        <el-form-item label="最长停留天数" prop="maxStayDays">
          <el-input-number v-model="ruleForm.maxStayDays" :min="1" :max="365" style="width: 100%" />
        </el-form-item>
        <el-form-item label="违规告警通知" prop="alertsEnabled">
          <el-switch v-model="ruleForm.alertsEnabled" />
        </el-form-item>
        <el-form-item label="自动检测时段" prop="autoDetectTime">
          <el-time-picker v-model="ruleForm.autoDetectTime" is-range range-separator="至"
            start-placeholder="开始时间" end-placeholder="结束时间" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ruleVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingRule" @click="saveRule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { getViolationList, reviewViolation, getViolationRules, saveViolationRules } from '/@/api/parking'
import StatusBadge from '../../common/StatusBadge.vue'
import PhotoViewer from '../../common/PhotoViewer.vue'

defineOptions({ name: 'ParkingViolation' })

const $baseMessage = inject<any>('$baseMessage')

const violationTypeMap: Record<string, string> = {
  wrong_parking: 'warning', overstay: 'danger', blocking: 'danger', speeding: 'info',
}

const list = ref<any[]>([])
const loading = ref(true)
const total = ref(0)
const activeTab = ref('all')
const reviewVisible = ref(false)
const currentRow = ref<any>(null)
const saving = ref(false)
const reviewFormRef = ref<any>(null)
const ruleVisible = ref(false)
const savingRule = ref(false)
const ruleFormRef = ref<any>(null)

const reviewForm = reactive({ reviewNote: '' })
const ruleForm = reactive({ maxStayDays: 7, alertsEnabled: true, autoDetectTime: ['08:00', '20:00'] })
const queryForm = reactive({ pageNo: 1, pageSize: 20, status: '' })

const fetchData = async () => {
  loading.value = true
  const params = { ...queryForm }
  if (activeTab.value !== 'all') params.status = activeTab.value
  const { data } = await getViolationList(params)
  list.value = data.list || []
  total.value = data.total || 0
  loading.value = false
}

const handleTabChange = () => { queryForm.pageNo = 1; fetchData() }

const handleReview = (row: any) => { currentRow.value = row; reviewForm.reviewNote = ''; reviewVisible.value = true }

const handleConfirm = async () => {
  try {
    saving.value = true
    await reviewViolation(currentRow.value.id, 'confirmed')
    $baseMessage.success('已确认违规')
    reviewVisible.value = false
    fetchData()
  } catch { /* Failed */ }
  finally { saving.value = false }
}

const handleOverturn = async () => {
  try {
    saving.value = true
    await reviewViolation(currentRow.value.id, 'overturned', reviewForm.reviewNote || undefined)
    $baseMessage.success('已撤销违规')
    reviewVisible.value = false
    fetchData()
  } catch { /* Failed */ }
  finally { saving.value = false }
}

const handleRuleDialog = async () => {
  try {
    const { data } = await getViolationRules()
    ruleForm.maxStayDays = data.maxStayDays ?? 7
    ruleForm.alertsEnabled = data.alertsEnabled ?? true
    ruleForm.autoDetectTime = data.autoDetectTime ?? ['08:00', '20:00']
  } catch { /* Use defaults */ }
  ruleVisible.value = true
}

const saveRule = async () => {
  try {
    savingRule.value = true
    await saveViolationRules({ maxStayDays: ruleForm.maxStayDays, alertsEnabled: ruleForm.alertsEnabled, autoDetectTime: ruleForm.autoDetectTime })
    $baseMessage.success('保存成功')
    ruleVisible.value = false
  } catch { /* Failed */ }
  finally { savingRule.value = false }
}

const handleSizeChange = (val: number) => { queryForm.pageSize = val; fetchData() }
const handleCurrentChange = (val: number) => { queryForm.pageNo = val; fetchData() }

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.violation-container { padding: 20px; }
</style>

<template>
  <div class="visitor-linkage-container no-background-container">
    <vab-card class="auto-height-card">
      <template #title><span>访客系统联动配置</span></template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="160px" style="max-width: 600px">
        <el-form-item label="启用联动" prop="enabled"><el-switch v-model="form.enabled" /></el-form-item>
        <el-form-item label="自动白名单访客" prop="autoWhitelistVisitor"><el-switch v-model="form.autoWhitelistVisitor" /></el-form-item>
        <el-form-item label="最长停留时间(小时)" prop="maxStayHours">
          <el-input-number v-model="form.maxStayHours" :min="1" :max="720" style="width: 100%" />
        </el-form-item>
        <el-form-item label="同步间隔(分钟)" prop="syncInterval">
          <el-input-number v-model="form.syncInterval" :min="1" :max="1440" style="width: 100%" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="save">保存</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </vab-card>
  </div>
</template>

<script lang="ts" setup>
import { getVisitorLinkageConfig, saveVisitorLinkageConfig } from '/@/api/parking'

defineOptions({ name: 'ParkingVisitorLinkage' })

const $baseMessage = inject<any>('$baseMessage')

const saving = ref(false)
const formRef = ref<any>(null)

const form = reactive({ enabled: false, autoWhitelistVisitor: false, maxStayHours: 24, syncInterval: 30 })

const rules = {
  maxStayHours: [{ required: true, message: '请输入最长停留时间', trigger: 'blur' }],
  syncInterval: [{ required: true, message: '请输入同步间隔', trigger: 'blur' }],
}

const fetchConfig = async () => {
  try {
    const { data } = await getVisitorLinkageConfig()
    if (data) {
      form.enabled = data.enabled ?? false
      form.autoWhitelistVisitor = data.autoWhitelistVisitor ?? false
      form.maxStayHours = data.maxStayHours ?? 24
      form.syncInterval = data.syncInterval ?? 30
    }
  } catch { /* Use defaults */ }
}

const save = async () => {
  try {
    await formRef.value.validate()
    saving.value = true
    await saveVisitorLinkageConfig({ ...form })
    $baseMessage.success('保存成功')
  } catch { /* Validation failed or save failed */ }
  finally { saving.value = false }
}

const resetForm = () => { form.enabled = false; form.autoWhitelistVisitor = false; form.maxStayHours = 24; form.syncInterval = 30 }

onMounted(() => { fetchConfig() })
</script>

<style lang="scss" scoped>
.visitor-linkage-container { padding: 20px; }
</style>

<template>
  <div class="parking-dashboard-container no-background-container">
    <el-row :gutter="20" class="dashboard-row">
      <el-col :span="8">
        <stat-card title="当前在楼车辆" :value="realtime.currentInBuilding" color="#409EFF" subtitle="含长期停放车辆" />
      </el-col>
      <el-col :span="8">
        <stat-card title="今日入场" :value="realtime.todayEntry" color="#67C23A" subtitle="截至当前统计" />
      </el-col>
      <el-col :span="8">
        <stat-card title="今日出场" :value="realtime.todayExit" color="#E6A23C" subtitle="截至当前统计" />
      </el-col>
    </el-row>
    <el-row :gutter="20" class="dashboard-row">
      <el-col :span="12">
        <vab-card title="24小时出入趋势">
          <vab-chart :option="trendOption" style="height: 300px" />
        </vab-card>
      </el-col>
      <el-col :span="12">
        <vab-card title="车位使用率">
          <vab-chart :option="usageOption" style="height: 300px" />
        </vab-card>
      </el-col>
    </el-row>
    <el-row class="dashboard-row">
      <el-col :span="24">
        <vab-card title="最近通行记录">
          <el-table :data="realtime.recentRecords" border stripe style="width: 100%">
            <el-table-column prop="plateNumber" label="车牌号" width="140" />
            <el-table-column label="类型" width="120">
              <template #default="{ row }">
                <el-tag :type="typeTagMap[row.type] || 'info'">{{ typeLabelMap[row.type] || row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="entryTime" label="入场时间" width="180" />
            <el-table-column prop="location" label="通道位置" min-width="150" />
          </el-table>
        </vab-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { getDashboardRealtime, getParkingUsage } from '/@/api/parking'
import StatCard from '../vabAutoComponents/StatCard.vue'

defineOptions({ name: 'ParkingDashboard' })

const typeTagMap: Record<string, string> = { staff: 'primary', visitor: 'warning', vip: 'success' }
const typeLabelMap: Record<string, string> = { staff: '员工车辆', visitor: '访客车辆', vip: 'VIP车辆' }

const realtime = reactive({
  currentInBuilding: 0, todayEntry: 0, todayExit: 0, availableSpots: 0,
  hourlyTrend: [] as { hour: string; entry: number; exit: number }[],
  recentRecords: [] as { plateNumber: string; type: string; entryTime: string; location: string }[],
})

const usageData = reactive({
  total: 0, used: 0, remain: 0, usageRate: '',
  areaDetails: [] as { area: string; total: number; used: number; remain: number; rate: number }[],
  details: [] as { type: string; total: number; used: number; color: string }[],
})

const trendOption = reactive({
  tooltip: { trigger: 'axis' },
  legend: { data: ['入场', '出场'], top: 0 },
  grid: { top: 40, left: 40, right: 20, bottom: 20 },
  xAxis: { type: 'category' as const, data: [] as string[], boundaryGap: false },
  yAxis: { type: 'value' as const },
  series: [
    { name: '入场', type: 'line', data: [] as number[], smooth: true, symbol: 'circle', showSymbol: false, areaStyle: { opacity: 0.3 }, itemStyle: { color: '#409EFF' } },
    { name: '出场', type: 'line', data: [] as number[], smooth: true, symbol: 'circle', showSymbol: false, areaStyle: { opacity: 0.3 }, itemStyle: { color: '#67C23A' } },
  ],
})

const usageOption = reactive({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { top: '5%', left: 'center' },
  series: [{
    name: '车位使用率', type: 'pie', radius: ['40%', '70%'], avoidLabelOverlap: false,
    itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
    label: { show: true, formatter: '{b}\n{d}%' },
    emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
    data: [] as { value: number; name: string; itemStyle: { color: string } }[],
  }],
})

const updateTrendChart = (trend: { hour: string; entry: number; exit: number }[]) => {
  trendOption.xAxis.data = trend.map((t) => t.hour)
  trendOption.series[0].data = trend.map((t) => t.entry)
  trendOption.series[1].data = trend.map((t) => t.exit)
}

const updateUsageChart = (details: { type: string; total: number; used: number; color: string }[]) => {
  usageOption.series[0].data = details.map((d) => ({ value: d.used, name: d.type, itemStyle: { color: d.color } }))
}

const fetchDashboard = async () => {
  try {
    const res = await getDashboardRealtime()
    const d = res.data
    realtime.currentInBuilding = d.currentInBuilding; realtime.todayEntry = d.todayEntry
    realtime.todayExit = d.todayExit; realtime.availableSpots = d.availableSpots
    realtime.hourlyTrend = d.hourlyTrend || []; realtime.recentRecords = d.recentRecords || []
    updateTrendChart(d.hourlyTrend || [])
  } catch { /* silently handle */ }
}

const fetchUsage = async () => {
  try {
    const res = await getParkingUsage()
    const d = res.data
    usageData.total = d.total; usageData.used = d.used; usageData.remain = d.remain
    usageData.usageRate = d.usageRate; usageData.areaDetails = d.areaDetails || []
    usageData.details = d.details || []
    updateUsageChart(d.details || [])
  } catch { /* silently handle */ }
}

const fetchAll = () => { fetchDashboard(); fetchUsage() }

let timer: ReturnType<typeof setInterval> | null = null

onMounted(() => { fetchAll(); timer = setInterval(fetchAll, 30000) })
onBeforeUnmount(() => { if (timer) { clearInterval(timer); timer = null } })
</script>

<style lang="scss" scoped>
.parking-dashboard-container { padding: 20px; }
.dashboard-row { margin-bottom: 20px; &:last-child { margin-bottom: 0; } }
</style>

<template>
  <div class="parking-usage-container no-background-container">
    <el-row :gutter="20">
      <el-col :span="12">
        <vab-card title="今日车辆概览"><div ref="overviewChartRef" class="overview-chart"></div></vab-card>
      </el-col>
      <el-col :span="12">
        <vab-card title="车位详情">
          <div class="details-list">
            <div v-for="item in data.details" :key="item.type" class="detail-item">
              <span class="label" :style="{ color: item.color }">{{ item.type }}</span>
              <el-progress :percentage="Math.round((item.used / item.total) * 100)" :color="item.color" />
              <span class="value">{{ item.used }} / {{ item.total }}</span>
            </div>
          </div>
        </vab-card>
      </el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <vab-card title="按区域分类">
          <el-table :data="data.areaDetails" border stripe>
            <el-table-column prop="area" label="区域名称" />
            <el-table-column prop="total" label="总车位" />
            <el-table-column prop="used" label="已用车位" />
            <el-table-column prop="remain" label="剩余车位" />
            <el-table-column label="使用率" width="220">
              <template #default="{ row }"><el-progress :percentage="row.rate" /></template>
            </el-table-column>
          </el-table>
        </vab-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import * as echarts from 'echarts'
import { getParkingUsage } from '/@/api/parking'

defineOptions({ name: 'ParkingUsageStats' })

const overviewChartRef = ref<HTMLElement | null>(null)
let overviewChart: echarts.ECharts | null = null

const data = reactive<any>({ total: 0, used: 0, remain: 0, details: [], areaDetails: [] })

const initChart = () => {
  if (!overviewChartRef.value) return
  overviewChart = echarts.init(overviewChartRef.value)
  overviewChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { top: '5%', left: 'center' },
    series: [{
      name: '车位使用', type: 'pie', radius: ['40%', '70%'], avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false, position: 'center' },
      emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold' } },
      labelLine: { show: false },
      data: [
        { value: data.used, name: '已占用', itemStyle: { color: '#F56C6C' } },
        { value: data.remain, name: '剩余', itemStyle: { color: '#67C23A' } },
      ],
    }],
  })
}

const fetchData = async () => {
  const res = await getParkingUsage()
  const d = res.data
  data.total = d.total; data.used = d.used; data.remain = d.remain
  data.details = d.details; data.areaDetails = d.areaDetails
  initChart()
}

onMounted(() => { fetchData(); setInterval(fetchData, 3600000) })
onBeforeUnmount(() => { if (overviewChart) { overviewChart.dispose(); overviewChart = null } })
</script>

<style lang="scss" scoped>
.parking-usage-container { padding: 20px; }
.overview-chart { width: 100%; height: 300px; }
.details-list { padding: 20px; }
.detail-item { margin-bottom: 20px; }
.label { display: block; margin-bottom: 5px; font-weight: bold; }
.value { display: block; margin-top: 5px; text-align: right; font-size: 12px; color: #666; }
</style>

<template>
  <div class="parking-statistics-container no-background-container">
    <div class="filter-bar" style="margin-bottom: 20px; display: flex; align-items: center; flex-wrap: wrap; gap: 12px">
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至"
        start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" @change="onDateRangeChange" />
      <el-radio-group v-model="granularity">
        <el-radio-button label="day">日</el-radio-button>
        <el-radio-button label="week">周</el-radio-button>
        <el-radio-button label="month">月</el-radio-button>
      </el-radio-group>
      <el-button type="primary" @click="fetchPeriodData">查询</el-button>
    </div>
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6"><vab-card><div class="stat-item"><div class="title">今日入场</div><div class="value">{{ data.todayFlow?.entry || 0 }}</div></div></vab-card></el-col>
      <el-col :span="6"><vab-card><div class="stat-item"><div class="title">今日出场</div><div class="value">{{ data.todayFlow?.exit || 0 }}</div></div></vab-card></el-col>
      <el-col :span="6"><vab-card><div class="stat-item"><div class="title">平均停留时长</div><div class="value">{{ data.avgDuration || '-' }}</div></div></vab-card></el-col>
      <el-col :span="6"><vab-card><div class="stat-item"><div class="title">当前在楼车辆</div><div class="value">{{ data.currentInBuilding || 0 }}</div></div></vab-card></el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12"><vab-card title="24小时在楼车辆趋势"><div ref="trendChartRef" class="trend-chart"></div></vab-card></el-col>
      <el-col :span="12"><vab-card title="访客车辆停车时长（按部门）"><div ref="visitorChartRef" class="visitor-chart"></div></vab-card></el-col>
    </el-row>
    <template v-if="periodData">
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="24">
          <vab-card title="周期统计概览">
            <el-row :gutter="20">
              <el-col :span="6"><div class="stat-item"><div class="title">总入场</div><div class="value">{{ periodData.summary.totalEntry }}</div></div></el-col>
              <el-col :span="6"><div class="stat-item"><div class="title">总出场</div><div class="value">{{ periodData.summary.totalExit }}</div></div></el-col>
              <el-col :span="6"><div class="stat-item"><div class="title">平均停留时长</div><div class="value">{{ periodData.summary.avgDuration }}</div></div></el-col>
              <el-col :span="6"><div class="stat-item"><div class="title">峰值日</div><div class="value">{{ periodData.summary.peakDay }}<span v-if="periodData.summary.peakCount">({{ periodData.summary.peakCount }})</span></div></div></el-col>
            </el-row>
          </vab-card>
        </el-col>
      </el-row>
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="24">
          <vab-card title="周期车流明细">
            <el-table :data="periodData.dailyFlow" border stripe>
              <el-table-column prop="date" label="日期" />
              <el-table-column prop="entry" label="入场" />
              <el-table-column prop="exit" label="出场" />
            </el-table>
          </vab-card>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script lang="ts" setup>
import * as echarts from 'echarts'
import { getParkingStatistics, getPeriodStatistics } from '/@/api/parking'

defineOptions({ name: 'ParkingStatisticsStats' })

const trendChartRef = ref<HTMLElement | null>(null)
const visitorChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let visitorChart: echarts.ECharts | null = null

const data = reactive<any>({})

const getDefaultDateRange = () => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 7)
  const fmt = (d: Date) => { const y = d.getFullYear(); const m = String(d.getMonth() + 1).padStart(2, '0'); const day = String(d.getDate()).padStart(2, '0'); return `${y}-${m}-${day}` }
  return [fmt(start), fmt(end)]
}

const dateRange = ref<string[]>(getDefaultDateRange())
const granularity = ref<'day' | 'week' | 'month'>('day')
const periodData = ref<any>(null)

const initCharts = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    const times = data.trend.map((i: any) => i.time)
    const counts = data.trend.map((i: any) => i.count)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: times },
      yAxis: { type: 'value' },
      series: [{ data: counts, type: 'line', smooth: true, areaStyle: {} }],
    })
  }
  if (visitorChartRef.value) {
    visitorChart = echarts.init(visitorChartRef.value)
    const depts = data.visitorStats.map((i: any) => i.dept)
    const durations = data.visitorStats.map((i: any) => i.duration)
    visitorChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: depts },
      yAxis: { type: 'value', name: '小时' },
      series: [{ data: durations, type: 'bar', barWidth: '40%' }],
    })
  }
}

const fetchData = async () => {
  const res = await getParkingStatistics()
  Object.assign(data, res.data)
  nextTick(() => { initCharts() })
}

const fetchPeriodData = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) return
  const res = await getPeriodStatistics({ startDate: dateRange.value[0], endDate: dateRange.value[1], granularity: granularity.value })
  periodData.value = res.data
}

const onDateRangeChange = (value: any) => { if (value && value.length === 2) fetchPeriodData() }

onMounted(() => { fetchData(); fetchPeriodData() })
onBeforeUnmount(() => { trendChart?.dispose(); visitorChart?.dispose() })
</script>

<style lang="scss" scoped>
.parking-statistics-container { padding: 20px; }
.filter-bar { margin-bottom: 20px; }
.stat-item { text-align: center; padding: 20px 0; }
.stat-item .title { font-size: 14px; color: #909399; margin-bottom: 10px; }
.stat-item .value { font-size: 24px; font-weight: bold; color: #303133; }
.trend-chart, .visitor-chart { width: 100%; height: 300px; }
</style>

<template>
  <div class="period-selector">
    <el-date-picker v-model="dateRange" type="daterange" range-separator="至"
      start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" @change="emitChange" />
    <el-radio-group :model-value="modelValue?.granularity || 'day'" class="period-selector__granularity" @change="onGranularityChange">
      <el-radio-button value="day">日</el-radio-button>
      <el-radio-button value="week">周</el-radio-button>
      <el-radio-button value="month">月</el-radio-button>
    </el-radio-group>
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'PeriodSelector' })

interface PeriodModel { startDate: string; endDate: string; granularity: 'day' | 'week' | 'month' }

const props = defineProps<{ modelValue: PeriodModel }>()
const emit = defineEmits<{ 'update:modelValue': [value: PeriodModel] }>()

const dateRange = computed({
  get: () => [props.modelValue.startDate, props.modelValue.endDate] as [string, string],
  set: (val: [string, string]) => { emit('update:modelValue', { ...props.modelValue, startDate: val[0], endDate: val[1] }) },
})

const onGranularityChange = (val: string | number | boolean) => {
  emit('update:modelValue', { ...props.modelValue, granularity: val as 'day' | 'week' | 'month' })
}

const emitChange = () => {}
</script>

<style lang="scss" scoped>
.period-selector { display: flex; align-items: center; gap: 12px; }
.period-selector__granularity { flex-shrink: 0; }
</style>

<template>
  <div class="stat-card" :style="{ borderLeftColor: color }">
    <div class="stat-card__title">{{ title }}</div>
    <div class="stat-card__value" :style="{ color }">{{ value }}</div>
    <div v-if="subtitle" class="stat-card__subtitle">{{ subtitle }}</div>
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'StatCard' })

withDefaults(defineProps<{ title: string; value: number | string; color?: string; subtitle?: string }>(), { color: '#409EFF', subtitle: '' })
</script>

<style lang="scss" scoped>
.stat-card {
  background: #fff; border-radius: 4px; padding: 20px; border-left: 4px solid;
  transition: box-shadow 0.3s, transform 0.3s; cursor: default;
  &:hover { box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1); transform: translateY(-2px); }
  &__title { font-size: 14px; color: #909399; margin-bottom: 8px; }
  &__value { font-size: 28px; font-weight: bold; line-height: 1.2; }
  &__subtitle { font-size: 12px; color: #c0c4cc; margin-top: 6px; }
}
</style>

<template>
  <div class="charging-status-container no-background-container">
    <vab-card class="auto-height-card">
      <el-row :gutter="20">
        <el-col v-for="item in list" :key="item.id" :span="6">
          <el-card shadow="hover" class="charging-pile-card" :class="item.status">
            <div class="pile-header">
              <span class="code">{{ item.code }}</span>
              <el-tag :type="getStatusType(item.status)" size="small">{{ getStatusText(item.status) }}</el-tag>
            </div>
            <div class="pile-content">
              <p>位置: {{ item.location }}</p>
              <p>当前功率: {{ item.power }}</p>
              <p v-if="item.currentVehicle">当前车辆: {{ item.currentVehicle }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </vab-card>
  </div>
</template>

<script lang="ts" setup>
import { getChargingStatus } from '/@/api/parking'

defineOptions({ name: 'ChargingStatus' })

const list = ref<any[]>([])

const fetchData = async () => { const { data } = await getChargingStatus(); list.value = data.list || [] }

const getStatusType = (status: string) => { const map: any = { idle: 'success', busy: 'warning', fault: 'danger' }; return map[status] || 'info' }
const getStatusText = (status: string) => { const map: any = { idle: '空闲', busy: '使用中', fault: '故障' }; return map[status] || status }

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.charging-status-container { padding: 20px; }
.charging-pile-card { margin-bottom: 20px; }
.pile-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.code { font-weight: bold; font-size: 16px; }
.pile-content p { margin: 5px 0; font-size: 13px; color: #606266; }
.charging-pile-card.idle { border-left: 5px solid #67c23a; }
.charging-pile-card.busy { border-left: 5px solid #e6a23c; }
.charging-pile-card.fault { border-left: 5px solid #f56c6c; }
</style>

<template>
  <div class="photo-viewer">
    <el-image v-if="src" :src="src" :preview-src-list="[src]" :style="{ width: width + 'px', height: height + 'px' }" fit="cover" :hide-on-click-modal="true">
      <template #error>
        <div class="photo-placeholder"><el-icon><picture-filled /></el-icon><span>暂无照片</span></div>
      </template>
    </el-image>
    <div v-else class="photo-placeholder" :style="{ width: width + 'px', height: height + 'px' }">
      <el-icon><camera /></el-icon>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PictureFilled, Camera } from '@element-plus/icons-vue'

withDefaults(defineProps<{ src?: string; width?: number; height?: number }>(), { width: 60, height: 60 })
</script>

<style scoped>
.photo-placeholder {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  background: var(--el-fill-color-lighter); border: 1px dashed var(--el-border-color);
  border-radius: 4px; color: var(--el-text-color-secondary); font-size: 12px; gap: 4px;
}
.photo-placeholder .el-icon { font-size: 20px; }
</style>

<template>
  <el-input v-model="plate" :placeholder="placeholder" :clearable="true" maxlength="8" style="text-transform: uppercase" @input="onInput" />
</template>

<script lang="ts" setup>
const props = withDefaults(defineProps<{ modelValue: string; placeholder?: string }>(), { placeholder: '请输入车牌号' })
const emit = defineEmits<{ 'update:modelValue': [val: string] }>()

const plate = ref(props.modelValue)

watch(() => props.modelValue, (v) => { plate.value = v })

const onInput = (val: string) => { const upper = val.toUpperCase(); plate.value = upper; emit('update:modelValue', upper) }
</script>

<template>
  <el-tag :type="tagType" :size="size">{{ text }}</el-tag>
</template>

<script lang="ts" setup>
const props = withDefaults(defineProps<{ status: string; size?: '' | 'small' | 'large' }>(), { size: '' })

const statusMap: Record<string, [string, string]> = {
  active: ['success', '启用'], inactive: ['info', '停用'],
  pending: ['warning', '待处理'], pending_review: ['warning', '待审核'],
  approved: ['success', '已通过'], assigned: ['success', '已分配'],
  rejected: ['danger', '已拒绝'], cancelled: ['info', '已取消'],
  confirmed: ['danger', '已确认'], overturned: ['success', '已撤销'],
  occupied: ['danger', '已占用'], vacant: ['success', '空闲'],
  reserved: ['warning', '已预约'], maintenance: ['info', '维护中'],
  idle: ['success', '空闲'], busy: ['warning', '使用中'],
  fault: ['danger', '故障'], expired: ['info', '已过期'],
}

const tagType = computed(() => statusMap[props.status]?.[0] ?? 'info')
const text = computed(() => statusMap[props.status]?.[1] ?? props.status)
</script>
```
