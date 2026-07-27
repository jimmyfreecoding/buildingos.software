# 源代码提交页（智能楼宇智慧安防管理系统 buildingos.security）

## 提交要求
- 提供源程序的连续前30页与连续后30页；不足60页需提供全部源代码
- 每页不少于50行
- 源代码中不得包含公司名称、个人名称、文件名称
- 源代码总数量需与申请表保持一致

## 前30页

```
import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { HttpModule } from '@nestjs/axios';
import { ClientsModule, Transport } from '@nestjs/microservices';

// Entities
import { PatrolRouteEntity } from './entities/patrol-route.entity';
import { PatrolPlanEntity } from './entities/patrol-plan.entity';
import { PatrolTaskEntity } from './entities/patrol-task.entity';
import { FireDeviceEntity } from './entities/fire-device.entity';
import { FireAlarmEntity } from './entities/fire-alarm.entity';
import { FireLinkageEntity } from './entities/fire-linkage.entity';
import { WorkOrderEntity } from './entities/work-order.entity';
import { AlarmEventEntity } from './entities/alarm-event.entity';
import { SchedulePersonEntity } from './entities/schedule-person.entity';
import { ScheduleSpecialEntity } from './entities/schedule-special.entity';
import { ScheduleWeekEntity } from './entities/schedule-week.entity';
import { StreamDeviceEntity } from './entities/stream-device.entity';
import { TranscodeTemplateEntity } from './entities/transcode-template.entity';

// Services
import { PatrolService } from './services/patrol.service';
import { FireService } from './services/fire.service';
import { WorkOrderService } from './services/workorder.service';
import { AlarmTypeService } from './services/alarmtype.service';
import { ScheduleService } from './services/schedule.service';
import { StreamService } from './services/stream.service';
import { IncidentService } from './services/incident.service';

// Controllers
import { SecurityController } from './security.controller';
import { SecurityMqttController } from './security.mqtt.controller';
import { PatrolController } from './controllers/patrol.controller';
import { FireController } from './controllers/fire.controller';
import { WorkOrderController } from './controllers/workorder.controller';
import { AlarmTypeController } from './controllers/alarmtype.controller';
import { ScheduleController } from './controllers/schedule.controller';
import { StreamController } from './controllers/stream.controller';
import { IncidentController } from './controllers/incident.controller';

// Integration
import { HostBridge } from './integration/host-bridge.service';

const ALL_ENTITIES = [
  PatrolRouteEntity,
  PatrolPlanEntity,
  PatrolTaskEntity,
  FireDeviceEntity,
  FireAlarmEntity,
  FireLinkageEntity,
  WorkOrderEntity,
  AlarmEventEntity,
  SchedulePersonEntity,
  ScheduleSpecialEntity,
  ScheduleWeekEntity,
  StreamDeviceEntity,
  TranscodeTemplateEntity,
];

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    HttpModule,
    TypeOrmModule.forRootAsync({
      useFactory: () => {
        const dbType = (process.env.DB_TYPE || 'sqlite').toLowerCase();
        if (dbType === 'mysql') {
          return {
            type: 'mysql' as const,
            host: process.env.DB_HOST || 'localhost',
            port: parseInt(process.env.DB_PORT || '3306', 10),
            username: process.env.DB_USER || 'root',
            password: process.env.DB_PASSWORD || '',
            database: process.env.DB_NAME || 'buildingos',
            entities: ALL_ENTITIES,
            synchronize: true,
          };
        }
        if (dbType === 'postgres') {
          return {
            type: 'postgres' as const,
            host: process.env.DB_HOST || 'localhost',
            port: parseInt(process.env.DB_PORT || '5432', 10),
            username: process.env.DB_USER || 'postgres',
            password: process.env.DB_PASSWORD || 'buildingos',
            database: process.env.DB_NAME || 'buildingos',
            entities: ALL_ENTITIES,
            synchronize: true,
          };
        }
        return {
          type: 'sqlite' as const,
          database: 'apps/security/data/security.sqlite',
          autoLoadEntities: true,
          synchronize: true,
        };
      },
    }),
    TypeOrmModule.forFeature(ALL_ENTITIES),
    ClientsModule.registerAsync([
      {
        name: 'HOST_CLIENT',
        imports: [ConfigModule],
        inject: [ConfigService],
        useFactory: (config: ConfigService) => ({
          transport: Transport.MQTT,
          options: {
            url:
              config.get<string>('MQTT_BROKER_URL') || 'mqtt://localhost:1883',
            username: config.get<string>('MQTT_USERNAME'),
            password: config.get<string>('MQTT_PASSWORD'),
            subscribeOptions: { qos: 1 },
            clientId:
              'buildingos_microservice_security_' +
              Math.random().toString(16).slice(2, 8),
          },
        }),
      },
    ]),
  ],
  controllers: [
    SecurityController,
    SecurityMqttController,
    PatrolController,
    FireController,
    WorkOrderController,
    AlarmTypeController,
    ScheduleController,
    StreamController,
    IncidentController,
  ],
  providers: [
    PatrolService,
    FireService,
    WorkOrderService,
    AlarmTypeService,
    ScheduleService,
    StreamService,
    IncidentService,
    HostBridge,
  ],
})
export class AppModule {}
import { Controller, Get, Query } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { AlarmTypeService } from '../services/alarmtype.service';
import { QueryAlarmEventDto } from '../dto/incident.dto';

@ApiTags('告警类型')
@Controller('alarmtype')
export class AlarmTypeController {
  constructor(private readonly svc: AlarmTypeService) {}

  @Get('types')
  @ApiOperation({ summary: '告警类型列表（mock）' })
  getTypes() {
    return { code: 200, msg: 'success', data: this.svc.getTypes() };
  }

  @Get('eventList')
  @ApiOperation({ summary: '告警事件列表' })
  async eventList(@Query() query: QueryAlarmEventDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getEventList(query),
    };
  }
}
import { Controller, Get, Post, Body, Query, Req } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { FireService } from '../services/fire.service';
import {
  QueryFireDeviceDto,
  QueryFireAlarmDto,
  AckAlarmDto,
  LinkageEditDto,
  DeleteDto,
} from '../dto/fire.dto';
import { extractUser } from '../utils/jwt.util';

@ApiTags('消防监测')
@Controller('fire')
export class FireController {
  constructor(private readonly svc: FireService) {}

  @Get('deviceList')
  @ApiOperation({ summary: '消防设备列表' })
  async deviceList(@Query() query: QueryFireDeviceDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getDeviceList(query),
    };
  }

  @Get('alarmList')
  @ApiOperation({ summary: '消防告警列表' })
  async alarmList(@Query() query: QueryFireAlarmDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getAlarmList(query),
    };
  }

  @Post('ackAlarm')
  @ApiOperation({ summary: '确认消防告警' })
  async ackAlarm(@Body() dto: AckAlarmDto, @Req() req: any) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.ackAlarm(dto, extractUser(req)),
    };
  }

  @Get('linkageList')
  @ApiOperation({ summary: '联动规则列表' })
  async linkageList() {
    return { code: 200, msg: 'success', data: await this.svc.getLinkageList() };
  }

  @Post('linkageEdit')
  @ApiOperation({ summary: '新增/编辑联动规则' })
  async linkageEdit(@Body() dto: LinkageEditDto) {
    return { code: 200, msg: 'success', data: await this.svc.editLinkage(dto) };
  }

  @Post('linkageDelete')
  @ApiOperation({ summary: '删除联动规则' })
  async linkageDelete(@Body() dto: DeleteDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.deleteLinkage(dto),
    };
  }
}
import { Controller, Post, Body, Req } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { IncidentService } from '../services/incident.service';
import { ReportIncidentDto } from '../dto/incident.dto';
import { extractUser } from '../utils/jwt.util';

@ApiTags('事件上报')
@Controller('incident')
export class IncidentController {
  constructor(private readonly svc: IncidentService) {}

  @Post('report')
  @ApiOperation({ summary: '上报安防事件' })
  async report(@Body() dto: ReportIncidentDto, @Req() req: any) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.report(dto, extractUser(req)),
    };
  }
}
import { Controller, Get, Post, Body, Query, Req } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { PatrolService } from '../services/patrol.service';
import {
  RouteEditDto,
  PlanEditDto,
  TaskCreateDto,
  QueryTaskDto,
  ReportAnomalyDto,
  DeleteDto,
} from '../dto/patrol.dto';
import { extractUser } from '../utils/jwt.util';

@ApiTags('视频巡更')
@Controller('patrol')
export class PatrolController {
  constructor(private readonly svc: PatrolService) {}

  @Get('routeList')
  @ApiOperation({ summary: '获取巡更路线列表' })
  async routeList() {
    return { code: 200, msg: 'success', data: await this.svc.getRouteList() };
  }

  @Post('routeEdit')
  @ApiOperation({ summary: '新增/编辑巡更路线' })
  async routeEdit(@Body() dto: RouteEditDto) {
    return { code: 200, msg: 'success', data: await this.svc.editRoute(dto) };
  }

  @Post('routeDelete')
  @ApiOperation({ summary: '删除巡更路线' })
  async routeDelete(@Body() dto: DeleteDto) {
    return { code: 200, msg: 'success', data: await this.svc.deleteRoute(dto) };
  }

  @Get('planList')
  @ApiOperation({ summary: '获取巡更计划列表' })
  async planList() {
    return { code: 200, msg: 'success', data: await this.svc.getPlanList() };
  }

  @Post('planEdit')
  @ApiOperation({ summary: '新增/编辑巡更计划' })
  async planEdit(@Body() dto: PlanEditDto) {
    return { code: 200, msg: 'success', data: await this.svc.editPlan(dto) };
  }

  @Post('planDelete')
  @ApiOperation({ summary: '删除巡更计划' })
  async planDelete(@Body() dto: DeleteDto) {
    return { code: 200, msg: 'success', data: await this.svc.deletePlan(dto) };
  }

  @Get('taskList')
  @ApiOperation({ summary: '获取巡更任务列表' })
  async taskList(@Query() query: QueryTaskDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getTaskList(query),
    };
  }

  @Post('taskCreate')
  @ApiOperation({ summary: '创建巡更任务' })
  async taskCreate(@Body() dto: TaskCreateDto) {
    return { code: 200, msg: 'success', data: await this.svc.createTask(dto) };
  }

  @Post('reportAnomaly')
  @ApiOperation({ summary: '上报巡更异常' })
  async reportAnomaly(@Body() dto: ReportAnomalyDto, @Req() req: any) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.reportAnomaly(dto, extractUser(req)),
    };
  }
}
import { Controller, Get, Post, Body } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { ScheduleService } from '../services/schedule.service';
import {
  PersonEditDto,
  SpecialDateEditDto,
  WeekEditDto,
  DeleteDto,
} from '../dto/schedule.dto';

@ApiTags('告警排班')
@Controller('schedule')
export class ScheduleController {
  constructor(private readonly svc: ScheduleService) {}

  @Get('personList')
  @ApiOperation({ summary: '排班人员列表' })
  async personList() {
    return { code: 200, msg: 'success', data: await this.svc.getPersonList() };
  }

  @Post('personEdit')
  @ApiOperation({ summary: '新增/编辑排班人员' })
  async personEdit(@Body() dto: PersonEditDto) {
    return { code: 200, msg: 'success', data: await this.svc.editPerson(dto) };
  }

  @Post('personDelete')
  @ApiOperation({ summary: '删除排班人员' })
  async personDelete(@Body() dto: DeleteDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.deletePerson(dto),
    };
  }

  @Get('specialDateList')
  @ApiOperation({ summary: '特定日期排班列表' })
  async specialDateList() {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getSpecialDateList(),
    };
  }

  @Post('specialDateEdit')
  @ApiOperation({ summary: '新增/编辑特定日期排班' })
  async specialDateEdit(@Body() dto: SpecialDateEditDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.editSpecialDate(dto),
    };
  }

  @Post('specialDateDelete')
  @ApiOperation({ summary: '删除特定日期排班' })
  async specialDateDelete(@Body() dto: DeleteDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.deleteSpecialDate(dto),
    };
  }

  @Get('weekList')
  @ApiOperation({ summary: '周排班列表' })
  async weekList() {
    return { code: 200, msg: 'success', data: await this.svc.getWeekList() };
  }

  @Post('weekEdit')
  @ApiOperation({ summary: '新增/编辑周排班' })
  async weekEdit(@Body() dto: WeekEditDto) {
    return { code: 200, msg: 'success', data: await this.svc.editWeek(dto) };
  }

  @Post('weekDelete')
  @ApiOperation({ summary: '删除周排班' })
  async weekDelete(@Body() dto: DeleteDto) {
    return { code: 200, msg: 'success', data: await this.svc.deleteWeek(dto) };
  }
}
import { Controller, Get, Post, Body, Query } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { StreamService } from '../services/stream.service';
import {
  ControlServiceDto,
  StreamDeviceEditDto,
  QueryStreamDeviceDto,
  TranscodeEditDto,
  FlowDeleteDto,
  QueryFlowDto,
  QueryGb28181Dto,
  Gb28181StopDto,
  DeleteDto,
} from '../dto/stream.dto';

@ApiTags('流媒体平台')
@Controller('stream')
export class StreamController {
  constructor(private readonly svc: StreamService) {}

  @Get('platformStatus')
  @ApiOperation({ summary: '平台服务状态' })
  async platformStatus() {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getPlatformStatus(),
    };
  }

  @Post('control')
  @ApiOperation({ summary: '服务控制' })
  control(@Body() dto: ControlServiceDto) {
    return { code: 200, msg: 'success', data: this.svc.controlService(dto) };
  }

  @Get('zlmConfig')
  @ApiOperation({ summary: 'ZLM配置信息' })
  zlmConfig() {
    return { code: 200, msg: 'success', data: this.svc.getZlmConfig() };
  }

  @Get('deviceList')
  @ApiOperation({ summary: '流媒体设备列表' })
  async deviceList(@Query() query: QueryStreamDeviceDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getDeviceList(query),
    };
  }

  @Post('deviceEdit')
  @ApiOperation({ summary: '新增/编辑流媒体设备' })
  async deviceEdit(@Body() dto: StreamDeviceEditDto) {
    return { code: 200, msg: 'success', data: await this.svc.editDevice(dto) };
  }

  @Post('deviceDelete')
  @ApiOperation({ summary: '删除流媒体设备' })
  async deviceDelete(@Body() dto: DeleteDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.deleteDevice(dto),
    };
  }

  @Get('transcodeList')
  @ApiOperation({ summary: '转码模板列表' })
  async transcodeList() {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getTranscodeList(),
    };
  }

  @Post('transcodeEdit')
  @ApiOperation({ summary: '新增/编辑转码模板' })
  async transcodeEdit(@Body() dto: TranscodeEditDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.editTranscode(dto),
    };
  }

  @Post('transcodeDelete')
  @ApiOperation({ summary: '删除转码模板' })
  async transcodeDelete(@Body() dto: DeleteDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.deleteTranscode(dto),
    };
  }

  @Get('flowList')
  @ApiOperation({ summary: '活跃流列表' })
  async flowList(@Query() query: QueryFlowDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getFlowList(query),
    };
  }

  @Post('flowDelete')
  @ApiOperation({ summary: '关闭流' })
  async flowDelete(@Body() dto: FlowDeleteDto) {
    return { code: 200, msg: 'success', data: await this.svc.deleteFlow(dto) };
  }

  @Get('gb28181List')
  @ApiOperation({ summary: 'GB28181设备列表' })
  async gb28181List(@Query() query: QueryGb28181Dto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getGb28181List(query),
    };
  }

  @Post('gb28181Stop')
  @ApiOperation({ summary: '停止GB28181流' })
  gb28181Stop(@Body() dto: Gb28181StopDto) {
    return { code: 200, msg: 'success', data: this.svc.stopGb28181(dto) };
  }

  @Get('resourceMonitor')
  @ApiOperation({ summary: '资源监控' })
  async resourceMonitor() {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getResourceMonitor(),
    };
  }
}
import { Controller, Get, Post, Body, Query, Req } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { WorkOrderService } from '../services/workorder.service';
import {
  QueryWorkOrderDto,
  WorkOrderEditDto,
  AssignDto,
  DeleteDto,
} from '../dto/workorder.dto';
import { extractUser } from '../utils/jwt.util';

@ApiTags('告警工单')
@Controller('workorder')
export class WorkOrderController {
  constructor(private readonly svc: WorkOrderService) {}

  @Get('getList')
  @ApiOperation({ summary: '工单列表' })
  async getList(@Query() query: QueryWorkOrderDto) {
    return { code: 200, msg: 'success', data: await this.svc.getList(query) };
  }

  @Post('doEdit')
  @ApiOperation({ summary: '新增/编辑工单' })
  async doEdit(@Body() dto: WorkOrderEditDto, @Req() req: any) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.doEdit(dto, extractUser(req)),
    };
  }

  @Post('doDelete')
  @ApiOperation({ summary: '删除工单' })
  async doDelete(@Body() dto: DeleteDto) {
    return { code: 200, msg: 'success', data: await this.svc.doDelete(dto) };
  }

  @Post('assign')
  @ApiOperation({ summary: '分配工单' })
  async assign(@Body() dto: AssignDto) {
    return { code: 200, msg: 'success', data: await this.svc.assign(dto) };
  }
}
import { ApiProperty } from '@nestjs/swagger';

export class QueryFireDeviceDto {
  @ApiProperty({ required: false }) type?: string;
  @ApiProperty({ required: false }) status?: string;
}

export class QueryFireAlarmDto {
  @ApiProperty({ required: false }) level?: string;
  @ApiProperty({ required: false }) status?: string;
  @ApiProperty({ required: false, default: 1 }) pageNo?: number;
  @ApiProperty({ required: false, default: 20 }) pageSize?: number;
}

export class AckAlarmDto {
  @ApiProperty() id!: string;
}

export class LinkageEditDto {
  @ApiProperty({ required: false }) id?: string;
  @ApiProperty() name!: string;
  @ApiProperty({ required: false, default: 'fire_alarm' }) triggerType?: string;
  @ApiProperty({ required: false, default: 'all' }) triggerArea?: string;
  @ApiProperty({ required: false }) action?: string;
  @ApiProperty({ required: false }) targetDescription?: string;
  @ApiProperty({ required: false, default: true }) enabled?: boolean;
}

export class DeleteDto {
  @ApiProperty() id!: string;
}
import { ApiProperty } from '@nestjs/swagger';

export class ReportIncidentDto {
  @ApiProperty() alarmType!: string;
  @ApiProperty() urgency!: string;
  @ApiProperty() description!: string;
  @ApiProperty({ required: false }) cameraId?: string;
  @ApiProperty({ required: false, description: 'Base64 截图' })
  snapshot?: string;
  @ApiProperty({ required: false }) location?: string;
  @ApiProperty({ required: false }) reporter?: string;
}

export class QueryAlarmEventDto {
  @ApiProperty({ description: 'emergency | fire | water_leak | smoke' })
  type!: string;
  @ApiProperty({ required: false }) status?: string;
  @ApiProperty({ required: false, default: 1 }) pageNo?: number;
  @ApiProperty({ required: false, default: 20 }) pageSize?: number;
}
import { ApiProperty } from '@nestjs/swagger';

export class RouteEditDto {
  @ApiProperty({ required: false }) id?: string;
  @ApiProperty() name!: string;
  @ApiProperty({ required: false }) description?: string;
  @ApiProperty({ required: false, type: [String] }) cameraIds?: string[];
  @ApiProperty({ required: false, default: 'active' }) status?: string;
}

export class PlanEditDto {
  @ApiProperty({ required: false }) id?: string;
  @ApiProperty() name!: string;
  @ApiProperty() routeId!: string;
  @ApiProperty({ required: false }) startTime?: string;
  @ApiProperty({ required: false }) endTime?: string;
  @ApiProperty({ required: false, default: 120 }) intervalMin?: number;
  @ApiProperty({ required: false, type: [Number] }) weekDays?: number[];
  @ApiProperty({ required: false, default: 'active' }) status?: string;
}

export class TaskCreateDto {
  @ApiProperty() planId!: string;
  @ApiProperty() executor!: string;
}

export class QueryTaskDto {
  @ApiProperty({ required: false }) status?: string;
}

export class ReportAnomalyDto {
  @ApiProperty() taskId!: string;
  @ApiProperty({ required: false }) cameraId?: string;
  @ApiProperty() alarmType!: string;
  @ApiProperty() urgency!: string;
  @ApiProperty() description!: string;
}

export class DeleteDto {
  @ApiProperty() id!: string;
}
import { ApiProperty } from '@nestjs/swagger';

export class PersonEditDto {
  @ApiProperty({ required: false }) id?: string;
  @ApiProperty() name!: string;
  @ApiProperty({ required: false }) phone?: string;
  @ApiProperty({ required: false }) email?: string;
  @ApiProperty({ required: false }) role?: string;
  @ApiProperty({ required: false }) alarmRule?: string;
  @ApiProperty({ required: false, default: 'active' }) status?: string;
}

export class SpecialDateEditDto {
  @ApiProperty({ required: false }) id?: string;
  @ApiProperty() name!: string;
  @ApiProperty({ required: false, type: [String] }) dateRange?: [
    string,
    string,
  ];
  @ApiProperty({ required: false, type: [String] }) personIds?: string[];
  @ApiProperty({ required: false }) deviceGroup?: string;
  @ApiProperty({ required: false }) note?: string;
}

export class WeekEditDto {
  @ApiProperty({ required: false }) id?: string;
  @ApiProperty() name!: string;
  @ApiProperty({ required: false, type: [String] }) personIds?: string[];
  @ApiProperty({ required: false }) deviceGroup?: string;
  @ApiProperty({ required: false, type: [Number] }) weekDays?: number[];
  @ApiProperty({ required: false }) startTime?: string;
  @ApiProperty({ required: false }) endTime?: string;
}

export class DeleteDto {
  @ApiProperty() id!: string;
}
import { ApiProperty } from '@nestjs/swagger';

export class ControlServiceDto {
  @ApiProperty({ description: 'zlm | sip | proxy | record' }) service!: string;
  @ApiProperty({ description: 'start | stop | restart' }) action!: string;
}

export class StreamDeviceEditDto {
  @ApiProperty({ required: false }) id?: string;
  @ApiProperty() name!: string;
  @ApiProperty({ required: false }) deviceType?: string;
  @ApiProperty({ required: false }) brand?: string;
  @ApiProperty({ required: false }) ip?: string;
  @ApiProperty({ required: false, default: 554 }) port?: number;
  @ApiProperty({ required: false }) username?: string;
  @ApiProperty({ required: false }) password?: string;
  @ApiProperty({ required: false, default: 1 }) channelCount?: number;
}

export class QueryStreamDeviceDto {
  @ApiProperty({ required: false }) deviceType?: string;
  @ApiProperty({ required: false }) status?: string;
}

export class TranscodeEditDto {
  @ApiProperty({ required: false }) id?: string;
  @ApiProperty() name!: string;
  @ApiProperty({ required: false }) resolution?: string;
  @ApiProperty({ required: false }) videoBitrate?: number;
  @ApiProperty({ required: false }) fps?: number;
  @ApiProperty({ required: false }) audioBitrate?: number;
  @ApiProperty({ required: false, default: 'h264' }) codec?: string;
  @ApiProperty({ required: false, default: true }) enabled?: boolean;
}

export class FlowDeleteDto {
  @ApiProperty() app!: string;
  @ApiProperty() stream!: string;
}

export class QueryFlowDto {
  @ApiProperty({ required: false }) keyword?: string;
}

export class QueryGb28181Dto {
  @ApiProperty({ required: false }) status?: string;
}

export class Gb28181StopDto {
  @ApiProperty() deviceId!: string;
}

export class DeleteDto {
  @ApiProperty() id!: string;
}
import { ApiProperty } from '@nestjs/swagger';

export class QueryWorkOrderDto {
  @ApiProperty({ required: false }) keyword?: string;
  @ApiProperty({ required: false }) status?: string;
  @ApiProperty({ required: false }) alarmType?: string;
  @ApiProperty({ required: false, default: 1 }) pageNo?: number;
  @ApiProperty({ required: false, default: 20 }) pageSize?: number;
}

export class WorkOrderEditDto {
  @ApiProperty({ required: false }) id?: string;
  @ApiProperty({ required: false }) alarmType?: string;
  @ApiProperty({ required: false }) urgency?: string;
  @ApiProperty({ required: false }) location?: string;
  @ApiProperty({ required: false }) status?: string;
  @ApiProperty({ required: false }) description?: string;
  @ApiProperty({ required: false }) handleNote?: string;
  @ApiProperty({ required: false }) reporter?: string;
}

export class AssignDto {
  @ApiProperty() id!: string;
  @ApiProperty() assignee!: string;
}

export class DeleteDto {
  @ApiProperty() id!: string;
}
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
} from 'typeorm';

@Entity('security_alarm_event')
export class AlarmEventEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ length: 30, nullable: true })
  type?: string;

  @Column({ length: 100, nullable: true })
  name?: string;

  @Column({ length: 200, nullable: true })
  location?: string;

  @Column({ length: 20, nullable: true })
  level?: string;

  @Column({ length: 20, default: 'unresolved' })
  status!: string;

  @Column({ name: 'trigger_time', nullable: true })
  triggerTime?: Date;

  @Column({ length: 50, nullable: true })
  handler?: string;

  @Column({ name: 'resolve_time', nullable: true })
  resolveTime?: Date;

  @Column({ length: 500, nullable: true })
  note?: string;

  @CreateDateColumn({ name: 'create_time' })
  createTime!: Date;
}
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
} from 'typeorm';

@Entity('security_fire_alarm')
export class FireAlarmEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ name: 'device_id', length: 36, nullable: true })
  deviceId?: string;

  @Column({ name: 'device_name', length: 100, nullable: true })
  deviceName?: string;

  @Column({ length: 50, nullable: true })
  type?: string;

  @Column({ length: 20, nullable: true })
  floor?: string;

  @Column({ length: 100, nullable: true })
  area?: string;

  @Column({ length: 20, nullable: true })
  level?: string;

  @Column({ nullable: true })
  time?: Date;

  @Column({ length: 20, default: 'unresolved' })
  status!: string;

  @Column({ length: 50, nullable: true })
  handler?: string;

  @Column({ name: 'resolve_time', nullable: true })
  resolveTime?: Date;

  @Column({ length: 500, nullable: true })
  note?: string;

  @CreateDateColumn({ name: 'create_time' })
  createTime!: Date;
}
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';

@Entity('security_fire_device')
export class FireDeviceEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ length: 100 })
  name!: string;

  @Column({ length: 50, nullable: true })
  type?: string;

  @Column({ length: 20, nullable: true })
  floor?: string;

  @Column({ length: 100, nullable: true })
  area?: string;

  @Column({ length: 20, default: 'normal' })
  status!: string;

  @Column({ default: true })
  online!: boolean;

  @Column({ name: 'last_alarm_time', nullable: true })
  lastAlarmTime?: Date;

  @CreateDateColumn({ name: 'create_time' })
  createTime!: Date;

  @UpdateDateColumn({ name: 'update_time' })
  updateTime!: Date;
}
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';

@Entity('security_fire_linkage')
export class FireLinkageEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ length: 100 })
  name!: string;

  @Column({ name: 'trigger_type', length: 50, default: 'fire_alarm' })
  triggerType!: string;

  @Column({ name: 'trigger_area', length: 50, default: 'all' })
  triggerArea!: string;

  @Column({ length: 50, nullable: true })
  action?: string;

  @Column({ name: 'target_description', length: 500, nullable: true })
  targetDescription?: string;

  @Column({ default: true })
  enabled!: boolean;

  @CreateDateColumn({ name: 'create_time' })
  createTime!: Date;

  @UpdateDateColumn({ name: 'update_time' })
  updateTime!: Date;
}
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';

@Entity('security_patrol_plan')
export class PatrolPlanEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ length: 100 })
  name!: string;

  @Column({ name: 'route_id', length: 36 })
  routeId!: string;

  @Column({ name: 'start_time', length: 10, nullable: true })
  startTime?: string;

  @Column({ name: 'end_time', length: 10, nullable: true })
  endTime?: string;

  @Column({ name: 'interval_min', default: 120 })
  intervalMin!: number;

  @Column({ name: 'week_days', type: 'simple-json', nullable: true })
  weekDays?: number[];

  @Column({ length: 20, default: 'active' })
  status!: string;

  @CreateDateColumn({ name: 'create_time' })
  createTime!: Date;

  @UpdateDateColumn({ name: 'update_time' })
  updateTime!: Date;
}
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';

@Entity('security_patrol_route')
export class PatrolRouteEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ length: 100 })
  name!: string;

  @Column({ length: 500, nullable: true })
  description?: string;

  @Column({ name: 'camera_ids', type: 'simple-json', nullable: true })
  cameraIds?: string[];

  @Column({ length: 20, default: 'active' })
  status!: string;

  @CreateDateColumn({ name: 'create_time' })
  createTime!: Date;

  @UpdateDateColumn({ name: 'update_time' })
  updateTime!: Date;
}
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';

@Entity('security_patrol_task')
export class PatrolTaskEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ name: 'plan_id', length: 36, nullable: true })
  planId?: string;

  @Column({ name: 'route_id', length: 36, nullable: true })
  routeId?: string;

  @Column({ length: 50, nullable: true })
  executor?: string;

  @Column({ name: 'start_time', nullable: true })
  startTime?: Date;

  @Column({ name: 'end_time', nullable: true })
  endTime?: Date;

  @Column({ length: 20, default: 'pending' })
  status!: string;

  @Column({ default: 0 })
  progress!: number;

  @Column({ name: 'anomaly_count', default: 0 })
  anomalyCount!: number;

  @CreateDateColumn({ name: 'create_time' })
  createTime!: Date;

  @UpdateDateColumn({ name: 'update_time' })
  updateTime!: Date;
}
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';

@Entity('security_schedule_person')
export class SchedulePersonEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ length: 50 })
  name!: string;

  @Column({ length: 20, nullable: true })
  phone?: string;

  @Column({ length: 100, nullable: true })
  email?: string;

  @Column({ length: 50, nullable: true })
  role?: string;

  @Column({ name: 'alarm_rule', length: 200, nullable: true })
  alarmRule?: string;

  @Column({ length: 20, default: 'active' })
  status!: string;

  @CreateDateColumn({ name: 'create_time' })
  createTime!: Date;

  @UpdateDateColumn({ name: 'update_time' })
  updateTime!: Date;
}
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';

@Entity('security_schedule_special')
export class ScheduleSpecialEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ length: 100 })
  name!: string;

  @Column({ name: 'date_start', length: 20, nullable: true })
  dateStart?: string;

  @Column({ name: 'date_end', length: 20, nullable: true })
  dateEnd?: string;

  @Column({ name: 'person_ids', type: 'simple-json', nullable: true })
  personIds?: string[];

  @Column({ name: 'device_group', length: 200, nullable: true })
  deviceGroup?: string;

  @Column({ length: 500, nullable: true })
  note?: string;

  @CreateDateColumn({ name: 'create_time' })
  createTime!: Date;

  @UpdateDateColumn({ name: 'update_time' })
  updateTime!: Date;
}
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';

@Entity('security_schedule_week')
export class ScheduleWeekEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ length: 100 })
  name!: string;

  @Column({ name: 'person_ids', type: 'simple-json', nullable: true })
  personIds?: string[];

  @Column({ name: 'device_group', length: 200, nullable: true })
  deviceGroup?: string;

  @Column({ name: 'week_days', type: 'simple-json', nullable: true })
  weekDays?: number[];

  @Column({ name: 'start_time', length: 10, nullable: true })
  startTime?: string;

  @Column({ name: 'end_time', length: 10, nullable: true })
  endTime?: string;

  @CreateDateColumn({ name: 'create_time' })
  createTime!: Date;

  @UpdateDateColumn({ name: 'update_time' })
  updateTime!: Date;
}
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';

@Entity('security_stream_device')
export class StreamDeviceEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ length: 100 })
  name!: string;

  @Column({ name: 'device_type', length: 20, nullable: true })
  deviceType?: string;

  @Column({ length: 50, nullable: true })
  brand?: string;

  @Column({ length: 50, nullable: true })
  ip?: string;

  @Column({ default: 554 })
  port!: number;

  @Column({ length: 50, nullable: true })
  username?: string;

  @Column({ name: 'password_enc', length: 200, nullable: true })
  passwordEnc?: string;

  @Column({ name: 'channel_count', default: 1 })
  channelCount!: number;

  @Column({ length: 20, default: 'offline' })
  status!: string;

  @CreateDateColumn({ name: 'create_time' })
  createTime!: Date;

  @UpdateDateColumn({ name: 'update_time' })
  updateTime!: Date;
}
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';

@Entity('security_transcode_template')
export class TranscodeTemplateEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ length: 100 })
  name!: string;

  @Column({ length: 20, nullable: true })
  resolution?: string;

  @Column({ name: 'video_bitrate', nullable: true })
  videoBitrate?: number;

  @Column({ nullable: true })
  fps?: number;

  @Column({ name: 'audio_bitrate', nullable: true })
  audioBitrate?: number;

  @Column({ length: 20, default: 'h264' })
  codec!: string;

  @Column({ default: true })
  enabled!: boolean;

  @CreateDateColumn({ name: 'create_time' })
  createTime!: Date;

  @UpdateDateColumn({ name: 'update_time' })
  updateTime!: Date;
}
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';

@Entity('security_work_order')
export class WorkOrderEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ name: 'order_no', length: 50, unique: true, nullable: true })
  orderNo?: string;

  @Column({ name: 'alarm_type', length: 50, nullable: true })
  alarmType?: string;

  @Column({ length: 20, nullable: true })
  urgency?: string;

  @Column({ length: 30, default: 'pending_assign' })
  status!: string;

  @Column({ length: 200, nullable: true })
  location?: string;

  @Column({ type: 'text', nullable: true })
  description?: string;

  @Column({ length: 50, nullable: true })
  reporter?: string;

  @Column({ length: 50, nullable: true })
  assignee?: string;

  @Column({ name: 'handle_note', type: 'text', nullable: true })
  handleNote?: string;

  @CreateDateColumn({ name: 'create_time' })
  createTime!: Date;

  @Column({ name: 'resolve_time', nullable: true })
  resolveTime?: Date;

  @UpdateDateColumn({ name: 'update_time' })
  updateTime!: Date;
}
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
import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as swagger from '@nestjs/swagger';
import { Transport, MicroserviceOptions } from '@nestjs/microservices';
import { Logger } from '@nestjs/common';

async function bootstrap() {
  const logger = new Logger('SecurityBootstrap');
  const app = await NestFactory.create(AppModule);
  app.setGlobalPrefix('security');
  app.enableCors();

  try {
    const url = process.env.MQTT_BROKER_URL;
    if (url) {
      // eslint-disable-next-line @typescript-eslint/await-thenable
      await app.connectMicroservice<MicroserviceOptions>({
        transport: Transport.MQTT,
        options: { url, subscribeOptions: { qos: 1 } },
      });

      await app.startAllMicroservices();
      logger.log(`MQTT microservice started, url=${url}`);
    }
  } catch (e) {
    logger.warn(`MQTT connect failed: ${e}`);
  }

  const config = new swagger.DocumentBuilder()
    .setTitle('Security API')
    .setDescription('安防管控微服务接口文档')
    .setVersion('1.0')
    .addBearerAuth()
    .build();
  const doc = swagger.SwaggerModule.createDocument(app, config);
  swagger.SwaggerModule.setup('security/docs', app, doc);

  const port = parseInt(process.env.PORT || '3015', 10);
  await app.listen(port);
  logger.log(`Security service running on port ${port}`);
}
void bootstrap();
import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';

@ApiTags('健康检查')
@Controller()
export class SecurityController {
  @Get('health')
  @ApiOperation({ summary: '健康检查' })
  health() {
    return { status: 'ok', service: 'security' };
  }

  @Get('menu.json')
  @ApiOperation({ summary: '菜单配置' })
  menuJson() {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    return require('../menu.json');
  }
}
import { Controller, Logger } from '@nestjs/common';
import { MessagePattern, Payload } from '@nestjs/microservices';

@Controller()
export class SecurityMqttController {
  private readonly logger = new Logger(SecurityMqttController.name);

  @MessagePattern('security/#')
  handle(@Payload() data: unknown) {
    this.logger.debug(`MQTT security/#: ${JSON.stringify(data)}`);
    return { code: 200, data };
  }
}
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { AlarmEventEntity } from '../entities/alarm-event.entity';
import { QueryAlarmEventDto } from '../dto/incident.dto';

const MOCK_ALARM_TYPES = [
  { value: 'emergency', label: '紧急事件' },
  { value: 'fire', label: '火警' },
  { value: 'smoke', label: '烟雾告警' },
  { value: 'water_leak', label: '漏水告警' },
  { value: 'gas_leak', label: '燃气泄漏' },
  { value: 'intrusion', label: '非法入侵' },
  { value: 'device_fault', label: '设备故障' },
  { value: 'power_outage', label: '停电告警' },
  { value: 'elevator_fault', label: '电梯故障' },
  { value: 'temperature_alert', label: '温度异常' },
  { value: 'humidity_alert', label: '湿度异常' },
  { value: 'access_control', label: '门禁异常' },
  { value: 'video_loss', label: '视频丢失' },
  { value: 'perimeter', label: '周界告警' },
];

@Injectable()
export class AlarmTypeService {
  constructor(
    @InjectRepository(AlarmEventEntity)
    private repo: Repository<AlarmEventEntity>,
  ) {}

  getTypes() {
    return MOCK_ALARM_TYPES;
  }

  async getEventList(query: QueryAlarmEventDto) {
    const pageNo = Number(query.pageNo) || 1;
    const pageSize = Number(query.pageSize) || 20;
    const qb = this.repo
      .createQueryBuilder('e')
      .andWhere('e.type = :type', { type: query.type });
    if (query.status)
      qb.andWhere('e.status = :status', { status: query.status });
    const [list, total] = await qb
      .orderBy('e.create_time', 'DESC')
      .skip((pageNo - 1) * pageSize)
      .take(pageSize)
      .getManyAndCount();
    return { list, total };
  }
}
import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { FireDeviceEntity } from '../entities/fire-device.entity';
import { FireAlarmEntity } from '../entities/fire-alarm.entity';
import { FireLinkageEntity } from '../entities/fire-linkage.entity';
import {
  QueryFireDeviceDto,
  QueryFireAlarmDto,
  AckAlarmDto,
  LinkageEditDto,
  DeleteDto,
} from '../dto/fire.dto';

@Injectable()
export class FireService {
  private readonly logger = new Logger(FireService.name);

  constructor(
    @InjectRepository(FireDeviceEntity)
    private deviceRepo: Repository<FireDeviceEntity>,
    @InjectRepository(FireAlarmEntity)
    private alarmRepo: Repository<FireAlarmEntity>,
    @InjectRepository(FireLinkageEntity)
    private linkageRepo: Repository<FireLinkageEntity>,
  ) {}

  // ── 消防设备 ─────────────────────────────────────────────────────────────────

  async getDeviceList(query: QueryFireDeviceDto) {
    const qb = this.deviceRepo.createQueryBuilder('d');
    if (query.type) qb.andWhere('d.type = :type', { type: query.type });
    if (query.status)
      qb.andWhere('d.status = :status', { status: query.status });
    const list = await qb.orderBy('d.create_time', 'DESC').getMany();
    return { list, total: list.length };
  }

  // ── 消防告警 ─────────────────────────────────────────────────────────────────

  async getAlarmList(query: QueryFireAlarmDto) {
    const pageNo = Number(query.pageNo) || 1;
    const pageSize = Number(query.pageSize) || 20;
    const qb = this.alarmRepo.createQueryBuilder('a');
    if (query.level) qb.andWhere('a.level = :level', { level: query.level });
    if (query.status)
      qb.andWhere('a.status = :status', { status: query.status });
    const [list, total] = await qb
      .orderBy('a.create_time', 'DESC')
      .skip((pageNo - 1) * pageSize)
      .take(pageSize)
      .getManyAndCount();
    return { list, total };
  }

  async ackAlarm(dto: AckAlarmDto, handler: string) {
    await this.alarmRepo.update(dto.id, {
      status: 'resolved',
      handler,
      resolveTime: new Date(),
    });
    // 更新关联消防设备状态
    const alarm = await this.alarmRepo.findOneBy({ id: dto.id });
    if (alarm?.deviceId) {
      await this.deviceRepo.update(alarm.deviceId, { status: 'normal' });
    }
    return { success: true };
  }

  // ── 联动规则 ─────────────────────────────────────────────────────────────────

  async getLinkageList() {
    const list = await this.linkageRepo.find({ order: { createTime: 'DESC' } });
    return { list, total: list.length };
  }

  async editLinkage(dto: LinkageEditDto) {
    if (dto.id) {
      await this.linkageRepo.update(dto.id, {
        name: dto.name,
        triggerType: dto.triggerType ?? 'fire_alarm',
        triggerArea: dto.triggerArea ?? 'all',
        action: dto.action,
        targetDescription: dto.targetDescription,
        enabled: dto.enabled ?? true,
      });
      return this.linkageRepo.findOneBy({ id: dto.id });
    }
    const entity = this.linkageRepo.create({
      name: dto.name,
      triggerType: dto.triggerType ?? 'fire_alarm',
      triggerArea: dto.triggerArea ?? 'all',
      action: dto.action,
      targetDescription: dto.targetDescription,
      enabled: dto.enabled ?? true,
    });
    return this.linkageRepo.save(entity);
  }

  async deleteLinkage(dto: DeleteDto) {
    await this.linkageRepo.delete(dto.id);
    return { success: true };
  }
}
import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { AlarmEventEntity } from '../entities/alarm-event.entity';
import { WorkOrderEntity } from '../entities/work-order.entity';
import { ReportIncidentDto } from '../dto/incident.dto';

const ALARM_TYPE_MAP: Record<string, string> = {
  紧急事件告警: 'emergency',
  消防事件告警: 'fire',
  漏水事件告警: 'water_leak',
  烟感事件告警: 'smoke',
};

@Injectable()
export class IncidentService {
  private readonly logger = new Logger(IncidentService.name);

  constructor(
    @InjectRepository(AlarmEventEntity)
    private eventRepo: Repository<AlarmEventEntity>,
    @InjectRepository(WorkOrderEntity)
    private workOrderRepo: Repository<WorkOrderEntity>,
  ) {}

  async report(dto: ReportIncidentDto, reporter: string) {
    // 1. 写入告警事件记录
    const event = await this.eventRepo.save(
      this.eventRepo.create({
        type: ALARM_TYPE_MAP[dto.alarmType] ?? 'emergency',
        name: dto.alarmType,
        location: dto.location ?? '',
        level: this.levelFromUrgency(dto.urgency),
        status: 'unresolved',
        triggerTime: new Date(),
      }),
    );

    // 2. 自动创建安防工单
    const orderNo = this.generateOrderNo();
    const workOrder = await this.workOrderRepo.save(
      this.workOrderRepo.create({
        orderNo,
        alarmType: dto.alarmType,
        urgency: dto.urgency,
        status: 'pending_assign',
        location: dto.location ?? '',
        description: dto.description,
        reporter: dto.reporter ?? reporter ?? 'system',
      }),
    );

    this.logger.log(`Incident reported: ${orderNo} - ${dto.alarmType}`);

    // 3. TODO: 通过 MQTT 推送告警消息到前端
    // await this.mqttClient.publish(`/security/alarm`, JSON.stringify({ ... }))

    return { eventId: event.id, workOrderId: workOrder.id, orderNo };
  }

  private levelFromUrgency(urgency: string): string {
    const m: Record<string, string> = {
      紧急: '紧急',
      高: '高',
      中: '中',
      低: '低',
    };
    return m[urgency] ?? '中';
  }

  private generateOrderNo(): string {
    const now = new Date();
    const y = now.getFullYear();
    const seq = String(Math.floor(Math.random() * 9000) + 1000);
    return `WO-${y}-${seq}`;
  }
}
import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { PatrolRouteEntity } from '../entities/patrol-route.entity';
import { PatrolPlanEntity } from '../entities/patrol-plan.entity';
import { PatrolTaskEntity } from '../entities/patrol-task.entity';
import {
  RouteEditDto,
  PlanEditDto,
  TaskCreateDto,
  QueryTaskDto,
  ReportAnomalyDto,
  DeleteDto,
} from '../dto/patrol.dto';
import { WorkOrderEntity } from '../entities/work-order.entity';
import { AlarmEventEntity } from '../entities/alarm-event.entity';

@Injectable()
export class PatrolService {
  private readonly logger = new Logger(PatrolService.name);

  constructor(
    @InjectRepository(PatrolRouteEntity)
    private routeRepo: Repository<PatrolRouteEntity>,
    @InjectRepository(PatrolPlanEntity)
    private planRepo: Repository<PatrolPlanEntity>,
    @InjectRepository(PatrolTaskEntity)
    private taskRepo: Repository<PatrolTaskEntity>,
    @InjectRepository(WorkOrderEntity)
    private workOrderRepo: Repository<WorkOrderEntity>,
    @InjectRepository(AlarmEventEntity)
    private alarmEventRepo: Repository<AlarmEventEntity>,
  ) {}

  // ── 路线 ────────────────────────────────────────────────────────────────────

  async getRouteList() {
    const list = await this.routeRepo.find({ order: { createTime: 'DESC' } });
    return { list, total: list.length };
  }

  async editRoute(dto: RouteEditDto) {
    if (dto.id) {
      await this.routeRepo.update(dto.id, {
        name: dto.name,
        description: dto.description,
        cameraIds: dto.cameraIds,
        status: dto.status ?? 'active',
      });
      return this.routeRepo.findOneBy({ id: dto.id });
    }
    const entity = this.routeRepo.create({
      name: dto.name,
      description: dto.description,
      cameraIds: dto.cameraIds ?? [],
      status: dto.status ?? 'active',
    });
    return this.routeRepo.save(entity);
  }

  async deleteRoute(dto: DeleteDto) {
    await this.routeRepo.delete(dto.id);
    return { success: true };
  }

  // ── 计划 ────────────────────────────────────────────────────────────────────

  async getPlanList() {
    const plans = await this.planRepo.find({ order: { createTime: 'DESC' } });
    const routes = await this.routeRepo.find();
    const routeMap = new Map(routes.map((r) => [r.id, r.name]));
    const list = plans.map((p) => ({
      ...p,
      routeName: routeMap.get(p.routeId) ?? '',
    }));
    return { list, total: list.length };
  }

  async editPlan(dto: PlanEditDto) {
    if (dto.id) {
      await this.planRepo.update(dto.id, {
        name: dto.name,
        routeId: dto.routeId,
        startTime: dto.startTime,
        endTime: dto.endTime,
        intervalMin: dto.intervalMin ?? 120,
        weekDays: dto.weekDays,
        status: dto.status ?? 'active',
      });
      return this.planRepo.findOneBy({ id: dto.id });
    }
    const entity = this.planRepo.create({
      name: dto.name,
      routeId: dto.routeId,
      startTime: dto.startTime,
      endTime: dto.endTime,
      intervalMin: dto.intervalMin ?? 120,
      weekDays: dto.weekDays ?? [],
      status: dto.status ?? 'active',
    });
    return this.planRepo.save(entity);
  }

  async deletePlan(dto: DeleteDto) {
    await this.planRepo.delete(dto.id);
    return { success: true };
  }

  // ── 任务 ────────────────────────────────────────────────────────────────────

  async getTaskList(query: QueryTaskDto) {
    const qb = this.taskRepo
      .createQueryBuilder('t')
      .orderBy('t.create_time', 'DESC');
    if (query.status)
      qb.andWhere('t.status = :status', { status: query.status });
    const tasks = await qb.getMany();

    const plans = await this.planRepo.find();
    const routes = await this.routeRepo.find();
    const planMap = new Map(plans.map((p) => [p.id, p]));
    const routeMap = new Map(routes.map((r) => [r.id, r.name]));

    const list = tasks.map((t) => {
      const plan = t.planId ? planMap.get(t.planId) : undefined;
      return {
        ...t,
        planName: plan?.name ?? '',
        routeName: t.routeId
          ? (routeMap.get(t.routeId) ?? '')
          : plan?.routeId
            ? (routeMap.get(plan.routeId) ?? '')
            : '',
      };
    });
    return { list, total: list.length };
  }

  async createTask(dto: TaskCreateDto) {
    const plan = await this.planRepo.findOneBy({ id: dto.planId });
    const entity = this.taskRepo.create({
      planId: dto.planId,
      routeId: plan?.routeId,
      executor: dto.executor,
      startTime: new Date(),
      status: 'pending',
      progress: 0,
      anomalyCount: 0,
    });
    return this.taskRepo.save(entity);
  }

  async reportAnomaly(dto: ReportAnomalyDto, reporter: string) {
    // 更新任务异常计数
    if (dto.taskId) {
      await this.taskRepo.increment({ id: dto.taskId }, 'anomalyCount', 1);
    }

    // 创建告警事件记录
    const event = this.alarmEventRepo.create({
      type: this.mapAlarmType(dto.alarmType),
      name: dto.alarmType,
      location: '',
      level: dto.urgency === '紧急' || dto.urgency === '高' ? '高' : '中',
      status: 'unresolved',
      triggerTime: new Date(),
    });
    await this.alarmEventRepo.save(event);

    // 自动创建安防工单
    const orderNo = this.generateOrderNo();
    const workOrder = this.workOrderRepo.create({
      orderNo,
      alarmType: dto.alarmType,
      urgency: dto.urgency,
      status: 'pending_assign',
      description: dto.description,
      reporter,
    });
    return this.workOrderRepo.save(workOrder);
  }

  private mapAlarmType(t: string): string {
    const m: Record<string, string> = {
      紧急事件告警: 'emergency',
      消防事件告警: 'fire',
      漏水事件告警: 'water_leak',
      烟感事件告警: 'smoke',
    };
    return m[t] ?? 'emergency';
  }

  private generateOrderNo(): string {
    const now = new Date();
    const y = now.getFullYear();
    const seq = String(Math.floor(Math.random() * 9000) + 1000);
    return `WO-${y}-${seq}`;
  }
}
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { SchedulePersonEntity } from '../entities/schedule-person.entity';
import { ScheduleSpecialEntity } from '../entities/schedule-special.entity';
import { ScheduleWeekEntity } from '../entities/schedule-week.entity';
import {
  PersonEditDto,
  SpecialDateEditDto,
  WeekEditDto,
  DeleteDto,
} from '../dto/schedule.dto';

@Injectable()
export class ScheduleService {
  constructor(
    @InjectRepository(SchedulePersonEntity)
    private personRepo: Repository<SchedulePersonEntity>,
    @InjectRepository(ScheduleSpecialEntity)
    private specialRepo: Repository<ScheduleSpecialEntity>,
    @InjectRepository(ScheduleWeekEntity)
    private weekRepo: Repository<ScheduleWeekEntity>,
  ) {}

  // ── 人员 ─────────────────────────────────────────────────────────────────────

  async getPersonList() {
    const list = await this.personRepo.find({ order: { createTime: 'DESC' } });
    return { list, total: list.length };
  }

  async editPerson(dto: PersonEditDto) {
    if (dto.id) {
      await this.personRepo.update(dto.id, {
        name: dto.name,
        phone: dto.phone,
        email: dto.email,
        role: dto.role,
        alarmRule: dto.alarmRule,
        status: dto.status ?? 'active',
      });
      return this.personRepo.findOneBy({ id: dto.id });
    }
    return this.personRepo.save(
      this.personRepo.create({
        name: dto.name,
        phone: dto.phone,
        email: dto.email,
        role: dto.role,
        alarmRule: dto.alarmRule,
        status: dto.status ?? 'active',
      }),
    );
  }

  async deletePerson(dto: DeleteDto) {
    await this.personRepo.delete(dto.id);
    return { success: true };
  }

  // ── 特定日期排班 ──────────────────────────────────────────────────────────────

  async getSpecialDateList() {
    const specials = await this.specialRepo.find({
      order: { createTime: 'DESC' },
    });
    const persons = await this.personRepo.find();
    const pMap = new Map(persons.map((p) => [p.id, p.name]));
    const list = specials.map((s) => ({
      ...s,
      dateRange: [s.dateStart, s.dateEnd] as [string, string],
      personNames: (s.personIds ?? [])
        .map((id) => pMap.get(id) ?? id)
        .join('、'),
    }));
    return { list, total: list.length };
  }

  async editSpecialDate(dto: SpecialDateEditDto) {
    const data = {
      name: dto.name,
      dateStart: dto.dateRange?.[0],
      dateEnd: dto.dateRange?.[1],
      personIds: dto.personIds ?? [],
      deviceGroup: dto.deviceGroup,
      note: dto.note,
    };
    if (dto.id) {
      await this.specialRepo.update(dto.id, data);
      return this.specialRepo.findOneBy({ id: dto.id });
    }
    return this.specialRepo.save(this.specialRepo.create(data));
  }

  async deleteSpecialDate(dto: DeleteDto) {
    await this.specialRepo.delete(dto.id);
    return { success: true };
  }

  // ── 周排班 ───────────────────────────────────────────────────────────────────

  async getWeekList() {
    const weeks = await this.weekRepo.find({ order: { createTime: 'DESC' } });
    const persons = await this.personRepo.find();
    const pMap = new Map(persons.map((p) => [p.id, p.name]));
    const list = weeks.map((w) => ({
      ...w,
      personNames: (w.personIds ?? [])
        .map((id) => pMap.get(id) ?? id)
        .join('、'),
    }));
    return { list, total: list.length };
  }

  async editWeek(dto: WeekEditDto) {
    const data = {
      name: dto.name,
      personIds: dto.personIds ?? [],
      deviceGroup: dto.deviceGroup,
      weekDays: dto.weekDays ?? [],
      startTime: dto.startTime,
      endTime: dto.endTime,
    };
    if (dto.id) {
      await this.weekRepo.update(dto.id, data);
      return this.weekRepo.findOneBy({ id: dto.id });
    }
    return this.weekRepo.save(this.weekRepo.create(data));
  }

  async deleteWeek(dto: DeleteDto) {
    await this.weekRepo.delete(dto.id);
    return { success: true };
  }
}
/* eslint-disable @typescript-eslint/no-unused-vars */
import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { StreamDeviceEntity } from '../entities/stream-device.entity';
import { TranscodeTemplateEntity } from '../entities/transcode-template.entity';
import {
  ControlServiceDto,
  StreamDeviceEditDto,
  QueryStreamDeviceDto,
  TranscodeEditDto,
  FlowDeleteDto,
  QueryFlowDto,
  QueryGb28181Dto,
  Gb28181StopDto,
  DeleteDto,
} from '../dto/stream.dto';

@Injectable()
export class StreamService {
  private readonly logger = new Logger(StreamService.name);

  private get zlmBase() {
    const host = process.env.ZLM_HOST || '127.0.0.1';
    const port = process.env.ZLM_PORT || '8080';
    return `http://${host}:${port}`;
  }

  private get zlmSecret() {
    return process.env.ZLM_SECRET || 'buildingos';
  }

  constructor(
    @InjectRepository(StreamDeviceEntity)
    private deviceRepo: Repository<StreamDeviceEntity>,
    @InjectRepository(TranscodeTemplateEntity)
    private transcodeRepo: Repository<TranscodeTemplateEntity>,
    private readonly http: HttpService,
  ) {}

  // ── 平台状态 ─────────────────────────────────────────────────────────────────

  async getPlatformStatus() {
    const status = { zlm: false, sip: false, proxy: false, record: false };
    try {
      const resp = await firstValueFrom(
        this.http.get(`${this.zlmBase}/index/api/getStatistic`, {
          params: { secret: this.zlmSecret },
          timeout: 3000,
        }),
      );
      if (resp.data?.code === 0) {
        status.zlm = true;
        status.sip = true;
        status.proxy = true;
      }
    } catch {
      this.logger.warn('ZLM unreachable, returning offline status');
    }
    return status;
  }

  controlService(dto: ControlServiceDto) {
    // 生产环境通过 systemd 或 docker exec 控制服务，这里返回模拟结果
    this.logger.log(`Control service: ${dto.service} -> ${dto.action}`);
    return { success: true, service: dto.service, action: dto.action };
  }

  getZlmConfig() {
    const host = process.env.ZLM_HOST || '127.0.0.1';
    const httpPort = parseInt(process.env.ZLM_PORT || '8080');
    return {
      zlm: {
        host,
        httpPort,
        rtmpPort: 1935,
        rtspPort: 554,
        wsPort: httpPort,
        secret: this.zlmSecret,
      },
      sip: {
        serverId: '34020000002000000001',
        domain: '3402000000',
        host,
        port: 5060,
        deviceCount: 0,
        onlineCount: 0,
      },
    };
  }

  // ── 流媒体设备 ───────────────────────────────────────────────────────────────

  async getDeviceList(query: QueryStreamDeviceDto) {
    const qb = this.deviceRepo.createQueryBuilder('d');
    if (query.deviceType)
      qb.andWhere('d.device_type = :dt', { dt: query.deviceType });
    if (query.status)
      qb.andWhere('d.status = :status', { status: query.status });
    const list = await qb.orderBy('d.create_time', 'DESC').getMany();
    // 不返回密码字段

    return {
      list: list.map(({ passwordEnc: _pw, ...rest }) => rest),
      total: list.length,
    };
  }

  async editDevice(dto: StreamDeviceEditDto) {
    const passwordEnc = dto.password
      ? Buffer.from(dto.password).toString('base64')
      : undefined;
    const data: Partial<StreamDeviceEntity> = {
      name: dto.name,
      deviceType: dto.deviceType,
      brand: dto.brand,
      ip: dto.ip,
      port: dto.port ?? 554,
      username: dto.username,
      channelCount: dto.channelCount ?? 1,
    };
    if (passwordEnc) data.passwordEnc = passwordEnc;
    if (dto.id) {
      await this.deviceRepo.update(dto.id, data);
      const entity = await this.deviceRepo.findOneBy({ id: dto.id });

      const { passwordEnc: _pw1, ...result } = entity!;
      return result;
    }
    const entity = await this.deviceRepo.save(this.deviceRepo.create(data));

    const { passwordEnc: _pw2, ...result } = entity;
    return result;
  }

  async deleteDevice(dto: DeleteDto) {
    await this.deviceRepo.delete(dto.id);
    return { success: true };
  }

  // ── 转码模板 ─────────────────────────────────────────────────────────────────

  async getTranscodeList() {
    const list = await this.transcodeRepo.find({
      order: { createTime: 'DESC' },
    });
    return { list, total: list.length };
  }

  async editTranscode(dto: TranscodeEditDto) {
    const data = {
      name: dto.name,
      resolution: dto.resolution,
      videoBitrate: dto.videoBitrate,
      fps: dto.fps,
      audioBitrate: dto.audioBitrate,
      codec: dto.codec ?? 'h264',
      enabled: dto.enabled ?? true,
    };
    if (dto.id) {
      await this.transcodeRepo.update(dto.id, data);
      return this.transcodeRepo.findOneBy({ id: dto.id });
    }
    return this.transcodeRepo.save(this.transcodeRepo.create(data));
  }

  async deleteTranscode(dto: DeleteDto) {
    await this.transcodeRepo.delete(dto.id);
    return { success: true };
  }

  // ── 流追踪 ───────────────────────────────────────────────────────────────────

  async getFlowList(query: QueryFlowDto) {
    try {
      const resp = await firstValueFrom(
        this.http.get(`${this.zlmBase}/index/api/getMediaList`, {
          params: { secret: this.zlmSecret },
          timeout: 3000,
        }),
      );
      if (resp.data?.code === 0) {
        let list: any[] = (resp.data.data || []).map((m: any) => ({
          app: m.app,
          stream: m.stream,
          originType: m.originType ?? 'unknown',
          readerCount: m.readerCount ?? 0,
          bytesSpeed: Math.round((m.bytesSpeed ?? 0) / 1024),
          durationSec: m.totalDuration ?? 0,
          createTime: m.createTime ?? '',
        }));
        if (query.keyword) {
          list = list.filter((f: any) =>
            String(f.stream).includes(query.keyword!),
          );
        }
        return { list, total: list.length };
      }
    } catch {
      this.logger.warn('ZLM getMediaList failed');
    }
    return { list: [], total: 0 };
  }

  async deleteFlow(dto: FlowDeleteDto) {
    try {
      await firstValueFrom(
        this.http.post(`${this.zlmBase}/index/api/close_streams`, null, {
          params: { secret: this.zlmSecret, app: dto.app, stream: dto.stream },
          timeout: 3000,
        }),
      );
    } catch {
      this.logger.warn(`Close stream failed: ${dto.app}/${dto.stream}`);
    }
    return { success: true };
  }

  // ── GB28181 ──────────────────────────────────────────────────────────────────

  async getGb28181List(query: QueryGb28181Dto) {
    try {
      const resp = await firstValueFrom(
        this.http.get(`${this.zlmBase}/index/api/getDeviceList`, {
          params: { secret: this.zlmSecret },
          timeout: 3000,
        }),
      );
      if (resp.data?.code === 0) {
        let list: any[] = (resp.data.data?.deviceList || []).map((d: any) => ({
          id: d.deviceId,
          deviceId: d.deviceId,
          name: d.name ?? d.deviceId,
          ip: d.ip ?? '',
          port: d.port ?? 5060,
          manufacturer: d.manufacturer ?? '',
          status: d.online ? 'online' : 'offline',
          registerTime: d.registerTime ?? '',
        }));
        if (query.status)
          list = list.filter((d: any) => d.status === query.status);
        return { list, total: list.length };
      }
    } catch {
      this.logger.warn('ZLM getDeviceList failed');
    }
    return { list: [], total: 0 };
  }

  stopGb28181(dto: Gb28181StopDto) {
    this.logger.log(`Stop GB28181 device: ${dto.deviceId}`);
    return { success: true };
  }

  // ── 资源监控 ─────────────────────────────────────────────────────────────────

  async getResourceMonitor() {
    let zlmStats: Record<string, any> | null = null;
    try {
      const resp = await firstValueFrom(
        this.http.get(`${this.zlmBase}/index/api/getStatistic`, {
          params: { secret: this.zlmSecret },
          timeout: 3000,
        }),
      );
      if (resp.data?.code === 0)
        zlmStats = resp.data.data as Record<string, any>;
    } catch {
      // ZLM 不可达时返回默认值
    }
    return {
      cpuUsage: zlmStats?.['cpuUsage'] ?? 0,
      memUsage: zlmStats?.['memUsage'] ?? 0,
      diskUsage: 0,
      networkUpload: 0,
      networkDownload: 0,
      networkUtil: 0,
      activeStreams: zlmStats?.['mediaServerCount'] ?? 0,
      totalConnections: zlmStats?.['totalConnections'] ?? 0,
      zlmVersion: zlmStats?.['version'] ?? 'unknown',
      uptime: zlmStats?.['uptime'] ?? '—',
    };
  }
}
import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { WorkOrderEntity } from '../entities/work-order.entity';
import {
  QueryWorkOrderDto,
  WorkOrderEditDto,
  AssignDto,
  DeleteDto,
} from '../dto/workorder.dto';

@Injectable()
export class WorkOrderService {
  private readonly logger = new Logger(WorkOrderService.name);

  constructor(
    @InjectRepository(WorkOrderEntity)
    private repo: Repository<WorkOrderEntity>,
  ) {}

  async getList(query: QueryWorkOrderDto) {
    const pageNo = Number(query.pageNo) || 1;
    const pageSize = Number(query.pageSize) || 20;
    const qb = this.repo.createQueryBuilder('w');

    if (query.status)
      qb.andWhere('w.status = :status', { status: query.status });
    if (query.alarmType)
      qb.andWhere('w.alarm_type = :alarmType', { alarmType: query.alarmType });
    if (query.keyword) {
      qb.andWhere('(w.order_no LIKE :kw OR w.description LIKE :kw)', {
        kw: `%${query.keyword}%`,
      });
    }

    const [list, total] = await qb
      .orderBy('w.create_time', 'DESC')
      .skip((pageNo - 1) * pageSize)
      .take(pageSize)
      .getManyAndCount();

    return { list, total };
  }

  async doEdit(dto: WorkOrderEditDto, reporter?: string) {
    if (dto.id) {
      const updates: Partial<WorkOrderEntity> = {
        alarmType: dto.alarmType,
        urgency: dto.urgency,
        location: dto.location,
        description: dto.description,
        handleNote: dto.handleNote,
      };
      if (dto.status) updates.status = dto.status;
      if (dto.status === 'completed') updates.resolveTime = new Date();
      await this.repo.update(dto.id, updates);
      return this.repo.findOneBy({ id: dto.id });
    }

    const orderNo = this.generateOrderNo();
    const entity = this.repo.create({
      orderNo,
      alarmType: dto.alarmType,
      urgency: dto.urgency ?? '中',
      status: dto.status ?? 'pending_assign',
      location: dto.location,
      description: dto.description,
      reporter: dto.reporter ?? reporter ?? 'system',
    });
    return this.repo.save(entity);
  }

  async doDelete(dto: DeleteDto) {
    await this.repo.delete(dto.id);
    return { success: true };
  }

  async assign(dto: AssignDto) {
    await this.repo.update(dto.id, {
      assignee: dto.assignee,
      status: 'pending_accept',
    });
    return this.repo.findOneBy({ id: dto.id });
  }

  private generateOrderNo(): string {
    const now = new Date();
    const y = now.getFullYear();
    const seq = String(Math.floor(Math.random() * 9000) + 1000);
    return `WO-${y}-${seq}`;
  }
}
export function extractUser(req: any): string {
  try {
    const auth: string =
      (req?.headers?.authorization as string | undefined) || '';
    const token = auth.replace(/^Bearer\s+/i, '');
    const payload = JSON.parse(
      Buffer.from(token.split('.')[1], 'base64url').toString(),
    ) as Record<string, unknown>;
    return (payload.username as string) || (payload.sub as string) || 'unknown';
  } catch {
    return 'unknown';
  }
}

{
  "name": "security",
  "version": "0.0.1",
  "private": true,
  "main": "dist/main.js",
  "scripts": {
    "build": "tsc -p tsconfig.json",
    "start": "node dist/main.js",
    "start:prod": "node dist/main.js",
    "start:dev": "ts-node -r tsconfig-paths/register src/main.ts",
    "version:patch": "npm version patch --no-git-tag-version",
    "pack": "npm pack",
    "pack:patch": "npm run version:patch && npm run build && npm pack",
    "publish:patch": "npm run version:patch && npm run build && npm publish --access public"
  },
  "dependencies": {
    "@nestjs/common": "^11.1.1",
    "@nestjs/core": "^11.1.1",
    "@nestjs/platform-express": "^11.1.1",
    "@nestjs/microservices": "^11.0.0",
    "@nestjs/axios": "^3.0.0",
    "@nestjs/config": "^3.1.1",
    "@nestjs/swagger": "^7.1.19",
    "@nestjs/typeorm": "^11.0.0",
    "axios": "^1.6.0",
    "mqtt": "^4.3.7",
    "typeorm": "^0.3.20",
    "rxjs": "^7.8.1",
    "reflect-metadata": "^0.2.2"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "ts-node": "^10.9.2",
    "tsconfig-paths": "^4.2.0",
    "typescript": "^5.7.3"
  },
  "buildingos": {
    "service": "security",
    "type": "microservice",
    "title": "安防管控",
    "defaultPort": 3015,
    "entry": {
      "module": "src/app.module.ts",
      "http": "src/main.ts"
    },
    "menu": "apps/security/menu.json",
    "health": "/security/health"
  }
}

[
  {
    "path": "/security",
    "name": "Security",
    "component": "Layout",
    "meta": {
      "title": "安防管控",
      "icon": "shield-line",
      "noColumn": false
    },
    "children": [
      {
        "path": "map",
        "name": "SecurityMap",
        "component": "/@/views/sence/security/map/index.vue",
        "meta": { "title": "安防指挥中心", "icon": "map-pin-line" }
      },
      {
        "path": "external-alarm",
        "name": "ExternalAlarm",
        "component": "/@/views/operate/firefighting/index.vue",
        "meta": { "title": "告警处置", "icon": "alarm-warning-line" }
      },
      {
        "path": "external-search",
        "name": "ExternalSearch",
        "component": "/@/views/operate/firefighting/searchbypic.vue",
        "meta": { "title": "以图搜图", "icon": "image-search-line" }
      },
      {
        "path": "external-blacklist",
        "name": "ExternalBlacklist",
        "component": "/@/views/operate/firefighting/blacklist.vue",
        "meta": { "title": "黑名单", "icon": "user-forbid-line" }
      },
      {
        "path": "video",
        "name": "SecurityVideo",
        "meta": { "title": "视频管理", "icon": "vidicon-line", "noColumn": false },
        "children": [
          {
            "path": "monitor",
            "name": "SecurityMonitor",
            "component": "/@/views/sence/security/video/monitor/index.vue",
            "meta": { "title": "视频监控管理" }
          },
          {
            "path": "patrol",
            "name": "SecurityPatrol",
            "component": "/@/views/sence/security/video/patrol/index.vue",
            "meta": { "title": "视频巡更" }
          }
        ]
      },
      {
        "path": "fire",
        "name": "SecurityFire",
        "component": "/@/views/sence/security/fire/index.vue",
        "meta": { "title": "安消联动", "icon": "fire-line" }
      },
      {
        "path": "alarm",
        "name": "SecurityAlarm",
        "meta": { "title": "安防告警", "icon": "alarm-warning-line", "noColumn": false },
        "children": [
          {
            "path": "workorder",
            "name": "SecurityAlarmWorkOrder",
            "component": "/@/views/sence/security/alarm/workorder/index.vue",
            "meta": { "title": "告警工单" }
          },
          {
            "path": "type",
            "name": "SecurityAlarmType",
            "component": "/@/views/sence/security/alarm/type/index.vue",
            "meta": { "title": "告警类型" }
          },
          {
            "path": "schedule",
            "name": "SecurityAlarmSchedule",
            "component": "/@/views/sence/security/alarm/schedule/index.vue",
            "meta": { "title": "告警排班" }
          },
          {
            "path": "sound",
            "name": "SecurityAlarmSound",
            "component": "/@/views/sence/security/alarm/sound/index.vue",
            "meta": { "title": "声音策略" }
          },
          {
            "path": "whitelist",
            "name": "SecurityAlarmWhitelist",
            "component": "/@/views/sence/security/alarm/whitelist/index.vue",
            "meta": { "title": "白名单管理" }
          },
          {
            "path": "escalation",
            "name": "SecurityAlarmEscalation",
            "component": "/@/views/sence/security/alarm/escalation/index.vue",
            "meta": { "title": "升级规则" }
          },
          {
            "path": "aggregation",
            "name": "SecurityAlarmAggregation",
            "component": "/@/views/sence/security/alarm/aggregation/index.vue",
            "meta": { "title": "告警聚合" }
          }
        ]
      },
      {
        "path": "zone",
        "name": "SecurityZone",
        "component": "/@/views/sence/security/zone/index.vue",
        "meta": { "title": "安防分区", "icon": "map-pin-user-line" }
      },
      {
        "path": "rule",
        "name": "SecurityRule",
        "component": "/@/views/sence/security/rule/index.vue",
        "meta": { "title": "事件规则", "icon": "settings-3-line" }
      },
      {
        "path": "stream",
        "name": "SecurityStream",
        "meta": { "title": "视频流服务", "icon": "broadcast-line", "noColumn": false },
        "children": [
          {
            "path": "platform",
            "name": "SecurityStreamPlatform",
            "component": "/@/views/sence/security/stream/platform/index.vue",
            "meta": { "title": "流媒体平台管理" }
          },
          {
            "path": "live",
            "name": "SecurityStreamLive",
            "component": "/@/views/sence/security/stream/live/index.vue",
            "meta": { "title": "Web端实时视频" }
          }
        ]
      }
    ]
  }
]

```

## 后30页

```
<template>
  <div class="security-alarm-aggregation table-auto-height">
    <!-- ─── Stat cards ─── -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <div class="stat-card stat-total">
          <div class="stat-label">今日告警总数</div>
          <div class="stat-value">{{ statTotal }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-pending">
          <div class="stat-label">未处理</div>
          <div class="stat-value">{{ statPending }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-processing">
          <div class="stat-label">处理中</div>
          <div class="stat-value">{{ statProcessing }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-done">
          <div class="stat-label">已处理</div>
          <div class="stat-value">{{ statDone }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- ─── Source filter tabs ─── -->
    <el-radio-group v-model="sourceFilter" style="margin-bottom: 16px" @change="onSourceChange">
      <el-radio-button value="">全部</el-radio-button>
      <el-radio-button value="video">视频监控</el-radio-button>
      <el-radio-button value="perimeter">周界防范</el-radio-button>
      <el-radio-button value="access">门禁系统</el-radio-button>
      <el-radio-button value="fire">消防报警</el-radio-button>
      <el-radio-button value="other">其他</el-radio-button>
    </el-radio-group>

    <!-- ─── Query area ─── -->
    <vab-query-form>
      <vab-query-form-left-panel />
      <vab-query-form-right-panel>
        <el-form inline :model="queryForm" @submit.prevent>
          <el-form-item label="日期">
            <el-date-picker
              v-model="queryForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始"
              end-placeholder="结束"
              value-format="YYYY-MM-DD"
              style="width: 240px"
            />
          </el-form-item>
          <el-form-item label="关键字">
            <el-input v-model="queryForm.keyword" clearable placeholder="告警类型/位置" style="width: 150px" @keyup.enter="fetchData" />
          </el-form-item>
          <el-form-item label="级别">
            <el-select v-model="queryForm.level" clearable placeholder="全部" style="width: 100px">
              <el-option label="低" value="低" />
              <el-option label="中" value="中" />
              <el-option label="高" value="高" />
              <el-option label="紧急" value="紧急" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="Search" @click="fetchData">查询</el-button>
          </el-form-item>
        </el-form>
      </vab-query-form-right-panel>
    </vab-query-form>

    <!-- ─── Alarm table ─── -->
    <el-table v-loading="listLoading" border :data="list" @expand-change="onExpandChange">
      <el-table-column type="expand" width="40">
        <template #default="{ row }">
          <div class="expand-detail">
            <el-descriptions :column="2" border size="small" title="原始告警数据">
              <el-descriptions-item label="告警ID">{{ row.id }}</el-descriptions-item>
              <el-descriptions-item label="来源系统">{{ sourceLabel(row.source) }}</el-descriptions-item>
              <el-descriptions-item label="告警类型">{{ row.alarmType }}</el-descriptions-item>
              <el-descriptions-item label="告警级别">{{ row.level }}</el-descriptions-item>
              <el-descriptions-item label="发生位置">{{ row.location }}</el-descriptions-item>
              <el-descriptions-item label="原始设备">{{ row.deviceName }}</el-descriptions-item>
              <el-descriptions-item label="告警时间">{{ row.time }}</el-descriptions-item>
              <el-descriptions-item label="当前状态">{{ statusLabel(row.status) }}</el-descriptions-item>
              <el-descriptions-item v-if="row.aggregationInfo" label="聚合信息" :span="2">
                {{ row.aggregationInfo }}
              </el-descriptions-item>
              <el-descriptions-item label="原始报文" :span="2">
                <el-input :model-value="row.rawPayload || '—'" type="textarea" :rows="2" readonly style="width: 100%" />
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </template>
      </el-table-column>
      <el-table-column align="center" label="序号" type="index" width="60" />
      <el-table-column label="告警时间" prop="time" width="160" />
      <el-table-column label="来源系统" width="110">
        <template #default="{ row }">
          <el-tag :type="sourceTagType(row.source)" size="small" effect="plain">
            {{ sourceLabel(row.source) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="告警类型" prop="alarmType" min-width="120" />
      <el-table-column label="告警级别" width="80">
        <template #default="{ row }">
          <el-tag :type="levelTagType(row.level)" size="small">
            {{ row.level }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="发生位置" prop="location" min-width="140" show-overflow-tooltip />
      <el-table-column label="原始设备" prop="deviceName" min-width="150" show-overflow-tooltip />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="聚合信息" min-width="140">
        <template #default="{ row }">
          <span v-if="row.aggregationInfo">
            <el-tag type="warning" size="small" effect="plain">
              {{ row.aggregationInfo }}
            </el-tag>
          </span>
          <span v-else>—</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDetail(row)">查看详情</el-button>
          <el-button v-if="row.status === '未处理'" link type="success" @click="handleProcess(row)">处理</el-button>
        </template>
      </el-table-column>
      <template #empty>
        <el-empty class="vab-data-empty" description="暂无告警数据" />
      </template>
    </el-table>

    <el-pagination
      background
      :current-page="queryForm.pageNo"
      layout="total, sizes, prev, pager, next, jumper"
      :page-size="queryForm.pageSize"
      :total="total"
      @current-change="
        (v) => {
          queryForm.pageNo = v
          fetchData()
        }
      "
      @size-change="
        (v) => {
          queryForm.pageSize = v
          queryForm.pageNo = 1
          fetchData()
        }
      "
    />

    <!-- ─── Detail dialog ─── -->
    <el-dialog v-model="detailVisible" title="告警详情" width="700px" destroy-on-close>
      <el-descriptions v-if="detailRow" :column="2" border>
        <el-descriptions-item label="告警ID">{{ detailRow.id }}</el-descriptions-item>
        <el-descriptions-item label="来源系统">{{ sourceLabel(detailRow.source) }}</el-descriptions-item>
        <el-descriptions-item label="告警类型">{{ detailRow.alarmType }}</el-descriptions-item>
        <el-descriptions-item label="告警级别">
          <el-tag :type="levelTagType(detailRow.level)" size="small">{{ detailRow.level }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发生位置" :span="2">{{ detailRow.location }}</el-descriptions-item>
        <el-descriptions-item label="原始设备" :span="2">{{ detailRow.deviceName }}</el-descriptions-item>
        <el-descriptions-item label="告警时间">{{ detailRow.time }}</el-descriptions-item>
        <el-descriptions-item label="当前状态">
          <el-tag :type="statusTagType(detailRow.status)" size="small">{{ statusLabel(detailRow.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item v-if="detailRow.aggregationInfo" label="聚合信息" :span="2">
          {{ detailRow.aggregationInfo }}
        </el-descriptions-item>
        <el-descriptions-item label="原始报文" :span="2">
          <pre class="raw-payload">{{ detailRow.rawPayload || '无原始报文' }}</pre>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button v-if="detailRow?.status === '未处理'" type="success" @click="handleProcess(detailRow)">处理告警</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { Search } from '@element-plus/icons-vue'

defineOptions({ name: 'SecurityAlarmAggregation' })

const $baseMessage = inject<any>('$baseMessage')

const mock = (data: any) => new Promise<any>((r) => setTimeout(() => r({ code: '200', msg: 'success', data }), 300))

// ---- Helpers ----

const sourceLabel = (s: string): string => {
  const map: Record<string, string> = {
    video: '视频监控',
    perimeter: '周界防范',
    access: '门禁系统',
    fire: '消防报警',
    other: '其他',
  }
  return map[s] || s
}

const sourceTagType = (s: string): string => {
  const map: Record<string, string> = {
    video: 'primary',
    perimeter: 'warning',
    access: 'success',
    fire: 'danger',
    other: 'info',
  }
  return map[s] || 'info'
}

const levelTagType = (level: string): string => {
  const map: Record<string, string> = {
    低: 'info',
    中: '',
    高: 'warning',
    紧急: 'danger',
  }
  return map[level] || 'info'
}

const statusLabel = (s: string): string => s
const statusTagType = (s: string): string => {
  const map: Record<string, string> = {
    未处理: 'danger',
    处理中: 'warning',
    已处理: 'success',
  }
  return map[s] || 'info'
}

// ---- Stat cards ----

interface AggStat {
  total: number
  pending: number
  processing: number
  done: number
}

const stats = ref<AggStat>({ total: 0, pending: 0, processing: 0, done: 0 })
const statTotal = computed(() => stats.value.total)
const statPending = computed(() => stats.value.pending)
const statProcessing = computed(() => stats.value.processing)
const statDone = computed(() => stats.value.done)

// ---- Query ----

const sourceFilter = ref('')
const queryForm = reactive({
  dateRange: [] as string[],
  keyword: '',
  level: '',
  pageNo: 1,
  pageSize: 20,
})
const listLoading = ref(false)
const list = ref<any[]>([])
const total = ref(0)

const onSourceChange = () => {
  queryForm.pageNo = 1
  fetchData()
}

// ---- Mock alarm records ----

const buildMockAlarms = (): any[] => {
  const now = new Date()
  const t = (offset: number) => {
    const d = new Date(now.getTime() + offset * 60 * 1000)
    return d.toLocaleString('zh-CN', { hour12: false })
  }

  const payloads = [
    '{"event":"motion_detect","camera":"CAM-001","confidence":0.95}',
    '{"event":"intrusion","zone":"perimeter-east","sensor":"IR-002","threshold":85}',
    '{"event":"door_forced","door":"ACC-DOOR-03","reader":"RDR-03","card":"unknown"}',
    '{"event":"fire_alarm","detector":"SMOKE-005","temperature":67,"smoke_level":890}',
    '{"event":"loop_detect","loop":"LP-01","vehicle":" SUV","direction":"inbound"}',
  ]

  return [
    {
      id: 'ALM-001',
      time: t(-10),
      source: 'video',
      alarmType: '区域入侵',
      level: '高',
      location: '1号楼-东侧外围',
      deviceName: '枪式摄像机-CAM-011',
      status: '未处理',
      aggregationInfo: '',
      rawPayload: payloads[0],
    },
    {
      id: 'ALM-002',
      time: t(-25),
      source: 'video',
      alarmType: '物体滞留',
      level: '中',
      location: '1号楼-Lobby',
      deviceName: '球型摄像机-CAM-008',
      status: '未处理',
      aggregationInfo: '',
      rawPayload: payloads[0],
    },
    {
      id: 'ALM-003',
      time: t(-8),
      source: 'perimeter',
      alarmType: '红外入侵',
      level: '紧急',
      location: '2号楼-周界东段',
      deviceName: '红外探测器-IR-002',
      status: '处理中',
      aggregationInfo: '合并3条相似告警',
      rawPayload: payloads[1],
    },
    {
      id: 'ALM-004',
      time: t(-40),
      source: 'perimeter',
      alarmType: '围栏震动',
      level: '中',
      location: '3号楼-周界北段',
      deviceName: '震动光纤-VF-001',
      status: '未处理',
      aggregationInfo: '',
      rawPayload: payloads[1],
    },
    {
      id: 'ALM-005',
      time: t(-15),
      source: 'perimeter',
      alarmType: '红外入侵',
      level: '高',
      location: '2号楼-周界东段',
      deviceName: '红外探测器-IR-002',
      status: '未处理',
      aggregationInfo: '',
      rawPayload: payloads[1],
    },
    {
      id: 'ALM-006',
      time: t(-60),
      source: 'access',
      alarmType: '非法闯入',
      level: '紧急',
      location: '3号楼-主入口',
      deviceName: '门磁-ACC-DOOR-003',
      status: '未处理',
      aggregationInfo: '合并2条相似告警',
      rawPayload: payloads[2],
    },
    {
      id: 'ALM-007',
      time: t(-90),
      source: 'access',
      alarmType: '门禁超时未关',
      level: '低',
      location: '2号楼-3F-会议室A',
      deviceName: '门禁控制器-ACC-CTRL-005',
      status: '已处理',
      aggregationInfo: '',
      rawPayload: payloads[2],
    },
    {
      id: 'ALM-008',
      time: t(-120),
      source: 'access',
      alarmType: '非法刷卡',
      level: '中',
      location: '1号楼-B1-车库入口',
      deviceName: '读卡器-RDR-001',
      status: '处理中',
      aggregationInfo: '',
      rawPayload: payloads[2],
    },
    {
      id: 'ALM-009',
      time: t(-5),
      source: 'fire',
      alarmType: '烟感告警',
      level: '紧急',
      location: '2号楼-4F-茶水间',
      deviceName: '烟感探测器-SMOKE-005',
      status: '未处理',
      aggregationInfo: '',
      rawPayload: payloads[3],
    },
    {
      id: 'ALM-010',
      time: t(-30),
      source: 'fire',
      alarmType: '烟感告警',
      level: '紧急',
      location: '2号楼-4F-走廊',
      deviceName: '烟感探测器-SMOKE-006',
      status: '未处理',
      aggregationInfo: '合并3条相似告警',
      rawPayload: payloads[3],
    },
    {
      id: 'ALM-011',
      time: t(-180),
      source: 'fire',
      alarmType: '手动报警',
      level: '高',
      location: '1号楼-2F-楼梯间',
      deviceName: '手动报警按钮-MANUAL-002',
      status: '已处理',
      aggregationInfo: '',
      rawPayload: payloads[3],
    },
    {
      id: 'ALM-012',
      time: t(-50),
      source: 'video',
      alarmType: '徘徊检测',
      level: '中',
      location: '1号楼-停车场入口',
      deviceName: '枪式摄像机-CAM-005',
      status: '处理中',
      aggregationInfo: '',
      rawPayload: payloads[0],
    },
    {
      id: 'ALM-013',
      time: t(-240),
      source: 'other',
      alarmType: '电梯困人',
      level: '紧急',
      location: '3号楼-电梯B',
      deviceName: '电梯对讲-ELEV-002',
      status: '已处理',
      aggregationInfo: '',
      rawPayload: payloads[4],
    },
    {
      id: 'ALM-014',
      time: t(-70),
      source: 'other',
      alarmType: '水浸告警',
      level: '高',
      location: '1号楼-B1-水泵房',
      deviceName: '水浸传感器-LEAK-003',
      status: '未处理',
      aggregationInfo: '',
      rawPayload: payloads[4],
    },
    {
      id: 'ALM-015',
      time: t(-300),
      source: 'access',
      alarmType: '门禁离线',
      level: '中',
      location: '3号楼-5F-机房',
      deviceName: '门禁控制器-ACC-CTRL-012',
      status: '已处理',
      aggregationInfo: '',
      rawPayload: payloads[2],
    },
    {
      id: 'ALM-016',
      time: t(-45),
      source: 'perimeter',
      alarmType: '红外入侵',
      level: '高',
      location: '2号楼-周界东段',
      deviceName: '红外探测器-IR-002',
      status: '未处理',
      aggregationInfo: '合并3条相似告警',
      rawPayload: payloads[1],
    },
  ]
}

const fetchData = async () => {
  listLoading.value = true
  const allData = buildMockAlarms()
  let filtered = [...allData]

  // filter by source
  if (sourceFilter.value) {
    filtered = filtered.filter((item) => item.source === sourceFilter.value)
  }

  // filter by keyword
  if (queryForm.keyword) {
    const kw = queryForm.keyword
    filtered = filtered.filter((item) => item.alarmType.includes(kw) || item.location.includes(kw) || item.deviceName.includes(kw))
  }

  // filter by level
  if (queryForm.level) {
    filtered = filtered.filter((item) => item.level === queryForm.level)
  }

  total.value = filtered.length

  // paginate
  const { pageNo, pageSize } = queryForm
  const start = (pageNo - 1) * pageSize
  const paginated = filtered.slice(start, start + pageSize)

  const { data: mockResult } = await mock(paginated)
  list.value = mockResult

  // stat
  stats.value = {
    total: allData.length,
    pending: allData.filter((d) => d.status === '未处理').length,
    processing: allData.filter((d) => d.status === '处理中').length,
    done: allData.filter((d) => d.status === '已处理').length,
  }

  listLoading.value = false
}

// ---- Detail / Expand ----

const detailVisible = ref(false)
const detailRow = ref<any>(null)

const openDetail = (row: any) => {
  detailRow.value = row
  detailVisible.value = true
}

const onExpandChange = (row: any, expandedRows: any[]) => {
  if (expandedRows.length > 0) {
    detailRow.value = row
  }
}

const handleProcess = (row: any) => {
  $baseMessage.success(`已处理告警「${row.id}」`)
  fetchData()
}

onBeforeMount(fetchData)
</script>

<style lang="scss" scoped>
.stat-card {
  padding: 20px 24px;
  border-radius: 8px;
  color: #fff;
  text-align: center;

  .stat-label {
    font-size: 14px;
    opacity: 0.9;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 36px;
    font-weight: 700;
    line-height: 1;
  }

  &.stat-total {
    background: linear-gradient(135deg, #667eea, #764ba2);
  }

  &.stat-pending {
    background: linear-gradient(135deg, #f093fb, #f5576c);
  }

  &.stat-processing {
    background: linear-gradient(135deg, #4facfe, #00f2fe);
  }

  &.stat-done {
    background: linear-gradient(135deg, #43e97b, #38f9d7);
  }
}

.expand-detail {
  padding: 16px 24px;
}

.raw-payload {
  margin: 0;
  background: var(--el-fill-color-lighter);
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 100px;
  overflow-y: auto;
}
</style>
<template>
  <div class="no-background-container table-auto-height">
    <vab-query-form>
      <vab-query-form-left-panel>
        <el-button type="primary" :icon="Plus" @click="openAddEdit({})">新增规则</el-button>
      </vab-query-form-left-panel>
    </vab-query-form>

    <el-table v-loading="listLoading" border :data="list">
      <el-table-column align="center" label="序号" type="index" width="60" />
      <el-table-column label="规则名称" prop="name" min-width="150" />
      <el-table-column label="告警级别" width="110">
        <template #default="{ row }">
          <el-tag :type="levelTypeMap[row.level]">{{ row.level }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="处置时限/分钟" width="130" prop="timeLimit" align="center" />
      <el-table-column label="超时动作" min-width="140" prop="actionOnTimeout" />
      <el-table-column label="升级目标" min-width="160" prop="escalationTarget" show-overflow-tooltip />
      <el-table-column label="通知方式" width="220">
        <template #default="{ row }">
          <el-tag v-for="m in row.notifyMethods" :key="m" :type="notifyTagMap[m]" style="margin-right: 4px; margin-bottom: 2px">
            {{ m }}
          </el-tag>
          <span v-if="!row.notifyMethods || row.notifyMethods.length === 0">—</span>
        </template>
      </el-table-column>
      <el-table-column label="启用" width="80">
        <template #default="{ row }">
          <el-switch v-model="row.enabled" @change="handleToggle(row)" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openAddEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
      <template #empty>
        <el-empty class="vab-data-empty" description="暂无升级规则" />
      </template>
    </el-table>

    <el-pagination
      background
      :current-page="queryForm.pageNo"
      layout="total, sizes, prev, pager, next, jumper"
      :page-size="queryForm.pageSize"
      :total="total"
      @current-change="
        (v) => {
          queryForm.pageNo = v
          fetchData()
        }
      "
      @size-change="
        (v) => {
          queryForm.pageSize = v
          queryForm.pageNo = 1
          fetchData()
        }
      "
    />

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑升级规则' : '新增升级规则'" width="600px" destroy-on-close>
      <el-form ref="formRef" label-width="120px" :model="form" :rules="formRules">
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="告警级别" prop="level">
          <el-select v-model="form.level" placeholder="请选择告警级别" style="width: 100%">
            <el-option label="低" value="低" />
            <el-option label="中" value="中" />
            <el-option label="高" value="高" />
            <el-option label="紧急" value="紧急" />
          </el-select>
        </el-form-item>
        <el-form-item label="处置时限/分钟" prop="timeLimit">
          <el-input-number v-model="form.timeLimit" :min="1" :max="1440" style="width: 100%" />
        </el-form-item>
        <el-form-item label="超时动作" prop="actionOnTimeout">
          <el-select v-model="form.actionOnTimeout" placeholder="请选择超时动作" style="width: 100%">
            <el-option label="升级告警级别" value="升级告警级别" />
            <el-option label="通知上级" value="通知上级" />
            <el-option label="自动分发到组" value="自动分发到组" />
          </el-select>
        </el-form-item>
        <el-form-item label="升级目标" prop="escalationTarget">
          <el-input v-model="form.escalationTarget" placeholder="如：紧急级别 / 张三 / 安防二组" />
        </el-form-item>
        <el-form-item label="通知方式" prop="notifyMethods">
          <el-checkbox-group v-model="form.notifyMethods">
            <el-checkbox value="声音" label="声音" />
            <el-checkbox value="弹窗" label="弹窗" />
            <el-checkbox value="短信" label="短信" />
            <el-checkbox value="飞书" label="飞书" />
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, inject, onBeforeMount } from 'vue'
import { Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'SecurityAlarmEscalation' })

const $baseMessage = inject<any>('$baseMessage')
const $baseConfirm = inject<any>('$baseConfirm')

const mock = (data: any) => new Promise<any>((r) => setTimeout(() => r({ code: '200', msg: 'success', data }), 300))

const levelTypeMap: Record<string, string> = {
  低: 'info',
  中: '',
  高: 'warning',
  紧急: 'danger',
}

const notifyTagMap: Record<string, string> = {
  声音: '',
  弹窗: 'primary',
  短信: 'warning',
  飞书: 'info',
}

const listLoading = ref(false)
const submitLoading = ref(false)
const list = ref<any[]>([])
const total = ref(0)

const queryForm = reactive({
  pageNo: 1,
  pageSize: 20,
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<any>()
const form = reactive<any>({
  id: '',
  name: '',
  level: '',
  timeLimit: 30,
  actionOnTimeout: '',
  escalationTarget: '',
  notifyMethods: [] as string[],
  enabled: true,
})

const formRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  level: [{ required: true, message: '请选择告警级别', trigger: 'change' }],
  timeLimit: [{ required: true, message: '请设置处置时限', trigger: 'blur' }],
  actionOnTimeout: [{ required: true, message: '请选择超时动作', trigger: 'change' }],
}

let nextId = 100

const fetchData = async () => {
  listLoading.value = true
  const { data } = await mock([
    {
      id: '1',
      name: '低级告警超时升级',
      level: '低',
      timeLimit: 60,
      actionOnTimeout: '升级告警级别',
      escalationTarget: '中级',
      notifyMethods: ['声音', '弹窗'],
      enabled: true,
    },
    {
      id: '2',
      name: '中级告警超时通知',
      level: '中',
      timeLimit: 30,
      actionOnTimeout: '通知上级',
      escalationTarget: '值班经理',
      notifyMethods: ['声音', '弹窗', '短信'],
      enabled: true,
    },
    {
      id: '3',
      name: '高级告警自动分发',
      level: '高',
      timeLimit: 15,
      actionOnTimeout: '自动分发到组',
      escalationTarget: '安防一组',
      notifyMethods: ['声音', '弹窗', '短信', '飞书'],
      enabled: true,
    },
    {
      id: '4',
      name: '紧急告警即时升级',
      level: '紧急',
      timeLimit: 5,
      actionOnTimeout: '通知上级',
      escalationTarget: '安全总监',
      notifyMethods: ['声音', '弹窗', '飞书'],
      enabled: true,
    },
  ])
  total.value = data.length
  list.value = data.slice((queryForm.pageNo - 1) * queryForm.pageSize, queryForm.pageNo * queryForm.pageSize)
  listLoading.value = false
}

const openAddEdit = (row: any) => {
  isEdit.value = !!row.id
  if (row.id) {
    Object.assign(form, {
      id: row.id,
      name: row.name,
      level: row.level,
      timeLimit: row.timeLimit,
      actionOnTimeout: row.actionOnTimeout,
      escalationTarget: row.escalationTarget,
      notifyMethods: [...(row.notifyMethods || [])],
      enabled: row.enabled,
    })
  } else {
    Object.assign(form, {
      id: '',
      name: '',
      level: '',
      timeLimit: 30,
      actionOnTimeout: '',
      escalationTarget: '',
      notifyMethods: [],
      enabled: true,
    })
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  await mock({ code: '200' })

  if (isEdit.value) {
    const idx = list.value.findIndex((r) => r.id === form.id)
    if (idx !== -1) {
      list.value[idx] = { ...form, notifyMethods: [...form.notifyMethods] }
    }
  } else {
    form.id = String(++nextId)
    list.value.unshift({ ...form, notifyMethods: [...form.notifyMethods] })
    total.value++
  }
  $baseMessage(isEdit.value ? '修改成功' : '新增成功', 'success', 'hey')
  submitLoading.value = false
  dialogVisible.value = false
}

const handleToggle = (row: any) => {
  const status = row.enabled ? '已启用' : '已停用'
  $baseMessage(`规则「${row.name}」${status}`, 'success', 'hey')
}

const handleDelete = (row: any) => {
  $baseConfirm(`确定删除升级规则「${row.name}」?`, '删除确认')
    .then(async () => {
      await mock({ code: '200' })
      list.value = list.value.filter((r) => r.id !== row.id)
      total.value--
      $baseMessage('删除成功', 'success', 'hey')
    })
    .catch(() => {
      // user cancelled
    })
}

onBeforeMount(() => {
  fetchData()
})
</script>
<template>
  <div class="no-background-container table-auto-height">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- ─── 人员信息 ──────────────────── -->
      <el-tab-pane label="人员信息" name="persons">
        <vab-query-form>
          <vab-query-form-right-panel>
            <el-button :icon="Plus" type="primary" @click="openPersonEdit({})">新增人员</el-button>
          </vab-query-form-right-panel>
        </vab-query-form>
        <el-table v-loading="personLoading" border :data="persons">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="姓名" prop="name" width="100" />
          <el-table-column label="联系方式" prop="phone" width="130" />
          <el-table-column label="邮箱" prop="email" min-width="160" />
          <el-table-column label="角色" prop="role" width="100" />
          <el-table-column label="告警规则" prop="alarmRule" min-width="160" />
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status === 'active' ? '在职' : '离职' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openPersonEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="deletePerson(row)">删除</el-button>
            </template>
          </el-table-column>
          <template #empty><el-empty description="暂无人员" /></template>
        </el-table>
      </el-tab-pane>

      <!-- ─── 特定日期排表 ──────────────── -->
      <el-tab-pane label="特定日期排表" name="special">
        <vab-query-form>
          <vab-query-form-right-panel>
            <el-button :icon="Plus" type="primary" @click="openSpecialEdit({})">新增排班</el-button>
          </vab-query-form-right-panel>
        </vab-query-form>
        <el-table v-loading="specialLoading" border :data="specialSchedules">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="排班名称" prop="name" min-width="140" />
          <el-table-column label="日期范围" min-width="200">
            <template #default="{ row }">{{ row.dateRange?.[0] }} ~ {{ row.dateRange?.[1] }}</template>
          </el-table-column>
          <el-table-column label="负责人" prop="personNames" min-width="140" />
          <el-table-column label="设备分组" prop="deviceGroup" min-width="120" />
          <el-table-column label="备注" prop="note" min-width="160" show-overflow-tooltip />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openSpecialEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="deleteSpecial(row)">删除</el-button>
            </template>
          </el-table-column>
          <template #empty><el-empty description="暂无特定日期排班" /></template>
        </el-table>
      </el-tab-pane>

      <!-- ─── 周排表 ──────────────────── -->
      <el-tab-pane label="周排表" name="week">
        <vab-query-form>
          <vab-query-form-right-panel>
            <el-button :icon="Plus" type="primary" @click="openWeekEdit({})">新增周排班</el-button>
          </vab-query-form-right-panel>
        </vab-query-form>
        <el-table v-loading="weekLoading" border :data="weekSchedules">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="排班名称" prop="name" min-width="130" />
          <el-table-column label="人员" prop="personNames" min-width="140" />
          <el-table-column label="设备分组" prop="deviceGroup" width="120" />
          <el-table-column label="重复日期" width="180">
            <template #default="{ row }">
              <el-tag v-for="d in row.weekDays" :key="d" size="small" style="margin-right: 2px">
                {{ ['', '一', '二', '三', '四', '五', '六', '日'][d] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="时间段" width="130">
            <template #default="{ row }">{{ row.startTime }} — {{ row.endTime }}</template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openWeekEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="deleteWeek(row)">删除</el-button>
            </template>
          </el-table-column>
          <template #empty><el-empty description="暂无周排班" /></template>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 人员 Dialog -->
    <el-dialog v-model="personEditVisible" :title="personForm.id ? '编辑人员' : '新增人员'" width="480px">
      <el-form
        ref="personFormRef"
        label-width="90px"
        :model="personForm"
        :rules="{ name: [{ required: true }], phone: [{ required: true }] }"
      >
        <el-form-item label="姓名" prop="name"><el-input v-model="personForm.name" /></el-form-item>
        <el-form-item label="联系方式" prop="phone"><el-input v-model="personForm.phone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="personForm.email" /></el-form-item>
        <el-form-item label="角色"><el-input v-model="personForm.role" /></el-form-item>
        <el-form-item label="告警规则"><el-input v-model="personForm.alarmRule" placeholder="如：所有类型告警" /></el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="personForm.status">
            <el-radio value="active">在职</el-radio>
            <el-radio value="inactive">离职</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="personEditVisible = false">取消</el-button>
        <el-button type="primary" @click="savePerson">保存</el-button>
      </template>
    </el-dialog>

    <!-- 特定日期 Dialog -->
    <el-dialog v-model="specialEditVisible" :title="specialForm.id ? '编辑特定日期排班' : '新增特定日期排班'" width="520px">
      <el-form ref="specialFormRef" label-width="90px" :model="specialForm" :rules="{ name: [{ required: true }] }">
        <el-form-item label="排班名称" prop="name"><el-input v-model="specialForm.name" /></el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="specialForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="specialForm.personIds" multiple style="width: 100%">
            <el-option v-for="p in persons" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备分组"><el-input v-model="specialForm.deviceGroup" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="specialForm.note" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="specialEditVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSpecial">保存</el-button>
      </template>
    </el-dialog>

    <!-- 周排班 Dialog -->
    <el-dialog v-model="weekEditVisible" :title="weekForm.id ? '编辑周排班' : '新增周排班'" width="520px">
      <el-form ref="weekFormRef" label-width="90px" :model="weekForm" :rules="{ name: [{ required: true }] }">
        <el-form-item label="排班名称" prop="name"><el-input v-model="weekForm.name" /></el-form-item>
        <el-form-item label="人员">
          <el-select v-model="weekForm.personIds" multiple style="width: 100%">
            <el-option v-for="p in persons" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备分组"><el-input v-model="weekForm.deviceGroup" /></el-form-item>
        <el-form-item label="重复日期">
          <el-checkbox-group v-model="weekForm.weekDays">
            <el-checkbox v-for="(d, i) in ['一', '二', '三', '四', '五', '六', '日']" :key="i + 1" :value="i + 1">{{ d }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="时间段">
          <el-time-picker v-model="weekForm.startTime" format="HH:mm" value-format="HH:mm" placeholder="开始" style="width: 46%" />
          <span style="margin: 0 8px">—</span>
          <el-time-picker v-model="weekForm.endTime" format="HH:mm" value-format="HH:mm" placeholder="结束" style="width: 46%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="weekEditVisible = false">取消</el-button>
        <el-button type="primary" @click="saveWeek">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getSchedulePersonList,
  doEditSchedulePerson,
  doDeleteSchedulePerson,
  getSpecialDateScheduleList,
  doEditSpecialDateSchedule,
  doDeleteSpecialDateSchedule,
  getWeekScheduleList,
  doEditWeekSchedule,
  doDeleteWeekSchedule,
} from '/@/api/security'

defineOptions({ name: 'SecurityAlarmSchedule' })

const activeTab = ref('persons')
const personLoading = ref(false)
const specialLoading = ref(false)
const weekLoading = ref(false)
const persons = ref<any[]>([])
const specialSchedules = ref<any[]>([])
const weekSchedules = ref<any[]>([])

const fetchAll = async () => {
  personLoading.value = true
  specialLoading.value = true
  weekLoading.value = true
  const [p, s, w] = await Promise.all([getSchedulePersonList(), getSpecialDateScheduleList(), getWeekScheduleList()])
  persons.value = p.data?.list || []
  specialSchedules.value = s.data?.list || []
  weekSchedules.value = w.data?.list || []
  personLoading.value = false
  specialLoading.value = false
  weekLoading.value = false
}

// 人员
const personEditVisible = ref(false)
const personFormRef = ref<any>()
const personForm = reactive<any>({ id: '', name: '', phone: '', email: '', role: '', alarmRule: '', status: 'active' })
const openPersonEdit = (row: any) => {
  Object.assign(personForm, { id: '', name: '', phone: '', email: '', role: '', alarmRule: '', status: 'active', ...row })
  personEditVisible.value = true
}
const savePerson = async () => {
  await personFormRef.value?.validate()
  await doEditSchedulePerson(personForm)
  ElMessage.success('保存成功')
  personEditVisible.value = false
  fetchAll()
}
const deletePerson = (row: any) => {
  ElMessageBox.confirm(`确定删除人员「${row.name}」?`, '提示', { type: 'warning' }).then(async () => {
    await doDeleteSchedulePerson({ id: row.id })
    ElMessage.success('删除成功')
    fetchAll()
  })
}

// 特定日期
const specialEditVisible = ref(false)
const specialFormRef = ref<any>()
const specialForm = reactive<any>({ id: '', name: '', dateRange: null, personIds: [], deviceGroup: '', note: '' })
const openSpecialEdit = (row: any) => {
  Object.assign(specialForm, { id: '', name: '', dateRange: null, personIds: [], deviceGroup: '', note: '', ...row })
  specialEditVisible.value = true
}
const saveSpecial = async () => {
  await specialFormRef.value?.validate()
  await doEditSpecialDateSchedule(specialForm)
  ElMessage.success('保存成功')
  specialEditVisible.value = false
  fetchAll()
}
const deleteSpecial = (row: any) => {
  ElMessageBox.confirm(`确定删除「${row.name}」?`, '提示', { type: 'warning' }).then(async () => {
    await doDeleteSpecialDateSchedule({ id: row.id })
    ElMessage.success('删除成功')
    fetchAll()
  })
}

// 周排班
const weekEditVisible = ref(false)
const weekFormRef = ref<any>()
const weekForm = reactive<any>({
  id: '',
  name: '',
  personIds: [],
  deviceGroup: '',
  weekDays: [1, 2, 3, 4, 5],
  startTime: '08:00',
  endTime: '17:00',
})
const openWeekEdit = (row: any) => {
  Object.assign(weekForm, {
    id: '',
    name: '',
    personIds: [],
    deviceGroup: '',
    weekDays: [1, 2, 3, 4, 5],
    startTime: '08:00',
    endTime: '17:00',
    ...row,
  })
  weekEditVisible.value = true
}
const saveWeek = async () => {
  await weekFormRef.value?.validate()
  await doEditWeekSchedule(weekForm)
  ElMessage.success('保存成功')
  weekEditVisible.value = false
  fetchAll()
}
const deleteWeek = (row: any) => {
  ElMessageBox.confirm(`确定删除「${row.name}」?`, '提示', { type: 'warning' }).then(async () => {
    await doDeleteWeekSchedule({ id: row.id })
    ElMessage.success('删除成功')
    fetchAll()
  })
}

onMounted(fetchAll)
</script>
<template>
  <div class="no-background-container table-auto-height">
    <!-- 声音策略配置 -->
    <vab-card>
      <template #header>声音策略配置</template>
      <el-form label-width="120px" label-position="top">
        <el-form-item label="声音告警">
          <el-switch v-model="soundConfig.soundEnabled" active-text="已开启" inactive-text="已关闭" />
        </el-form-item>
        <el-form-item label="音量">
          <el-slider v-model="soundConfig.volume" :min="0" :max="100" show-input style="width: 320px" />
        </el-form-item>
        <el-form-item label="播报类型">
          <el-select v-model="soundConfig.soundType" style="width: 240px">
            <el-option label="语音播报" value="voice" />
            <el-option label="蜂鸣" value="buzzer" />
            <el-option label="自定义音频" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="soundConfig.soundType === 'custom'" label="上传音频文件">
          <el-upload v-model:file-list="uploadFiles" :auto-upload="false" accept=".mp3,.wav" :limit="1">
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <span style="font-size: 12px; color: #999; margin-left: 8px">支持 .mp3 / .wav 格式</span>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item>
          <el-button type="info" @click="handlePreview">试听</el-button>
          <el-button type="primary" style="margin-left: 12px" @click="handleSaveConfig">保存配置</el-button>
        </el-form-item>
      </el-form>
    </vab-card>

    <!-- 告警级别声音绑定 -->
    <vab-card style="margin-top: 16px">
      <template #header>告警级别声音绑定</template>
      <el-table v-loading="listLoading" border :data="levelList">
        <el-table-column align="center" label="序号" type="index" width="60" />
        <el-table-column label="告警级别" width="120">
          <template #default="{ row }">
            <el-tag :type="levelTypeMap[row.level]">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="声音文件" min-width="180" prop="soundFile" />
        <el-table-column label="重复次数" width="120" prop="repeatCount" />
        <el-table-column label="间隔(秒)" width="120" prop="interval" />
        <el-table-column label="启用" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="handleToggleEnabled(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openLevelEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty class="vab-data-empty" description="暂无数据" />
        </template>
      </el-table>
    </vab-card>

    <!-- 级别编辑 Dialog -->
    <el-dialog v-model="levelEditVisible" title="编辑告警级别声音绑定" width="500px" destroy-on-close>
      <el-form ref="levelFormRef" label-width="110px" :model="levelForm">
        <el-form-item label="告警级别">
          <el-tag :type="levelTypeMap[levelForm.level]">{{ levelForm.level }}</el-tag>
        </el-form-item>
        <el-form-item label="声音文件" prop="soundFile">
          <el-input v-model="levelForm.soundFile" placeholder="请输入声音文件名称" />
        </el-form-item>
        <el-form-item label="重复次数" prop="repeatCount">
          <el-input-number v-model="levelForm.repeatCount" :min="1" :max="99" />
        </el-form-item>
        <el-form-item label="间隔(秒)" prop="interval">
          <el-input-number v-model="levelForm.interval" :min="1" :max="600" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="levelForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="levelEditVisible = false">取消</el-button>
        <el-button type="primary" @click="saveLevel">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, inject, onBeforeMount } from 'vue'
import { Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'SecurityAlarmSound' })

const $baseMessage = inject<any>('$baseMessage')
const $baseConfirm = inject<any>('$baseConfirm')

const mock = (data: any) => new Promise<any>((r) => setTimeout(() => r({ code: '200', msg: 'success', data }), 300))

const levelTypeMap: Record<string, string> = {
  低: 'info',
  中: '',
  高: 'warning',
  紧急: 'danger',
}

const soundConfig = reactive({
  soundEnabled: true,
  volume: 80,
  soundType: 'voice',
})

const uploadFiles = ref<any[]>([])

const listLoading = ref(false)
const levelList = ref<any[]>([])
const levelEditVisible = ref(false)
const levelFormRef = ref<any>()
const levelForm = reactive<any>({
  level: '',
  soundFile: '',
  repeatCount: 3,
  interval: 10,
  enabled: true,
})

const fetchLevelList = async () => {
  listLoading.value = true
  const { data } = await mock([
    { level: '低', soundFile: 'voice_low.mp3', repeatCount: 1, interval: 30, enabled: true },
    { level: '中', soundFile: 'voice_mid.mp3', repeatCount: 3, interval: 15, enabled: true },
    { level: '高', soundFile: 'voice_high.mp3', repeatCount: 5, interval: 10, enabled: true },
    { level: '紧急', soundFile: 'voice_emergency.mp3', repeatCount: 10, interval: 5, enabled: true },
  ])
  levelList.value = data
  listLoading.value = false
}

const handlePreview = () => {
  if (!soundConfig.soundEnabled) {
    $baseMessage('声音告警已关闭，请先开启', 'warning', 'hey')
    return
  }
  $baseMessage('正在播放试听音频...', 'success', 'hey')
}

const handleSaveConfig = async () => {
  const { data } = await mock({ ...soundConfig })
  $baseMessage('声音策略配置已保存', 'success', 'hey')
}

const handleToggleEnabled = (row: any) => {
  const status = row.enabled ? '已启用' : '已禁用'
  $baseMessage(`「${row.level}」级别声音${status}`, 'success', 'hey')
}

const openLevelEdit = (row: any) => {
  Object.assign(levelForm, {
    level: row.level,
    soundFile: row.soundFile,
    repeatCount: row.repeatCount,
    interval: row.interval,
    enabled: row.enabled,
  })
  levelEditVisible.value = true
}

const saveLevel = async () => {
  const idx = levelList.value.findIndex((item) => item.level === levelForm.level)
  if (idx !== -1) {
    levelList.value[idx] = { ...levelList.value[idx], ...levelForm }
  }
  await mock({ code: '200' })
  $baseMessage('保存成功', 'success', 'hey')
  levelEditVisible.value = false
}

onBeforeMount(() => {
  fetchLevelList()
})
</script>
<template>
  <div class="no-background-container table-auto-height">
    <el-tabs v-model="activeType" type="border-card" @tab-change="onTabChange">
      <el-tab-pane v-for="t in alarmTypeTabs" :key="t.value" :label="t.label" :name="t.value">
        <vab-query-form>
          <vab-query-form-top-panel>
            <el-form inline :model="queryForm" @submit.prevent>
              <el-form-item label="状态">
                <el-select v-model="queryForm.status" clearable placeholder="全部">
                  <el-option label="未处理" value="unresolved" />
                  <el-option label="已处理" value="resolved" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button :icon="Search" type="primary" @click="fetchData">查询</el-button>
              </el-form-item>
            </el-form>
          </vab-query-form-top-panel>
        </vab-query-form>

        <el-table v-loading="listLoading" border :data="list">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="告警名称" prop="name" width="130" />
          <el-table-column label="触发位置" prop="location" min-width="160" />
          <el-table-column label="告警级别" width="90">
            <template #default="{ row }">
              <el-tag :type="{ 低: 'info', 中: '', 高: 'warning', 紧急: 'danger' }[row.level]">{{ row.level }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="触发时间" prop="triggerTime" min-width="160" />
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'resolved' ? 'success' : 'danger'">
                {{ row.status === 'resolved' ? '已处理' : '未处理' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="处理人" width="100">
            <template #default="{ row }">{{ row.handler || '—' }}</template>
          </el-table-column>
          <el-table-column label="处理时间" min-width="160">
            <template #default="{ row }">{{ row.resolveTime || '—' }}</template>
          </el-table-column>
          <el-table-column label="备注" min-width="160" show-overflow-tooltip>
            <template #default="{ row }">{{ row.note || '—' }}</template>
          </el-table-column>
          <template #empty><el-empty description="暂无告警记录" /></template>
        </el-table>

        <el-pagination
          background
          :current-page="queryForm.pageNo"
          layout="total, sizes, prev, pager, next"
          :page-size="queryForm.pageSize"
          :total="total"
          @current-change="
            (v) => {
              queryForm.pageNo = v
              fetchData()
            }
          "
          @size-change="
            (v) => {
              queryForm.pageSize = v
              queryForm.pageNo = 1
              fetchData()
            }
          "
        />
      </el-tab-pane>
    </el-tabs>

    <!-- 告警类型说明卡片 -->
    <vab-card style="margin-top: 16px">
      <template #header>告警类型说明</template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="紧急事件告警">健身房、办公区等重点区域一键告警按钮触发，需联动视频调阅快速处置</el-descriptions-item>
        <el-descriptions-item label="消防事件告警">对接消控主机系统，获取消防告警信息并自动触发生成安防工单</el-descriptions-item>
        <el-descriptions-item label="漏水事件告警">IT机房、茶水间等重点区域水浸传感器触发，快速生成安防工单</el-descriptions-item>
        <el-descriptions-item label="烟感事件告警">卫生间内消防烟感触发，获取烟感告警信息并自动生成安防工单</el-descriptions-item>
      </el-descriptions>
    </vab-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getAlarmEventList } from '/@/api/security'

defineOptions({ name: 'SecurityAlarmType' })

const alarmTypeTabs = [
  { label: '紧急事件告警', value: 'emergency' },
  { label: '消防事件告警', value: 'fire' },
  { label: '漏水事件告警', value: 'water_leak' },
  { label: '烟感事件告警', value: 'smoke' },
]

const activeType = ref('emergency')
const listLoading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const queryForm = reactive({ status: '', pageNo: 1, pageSize: 20 })

const fetchData = async () => {
  listLoading.value = true
  const { data } = await getAlarmEventList({ type: activeType.value, ...queryForm })
  list.value = data?.list || []
  total.value = data?.total || 0
  listLoading.value = false
}

const onTabChange = () => {
  queryForm.pageNo = 1
  fetchData()
}

onMounted(fetchData)
</script>
<template>
  <div class="no-background-container table-auto-height">
    <vab-query-form>
      <vab-query-form-left-panel>
        <el-button type="primary" :icon="Plus" @click="openAddEdit({})">新增白名单</el-button>
      </vab-query-form-left-panel>
      <vab-query-form-right-panel>
        <el-form inline :model="queryForm" @submit.prevent>
          <el-form-item label="对象类型">
            <el-select v-model="queryForm.type" clearable placeholder="全部" style="width: 130px">
              <el-option label="全部" value="" />
              <el-option label="人员" value="person" />
              <el-option label="车辆" value="vehicle" />
              <el-option label="设备" value="device" />
              <el-option label="陌生人" value="stranger" />
            </el-select>
          </el-form-item>
          <el-form-item label="关键词">
            <el-input v-model="queryForm.keyword" clearable placeholder="对象名称 / 备注" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="Search" @click="fetchData">查询</el-button>
          </el-form-item>
        </el-form>
      </vab-query-form-right-panel>
    </vab-query-form>

    <el-table v-loading="listLoading" border :data="list">
      <el-table-column align="center" label="序号" type="index" width="60" />
      <el-table-column label="对象名称" prop="name" min-width="130" />
      <el-table-column label="对象类型" width="110">
        <template #default="{ row }">
          <el-tag :type="typeTagMap[row.type]">{{ typeLabelMap[row.type] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="白名单类型" prop="whitelistType" min-width="150" show-overflow-tooltip />
      <el-table-column label="适用范围" prop="scope" min-width="160" show-overflow-tooltip />
      <el-table-column label="有效期" min-width="220">
        <template #default="{ row }">{{ row.validFrom || '--' }} ~ {{ row.validTo || '--' }}</template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
            {{ row.status === 'active' ? '有效' : '已过期' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="备注" prop="remark" min-width="160" show-overflow-tooltip />
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openAddEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
      <template #empty>
        <el-empty class="vab-data-empty" description="暂无白名单记录" />
      </template>
    </el-table>

    <el-pagination
      background
      :current-page="queryForm.pageNo"
      layout="total, sizes, prev, pager, next, jumper"
      :page-size="queryForm.pageSize"
      :total="total"
      @current-change="
        (v) => {
          queryForm.pageNo = v
          fetchData()
        }
      "
      @size-change="
        (v) => {
          queryForm.pageSize = v
          queryForm.pageNo = 1
          fetchData()
        }
      "
    />

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑白名单' : '新增白名单'" width="560px" destroy-on-close>
      <el-form ref="formRef" label-width="100px" :model="form" :rules="formRules">
        <el-form-item label="对象名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入对象名称" />
        </el-form-item>
        <el-form-item label="对象类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择对象类型" style="width: 100%">
            <el-option label="人员" value="person" />
            <el-option label="车辆" value="vehicle" />
            <el-option label="设备" value="device" />
            <el-option label="陌生人" value="stranger" />
          </el-select>
        </el-form-item>
        <el-form-item label="白名单类型" prop="whitelistType">
          <el-select v-model="form.whitelistType" placeholder="请选择白名单类型" style="width: 100%">
            <el-option label="误报加白" value="误报加白" />
            <el-option label="临时通行" value="临时通行" />
            <el-option label="设备维护" value="设备维护" />
          </el-select>
        </el-form-item>
        <el-form-item label="适用范围" prop="scope">
          <el-input v-model="form.scope" placeholder="描述适用范围，如：1F-3F办公区" />
        </el-form-item>
        <el-form-item label="有效期">
          <el-date-picker
            v-model="validRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, inject, onBeforeMount } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'

defineOptions({ name: 'SecurityAlarmWhitelist' })

const $baseMessage = inject<any>('$baseMessage')
const $baseConfirm = inject<any>('$baseConfirm')

const mock = (data: any) => new Promise<any>((r) => setTimeout(() => r({ code: '200', msg: 'success', data }), 300))

const typeTagMap: Record<string, string> = {
  person: 'primary',
  vehicle: 'success',
  device: 'warning',
  stranger: 'info',
}

const typeLabelMap: Record<string, string> = {
  person: '人员',
  vehicle: '车辆',
  device: '设备',
  stranger: '陌生人',
}

const listLoading = ref(false)
const submitLoading = ref(false)
const list = ref<any[]>([])
const total = ref(0)

const queryForm = reactive({
  type: '',
  keyword: '',
  pageNo: 1,
  pageSize: 20,
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<any>()
const form = reactive<any>({
  id: '',
  name: '',
  type: '',
  whitelistType: '',
  scope: '',
  validFrom: '',
  validTo: '',
  remark: '',
  status: 'active',
})
const validRange = ref<any>(null)

const formRules = {
  name: [{ required: true, message: '请输入对象名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择对象类型', trigger: 'change' }],
  whitelistType: [{ required: true, message: '请选择白名单类型', trigger: 'change' }],
}

let nextId = 100

const fetchData = async () => {
  listLoading.value = true
  const { data } = await mock([
    {
      id: '1',
      name: '张工',
      type: 'person',
      whitelistType: '误报加白',
      scope: '1F-3F办公区',
      validFrom: '2026-01-01',
      validTo: '2026-12-31',
      status: 'active',
      remark: '门禁误报免打扰',
    },
    {
      id: '2',
      name: '京A·88888',
      type: 'vehicle',
      whitelistType: '临时通行',
      scope: 'B1停车场',
      validFrom: '2026-06-01',
      validTo: '2026-07-01',
      status: 'expired',
      remark: '临时访客车辆',
    },
    {
      id: '3',
      name: '温感探头-A12',
      type: 'device',
      whitelistType: '设备维护',
      scope: '5F机房',
      validFrom: '2026-07-01',
      validTo: '2026-07-15',
      status: 'active',
      remark: '设备定期校准',
    },
    {
      id: '4',
      name: 'Unknown-3F-东',
      type: 'stranger',
      whitelistType: '误报加白',
      scope: '3F东侧走廊',
      validFrom: '2026-06-15',
      validTo: '2026-07-15',
      status: 'active',
      remark: '常驻保洁人员误识别',
    },
    {
      id: '5',
      name: '李师傅',
      type: 'person',
      whitelistType: '临时通行',
      scope: '全楼',
      validFrom: '2026-07-10',
      validTo: '2026-07-20',
      status: 'active',
      remark: '空调维修师傅',
    },
  ])
  let filtered = data
  if (queryForm.type) filtered = filtered.filter((r: any) => r.type === queryForm.type)
  if (queryForm.keyword) {
    const kw = queryForm.keyword.toLowerCase()
    filtered = filtered.filter((r: any) => r.name.toLowerCase().includes(kw) || (r.remark || '').toLowerCase().includes(kw))
  }
  total.value = filtered.length
  list.value = filtered.slice((queryForm.pageNo - 1) * queryForm.pageSize, queryForm.pageNo * queryForm.pageSize)
  listLoading.value = false
}

const openAddEdit = (row: any) => {
  isEdit.value = !!row.id
  if (row.id) {
    Object.assign(form, {
      id: row.id,
      name: row.name,
      type: row.type,
      whitelistType: row.whitelistType,
      scope: row.scope,
      validFrom: row.validFrom,
      validTo: row.validTo,
      remark: row.remark,
      status: row.status,
    })
    validRange.value = row.validFrom && row.validTo ? [row.validFrom, row.validTo] : null
  } else {
    Object.assign(form, {
      id: '',
      name: '',
      type: '',
      whitelistType: '',
      scope: '',
      validFrom: '',
      validTo: '',
      remark: '',
      status: 'active',
    })
    validRange.value = null
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  if (validRange.value) {
    form.validFrom = validRange.value[0]
    form.validTo = validRange.value[1]
  }

  await mock({ code: '200' })
  if (isEdit.value) {
    const idx = list.value.findIndex((r) => r.id === form.id)
    if (idx !== -1) list.value[idx] = { ...form }
  } else {
    form.id = String(++nextId)
    list.value.unshift({ ...form })
    total.value++
  }
  $baseMessage(isEdit.value ? '修改成功' : '新增成功', 'success', 'hey')
  submitLoading.value = false
  dialogVisible.value = false
}

const handleDelete = (row: any) => {
  $baseConfirm(`确定删除白名单「${row.name}」?`, '删除确认')
    .then(async () => {
      await mock({ code: '200' })
      list.value = list.value.filter((r) => r.id !== row.id)
      total.value--
      $baseMessage('删除成功', 'success', 'hey')
    })
    .catch(() => {
      // user cancelled
    })
}

onBeforeMount(() => {
  fetchData()
})
</script>
<template>
  <div class="no-background-container table-auto-height">
    <vab-query-form>
      <vab-query-form-top-panel>
        <el-form inline :model="queryForm" @submit.prevent>
          <el-form-item label="关键字">
            <el-input v-model.trim="queryForm.keyword" clearable placeholder="工单号/描述" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="queryForm.status" clearable placeholder="全部">
              <el-option label="待分配" value="pending_assign" />
              <el-option label="待接受" value="pending_accept" />
              <el-option label="处理中" value="in_progress" />
              <el-option label="已完成" value="completed" />
            </el-select>
          </el-form-item>
          <el-form-item label="告警类型">
            <el-select v-model="queryForm.alarmType" clearable placeholder="全部">
              <el-option label="紧急事件告警" value="紧急事件告警" />
              <el-option label="消防事件告警" value="消防事件告警" />
              <el-option label="漏水事件告警" value="漏水事件告警" />
              <el-option label="烟感事件告警" value="烟感事件告警" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button :icon="Search" type="primary" @click="fetchData">查询</el-button>
          </el-form-item>
        </el-form>
      </vab-query-form-top-panel>
      <vab-query-form-right-panel>
        <el-button :icon="Plus" type="primary" @click="openEdit({})">新增工单</el-button>
      </vab-query-form-right-panel>
    </vab-query-form>

    <!-- 状态统计卡片 -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col v-for="(s, key) in statusStats" :key="key" :span="6">
        <div class="stat-card" :class="key">
          <div class="stat-num">{{ s.count }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </el-col>
    </el-row>

    <el-table v-loading="listLoading" border :data="list">
      <el-table-column align="center" label="序号" type="index" width="60" />
      <el-table-column label="工单号" prop="orderNo" width="160" />
      <el-table-column label="告警类型" prop="alarmType" width="130" />
      <el-table-column label="紧急程度" width="90">
        <template #default="{ row }">
          <el-tag :type="{ 低: 'info', 中: '', 高: 'warning', 紧急: 'danger' }[row.urgency]">{{ row.urgency }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="位置" prop="location" min-width="140" />
      <el-table-column label="描述" prop="description" min-width="180" show-overflow-tooltip />
      <el-table-column label="上报人" prop="reporter" width="90" />
      <el-table-column label="接单人" width="90">
        <template #default="{ row }">{{ row.assignee || '—' }}</template>
      </el-table-column>
      <el-table-column label="创建时间" prop="createTime" min-width="160" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openView(row)">查看</el-button>
          <el-button v-if="row.status === 'pending_assign'" link type="warning" @click="openAssign(row)">分配</el-button>
          <el-button v-if="row.status !== 'completed'" link type="success" @click="openEdit(row)">处理</el-button>
          <el-button link type="danger" @click="deleteRow(row)">删除</el-button>
          <el-button link type="info" @click="openNearbyCameras(row)">摄像头</el-button>
        </template>
      </el-table-column>
      <template #empty><el-empty description="暂无工单" /></template>
    </el-table>

    <el-pagination
      background
      :current-page="queryForm.pageNo"
      layout="total, sizes, prev, pager, next, jumper"
      :page-size="queryForm.pageSize"
      :total="total"
      @current-change="
        (v) => {
          queryForm.pageNo = v
          fetchData()
        }
      "
      @size-change="
        (v) => {
          queryForm.pageSize = v
          queryForm.pageNo = 1
          fetchData()
        }
      "
    />

    <!-- 编辑/处理 Dialog -->
    <el-dialog v-model="editVisible" :title="editForm.id ? '处理工单' : '新增工单'" width="560px">
      <el-form ref="editFormRef" label-width="90px" :model="editForm" :rules="editRules">
        <el-form-item label="告警类型" prop="alarmType">
          <el-select v-model="editForm.alarmType" style="width: 100%">
            <el-option label="紧急事件告警" value="紧急事件告警" />
            <el-option label="消防事件告警" value="消防事件告警" />
            <el-option label="漏水事件告警" value="漏水事件告警" />
            <el-option label="烟感事件告警" value="烟感事件告警" />
          </el-select>
        </el-form-item>
        <el-form-item label="紧急程度" prop="urgency">
          <el-radio-group v-model="editForm.urgency">
            <el-radio-button value="低">低</el-radio-button>
            <el-radio-button value="中">中</el-radio-button>
            <el-radio-button value="高">高</el-radio-button>
            <el-radio-button value="紧急">紧急</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="位置" prop="location">
          <el-input v-model="editForm.location" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" style="width: 100%">
            <el-option label="待分配" value="pending_assign" />
            <el-option label="待接受" value="pending_accept" />
            <el-option label="处理中" value="in_progress" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item v-if="editForm.id" label="处理记录">
          <el-input v-model="editForm.handleNote" type="textarea" :rows="2" placeholder="填写处理过程和结果" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 查看 Dialog（含附近摄像头） -->
    <el-dialog v-model="viewVisible" title="工单详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="工单号">{{ viewRow.orderNo }}</el-descriptions-item>
        <el-descriptions-item label="告警类型">{{ viewRow.alarmType }}</el-descriptions-item>
        <el-descriptions-item label="紧急程度">{{ viewRow.urgency }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ statusLabel(viewRow.status) }}</el-descriptions-item>
        <el-descriptions-item label="位置" :span="2">{{ viewRow.location }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ viewRow.description }}</el-descriptions-item>
        <el-descriptions-item label="上报人">{{ viewRow.reporter }}</el-descriptions-item>
        <el-descriptions-item label="接单人">{{ viewRow.assignee || '—' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ viewRow.createTime }}</el-descriptions-item>
        <el-descriptions-item label="完成时间">{{ viewRow.resolveTime || '—' }}</el-descriptions-item>
      </el-descriptions>

      <!-- 附近摄像头 -->
      <div v-if="nearbyCameras.length" class="nearby-section">
        <div class="nearby-title">
          <vab-icon icon="camera-line" />
          附近摄像头（20m）
        </div>
        <div class="nearby-grid">
          <div v-for="cam in nearbyCameras" :key="cam.id" class="nearby-card" :class="{ offline: cam.status === 'offline' }">
            <div class="nearby-card-header">
              <span class="nearby-cam-name">{{ cam.name }}</span>
              <el-tag size="small" :type="cam.status === 'online' ? 'success' : 'danger'">
                {{ cam.status === 'online' ? '在线' : '离线' }}
              </el-tag>
            </div>
            <div class="nearby-card-body">
              <span class="nearby-distance">
                <vab-icon icon="map-pin-line" />
                {{ cam.distance }}
              </span>
            </div>
            <div class="nearby-card-actions">
              <el-button size="small" type="primary" :disabled="cam.status !== 'online'" @click="openPreview(cam)">
                <vab-icon icon="film-line" style="margin-right: 4px" />
                实时预览
              </el-button>
              <el-button size="small" type="warning" :disabled="cam.status !== 'online'" @click="openPlayback(cam)">
                <vab-icon icon="history-line" style="margin-right: 4px" />
                历史回放
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 附近摄像头 - 从操作列弹出的独立 Dialog -->
    <el-dialog v-model="nearbyDialogVisible" :title="`附近摄像头（20m）- ${nearbyDialogLocation}`" width="720px" destroy-on-close>
      <div v-if="nearbyDialogCameras.length" class="nearby-grid">
        <div v-for="cam in nearbyDialogCameras" :key="cam.id" class="nearby-card" :class="{ offline: cam.status === 'offline' }">
          <div class="nearby-card-header">
            <span class="nearby-cam-name">{{ cam.name }}</span>
            <el-tag size="small" :type="cam.status === 'online' ? 'success' : 'danger'">
              {{ cam.status === 'online' ? '在线' : '离线' }}
            </el-tag>
          </div>
          <div class="nearby-card-body">
            <span class="nearby-distance">
              <vab-icon icon="map-pin-line" />
              {{ cam.distance }}
            </span>
          </div>
          <div class="nearby-card-actions">
            <el-button size="small" type="primary" :disabled="cam.status !== 'online'" @click="openPreview(cam)">
              <vab-icon icon="film-line" style="margin-right: 4px" />
              实时预览
            </el-button>
            <el-button size="small" type="warning" :disabled="cam.status !== 'online'" @click="openPlayback(cam)">
              <vab-icon icon="history-line" style="margin-right: 4px" />
              历史回放
            </el-button>
          </div>
        </div>
      </div>
      <el-empty v-else description="该位置附近未找到摄像头" />
    </el-dialog>

    <!-- 实时预览 Dialog -->
    <el-dialog
      v-model="previewVisible"
      :title="`实时预览 - ${previewCamera?.name || ''}`"
      width="720px"
      destroy-on-close
      @closed="destroyPreviewPlayer"
    >
      <div v-if="previewCamera" class="player-wrap">
        <vab-jessibuca-player
          :key="previewCamera.id"
          :stream-name="previewCamera.streamName"
          :title="previewCamera.name"
          aspect-ratio="16 / 9"
          has-audio
        />
      </div>
    </el-dialog>

    <!-- 历史回放 Dialog -->
    <el-dialog
      v-model="playbackVisible"
      :title="`历史回放 - ${playbackCamera?.name || ''}`"
      width="720px"
      destroy-on-close
      @closed="destroyPlaybackPlayer"
    >
      <el-form inline>
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="playbackStartTime"
            type="datetime"
            placeholder="选择开始时间"
            default-time="00:00:00"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="playbackEndTime"
            type="datetime"
            placeholder="选择结束时间"
            default-time="23:59:59"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :disabled="!playbackStartTime || !playbackEndTime" @click="startPlayback">开始回放</el-button>
        </el-form-item>
      </el-form>
      <div v-if="playbackActive && playbackCamera" class="player-wrap">
        <vab-jessibuca-player
          :key="`pb-${playbackCamera.id}`"
          :stream-name="playbackCamera.streamName"
          :title="`回放 - ${playbackCamera.name}`"
          aspect-ratio="16 / 9"
          has-audio
        />
      </div>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { getSecurityWorkOrderList, doEditSecurityWorkOrder, doDeleteSecurityWorkOrder } from '/@/api/security'
import VabJessibucaPlayer from '/@vab/components/VabJessibucaPlayer.vue'

defineOptions({ name: 'SecurityAlarmWorkOrder' })

const listLoading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const queryForm = reactive({ keyword: '', status: '', alarmType: '', pageNo: 1, pageSize: 20 })

const statusLabel = (s: string) =>
  ({ pending_assign: '待分配', pending_accept: '待接受', in_progress: '处理中', completed: '已完成' })[s] || s
const statusTagType = (s: string) =>
  ({ pending_assign: 'danger', pending_accept: 'warning', in_progress: '', completed: 'success' })[s] || 'info'

const statusStats = computed(() => ({
  pending_assign: { label: '待分配', count: list.value.filter((o) => o.status === 'pending_assign').length },
  pending_accept: { label: '待接受', count: list.value.filter((o) => o.status === 'pending_accept').length },
  in_progress: { label: '处理中', count: list.value.filter((o) => o.status === 'in_progress').length },
  completed: { label: '已完成', count: list.value.filter((o) => o.status === 'completed').length },
}))

const fetchData = async () => {
  listLoading.value = true
  const { data } = await getSecurityWorkOrderList(queryForm)
  list.value = data?.list || []
  total.value = data?.total || 0
  listLoading.value = false
}

// 编辑
const editVisible = ref(false)
const editFormRef = ref<any>()
const editForm = reactive<any>({
  id: '',
  alarmType: '',
  urgency: '中',
  location: '',
  status: 'pending_assign',
  description: '',
  handleNote: '',
})
const editRules = {
  alarmType: [{ required: true, message: '请选择告警类型' }],
  location: [{ required: true, message: '请填写位置' }],
  description: [{ required: true, message: '请填写描述' }],
}
const openEdit = (row: any) => {
  Object.assign(editForm, {
    id: '',
    alarmType: '',
    urgency: '中',
    location: '',
    status: 'pending_assign',
    description: '',
    handleNote: '',
    ...row,
  })
  editVisible.value = true
}
const saveEdit = async () => {
  await editFormRef.value?.validate()
  await doEditSecurityWorkOrder(editForm)
  ElMessage.success('保存成功')
  editVisible.value = false
  fetchData()
}

// 查看
const viewVisible = ref(false)
const viewRow = ref<any>({})
const openView = (row: any) => {
  viewRow.value = row
  nearbyCameras.value = mockNearbyCameras(row.location || '')
  viewVisible.value = true
}

const openAssign = (row: any) => {
  openEdit({ ...row, status: 'pending_accept' })
}

const deleteRow = (row: any) => {
  ElMessageBox.confirm(`确定删除工单「${row.orderNo}」?`, '提示', { type: 'warning' }).then(async () => {
    await doDeleteSecurityWorkOrder({ id: row.id })
    ElMessage.success('删除成功')
    fetchData()
  })
}

// ====== 附近摄像头功能 ======

const nearbyCameras = ref<any[]>([])

const nearbyDialogVisible = ref(false)
const nearbyDialogLocation = ref('')
const nearbyDialogCameras = ref<any[]>([])

const openNearbyCameras = (row: any) => {
  nearbyDialogLocation.value = row.location || ''
  nearbyDialogCameras.value = mockNearbyCameras(row.location || '')
  nearbyDialogVisible.value = true
}

const mockNearbyCameras = (location: string): any[] => {
  if (!location) return []
  const loc = location.toLowerCase()

  if (loc.includes('入口') || loc.includes('门') || loc.includes('闸机')) {
    return [
      { id: 'CAM01', name: '北门入口摄像头', distance: '8m', status: 'online', streamName: 'cam_north_entrance' },
      { id: 'CAM02', name: '西门入口摄像头', distance: '15m', status: 'online', streamName: 'cam_west_entrance' },
      { id: 'CAM03', name: '南门入口摄像头', distance: '22m', status: 'offline', streamName: 'cam_south_entrance' },
    ]
  }
  if (loc.includes('大堂') || loc.includes('大厅')) {
    return [
      { id: 'CAM04', name: '大堂全景摄像机', distance: '5m', status: 'online', streamName: 'cam_lobby_panoramic' },
      { id: 'CAM05', name: '大堂前台摄像机', distance: '12m', status: 'online', streamName: 'cam_lobby_front' },
      { id: 'CAM06', name: '大堂电梯口摄像机', distance: '18m', status: 'online', streamName: 'cam_lobby_elevator' },
    ]
  }
  if (loc.includes('走廊') || loc.includes('通道')) {
    return [
      { id: 'CAM07', name: '东走廊摄像头', distance: '6m', status: 'online', streamName: 'cam_corridor_east' },
      { id: 'CAM08', name: '西走廊摄像头', distance: '14m', status: 'online', streamName: 'cam_corridor_west' },
      { id: 'CAM09', name: '走廊中间摄像头', distance: '20m', status: 'online', streamName: 'cam_corridor_mid' },
    ]
  }
  if (loc.includes('停车场') || loc.includes('车库') || loc.includes('地库')) {
    return [
      { id: 'CAM10', name: 'B1停车场入口', distance: '10m', status: 'online', streamName: 'cam_parking_b1_entrance' },
      { id: 'CAM11', name: 'B1停车场A区', distance: '25m', status: 'online', streamName: 'cam_parking_b1_a' },
      { id: 'CAM12', name: 'B2停车场B区', distance: '30m', status: 'offline', streamName: 'cam_parking_b2_b' },
    ]
  }
  if (loc.includes('办公区') || loc.includes('办公室')) {
    return [
      { id: 'CAM13', name: '2F办公区东摄像头', distance: '7m', status: 'online', streamName: 'cam_office_2f_east' },
      { id: 'CAM14', name: '2F办公区西摄像头', distance: '13m', status: 'online', streamName: 'cam_office_2f_west' },
      { id: 'CAM15', name: '2F茶水间摄像头', distance: '19m', status: 'online', streamName: 'cam_office_2f_tea' },
    ]
  }
  if (loc.includes('配电') || loc.includes('机房') || loc.includes('设备')) {
    return [
      { id: 'CAM16', name: '配电房摄像头01', distance: '4m', status: 'online', streamName: 'cam_power_room_01' },
      { id: 'CAM17', name: '配电房摄像头02', distance: '11m', status: 'online', streamName: 'cam_power_room_02' },
      { id: 'CAM18', name: '走廊设备区摄像头', distance: '16m', status: 'offline', streamName: 'cam_equip_corridor' },
    ]
  }
  // 周界相关
  if (loc.includes('周界') || loc.includes('围墙') || loc.includes('围栏')) {
    return [
      { id: 'CAM19', name: '北侧周界摄像头', distance: '3m', status: 'online', streamName: 'cam_perimeter_north' },
      { id: 'CAM20', name: '南侧周界摄像头', distance: '15m', status: 'online', streamName: 'cam_perimeter_south' },
      { id: 'CAM21', name: '东侧周界摄像头', distance: '25m', status: 'offline', streamName: 'cam_perimeter_east' },
    ]
  }
  if (loc.includes('电梯') || loc.includes('楼道')) {
    return [
      { id: 'CAM22', name: '电梯内部摄像头', distance: '2m', status: 'online', streamName: 'cam_elevator_inside' },
      { id: 'CAM23', name: '电梯厅摄像头', distance: '8m', status: 'online', streamName: 'cam_elevator_hall' },
    ]
  }
  // 默认
  return [
    { id: 'CAM99', name: '附近摄像头01', distance: '10m', status: 'online', streamName: 'cam_nearby_01' },
    { id: 'CAM98', name: '附近摄像头02', distance: '20m', status: 'online', streamName: 'cam_nearby_02' },
  ]
}

// 实时预览
const previewVisible = ref(false)
const previewCamera = ref<any>(null)

const openPreview = (cam: any) => {
  previewCamera.value = cam
  previewVisible.value = true
}

const destroyPreviewPlayer = () => {
  // VabJessibucaPlayer handles self-destruction on beforeUnmount
  previewCamera.value = null
}

// 历史回放
const playbackVisible = ref(false)
const playbackCamera = ref<any>(null)
const playbackStartTime = ref<Date | null>(null)
const playbackEndTime = ref<Date | null>(null)
const playbackActive = ref(false)

const openPlayback = (cam: any) => {
  playbackCamera.value = cam
  playbackStartTime.value = null
  playbackEndTime.value = null
  playbackActive.value = false
  playbackVisible.value = true
}

const startPlayback = () => {
  if (!playbackStartTime.value || !playbackEndTime.value) {
    ElMessage.warning('请选择回放时间段')
    return
  }
  playbackActive.value = true
  ElMessage.success(`开始回放 ${playbackCamera.value?.name} 的视频`)
}

const destroyPlaybackPlayer = () => {
  playbackCamera.value = null
  playbackActive.value = false
}

onMounted(fetchData)
</script>

<style lang="scss" scoped>
.stat-card {
  padding: 16px;
  border-radius: 8px;
  background: var(--el-fill-color-lighter);
  text-align: center;
  border-left: 4px solid var(--el-color-info);

  &.pending_assign {
    border-color: var(--el-color-danger);
  }
  &.pending_accept {
    border-color: var(--el-color-warning);
  }
  &.in_progress {
    border-color: var(--el-color-primary);
  }
  &.completed {
    border-color: var(--el-color-success);
  }

  .stat-num {
    font-size: 28px;
    font-weight: 700;
    line-height: 1.2;
  }
  .stat-label {
    font-size: 13px;
    color: #666;
    margin-top: 4px;
  }
}

// 附近摄像头
.nearby-section {
  margin-top: 20px;
  border-top: 1px solid var(--el-border-color-light);
  padding-top: 16px;
}

.nearby-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--el-text-color-primary);
}

.nearby-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.nearby-card {
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  padding: 14px;
  transition: box-shadow 0.2s;
  background: var(--el-bg-color);

  &:hover {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  }

  &.offline {
    opacity: 0.65;
    background: var(--el-fill-color-lighter);
  }
}

.nearby-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.nearby-cam-name {
  font-weight: 600;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  margin-right: 8px;
}

.nearby-card-body {
  margin-bottom: 12px;
}

.nearby-distance {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.nearby-card-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.player-wrap {
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}
</style>
<template>
  <div class="security-fire no-background-container table-auto-height">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- ─── 消防监测 ──────────────────────────────── -->
      <el-tab-pane label="消防监测" name="monitor">
        <div class="stat-row">
          <el-statistic title="在线设备" :value="onlineCount" class="stat-item" />
          <el-statistic title="离线设备" :value="offlineCount" class="stat-item danger" />
          <el-statistic title="告警设备" :value="alarmCount" class="stat-item warning" />
          <el-statistic title="故障设备" :value="faultCount" class="stat-item" />
        </div>
        <vab-query-form>
          <vab-query-form-top-panel>
            <el-form inline :model="deviceQuery" @submit.prevent>
              <el-form-item label="设备类型">
                <el-select v-model="deviceQuery.type" clearable placeholder="全部">
                  <el-option label="火灾报警控制器" value="controller" />
                  <el-option label="烟雾探测器" value="smoke_detector" />
                  <el-option label="温感探测器" value="heat_detector" />
                  <el-option label="手动报警按钮" value="manual_button" />
                  <el-option label="消防水泵" value="water_pump" />
                  <el-option label="排烟风机" value="smoke_exhaust_fan" />
                </el-select>
              </el-form-item>
              <el-form-item label="状态">
                <el-select v-model="deviceQuery.status" clearable placeholder="全部">
                  <el-option label="正常" value="normal" />
                  <el-option label="告警" value="alarm" />
                  <el-option label="故障" value="fault" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button :icon="Search" type="primary" @click="fetchFireDevices">查询</el-button>
              </el-form-item>
            </el-form>
          </vab-query-form-top-panel>
        </vab-query-form>

        <el-table v-loading="deviceLoading" border :data="fireDevices">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="设备名称" prop="name" min-width="180" />
          <el-table-column label="设备类型" width="140">
            <template #default="{ row }">{{ deviceTypeMap[row.type] || row.type }}</template>
          </el-table-column>
          <el-table-column label="楼层" prop="floor" width="80" />
          <el-table-column label="位置" prop="area" width="120" />
          <el-table-column label="在线" width="80">
            <template #default="{ row }">
              <el-tag :type="row.online ? 'success' : 'danger'" size="small">{{ row.online ? '在线' : '离线' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="{ normal: 'success', alarm: 'danger', fault: 'warning' }[row.status] || 'info'" size="small">
                {{ { normal: '正常', alarm: '告警', fault: '故障' }[row.status] || row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="最近告警时间" min-width="160">
            <template #default="{ row }">{{ row.lastAlarmTime || '—' }}</template>
          </el-table-column>
          <template #empty><el-empty description="暂无数据" /></template>
        </el-table>
      </el-tab-pane>

      <!-- ─── 告警定位 ──────────────────────────────── -->
      <el-tab-pane label="告警定位" name="alarm">
        <vab-query-form>
          <vab-query-form-top-panel>
            <el-form inline :model="alarmQuery" @submit.prevent>
              <el-form-item label="告警级别">
                <el-select v-model="alarmQuery.level" clearable placeholder="全部">
                  <el-option label="告警" value="alarm" />
                  <el-option label="故障" value="fault" />
                </el-select>
              </el-form-item>
              <el-form-item label="状态">
                <el-select v-model="alarmQuery.status" clearable placeholder="全部">
                  <el-option label="未处理" value="unresolved" />
                  <el-option label="已处理" value="resolved" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button :icon="Search" type="primary" @click="fetchFireAlarms">查询</el-button>
              </el-form-item>
            </el-form>
          </vab-query-form-top-panel>
        </vab-query-form>

        <el-table v-loading="alarmLoading" border :data="fireAlarms">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="设备名称" prop="deviceName" min-width="180" />
          <el-table-column label="告警类型" prop="type" width="120" />
          <el-table-column label="楼层" prop="floor" width="80" />
          <el-table-column label="位置" prop="area" width="120" />
          <el-table-column label="级别" width="90">
            <template #default="{ row }">
              <el-tag :type="row.level === 'alarm' ? 'danger' : 'warning'">{{ row.level === 'alarm' ? '告警' : '故障' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="告警时间" prop="time" min-width="160" />
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'resolved' ? 'success' : 'danger'">
                {{ row.status === 'resolved' ? '已处理' : '未处理' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="处理人" prop="handler" width="100">
            <template #default="{ row }">{{ row.handler || '—' }}</template>
          </el-table-column>
          <el-table-column label="备注" prop="note" min-width="160">
            <template #default="{ row }">{{ row.note || '—' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="90" fixed="right">
            <template #default="{ row }">
              <el-button v-if="row.status !== 'resolved'" link type="primary" @click="ackAlarm(row)">确认</el-button>
            </template>
          </el-table-column>
          <template #empty><el-empty description="暂无告警记录" /></template>
        </el-table>

        <el-pagination
          background
          :current-page="alarmQuery.pageNo"
          layout="total, sizes, prev, pager, next"
          :page-size="alarmQuery.pageSize"
          :total="alarmTotal"
          @current-change="
            (v) => {
              alarmQuery.pageNo = v
              fetchFireAlarms()
            }
          "
          @size-change="
            (v) => {
              alarmQuery.pageSize = v
              alarmQuery.pageNo = 1
              fetchFireAlarms()
            }
          "
        />
      </el-tab-pane>

      <!-- ─── 消防联动 ──────────────────────────────── -->
      <el-tab-pane label="消防联动" name="linkage">
        <vab-query-form>
          <vab-query-form-right-panel>
            <el-button :icon="Plus" type="primary" @click="openLinkageEdit({})">新增联动规则</el-button>
          </vab-query-form-right-panel>
        </vab-query-form>
        <el-table v-loading="linkageLoading" border :data="fireLinkages">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="规则名称" prop="name" min-width="180" />
          <el-table-column label="触发类型" width="120">
            <template #default="{ row }">{{ row.triggerType === 'fire_alarm' ? '消防告警' : row.triggerType }}</template>
          </el-table-column>
          <el-table-column label="触发区域" prop="triggerArea" width="120">
            <template #default="{ row }">{{ row.triggerArea === 'all' ? '全部区域' : row.triggerArea }}</template>
          </el-table-column>
          <el-table-column label="联动动作" width="120">
            <template #default="{ row }">{{ { open_door: '门禁开启', popup_camera: '摄像机弹窗' }[row.action] || row.action }}</template>
          </el-table-column>
          <el-table-column label="说明" prop="targetDescription" min-width="200" />
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" @change="toggleLinkage(row)" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openLinkageEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="deleteLinkage(row)">删除</el-button>
            </template>
          </el-table-column>
          <template #empty><el-empty description="暂无联动规则" /></template>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 联动规则 Dialog -->
    <el-dialog v-model="linkageEditVisible" :title="linkageForm.id ? '编辑联动规则' : '新增联动规则'" width="500px">
      <el-form ref="linkageFormRef" label-width="100px" :model="linkageForm">
        <el-form-item label="规则名称" :rules="[{ required: true }]" prop="name">
          <el-input v-model="linkageForm.name" />
        </el-form-item>
        <el-form-item label="触发类型">
          <el-select v-model="linkageForm.triggerType" style="width: 100%">
            <el-option label="消防告警" value="fire_alarm" />
          </el-select>
        </el-form-item>
        <el-form-item label="触发区域">
          <el-input v-model="linkageForm.triggerArea" placeholder="如：1F 或 all" />
        </el-form-item>
        <el-form-item label="联动动作">
          <el-select v-model="linkageForm.action" style="width: 100%">
            <el-option label="门禁开启" value="open_door" />
            <el-option label="摄像机弹窗" value="popup_camera" />
          </el-select>
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="linkageForm.targetDescription" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="linkageForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="linkageEditVisible = false">取消</el-button>
        <el-button type="primary" @click="saveLinkage">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import {
  getFireDeviceList,
  getFireAlarmList,
  ackFireAlarm,
  getFireLinkageList,
  doEditFireLinkage,
  doDeleteFireLinkage,
} from '/@/api/security'

defineOptions({ name: 'SecurityFire' })

const activeTab = ref('monitor')
const deviceTypeMap: Record<string, string> = {
  controller: '火灾报警控制器',
  smoke_detector: '烟雾探测器',
  heat_detector: '温感探测器',
  manual_button: '手动报警按钮',
  water_pump: '消防水泵',
  smoke_exhaust_fan: '排烟风机',
}

// 设备
const deviceLoading = ref(false)
const fireDevices = ref<any[]>([])
const deviceQuery = reactive({ type: '', status: '' })
const onlineCount = computed(() => fireDevices.value.filter((d) => d.online).length)
const offlineCount = computed(() => fireDevices.value.filter((d) => !d.online).length)
const alarmCount = computed(() => fireDevices.value.filter((d) => d.status === 'alarm').length)
const faultCount = computed(() => fireDevices.value.filter((d) => d.status === 'fault').length)

const fetchFireDevices = async () => {
  deviceLoading.value = true
  const { data } = await getFireDeviceList(deviceQuery)
  fireDevices.value = data?.list || []
  deviceLoading.value = false
}

// 告警
const alarmLoading = ref(false)
const fireAlarms = ref<any[]>([])
const alarmTotal = ref(0)
const alarmQuery = reactive({ level: '', status: '', pageNo: 1, pageSize: 20 })

const fetchFireAlarms = async () => {
  alarmLoading.value = true
  const { data } = await getFireAlarmList(alarmQuery)
  fireAlarms.value = data?.list || []
  alarmTotal.value = data?.total || 0
  alarmLoading.value = false
}

const ackAlarm = async (row: any) => {
  await ackFireAlarm({ id: row.id })
  ElMessage.success('已确认')
  fetchFireAlarms()
}

// 联动
const linkageLoading = ref(false)
const fireLinkages = ref<any[]>([])
const linkageEditVisible = ref(false)
const linkageFormRef = ref<any>()
const linkageForm = reactive<any>({
  id: '',
  name: '',
  triggerType: 'fire_alarm',
  triggerArea: 'all',
  action: 'open_door',
  targetDescription: '',
  enabled: true,
})

const fetchFireLinkages = async () => {
  linkageLoading.value = true
  const { data } = await getFireLinkageList()
  fireLinkages.value = data?.list || []
  linkageLoading.value = false
}

const openLinkageEdit = (row: any) => {
  Object.assign(linkageForm, {
    id: '',
    name: '',
    triggerType: 'fire_alarm',
    triggerArea: 'all',
    action: 'open_door',
    targetDescription: '',
    enabled: true,
    ...row,
  })
  linkageEditVisible.value = true
}
const saveLinkage = async () => {
  await linkageFormRef.value?.validate()
  await doEditFireLinkage(linkageForm)
  ElMessage.success('保存成功')
  linkageEditVisible.value = false
  fetchFireLinkages()
}
const toggleLinkage = async (row: any) => {
  await doEditFireLinkage(row)
  ElMessage.success(row.enabled ? '已启用' : '已停用')
}
const deleteLinkage = (row: any) => {
  ElMessageBox.confirm(`确定删除联动规则「${row.name}」?`, '提示', { type: 'warning' }).then(async () => {
    await doDeleteFireLinkage({ id: row.id })
    ElMessage.success('删除成功')
    fetchFireLinkages()
  })
}

onMounted(() => {
  fetchFireDevices()
  fetchFireAlarms()
  fetchFireLinkages()
})
</script>

<style lang="scss" scoped>
.stat-row {
  display: flex;
  gap: 20px;
  padding: 16px 0;
  margin-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);

  .stat-item {
    flex: 1;
    padding: 12px 16px;
    background: var(--el-fill-color-lighter);
    border-radius: 8px;
    &.danger :deep(.el-statistic__number) {
      color: var(--el-color-danger);
    }
    &.warning :deep(.el-statistic__number) {
      color: var(--el-color-warning);
    }
  }
}
</style>
<template>
  <div>
    <vab-card>
      <!-- Header Row -->
      <div class="header-row">
        <span class="page-title">安防指挥中心</span>
        <div class="header-right">
          <el-select v-model="currentFloor" placeholder="选择楼层" @change="handleFloorChange">
            <el-option v-for="item in floorList" :key="item.floorCode" :label="item.floorName" :value="item.floorCode" />
          </el-select>
        </div>
      </div>

      <!-- Legend Bar -->
      <div class="legend-bar">
        <div class="legend-item">
          <span class="dot dot-camera"></span>
          摄像头
        </div>
        <div class="legend-item">
          <span class="dot dot-door"></span>
          门禁点
        </div>
        <div class="legend-item">
          <span class="dot dot-perimeter"></span>
          周界防区
        </div>
        <div class="legend-item">
          <span class="dot dot-alarm"></span>
          实时告警
        </div>
      </div>

      <!-- Main Content -->
      <el-row :gutter="16">
        <!-- Map Area 70% -->
        <el-col :xs="24" :lg="17">
          <div id="map" class="map-container"></div>
        </el-col>

        <!-- Right Panel 30% -->
        <el-col :xs="24" :lg="7">
          <el-tabs v-model="activeTab" class="right-tabs">
            <!-- Point List Tab -->
            <el-tab-pane label="点位列表" name="pointList">
              <div class="filter-bar">
                <el-radio-group v-model="pointFilter" size="small" @change="handleFilterChange">
                  <el-radio-button value="all">全部</el-radio-button>
                  <el-radio-button value="camera">摄像头</el-radio-button>
                  <el-radio-button value="doorAccess">门禁点</el-radio-button>
                  <el-radio-button value="perimeter">周界防区</el-radio-button>
                </el-radio-group>
              </div>
              <el-scrollbar max-height="calc(100vh - 400px)">
                <div v-for="item in filteredPoints" :key="item.id" class="point-item">
                  <div class="point-left">
                    <span class="point-type-dot" :class="'dot-' + item.type"></span>
                    <div class="point-info">
                      <div class="point-name">{{ item.name }}</div>
                      <div class="point-meta">
                        <span class="point-location">{{ item.location }}</span>
                        <span class="point-status" :class="item.status">{{ item.status === 'online' ? '在线' : '离线' }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="point-actions">
                    <el-button size="small" @click="flyToPoint(item)">查看</el-button>
                    <el-button v-if="item.type === 'camera'" size="small" type="primary" @click="openVideo(item)">视频</el-button>
                  </div>
                </div>
                <el-empty v-if="filteredPoints.length === 0" description="暂无数据" />
              </el-scrollbar>
            </el-tab-pane>

            <!-- Alarm Tab -->
            <el-tab-pane label="实时告警" name="alarms">
              <el-scrollbar max-height="calc(100vh - 400px)">
                <div v-for="alarm in alarmList" :key="alarm.id" class="alarm-item" @click="flyToAlarm(alarm)">
                  <div class="alarm-header">
                    <span class="alarm-type-dot"></span>
                    <span class="alarm-type">{{ alarm.type }}</span>
                    <span class="alarm-time">{{ alarm.time }}</span>
                  </div>
                  <div class="alarm-location">{{ alarm.location }}</div>
                  <div class="alarm-desc">{{ alarm.description }}</div>
                </div>
                <el-empty v-if="alarmList.length === 0" description="暂无告警" />
              </el-scrollbar>
            </el-tab-pane>
          </el-tabs>
        </el-col>
      </el-row>
    </vab-card>

    <!-- Video Dialog -->
    <el-dialog v-model="videoDialogVisible" title="实时视频" width="800px" destroy-on-close>
      <vab-jessibuca-player
        v-if="currentStream"
        :key="currentStream"
        :stream-name="currentStream"
        :auto-play="true"
        :title="currentCameraName"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { storeToRefs } from 'pinia'
import { getSpaceFloorList } from '/@/api/space'
import { useUserStore } from '/@/store/modules/user'
import { getFloorMapUrl } from '/@/utils/index'
import VabJessibucaPlayer from '/@vab/components/VabJessibucaPlayer.vue'

const userStore = useUserStore()
const { spaceCode } = storeToRefs(userStore)

// ─── State ──────────────────────────────────────────────────────
const map = ref<any>(null)
const floorList = ref<any[]>([])
const currentFloor = ref<string>('')
const activeTab = ref<string>('pointList')
const pointFilter = ref<string>('all')
const markersMap = new Map<string, any>()

// Video dialog
const videoDialogVisible = ref(false)
const currentStream = ref('')
const currentCameraName = ref('')

// ─── Mock Data ──────────────────────────────────────────────────
const mockCameras = [
  {
    id: 'cam-1',
    name: '北门摄像头',
    type: 'camera',
    floor: '1F',
    position: { x: -20, z: 15 },
    location: '1F 北门入口',
    status: 'online',
    streamName: 'camera-01',
  },
  {
    id: 'cam-2',
    name: '西门摄像头',
    type: 'camera',
    floor: '1F',
    position: { x: -25, z: -5 },
    location: '1F 西门出口',
    status: 'online',
    streamName: 'camera-02',
  },
  {
    id: 'cam-3',
    name: '2F走廊摄像头东',
    type: 'camera',
    floor: '2F',
    position: { x: 10, z: 5 },
    location: '2F 走廊东侧',
    status: 'online',
    streamName: 'camera-04',
  },
  {
    id: 'cam-4',
    name: '2F走廊摄像头西',
    type: 'camera',
    floor: '2F',
    position: { x: -10, z: 5 },
    location: '2F 走廊西侧',
    status: 'online',
    streamName: 'camera-05',
  },
  {
    id: 'cam-5',
    name: '3F走廊摄像头',
    type: 'camera',
    floor: '3F',
    position: { x: 0, z: 0 },
    location: '3F 走廊中段',
    status: 'offline',
    streamName: 'camera-06',
  },
  {
    id: 'cam-6',
    name: '地库摄像头01',
    type: 'camera',
    floor: 'B1',
    position: { x: -8, z: 8 },
    location: 'B1 车库A区',
    status: 'online',
    streamName: 'camera-07',
  },
  {
    id: 'cam-7',
    name: '地库摄像头02',
    type: 'camera',
    floor: 'B1',
    position: { x: 8, z: -8 },
    location: 'B1 车库B区',
    status: 'online',
    streamName: 'camera-08',
  },
  {
    id: 'cam-8',
    name: '大堂全景摄像机',
    type: 'camera',
    floor: '1F',
    position: { x: 0, z: 2 },
    location: '1F 大堂',
    status: 'online',
    streamName: 'camera-09',
  },
]

const mockDoorAccess = [
  {
    id: 'door-1',
    name: '北门闸机',
    type: 'doorAccess',
    floor: '1F',
    position: { x: -20, z: 14 },
    location: '1F 北门通道',
    status: 'online',
  },
  {
    id: 'door-2',
    name: '西门闸机',
    type: 'doorAccess',
    floor: '1F',
    position: { x: -24, z: -5 },
    location: '1F 西门通道',
    status: 'online',
  },
  {
    id: 'door-3',
    name: '南门闸机',
    type: 'doorAccess',
    floor: '1F',
    position: { x: 14, z: -10 },
    location: '1F 南门通道',
    status: 'offline',
  },
  {
    id: 'door-4',
    name: '2F办公区东',
    type: 'doorAccess',
    floor: '2F',
    position: { x: 12, z: 3 },
    location: '2F 办公区东入口',
    status: 'online',
  },
  {
    id: 'door-5',
    name: '2F办公区西',
    type: 'doorAccess',
    floor: '2F',
    position: { x: -12, z: 3 },
    location: '2F 办公区西入口',
    status: 'online',
  },
  {
    id: 'door-6',
    name: '3F办公区',
    type: 'doorAccess',
    floor: '3F',
    position: { x: 0, z: -2 },
    location: '3F 办公区主入口',
    status: 'online',
  },
]

const mockPerimeter = [
  { id: 'per-1', name: '北侧周界', type: 'perimeter', floor: '1F', position: { x: 0, z: 20 }, location: '建筑北侧外围', status: 'online' },
  { id: 'per-2', name: '南侧周界', type: 'perimeter', floor: '1F', position: { x: 0, z: -20 }, location: '建筑南侧外围', status: 'online' },
  { id: 'per-3', name: '东侧周界', type: 'perimeter', floor: '1F', position: { x: 30, z: 0 }, location: '建筑东侧外围', status: 'online' },
  { id: 'per-4', name: '西侧周界', type: 'perimeter', floor: '1F', position: { x: -30, z: 0 }, location: '建筑西侧外围', status: 'online' },
]

const mockAlarms = [
  {
    id: 'alarm-1',
    time: '2026-07-11 14:23:15',
    type: '门禁异常',
    location: '南门闸机',
    description: '连续3次刷卡验证失败',
    position: { x: 14, z: -10 },
    floor: '1F',
  },
  {
    id: 'alarm-2',
    time: '2026-07-11 13:45:00',
    type: '周界告警',
    location: '北侧周界',
    description: '检测到异常闯入',
    position: { x: 0, z: 20 },
    floor: '1F',
  },
  {
    id: 'alarm-3',
    time: '2026-07-11 12:30:22',
    type: '摄像头离线',
    location: '3F走廊摄像头',
    description: '设备离线超过30分钟',
    position: { x: 0, z: 0 },
    floor: '3F',
  },
  {
    id: 'alarm-4',
    time: '2026-07-11 10:15:08',
    type: '门禁异常',
    location: '西门闸机',
    description: '非授权时段开门',
    position: { x: -24, z: -5 },
    floor: '1F',
  },
  {
    id: 'alarm-5',
    time: '2026-07-11 08:05:33',
    type: '周界告警',
    location: '东侧周界',
    description: '防区传感器触发',
    position: { x: 30, z: 0 },
    floor: '1F',
  },
]

// ─── Computed ───────────────────────────────────────────────────
const allPoints = computed(() => [...mockCameras, ...mockDoorAccess, ...mockPerimeter])

const filteredPoints = computed(() => {
  const floor = currentFloor.value
  if (pointFilter.value === 'all') {
    return allPoints.value.filter((p) => p.floor === floor)
  }
  return allPoints.value.filter((p) => p.floor === floor && p.type === pointFilter.value)
})

const alarmList = computed(() => mockAlarms)

// ─── Type Colors ────────────────────────────────────────────────
const typeColors: Record<string, string> = {
  camera: '#409EFF',
  doorAccess: '#67C23A',
  perimeter: '#E6A23C',
}

// ─── Helpers ────────────────────────────────────────────────────
function createColorIcon(color: string, size = 40): string {
  const canvas = document.createElement('canvas')
  canvas.width = size
  canvas.height = size
  const ctx = canvas.getContext('2d')
  if (!ctx) return ''

  // Outer glow
  ctx.shadowColor = color
  ctx.shadowBlur = 8

  // Filled circle
  ctx.beginPath()
  ctx.arc(size / 2, size / 2, size / 2 - 3, 0, Math.PI * 2)
  ctx.fillStyle = color
  ctx.fill()

  // White border
  ctx.shadowBlur = 0
  ctx.strokeStyle = '#ffffff'
  ctx.lineWidth = 2
  ctx.stroke()

  return canvas.toDataURL()
}

function getFloorName(floorCode: string): string {
  return floorCode.toLowerCase()
}

// ─── Map ────────────────────────────────────────────────────────
function initMap(floorCode: string) {
  if (map.value) {
    map.value.dispose()
    map.value = null
  }

  const container = document.getElementById('map')
  if (!container) return

  map.value = new AirocovMap.Map({
    container,
    mapUrl: getFloorMapUrl(spaceCode.value, floorCode),
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
    zoom: 1,
    bgColor: 'transparent',
    clickIntoBuilding: false,
    font: {
      fontscale: 200,
      iconScale: 5,
      indent: 100,
    },
    onReady: function () {
      map.value.event.on('click', handleMapClick)
      addAllMarkers()
    },
  })

  new AirocovMap.controls.ModeSwitch(map.value, {
    left: '10px',
    bottom: '40px',
    clickCallBack: function () {},
  })

  new AirocovMap.controls.Compass(map.value, {
    width: '48px',
    left: '10px',
    bottom: '130px',
  })
}

function addMarker(item: any) {
  if (!map.value) return

  const color = typeColors[item.type] || '#909399'
  const iconUrl = createColorIcon(color, 40)

  const marker = new AirocovMap.covers.ImageMarker({
    name: 'security',
    imgSrc: iconUrl,
    size: 40,
    position: {
      x: Number(item.position.x),
      y: 2,
      z: Number(item.position.z || 0),
    },
    userData: item,
    canvasHeight: map.value.dom.offsetHeight,
    info: item.name,
    fontSize: 30,
    callback: function (marker: any) {
      markersMap.set(item.id, marker)
      marker.material.depthTest = false
      map.value.addToMap({
        object: marker,
        floorName: getFloorName(item.floor),
        layerName: 'security',
        isClick: true,
      })
    },
  })
}

function addAllMarkers() {
  markersMap.clear()
  allPoints.value.forEach((item) => {
    if (item.floor === currentFloor.value) {
      addMarker(item)
    }
  })
}

// ─── Handlers ───────────────────────────────────────────────────
function handleFloorChange(val: string) {
  currentFloor.value = val
  initMap(val)
}

function handleFilterChange() {
  // computed will re-evaluate automatically
}

function flyCameraTo(position: any) {
  if (!map.value) return
  try {
    if (map.value.render && map.value.render.camera) {
      const cam = map.value.render.camera
      cam.position.set(position.x, 8, position.z + 12)
      if (cam.control && cam.control.target) {
        cam.control.target.set(position.x, 0, position.z)
      }
    }
  } catch (e) {
    console.warn('flyCameraTo error:', e)
  }
}

function flyToPoint(item: any) {
  if (item.floor !== currentFloor.value) {
    currentFloor.value = item.floor
    initMap(item.floor)
    setTimeout(() => {
      flyCameraTo(item.position)
    }, 2000)
  } else {
    flyCameraTo(item.position)
  }
}

function flyToAlarm(alarm: any) {
  if (alarm.floor !== currentFloor.value) {
    currentFloor.value = alarm.floor
    initMap(alarm.floor)
    setTimeout(() => {
      flyCameraTo(alarm.position)
    }, 2000)
  } else {
    flyCameraTo(alarm.position)
  }
}

function openVideo(item: any) {
  currentCameraName.value = item.name
  currentStream.value = item.streamName || ''
  videoDialogVisible.value = true
}

function handleMapClick(e: any) {
  if (e.type === 'ImageMarker' && e.target && e.target.info === 'security') {
    console.log('Clicked security point:', e.target.userData)
  }
}

// ─── Data Fetching ──────────────────────────────────────────────
async function fetchFloorData() {
  try {
    const { data } = await getSpaceFloorList({ spaceCode: spaceCode.value })
    floorList.value = data.SpaceFloorList || []
    if (floorList.value.length > 0) {
      currentFloor.value = floorList.value[0].floorCode
      initMap(currentFloor.value)
    }
  } catch (e) {
    console.error('Failed to load floor list', e)
  }
}

// ─── Lifecycle ──────────────────────────────────────────────────
onMounted(() => {
  fetchFloorData()
})

onBeforeUnmount(() => {
  if (map.value) {
    map.value.dispose()
    map.value = null
  }
})
</script>

<style lang="scss" scoped>
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  .page-title {
    font-size: 20px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

.legend-bar {
  display: flex;
  gap: 24px;
  padding: 12px 0;
  margin-bottom: 12px;
  border-top: 1px solid var(--el-border-color-light);
  border-bottom: 1px solid var(--el-border-color-light);

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  .dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;

    &-camera {
      background: #409eff;
    }

    &-door {
      background: #67c23a;
    }

    &-perimeter {
      background: #e6a23c;
    }

    &-alarm {
      background: #f56c6c;
      animation: blink 1s ease-in-out infinite;
    }
  }
}

@keyframes blink {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}

.map-container {
  width: 100%;
  height: calc(100vh - 280px);
  min-height: 500px;
  border-radius: 4px;
  overflow: hidden;
  position: relative;

  :deep(.airocovFloorSwitch) {
    top: 80px !important;
    left: 20px !important;
  }
}

.right-tabs {
  height: 100%;
}

.filter-bar {
  margin-bottom: 12px;
}

.point-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);

  &:last-child {
    border-bottom: none;
  }

  .point-left {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
    min-width: 0;
  }

  .point-type-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;

    &.dot-camera {
      background: #409eff;
    }

    &.dot-doorAccess {
      background: #67c23a;
    }

    &.dot-perimeter {
      background: #e6a23c;
    }
  }

  .point-info {
    flex: 1;
    min-width: 0;
  }

  .point-name {
    display: block;
    font-size: 14px;
    font-weight: 500;
    color: var(--el-text-color-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .point-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 2px;
  }

  .point-location {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .point-status {
    font-size: 11px;
    padding: 1px 6px;
    border-radius: 2px;

    &.online {
      color: #67c23a;
      background: rgba(103, 194, 58, 0.1);
    }

    &.offline {
      color: #f56c6c;
      background: rgba(245, 108, 108, 0.1);
    }
  }

  .point-actions {
    display: flex;
    gap: 4px;
    flex-shrink: 0;
    margin-left: 8px;
  }
}

.alarm-item {
  padding: 10px 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: var(--el-fill-color-light);
  }

  &:last-child {
    border-bottom: none;
  }

  .alarm-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 4px;
  }

  .alarm-type-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #f56c6c;
    animation: blink 1s ease-in-out infinite;
    flex-shrink: 0;
  }

  .alarm-type {
    font-size: 13px;
    font-weight: 500;
    color: #f56c6c;
  }

  .alarm-time {
    font-size: 11px;
    color: var(--el-text-color-secondary);
    margin-left: auto;
  }

  .alarm-location {
    font-size: 12px;
    color: var(--el-text-color-primary);
    margin-bottom: 2px;
  }

  .alarm-desc {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
}
</style>

<style>
.infoWindowBody {
  z-index: 1 !important;
  background-color: transparent !important;
  border: 0px !important;
}
.airocov_info_Triangle {
  display: none !important;
}
</style>
<template>
  <div class="security-rule-engine table-auto-height">
    <el-tabs v-model="activeTab" type="border-card" @tab-change="onTabChange">
      <!-- ============================================================ -->
      <!-- Tab 1: 合并策略                                                -->
      <!-- ============================================================ -->
      <el-tab-pane label="合并策略" name="merge">
        <vab-query-form>
          <vab-query-form-left-panel>
            <el-button type="primary" :icon="Plus" @click="openMergeDialog({})">新增策略</el-button>
          </vab-query-form-left-panel>
          <vab-query-form-right-panel />
        </vab-query-form>

        <el-table v-loading="mergeLoading" border :data="mergeList">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="名称" prop="name" min-width="160" />
          <el-table-column label="合并窗口(秒)" prop="window" width="130" align="center" />
          <el-table-column label="合并字段" min-width="220">
            <template #default="{ row }">
              <el-checkbox
                v-for="f in mergeFieldOptions"
                :key="f.value"
                v-model="row.fields"
                :label="f.value"
                :value="f.value"
                disabled
                style="margin-right: 12px"
              >
                {{ f.label }}
              </el-checkbox>
            </template>
          </el-table-column>
          <el-table-column label="最大合并数" prop="maxCount" width="110" align="center" />
          <el-table-column label="启用" width="70" align="center">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" @change="() => toggleMerge(row)" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openMergeDialog(row)">编辑</el-button>
              <el-button link type="danger" @click="handleDelete('merge', row)">删除</el-button>
            </template>
          </el-table-column>
          <template #empty>
            <el-empty class="vab-data-empty" description="暂无合并策略" />
          </template>
        </el-table>

        <el-pagination
          background
          :current-page="mergePage.pageNo"
          layout="total, sizes, prev, pager, next, jumper"
          :page-size="mergePage.pageSize"
          :total="mergeTotal"
          @current-change="
            (v) => {
              mergePage.pageNo = v
              fetchMerge()
            }
          "
          @size-change="
            (v) => {
              mergePage.pageSize = v
              mergePage.pageNo = 1
              fetchMerge()
            }
          "
        />
      </el-tab-pane>

      <!-- ============================================================ -->
      <!-- Tab 2: 过滤规则                                                -->
      <!-- ============================================================ -->
      <el-tab-pane label="过滤规则" name="filter">
        <vab-query-form>
          <vab-query-form-left-panel>
            <el-button type="primary" :icon="Plus" @click="openFilterDialog({})">新增规则</el-button>
          </vab-query-form-left-panel>
          <vab-query-form-right-panel />
        </vab-query-form>

        <el-table v-loading="filterLoading" border :data="filterList">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="名称" prop="name" min-width="160" />
          <el-table-column label="过滤条件" min-width="300">
            <template #default="{ row }">
              <span v-if="row.conditions && row.conditions.length">
                <el-tag v-for="(cond, ci) in row.conditions" :key="ci" size="small" style="margin-right: 4px; margin-bottom: 2px">
                  {{ cond.field }} {{ cond.operator }} {{ cond.value }}
                </el-tag>
                <span v-if="row.conditions.length > 1" style="color: var(--el-color-primary); margin-left: 4px">AND</span>
              </span>
              <span v-else>—</span>
            </template>
          </el-table-column>
          <el-table-column label="优先级" prop="priority" width="80" align="center" />
          <el-table-column label="启用" width="70" align="center">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" @change="() => toggleFilter(row)" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openFilterDialog(row)">编辑</el-button>
              <el-button link type="danger" @click="handleDelete('filter', row)">删除</el-button>
            </template>
          </el-table-column>
          <template #empty>
            <el-empty class="vab-data-empty" description="暂无过滤规则" />
          </template>
        </el-table>

        <el-pagination
          background
          :current-page="filterPage.pageNo"
          layout="total, sizes, prev, pager, next, jumper"
          :page-size="filterPage.pageSize"
          :total="filterTotal"
          @current-change="
            (v) => {
              filterPage.pageNo = v
              fetchFilter()
            }
          "
          @size-change="
            (v) => {
              filterPage.pageSize = v
              filterPage.pageNo = 1
              fetchFilter()
            }
          "
        />
      </el-tab-pane>

      <!-- ============================================================ -->
      <!-- Tab 3: 分发规则                                                -->
      <!-- ============================================================ -->
      <el-tab-pane label="分发规则" name="dispatch">
        <vab-query-form>
          <vab-query-form-left-panel>
            <el-button type="primary" :icon="Plus" @click="openDispatchDialog({})">新增规则</el-button>
          </vab-query-form-left-panel>
          <vab-query-form-right-panel />
        </vab-query-form>

        <el-table v-loading="dispatchLoading" border :data="dispatchList">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="名称" prop="name" min-width="150" />
          <el-table-column label="匹配条件" min-width="180" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="row.matchCondition">{{ row.matchCondition }}</span>
              <span v-else>—</span>
            </template>
          </el-table-column>
          <el-table-column label="分发目标" min-width="160">
            <template #default="{ row }">
              <el-tag v-for="t in row.targets" :key="t" size="small" style="margin-right: 4px; margin-bottom: 2px">
                {{ t }}
              </el-tag>
              <span v-if="!row.targets || !row.targets.length">—</span>
            </template>
          </el-table-column>
          <el-table-column label="通知方式" min-width="150">
            <template #default="{ row }">
              <el-tag
                v-for="n in row.notifyMethods"
                :key="n"
                :type="notifyTagType(n)"
                size="small"
                effect="plain"
                style="margin-right: 4px; margin-bottom: 2px"
              >
                {{ n }}
              </el-tag>
              <span v-if="!row.notifyMethods || !row.notifyMethods.length">—</span>
            </template>
          </el-table-column>
          <el-table-column label="启用" width="70" align="center">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" @change="() => toggleDispatch(row)" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openDispatchDialog(row)">编辑</el-button>
              <el-button link type="danger" @click="handleDelete('dispatch', row)">删除</el-button>
            </template>
          </el-table-column>
          <template #empty>
            <el-empty class="vab-data-empty" description="暂无分发规则" />
          </template>
        </el-table>

        <el-pagination
          background
          :current-page="dispatchPage.pageNo"
          layout="total, sizes, prev, pager, next, jumper"
          :page-size="dispatchPage.pageSize"
          :total="dispatchTotal"
          @current-change="
            (v) => {
              dispatchPage.pageNo = v
              fetchDispatch()
            }
          "
          @size-change="
            (v) => {
              dispatchPage.pageSize = v
              dispatchPage.pageNo = 1
              fetchDispatch()
            }
          "
        />
      </el-tab-pane>

      <!-- ============================================================ -->
      <!-- Tab 4: 处置SOP                                                -->
      <!-- ============================================================ -->
      <el-tab-pane label="处置SOP" name="sop">
        <vab-query-form>
          <vab-query-form-left-panel>
            <el-button type="primary" :icon="Plus" @click="openSopDialog({})">新增SOP</el-button>
          </vab-query-form-left-panel>
          <vab-query-form-right-panel />
        </vab-query-form>

        <el-table v-loading="sopLoading" border :data="sopList">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="名称" prop="name" min-width="160" />
          <el-table-column label="适用告警类型" prop="alarmType" min-width="160" />
          <el-table-column label="步骤数" prop="stepCount" width="80" align="center" />
          <el-table-column label="启用" width="70" align="center">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" @change="() => toggleSop(row)" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openSopDialog(row)">编辑</el-button>
              <el-button link type="danger" @click="handleDelete('sop', row)">删除</el-button>
            </template>
          </el-table-column>
          <template #empty>
            <el-empty class="vab-data-empty" description="暂无SOP模板" />
          </template>
        </el-table>

        <el-pagination
          background
          :current-page="sopPage.pageNo"
          layout="total, sizes, prev, pager, next, jumper"
          :page-size="sopPage.pageSize"
          :total="sopTotal"
          @current-change="
            (v) => {
              sopPage.pageNo = v
              fetchSop()
            }
          "
          @size-change="
            (v) => {
              sopPage.pageSize = v
              sopPage.pageNo = 1
              fetchSop()
            }
          "
        />
      </el-tab-pane>
    </el-tabs>

    <!-- ================================================================ -->
    <!-- DIALOG: 合并策略                                                  -->
    <!-- ================================================================ -->
    <el-dialog v-model="mergeDialogVisible" :title="mergeForm.id ? '编辑合并策略' : '新增合并策略'" width="600px" destroy-on-close>
      <el-form ref="mergeFormRef" :model="mergeForm" :rules="mergeRules" label-width="120px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="mergeForm.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="合并窗口(秒)" prop="window">
          <el-input-number v-model="mergeForm.window" :min="1" :max="3600" style="width: 100%" />
        </el-form-item>
        <el-form-item label="合并字段" prop="fields">
          <el-checkbox-group v-model="mergeForm.fields">
            <el-checkbox v-for="f in mergeFieldOptions" :key="f.value" :label="f.value" :value="f.value">
              {{ f.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="最大合并数" prop="maxCount">
          <el-input-number v-model="mergeForm.maxCount" :min="2" :max="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="mergeForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="mergeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="mergeSubmitLoading" @click="submitMerge">保存</el-button>
      </template>
    </el-dialog>

    <!-- ================================================================ -->
    <!-- DIALOG: 过滤规则                                                  -->
    <!-- ================================================================ -->
    <el-dialog v-model="filterDialogVisible" :title="filterForm.id ? '编辑过滤规则' : '新增过滤规则'" width="650px" destroy-on-close>
      <el-form ref="filterFormRef" :model="filterForm" :rules="filterRules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="filterForm.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="过滤条件" prop="conditions">
          <div class="condition-builder">
            <div v-for="(cond, ci) in filterForm.conditions" :key="ci" class="condition-row">
              <el-select v-model="cond.field" placeholder="字段" style="width: 140px" @change="onFilterConditionChange">
                <el-option v-for="f in filterFieldOptions" :key="f.value" :label="f.label" :value="f.value" />
              </el-select>
              <el-select
                v-model="cond.operator"
                placeholder="运算符"
                style="width: 120px; margin-left: 8px"
                @change="onFilterConditionChange"
              >
                <el-option v-for="o in filterOperatorOptions" :key="o.value" :label="o.label" :value="o.value" />
              </el-select>
              <el-input v-model="cond.value" placeholder="值" style="width: 140px; margin-left: 8px" @change="onFilterConditionChange" />
              <el-button type="danger" :icon="Delete" circle size="small" style="margin-left: 8px" @click="removeFilterCondition(ci)" />
            </div>
            <el-button type="primary" link :icon="Plus" @click="addFilterCondition">添加条件</el-button>
          </div>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-input-number v-model="filterForm.priority" :min="1" :max="999" style="width: 100%" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="filterForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="filterDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="filterSubmitLoading" @click="submitFilter">保存</el-button>
      </template>
    </el-dialog>

    <!-- ================================================================ -->
    <!-- DIALOG: 分发规则                                                  -->
    <!-- ================================================================ -->
    <el-dialog v-model="dispatchDialogVisible" :title="dispatchForm.id ? '编辑分发规则' : '新增分发规则'" width="600px" destroy-on-close>
      <el-form ref="dispatchFormRef" :model="dispatchForm" :rules="dispatchRules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="dispatchForm.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="匹配条件" prop="matchCondition">
          <el-input v-model="dispatchForm.matchCondition" type="textarea" :rows="2" placeholder="如：告警级别=紧急 AND 来源系统=消防报警" />
        </el-form-item>
        <el-form-item label="分发目标" prop="targets">
          <el-select v-model="dispatchForm.targets" multiple placeholder="选择角色/人员" style="width: 100%">
            <el-option label="保安队长" value="保安队长" />
            <el-option label="值班员" value="值班员" />
            <el-option label="监控员" value="监控员" />
            <el-option label="张三(值班经理)" value="张三(值班经理)" />
            <el-option label="李四(消防主管)" value="李四(消防主管)" />
            <el-option label="王五(安保员)" value="王五(安保员)" />
          </el-select>
        </el-form-item>
        <el-form-item label="通知方式" prop="notifyMethods">
          <el-checkbox-group v-model="dispatchForm.notifyMethods">
            <el-checkbox label="系统通知" value="系统通知" />
            <el-checkbox label="短信" value="短信" />
            <el-checkbox label="邮件" value="邮件" />
            <el-checkbox label="电话" value="电话" />
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="dispatchForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dispatchDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dispatchSubmitLoading" @click="submitDispatch">保存</el-button>
      </template>
    </el-dialog>

    <!-- ================================================================ -->
    <!-- DIALOG: 处置SOP                                                  -->
    <!-- ================================================================ -->
    <el-dialog v-model="sopDialogVisible" :title="sopForm.id ? '编辑SOP模板' : '新增SOP模板'" width="700px" destroy-on-close>
      <el-form ref="sopFormRef" :model="sopForm" :rules="sopRules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="sopForm.name" placeholder="请输入SOP名称" />
        </el-form-item>
        <el-form-item label="适用告警类型" prop="alarmType">
          <el-select v-model="sopForm.alarmType" placeholder="请选择告警类型" style="width: 100%">
            <el-option label="区域入侵" value="区域入侵" />
            <el-option label="红外入侵" value="红外入侵" />
            <el-option label="非法闯入" value="非法闯入" />
            <el-option label="烟感告警" value="烟感告警" />
            <el-option label="电梯困人" value="电梯困人" />
            <el-option label="水浸告警" value="水浸告警" />
          </el-select>
        </el-form-item>
        <el-form-item label="处置步骤" prop="steps">
          <div class="sop-steps">
            <el-timeline>
              <el-timeline-item v-for="(step, si) in sopForm.steps" :key="si" :timestamp="'第 ' + (si + 1) + ' 步'" placement="top">
                <div class="sop-step-row">
                  <el-form-item
                    :label="'步骤描述'"
                    :prop="'steps.' + si + '.description'"
                    :rules="[{ required: true, message: '请输入步骤描述', trigger: 'blur' }]"
                    style="margin-bottom: 8px"
                  >
                    <el-input v-model="step.description" placeholder="描述该步骤操作内容" type="textarea" :rows="2" />
                  </el-form-item>
                  <div style="display: flex; gap: 12px; align-items: center">
                    <el-form-item
                      label="负责岗位"
                      :prop="'steps.' + si + '.responsibleRole'"
                      :rules="[{ required: true, message: '请选择负责岗位', trigger: 'change' }]"
                      style="margin-bottom: 0; flex: 1"
                    >
                      <el-select v-model="step.responsibleRole" placeholder="负责岗位">
                        <el-option label="保安队长" value="保安队长" />
                        <el-option label="值班员" value="值班员" />
                        <el-option label="监控员" value="监控员" />
                        <el-option label="消防主管" value="消防主管" />
                        <el-option label="工程人员" value="工程人员" />
                      </el-select>
                    </el-form-item>
                    <el-form-item
                      label="时限(min)"
                      :prop="'steps.' + si + '.timeLimit'"
                      :rules="[{ required: true, message: '请输入时限', trigger: 'blur' }]"
                      style="margin-bottom: 0; width: 140px"
                    >
                      <el-input-number v-model="step.timeLimit" :min="1" :max="1440" style="width: 100%" />
                    </el-form-item>
                    <el-button type="danger" :icon="Delete" circle size="small" @click="removeStep(si)" />
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
            <el-button type="primary" link :icon="Plus" @click="addStep">添加步骤</el-button>
          </div>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="sopForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="sopDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="sopSubmitLoading" @click="submitSop">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { Search, Plus, Delete } from '@element-plus/icons-vue'

defineOptions({ name: 'SecurityEventRuleEngine' })

const $baseMessage = inject<any>('$baseMessage')
const $baseConfirm = inject<any>('$baseConfirm')

const mock = (data: any) => new Promise<any>((r) => setTimeout(() => r({ code: '200', msg: 'success', data }), 300))

// ============================================================
// Shared options
// ============================================================

const mergeFieldOptions = [
  { value: 'device', label: '设备' },
  { value: 'location', label: '位置' },
  { value: 'type', label: '类型' },
]

const filterFieldOptions = [
  { value: '告警类型', label: '告警类型' },
  { value: '设备类型', label: '设备类型' },
  { value: '位置', label: '位置' },
  { value: '告警级别', label: '告警级别' },
  { value: '来源系统', label: '来源系统' },
]

const filterOperatorOptions = [
  { value: '=', label: '=' },
  { value: '!=', label: '!=' },
  { value: '包含', label: '包含' },
  { value: '不包含', label: '不包含' },
  { value: '大于', label: '大于' },
  { value: '小于', label: '小于' },
]

const notifyTagType = (n: string): string => {
  const map: Record<string, string> = {
    系统通知: 'primary',
    短信: 'warning',
    邮件: 'info',
    电话: 'danger',
  }
  return map[n] || ''
}

// ============================================================
// Tabs
// ============================================================

const activeTab = ref('merge')

const onTabChange = () => {
  // data is already loaded on mount
}

// ============================================================
// Tab 1: 合并策略
// ============================================================

const mergeLoading = ref(false)
const mergeList = ref<any[]>([])
const mergeTotal = ref(0)
const mergePage = reactive({ pageNo: 1, pageSize: 20 })
const mergeDialogVisible = ref(false)
const mergeSubmitLoading = ref(false)
const mergeFormRef = ref<any>(null)

const mergeForm = reactive<any>({
  id: '',
  name: '',
  window: 30,
  fields: ['device', 'location'],
  maxCount: 10,
  enabled: true,
})

const mergeRules = {
  name: [{ required: true, message: '请输入策略名称', trigger: 'blur' }],
  window: [{ required: true, message: '请输入合并窗口', trigger: 'blur' }],
  maxCount: [{ required: true, message: '请输入最大合并数', trigger: 'blur' }],
}

const fetchMerge = async () => {
  mergeLoading.value = true
  const { data } = await mock([
    {
      id: 'M1',
      name: '默认合并策略',
      window: 30,
      fields: ['device', 'location', 'type'],
      maxCount: 10,
      enabled: true,
    },
    {
      id: 'M2',
      name: '周界入侵合并',
      window: 60,
      fields: ['device', 'location'],
      maxCount: 5,
      enabled: true,
    },
    {
      id: 'M3',
      name: '消防告警合并',
      window: 120,
      fields: ['device'],
      maxCount: 20,
      enabled: false,
    },
  ])
  mergeList.value = data
  mergeTotal.value = data.length
  mergeLoading.value = false
}

const openMergeDialog = (row: any) => {
  if (row.id) {
    Object.assign(mergeForm, {
      id: row.id,
      name: row.name,
      window: row.window,
      fields: [...(row.fields || [])],
      maxCount: row.maxCount,
      enabled: row.enabled,
    })
  } else {
    Object.assign(mergeForm, {
      id: '',
      name: '',
      window: 30,
      fields: ['device', 'location'],
      maxCount: 10,
      enabled: true,
    })
  }
  mergeDialogVisible.value = true
}

const submitMerge = async () => {
  await mergeFormRef.value?.validate()
  mergeSubmitLoading.value = true
  await mock(null)
  mergeSubmitLoading.value = false
  mergeDialogVisible.value = false
  $baseMessage.success(mergeForm.id ? '编辑成功' : '新增成功')
  fetchMerge()
}

const toggleMerge = async (row: any) => {
  await mock(null)
  $baseMessage.success(row.enabled ? '已启用' : '已停用')
}

// ============================================================
// Tab 2: 过滤规则
// ============================================================

const filterLoading = ref(false)
const filterList = ref<any[]>([])
const filterTotal = ref(0)
const filterPage = reactive({ pageNo: 1, pageSize: 20 })
const filterDialogVisible = ref(false)
const filterSubmitLoading = ref(false)
const filterFormRef = ref<any>(null)

const filterForm = reactive<any>({
  id: '',
  name: '',
  conditions: [{ field: '告警级别', operator: '=', value: '紧急' }],
  priority: 1,
  enabled: true,
})

const filterRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
}

const fetchFilter = async () => {
  filterLoading.value = true
  const { data } = await mock([
    {
      id: 'F1',
      name: '紧急告警过滤',
      conditions: [
        { field: '告警级别', operator: '=', value: '紧急' },
        { field: '来源系统', operator: '!=', value: '其他' },
      ],
      priority: 1,
      enabled: true,
    },
    {
      id: 'F2',
      name: '消防烟感过滤',
      conditions: [
        { field: '告警类型', operator: '包含', value: '烟感' },
        { field: '位置', operator: '包含', value: '茶水间' },
      ],
      priority: 2,
      enabled: true,
    },
    {
      id: 'F3',
      name: '误报排除规则',
      conditions: [
        { field: '设备类型', operator: '=', value: '震动光纤' },
        { field: '告警级别', operator: '=', value: '低' },
      ],
      priority: 5,
      enabled: false,
    },
  ])
  filterList.value = data
  filterTotal.value = data.length
  filterLoading.value = false
}

const openFilterDialog = (row: any) => {
  if (row.id) {
    Object.assign(filterForm, {
      id: row.id,
      name: row.name,
      conditions: row.conditions.map((c: any) => ({ ...c })),
      priority: row.priority,
      enabled: row.enabled,
    })
  } else {
    Object.assign(filterForm, {
      id: '',
      name: '',
      conditions: [{ field: '告警级别', operator: '=', value: '紧急' }],
      priority: 1,
      enabled: true,
    })
  }
  filterDialogVisible.value = true
}

const onFilterConditionChange = () => {
  // trigger reactivity for computed display
}

const addFilterCondition = () => {
  filterForm.conditions.push({ field: '告警类型', operator: '=', value: '' })
}

const removeFilterCondition = (index: number) => {
  filterForm.conditions.splice(index, 1)
}

const submitFilter = async () => {
  await filterFormRef.value?.validate()
  if (!filterForm.conditions.length) {
    $baseMessage.warning('请至少添加一个过滤条件')
    return
  }
  filterSubmitLoading.value = true
  await mock(null)
  filterSubmitLoading.value = false
  filterDialogVisible.value = false
  $baseMessage.success(filterForm.id ? '编辑成功' : '新增成功')
  fetchFilter()
}

const toggleFilter = async (row: any) => {
  await mock(null)
  $baseMessage.success(row.enabled ? '已启用' : '已停用')
}

// ============================================================
// Tab 3: 分发规则
// ============================================================

const dispatchLoading = ref(false)
const dispatchList = ref<any[]>([])
const dispatchTotal = ref(0)
const dispatchPage = reactive({ pageNo: 1, pageSize: 20 })
const dispatchDialogVisible = ref(false)
const dispatchSubmitLoading = ref(false)
const dispatchFormRef = ref<any>(null)

const dispatchForm = reactive<any>({
  id: '',
  name: '',
  matchCondition: '',
  targets: [],
  notifyMethods: [],
  enabled: true,
})

const dispatchRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
}

const fetchDispatch = async () => {
  dispatchLoading.value = true
  const { data } = await mock([
    {
      id: 'D1',
      name: '紧急告警分发',
      matchCondition: '告警级别 = 紧急',
      targets: ['保安队长', '张三(值班经理)'],
      notifyMethods: ['系统通知', '电话'],
      enabled: true,
    },
    {
      id: 'D2',
      name: '消防事件分发',
      matchCondition: '来源系统 = 消防报警',
      targets: ['李四(消防主管)', '值班员'],
      notifyMethods: ['系统通知', '短信', '电话'],
      enabled: true,
    },
    {
      id: 'D3',
      name: '周界入侵分发',
      matchCondition: '告警级别 = 高 OR 告警级别 = 紧急 AND 来源系统 = 周界防范',
      targets: ['王五(安保员)', '监控员'],
      notifyMethods: ['系统通知', '短信'],
      enabled: false,
    },
  ])
  dispatchList.value = data
  dispatchTotal.value = data.length
  dispatchLoading.value = false
}

const openDispatchDialog = (row: any) => {
  if (row.id) {
    Object.assign(dispatchForm, {
      id: row.id,
      name: row.name,
      matchCondition: row.matchCondition,
      targets: [...(row.targets || [])],
      notifyMethods: [...(row.notifyMethods || [])],
      enabled: row.enabled,
    })
  } else {
    Object.assign(dispatchForm, {
      id: '',
      name: '',
      matchCondition: '',
      targets: [],
      notifyMethods: [],
      enabled: true,
    })
  }
  dispatchDialogVisible.value = true
}

const submitDispatch = async () => {
  await dispatchFormRef.value?.validate()
  dispatchSubmitLoading.value = true
  await mock(null)
  dispatchSubmitLoading.value = false
  dispatchDialogVisible.value = false
  $baseMessage.success(dispatchForm.id ? '编辑成功' : '新增成功')
  fetchDispatch()
}

const toggleDispatch = async (row: any) => {
  await mock(null)
  $baseMessage.success(row.enabled ? '已启用' : '已停用')
}

// ============================================================
// Tab 4: 处置SOP
// ============================================================

const sopLoading = ref(false)
const sopList = ref<any[]>([])
const sopTotal = ref(0)
const sopPage = reactive({ pageNo: 1, pageSize: 20 })
const sopDialogVisible = ref(false)
const sopSubmitLoading = ref(false)
const sopFormRef = ref<any>(null)

const sopForm = reactive<any>({
  id: '',
  name: '',
  alarmType: '',
  steps: [
    { order: 1, description: '确认告警信息，调阅现场视频', responsibleRole: '监控员', timeLimit: 2 },
    { order: 2, description: '通知就近安保人员前往现场', responsibleRole: '值班员', timeLimit: 5 },
  ],
  enabled: true,
})

const sopRules = {
  name: [{ required: true, message: '请输入SOP名称', trigger: 'blur' }],
  alarmType: [{ required: true, message: '请选择适用告警类型', trigger: 'change' }],
}

const fetchSop = async () => {
  sopLoading.value = true
  const { data } = await mock([
    {
      id: 'S1',
      name: '入侵事件处置流程',
      alarmType: '区域入侵',
      steps: [
        { order: 1, description: '监控员确认告警视频，判断入侵真实性', responsibleRole: '监控员', timeLimit: 1 },
        { order: 2, description: '通知附近安保人员前往现场处置', responsibleRole: '值班员', timeLimit: 3 },
        { order: 3, description: '安保人员到达现场并反馈处置结果', responsibleRole: '保安队长', timeLimit: 10 },
      ],
      enabled: true,
    },
    {
      id: 'S2',
      name: '消防告警处置流程',
      alarmType: '烟感告警',
      steps: [
        { order: 1, description: '确认报警点位，查看烟感探测器状态', responsibleRole: '监控员', timeLimit: 1 },
        { order: 2, description: '通知消防主管前往现场核查', responsibleRole: '值班员', timeLimit: 3 },
        { order: 3, description: '现场核查并反馈情况，必要时启动消防广播', responsibleRole: '消防主管', timeLimit: 8 },
        { order: 4, description: '记录处置结果并归档', responsibleRole: '值班员', timeLimit: 5 },
      ],
      enabled: true,
    },
    {
      id: 'S3',
      name: '电梯困人处置流程',
      alarmType: '电梯困人',
      steps: [
        { order: 1, description: '通过对讲系统安抚被困人员', responsibleRole: '监控员', timeLimit: 1 },
        { order: 2, description: '通知工程人员前往电梯机房', responsibleRole: '值班员', timeLimit: 2 },
        { order: 3, description: '工程人员实施救援操作', responsibleRole: '工程人员', timeLimit: 15 },
      ],
      enabled: false,
    },
  ])
  sopList.value = data
  sopTotal.value = data.length
  sopLoading.value = false
}

const openSopDialog = (row: any) => {
  if (row.id) {
    Object.assign(sopForm, {
      id: row.id,
      name: row.name,
      alarmType: row.alarmType,
      steps: row.steps.map((s: any) => ({ ...s })),
      enabled: row.enabled,
    })
  } else {
    Object.assign(sopForm, {
      id: '',
      name: '',
      alarmType: '',
      steps: [{ order: 1, description: '', responsibleRole: '', timeLimit: 5 }],
      enabled: true,
    })
  }
  sopDialogVisible.value = true
}

const addStep = () => {
  sopForm.steps.push({
    order: sopForm.steps.length + 1,
    description: '',
    responsibleRole: '',
    timeLimit: 5,
  })
}

const removeStep = (index: number) => {
  if (sopForm.steps.length <= 1) {
    $baseMessage.warning('至少保留一个步骤')
    return
  }
  sopForm.steps.splice(index, 1)
  // renumber
  sopForm.steps.forEach((s: any, i: number) => {
    s.order = i + 1
  })
}

const submitSop = async () => {
  await sopFormRef.value?.validate()
  if (!sopForm.steps.length) {
    $baseMessage.warning('请至少添加一个处置步骤')
    return
  }
  sopSubmitLoading.value = true
  await mock(null)
  sopSubmitLoading.value = false
  sopDialogVisible.value = false
  $baseMessage.success(sopForm.id ? '编辑成功' : '新增成功')
  fetchSop()
}

const toggleSop = async (row: any) => {
  await mock(null)
  $baseMessage.success(row.enabled ? '已启用' : '已停用')
}

// ---- Common delete ----

const handleDelete = (tab: string, row: any) => {
  const nameMap: Record<string, string> = {
    merge: '合并策略',
    filter: '过滤规则',
    dispatch: '分发规则',
    sop: 'SOP模板',
  }
  $baseConfirm(`确定删除${nameMap[tab]}「${row.name}」?`, '提示', { type: 'warning' }).then(async () => {
    await mock(null)
    $baseMessage.success('删除成功')
    const fetchers: Record<string, () => Promise<void>> = {
      merge: fetchMerge,
      filter: fetchFilter,
      dispatch: fetchDispatch,
      sop: fetchSop,
    }
    fetchers[tab]?.()
  })
}

// ---- Init ----

onBeforeMount(() => {
  fetchMerge()
  fetchFilter()
  fetchDispatch()
  fetchSop()
})
</script>
<template>
  <div class="security-live no-background-container">
    <el-row :gutter="12" style="height: calc(100vh - 120px)">
      <!-- 左侧：摄像头选择 -->
      <el-col :span="5" style="height: 100%; display: flex; flex-direction: column">
        <vab-card style="flex: 1; overflow: hidden; display: flex; flex-direction: column">
          <template #header>摄像头列表</template>
          <el-input
            v-model="cameraSearch"
            clearable
            placeholder="搜索摄像头"
            style="margin-bottom: 8px; flex-shrink: 0"
            @input="filterCameras"
          />
          <div style="flex: 1; overflow-y: auto">
            <div
              v-for="cam in filteredCameras"
              :key="cam.id"
              class="camera-item"
              :class="{ active: activeCameraIds.includes(cam.id), disabled: !cam.enabled }"
              @click="toggleCamera(cam)"
            >
              <div class="cam-status" :class="cam.status === 'online' ? 'online' : 'offline'" />
              <div class="cam-info">
                <div class="cam-name" :title="cam.name">{{ cam.name }}</div>
                <div class="cam-sub">{{ cam.group || cam.ip }}</div>
              </div>
              <el-icon v-if="activeCameraIds.includes(cam.id)" class="cam-playing"><video-play /></el-icon>
            </div>
            <el-empty v-if="!filteredCameras.length" description="暂无摄像头" />
          </div>
        </vab-card>
      </el-col>

      <!-- 右侧：视频墙 -->
      <el-col :span="19" style="height: 100%; display: flex; flex-direction: column">
        <!-- 工具栏 -->
        <div class="video-toolbar">
          <div class="grid-btns">
            <el-tooltip v-for="g in gridOptions" :key="g.value" :content="`${g.value}画面`">
              <el-button size="small" :type="gridMode === g.value ? 'primary' : ''" @click="setGrid(g.value)">{{ g.label }}</el-button>
            </el-tooltip>
          </div>
          <div class="toolbar-right">
            <el-button size="small" :icon="Refresh" @click="reloadAll">全部刷新</el-button>
            <el-button size="small" type="danger" @click="stopAll">全部停止</el-button>
          </div>
        </div>

        <!-- 视频网格 -->
        <div class="video-grid-wrap" style="flex: 1; overflow: hidden">
          <div class="video-grid" :class="`grid-${gridMode}`">
            <div
              v-for="idx in gridMode"
              :key="idx"
              class="video-cell"
              :class="{ active: activeCells[idx - 1]?.cameraId, selected: selectedCell === idx - 1 }"
              @click="selectedCell = idx - 1"
            >
              <!-- 空格占位 -->
              <div v-if="!activeCells[idx - 1]?.cameraId" class="cell-placeholder">
                <el-icon :size="32"><video-camera /></el-icon>
                <div class="cell-hint">点击左侧摄像头加入</div>
              </div>

              <!-- 视频容器 -->
              <div v-else class="cell-content">
                <div :ref="(el) => setCellRef(el, idx - 1)" class="jessibuca-container" />
                <div class="cell-overlay">
                  <div class="cell-title">{{ activeCells[idx - 1]?.cameraName }}</div>
                  <div class="cell-actions">
                    <el-tooltip content="截图">
                      <el-button circle size="small" :icon="Camera" @click.stop="captureCell(idx - 1)" />
                    </el-tooltip>
                    <el-tooltip content="PTZ控制">
                      <el-button circle size="small" :icon="Aim" @click.stop="openPtz(idx - 1)" />
                    </el-tooltip>
                    <el-tooltip content="关闭">
                      <el-button circle size="small" type="danger" :icon="Close" @click.stop="removeCell(idx - 1)" />
                    </el-tooltip>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- PTZ控制 Dialog -->
    <el-dialog v-model="ptzVisible" title="PTZ云台控制" width="360px" :close-on-click-modal="false">
      <div class="ptz-panel">
        <div class="ptz-name">{{ ptzCell?.cameraName }}</div>
        <div class="ptz-arrows">
          <el-button @mousedown="startPtz('up')" @mouseup="stopPtz" @mouseleave="stopPtz">↑</el-button>
          <div class="ptz-row">
            <el-button @mousedown="startPtz('left')" @mouseup="stopPtz" @mouseleave="stopPtz">←</el-button>
            <el-button @mousedown="startPtz('home')" @mouseup="stopPtz" @mouseleave="stopPtz">⌂</el-button>
            <el-button @mousedown="startPtz('right')" @mouseup="stopPtz" @mouseleave="stopPtz">→</el-button>
          </div>
          <el-button @mousedown="startPtz('down')" @mouseup="stopPtz" @mouseleave="stopPtz">↓</el-button>
        </div>
        <div class="ptz-zoom">
          <el-button @mousedown="startPtz('zoom_in')" @mouseup="stopPtz" @mouseleave="stopPtz">变焦+</el-button>
          <el-button @mousedown="startPtz('zoom_out')" @mouseup="stopPtz" @mouseleave="stopPtz">变焦-</el-button>
        </div>
        <div class="ptz-speed">
          <span>速度：</span>
          <el-slider v-model="ptzSpeed" :min="1" :max="10" style="width: 200px" />
        </div>
        <el-divider>预置点</el-divider>
        <div class="preset-row">
          <el-select v-model="selectedPreset" placeholder="选择预置点" style="flex: 1">
            <el-option v-for="p in presetPoints" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
          <el-button type="primary" @click="gotoPreset">转到</el-button>
          <el-button @click="addPreset">设置</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, VideoCamera, Camera, Aim, Close, Refresh } from '@element-plus/icons-vue'
import { getCameraList } from '/@/api/security'

defineOptions({ name: 'SecurityStreamLive' })

const gridOptions = [
  { value: 1, label: '1' },
  { value: 4, label: '4' },
  { value: 9, label: '9' },
  { value: 16, label: '16' },
]

const gridMode = ref<1 | 4 | 9 | 16>(4)
const selectedCell = ref(0)
const cameraSearch = ref('')
const allCameras = ref<any[]>([])
const filteredCameras = ref<any[]>([])
const activeCells = ref<Array<{ cameraId: string; cameraName: string; url: string } | null>>(Array(16).fill(null))
const activeCameraIds = computed(() => activeCells.value.filter(Boolean).map((c) => c!.cameraId))

const players = new Map<number, any>()
const cellRefs = new Map<number, HTMLElement>()

const setCellRef = (el: any, idx: number) => {
  if (el) cellRefs.set(idx, el)
}

const fetchCameras = async () => {
  const { data } = await getCameraList({ enabled: true })
  allCameras.value = Array.isArray(data) ? data : data?.list || []
  filteredCameras.value = [...allCameras.value]
}

const filterCameras = () => {
  const q = cameraSearch.value.toLowerCase()
  filteredCameras.value = q
    ? allCameras.value.filter((c) => c.name?.toLowerCase().includes(q) || c.ip?.includes(q) || c.group?.toLowerCase().includes(q))
    : [...allCameras.value]
}

const toggleCamera = (cam: any) => {
  if (!cam.enabled) {
    ElMessage.warning('该摄像头未启用')
    return
  }
  const existing = activeCells.value.findIndex((c) => c?.cameraId === cam.id)
  if (existing >= 0) {
    removeCell(existing)
    return
  }
  let target = selectedCell.value
  if (activeCells.value[target]?.cameraId) {
    const empty = activeCells.value.findIndex((c, i) => !c && i < gridMode.value)
    if (empty < 0) {
      ElMessage.warning('当前画面已满，请关闭一个窗格')
      return
    }
    target = empty
  }
  openInCell(target, cam)
}

const openInCell = async (idx: number, cam: any) => {
  const url = cam.live_url || `ws://127.0.0.1:8080/live/${cam.stream || cam.id}.live.flv`
  activeCells.value[idx] = { cameraId: cam.id, cameraName: cam.name, url }
  await nextTick()
  mountPlayer(idx, url)
}

const mountPlayer = (idx: number, url: string) => {
  const container = cellRefs.get(idx)
  if (!container) return
  destroyPlayer(idx)
  const player = new (window as any).Jessibuca({
    container,
    videoBuffer: 0.2,
    decoder: new URL('/src/assets/jessibuca/decoder.js', import.meta.url).href,
    useMSE: true,
    useWCS: true,
    isResize: false,
    isFullResize: true,
    loadingText: '加载中...',
    debug: false,
    showBandwidth: false,
    operateBtns: { fullscreen: false, screenshot: false, play: false, audio: false },
  })
  player.play(url)
  players.set(idx, player)
}

const destroyPlayer = (idx: number) => {
  const p = players.get(idx)
  if (p) {
    try {
      p.destroy()
    } catch (_) {}
    players.delete(idx)
  }
}

const removeCell = (idx: number) => {
  destroyPlayer(idx)
  activeCells.value[idx] = null
}

const setGrid = (n: 1 | 4 | 9 | 16) => {
  for (let i = n; i < gridMode.value; i++) removeCell(i)
  gridMode.value = n
  if (selectedCell.value >= n) selectedCell.value = 0
}

const captureCell = (idx: number) => {
  const p = players.get(idx)
  if (p) {
    const blob = p.screenshot?.()
    if (blob) {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = `snapshot_${Date.now()}.png`
      a.click()
      ElMessage.success('截图已保存')
    }
  }
}

const reloadAll = async () => {
  const snapshot = activeCells.value.map((c) => c)
  snapshot.forEach((cell, idx) => {
    if (cell) {
      destroyPlayer(idx)
      nextTick(() => mountPlayer(idx, cell.url))
    }
  })
}

const stopAll = () => {
  for (let i = 0; i < 16; i++) removeCell(i)
}

// PTZ
const ptzVisible = ref(false)
const ptzCell = ref<{ cameraId: string; cameraName: string } | null>(null)
const ptzSpeed = ref(5)
const selectedPreset = ref('')
const presetPoints = ref<any[]>([])

const openPtz = (idx: number) => {
  const cell = activeCells.value[idx]
  if (!cell) return
  ptzCell.value = cell
  presetPoints.value = [
    { id: '1', name: '预置点1' },
    { id: '2', name: '预置点2' },
    { id: '3', name: '门口' },
  ]
  ptzVisible.value = true
}

const startPtz = (direction: string) => {
  ElMessage.info(`PTZ: ${direction} 速度${ptzSpeed.value}`)
}
const stopPtz = () => {}
const gotoPreset = () => {
  if (!selectedPreset.value) return
  ElMessage.success(`已转到预置点 ${selectedPreset.value}`)
}
const addPreset = () => {
  ElMessage.success('预置点已设置')
}

onMounted(fetchCameras)
onBeforeUnmount(() => {
  for (let i = 0; i < 16; i++) destroyPlayer(i)
})
</script>

<style lang="scss" scoped>
.video-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--el-fill-color-lighter);
  border-radius: 6px;
  margin-bottom: 8px;
  flex-shrink: 0;

  .grid-btns {
    display: flex;
    gap: 4px;
  }
  .toolbar-right {
    display: flex;
    gap: 8px;
  }
}

.video-grid-wrap {
  border-radius: 6px;
  overflow: hidden;
}

.video-grid {
  height: 100%;
  display: grid;
  gap: 4px;
  background: #1a1a2e;
  padding: 4px;

  &.grid-1 {
    grid-template-columns: 1fr;
  }
  &.grid-4 {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 1fr);
  }
  &.grid-9 {
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(3, 1fr);
  }
  &.grid-16 {
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: repeat(4, 1fr);
  }
}

.video-cell {
  position: relative;
  background: #0d0d1a;
  border: 2px solid transparent;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s;

  &:hover {
    border-color: rgba(64, 158, 255, 0.4);
  }
  &.selected {
    border-color: var(--el-color-primary);
  }

  .cell-placeholder {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: rgba(255, 255, 255, 0.3);
    gap: 8px;
    .cell-hint {
      font-size: 12px;
    }
  }

  .cell-content {
    height: 100%;
    position: relative;
  }

  .jessibuca-container {
    width: 100%;
    height: 100%;
  }

  .cell-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 8px;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
    opacity: 0;
    transition: opacity 0.2s;
  }

  &:hover .cell-overlay {
    opacity: 1;
  }

  .cell-title {
    color: #fff;
    font-size: 12px;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .cell-actions {
    display: flex;
    gap: 4px;
    flex-shrink: 0;
  }
}

// 左侧摄像头列表
.camera-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;

  &:hover {
    background: var(--el-fill-color);
  }
  &.active {
    background: var(--el-color-primary-light-9);
  }
  &.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .cam-status {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
    &.online {
      background: var(--el-color-success);
    }
    &.offline {
      background: var(--el-color-danger);
    }
  }

  .cam-info {
    flex: 1;
    overflow: hidden;
  }
  .cam-name {
    font-size: 13px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .cam-sub {
    font-size: 11px;
    color: #999;
  }
  .cam-playing {
    color: var(--el-color-primary);
    flex-shrink: 0;
  }
}

// PTZ面板
.ptz-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;

  .ptz-name {
    font-weight: 600;
  }

  .ptz-arrows {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;

    .ptz-row {
      display: flex;
      gap: 4px;
    }
  }

  .ptz-zoom {
    display: flex;
    gap: 8px;
  }
  .ptz-speed {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
  }
  .preset-row {
    display: flex;
    gap: 8px;
    width: 100%;
  }
}
</style>
<template>
  <div class="no-background-container table-auto-height">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- ─── 平台状态 ──────────────────────────────── -->
      <el-tab-pane label="平台状态" name="status">
        <el-row :gutter="16" style="margin-bottom: 16px">
          <el-col v-for="(s, key) in platformStatus" :key="key" :span="6">
            <div class="status-card">
              <div class="status-icon" :class="s.running ? 'running' : 'stopped'">
                <el-icon><component :is="s.running ? CircleCheck : CircleClose" /></el-icon>
              </div>
              <div class="status-info">
                <div class="status-name">{{ s.name }}</div>
                <el-tag :type="s.running ? 'success' : 'danger'" size="small">{{ s.running ? '运行中' : '已停止' }}</el-tag>
              </div>
              <div class="status-actions">
                <el-button v-if="!s.running" size="small" type="success" @click="controlService(key, 'start')">启动</el-button>
                <el-button v-else size="small" type="danger" @click="controlService(key, 'stop')">停止</el-button>
                <el-button size="small" type="warning" @click="controlService(key, 'restart')">重启</el-button>
              </div>
            </div>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <vab-card>
              <template #header>流媒体服务信息</template>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="服务地址">{{ zlmConfig.host || '—' }}</el-descriptions-item>
                <el-descriptions-item label="HTTP端口">{{ zlmConfig.httpPort || '—' }}</el-descriptions-item>
                <el-descriptions-item label="RTMP端口">{{ zlmConfig.rtmpPort || '—' }}</el-descriptions-item>
                <el-descriptions-item label="RTSP端口">{{ zlmConfig.rtspPort || '—' }}</el-descriptions-item>
                <el-descriptions-item label="WebSocket端口">{{ zlmConfig.wsPort || '—' }}</el-descriptions-item>
                <el-descriptions-item label="密钥">{{ zlmConfig.secret || '—' }}</el-descriptions-item>
              </el-descriptions>
            </vab-card>
          </el-col>
          <el-col :span="12">
            <vab-card>
              <template #header>SIP服务信息 (GB28181)</template>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="SIP服务器ID">{{ sipConfig.serverId || '—' }}</el-descriptions-item>
                <el-descriptions-item label="SIP域">{{ sipConfig.domain || '—' }}</el-descriptions-item>
                <el-descriptions-item label="SIP地址">{{ sipConfig.host || '—' }}</el-descriptions-item>
                <el-descriptions-item label="SIP端口">{{ sipConfig.port || '—' }}</el-descriptions-item>
                <el-descriptions-item label="注册设备数">{{ sipConfig.deviceCount || 0 }}</el-descriptions-item>
                <el-descriptions-item label="在线设备数">{{ sipConfig.onlineCount || 0 }}</el-descriptions-item>
              </el-descriptions>
            </vab-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ─── 转码模板 ──────────────────────────────── -->
      <el-tab-pane label="转码模板" name="transcode">
        <vab-query-form>
          <vab-query-form-right-panel>
            <el-button :icon="Plus" type="primary" @click="openTranscodeEdit({})">新增模板</el-button>
          </vab-query-form-right-panel>
        </vab-query-form>
        <el-table v-loading="transcodeLoading" border :data="transcodeList">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="模板名称" prop="name" min-width="140" />
          <el-table-column label="分辨率" prop="resolution" width="110" />
          <el-table-column label="视频码率(kbps)" prop="videoBitrate" width="140" />
          <el-table-column label="帧率" prop="fps" width="80" />
          <el-table-column label="音频码率(kbps)" prop="audioBitrate" width="140" />
          <el-table-column label="编码" prop="codec" width="100" />
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openTranscodeEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="deleteTranscode(row)">删除</el-button>
            </template>
          </el-table-column>
          <template #empty><el-empty description="暂无转码模板" /></template>
        </el-table>
      </el-tab-pane>

      <!-- ─── 设备管理 ──────────────────────────────── -->
      <el-tab-pane label="设备管理" name="devices">
        <vab-query-form>
          <vab-query-form-top-panel>
            <el-form inline :model="deviceQuery" @submit.prevent>
              <el-form-item label="设备类型">
                <el-select v-model="deviceQuery.deviceType" clearable placeholder="全部">
                  <el-option label="IPC" value="ipc" />
                  <el-option label="NVR" value="nvr" />
                </el-select>
              </el-form-item>
              <el-form-item label="状态">
                <el-select v-model="deviceQuery.status" clearable placeholder="全部">
                  <el-option label="在线" value="online" />
                  <el-option label="离线" value="offline" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button :icon="Search" type="primary" @click="fetchStreamDevices">查询</el-button>
              </el-form-item>
            </el-form>
          </vab-query-form-top-panel>
          <vab-query-form-right-panel>
            <el-button :icon="Plus" type="primary" @click="openStreamDeviceEdit({})">新增设备</el-button>
          </vab-query-form-right-panel>
        </vab-query-form>
        <el-table v-loading="streamDeviceLoading" border :data="streamDevices">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="设备名称" prop="name" min-width="160" />
          <el-table-column label="类型" prop="deviceType" width="80">
            <template #default="{ row }">{{ row.deviceType?.toUpperCase() }}</template>
          </el-table-column>
          <el-table-column label="品牌" prop="brand" width="100" />
          <el-table-column label="IP地址" prop="ip" width="140" />
          <el-table-column label="端口" prop="port" width="80" />
          <el-table-column label="通道数" prop="channelCount" width="80" />
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'online' ? 'success' : 'danger'" size="small">
                {{ row.status === 'online' ? '在线' : '离线' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openStreamDeviceEdit(row)">编辑</el-button>
              <el-button link type="success" @click="addProxy(row)">拉流</el-button>
              <el-button link type="danger" @click="deleteStreamDevice(row)">删除</el-button>
            </template>
          </el-table-column>
          <template #empty><el-empty description="暂无设备" /></template>
        </el-table>
      </el-tab-pane>

      <!-- ─── 流追踪 ──────────────────────────────── -->
      <el-tab-pane label="流追踪" name="flows">
        <vab-query-form>
          <vab-query-form-top-panel>
            <el-form inline :model="flowQuery" @submit.prevent>
              <el-form-item label="关键字">
                <el-input v-model.trim="flowQuery.keyword" clearable placeholder="应用/流ID" />
              </el-form-item>
              <el-form-item>
                <el-button :icon="Search" type="primary" @click="fetchFlows">查询</el-button>
                <el-button :icon="Refresh" style="margin-left: 8px" @click="fetchFlows">刷新</el-button>
              </el-form-item>
            </el-form>
          </vab-query-form-top-panel>
        </vab-query-form>
        <el-table v-loading="flowLoading" border :data="flowList">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="应用" prop="app" width="100" />
          <el-table-column label="流ID" prop="stream" min-width="200" show-overflow-tooltip />
          <el-table-column label="来源类型" prop="originType" width="100" />
          <el-table-column label="客户端数" prop="readerCount" width="90" />
          <el-table-column label="码率(kbps)" prop="bytesSpeed" width="110" />
          <el-table-column label="时长(s)" prop="durationSec" width="90" />
          <el-table-column label="推流时间" prop="createTime" min-width="160" />
          <el-table-column label="操作" width="90" fixed="right">
            <template #default="{ row }">
              <el-button link type="danger" @click="closeFlow(row)">关闭</el-button>
            </template>
          </el-table-column>
          <template #empty><el-empty description="暂无活跃流" /></template>
        </el-table>
      </el-tab-pane>

      <!-- ─── GB28181 ──────────────────────────────── -->
      <el-tab-pane label="GB28181设备" name="gb28181">
        <vab-query-form>
          <vab-query-form-top-panel>
            <el-form inline :model="gbQuery" @submit.prevent>
              <el-form-item label="状态">
                <el-select v-model="gbQuery.status" clearable placeholder="全部">
                  <el-option label="在线" value="online" />
                  <el-option label="离线" value="offline" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button :icon="Search" type="primary" @click="fetchGb28181">查询</el-button>
              </el-form-item>
            </el-form>
          </vab-query-form-top-panel>
        </vab-query-form>
        <el-table v-loading="gbLoading" border :data="gb28181List">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="设备ID" prop="deviceId" min-width="200" show-overflow-tooltip />
          <el-table-column label="设备名称" prop="name" min-width="160" />
          <el-table-column label="IP地址" prop="ip" width="140" />
          <el-table-column label="端口" prop="port" width="80" />
          <el-table-column label="厂商" prop="manufacturer" width="100" />
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'online' ? 'success' : 'danger'" size="small">
                {{ row.status === 'online' ? '在线' : '离线' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="注册时间" prop="registerTime" min-width="160" />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="gbPlayback(row)">回放</el-button>
              <el-button link type="success" @click="gbPreview(row)">预览</el-button>
            </template>
          </el-table-column>
          <template #empty><el-empty description="暂无GB28181设备" /></template>
        </el-table>
      </el-tab-pane>

      <!-- ─── 资源监控 ──────────────────────────────── -->
      <el-tab-pane label="资源监控" name="resource">
        <el-row :gutter="16" style="margin-bottom: 16px">
          <el-col v-for="m in resourceMetrics" :key="m.key" :span="6">
            <div class="metric-card">
              <div class="metric-title">{{ m.label }}</div>
              <el-progress
                type="dashboard"
                :percentage="m.value"
                :color="m.value > 80 ? '#f56c6c' : m.value > 60 ? '#e6a23c' : '#67c23a'"
                :width="100"
              />
              <div class="metric-value">{{ m.display }}</div>
            </div>
          </el-col>
        </el-row>
        <vab-card>
          <template #header>
            <span>实时指标</span>
            <el-button style="float: right" size="small" :icon="Refresh" @click="fetchResource">刷新</el-button>
          </template>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="CPU使用率">{{ resourceData.cpuUsage }}%</el-descriptions-item>
            <el-descriptions-item label="内存使用率">{{ resourceData.memUsage }}%</el-descriptions-item>
            <el-descriptions-item label="磁盘使用率">{{ resourceData.diskUsage }}%</el-descriptions-item>
            <el-descriptions-item label="网络上行">{{ resourceData.networkUpload }} Mbps</el-descriptions-item>
            <el-descriptions-item label="网络下行">{{ resourceData.networkDownload }} Mbps</el-descriptions-item>
            <el-descriptions-item label="活跃流数">{{ resourceData.activeStreams }}</el-descriptions-item>
            <el-descriptions-item label="总连接数">{{ resourceData.totalConnections }}</el-descriptions-item>
            <el-descriptions-item label="ZLM版本">{{ resourceData.zlmVersion }}</el-descriptions-item>
            <el-descriptions-item label="运行时长">{{ resourceData.uptime }}</el-descriptions-item>
          </el-descriptions>
        </vab-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 转码模板 Dialog -->
    <el-dialog v-model="transcodeEditVisible" :title="transcodeForm.id ? '编辑转码模板' : '新增转码模板'" width="520px">
      <el-form ref="transcodeFormRef" label-width="110px" :model="transcodeForm" :rules="{ name: [{ required: true }] }">
        <el-form-item label="模板名称" prop="name"><el-input v-model="transcodeForm.name" /></el-form-item>
        <el-form-item label="分辨率">
          <el-select v-model="transcodeForm.resolution" style="width: 100%">
            <el-option label="3840x2160 (4K)" value="3840x2160" />
            <el-option label="1920x1080 (1080P)" value="1920x1080" />
            <el-option label="1280x720 (720P)" value="1280x720" />
            <el-option label="640x480 (480P)" value="640x480" />
          </el-select>
        </el-form-item>
        <el-form-item label="视频码率(kbps)">
          <el-input-number v-model="transcodeForm.videoBitrate" :min="100" :max="20000" :step="100" />
        </el-form-item>
        <el-form-item label="帧率"><el-input-number v-model="transcodeForm.fps" :min="1" :max="60" /></el-form-item>
        <el-form-item label="音频码率(kbps)">
          <el-input-number v-model="transcodeForm.audioBitrate" :min="32" :max="320" :step="32" />
        </el-form-item>
        <el-form-item label="编码格式">
          <el-select v-model="transcodeForm.codec" style="width: 100%">
            <el-option label="H.264" value="h264" />
            <el-option label="H.265" value="h265" />
          </el-select>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="transcodeForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="transcodeEditVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTranscode">保存</el-button>
      </template>
    </el-dialog>

    <!-- 流媒体设备 Dialog -->
    <el-dialog v-model="streamDeviceEditVisible" :title="streamDeviceForm.id ? '编辑设备' : '新增设备'" width="520px">
      <el-form
        ref="streamDeviceFormRef"
        label-width="90px"
        :model="streamDeviceForm"
        :rules="{ name: [{ required: true }], ip: [{ required: true }] }"
      >
        <el-form-item label="设备名称" prop="name"><el-input v-model="streamDeviceForm.name" /></el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="streamDeviceForm.deviceType" style="width: 100%">
            <el-option label="IPC" value="ipc" />
            <el-option label="NVR" value="nvr" />
          </el-select>
        </el-form-item>
        <el-form-item label="品牌"><el-input v-model="streamDeviceForm.brand" /></el-form-item>
        <el-form-item label="IP地址" prop="ip"><el-input v-model="streamDeviceForm.ip" /></el-form-item>
        <el-form-item label="端口"><el-input-number v-model="streamDeviceForm.port" :min="1" :max="65535" /></el-form-item>
        <el-form-item label="用户名"><el-input v-model="streamDeviceForm.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="streamDeviceForm.password" type="password" show-password /></el-form-item>
        <el-form-item label="通道数"><el-input-number v-model="streamDeviceForm.channelCount" :min="1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="streamDeviceEditVisible = false">取消</el-button>
        <el-button type="primary" @click="saveStreamDevice">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Refresh, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import {
  getPlatformStatus,
  controlPlatformService,
  getZlmConfig,
  getTranscodeTemplateList,
  doEditTranscodeTemplate,
  doDeleteTranscodeTemplate,
  getStreamDeviceList,
  doEditStreamDevice,
  doDeleteStreamDevice,
  addStreamProxy,
  getFlowList,
  closeStream,
  getGb28181DeviceList,
  getResourceMonitor,
} from '/@/api/security'

defineOptions({ name: 'SecurityStreamPlatform' })

const activeTab = ref('status')

// 平台状态
const platformStatus = ref<Record<string, any>>({
  zlm: { name: 'ZLMediaKit 流媒体服务', running: false },
  sip: { name: 'SIP 信令服务 (GB28181)', running: false },
  proxy: { name: '拉流代理服务', running: false },
  record: { name: '录像存储服务', running: false },
})
const zlmConfig = ref<any>({})
const sipConfig = ref<any>({})

const fetchStatus = async () => {
  const [statusRes, configRes] = await Promise.all([getPlatformStatus(), getZlmConfig()])
  const s = statusRes.data || {}
  Object.keys(platformStatus.value).forEach((k) => {
    if (s[k] !== undefined) platformStatus.value[k].running = s[k]
  })
  zlmConfig.value = configRes.data?.zlm || {}
  sipConfig.value = configRes.data?.sip || {}
}

const controlService = async (service: string, action: string) => {
  await controlPlatformService({ service, action })
  ElMessage.success(`操作成功`)
  fetchStatus()
}

// 转码模板
const transcodeLoading = ref(false)
const transcodeList = ref<any[]>([])
const transcodeEditVisible = ref(false)
const transcodeFormRef = ref<any>()
const transcodeForm = reactive<any>({
  id: '',
  name: '',
  resolution: '1920x1080',
  videoBitrate: 2000,
  fps: 25,
  audioBitrate: 128,
  codec: 'h264',
  enabled: true,
})

const fetchTranscodes = async () => {
  transcodeLoading.value = true
  const { data } = await getTranscodeTemplateList()
  transcodeList.value = data?.list || []
  transcodeLoading.value = false
}

const openTranscodeEdit = (row: any) => {
  Object.assign(transcodeForm, {
    id: '',
    name: '',
    resolution: '1920x1080',
    videoBitrate: 2000,
    fps: 25,
    audioBitrate: 128,
    codec: 'h264',
    enabled: true,
    ...row,
  })
  transcodeEditVisible.value = true
}
const saveTranscode = async () => {
  await transcodeFormRef.value?.validate()
  await doEditTranscodeTemplate(transcodeForm)
  ElMessage.success('保存成功')
  transcodeEditVisible.value = false
  fetchTranscodes()
}
const deleteTranscode = (row: any) => {
  ElMessageBox.confirm(`确定删除转码模板「${row.name}」?`, '提示', { type: 'warning' }).then(async () => {
    await doDeleteTranscodeTemplate({ id: row.id })
    ElMessage.success('删除成功')
    fetchTranscodes()
  })
}

// 设备管理
const streamDeviceLoading = ref(false)
const streamDevices = ref<any[]>([])
const deviceQuery = reactive({ deviceType: '', status: '' })
const streamDeviceEditVisible = ref(false)
const streamDeviceFormRef = ref<any>()
const streamDeviceForm = reactive<any>({
  id: '',
  name: '',
  deviceType: 'ipc',
  brand: '',
  ip: '',
  port: 554,
  username: 'admin',
  password: '',
  channelCount: 1,
})

const fetchStreamDevices = async () => {
  streamDeviceLoading.value = true
  const { data } = await getStreamDeviceList(deviceQuery)
  streamDevices.value = data?.list || []
  streamDeviceLoading.value = false
}
const openStreamDeviceEdit = (row: any) => {
  Object.assign(streamDeviceForm, {
    id: '',
    name: '',
    deviceType: 'ipc',
    brand: '',
    ip: '',
    port: 554,
    username: 'admin',
    password: '',
    channelCount: 1,
    ...row,
  })
  streamDeviceEditVisible.value = true
}
const saveStreamDevice = async () => {
  await streamDeviceFormRef.value?.validate()
  await doEditStreamDevice(streamDeviceForm)
  ElMessage.success('保存成功')
  streamDeviceEditVisible.value = false
  fetchStreamDevices()
}
const deleteStreamDevice = (row: any) => {
  ElMessageBox.confirm(`确定删除设备「${row.name}」?`, '提示', { type: 'warning' }).then(async () => {
    await doDeleteStreamDevice({ id: row.id })
    ElMessage.success('删除成功')
    fetchStreamDevices()
  })
}
const addProxy = async (row: any) => {
  await addStreamProxy({ deviceId: row.id })
  ElMessage.success('拉流成功，已推送至流媒体服务')
}

// 流追踪
const flowLoading = ref(false)
const flowList = ref<any[]>([])
const flowQuery = reactive({ keyword: '' })

const fetchFlows = async () => {
  flowLoading.value = true
  const { data } = await getFlowList(flowQuery)
  flowList.value = data?.list || []
  flowLoading.value = false
}
const closeFlow = (row: any) => {
  ElMessageBox.confirm(`确定关闭流「${row.stream}」?`, '提示', { type: 'warning' }).then(async () => {
    await closeStream({ app: row.app, stream: row.stream })
    ElMessage.success('已关闭')
    fetchFlows()
  })
}

// GB28181
const gbLoading = ref(false)
const gb28181List = ref<any[]>([])
const gbQuery = reactive({ status: '' })

const fetchGb28181 = async () => {
  gbLoading.value = true
  const { data } = await getGb28181DeviceList(gbQuery)
  gb28181List.value = data?.list || []
  gbLoading.value = false
}
const gbPreview = (row: any) => {
  ElMessage.info(`预览设备: ${row.name}（${row.deviceId}）`)
}
const gbPlayback = (row: any) => {
  ElMessage.info(`回放设备: ${row.name}（${row.deviceId}）`)
}

// 资源监控
const resourceData = ref<any>({
  cpuUsage: 0,
  memUsage: 0,
  diskUsage: 0,
  networkUpload: 0,
  networkDownload: 0,
  activeStreams: 0,
  totalConnections: 0,
  zlmVersion: '—',
  uptime: '—',
})

const resourceMetrics = computed(() => [
  { key: 'cpu', label: 'CPU', value: resourceData.value.cpuUsage, display: `${resourceData.value.cpuUsage}%` },
  { key: 'mem', label: '内存', value: resourceData.value.memUsage, display: `${resourceData.value.memUsage}%` },
  { key: 'disk', label: '磁盘', value: resourceData.value.diskUsage, display: `${resourceData.value.diskUsage}%` },
  {
    key: 'net',
    label: '带宽利用率',
    value: resourceData.value.networkUtil || 0,
    display: `↑${resourceData.value.networkUpload} / ↓${resourceData.value.networkDownload} Mbps`,
  },
])

const fetchResource = async () => {
  const { data } = await getResourceMonitor()
  resourceData.value = data || resourceData.value
}

onMounted(async () => {
  await fetchStatus()
  fetchTranscodes()
  fetchStreamDevices()
  fetchFlows()
  fetchGb28181()
  fetchResource()
})
</script>

<style lang="scss" scoped>
.status-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--el-fill-color-lighter);
  border-radius: 8px;

  .status-icon {
    font-size: 28px;
    &.running {
      color: var(--el-color-success);
    }
    &.stopped {
      color: var(--el-color-danger);
    }
  }
  .status-info {
    flex: 1;
    .status-name {
      font-weight: 600;
      margin-bottom: 4px;
    }
  }
  .status-actions {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
}

.metric-card {
  background: var(--el-fill-color-lighter);
  border-radius: 8px;
  padding: 16px;
  text-align: center;

  .metric-title {
    font-weight: 600;
    margin-bottom: 12px;
  }
  .metric-value {
    margin-top: 8px;
    color: #666;
    font-size: 12px;
  }
}
</style>
<template>
  <div class="security-monitor no-background-container">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- ─── 监控设备管理 ──────────────────────────────────────────── -->
      <el-tab-pane label="监控设备管理" name="devices">
        <vab-query-form>
          <vab-query-form-top-panel>
            <el-form inline :model="deviceQuery" @submit.prevent>
              <el-form-item label="设备名称">
                <el-input v-model.trim="deviceQuery.name" clearable placeholder="请输入设备名称" />
              </el-form-item>
              <el-form-item label="状态">
                <el-select v-model="deviceQuery.status" clearable placeholder="全部">
                  <el-option label="在线" value="online" />
                  <el-option label="离线" value="offline" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button :icon="Search" type="primary" @click="fetchCameras">查询</el-button>
              </el-form-item>
            </el-form>
          </vab-query-form-top-panel>
          <vab-query-form-right-panel>
            <el-button :icon="Plus" type="primary" @click="openCameraEdit({})">新增摄像头</el-button>
          </vab-query-form-right-panel>
        </vab-query-form>

        <el-table v-loading="cameraLoading" border :data="cameraList" class="table-auto-height">
          <el-table-column align="center" label="序号" type="index" width="60" />
          <el-table-column label="设备名称" prop="name" min-width="160" />
          <el-table-column label="IP地址" prop="ip" width="140" />
          <el-table-column label="类型" prop="type" width="80" />
          <el-table-column label="品牌" prop="brand" width="100" />
          <el-table-column label="所属分组" prop="group" min-width="120" />
          <el-table-column label="PTZ协议" prop="ptzProtocol" width="110" />
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'online' ? 'success' : 'danger'">
                {{ row.status === 'online' ? '在线' : '离线' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="启用" width="80">
            <template #default="{ row }">
              <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '启用' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openCameraEdit(row)">编辑</el-button>
              <el-button link type="warning" @click="startStream(row)">拉流</el-button>
              <el-button link type="danger" @click="deleteCameraRow(row)">删除</el-button>
            </template>
          </el-table-column>
          <template #empty><el-empty description="暂无数据" /></template>
        </el-table>
      </el-tab-pane>

      <!-- ─── 视频调阅 ──────────────────────────────────────────────── -->
      <el-tab-pane label="视频调阅" name="live">
        <el-row :gutter="16" style="height: calc(100vh - 200px)">
          <el-col :span="5" style="height: 100%; overflow: auto">
            <vab-card style="height: 100%">
              <template #header>区域选择</template>
              <el-tree
                ref="spaceTreeRef"
                :data="spaceTree"
                :expand-on-click-node="false"
                default-expand-all
                highlight-current
                node-key="id"
                :props="{ label: 'label', children: 'children' }"
                @node-click="onSpaceNodeClick"
              />
            </vab-card>
          </el-col>
          <el-col :span="19" style="height: 100%; display: flex; flex-direction: column">
            <!-- 工具栏 -->
            <div class="live-toolbar">
              <el-input v-model="liveSearch" clearable placeholder="搜索摄像头" style="width: 200px" @input="filterLiveCameras" />
              <div class="grid-btns">
                <el-tooltip content="单屏">
                  <el-button :type="gridCount === 1 ? 'primary' : ''" circle @click="setGrid(1)">
                    <vab-icon icon="layout-line" />
                  </el-button>
                </el-tooltip>
                <el-tooltip content="四分屏">
                  <el-button :type="gridCount === 4 ? 'primary' : ''" circle @click="setGrid(4)">
                    <vab-icon icon="grid-fill" />
                  </el-button>
                </el-tooltip>
                <el-tooltip content="九分屏">
                  <el-button :type="gridCount === 9 ? 'primary' : ''" circle @click="setGrid(9)">
                    <vab-icon icon="layout-grid-fill" />
                  </el-button>
                </el-tooltip>
                <el-tooltip content="十六分屏">
                  <el-button :type="gridCount === 16 ? 'primary' : ''" circle @click="setGrid(16)">
                    <vab-icon icon="apps-fill" />
                  </el-button>
                </el-tooltip>
              </div>
              <el-button type="danger" plain @click="stopAllStreams">停止全部</el-button>
            </div>

            <!-- 视频网格 -->
            <div class="video-grid" :class="`grid-${gridCount}`">
              <div
                v-for="(slot, idx) in gridCount"
                :key="idx"
                class="video-cell"
                :class="{ selected: selectedCell === idx }"
                @click="selectedCell = idx"
              >
                <template v-if="liveCells[idx]">
                  <div class="video-label">{{ liveCells[idx].name }}</div>
                  <div :id="`live-player-${idx}`" class="jessibuca-container"></div>
                  <div class="video-actions">
                    <el-button link size="small" type="primary" @click.stop="playCell(idx)">播放</el-button>
                    <el-button link size="small" @click.stop="captureCell(idx, liveCells[idx])">抓拍</el-button>
                    <el-button link size="small" type="warning" @click.stop="openReport(liveCells[idx])">上报异常</el-button>
                    <el-button link size="small" type="danger" @click.stop="stopCell(idx)">关闭</el-button>
                  </div>
                </template>
                <template v-else>
                  <div class="empty-cell">
                    <div class="empty-hint">点击选中后，从左侧拖入或点击下方添加</div>
                    <el-popover placement="bottom" trigger="click" :width="260">
                      <template #reference>
                        <el-button :icon="Plus" size="small" type="primary" plain>添加摄像头</el-button>
                      </template>
                      <el-scrollbar height="240px">
                        <div v-for="cam in filteredLiveCameras" :key="cam.id" class="cam-pick-item" @click="assignCameraToCell(idx, cam)">
                          <el-tag :type="cam.status === 'online' ? 'success' : 'danger'" size="small">
                            {{ cam.status === 'online' ? '在线' : '离线' }}
                          </el-tag>
                          {{ cam.name }}
                        </div>
                      </el-scrollbar>
                    </el-popover>
                  </div>
                </template>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ─── 视频回放 ──────────────────────────────────────────────── -->
      <el-tab-pane label="视频回放" name="playback">
        <el-row :gutter="20" style="height: calc(100vh - 200px)">
          <el-col :span="6" style="height: 100%">
            <vab-card style="height: 100%">
              <template #header>回放设置</template>
              <el-form label-position="top" :model="playbackForm">
                <el-form-item label="选择摄像头">
                  <el-select v-model="playbackForm.cameraId" clearable filterable placeholder="请选择摄像头" style="width: 100%">
                    <el-option v-for="c in cameraList" :key="c.id" :label="c.name" :value="c.id" :disabled="c.status === 'offline'" />
                  </el-select>
                </el-form-item>
                <el-form-item label="时间范围">
                  <el-date-picker
                    v-model="playbackForm.timeRange"
                    end-placeholder="结束时间"
                    start-placeholder="开始时间"
                    style="width: 100%"
                    type="datetimerange"
                    value-format="YYYY-MM-DD HH:mm:ss"
                  />
                </el-form-item>
                <el-form-item label="播放速度">
                  <el-radio-group v-model="playbackForm.speed">
                    <el-radio-button :value="0.25">0.25x</el-radio-button>
                    <el-radio-button :value="0.5">0.5x</el-radio-button>
                    <el-radio-button :value="1">1x</el-radio-button>
                    <el-radio-button :value="2">2x</el-radio-button>
                    <el-radio-button :value="4">4x</el-radio-button>
                  </el-radio-group>
                </el-form-item>
                <el-form-item>
                  <el-button style="width: 100%" type="primary" @click="startPlayback">开始回放</el-button>
                </el-form-item>
              </el-form>

              <el-divider />
              <div class="playback-controls">
                <el-button :icon="VideoPause" circle :disabled="!playbackActive" @click="pausePlayback" />
                <el-button :icon="VideoPlay" circle :disabled="!playbackActive" @click="resumePlayback" />
                <el-button :icon="RefreshRight" circle :disabled="!playbackActive" @click="restartPlayback" />
                <el-button :icon="Close" circle :disabled="!playbackActive" @click="stopPlayback" />
              </div>
              <div v-if="playbackActive" style="margin-top: 12px">
                <el-slider v-model="playbackProgress" :show-tooltip="false" @change="seekPlayback" />
                <div style="font-size: 12px; color: #999; margin-top: 4px">{{ playbackTimeDisplay }}</div>
              </div>
              <el-button v-if="playbackActive" style="margin-top: 8px; width: 100%" type="warning" plain @click="openReport(null)">
                上报异常
              </el-button>
            </vab-card>
          </el-col>
          <el-col :span="18" style="height: 100%">
            <div id="playback-player" class="playback-player">
              <el-empty v-if="!playbackActive" description="请在左侧选择摄像头和时间后点击开始回放" />
            </div>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>

    <!-- ─── 摄像头编辑 Dialog ──────────────────────────────────── -->
    <el-dialog v-model="cameraEditVisible" :title="cameraForm.id ? '编辑摄像头' : '新增摄像头'" width="560px" @close="resetCameraForm">
      <el-form ref="cameraFormRef" label-width="100px" :model="cameraForm" :rules="cameraRules">
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="cameraForm.name" />
        </el-form-item>
        <el-form-item label="IP地址" prop="ip">
          <el-input v-model="cameraForm.ip" />
        </el-form-item>
        <el-form-item label="设备类型" prop="type">
          <el-select v-model="cameraForm.type" style="width: 100%">
            <el-option label="IPC" value="IPC" />
            <el-option label="NVR" value="NVR" />
          </el-select>
        </el-form-item>
        <el-form-item label="品牌">
          <el-input v-model="cameraForm.brand" />
        </el-form-item>
        <el-form-item label="型号">
          <el-input v-model="cameraForm.model" />
        </el-form-item>
        <el-form-item label="所属分组">
          <el-input v-model="cameraForm.group" />
        </el-form-item>
        <el-form-item label="PTZ协议">
          <el-select v-model="cameraForm.ptzProtocol" style="width: 100%">
            <el-option label="PELCO-D" value="PELCO-D" />
            <el-option label="PELCO-P" value="PELCO-P" />
            <el-option label="VISCA" value="VISCA" />
            <el-option label="无" value="none" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="cameraForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cameraEditVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCameraForm">保存</el-button>
      </template>
    </el-dialog>

    <!-- ─── 上报异常 Dialog ──────────────────────────────────── -->
    <el-dialog v-model="reportVisible" title="上报安防异常" width="480px">
      <el-form ref="reportFormRef" label-width="90px" :model="reportForm" :rules="reportRules">
        <el-form-item label="摄像头">
          <el-input :value="reportForm.cameraName" disabled />
        </el-form-item>
        <el-form-item label="告警类型" prop="alarmType">
          <el-select v-model="reportForm.alarmType" style="width: 100%">
            <el-option label="紧急事件告警" value="emergency" />
            <el-option label="消防事件告警" value="fire" />
            <el-option label="漏水事件告警" value="water_leak" />
            <el-option label="烟感事件告警" value="smoke" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="紧急程度" prop="urgency">
          <el-radio-group v-model="reportForm.urgency">
            <el-radio-button value="low">低</el-radio-button>
            <el-radio-button value="medium">中</el-radio-button>
            <el-radio-button value="high">高</el-radio-button>
            <el-radio-button value="urgent">紧急</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="异常描述" prop="description">
          <el-input v-model="reportForm.description" :rows="3" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reportVisible = false">取消</el-button>
        <el-button type="danger" @click="submitReport">提交上报</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onBeforeUnmount, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, VideoPause, VideoPlay, RefreshRight, Close } from '@element-plus/icons-vue'
import { getCameraList, doEditCamera, doDeleteCamera, addStreamProxy, delStreamProxy, reportSecurityIncident } from '/@/api/security'

defineOptions({ name: 'SecurityMonitor' })

// ─── tabs ─────────────────────────────────────────────────────────────────────
const activeTab = ref('devices')

// ─── 监控设备 ─────────────────────────────────────────────────────────────────
const cameraLoading = ref(false)
const cameraList = ref<any[]>([])
const deviceQuery = reactive({ name: '', status: '' })

const fetchCameras = async () => {
  cameraLoading.value = true
  try {
    const { data } = await getCameraList(deviceQuery)
    cameraList.value = Array.isArray(data) ? data : data?.list || []
  } finally {
    cameraLoading.value = false
  }
}

const cameraEditVisible = ref(false)
const cameraFormRef = ref<any>()
const cameraForm = reactive<any>({
  id: '',
  name: '',
  ip: '',
  type: 'IPC',
  brand: '',
  model: '',
  group: '',
  ptzProtocol: 'PELCO-D',
  enabled: true,
})
const cameraRules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  ip: [{ required: true, message: '请输入IP地址', trigger: 'blur' }],
  type: [{ required: true, message: '请选择设备类型', trigger: 'change' }],
}

const openCameraEdit = (row: any) => {
  Object.assign(cameraForm, {
    id: '',
    name: '',
    ip: '',
    type: 'IPC',
    brand: '',
    model: '',
    group: '',
    ptzProtocol: 'PELCO-D',
    enabled: true,
    ...row,
  })
  cameraEditVisible.value = true
}
const resetCameraForm = () => {
  cameraFormRef.value?.resetFields()
}

const saveCameraForm = async () => {
  await cameraFormRef.value?.validate()
  await doEditCamera(cameraForm)
  ElMessage.success('保存成功')
  cameraEditVisible.value = false
  fetchCameras()
}

const startStream = async (row: any) => {
  await addStreamProxy(row)
  ElMessage.success('拉流指令已发送')
}

const deleteCameraRow = (row: any) => {
  ElMessageBox.confirm(`确定删除摄像头「${row.name}」吗？`, '提示', { type: 'warning' }).then(async () => {
    await doDeleteCamera({ id: row.id })
    ElMessage.success('删除成功')
    fetchCameras()
  })
}

// ─── 视频调阅 ─────────────────────────────────────────────────────────────────
const spaceTreeRef = ref<any>()
const spaceTree = ref([
  {
    id: '1',
    label: '极企大厦',
    children: [
      {
        id: '1F',
        label: '1层',
        children: [
          { id: '1F-entrance', label: '大门区域' },
          { id: '1F-elevator', label: '电梯口' },
        ],
      },
      {
        id: '2F',
        label: '2层',
        children: [
          { id: '2F-corridor', label: '走廊' },
          { id: '2F-stairwell', label: '楼梯间' },
        ],
      },
      { id: 'B1', label: '地下1层', children: [{ id: 'B1-parking', label: '停车场' }] },
    ],
  },
])
const liveSearch = ref('')
const gridCount = ref(4)
const liveCells = ref<any[]>(new Array(16).fill(null))
const selectedCell = ref(0)
const players = ref(new Map<string, any>())
const playingStreams = ref<string[]>([])

const filteredLiveCameras = computed(() => {
  if (!liveSearch.value) return cameraList.value
  return cameraList.value.filter((c) => c.name.includes(liveSearch.value))
})

const filterLiveCameras = () => {}

const onSpaceNodeClick = (node: any) => {
  if (!node.children) {
    fetchCameras()
  }
}

const setGrid = (count: number) => {
  gridCount.value = count
}

const assignCameraToCell = async (cellIdx: number, cam: any) => {
  liveCells.value[cellIdx] = cam
  if (cam.live_url) {
    await addStreamProxy(cam)
    setTimeout(() => createJessibucaPlayer(`live-player-${cellIdx}`, cam.live_url), 300)
  }
}

const createJessibucaPlayer = (containerId: string, url: string) => {
  const container = document.getElementById(containerId)
  if (!container || !(window as any).Jessibuca) return null
  if (players.value.has(containerId)) {
    players.value.get(containerId)?.destroy()
    players.value.delete(containerId)
  }
  try {
    const player = new (window as any).Jessibuca({
      container,
      isFlv: true,
      decoder: new URL('/src/assets/jessibuca/decoder.js', import.meta.url).href,
      videoBuffer: 0.2,
      isResize: false,
      useWCS: true,
      useMSE: true,
      hasAudio: false,
      loadingText: '加载中...',
      supportDblclickFullscreen: true,
      operateBtns: { fullscreen: true, screenshot: true, play: true },
      timeout: 30,
    })
    player.on('play', () => {
      if (!playingStreams.value.includes(containerId)) playingStreams.value.push(containerId)
    })
    player.on('pause', () => {
      playingStreams.value = playingStreams.value.filter((k) => k !== containerId)
    })
    player.play(url)
    players.value.set(containerId, player)
    return player
  } catch (e) {
    console.error('Jessibuca init failed:', e)
    return null
  }
}

const playCell = (idx: number) => {
  const cam = liveCells.value[idx]
  if (!cam?.live_url) {
    ElMessage.warning('该摄像头暂无直播流')
    return
  }
  createJessibucaPlayer(`live-player-${idx}`, cam.live_url)
}

const captureCell = (idx: number, cam: any) => {
  const player = players.value.get(`live-player-${idx}`)
  if (player?.screenshot) {
    player.screenshot(`snapshot_${cam.name}_${Date.now()}`, 'png')
    ElMessage.success('截图已保存到本地')
  } else {
    ElMessage.info('播放器未就绪，无法抓拍')
  }
}

const stopCell = async (idx: number) => {
  const cam = liveCells.value[idx]
  const key = `live-player-${idx}`
  players.value.get(key)?.destroy()
  players.value.delete(key)
  if (cam) await delStreamProxy({ key: `__defaultVhost__/${cam.app}/${cam.stream}` })
  liveCells.value[idx] = null
}

const stopAllStreams = async () => {
  for (let i = 0; i < gridCount.value; i++) {
    if (liveCells.value[i]) await stopCell(i)
  }
}

// ─── 视频回放 ─────────────────────────────────────────────────────────────────
const playbackForm = reactive({ cameraId: '', timeRange: null as any, speed: 1 })
const playbackActive = ref(false)
const playbackProgress = ref(0)
const playbackTimeDisplay = ref('')
let playbackPlayer: any = null
let progressTimer: any = null

const startPlayback = () => {
  if (!playbackForm.cameraId) {
    ElMessage.warning('请选择摄像头')
    return
  }
  if (!playbackForm.timeRange) {
    ElMessage.warning('请选择时间范围')
    return
  }
  const cam = cameraList.value.find((c) => c.id === playbackForm.cameraId)
  if (!cam?.live_url) {
    ElMessage.warning('该摄像头暂无可用流地址')
    return
  }
  playbackActive.value = true
  playbackProgress.value = 0
  if (playbackPlayer) {
    playbackPlayer.destroy()
    playbackPlayer = null
  }
  setTimeout(() => {
    playbackPlayer = createJessibucaPlayer('playback-player', cam.live_url)
  }, 200)
  progressTimer = setInterval(() => {
    if (playbackProgress.value < 100) playbackProgress.value += 0.1
    else clearInterval(progressTimer)
  }, 500)
}
const pausePlayback = () => playbackPlayer?.pause()
const resumePlayback = () =>
  playbackPlayer?.resume
    ? playbackPlayer.resume()
    : playbackPlayer?.play(cameraList.value.find((c) => c.id === playbackForm.cameraId)?.live_url)
const restartPlayback = () => {
  playbackProgress.value = 0
  startPlayback()
}
const stopPlayback = () => {
  playbackPlayer?.destroy()
  playbackPlayer = null
  clearInterval(progressTimer)
  playbackActive.value = false
  playbackProgress.value = 0
}
const seekPlayback = (val: number) => {
  playbackTimeDisplay.value = `进度 ${val.toFixed(1)}%`
}

// ─── 上报异常 Dialog ──────────────────────────────────────────────────────────
const reportVisible = ref(false)
const reportFormRef = ref<any>()
const reportForm = reactive({ cameraId: '', cameraName: '', alarmType: '', urgency: 'medium', description: '' })
const reportRules = {
  alarmType: [{ required: true, message: '请选择告警类型', trigger: 'change' }],
  urgency: [{ required: true, message: '请选择紧急程度', trigger: 'change' }],
  description: [{ required: true, message: '请填写异常描述', trigger: 'blur' }],
}
const openReport = (cam: any) => {
  Object.assign(reportForm, {
    cameraId: cam?.id || '',
    cameraName: cam?.name || '（回放视频）',
    alarmType: '',
    urgency: 'medium',
    description: '',
  })
  reportVisible.value = true
}
const submitReport = async () => {
  await reportFormRef.value?.validate()
  await reportSecurityIncident(reportForm)
  ElMessage.success('上报成功，工单已创建')
  reportVisible.value = false
}

// ─── 生命周期 ─────────────────────────────────────────────────────────────────
onMounted(() => {
  fetchCameras()
})

onBeforeUnmount(() => {
  clearInterval(progressTimer)
  players.value.forEach((p) => p?.destroy?.())
  players.value.clear()
  playbackPlayer?.destroy()
})
</script>

<style lang="scss" scoped>
.security-monitor {
  height: 100%;

  .live-toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
    padding: 8px 0;
    border-bottom: 1px solid var(--el-border-color-lighter);

    .grid-btns {
      display: flex;
      gap: 6px;
    }
  }

  .video-grid {
    flex: 1;
    display: grid;
    gap: 4px;
    overflow: hidden;

    &.grid-1 {
      grid-template-columns: 1fr;
      grid-template-rows: 1fr;
    }
    &.grid-4 {
      grid-template-columns: repeat(2, 1fr);
      grid-template-rows: repeat(2, 1fr);
    }
    &.grid-9 {
      grid-template-columns: repeat(3, 1fr);
      grid-template-rows: repeat(3, 1fr);
    }
    &.grid-16 {
      grid-template-columns: repeat(4, 1fr);
      grid-template-rows: repeat(4, 1fr);
    }
  }

  .video-cell {
    background: #1a1a1a;
    border: 2px solid #333;
    border-radius: 4px;
    position: relative;
    overflow: hidden;
    cursor: pointer;

    &.selected {
      border-color: var(--el-color-primary);
    }

    .video-label {
      position: absolute;
      top: 4px;
      left: 6px;
      z-index: 10;
      color: #fff;
      font-size: 12px;
      background: rgba(0, 0, 0, 0.5);
      padding: 2px 6px;
      border-radius: 2px;
    }

    .video-actions {
      position: absolute;
      bottom: 4px;
      left: 0;
      right: 0;
      z-index: 10;
      display: flex;
      justify-content: center;
      gap: 8px;
      opacity: 0;
      transition: opacity 0.2s;
      background: rgba(0, 0, 0, 0.5);
      padding: 4px 0;
    }

    &:hover .video-actions {
      opacity: 1;
    }
  }

  .jessibuca-container {
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
  }

  .empty-cell {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #666;
    gap: 8px;

    .empty-hint {
      font-size: 12px;
      text-align: center;
      padding: 0 12px;
    }
  }

  .playback-player {
    height: 100%;
    background: #000;
    border-radius: 4px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .playback-controls {
    display: flex;
    gap: 8px;
    justify-content: center;
  }

  .cam-pick-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    cursor: pointer;
    border-radius: 4px;
    font-size: 13px;

    &:hover {
      background: var(--el-fill-color-light);
    }
  }
}
</style>
<template>
  <div class="security-patrol no-background-container">
    <el-row :gutter="16" style="height: calc(100vh - 120px)">
      <!-- 左侧：路线/计划 -->
      <el-col :span="7" style="height: 100%; display: flex; flex-direction: column; gap: 12px">
        <!-- 巡更路线 -->
        <vab-card style="flex: 1; overflow: auto">
          <template #header>
            <span>巡更路线</span>
            <el-button style="float: right" size="small" :icon="Plus" type="primary" @click="openRouteEdit({})">新增</el-button>
          </template>
          <div v-loading="routeLoading">
            <div
              v-for="route in routeList"
              :key="route.id"
              class="route-item"
              :class="{ active: selectedRoute?.id === route.id }"
              @click="selectedRoute = route"
            >
              <div class="route-name">{{ route.name }}</div>
              <div class="route-desc">{{ route.description }}</div>
              <div class="route-meta">
                <el-tag size="small" :type="route.status === 'active' ? 'success' : 'info'">
                  {{ route.status === 'active' ? '启用' : '停用' }}
                </el-tag>
                <span style="margin-left: 8px; font-size: 12px; color: #999">{{ route.cameraIds?.length || 0 }} 个摄像头</span>
              </div>
              <div class="route-actions">
                <el-button link size="small" @click.stop="openRouteEdit(route)">编辑</el-button>
                <el-button link size="small" type="danger" @click.stop="deleteRoute(route)">删除</el-button>
              </div>
            </div>
            <el-empty v-if="!routeList.length" description="暂无路线" />
          </div>
        </vab-card>

        <!-- 巡更计划 -->
        <vab-card style="flex: 1; overflow: auto">
          <template #header>
            <span>巡更计划</span>
            <el-button style="float: right" size="small" :icon="Plus" type="primary" @click="openPlanEdit({})">新增</el-button>
          </template>
          <div v-loading="planLoading">
            <div v-for="plan in planList" :key="plan.id" class="route-item">
              <div class="route-name">{{ plan.name }}</div>
              <div class="route-desc">{{ plan.routeName }} | 间隔 {{ plan.intervalMin }} 分钟</div>
              <div class="route-meta">
                <el-tag size="small" :type="plan.status === 'active' ? 'success' : 'info'">
                  {{ plan.status === 'active' ? '启用' : '停用' }}
                </el-tag>
                <span style="margin-left: 8px; font-size: 12px; color: #999">{{ plan.startTime }}–{{ plan.endTime }}</span>
              </div>
              <div class="route-actions">
                <el-button link size="small" @click.stop="openPlanEdit(plan)">编辑</el-button>
                <el-button link size="small" type="danger" @click.stop="deletePlan(plan)">删除</el-button>
              </div>
            </div>
            <el-empty v-if="!planList.length" description="暂无计划" />
          </div>
        </vab-card>
      </el-col>

      <!-- 右侧：巡更任务 -->
      <el-col :span="17" style="height: 100%">
        <vab-card style="height: 100%">
          <template #header>
            <span>巡更任务</span>
            <el-button style="float: right" :icon="Plus" type="primary" @click="openTaskCreate">创建任务</el-button>
          </template>
          <vab-query-form>
            <vab-query-form-top-panel>
              <el-form inline :model="taskQuery" @submit.prevent>
                <el-form-item label="状态">
                  <el-select v-model="taskQuery.status" clearable placeholder="全部">
                    <el-option label="待执行" value="pending" />
                    <el-option label="执行中" value="in_progress" />
                    <el-option label="已完成" value="completed" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button :icon="Search" type="primary" @click="fetchTasks">查询</el-button>
                </el-form-item>
              </el-form>
            </vab-query-form-top-panel>
          </vab-query-form>

          <el-table v-loading="taskLoading" border :data="taskList">
            <el-table-column label="巡更计划" prop="planName" min-width="120" />
            <el-table-column label="巡更路线" prop="routeName" min-width="120" />
            <el-table-column label="执行人" prop="executor" width="100" />
            <el-table-column label="开始时间" prop="startTime" min-width="160" />
            <el-table-column label="结束时间" min-width="160">
              <template #default="{ row }">{{ row.endTime || '—' }}</template>
            </el-table-column>
            <el-table-column label="完成进度" width="150">
              <template #default="{ row }">
                <el-progress :percentage="row.progress" :status="row.progress === 100 ? 'success' : ''" />
              </template>
            </el-table-column>
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="{ pending: 'info', in_progress: 'warning', completed: 'success' }[row.status]">
                  {{ { pending: '待执行', in_progress: '执行中', completed: '已完成' }[row.status] }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="异常" width="70">
              <template #default="{ row }">
                <el-badge v-if="row.anomalyCount > 0" :value="row.anomalyCount" type="danger">
                  <el-button link type="danger" size="small">查看</el-button>
                </el-badge>
                <span v-else style="color: #999; font-size: 12px">无</span>
              </template>
            </el-table-column>
            <template #empty><el-empty description="暂无任务" /></template>
          </el-table>
        </vab-card>
      </el-col>
    </el-row>

    <!-- 路线 Dialog -->
    <el-dialog v-model="routeEditVisible" :title="routeForm.id ? '编辑路线' : '新增路线'" width="500px">
      <el-form ref="routeFormRef" label-width="90px" :model="routeForm">
        <el-form-item label="路线名称" :rules="[{ required: true, message: '必填' }]" prop="name">
          <el-input v-model="routeForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="routeForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="摄像头">
          <el-select v-model="routeForm.cameraIds" multiple style="width: 100%">
            <el-option v-for="c in cameraOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="routeForm.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="routeEditVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRoute">保存</el-button>
      </template>
    </el-dialog>

    <!-- 计划 Dialog -->
    <el-dialog v-model="planEditVisible" :title="planForm.id ? '编辑计划' : '新增计划'" width="500px">
      <el-form ref="planFormRef" label-width="90px" :model="planForm">
        <el-form-item label="计划名称" :rules="[{ required: true }]" prop="name">
          <el-input v-model="planForm.name" />
        </el-form-item>
        <el-form-item label="关联路线" :rules="[{ required: true }]" prop="routeId">
          <el-select v-model="planForm.routeId" style="width: 100%">
            <el-option v-for="r in routeList" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="巡更时间">
          <el-time-picker v-model="planForm.startTime" format="HH:mm" value-format="HH:mm" placeholder="开始时间" style="width: 46%" />
          <span style="margin: 0 6px">—</span>
          <el-time-picker v-model="planForm.endTime" format="HH:mm" value-format="HH:mm" placeholder="结束时间" style="width: 46%" />
        </el-form-item>
        <el-form-item label="巡更间隔">
          <el-input-number v-model="planForm.intervalMin" :min="10" :step="10" />
          <span style="margin-left: 8px">分钟</span>
        </el-form-item>
        <el-form-item label="重复日期">
          <el-checkbox-group v-model="planForm.weekDays">
            <el-checkbox v-for="(d, i) in ['一', '二', '三', '四', '五', '六', '日']" :key="i + 1" :value="i + 1">{{ d }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planEditVisible = false">取消</el-button>
        <el-button type="primary" @click="savePlan">保存</el-button>
      </template>
    </el-dialog>

    <!-- 创建任务 Dialog -->
    <el-dialog v-model="taskCreateVisible" title="创建巡更任务" width="400px">
      <el-form ref="taskFormRef" label-width="90px" :model="taskForm">
        <el-form-item label="关联计划" :rules="[{ required: true }]" prop="planId">
          <el-select v-model="taskForm.planId" style="width: 100%">
            <el-option v-for="p in planList" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行人" :rules="[{ required: true }]" prop="executor">
          <el-input v-model="taskForm.executor" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskCreateVisible = false">取消</el-button>
        <el-button type="primary" @click="createTask">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import {
  getPatrolRouteList,
  doEditPatrolRoute,
  doDeletePatrolRoute,
  getPatrolPlanList,
  doEditPatrolPlan,
  doDeletePatrolPlan,
  getPatrolTaskList,
  doCreatePatrolTask,
  getCameraList,
} from '/@/api/security'

defineOptions({ name: 'SecurityPatrol' })

const routeLoading = ref(false)
const planLoading = ref(false)
const taskLoading = ref(false)
const routeList = ref<any[]>([])
const planList = ref<any[]>([])
const taskList = ref<any[]>([])
const cameraOptions = ref<any[]>([])
const selectedRoute = ref<any>(null)
const taskQuery = reactive({ status: '' })

const fetchAll = async () => {
  routeLoading.value = true
  const [r, p, t, c] = await Promise.all([getPatrolRouteList(), getPatrolPlanList(), getPatrolTaskList(), getCameraList()])
  routeList.value = r.data?.list || []
  planList.value = p.data?.list || []
  taskList.value = t.data?.list || []
  cameraOptions.value = Array.isArray(c.data) ? c.data : c.data?.list || []
  routeLoading.value = false
}

const fetchTasks = async () => {
  taskLoading.value = true
  const { data } = await getPatrolTaskList(taskQuery)
  taskList.value = data?.list || []
  taskLoading.value = false
}

// 路线
const routeEditVisible = ref(false)
const routeFormRef = ref<any>()
const routeForm = reactive<any>({ id: '', name: '', description: '', cameraIds: [], status: 'active' })
const openRouteEdit = (row: any) => {
  Object.assign(routeForm, { id: '', name: '', description: '', cameraIds: [], status: 'active', ...row })
  routeEditVisible.value = true
}
const saveRoute = async () => {
  await routeFormRef.value?.validate()
  await doEditPatrolRoute(routeForm)
  ElMessage.success('保存成功')
  routeEditVisible.value = false
  fetchAll()
}
const deleteRoute = (row: any) => {
  ElMessageBox.confirm(`确定删除路线「${row.name}」?`, '提示', { type: 'warning' }).then(async () => {
    await doDeletePatrolRoute({ id: row.id })
    ElMessage.success('删除成功')
    fetchAll()
  })
}

// 计划
const planEditVisible = ref(false)
const planFormRef = ref<any>()
const planForm = reactive<any>({
  id: '',
  name: '',
  routeId: '',
  startTime: '08:00',
  endTime: '17:00',
  intervalMin: 120,
  weekDays: [1, 2, 3, 4, 5],
})
const openPlanEdit = (row: any) => {
  Object.assign(planForm, {
    id: '',
    name: '',
    routeId: '',
    startTime: '08:00',
    endTime: '17:00',
    intervalMin: 120,
    weekDays: [1, 2, 3, 4, 5],
    ...row,
  })
  planEditVisible.value = true
}
const savePlan = async () => {
  await planFormRef.value?.validate()
  await doEditPatrolPlan(planForm)
  ElMessage.success('保存成功')
  planEditVisible.value = false
  fetchAll()
}
const deletePlan = (row: any) => {
  ElMessageBox.confirm(`确定删除计划「${row.name}」?`, '提示', { type: 'warning' }).then(async () => {
    await doDeletePatrolPlan({ id: row.id })
    ElMessage.success('删除成功')
    fetchAll()
  })
}

// 任务
const taskCreateVisible = ref(false)
const taskFormRef = ref<any>()
const taskForm = reactive<any>({ planId: '', executor: '' })
const openTaskCreate = () => {
  Object.assign(taskForm, { planId: '', executor: '' })
  taskCreateVisible.value = true
}
const createTask = async () => {
  await taskFormRef.value?.validate()
  await doCreatePatrolTask(taskForm)
  ElMessage.success('任务创建成功')
  taskCreateVisible.value = false
  fetchTasks()
}

onMounted(fetchAll)
</script>

<style lang="scss" scoped>
.route-item {
  padding: 10px 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover,
  &.active {
    border-color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }

  .route-name {
    font-weight: 600;
    font-size: 14px;
  }
  .route-desc {
    font-size: 12px;
    color: #999;
    margin: 2px 0;
  }
  .route-meta {
    display: flex;
    align-items: center;
    margin-top: 4px;
  }
  .route-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 4px;
  }
}
</style>
<template>
  <div class="security-zone-container table-auto-height">
    <vab-query-form>
      <vab-query-form-left-panel>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增分区</el-button>
      </vab-query-form-left-panel>
      <vab-query-form-right-panel>
        <el-form inline :model="queryForm" @submit.prevent>
          <el-form-item label="关键字">
            <el-input v-model="queryForm.keyword" clearable placeholder="分区名称/空间" @keyup.enter="fetchData" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="Search" @click="fetchData">查询</el-button>
          </el-form-item>
        </el-form>
      </vab-query-form-right-panel>
    </vab-query-form>

    <el-table v-loading="listLoading" border :data="list">
      <el-table-column align="center" label="序号" type="index" width="60" />
      <el-table-column label="分区名称" prop="name" min-width="130" />
      <el-table-column label="空间范围" min-width="180">
        <template #default="{ row }">
          <el-tag v-for="s in row.scope" :key="s" size="small" style="margin-right: 4px; margin-bottom: 2px">
            {{ s }}
          </el-tag>
          <span v-if="!row.scope || row.scope.length === 0">--</span>
        </template>
      </el-table-column>
      <el-table-column label="关联设备" min-width="180">
        <template #default="{ row }">
          <el-tag v-for="d in row.devices" :key="d" size="small" style="margin-right: 4px; margin-bottom: 2px">
            {{ d }}
          </el-tag>
          <span v-if="!row.devices || row.devices.length === 0">--</span>
        </template>
      </el-table-column>
      <el-table-column label="分发岗位" min-width="150">
        <template #default="{ row }">
          <el-tag v-for="r in row.dispatchRoles" :key="r" size="small" style="margin-right: 4px; margin-bottom: 2px">
            {{ r }}
          </el-tag>
          <span v-if="!row.dispatchRoles || row.dispatchRoles.length === 0">--</span>
        </template>
      </el-table-column>
      <el-table-column label="分发人员" min-width="150">
        <template #default="{ row }">
          <el-tag v-for="u in row.dispatchUsers" :key="u" size="small" style="margin-right: 4px; margin-bottom: 2px">
            {{ u }}
          </el-tag>
          <span v-if="!row.dispatchUsers || row.dispatchUsers.length === 0">--</span>
        </template>
      </el-table-column>
      <el-table-column label="启用" width="70" align="center">
        <template #default="{ row }">
          <el-switch v-model="row.enabled" @change="() => toggleEnabled(row)" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="primary" @click="openWhitelist(row)">临时白名单</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
      <template #empty>
        <el-empty class="vab-data-empty" description="暂无分区数据" />
      </template>
    </el-table>

    <el-pagination
      background
      :current-page="queryForm.pageNo"
      layout="total, sizes, prev, pager, next, jumper"
      :page-size="queryForm.pageSize"
      :total="total"
      @current-change="
        (v) => {
          queryForm.pageNo = v
          fetchData()
        }
      "
      @size-change="
        (v) => {
          queryForm.pageSize = v
          queryForm.pageNo = 1
          fetchData()
        }
      "
    />

    <!-- Add / Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑分区' : '新增分区'" width="700px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="分区名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分区名称" />
        </el-form-item>
        <el-form-item label="空间范围" prop="scope">
          <el-select v-model="form.scope" multiple placeholder="请选择空间范围（楼栋/楼层）" style="width: 100%">
            <el-option v-for="item in mockBuildings" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联设备" prop="devices">
          <el-select v-model="form.devices" multiple placeholder="请选择关联设备" style="width: 100%">
            <el-option v-for="item in mockDevices" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="分发岗位" prop="dispatchRoles">
          <el-select v-model="form.dispatchRoles" multiple placeholder="请选择分发岗位" style="width: 100%">
            <el-option v-for="item in mockRoles" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="分发人员" prop="dispatchUsers">
          <el-select
            v-model="form.dispatchUsers"
            multiple
            filterable
            remote
            :remote-method="searchUsers"
            placeholder="搜索并选择分发人员"
            style="width: 100%"
          >
            <el-option v-for="item in filteredUsers" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>

    <!-- Temporary Whitelist Sub-dialog -->
    <el-dialog v-model="whitelistVisible" :title="`临时白名单 - ${currentZone?.name || ''}`" width="650px" destroy-on-close>
      <el-table border :data="whitelistData" style="margin-bottom: 16px">
        <el-table-column label="姓名" prop="name" min-width="100" />
        <el-table-column label="类型" prop="type" width="100" />
        <el-table-column label="生效时间" prop="validFrom" width="150" />
        <el-table-column label="过期时间" prop="validTo" width="150" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row, $index }">
            <el-button link type="danger" @click="removeWhitelistItem($index)">移除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty class="vab-data-empty" description="暂无白名单" />
        </template>
      </el-table>

      <el-divider />

      <div class="whitelist-add-section">
        <span class="whitelist-add-title">添加白名单</span>
        <el-form inline :model="whitelistForm" @submit.prevent>
          <el-form-item label="姓名">
            <el-input v-model="whitelistForm.name" placeholder="人员姓名" style="width: 130px" />
          </el-form-item>
          <el-form-item label="类型">
            <el-select v-model="whitelistForm.type" placeholder="类型" style="width: 110px">
              <el-option label="访客" value="访客" />
              <el-option label="临时工" value="临时工" />
              <el-option label="供应商" value="供应商" />
            </el-select>
          </el-form-item>
          <el-form-item label="有效日期">
            <el-date-picker
              v-model="whitelistForm.validRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始"
              end-placeholder="结束"
              value-format="YYYY-MM-DD"
              style="width: 240px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="addWhitelistItem">添加</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { Search, Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'SecurityZone' })

const $baseMessage = inject<any>('$baseMessage')
const $baseConfirm = inject<any>('$baseConfirm')

const mock = (data: any) => new Promise<any>((r) => setTimeout(() => r({ code: '200', msg: 'success', data }), 300))

// ---- Mock data pools ----

const mockBuildings = [
  { value: '1号楼-1F', label: '1号楼-1F' },
  { value: '1号楼-2F', label: '1号楼-2F' },
  { value: '1号楼-3F', label: '1号楼-3F' },
  { value: '1号楼-B1', label: '1号楼-B1' },
  { value: '2号楼-1F', label: '2号楼-1F' },
  { value: '2号楼-2F', label: '2号楼-2F' },
  { value: '2号楼-3F', label: '2号楼-3F' },
  { value: '3号楼-1F', label: '3号楼-1F' },
  { value: '3号楼-2F', label: '3号楼-2F' },
  { value: '3号楼-3F', label: '3号楼-3F' },
  { value: '3号楼-4F', label: '3号楼-4F' },
  { value: '3号楼-5F', label: '3号楼-5F' },
  { value: '3号楼-6F', label: '3号楼-6F' },
  { value: '3号楼-7F', label: '3号楼-7F' },
  { value: '3号楼-8F', label: '3号楼-8F' },
  { value: '3号楼-9F', label: '3号楼-9F' },
  { value: '3号楼-10F', label: '3号楼-10F' },
]

const mockDevices = [
  { value: '半球摄像机-1F-01', label: '半球摄像机-1F-01' },
  { value: '半球摄像机-1F-02', label: '半球摄像机-1F-02' },
  { value: '半球摄像机-2F-01', label: '半球摄像机-2F-01' },
  { value: '枪式摄像机-B1-01', label: '枪式摄像机-B1-01' },
  { value: '球型摄像机-Lobby-01', label: '球型摄像机-Lobby-01' },
  { value: '门磁-1F-主入口', label: '门磁-1F-主入口' },
  { value: '门磁-2F-东侧', label: '门磁-2F-东侧' },
  { value: '红外探测-B1-01', label: '红外探测-B1-01' },
  { value: '红外探测-1F-02', label: '红外探测-1F-02' },
  { value: '烟感探测器-1F-03', label: '烟感探测器-1F-03' },
]

const mockRoles = [
  { value: '保安队长', label: '保安队长' },
  { value: '值班员', label: '值班员' },
  { value: '监控员', label: '监控员' },
]

const mockUserPool = [
  { value: '张三', label: '张三' },
  { value: '李四', label: '李四' },
  { value: '王五', label: '王五' },
  { value: '赵六', label: '赵六' },
  { value: '钱七', label: '钱七' },
  { value: '孙八', label: '孙八' },
  { value: '周九', label: '周九' },
  { value: '吴十', label: '吴十' },
]

// ---- Query & List ----

const queryForm = reactive({
  keyword: '',
  pageNo: 1,
  pageSize: 20,
})

const listLoading = ref(false)
const list = ref<any[]>([])
const total = ref(0)

const fetchData = async () => {
  listLoading.value = true
  const { data } = await mock([
    {
      id: '1',
      name: 'A区安防分区',
      scope: ['1号楼-1F', '1号楼-2F', '2号楼-1F'],
      devices: ['半球摄像机-1F-01', '门磁-1F-主入口'],
      dispatchRoles: ['保安队长', '监控员'],
      dispatchUsers: ['张三', '李四'],
      enabled: true,
    },
    {
      id: '2',
      name: 'B区安防分区',
      scope: ['3号楼-1F', '3号楼-2F', '3号楼-3F'],
      devices: ['球型摄像机-Lobby-01', '半球摄像机-1F-02'],
      dispatchRoles: ['值班员'],
      dispatchUsers: ['王五'],
      enabled: true,
    },
    {
      id: '3',
      name: '地下停车场分区',
      scope: ['1号楼-B1', '2号楼-B1'],
      devices: ['枪式摄像机-B1-01', '红外探测-B1-01'],
      dispatchRoles: ['保安队长', '值班员', '监控员'],
      dispatchUsers: ['张三', '王五', '赵六'],
      enabled: false,
    },
  ])
  list.value = data
  total.value = data.length
  listLoading.value = false
}

// ---- Add / Edit Dialog ----

const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref<any>(null)

const form = reactive<any>({
  id: '',
  name: '',
  scope: [],
  devices: [],
  dispatchRoles: [],
  dispatchUsers: [],
  enabled: true,
})

const rules = {
  name: [{ required: true, message: '请输入分区名称', trigger: 'blur' }],
  scope: [{ required: true, message: '请至少选择一个空间范围', trigger: 'change' }],
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(form, {
    id: '',
    name: '',
    scope: [],
    devices: [],
    dispatchRoles: [],
    dispatchUsers: [],
    enabled: true,
  })
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    name: row.name,
    scope: [...(row.scope || [])],
    devices: [...(row.devices || [])],
    dispatchRoles: [...(row.dispatchRoles || [])],
    dispatchUsers: [...(row.dispatchUsers || [])],
    enabled: row.enabled,
  })
  dialogVisible.value = true
}

const submitForm = async () => {
  await formRef.value?.validate()
  submitLoading.value = true
  await mock(null)
  submitLoading.value = false
  dialogVisible.value = false
  $baseMessage.success(isEdit.value ? '编辑成功' : '新增成功')
  fetchData()
}

const handleDelete = (row: any) => {
  $baseConfirm(`确定删除分区「${row.name}」?`, '提示', { type: 'warning' }).then(async () => {
    await mock(null)
    $baseMessage.success('删除成功')
    fetchData()
  })
}

const toggleEnabled = async (row: any) => {
  await mock(null)
  $baseMessage.success(row.enabled ? '已启用' : '已停用')
}

// ---- Remote user search ----

const filteredUsers = ref<{ value: string; label: string }[]>([...mockUserPool])

const searchUsers = (query: string) => {
  if (!query) {
    filteredUsers.value = [...mockUserPool]
    return
  }
  filteredUsers.value = mockUserPool.filter((u) => u.value.includes(query))
}

// ---- Whitelist sub-dialog ----

const whitelistVisible = ref(false)
const currentZone = ref<any>(null)
const whitelistData = ref<any[]>([])

const whitelistForm = reactive({
  name: '',
  type: '访客',
  validRange: [] as string[],
})

const openWhitelist = (row: any) => {
  currentZone.value = row
  whitelistData.value = [
    { name: '刘工', type: '供应商', validFrom: '2026-07-01', validTo: '2026-07-15' },
    { name: '陈师傅', type: '临时工', validFrom: '2026-07-10', validTo: '2026-07-12' },
    { name: '林小姐', type: '访客', validFrom: '2026-07-08', validTo: '2026-07-09' },
  ]
  whitelistVisible.value = true
}

const addWhitelistItem = () => {
  if (!whitelistForm.name || !whitelistForm.type || !whitelistForm.validRange?.length) {
    $baseMessage.warning('请填写完整白名单信息')
    return
  }
  whitelistData.value.push({
    name: whitelistForm.name,
    type: whitelistForm.type,
    validFrom: whitelistForm.validRange[0],
    validTo: whitelistForm.validRange[1],
  })
  whitelistForm.name = ''
  whitelistForm.validRange = []
  $baseMessage.success('添加成功')
}

const removeWhitelistItem = (index: number) => {
  whitelistData.value.splice(index, 1)
  $baseMessage.success('已移除')
}

onBeforeMount(fetchData)
</script>

```
