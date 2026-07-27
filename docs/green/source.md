# 源代码提交页（智能楼宇智能绿色能源管理系统 buildingos.green）

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

import { EnergyMeterEntity } from './entities/energy-meter.entity';
import { EnergyReadingEntity } from './entities/energy-reading.entity';
import { EnergyAlarmConfigEntity } from './entities/energy-alarm-config.entity';
import { EnergyAlarmEntity } from './entities/energy-alarm.entity';
import { EnergyPriceEntity } from './entities/energy-price.entity';
import { EnergyElecConfigEntity } from './entities/energy-elec-config.entity';
import { CarbonTransactionEntity } from './entities/carbon-transaction.entity';
import { CarbonFootprintEntity } from './entities/carbon-footprint.entity';
import { CarbonDecisionEntity } from './entities/carbon-decision.entity';

import { CollectService } from './services/collect.service';
import { MonitorService } from './services/monitor.service';
import { LedgerService } from './services/ledger.service';
import { PriceService } from './services/price.service';
import { CarbonService } from './services/carbon.service';

import { EnergyController } from './energy.controller';
import { EnergyMqttController } from './energy.mqtt.controller';
import { CollectController } from './controllers/collect.controller';
import { MonitorController } from './controllers/monitor.controller';
import { LedgerController } from './controllers/ledger.controller';
import { PriceController } from './controllers/price.controller';
import { CarbonController } from './controllers/carbon.controller';

import { HostBridge } from './integration/host-bridge.service';

const ALL_ENTITIES = [
  EnergyMeterEntity,
  EnergyReadingEntity,
  EnergyAlarmConfigEntity,
  EnergyAlarmEntity,
  EnergyPriceEntity,
  EnergyElecConfigEntity,
  CarbonTransactionEntity,
  CarbonFootprintEntity,
  CarbonDecisionEntity,
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
          database: 'apps/energy/data/energy.sqlite',
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
              'buildingos_microservice_energy_' +
              Math.random().toString(16).slice(2, 8),
          },
        }),
      },
    ]),
  ],
  controllers: [
    EnergyController,
    EnergyMqttController,
    CollectController,
    MonitorController,
    LedgerController,
    PriceController,
    CarbonController,
  ],
  providers: [
    CollectService,
    MonitorService,
    LedgerService,
    PriceService,
    CarbonService,
    HostBridge,
  ],
})
export class AppModule {}

import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as swagger from '@nestjs/swagger';
import { Transport, MicroserviceOptions } from '@nestjs/microservices';
import { Logger } from '@nestjs/common';

async function bootstrap() {
  const logger = new Logger('EnergyBootstrap');
  const app = await NestFactory.create(AppModule);
  app.setGlobalPrefix('energy');
  app.enableCors();

  try {
    const url = process.env.MQTT_BROKER_URL;
    if (url) {
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
    .setTitle('Energy API')
    .setDescription('能耗管理微服务接口文档')
    .setVersion('1.0')
    .addBearerAuth()
    .build();
  const doc = swagger.SwaggerModule.createDocument(app, config);
  swagger.SwaggerModule.setup('energy/docs', app, doc);

  const port = parseInt(process.env.PORT || '3016', 10);
  await app.listen(port);
  logger.log(`Energy service running on port ${port}`);
}
void bootstrap();

import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';

@ApiTags('健康检查')
@Controller()
export class EnergyController {
  @Get('health')
  @ApiOperation({ summary: '健康检查' })
  health() {
    return { status: 'ok', service: 'energy' };
  }

  @Get('menu.json')
  @ApiOperation({ summary: '菜单配置' })
  menuJson() {
    return require('../menu.json');
  }
}

import { Controller, Logger } from '@nestjs/common';
import { MessagePattern, Payload } from '@nestjs/microservices';

@Controller()
export class EnergyMqttController {
  private readonly logger = new Logger(EnergyMqttController.name);

  @MessagePattern('energy/#')
  handle(@Payload() data: unknown) {
    this.logger.debug(`MQTT energy/#: ${JSON.stringify(data)}`);
    return { code: 200, data };
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

import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';

@Entity('energy_meter')
export class EnergyMeterEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ length: 100 })
  name!: string;

  @Column({ name: 'meter_no', length: 50, nullable: true })
  meterNo?: string;

  @Column({ name: 'energy_type', length: 20 })
  energyType!: string;

  @Column({ length: 100, nullable: true })
  building?: string;

  @Column({ length: 50, nullable: true })
  floor?: string;

  @Column({ length: 100, nullable: true })
  area?: string;

  @Column({ length: 100, nullable: true })
  branch?: string;

  @Column({ name: 'site_name', length: 100, nullable: true })
  siteName?: string;

  @Column({ name: 'device_id', length: 36, nullable: true })
  deviceId?: string;

  @Column({ length: 20, nullable: true })
  unit?: string;

  @Column({ name: 'install_date', nullable: true })
  installDate?: Date;

  @Column({ length: 20, default: 'active' })
  status!: string;

  @Column({ length: 200, nullable: true })
  remark?: string;

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
} from 'typeorm';

@Entity('energy_reading')
export class EnergyReadingEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ name: 'meter_id', length: 36, nullable: true })
  meterId?: string;

  @Column({ name: 'meter_no', length: 50, nullable: true })
  meterNo?: string;

  @Column({ name: 'meter_name', length: 100, nullable: true })
  meterName?: string;

  @Column({ name: 'energy_type', length: 20 })
  energyType!: string;

  @Column({ type: 'float', default: 0 })
  value!: number;

  @Column({ length: 20, nullable: true })
  unit?: string;

  @Column({ name: 'read_time', nullable: true })
  readTime?: Date;

  @Column({ nullable: true })
  year?: number;

  @Column({ nullable: true })
  month?: number;

  @Column({ nullable: true })
  day?: number;

  @Column({ name: 'sub_item', length: 50, nullable: true })
  subItem?: string;

  @Column({ name: 'is_manual', default: false })
  isManual!: boolean;

  @Column({ length: 200, nullable: true })
  remark?: string;

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

@Entity('energy_alarm_config')
export class EnergyAlarmConfigEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ name: 'meter_id', length: 36, nullable: true })
  meterId?: string;

  @Column({ name: 'meter_name', length: 100, nullable: true })
  meterName?: string;

  @Column({ name: 'energy_type', length: 20, nullable: true })
  energyType?: string;

  @Column({ type: 'float', nullable: true })
  threshold?: number;

  @Column({ length: 20, default: 'day' })
  period!: string;

  @Column({ default: true })
  enabled!: boolean;

  @Column({ name: 'notify_user', length: 200, nullable: true })
  notifyUser?: string;

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
} from 'typeorm';

@Entity('energy_alarm')
export class EnergyAlarmEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ name: 'meter_id', length: 36, nullable: true })
  meterId?: string;

  @Column({ name: 'meter_name', length: 100, nullable: true })
  meterName?: string;

  @Column({ name: 'energy_type', length: 20, nullable: true })
  energyType?: string;

  @Column({ type: 'float', nullable: true })
  value?: number;

  @Column({ type: 'float', nullable: true })
  threshold?: number;

  @Column({ name: 'alarm_time', nullable: true })
  alarmTime?: Date;

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

@Entity('energy_price')
export class EnergyPriceEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ name: 'energy_type', length: 20 })
  energyType!: string;

  @Column({ length: 10, nullable: true })
  month?: string;

  @Column({ name: 'tier1_limit', type: 'float', nullable: true })
  tier1Limit?: number;

  @Column({ name: 'tier1_price', type: 'float', nullable: true })
  tier1Price?: number;

  @Column({ name: 'tier2_limit', type: 'float', nullable: true })
  tier2Limit?: number;

  @Column({ name: 'tier2_price', type: 'float', nullable: true })
  tier2Price?: number;

  @Column({ name: 'tier3_price', type: 'float', nullable: true })
  tier3Price?: number;

  @Column({ length: 20, nullable: true })
  unit?: string;

  @Column({ length: 200, nullable: true })
  remark?: string;

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

@Entity('energy_elec_config')
export class EnergyElecConfigEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ name: 'branch_name', length: 100 })
  branchName!: string;

  @Column({ name: 'sharp_start', length: 10, nullable: true })
  sharpStart?: string;

  @Column({ name: 'sharp_end', length: 10, nullable: true })
  sharpEnd?: string;

  @Column({ name: 'sharp_price', type: 'float', nullable: true })
  sharpPrice?: number;

  @Column({ name: 'peak_start', length: 10, nullable: true })
  peakStart?: string;

  @Column({ name: 'peak_end', length: 10, nullable: true })
  peakEnd?: string;

  @Column({ name: 'peak_price', type: 'float', nullable: true })
  peakPrice?: number;

  @Column({ name: 'flat_start', length: 10, nullable: true })
  flatStart?: string;

  @Column({ name: 'flat_end', length: 10, nullable: true })
  flatEnd?: string;

  @Column({ name: 'flat_price', type: 'float', nullable: true })
  flatPrice?: number;

  @Column({ name: 'valley_start', length: 10, nullable: true })
  valleyStart?: string;

  @Column({ name: 'valley_end', length: 10, nullable: true })
  valleyEnd?: string;

  @Column({ name: 'valley_price', type: 'float', nullable: true })
  valleyPrice?: number;

  @Column({ name: 'monthly_limit', type: 'float', nullable: true })
  monthlyLimit?: number;

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

@Entity('energy_carbon_transaction')
export class CarbonTransactionEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ length: 100, nullable: true })
  building?: string;

  @Column({ name: 'trade_time', nullable: true })
  tradeTime?: Date;

  @Column({ name: 'effect_time', nullable: true })
  effectTime?: Date;

  @Column({ name: 'purchase_type', length: 50, nullable: true })
  purchaseType?: string;

  @Column({ name: 'carbon_amount', type: 'float', nullable: true })
  carbonAmount?: number;

  @Column({ name: 'trade_platform', length: 100, nullable: true })
  tradePlatform?: string;

  @Column({ length: 20, default: 'completed' })
  status!: string;

  @Column({ length: 500, nullable: true })
  remark?: string;

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

@Entity('energy_carbon_footprint')
export class CarbonFootprintEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ length: 100, nullable: true })
  building?: string;

  @Column({ name: 'product_name', length: 100, nullable: true })
  productName?: string;

  @Column({ name: 'carbon_amount', type: 'float', nullable: true })
  carbonAmount?: number;

  @Column({ name: 'per_product_carbon', type: 'float', nullable: true })
  perProductCarbon?: number;

  @Column({ length: 20, nullable: true })
  unit?: string;

  @Column({ name: 'product_start_time', nullable: true })
  productStartTime?: Date;

  @Column({ name: 'product_end_time', nullable: true })
  productEndTime?: Date;

  @Column({ name: 'check_start_time', nullable: true })
  checkStartTime?: Date;

  @Column({ name: 'check_end_time', nullable: true })
  checkEndTime?: Date;

  @Column({ length: 200, nullable: true })
  conclusion?: string;

  @Column({ length: 500, nullable: true })
  remark?: string;

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

@Entity('energy_carbon_decision')
export class CarbonDecisionEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ length: 100, nullable: true })
  building?: string;

  @Column({ name: 'energy_consumption', type: 'float', nullable: true })
  energyConsumption?: number;

  @Column({ name: 'investment_value', type: 'float', nullable: true })
  investmentValue?: number;

  @Column({ name: 'energy_saving_rate', type: 'float', nullable: true })
  energySavingRate?: number;

  @Column({ name: 'energy_saving_amount', type: 'float', nullable: true })
  energySavingAmount?: number;

  @Column({ name: 'carbon_reduction_amount', type: 'float', nullable: true })
  carbonReductionAmount?: number;

  @Column({ length: 500, nullable: true })
  remark?: string;

  @CreateDateColumn({ name: 'create_time' })
  createTime!: Date;

  @UpdateDateColumn({ name: 'update_time' })
  updateTime!: Date;
}

import { Controller, Get, Post, Body, Query } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { CollectService } from '../services/collect.service';
import {
  QueryMeterDto,
  MeterEditDto,
  QueryReadingDto,
  ReadingEditDto,
  DeleteDto,
} from '../dto/collect.dto';

@ApiTags('能耗采集')
@Controller('collect')
export class CollectController {
  constructor(private readonly svc: CollectService) {}

  @Get('meterList')
  @ApiOperation({ summary: '能耗表计列表' })
  async meterList(@Query() query: QueryMeterDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getMeterList(query),
    };
  }

  @Post('meterEdit')
  @ApiOperation({ summary: '新增/编辑表计' })
  async meterEdit(@Body() dto: MeterEditDto) {
    return { code: 200, msg: 'success', data: await this.svc.editMeter(dto) };
  }

  @Post('meterDelete')
  @ApiOperation({ summary: '删除表计' })
  async meterDelete(@Body() dto: DeleteDto) {
    return { code: 200, msg: 'success', data: await this.svc.deleteMeter(dto) };
  }

  @Get('readingList')
  @ApiOperation({ summary: '用能数据列表' })
  async readingList(@Query() query: QueryReadingDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getReadingList(query),
    };
  }

  @Post('readingEdit')
  @ApiOperation({ summary: '录入用能数据' })
  async readingEdit(@Body() dto: ReadingEditDto) {
    return { code: 200, msg: 'success', data: await this.svc.editReading(dto) };
  }

  @Post('readingDelete')
  @ApiOperation({ summary: '删除用能数据' })
  async readingDelete(@Body() dto: DeleteDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.deleteReading(dto),
    };
  }
}

import { Controller, Get, Post, Body, Query, Req } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { MonitorService } from '../services/monitor.service';
import {
  QueryAlarmConfigDto,
  AlarmConfigEditDto,
  QueryAlarmDto,
  AckAlarmDto,
  QueryStatisticsDto,
  DeleteDto,
} from '../dto/monitor.dto';
import { extractUser } from '../utils/jwt.util';

@ApiTags('能耗监测')
@Controller('monitor')
export class MonitorController {
  constructor(private readonly svc: MonitorService) {}

  @Get('alarmConfigList')
  @ApiOperation({ summary: '告警配置列表' })
  async alarmConfigList(@Query() query: QueryAlarmConfigDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getAlarmConfigList(query),
    };
  }

  @Post('alarmConfigEdit')
  @ApiOperation({ summary: '新增/编辑告警配置' })
  async alarmConfigEdit(@Body() dto: AlarmConfigEditDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.editAlarmConfig(dto),
    };
  }

  @Post('alarmConfigDelete')
  @ApiOperation({ summary: '删除告警配置' })
  async alarmConfigDelete(@Body() dto: DeleteDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.deleteAlarmConfig(dto),
    };
  }

  @Get('alarmList')
  @ApiOperation({ summary: '告警列表' })
  async alarmList(@Query() query: QueryAlarmDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getAlarmList(query),
    };
  }

  @Post('ackAlarm')
  @ApiOperation({ summary: '确认/处理告警' })
  async ackAlarm(@Body() dto: AckAlarmDto, @Req() req: any) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.ackAlarm(dto, extractUser(req)),
    };
  }

  @Get('statistics')
  @ApiOperation({ summary: '用能统计' })
  async statistics(@Query() query: QueryStatisticsDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getStatistics(query),
    };
  }
}

import { Controller, Get, Post, Body, Query } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { LedgerService } from '../services/ledger.service';
import { QueryLedgerDto, LedgerEditDto, DeleteDto } from '../dto/ledger.dto';

@ApiTags('基础台账')
@Controller('ledger')
export class LedgerController {
  constructor(private readonly svc: LedgerService) {}

  @Get('list')
  @ApiOperation({ summary: '台账列表' })
  async list(@Query() query: QueryLedgerDto) {
    return { code: 200, msg: 'success', data: await this.svc.getList(query) };
  }

  @Post('edit')
  @ApiOperation({ summary: '新增/编辑台账记录' })
  async edit(@Body() dto: LedgerEditDto) {
    return { code: 200, msg: 'success', data: await this.svc.edit(dto) };
  }

  @Post('delete')
  @ApiOperation({ summary: '删除台账记录' })
  async delete(@Body() dto: DeleteDto) {
    return { code: 200, msg: 'success', data: await this.svc.delete(dto) };
  }
}

import { Controller, Get, Post, Body, Query } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { PriceService } from '../services/price.service';
import {
  QueryPriceDto,
  PriceEditDto,
  QueryElecConfigDto,
  ElecConfigEditDto,
  DeleteDto,
} from '../dto/price.dto';

@ApiTags('能耗配置')
@Controller('price')
export class PriceController {
  constructor(private readonly svc: PriceService) {}

  @Get('list')
  @ApiOperation({ summary: '水气价格配置列表' })
  async list(@Query() query: QueryPriceDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getPriceList(query),
    };
  }

  @Post('edit')
  @ApiOperation({ summary: '新增/编辑价格配置' })
  async edit(@Body() dto: PriceEditDto) {
    return { code: 200, msg: 'success', data: await this.svc.editPrice(dto) };
  }

  @Post('delete')
  @ApiOperation({ summary: '删除价格配置' })
  async delete(@Body() dto: DeleteDto) {
    return { code: 200, msg: 'success', data: await this.svc.deletePrice(dto) };
  }

  @Get('elecConfigList')
  @ApiOperation({ summary: '用电配置列表（尖峰平谷）' })
  async elecConfigList(@Query() query: QueryElecConfigDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getElecConfigList(query),
    };
  }

  @Post('elecConfigEdit')
  @ApiOperation({ summary: '新增/编辑用电配置' })
  async elecConfigEdit(@Body() dto: ElecConfigEditDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.editElecConfig(dto),
    };
  }

  @Post('elecConfigDelete')
  @ApiOperation({ summary: '删除用电配置' })
  async elecConfigDelete(@Body() dto: DeleteDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.deleteElecConfig(dto),
    };
  }
}

import { Controller, Get, Post, Body, Query } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { CarbonService } from '../services/carbon.service';
import {
  QueryCarbonOverviewDto,
  QueryTransactionDto,
  TransactionEditDto,
  QueryFootprintDto,
  FootprintEditDto,
  QueryCurveDto,
  CurveEditDto,
  QueryDecisionDto,
  DecisionEditDto,
  QueryAssetsDto,
  DeleteDto,
} from '../dto/carbon.dto';

@ApiTags('双碳管理')
@Controller('carbon')
export class CarbonController {
  constructor(private readonly svc: CarbonService) {}

  @Get('overview')
  @ApiOperation({ summary: '碳概览统计' })
  async overview(@Query() query: QueryCarbonOverviewDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getOverview(query),
    };
  }

  @Get('transactionList')
  @ApiOperation({ summary: '碳交易列表' })
  async transactionList(@Query() query: QueryTransactionDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getTransactionList(query),
    };
  }

  @Post('transactionEdit')
  @ApiOperation({ summary: '新增/编辑碳交易' })
  async transactionEdit(@Body() dto: TransactionEditDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.editTransaction(dto),
    };
  }

  @Post('transactionDelete')
  @ApiOperation({ summary: '删除碳交易' })
  async transactionDelete(@Body() dto: DeleteDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.deleteTransaction(dto),
    };
  }

  @Get('footprintList')
  @ApiOperation({ summary: '碳足迹列表' })
  async footprintList(@Query() query: QueryFootprintDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getFootprintList(query),
    };
  }

  @Post('footprintEdit')
  @ApiOperation({ summary: '新增/编辑碳足迹' })
  async footprintEdit(@Body() dto: FootprintEditDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.editFootprint(dto),
    };
  }

  @Post('footprintDelete')
  @ApiOperation({ summary: '删除碳足迹' })
  async footprintDelete(@Body() dto: DeleteDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.deleteFootprint(dto),
    };
  }

  @Get('curve')
  @ApiOperation({ summary: '双碳曲线数据' })
  curve(@Query() query: QueryCurveDto) {
    return { code: 200, msg: 'success', data: this.svc.getCurve(query) };
  }

  @Post('curveEdit')
  @ApiOperation({ summary: '设置双碳曲线参数' })
  curveEdit(@Body() dto: CurveEditDto) {
    return { code: 200, msg: 'success', data: this.svc.editCurve(dto) };
  }

  @Get('evaluation')
  @ApiOperation({ summary: '动态评价（单位面积/人均能耗）' })
  async evaluation(@Query() query: QueryCurveDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getEvaluation(query),
    };
  }

  @Get('decisionList')
  @ApiOperation({ summary: '辅助决策列表' })
  async decisionList(@Query() query: QueryDecisionDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.getDecisionList(query),
    };
  }

  @Post('decisionEdit')
  @ApiOperation({ summary: '新增/编辑辅助决策' })
  async decisionEdit(@Body() dto: DecisionEditDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.editDecision(dto),
    };
  }

  @Post('decisionDelete')
  @ApiOperation({ summary: '删除辅助决策' })
  async decisionDelete(@Body() dto: DeleteDto) {
    return {
      code: 200,
      msg: 'success',
      data: await this.svc.deleteDecision(dto),
    };
  }

  @Get('assets')
  @ApiOperation({ summary: '碳资产管理' })
  async assets(@Query() query: QueryAssetsDto) {
    return { code: 200, msg: 'success', data: await this.svc.getAssets(query) };
  }
}

import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { EnergyMeterEntity } from '../entities/energy-meter.entity';
import { EnergyReadingEntity } from '../entities/energy-reading.entity';
import {
  QueryMeterDto,
  MeterEditDto,
  QueryReadingDto,
  ReadingEditDto,
  DeleteDto,
} from '../dto/collect.dto';

@Injectable()
export class CollectService {
  private readonly logger = new Logger(CollectService.name);

  constructor(
    @InjectRepository(EnergyMeterEntity)
    private meterRepo: Repository<EnergyMeterEntity>,
    @InjectRepository(EnergyReadingEntity)
    private readingRepo: Repository<EnergyReadingEntity>,
  ) {}

  async getMeterList(query: QueryMeterDto) {
    const qb = this.meterRepo.createQueryBuilder('m');
    if (query.energyType)
      qb.andWhere('m.energy_type = :et', { et: query.energyType });
    if (query.building) qb.andWhere('m.building = :b', { b: query.building });
    if (query.floor) qb.andWhere('m.floor = :f', { f: query.floor });
    if (query.status) qb.andWhere('m.status = :s', { s: query.status });
    const list = await qb.orderBy('m.create_time', 'DESC').getMany();
    return { list, total: list.length };
  }

  async editMeter(dto: MeterEditDto) {
    const data: Partial<EnergyMeterEntity> = {
      name: dto.name,
      meterNo: dto.meterNo,
      energyType: dto.energyType,
      building: dto.building,
      floor: dto.floor,
      area: dto.area,
      branch: dto.branch,
      siteName: dto.siteName,
      deviceId: dto.deviceId,
      unit: dto.unit,
      status: dto.status ?? 'active',
      remark: dto.remark,
    };
    if (dto.installDate) data.installDate = new Date(dto.installDate);
    if (dto.id) {
      await this.meterRepo.update(dto.id, data);
      return this.meterRepo.findOneBy({ id: dto.id });
    }
    return this.meterRepo.save(this.meterRepo.create(data));
  }

  async deleteMeter(dto: DeleteDto) {
    await this.meterRepo.delete(dto.id);
    return { success: true };
  }

  async getReadingList(query: QueryReadingDto) {
    const pageNo = Number(query.pageNo) || 1;
    const pageSize = Number(query.pageSize) || 20;
    const qb = this.readingRepo.createQueryBuilder('r');
    if (query.meterId) qb.andWhere('r.meter_id = :mid', { mid: query.meterId });
    if (query.energyType)
      qb.andWhere('r.energy_type = :et', { et: query.energyType });
    if (query.year) qb.andWhere('r.year = :y', { y: query.year });
    if (query.month) qb.andWhere('r.month = :m', { m: query.month });
    if (query.startTime)
      qb.andWhere('r.read_time >= :st', { st: new Date(query.startTime) });
    if (query.endTime)
      qb.andWhere('r.read_time <= :et2', { et2: new Date(query.endTime) });
    const [list, total] = await qb
      .orderBy('r.read_time', 'DESC')
      .skip((pageNo - 1) * pageSize)
      .take(pageSize)
      .getManyAndCount();
    return { list, total };
  }

  async editReading(dto: ReadingEditDto) {
    const now = new Date();
    const data: Partial<EnergyReadingEntity> = {
      meterId: dto.meterId,
      meterNo: dto.meterNo,
      meterName: dto.meterName,
      energyType: dto.energyType,
      value: dto.value,
      unit: dto.unit,
      subItem: dto.subItem,
      isManual: dto.isManual ?? true,
      remark: dto.remark,
    };
    const d = dto.readTime ? new Date(dto.readTime) : now;
    data.readTime = d;
    data.year = d.getFullYear();
    data.month = d.getMonth() + 1;
    data.day = d.getDate();
    if (dto.id) {
      await this.readingRepo.update(dto.id, data);
      return this.readingRepo.findOneBy({ id: dto.id });
    }
    return this.readingRepo.save(this.readingRepo.create(data));
  }

  async deleteReading(dto: DeleteDto) {
    await this.readingRepo.delete(dto.id);
    return { success: true };
  }
}

import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { EnergyAlarmConfigEntity } from '../entities/energy-alarm-config.entity';
import { EnergyAlarmEntity } from '../entities/energy-alarm.entity';
import { EnergyReadingEntity } from '../entities/energy-reading.entity';
import {
  QueryAlarmConfigDto,
  AlarmConfigEditDto,
  QueryAlarmDto,
  AckAlarmDto,
  QueryStatisticsDto,
  DeleteDto,
} from '../dto/monitor.dto';

@Injectable()
export class MonitorService {
  private readonly logger = new Logger(MonitorService.name);

  constructor(
    @InjectRepository(EnergyAlarmConfigEntity)
    private configRepo: Repository<EnergyAlarmConfigEntity>,
    @InjectRepository(EnergyAlarmEntity)
    private alarmRepo: Repository<EnergyAlarmEntity>,
    @InjectRepository(EnergyReadingEntity)
    private readingRepo: Repository<EnergyReadingEntity>,
  ) {}

  async getAlarmConfigList(query: QueryAlarmConfigDto) {
    const qb = this.configRepo.createQueryBuilder('c');
    if (query.energyType)
      qb.andWhere('c.energy_type = :et', { et: query.energyType });
    const list = await qb.orderBy('c.create_time', 'DESC').getMany();
    return { list, total: list.length };
  }

  async editAlarmConfig(dto: AlarmConfigEditDto) {
    const data: Partial<EnergyAlarmConfigEntity> = {
      meterId: dto.meterId,
      meterName: dto.meterName,
      energyType: dto.energyType,
      threshold: dto.threshold,
      period: dto.period ?? 'day',
      enabled: dto.enabled ?? true,
      notifyUser: dto.notifyUser,
    };
    if (dto.id) {
      await this.configRepo.update(dto.id, data);
      return this.configRepo.findOneBy({ id: dto.id });
    }
    return this.configRepo.save(this.configRepo.create(data));
  }

  async deleteAlarmConfig(dto: DeleteDto) {
    await this.configRepo.delete(dto.id);
    return { success: true };
  }

  async getAlarmList(query: QueryAlarmDto) {
    const pageNo = Number(query.pageNo) || 1;
    const pageSize = Number(query.pageSize) || 20;
    const qb = this.alarmRepo.createQueryBuilder('a');
    if (query.energyType)
      qb.andWhere('a.energy_type = :et', { et: query.energyType });
    if (query.status) qb.andWhere('a.status = :s', { s: query.status });
    if (query.startTime)
      qb.andWhere('a.alarm_time >= :st', { st: new Date(query.startTime) });
    if (query.endTime)
      qb.andWhere('a.alarm_time <= :et2', { et2: new Date(query.endTime) });
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
      note: dto.note,
    });
    return { success: true };
  }

  async getStatistics(query: QueryStatisticsDto) {
    const qb = this.readingRepo.createQueryBuilder('r');
    if (query.energyType)
      qb.andWhere('r.energy_type = :et', { et: query.energyType });
    if (query.year) qb.andWhere('r.year = :y', { y: query.year });
    if (query.month) qb.andWhere('r.month = :m', { m: query.month });
    if (query.startTime)
      qb.andWhere('r.read_time >= :st', { st: new Date(query.startTime) });
    if (query.endTime)
      qb.andWhere('r.read_time <= :et2', { et2: new Date(query.endTime) });
    const readings = await qb.getMany();
    const totalValue = readings.reduce((s, r) => s + (r.value || 0), 0);

    const byMonth: Record<string, number> = {};
    for (const r of readings) {
      const key = `${r.year}-${String(r.month).padStart(2, '0')}`;
      byMonth[key] = (byMonth[key] || 0) + r.value;
    }

    const bySubItem: Record<string, number> = {};
    for (const r of readings) {
      const key = r.subItem || 'other';
      bySubItem[key] = (bySubItem[key] || 0) + r.value;
    }

    return {
      totalValue: Math.round(totalValue * 100) / 100,
      byMonth: Object.entries(byMonth)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([k, v]) => ({ period: k, value: Math.round(v * 100) / 100 })),
      bySubItem: Object.entries(bySubItem).map(([k, v]) => ({
        subItem: k,
        value: Math.round(v * 100) / 100,
      })),
      count: readings.length,
    };
  }
}

import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { EnergyMeterEntity } from '../entities/energy-meter.entity';
import { QueryLedgerDto, LedgerEditDto, DeleteDto } from '../dto/ledger.dto';

@Injectable()
export class LedgerService {
  private readonly logger = new Logger(LedgerService.name);

  constructor(
    @InjectRepository(EnergyMeterEntity)
    private meterRepo: Repository<EnergyMeterEntity>,
  ) {}

  async getList(query: QueryLedgerDto) {
    const pageNo = Number(query.pageNo) || 1;
    const pageSize = Number(query.pageSize) || 20;
    const qb = this.meterRepo.createQueryBuilder('m');
    if (query.building) qb.andWhere('m.building = :b', { b: query.building });
    if (query.floor) qb.andWhere('m.floor = :f', { f: query.floor });
    if (query.energyType)
      qb.andWhere('m.energy_type = :et', { et: query.energyType });
    if (query.status) qb.andWhere('m.status = :s', { s: query.status });
    const [list, total] = await qb
      .orderBy('m.create_time', 'DESC')
      .skip((pageNo - 1) * pageSize)
      .take(pageSize)
      .getManyAndCount();
    return { list, total };
  }

  async edit(dto: LedgerEditDto) {
    const data: Partial<EnergyMeterEntity> = {
      name: dto.name,
      meterNo: dto.meterNo,
      energyType: dto.energyType,
      building: dto.building,
      floor: dto.floor,
      area: dto.area,
      branch: dto.branch,
      siteName: dto.siteName,
      unit: dto.unit,
      status: dto.status ?? 'active',
      remark: dto.remark,
    };
    if (dto.installDate) data.installDate = new Date(dto.installDate);
    if (dto.id) {
      await this.meterRepo.update(dto.id, data);
      return this.meterRepo.findOneBy({ id: dto.id });
    }
    return this.meterRepo.save(this.meterRepo.create(data));
  }

  async delete(dto: DeleteDto) {
    await this.meterRepo.delete(dto.id);
    return { success: true };
  }
}

import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { EnergyPriceEntity } from '../entities/energy-price.entity';
import { EnergyElecConfigEntity } from '../entities/energy-elec-config.entity';
import {
  QueryPriceDto,
  PriceEditDto,
  QueryElecConfigDto,
  ElecConfigEditDto,
  DeleteDto,
} from '../dto/price.dto';

@Injectable()
export class PriceService {
  private readonly logger = new Logger(PriceService.name);

  constructor(
    @InjectRepository(EnergyPriceEntity)
    private priceRepo: Repository<EnergyPriceEntity>,
    @InjectRepository(EnergyElecConfigEntity)
    private elecConfigRepo: Repository<EnergyElecConfigEntity>,
  ) {}

  async getPriceList(query: QueryPriceDto) {
    const qb = this.priceRepo.createQueryBuilder('p');
    if (query.energyType)
      qb.andWhere('p.energy_type = :et', { et: query.energyType });
    if (query.month) qb.andWhere('p.month = :m', { m: query.month });
    const list = await qb.orderBy('p.create_time', 'DESC').getMany();
    return { list, total: list.length };
  }

  async editPrice(dto: PriceEditDto) {
    const data: Partial<EnergyPriceEntity> = {
      energyType: dto.energyType,
      month: dto.month,
      tier1Limit: dto.tier1Limit,
      tier1Price: dto.tier1Price,
      tier2Limit: dto.tier2Limit,
      tier2Price: dto.tier2Price,
      tier3Price: dto.tier3Price,
      unit: dto.unit,
      remark: dto.remark,
    };
    if (dto.id) {
      await this.priceRepo.update(dto.id, data);
      return this.priceRepo.findOneBy({ id: dto.id });
    }
    return this.priceRepo.save(this.priceRepo.create(data));
  }

  async deletePrice(dto: DeleteDto) {
    await this.priceRepo.delete(dto.id);
    return { success: true };
  }

  async getElecConfigList(query: QueryElecConfigDto) {
    const qb = this.elecConfigRepo.createQueryBuilder('e');
    if (query.branchName)
      qb.andWhere('e.branch_name LIKE :bn', { bn: `%${query.branchName}%` });
    const list = await qb.orderBy('e.create_time', 'DESC').getMany();
    return { list, total: list.length };
  }

  async editElecConfig(dto: ElecConfigEditDto) {
    const data: Partial<EnergyElecConfigEntity> = {
      branchName: dto.branchName,
      sharpStart: dto.sharpStart,
      sharpEnd: dto.sharpEnd,
      sharpPrice: dto.sharpPrice,
      peakStart: dto.peakStart,
      peakEnd: dto.peakEnd,
      peakPrice: dto.peakPrice,
      flatStart: dto.flatStart,
      flatEnd: dto.flatEnd,
      flatPrice: dto.flatPrice,
      valleyStart: dto.valleyStart,
      valleyEnd: dto.valleyEnd,
      valleyPrice: dto.valleyPrice,
      monthlyLimit: dto.monthlyLimit,
    };
    if (dto.id) {
      await this.elecConfigRepo.update(dto.id, data);
      return this.elecConfigRepo.findOneBy({ id: dto.id });
    }
    return this.elecConfigRepo.save(this.elecConfigRepo.create(data));
  }

  async deleteElecConfig(dto: DeleteDto) {
    await this.elecConfigRepo.delete(dto.id);
    return { success: true };
  }
}

import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { CarbonTransactionEntity } from '../entities/carbon-transaction.entity';
import { CarbonFootprintEntity } from '../entities/carbon-footprint.entity';
import { CarbonDecisionEntity } from '../entities/carbon-decision.entity';
import { EnergyReadingEntity } from '../entities/energy-reading.entity';
import {
  QueryCarbonOverviewDto,
  QueryTransactionDto,
  TransactionEditDto,
  QueryFootprintDto,
  FootprintEditDto,
  QueryCurveDto,
  CurveEditDto,
  QueryDecisionDto,
  DecisionEditDto,
  QueryAssetsDto,
  DeleteDto,
} from '../dto/carbon.dto';

const ELEC_CARBON_FACTOR = 0.581;

@Injectable()
export class CarbonService {
  private readonly logger = new Logger(CarbonService.name);

  constructor(
    @InjectRepository(CarbonTransactionEntity)
    private transactionRepo: Repository<CarbonTransactionEntity>,
    @InjectRepository(CarbonFootprintEntity)
    private footprintRepo: Repository<CarbonFootprintEntity>,
    @InjectRepository(CarbonDecisionEntity)
    private decisionRepo: Repository<CarbonDecisionEntity>,
    @InjectRepository(EnergyReadingEntity)
    private readingRepo: Repository<EnergyReadingEntity>,
  ) {}

  async getOverview(query: QueryCarbonOverviewDto) {
    const qb = this.readingRepo
      .createQueryBuilder('r')
      .where('r.energy_type = :et', { et: 'electricity' });
    if (query.year) qb.andWhere('r.year = :y', { y: query.year });
    if (query.month) qb.andWhere('r.month = :m', { m: query.month });
    const readings = await qb.getMany();
    const totalKwh = readings.reduce((s, r) => s + (r.value || 0), 0);
    const directEmission = 0;
    const indirectEmission =
      Math.round(totalKwh * ELEC_CARBON_FACTOR * 100) / 100;
    const totalEmission =
      Math.round((directEmission + indirectEmission) * 100) / 100;

    const byMonthMap: Record<string, number> = {};
    for (const r of readings) {
      const key = `${r.year}-${String(r.month).padStart(2, '0')}`;
      byMonthMap[key] = (byMonthMap[key] || 0) + r.value * ELEC_CARBON_FACTOR;
    }
    return {
      totalEmission,
      directEmission,
      indirectEmission,
      history: Object.entries(byMonthMap)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([k, v]) => ({ period: k, value: Math.round(v * 100) / 100 })),
    };
  }

  async getTransactionList(query: QueryTransactionDto) {
    const pageNo = Number(query.pageNo) || 1;
    const pageSize = Number(query.pageSize) || 20;
    const qb = this.transactionRepo.createQueryBuilder('t');
    if (query.building) qb.andWhere('t.building = :b', { b: query.building });
    if (query.purchaseType)
      qb.andWhere('t.purchase_type = :pt', { pt: query.purchaseType });
    const [list, total] = await qb
      .orderBy('t.create_time', 'DESC')
      .skip((pageNo - 1) * pageSize)
      .take(pageSize)
      .getManyAndCount();
    return { list, total };
  }

  async editTransaction(dto: TransactionEditDto) {
    const data: Partial<CarbonTransactionEntity> = {
      building: dto.building,
      purchaseType: dto.purchaseType,
      carbonAmount: dto.carbonAmount,
      tradePlatform: dto.tradePlatform,
      status: dto.status ?? 'completed',
      remark: dto.remark,
    };
    if (dto.tradeTime) data.tradeTime = new Date(dto.tradeTime);
    if (dto.effectTime) data.effectTime = new Date(dto.effectTime);
    if (dto.id) {
      await this.transactionRepo.update(dto.id, data);
      return this.transactionRepo.findOneBy({ id: dto.id });
    }
    return this.transactionRepo.save(this.transactionRepo.create(data));
  }

  async deleteTransaction(dto: DeleteDto) {
    await this.transactionRepo.delete(dto.id);
    return { success: true };
  }

  async getFootprintList(query: QueryFootprintDto) {
    const pageNo = Number(query.pageNo) || 1;
    const pageSize = Number(query.pageSize) || 20;
    const qb = this.footprintRepo.createQueryBuilder('f');
    if (query.building) qb.andWhere('f.building = :b', { b: query.building });
    const [list, total] = await qb
      .orderBy('f.create_time', 'DESC')
      .skip((pageNo - 1) * pageSize)
      .take(pageSize)
      .getManyAndCount();
    return { list, total };
  }

  async editFootprint(dto: FootprintEditDto) {
    const data: Partial<CarbonFootprintEntity> = {
      building: dto.building,
      productName: dto.productName,
      carbonAmount: dto.carbonAmount,
      perProductCarbon: dto.perProductCarbon,
      unit: dto.unit,
      conclusion: dto.conclusion,
      remark: dto.remark,
    };
    if (dto.productStartTime)
      data.productStartTime = new Date(dto.productStartTime);
    if (dto.productEndTime) data.productEndTime = new Date(dto.productEndTime);
    if (dto.checkStartTime) data.checkStartTime = new Date(dto.checkStartTime);
    if (dto.checkEndTime) data.checkEndTime = new Date(dto.checkEndTime);
    if (dto.id) {
      await this.footprintRepo.update(dto.id, data);
      return this.footprintRepo.findOneBy({ id: dto.id });
    }
    return this.footprintRepo.save(this.footprintRepo.create(data));
  }

  async deleteFootprint(dto: DeleteDto) {
    await this.footprintRepo.delete(dto.id);
    return { success: true };
  }

  getCurve(query: QueryCurveDto) {
    const baseYear = new Date().getFullYear();
    const rate = query.scenario === 'plan' ? 0.05 : 0.03;
    const data = Array.from({ length: 30 }, (_, i) => ({
      year: baseYear + i,
      emission: Math.round(100 * Math.pow(1 - rate, i) * 100) / 100,
    }));
    return {
      building: query.building,
      scenario: query.scenario ?? 'simulation',
      data,
    };
  }

  editCurve(dto: CurveEditDto) {
    return { success: true, ...dto };
  }

  async getEvaluation(query: QueryCurveDto) {
    const readings = await this.readingRepo.find({
      where: { energyType: 'electricity' },
    });
    const totalKwh = readings.reduce((s, r) => s + (r.value || 0), 0);
    const totalKgce = totalKwh * 0.1229;
    return {
      building: query.building,
      energyPerArea: Math.round((totalKgce / 10000) * 100) / 100,
      energyPerCapita: Math.round((totalKgce / 500) * 100) / 100,
      unit: 'kgace',
    };
  }

  async getDecisionList(query: QueryDecisionDto) {
    const pageNo = Number(query.pageNo) || 1;
    const pageSize = Number(query.pageSize) || 20;
    const qb = this.decisionRepo.createQueryBuilder('d');
    if (query.building) qb.andWhere('d.building = :b', { b: query.building });
    const [list, total] = await qb
      .orderBy('d.create_time', 'DESC')
      .skip((pageNo - 1) * pageSize)
      .take(pageSize)
      .getManyAndCount();
    return { list, total };
  }

  async editDecision(dto: DecisionEditDto) {
    const data: Partial<CarbonDecisionEntity> = {
      building: dto.building,
      energyConsumption: dto.energyConsumption,
      investmentValue: dto.investmentValue,
      energySavingRate: dto.energySavingRate,
      energySavingAmount: dto.energySavingAmount,
      carbonReductionAmount: dto.carbonReductionAmount,
      remark: dto.remark,
    };
    if (dto.id) {
      await this.decisionRepo.update(dto.id, data);
      return this.decisionRepo.findOneBy({ id: dto.id });
    }
    return this.decisionRepo.save(this.decisionRepo.create(data));
  }

  async deleteDecision(dto: DeleteDto) {
    await this.decisionRepo.delete(dto.id);
    return { success: true };
  }

  async getAssets(query: QueryAssetsDto) {
    const txQb = this.transactionRepo.createQueryBuilder('t');
    if (query.building) txQb.andWhere('t.building = :b', { b: query.building });
    const transactions = await txQb.getMany();
    const totalTrade = transactions.reduce(
      (s, t) => s + (t.carbonAmount || 0),
      0,
    );

    const readings = await this.readingRepo.find({
      where: { energyType: 'electricity' },
    });
    const totalKwh = readings.reduce((s, r) => s + (r.value || 0), 0);
    const emission = Math.round(totalKwh * ELEC_CARBON_FACTOR * 100) / 100;
    const target = Math.round(emission * 0.8 * 100) / 100;

    return {
      building: query.building,
      emissionTarget: target,
      actualEmission: emission,
      tradeAmount: Math.round(totalTrade * 100) / 100,
      carbonNeutral: Math.round(totalTrade * 100) / 100,
      trend: transactions.slice(-6).map((t) => ({
        period: t.tradeTime ? t.tradeTime.toISOString().slice(0, 7) : '',
        tradeAmount: t.carbonAmount ?? 0,
      })),
    };
  }
}

import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class QueryMeterDto {
  @ApiPropertyOptional() energyType?: string;
  @ApiPropertyOptional() building?: string;
  @ApiPropertyOptional() floor?: string;
  @ApiPropertyOptional() status?: string;
}

export class MeterEditDto {
  @ApiPropertyOptional() id?: string;
  @ApiProperty() name!: string;
  @ApiPropertyOptional() meterNo?: string;
  @ApiProperty() energyType!: string;
  @ApiPropertyOptional() building?: string;
  @ApiPropertyOptional() floor?: string;
  @ApiPropertyOptional() area?: string;
  @ApiPropertyOptional() branch?: string;
  @ApiPropertyOptional() siteName?: string;
  @ApiPropertyOptional() deviceId?: string;
  @ApiPropertyOptional() unit?: string;
  @ApiPropertyOptional() installDate?: string;
  @ApiPropertyOptional() status?: string;
  @ApiPropertyOptional() remark?: string;
}

export class QueryReadingDto {
  @ApiPropertyOptional() meterId?: string;
  @ApiPropertyOptional() energyType?: string;
  @ApiPropertyOptional() startTime?: string;
  @ApiPropertyOptional() endTime?: string;
  @ApiPropertyOptional() year?: number;
  @ApiPropertyOptional() month?: number;
  @ApiPropertyOptional() pageNo?: number;
  @ApiPropertyOptional() pageSize?: number;
}

export class ReadingEditDto {
  @ApiPropertyOptional() id?: string;
  @ApiPropertyOptional() meterId?: string;
  @ApiPropertyOptional() meterNo?: string;
  @ApiPropertyOptional() meterName?: string;
  @ApiProperty() energyType!: string;
  @ApiProperty() value!: number;
  @ApiPropertyOptional() unit?: string;
  @ApiPropertyOptional() readTime?: string;
  @ApiPropertyOptional() subItem?: string;
  @ApiPropertyOptional() isManual?: boolean;
  @ApiPropertyOptional() remark?: string;
}

export class DeleteDto {
  @ApiProperty() id!: string;
}

import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class QueryAlarmConfigDto {
  @ApiPropertyOptional() energyType?: string;
}

export class AlarmConfigEditDto {
  @ApiPropertyOptional() id?: string;
  @ApiPropertyOptional() meterId?: string;
  @ApiPropertyOptional() meterName?: string;
  @ApiPropertyOptional() energyType?: string;
  @ApiPropertyOptional() threshold?: number;
  @ApiPropertyOptional() period?: string;
  @ApiPropertyOptional() enabled?: boolean;
  @ApiPropertyOptional() notifyUser?: string;
}

export class QueryAlarmDto {
  @ApiPropertyOptional() energyType?: string;
  @ApiPropertyOptional() status?: string;
  @ApiPropertyOptional() startTime?: string;
  @ApiPropertyOptional() endTime?: string;
  @ApiPropertyOptional() pageNo?: number;
  @ApiPropertyOptional() pageSize?: number;
}

export class AckAlarmDto {
  @ApiProperty() id!: string;
  @ApiPropertyOptional() note?: string;
}

export class QueryStatisticsDto {
  @ApiPropertyOptional() energyType?: string;
  @ApiPropertyOptional() period?: string;
  @ApiPropertyOptional() dimension?: string;
  @ApiPropertyOptional() startTime?: string;
  @ApiPropertyOptional() endTime?: string;
  @ApiPropertyOptional() year?: number;
  @ApiPropertyOptional() month?: number;
  @ApiPropertyOptional() compareType?: string;
}

export class DeleteDto {
  @ApiProperty() id!: string;
}

import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class QueryLedgerDto {
  @ApiPropertyOptional() building?: string;
  @ApiPropertyOptional() floor?: string;
  @ApiPropertyOptional() energyType?: string;
  @ApiPropertyOptional() status?: string;
  @ApiPropertyOptional() pageNo?: number;
  @ApiPropertyOptional() pageSize?: number;
}

export class LedgerEditDto {
  @ApiPropertyOptional() id?: string;
  @ApiProperty() name!: string;
  @ApiPropertyOptional() meterNo?: string;
  @ApiProperty() energyType!: string;
  @ApiPropertyOptional() building?: string;
  @ApiPropertyOptional() floor?: string;
  @ApiPropertyOptional() area?: string;
  @ApiPropertyOptional() branch?: string;
  @ApiPropertyOptional() siteName?: string;
  @ApiPropertyOptional() unit?: string;
  @ApiPropertyOptional() installDate?: string;
  @ApiPropertyOptional() status?: string;
  @ApiPropertyOptional() remark?: string;
}

export class DeleteDto {
  @ApiProperty() id!: string;
}

import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class QueryPriceDto {
  @ApiPropertyOptional() energyType?: string;
  @ApiPropertyOptional() month?: string;
}

export class PriceEditDto {
  @ApiPropertyOptional() id?: string;
  @ApiProperty() energyType!: string;
  @ApiPropertyOptional() month?: string;
  @ApiPropertyOptional() tier1Limit?: number;
  @ApiPropertyOptional() tier1Price?: number;
  @ApiPropertyOptional() tier2Limit?: number;
  @ApiPropertyOptional() tier2Price?: number;
  @ApiPropertyOptional() tier3Price?: number;
  @ApiPropertyOptional() unit?: string;
  @ApiPropertyOptional() remark?: string;
}

export class QueryElecConfigDto {
  @ApiPropertyOptional() branchName?: string;
}

export class ElecConfigEditDto {
  @ApiPropertyOptional() id?: string;
  @ApiProperty() branchName!: string;
  @ApiPropertyOptional() sharpStart?: string;
  @ApiPropertyOptional() sharpEnd?: string;
  @ApiPropertyOptional() sharpPrice?: number;
  @ApiPropertyOptional() peakStart?: string;
  @ApiPropertyOptional() peakEnd?: string;
  @ApiPropertyOptional() peakPrice?: number;
  @ApiPropertyOptional() flatStart?: string;
  @ApiPropertyOptional() flatEnd?: string;
  @ApiPropertyOptional() flatPrice?: number;
  @ApiPropertyOptional() valleyStart?: string;
  @ApiPropertyOptional() valleyEnd?: string;
  @ApiPropertyOptional() valleyPrice?: number;
  @ApiPropertyOptional() monthlyLimit?: number;
}

export class DeleteDto {
  @ApiProperty() id!: string;
}

import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class QueryCarbonOverviewDto {
  @ApiPropertyOptional() building?: string;
  @ApiPropertyOptional() period?: string;
  @ApiPropertyOptional() year?: number;
  @ApiPropertyOptional() month?: number;
  @ApiPropertyOptional() startDate?: string;
  @ApiPropertyOptional() endDate?: string;
}

export class QueryTransactionDto {
  @ApiPropertyOptional() building?: string;
  @ApiPropertyOptional() purchaseType?: string;
  @ApiPropertyOptional() startTime?: string;
  @ApiPropertyOptional() endTime?: string;
  @ApiPropertyOptional() pageNo?: number;
  @ApiPropertyOptional() pageSize?: number;
}

export class TransactionEditDto {
  @ApiPropertyOptional() id?: string;
  @ApiPropertyOptional() building?: string;
  @ApiPropertyOptional() tradeTime?: string;
  @ApiPropertyOptional() effectTime?: string;
  @ApiPropertyOptional() purchaseType?: string;
  @ApiPropertyOptional() carbonAmount?: number;
  @ApiPropertyOptional() tradePlatform?: string;
  @ApiPropertyOptional() status?: string;
  @ApiPropertyOptional() remark?: string;
}

export class QueryFootprintDto {
  @ApiPropertyOptional() building?: string;
  @ApiPropertyOptional() pageNo?: number;
  @ApiPropertyOptional() pageSize?: number;
}

export class FootprintEditDto {
  @ApiPropertyOptional() id?: string;
  @ApiPropertyOptional() building?: string;
  @ApiPropertyOptional() productName?: string;
  @ApiPropertyOptional() carbonAmount?: number;
  @ApiPropertyOptional() perProductCarbon?: number;
  @ApiPropertyOptional() unit?: string;
  @ApiPropertyOptional() productStartTime?: string;
  @ApiPropertyOptional() productEndTime?: string;
  @ApiPropertyOptional() checkStartTime?: string;
  @ApiPropertyOptional() checkEndTime?: string;
  @ApiPropertyOptional() conclusion?: string;
  @ApiPropertyOptional() remark?: string;
}

export class QueryCurveDto {
  @ApiPropertyOptional() building?: string;
  @ApiPropertyOptional() scenario?: string;
}

export class CurveEditDto {
  @ApiPropertyOptional() building?: string;
  @ApiPropertyOptional() scenario?: string;
  @ApiPropertyOptional() targetYear?: number;
  @ApiPropertyOptional() energySavingRate?: number;
  @ApiPropertyOptional() buildingScope?: string;
  @ApiPropertyOptional() subItemSavingRate?: string;
}

export class QueryDecisionDto {
  @ApiPropertyOptional() building?: string;
  @ApiPropertyOptional() pageNo?: number;
  @ApiPropertyOptional() pageSize?: number;
}

export class DecisionEditDto {
  @ApiPropertyOptional() id?: string;
  @ApiPropertyOptional() building?: string;
  @ApiPropertyOptional() energyConsumption?: number;
  @ApiPropertyOptional() investmentValue?: number;
  @ApiPropertyOptional() energySavingRate?: number;
  @ApiPropertyOptional() energySavingAmount?: number;
  @ApiPropertyOptional() carbonReductionAmount?: number;
  @ApiPropertyOptional() remark?: string;
}

export class QueryAssetsDto {
  @ApiPropertyOptional() building?: string;
  @ApiPropertyOptional() startTime?: string;
  @ApiPropertyOptional() endTime?: string;
}

export class DeleteDto {
  @ApiProperty() id!: string;
}
```

## 后30页

此部分收录前端Vue组件源代码，包括能耗采集（电耗/水耗）、能耗监测（告警/统计）、能耗管理（用水/用电/台账/价格/用电配置）、双碳管理（碳概览/碳交易/碳足迹/双碳曲线/动态评价/辅助决策/碳资产管理）共16个页面组件及1个API文件。代码按文件顺序连续排列。

```
import request from '/@/utils/request'

// ── 能耗采集 ────────────────────────────────────────────────────────────────
export function getEnergyMeterList(params?: any) {
  return request({ url: '/energy/collect/meterList', method: 'get', params })
}
export function doEditEnergyMeter(data: any) {
  return request({ url: '/energy/collect/meterEdit', method: 'post', data })
}
export function doDeleteEnergyMeter(data: any) {
  return request({ url: '/energy/collect/meterDelete', method: 'post', data })
}
export function getEnergyReadingList(params?: any) {
  return request({ url: '/energy/collect/readingList', method: 'get', params })
}
export function doEditEnergyReading(data: any) {
  return request({ url: '/energy/collect/readingEdit', method: 'post', data })
}
export function doDeleteEnergyReading(data: any) {
  return request({ url: '/energy/collect/readingDelete', method: 'post', data })
}

// ── 能耗监测 ────────────────────────────────────────────────────────────────
export function getEnergyAlarmConfigList(params?: any) {
  return request({ url: '/energy/monitor/alarmConfigList', method: 'get', params })
}
export function doEditEnergyAlarmConfig(data: any) {
  return request({ url: '/energy/monitor/alarmConfigEdit', method: 'post', data })
}
export function doDeleteEnergyAlarmConfig(data: any) {
  return request({ url: '/energy/monitor/alarmConfigDelete', method: 'post', data })
}
export function getEnergyAlarmList(params?: any) {
  return request({ url: '/energy/monitor/alarmList', method: 'get', params })
}
export function ackEnergyAlarm(data: any) {
  return request({ url: '/energy/monitor/ackAlarm', method: 'post', data })
}
export function getEnergyStatistics(params?: any) {
  return request({ url: '/energy/monitor/statistics', method: 'get', params })
}

// ── 基础台账 ────────────────────────────────────────────────────────────────
export function getEnergyLedgerList(params?: any) {
  return request({ url: '/energy/ledger/list', method: 'get', params })
}
export function doEditEnergyLedger(data: any) {
  return request({ url: '/energy/ledger/edit', method: 'post', data })
}
export function doDeleteEnergyLedger(data: any) {
  return request({ url: '/energy/ledger/delete', method: 'post', data })
}

// ── 价格配置 ────────────────────────────────────────────────────────────────
export function getEnergyPriceList(params?: any) {
  return request({ url: '/energy/price/list', method: 'get', params })
}
export function doEditEnergyPrice(data: any) {
  return request({ url: '/energy/price/edit', method: 'post', data })
}
export function doDeleteEnergyPrice(data: any) {
  return request({ url: '/energy/price/delete', method: 'post', data })
}

// ── 用电配置（尖峰平谷）──────────────────────────────────────────────────────
export function getEnergyElecConfigList(params?: any) {
  return request({ url: '/energy/price/elecConfigList', method: 'get', params })
}
export function doEditEnergyElecConfig(data: any) {
  return request({ url: '/energy/price/elecConfigEdit', method: 'post', data })
}
export function doDeleteEnergyElecConfig(data: any) {
  return request({ url: '/energy/price/elecConfigDelete', method: 'post', data })
}

// ── 双碳管理 ────────────────────────────────────────────────────────────────
export function getCarbonOverview(params?: any) {
  return request({ url: '/energy/carbon/overview', method: 'get', params })
}
export function getCarbonTransactionList(params?: any) {
  return request({ url: '/energy/carbon/transactionList', method: 'get', params })
}
export function doEditCarbonTransaction(data: any) {
  return request({ url: '/energy/carbon/transactionEdit', method: 'post', data })
}
export function doDeleteCarbonTransaction(data: any) {
  return request({ url: '/energy/carbon/transactionDelete', method: 'post', data })
}
export function getCarbonFootprintList(params?: any) {
  return request({ url: '/energy/carbon/footprintList', method: 'get', params })
}
export function doEditCarbonFootprint(data: any) {
  return request({ url: '/energy/carbon/footprintEdit', method: 'post', data })
}
export function doDeleteCarbonFootprint(data: any) {
  return request({ url: '/energy/carbon/footprintDelete', method: 'post', data })
}
export function getCarbonCurve(params?: any) {
  return request({ url: '/energy/carbon/curve', method: 'get', params })
}
export function doEditCarbonCurve(data: any) {
  return request({ url: '/energy/carbon/curveEdit', method: 'post', data })
}
export function getCarbonEvaluation(params?: any) {
  return request({ url: '/energy/carbon/evaluation', method: 'get', params })
}
export function getCarbonDecisionList(params?: any) {
  return request({ url: '/energy/carbon/decisionList', method: 'get', params })
}
export function doEditCarbonDecision(data: any) {
  return request({ url: '/energy/carbon/decisionEdit', method: 'post', data })
}
export function doDeleteCarbonDecision(data: any) {
  return request({ url: '/energy/carbon/decisionDelete', method: 'post', data })
}
export function getCarbonAssets(params?: any) {
  return request({ url: '/energy/carbon/assets', method: 'get', params })
}

<template>
  <div class="energy-collect-container">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="表计管理" name="meter">
        <el-row :gutter="12" style="margin-bottom: 16px">
          <el-col :span="5">
            <el-select v-model="meterQuery.building" clearable placeholder="楼宇" style="width: 100%" @change="loadMeters">
              <el-option v-for="b in buildingOptions" :key="b" :label="b" :value="b" />
            </el-select>
          </el-col>
          <el-col :span="5">
            <el-select v-model="meterQuery.floor" clearable placeholder="楼层" style="width: 100%" @change="loadMeters">
              <el-option v-for="f in floorOptions" :key="f" :label="f" :value="f" />
            </el-select>
          </el-col>
          <el-col :span="5">
            <el-select v-model="meterQuery.status" clearable placeholder="状态" style="width: 100%" @change="loadMeters">
              <el-option label="在用" value="active" />
              <el-option label="停用" value="inactive" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-button type="primary" @click="loadMeters">查询</el-button>
            <el-button type="success" @click="openMeterDialog()">新增表计</el-button>
          </el-col>
        </el-row>

        <el-table :data="meterList" border stripe>
          <el-table-column prop="name" label="表计名称" min-width="120" />
          <el-table-column prop="meterNo" label="表计编号" width="130" />
          <el-table-column prop="building" label="楼宇" width="100" />
          <el-table-column prop="floor" label="楼层" width="80" />
          <el-table-column prop="area" label="区域" width="100" />
          <el-table-column prop="branch" label="分公司" width="100" />
          <el-table-column prop="unit" label="计量单位" width="80" />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                {{ row.status === 'active' ? '在用' : '停用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openMeterDialog(row)">编辑</el-button>
              <el-button link type="danger" @click="deleteMeter(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="用量数据" name="reading">
        <el-row :gutter="12" style="margin-bottom: 16px">
          <el-col :span="5">
            <el-select v-model="readingQuery.meterId" clearable placeholder="选择表计" style="width: 100%" @change="loadReadings">
              <el-option v-for="m in meterList" :key="m.id" :label="m.name" :value="m.id" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-input-number
              v-model="readingQuery.year"
              :min="2020"
              :max="2030"
              placeholder="年份"
              style="width: 100%"
              controls-position="right"
            />
          </el-col>
          <el-col :span="4">
            <el-select v-model="readingQuery.month" clearable placeholder="月份" style="width: 100%" @change="loadReadings">
              <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
            </el-select>
          </el-col>
          <el-col :span="5">
            <el-button type="primary" @click="loadReadings">查询</el-button>
            <el-button type="success" @click="openReadingDialog()">手工录入</el-button>
          </el-col>
        </el-row>

        <el-table :data="readingList" border stripe>
          <el-table-column prop="meterName" label="表计" min-width="120" />
          <el-table-column prop="readTime" label="采集时间" width="160">
            <template #default="{ row }">{{ formatDate(row.readTime) }}</template>
          </el-table-column>
          <el-table-column prop="value" label="用量" width="100" />
          <el-table-column prop="unit" label="单位" width="80" />
          <el-table-column prop="subItem" label="分项" width="100" />
          <el-table-column prop="isManual" label="来源" width="80">
            <template #default="{ row }">
              <el-tag :type="row.isManual ? 'warning' : 'success'" size="small">
                {{ row.isManual ? '手工' : '自动' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="remark" label="备注" min-width="120" />
          <el-table-column label="操作" width="80" fixed="right">
            <template #default="{ row }">
              <el-button link type="danger" @click="deleteReading(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          v-model:current-page="readingQuery.pageNo"
          v-model:page-size="readingQuery.pageSize"
          :total="readingTotal"
          layout="total, prev, pager, next"
          style="margin-top: 12px"
          @change="loadReadings"
        />
      </el-tab-pane>
    </el-tabs>

    <!-- 表计弹窗 -->
    <el-dialog v-model="meterDialogVisible" :title="meterForm.id ? '编辑表计' : '新增表计'" width="560px">
      <el-form :model="meterForm" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="表计名称" required>
              <el-input v-model="meterForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="表计编号">
              <el-input v-model="meterForm.meterNo" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="楼宇">
              <el-input v-model="meterForm.building" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="楼层">
              <el-input v-model="meterForm.floor" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="区域">
              <el-input v-model="meterForm.area" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分公司">
              <el-input v-model="meterForm.branch" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计量单位">
              <el-select v-model="meterForm.unit" style="width: 100%">
                <el-option label="kWh" value="kWh" />
                <el-option label="度" value="度" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="meterForm.status" style="width: 100%">
                <el-option label="在用" value="active" />
                <el-option label="停用" value="inactive" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="meterDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMeter">保存</el-button>
      </template>
    </el-dialog>

    <!-- 录入弹窗 -->
    <el-dialog v-model="readingDialogVisible" title="手工录入用电数据" width="480px">
      <el-form :model="readingForm" label-width="100px">
        <el-form-item label="表计">
          <el-select v-model="readingForm.meterId" style="width: 100%" @change="onMeterChange">
            <el-option v-for="m in meterList" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="采集时间">
          <el-date-picker v-model="readingForm.readTime" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="用量" required>
          <el-input-number v-model="readingForm.value" :precision="2" :min="0" style="width: 100%" controls-position="right" />
        </el-form-item>
        <el-form-item label="分项">
          <el-select v-model="readingForm.subItem" clearable style="width: 100%">
            <el-option label="空调" value="空调" />
            <el-option label="照明" value="照明" />
            <el-option label="新风" value="新风" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="readingForm.remark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="readingDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveReading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getEnergyMeterList,
  doEditEnergyMeter,
  doDeleteEnergyMeter,
  getEnergyReadingList,
  doEditEnergyReading,
  doDeleteEnergyReading,
} from '/@/api/energy'

const activeTab = ref('meter')
const meterList = ref<any[]>([])
const readingList = ref<any[]>([])
const readingTotal = ref(0)

const meterQuery = ref<any>({ building: '', floor: '', status: '' })
const readingQuery = ref<any>({ pageNo: 1, pageSize: 20 })
const meterDialogVisible = ref(false)
const readingDialogVisible = ref(false)
const meterForm = ref<any>({ energyType: 'electricity', status: 'active', unit: 'kWh' })
const readingForm = ref<any>({ energyType: 'electricity', isManual: true })

const buildingOptions = ref<string[]>([])
const floorOptions = ref(['1F', '2F', '3F', '4F', '5F', 'B1', 'B2'])

function formatDate(d: string) {
  return d ? d.replace('T', ' ').slice(0, 16) : '-'
}

async function loadMeters() {
  const res = await getEnergyMeterList({ ...meterQuery.value, energyType: 'electricity' })
  if (res.code === 200) {
    meterList.value = res.data.list
    const buildings = [...new Set<string>(res.data.list.map((m: any) => m.building).filter(Boolean))]
    buildingOptions.value = buildings
  }
}

async function loadReadings() {
  const res = await getEnergyReadingList({ ...readingQuery.value, energyType: 'electricity' })
  if (res.code === 200) {
    readingList.value = res.data.list
    readingTotal.value = res.data.total
  }
}

function openMeterDialog(row?: any) {
  meterForm.value = row ? { ...row } : { energyType: 'electricity', status: 'active', unit: 'kWh' }
  meterDialogVisible.value = true
}

async function saveMeter() {
  if (!meterForm.value.name) return ElMessage.warning('请输入表计名称')
  const res = await doEditEnergyMeter(meterForm.value)
  if (res.code === 200) {
    ElMessage.success('保存成功')
    meterDialogVisible.value = false
    loadMeters()
  }
}

async function deleteMeter(id: string) {
  await ElMessageBox.confirm('确认删除该表计？', '提示', { type: 'warning' })
  const res = await doDeleteEnergyMeter({ id })
  if (res.code === 200) {
    ElMessage.success('删除成功')
    loadMeters()
  }
}

function openReadingDialog() {
  readingForm.value = { energyType: 'electricity', isManual: true }
  readingDialogVisible.value = true
}

function onMeterChange(id: string) {
  const meter = meterList.value.find((m: any) => m.id === id)
  if (meter) {
    readingForm.value.meterNo = meter.meterNo
    readingForm.value.meterName = meter.name
    readingForm.value.unit = meter.unit || 'kWh'
  }
}

async function saveReading() {
  if (!readingForm.value.value) return ElMessage.warning('请输入用量')
  const res = await doEditEnergyReading(readingForm.value)
  if (res.code === 200) {
    ElMessage.success('录入成功')
    readingDialogVisible.value = false
    loadReadings()
  }
}

async function deleteReading(id: string) {
  await ElMessageBox.confirm('确认删除该记录？', '提示', { type: 'warning' })
  const res = await doDeleteEnergyReading({ id })
  if (res.code === 200) {
    ElMessage.success('删除成功')
    loadReadings()
  }
}

onMounted(() => {
  loadMeters()
  loadReadings()
})
</script>

<template>
  <div class="energy-collect-water-container">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="水表管理" name="meter">
        <el-row :gutter="12" style="margin-bottom: 16px">
          <el-col :span="5">
            <el-input v-model="meterQuery.building" clearable placeholder="楼宇/站点" @keyup.enter="loadMeters" />
          </el-col>
          <el-col :span="5">
            <el-input v-model="meterQuery.floor" clearable placeholder="楼层" @keyup.enter="loadMeters" />
          </el-col>
          <el-col :span="4">
            <el-button type="primary" @click="loadMeters">查询</el-button>
            <el-button type="success" @click="openMeterDialog()">新增水表</el-button>
          </el-col>
        </el-row>
        <el-table :data="meterList" border stripe>
          <el-table-column prop="name" label="水表名称" min-width="120" />
          <el-table-column prop="meterNo" label="表计编号" width="130" />
          <el-table-column prop="building" label="楼宇/站点" width="120" />
          <el-table-column prop="floor" label="楼层" width="80" />
          <el-table-column prop="area" label="区域" width="100" />
          <el-table-column prop="unit" label="单位" width="70" />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                {{ row.status === 'active' ? '在用' : '停用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openMeterDialog(row)">编辑</el-button>
              <el-button link type="danger" @click="deleteMeter(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="用水数据" name="reading">
        <el-row :gutter="12" style="margin-bottom: 16px">
          <el-col :span="5">
            <el-select v-model="readingQuery.meterId" clearable placeholder="选择水表" style="width: 100%">
              <el-option v-for="m in meterList" :key="m.id" :label="m.name" :value="m.id" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-input-number
              v-model="readingQuery.year"
              :min="2020"
              :max="2030"
              placeholder="年份"
              style="width: 100%"
              controls-position="right"
            />
          </el-col>
          <el-col :span="4">
            <el-select v-model="readingQuery.month" clearable placeholder="月份" style="width: 100%">
              <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
            </el-select>
          </el-col>
          <el-col :span="5">
            <el-button type="primary" @click="loadReadings">查询</el-button>
            <el-button type="success" @click="openReadingDialog()">手工录入</el-button>
          </el-col>
        </el-row>
        <el-table :data="readingList" border stripe>
          <el-table-column prop="meterName" label="水表" min-width="120" />
          <el-table-column prop="readTime" label="采集时间" width="160">
            <template #default="{ row }">{{ formatDate(row.readTime) }}</template>
          </el-table-column>
          <el-table-column prop="value" label="用量" width="100" />
          <el-table-column prop="unit" label="单位" width="70" />
          <el-table-column prop="isManual" label="来源" width="80">
            <template #default="{ row }">
              <el-tag :type="row.isManual ? 'warning' : 'success'" size="small">
                {{ row.isManual ? '手工' : '自动' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="remark" label="备注" min-width="120" />
          <el-table-column label="操作" width="80" fixed="right">
            <template #default="{ row }">
              <el-button link type="danger" @click="deleteReading(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          v-model:current-page="readingQuery.pageNo"
          v-model:page-size="readingQuery.pageSize"
          :total="readingTotal"
          layout="total, prev, pager, next"
          style="margin-top: 12px"
          @change="loadReadings"
        />
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="meterDialogVisible" :title="meterForm.id ? '编辑水表' : '新增水表'" width="520px">
      <el-form :model="meterForm" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="水表名称" required>
              <el-input v-model="meterForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="表计编号">
              <el-input v-model="meterForm.meterNo" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="楼宇/站点">
              <el-input v-model="meterForm.building" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="楼层">
              <el-input v-model="meterForm.floor" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="区域">
              <el-input v-model="meterForm.area" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="meterForm.status" style="width: 100%">
                <el-option label="在用" value="active" />
                <el-option label="停用" value="inactive" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="meterDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMeter">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="readingDialogVisible" title="手工录入用水数据" width="440px">
      <el-form :model="readingForm" label-width="100px">
        <el-form-item label="水表">
          <el-select v-model="readingForm.meterId" style="width: 100%" @change="onMeterChange">
            <el-option v-for="m in meterList" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="采集时间">
          <el-date-picker v-model="readingForm.readTime" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="用量（m³）" required>
          <el-input-number v-model="readingForm.value" :precision="3" :min="0" style="width: 100%" controls-position="right" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="readingForm.remark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="readingDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveReading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getEnergyMeterList,
  doEditEnergyMeter,
  doDeleteEnergyMeter,
  getEnergyReadingList,
  doEditEnergyReading,
  doDeleteEnergyReading,
} from '/@/api/energy'

const activeTab = ref('meter')
const meterList = ref<any[]>([])
const readingList = ref<any[]>([])
const readingTotal = ref(0)
const meterQuery = ref<any>({ building: '', floor: '' })
const readingQuery = ref<any>({ pageNo: 1, pageSize: 20 })
const meterDialogVisible = ref(false)
const readingDialogVisible = ref(false)
const meterForm = ref<any>({ energyType: 'water', status: 'active', unit: 'm³' })
const readingForm = ref<any>({ energyType: 'water', isManual: true })

function formatDate(d: string) {
  return d ? d.replace('T', ' ').slice(0, 16) : '-'
}

async function loadMeters() {
  const res = await getEnergyMeterList({ ...meterQuery.value, energyType: 'water' })
  if (res.code === 200) meterList.value = res.data.list
}

async function loadReadings() {
  const res = await getEnergyReadingList({ ...readingQuery.value, energyType: 'water' })
  if (res.code === 200) {
    readingList.value = res.data.list
    readingTotal.value = res.data.total
  }
}

function openMeterDialog(row?: any) {
  meterForm.value = row ? { ...row } : { energyType: 'water', status: 'active', unit: 'm³' }
  meterDialogVisible.value = true
}

async function saveMeter() {
  if (!meterForm.value.name) return ElMessage.warning('请输入水表名称')
  const res = await doEditEnergyMeter(meterForm.value)
  if (res.code === 200) {
    ElMessage.success('保存成功')
    meterDialogVisible.value = false
    loadMeters()
  }
}

async function deleteMeter(id: string) {
  await ElMessageBox.confirm('确认删除该水表？', '提示', { type: 'warning' })
  const res = await doDeleteEnergyMeter({ id })
  if (res.code === 200) {
    ElMessage.success('删除成功')
    loadMeters()
  }
}

function openReadingDialog() {
  readingForm.value = { energyType: 'water', isManual: true }
  readingDialogVisible.value = true
}

function onMeterChange(id: string) {
  const meter = meterList.value.find((m: any) => m.id === id)
  if (meter) {
    readingForm.value.meterNo = meter.meterNo
    readingForm.value.meterName = meter.name
  }
}

async function saveReading() {
  if (!readingForm.value.value) return ElMessage.warning('请输入用量')
  const res = await doEditEnergyReading({ ...readingForm.value, unit: 'm³' })
  if (res.code === 200) {
    ElMessage.success('录入成功')
    readingDialogVisible.value = false
    loadReadings()
  }
}

async function deleteReading(id: string) {
  await ElMessageBox.confirm('确认删除该记录？', '提示', { type: 'warning' })
  const res = await doDeleteEnergyReading({ id })
  if (res.code === 200) {
    ElMessage.success('删除成功')
    loadReadings()
  }
}

onMounted(() => {
  loadMeters()
  loadReadings()
})
</script>

<template>
  <div class="energy-alarm-container">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="告警记录" name="list">
        <el-row :gutter="12" style="margin-bottom: 16px">
          <el-col :span="5">
            <el-select v-model="query.energyType" clearable placeholder="能源类型" style="width: 100%" @change="loadAlarms">
              <el-option label="电能" value="electricity" />
              <el-option label="水能" value="water" />
              <el-option label="气能" value="gas" />
            </el-select>
          </el-col>
          <el-col :span="5">
            <el-select v-model="query.status" clearable placeholder="处理状态" style="width: 100%" @change="loadAlarms">
              <el-option label="未处理" value="unresolved" />
              <el-option label="已处理" value="resolved" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              style="width: 100%"
              @change="onDateChange"
            />
          </el-col>
          <el-col :span="4">
            <el-button type="primary" @click="loadAlarms">查询</el-button>
          </el-col>
        </el-row>

        <el-row :gutter="16" style="margin-bottom: 16px">
          <el-col :span="6">
            <el-card shadow="never" style="background: #fff3cd">
              <div style="text-align: center">
                <div style="font-size: 28px; font-weight: bold; color: #856404">{{ pendingCount }}</div>
                <div style="color: #856404">待处理告警</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="never" style="background: #d4edda">
              <div style="text-align: center">
                <div style="font-size: 28px; font-weight: bold; color: #155724">{{ resolvedCount }}</div>
                <div style="color: #155724">已处理告警</div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-table :data="alarmList" border stripe>
          <el-table-column prop="meterName" label="表计" min-width="120" />
          <el-table-column prop="energyType" label="能源类型" width="90">
            <template #default="{ row }">{{ typeLabel(row.energyType) }}</template>
          </el-table-column>
          <el-table-column prop="value" label="超标值" width="100" />
          <el-table-column prop="threshold" label="阈值" width="90" />
          <el-table-column prop="alarmTime" label="告警时间" width="160">
            <template #default="{ row }">{{ formatDate(row.alarmTime) }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'resolved' ? 'success' : 'danger'">
                {{ row.status === 'resolved' ? '已处理' : '未处理' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="handler" label="处理人" width="90" />
          <el-table-column prop="note" label="备注" min-width="120" />
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button v-if="row.status !== 'resolved'" link type="primary" @click="openAckDialog(row)">确认处理</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          v-model:current-page="query.pageNo"
          v-model:page-size="query.pageSize"
          :total="total"
          layout="total, prev, pager, next"
          style="margin-top: 12px"
          @change="loadAlarms"
        />
      </el-tab-pane>

      <el-tab-pane label="告警配置" name="config">
        <el-row style="margin-bottom: 16px">
          <el-col>
            <el-button type="success" @click="openConfigDialog()">新增配置</el-button>
          </el-col>
        </el-row>
        <el-table :data="configList" border stripe>
          <el-table-column prop="meterName" label="表计" min-width="120" />
          <el-table-column prop="energyType" label="能源类型" width="90">
            <template #default="{ row }">{{ typeLabel(row.energyType) }}</template>
          </el-table-column>
          <el-table-column prop="threshold" label="告警阈值" width="100" />
          <el-table-column prop="period" label="统计周期" width="90">
            <template #default="{ row }">{{ periodLabel(row.period) }}</template>
          </el-table-column>
          <el-table-column prop="enabled" label="启用" width="80">
            <template #default="{ row }">
              <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '是' : '否' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="notifyUser" label="通知人" min-width="120" />
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openConfigDialog(row)">编辑</el-button>
              <el-button link type="danger" @click="deleteConfig(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 确认处理弹窗 -->
    <el-dialog v-model="ackDialogVisible" title="处理告警" width="420px">
      <el-form :model="ackForm" label-width="80px">
        <el-form-item label="备注说明">
          <el-input v-model="ackForm.note" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ackDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAck">确认处理</el-button>
      </template>
    </el-dialog>

    <!-- 告警配置弹窗 -->
    <el-dialog v-model="configDialogVisible" :title="configForm.id ? '编辑告警配置' : '新增告警配置'" width="480px">
      <el-form :model="configForm" label-width="100px">
        <el-form-item label="表计名称">
          <el-input v-model="configForm.meterName" />
        </el-form-item>
        <el-form-item label="能源类型">
          <el-select v-model="configForm.energyType" style="width: 100%">
            <el-option label="电能" value="electricity" />
            <el-option label="水能" value="water" />
            <el-option label="气能" value="gas" />
          </el-select>
        </el-form-item>
        <el-form-item label="告警阈值" required>
          <el-input-number v-model="configForm.threshold" :min="0" style="width: 100%" controls-position="right" />
        </el-form-item>
        <el-form-item label="统计周期">
          <el-select v-model="configForm.period" style="width: 100%">
            <el-option label="小时" value="hour" />
            <el-option label="天" value="day" />
            <el-option label="周" value="week" />
            <el-option label="月" value="month" />
          </el-select>
        </el-form-item>
        <el-form-item label="通知人">
          <el-input v-model="configForm.notifyUser" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="configForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveConfig">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getEnergyAlarmList,
  ackEnergyAlarm,
  getEnergyAlarmConfigList,
  doEditEnergyAlarmConfig,
  doDeleteEnergyAlarmConfig,
} from '/@/api/energy'

const activeTab = ref('list')
const alarmList = ref<any[]>([])
const configList = ref<any[]>([])
const total = ref(0)
const dateRange = ref<any[]>([])
const query = ref<any>({ pageNo: 1, pageSize: 20 })
const ackDialogVisible = ref(false)
const configDialogVisible = ref(false)
const ackForm = ref<any>({})
const configForm = ref<any>({ period: 'day', enabled: true })

const pendingCount = computed(() => alarmList.value.filter((a) => a.status !== 'resolved').length)
const resolvedCount = computed(() => alarmList.value.filter((a) => a.status === 'resolved').length)

function typeLabel(t: string) {
  return { electricity: '电能', water: '水能', gas: '气能' }[t] || t
}
function periodLabel(p: string) {
  return { hour: '小时', day: '天', week: '周', month: '月' }[p] || p
}
function formatDate(d: string) {
  return d ? d.replace('T', ' ').slice(0, 16) : '-'
}
function onDateChange(val: any) {
  if (val) {
    query.value.startTime = val[0]
    query.value.endTime = val[1]
  } else {
    delete query.value.startTime
    delete query.value.endTime
  }
}

async function loadAlarms() {
  const res = await getEnergyAlarmList(query.value)
  if (res.code === 200) {
    alarmList.value = res.data.list
    total.value = res.data.total
  }
}

async function loadConfigs() {
  const res = await getEnergyAlarmConfigList({})
  if (res.code === 200) configList.value = res.data.list
}

function openAckDialog(row: any) {
  ackForm.value = { id: row.id, note: '' }
  ackDialogVisible.value = true
}

async function submitAck() {
  const res = await ackEnergyAlarm(ackForm.value)
  if (res.code === 200) {
    ElMessage.success('处理成功')
    ackDialogVisible.value = false
    loadAlarms()
  }
}

function openConfigDialog(row?: any) {
  configForm.value = row ? { ...row } : { period: 'day', enabled: true }
  configDialogVisible.value = true
}

async function saveConfig() {
  if (!configForm.value.threshold) return ElMessage.warning('请输入告警阈值')
  const res = await doEditEnergyAlarmConfig(configForm.value)
  if (res.code === 200) {
    ElMessage.success('保存成功')
    configDialogVisible.value = false
    loadConfigs()
  }
}

async function deleteConfig(id: string) {
  await ElMessageBox.confirm('确认删除该配置？', '提示', { type: 'warning' })
  const res = await doDeleteEnergyAlarmConfig({ id })
  if (res.code === 200) {
    ElMessage.success('删除成功')
    loadConfigs()
  }
}

onMounted(() => {
  loadAlarms()
  loadConfigs()
})
</script>

<template>
  <div class="energy-statistics-container">
    <el-card shadow="never" style="margin-bottom: 16px">
      <el-row :gutter="16">
        <el-col :span="5">
          <el-select v-model="query.energyType" placeholder="能源类型" style="width: 100%">
            <el-option label="电能" value="electricity" />
            <el-option label="水能" value="water" />
            <el-option label="气能" value="gas" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-input-number v-model="query.year" :min="2020" :max="2030" placeholder="年份" style="width: 100%" controls-position="right" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="query.month" clearable placeholder="月份（不选=全年）" style="width: 100%">
            <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadStats">查询</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 汇总卡片 -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <el-card shadow="never">
          <div style="text-align: center">
            <div style="font-size: 32px; font-weight: bold; color: #409eff">{{ stats.totalValue }}</div>
            <div style="color: #666; margin-top: 4px">总用量（{{ unitLabel }}）</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <div style="text-align: center">
            <div style="font-size: 32px; font-weight: bold; color: #67c23a">{{ stats.count }}</div>
            <div style="color: #666; margin-top: 4px">采集记录数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <!-- 月度用量 -->
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>
            <span>月度用量统计</span>
          </template>
          <el-table :data="stats.byMonth" border size="small">
            <el-table-column prop="period" label="统计月份" width="120" />
            <el-table-column prop="value" :label="`用量（${unitLabel}）`" />
            <el-table-column label="占比" width="120">
              <template #default="{ row }">
                <el-progress :percentage="stats.totalValue > 0 ? Math.round((row.value / stats.totalValue) * 100) : 0" :stroke-width="10" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 分项用量 -->
      <el-col :span="10">
        <el-card shadow="never">
          <template #header>
            <span>分项用量统计</span>
          </template>
          <el-table :data="stats.bySubItem" border size="small">
            <el-table-column prop="subItem" label="用能分项" width="120">
              <template #default="{ row }">{{ subItemLabel(row.subItem) }}</template>
            </el-table-column>
            <el-table-column prop="value" :label="`用量（${unitLabel}）`" />
            <el-table-column label="占比" width="100">
              <template #default="{ row }">{{ stats.totalValue > 0 ? ((row.value / stats.totalValue) * 100).toFixed(1) : 0 }}%</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getEnergyStatistics } from '/@/api/energy'

const query = ref<any>({
  energyType: 'electricity',
  year: new Date().getFullYear(),
})

const stats = ref<any>({
  totalValue: 0,
  count: 0,
  byMonth: [],
  bySubItem: [],
})

const unitLabel = computed(() => {
  return { electricity: 'kWh', water: 'm³', gas: 'm³' }[query.value.energyType as string] || ''
})

function subItemLabel(k: string) {
  return { 空调: '空调', 照明: '照明', 新风: '新风', other: '其他' }[k] || k
}

async function loadStats() {
  const res = await getEnergyStatistics(query.value)
  if (res.code === 200) stats.value = res.data
}

onMounted(loadStats)
</script>

<template>
  <div class="energy-manage-water-container">
    <el-card shadow="never" style="margin-bottom: 16px">
      <el-row :gutter="12">
        <el-col :span="5">
          <el-input v-model="query.building" clearable placeholder="分公司/站点" />
        </el-col>
        <el-col :span="6">
          <el-date-picker
            v-model="dateRange"
            type="monthrange"
            range-separator="至"
            start-placeholder="开始月份"
            end-placeholder="结束月份"
            value-format="YYYY-MM"
            style="width: 100%"
            @change="onDateChange"
          />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 汇总卡片 -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <el-card shadow="never" style="background: #e8f4fd">
          <div style="text-align: center">
            <div style="font-size: 28px; font-weight: bold; color: #1890ff">{{ summary.totalWater }}</div>
            <div style="color: #1890ff">总用水量（m³）</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" style="background: #e8f8ed">
          <div style="text-align: center">
            <div style="font-size: 28px; font-weight: bold; color: #52c41a">{{ summary.totalCost }}</div>
            <div style="color: #52c41a">预估费用（元）</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" style="background: #fff7e6">
          <div style="text-align: center">
            <div style="font-size: 28px; font-weight: bold; color: #fa8c16">{{ summary.meterCount }}</div>
            <div style="color: #fa8c16">在用水表数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 月度用水明细 -->
    <el-card shadow="never">
      <template #header><span>用水明细（按站点/楼层）</span></template>
      <el-table :data="readingList" border stripe>
        <el-table-column prop="meterName" label="水表" min-width="120" />
        <el-table-column prop="building" label="站点/楼宇" width="120" />
        <el-table-column prop="floor" label="楼层" width="80" />
        <el-table-column label="时间" width="110">
          <template #default="{ row }">{{ row.year }}-{{ String(row.month).padStart(2, '0') }}</template>
        </el-table-column>
        <el-table-column prop="value" label="用量（m³）" width="110" />
        <el-table-column prop="isManual" label="来源" width="80">
          <template #default="{ row }">
            <el-tag :type="row.isManual ? 'warning' : 'success'" size="small">
              {{ row.isManual ? '手工' : '自动' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="query.pageNo"
        v-model:page-size="query.pageSize"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top: 12px"
        @change="loadData"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getEnergyReadingList } from '/@/api/energy'

const query = ref<any>({ pageNo: 1, pageSize: 20 })
const dateRange = ref<any[]>([])
const readingList = ref<any[]>([])
const total = ref(0)
const summary = ref({ totalWater: 0, totalCost: 0, meterCount: 0 })

function onDateChange(val: any) {
  if (val) {
    query.value.startTime = `${val[0]}-01`
    query.value.endTime = `${val[1]}-28`
  } else {
    delete query.value.startTime
    delete query.value.endTime
  }
}

async function loadData() {
  const res = await getEnergyReadingList({ ...query.value, energyType: 'water' })
  if (res.code === 200) {
    readingList.value = res.data.list
    total.value = res.data.total
    const total_water = res.data.list.reduce((s: number, r: any) => s + (r.value || 0), 0)
    summary.value.totalWater = Math.round(total_water * 100) / 100
    summary.value.totalCost = Math.round(total_water * 4.5 * 100) / 100 // 预估单价 4.5元/m³
    summary.value.meterCount = new Set(res.data.list.map((r: any) => r.meterId)).size
  }
}

onMounted(loadData)
</script>

<template>
  <div class="energy-manage-elec-container">
    <el-card shadow="never" style="margin-bottom: 16px">
      <el-row :gutter="12">
        <el-col :span="5">
          <el-input v-model="query.building" clearable placeholder="分公司/楼宇" />
        </el-col>
        <el-col :span="4">
          <el-input-number v-model="query.year" :min="2020" :max="2030" placeholder="年份" style="width: 100%" controls-position="right" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="query.month" clearable placeholder="月份" style="width: 100%">
            <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 汇总卡片 -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <el-card shadow="never" style="background: #f0f9ff">
          <div style="text-align: center">
            <div style="font-size: 28px; font-weight: bold; color: #0ea5e9">{{ summary.totalKwh }}</div>
            <div style="color: #0ea5e9">总耗电量（kWh）</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" style="background: #f0fdf4">
          <div style="text-align: center">
            <div style="font-size: 28px; font-weight: bold; color: #16a34a">{{ summary.totalCost }}</div>
            <div style="color: #16a34a">预估费用（元）</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" style="background: #fef3c7">
          <div style="text-align: center">
            <div style="font-size: 28px; font-weight: bold; color: #d97706">{{ summary.carbonEmission }}</div>
            <div style="color: #d97706">碳排放量（kg）</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" style="background: #fdf2f8">
          <div style="text-align: center">
            <div style="font-size: 28px; font-weight: bold; color: #7c3aed">{{ summary.peakPct }}%</div>
            <div style="color: #7c3aed">峰时用电占比</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分项用电 -->
    <el-row :gutter="16">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header><span>用电明细</span></template>
          <el-table :data="readingList" border stripe>
            <el-table-column prop="meterName" label="表计" min-width="120" />
            <el-table-column label="时间" width="110">
              <template #default="{ row }">{{ row.year }}-{{ String(row.month).padStart(2, '0') }}</template>
            </el-table-column>
            <el-table-column prop="value" label="用量（kWh）" width="110" />
            <el-table-column prop="subItem" label="分项" width="90">
              <template #default="{ row }">{{ row.subItem || '综合' }}</template>
            </el-table-column>
            <el-table-column prop="isManual" label="来源" width="80">
              <template #default="{ row }">
                <el-tag :type="row.isManual ? 'warning' : 'success'" size="small">
                  {{ row.isManual ? '手工' : '自动' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="query.pageNo"
            v-model:page-size="query.pageSize"
            :total="total"
            layout="total, prev, pager, next"
            style="margin-top: 12px"
            @change="loadData"
          />
        </el-card>
      </el-col>

      <!-- 分项统计 -->
      <el-col :span="10">
        <el-card shadow="never">
          <template #header><span>分项用电排名</span></template>
          <div v-for="item in subItemStats" :key="item.subItem" style="margin-bottom: 12px">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px">
              <span>{{ item.subItem || '综合' }}</span>
              <span>{{ item.value }} kWh</span>
            </div>
            <el-progress :percentage="summary.totalKwh > 0 ? Math.round((item.value / summary.totalKwh) * 100) : 0" :stroke-width="10" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getEnergyReadingList } from '/@/api/energy'

const query = ref<any>({ pageNo: 1, pageSize: 20, year: new Date().getFullYear() })
const readingList = ref<any[]>([])
const total = ref(0)
const subItemStats = ref<any[]>([])
const summary = ref({ totalKwh: 0, totalCost: 0, carbonEmission: 0, peakPct: 30 })

async function loadData() {
  const res = await getEnergyReadingList({ ...query.value, energyType: 'electricity' })
  if (res.code === 200) {
    readingList.value = res.data.list
    total.value = res.data.total
    const totalKwh = res.data.list.reduce((s: number, r: any) => s + (r.value || 0), 0)
    summary.value.totalKwh = Math.round(totalKwh * 100) / 100
    summary.value.totalCost = Math.round(totalKwh * 0.65 * 100) / 100
    summary.value.carbonEmission = Math.round(totalKwh * 0.581 * 100) / 100
    // 分项统计
    const map: Record<string, number> = {}
    for (const r of res.data.list) {
      const k = r.subItem || '综合'
      map[k] = (map[k] || 0) + (r.value || 0)
    }
    subItemStats.value = Object.entries(map)
      .map(([subItem, value]) => ({ subItem, value: Math.round(value * 100) / 100 }))
      .sort((a, b) => b.value - a.value)
  }
}

onMounted(loadData)
</script>

<template>
  <div class="energy-ledger-container">
    <el-row :gutter="12" style="margin-bottom: 16px">
      <el-col :span="4">
        <el-input v-model="query.building" clearable placeholder="楼宇" @keyup.enter="loadList" />
      </el-col>
      <el-col :span="4">
        <el-input v-model="query.floor" clearable placeholder="楼层" @keyup.enter="loadList" />
      </el-col>
      <el-col :span="4">
        <el-select v-model="query.energyType" clearable placeholder="能源类型" style="width: 100%" @change="loadList">
          <el-option label="电能" value="electricity" />
          <el-option label="水能" value="water" />
          <el-option label="气能" value="gas" />
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-select v-model="query.status" clearable placeholder="状态" style="width: 100%" @change="loadList">
          <el-option label="在用" value="active" />
          <el-option label="停用" value="inactive" />
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-button type="primary" @click="loadList">查询</el-button>
        <el-button type="success" @click="openDialog()">新增台账</el-button>
      </el-col>
    </el-row>

    <el-table :data="list" border stripe>
      <el-table-column type="index" label="序号" width="60" />
      <el-table-column prop="name" label="表计名称" min-width="120" />
      <el-table-column prop="meterNo" label="表计编号" width="130" />
      <el-table-column prop="energyType" label="能源类型" width="90">
        <template #default="{ row }">{{ typeLabel(row.energyType) }}</template>
      </el-table-column>
      <el-table-column prop="building" label="楼宇" width="100" />
      <el-table-column prop="floor" label="楼层" width="80" />
      <el-table-column prop="area" label="区域" width="100" />
      <el-table-column prop="branch" label="分公司" width="100" />
      <el-table-column prop="siteName" label="站点" width="100" />
      <el-table-column prop="unit" label="计量单位" width="80" />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">
            {{ row.status === 'active' ? '在用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="120" />
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="deleteItem(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="query.pageNo"
      v-model:page-size="query.pageSize"
      :total="total"
      layout="total, prev, pager, next"
      style="margin-top: 12px"
      @change="loadList"
    />

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑台账' : '新增台账'" width="620px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="表计名称" required>
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="表计编号">
              <el-input v-model="form.meterNo" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="能源类型" required>
              <el-select v-model="form.energyType" style="width: 100%">
                <el-option label="电能" value="electricity" />
                <el-option label="水能" value="water" />
                <el-option label="气能" value="gas" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计量单位">
              <el-input v-model="form.unit" placeholder="kWh / m³" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="楼宇">
              <el-input v-model="form.building" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="楼层">
              <el-input v-model="form.floor" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="区域">
              <el-input v-model="form.area" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分公司">
              <el-input v-model="form.branch" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="站点">
              <el-input v-model="form.siteName" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="安装日期">
              <el-date-picker v-model="form.installDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="在用" value="active" />
                <el-option label="停用" value="inactive" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input v-model="form.remark" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEnergyLedgerList, doEditEnergyLedger, doDeleteEnergyLedger } from '/@/api/energy'

const list = ref<any[]>([])
const total = ref(0)
const query = ref<any>({ pageNo: 1, pageSize: 20 })
const dialogVisible = ref(false)
const form = ref<any>({ status: 'active' })

function typeLabel(t: string) {
  return { electricity: '电能', water: '水能', gas: '气能' }[t] || t
}

async function loadList() {
  const res = await getEnergyLedgerList(query.value)
  if (res.code === 200) {
    list.value = res.data.list
    total.value = res.data.total
  }
}

function openDialog(row?: any) {
  form.value = row ? { ...row } : { status: 'active' }
  dialogVisible.value = true
}

async function save() {
  if (!form.value.name) return ElMessage.warning('请输入表计名称')
  if (!form.value.energyType) return ElMessage.warning('请选择能源类型')
  const res = await doEditEnergyLedger(form.value)
  if (res.code === 200) {
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadList()
  }
}

async function deleteItem(id: string) {
  await ElMessageBox.confirm('确认删除该台账记录？', '提示', { type: 'warning' })
  const res = await doDeleteEnergyLedger({ id })
  if (res.code === 200) {
    ElMessage.success('删除成功')
    loadList()
  }
}

onMounted(loadList)
</script>

<template>
  <div class="energy-price-container">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="水气价格配置" name="price">
        <el-row :gutter="12" style="margin-bottom: 16px">
          <el-col :span="5">
            <el-select v-model="priceQuery.energyType" clearable placeholder="能源类型" style="width: 100%" @change="loadPrices">
              <el-option label="水" value="water" />
              <el-option label="气" value="gas" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-input v-model="priceQuery.month" clearable placeholder="月份(2025-01)" @keyup.enter="loadPrices" />
          </el-col>
          <el-col :span="5">
            <el-button type="primary" @click="loadPrices">查询</el-button>
            <el-button type="success" @click="openPriceDialog()">新增配置</el-button>
          </el-col>
        </el-row>

        <el-table :data="priceList" border stripe>
          <el-table-column prop="energyType" label="能源类型" width="100">
            <template #default="{ row }">{{ row.energyType === 'water' ? '水' : '气' }}</template>
          </el-table-column>
          <el-table-column prop="month" label="生效月份" width="110">
            <template #default="{ row }">{{ row.month || '默认' }}</template>
          </el-table-column>
          <el-table-column prop="tier1Limit" label="一档用量上限" width="120" />
          <el-table-column prop="tier1Price" label="一档单价" width="100" />
          <el-table-column prop="tier2Limit" label="二档用量上限" width="120" />
          <el-table-column prop="tier2Price" label="二档单价" width="100" />
          <el-table-column prop="tier3Price" label="三档单价" width="100" />
          <el-table-column prop="unit" label="单位" width="80" />
          <el-table-column prop="remark" label="备注" min-width="120" />
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openPriceDialog(row)">编辑</el-button>
              <el-button link type="danger" @click="deletePrice(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="priceDialogVisible" :title="priceForm.id ? '编辑价格配置' : '新增价格配置'" width="520px">
      <el-form :model="priceForm" label-width="120px">
        <el-form-item label="能源类型" required>
          <el-select v-model="priceForm.energyType" style="width: 100%">
            <el-option label="水" value="water" />
            <el-option label="气" value="gas" />
          </el-select>
        </el-form-item>
        <el-form-item label="生效月份">
          <el-input v-model="priceForm.month" placeholder="留空=默认，格式:2025-01" />
        </el-form-item>
        <el-form-item label="一档用量上限（m³）">
          <el-input-number v-model="priceForm.tier1Limit" :min="0" style="width: 100%" controls-position="right" />
        </el-form-item>
        <el-form-item label="一档单价（元）">
          <el-input-number v-model="priceForm.tier1Price" :min="0" :precision="4" style="width: 100%" controls-position="right" />
        </el-form-item>
        <el-form-item label="二档用量上限（m³）">
          <el-input-number v-model="priceForm.tier2Limit" :min="0" style="width: 100%" controls-position="right" />
        </el-form-item>
        <el-form-item label="二档单价（元）">
          <el-input-number v-model="priceForm.tier2Price" :min="0" :precision="4" style="width: 100%" controls-position="right" />
        </el-form-item>
        <el-form-item label="三档单价（元）">
          <el-input-number v-model="priceForm.tier3Price" :min="0" :precision="4" style="width: 100%" controls-position="right" />
        </el-form-item>
        <el-form-item label="计量单位">
          <el-input v-model="priceForm.unit" placeholder="m³ / 元/m³" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="priceForm.remark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="priceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePrice">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEnergyPriceList, doEditEnergyPrice, doDeleteEnergyPrice } from '/@/api/energy'

const activeTab = ref('price')
const priceList = ref<any[]>([])
const priceQuery = ref<any>({})
const priceDialogVisible = ref(false)
const priceForm = ref<any>({ energyType: 'water' })

async function loadPrices() {
  const res = await getEnergyPriceList(priceQuery.value)
  if (res.code === 200) priceList.value = res.data.list
}

function openPriceDialog(row?: any) {
  priceForm.value = row ? { ...row } : { energyType: 'water' }
  priceDialogVisible.value = true
}

async function savePrice() {
  if (!priceForm.value.energyType) return ElMessage.warning('请选择能源类型')
  const res = await doEditEnergyPrice(priceForm.value)
  if (res.code === 200) {
    ElMessage.success('保存成功')
    priceDialogVisible.value = false
    loadPrices()
  }
}

async function deletePrice(id: string) {
  await ElMessageBox.confirm('确认删除该价格配置？', '提示', { type: 'warning' })
  const res = await doDeleteEnergyPrice({ id })
  if (res.code === 200) {
    ElMessage.success('删除成功')
    loadPrices()
  }
}

onMounted(loadPrices)
</script>

<template>
  <div class="energy-elecconfig-container">
    <el-row :gutter="12" style="margin-bottom: 16px">
      <el-col :span="5">
        <el-input v-model="query.branchName" clearable placeholder="分公司名称" @keyup.enter="loadList" />
      </el-col>
      <el-col :span="4">
        <el-button type="primary" @click="loadList">查询</el-button>
        <el-button type="success" @click="openDialog()">新增配置</el-button>
      </el-col>
    </el-row>

    <el-table :data="list" border stripe>
      <el-table-column prop="branchName" label="分公司" min-width="120" />
      <el-table-column label="尖峰时段" width="160">
        <template #default="{ row }">{{ row.sharpStart }}~{{ row.sharpEnd }}</template>
      </el-table-column>
      <el-table-column prop="sharpPrice" label="尖价（元/kWh）" width="130" />
      <el-table-column label="高峰时段" width="160">
        <template #default="{ row }">{{ row.peakStart }}~{{ row.peakEnd }}</template>
      </el-table-column>
      <el-table-column prop="peakPrice" label="峰价（元/kWh）" width="130" />
      <el-table-column label="平时时段" width="160">
        <template #default="{ row }">{{ row.flatStart }}~{{ row.flatEnd }}</template>
      </el-table-column>
      <el-table-column prop="flatPrice" label="平价（元/kWh）" width="130" />
      <el-table-column label="谷时时段" width="160">
        <template #default="{ row }">{{ row.valleyStart }}~{{ row.valleyEnd }}</template>
      </el-table-column>
      <el-table-column prop="valleyPrice" label="谷价（元/kWh）" width="130" />
      <el-table-column prop="monthlyLimit" label="月用量限额（kWh）" width="150" />
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="deleteItem(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑用电配置' : '新增用电配置'" width="640px">
      <el-form :model="form" label-width="140px">
        <el-form-item label="分公司名称" required>
          <el-input v-model="form.branchName" />
        </el-form-item>
        <el-divider>尖峰时段（最高电价）</el-divider>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="尖峰开始">
              <el-time-select v-model="form.sharpStart" start="00:00" step="00:30" end="23:30" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="尖峰结束">
              <el-time-select v-model="form.sharpEnd" start="00:00" step="00:30" end="23:30" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="尖峰单价">
              <el-input-number v-model="form.sharpPrice" :precision="4" :min="0" style="width: 100%" controls-position="right" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider>高峰时段</el-divider>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="峰段开始">
              <el-time-select v-model="form.peakStart" start="00:00" step="00:30" end="23:30" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="峰段结束">
              <el-time-select v-model="form.peakEnd" start="00:00" step="00:30" end="23:30" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="峰段单价">
              <el-input-number v-model="form.peakPrice" :precision="4" :min="0" style="width: 100%" controls-position="right" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider>平时时段</el-divider>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="平段开始">
              <el-time-select v-model="form.flatStart" start="00:00" step="00:30" end="23:30" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="平段结束">
              <el-time-select v-model="form.flatEnd" start="00:00" step="00:30" end="23:30" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="平段单价">
              <el-input-number v-model="form.flatPrice" :precision="4" :min="0" style="width: 100%" controls-position="right" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider>谷时时段（最低电价）</el-divider>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="谷段开始">
              <el-time-select v-model="form.valleyStart" start="00:00" step="00:30" end="23:30" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="谷段结束">
              <el-time-select v-model="form.valleyEnd" start="00:00" step="00:30" end="23:30" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="谷段单价">
              <el-input-number v-model="form.valleyPrice" :precision="4" :min="0" style="width: 100%" controls-position="right" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider />
        <el-form-item label="月用量限额（kWh）">
          <el-input-number v-model="form.monthlyLimit" :min="0" style="width: 100%" controls-position="right" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEnergyElecConfigList, doEditEnergyElecConfig, doDeleteEnergyElecConfig } from '/@/api/energy'

const list = ref<any[]>([])
const query = ref<any>({})
const dialogVisible = ref(false)
const form = ref<any>({})

async function loadList() {
  const res = await getEnergyElecConfigList(query.value)
  if (res.code === 200) list.value = res.data.list
}

function openDialog(row?: any) {
  form.value = row ? { ...row } : {}
  dialogVisible.value = true
}

async function save() {
  if (!form.value.branchName) return ElMessage.warning('请输入分公司名称')
  const res = await doEditEnergyElecConfig(form.value)
  if (res.code === 200) {
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadList()
  }
}

async function deleteItem(id: string) {
  await ElMessageBox.confirm('确认删除该用电配置？', '提示', { type: 'warning' })
  const res = await doDeleteEnergyElecConfig({ id })
  if (res.code === 200) {
    ElMessage.success('删除成功')
    loadList()
  }
}

onMounted(loadList)
</script>

<template>
  <div class="carbon-overview-container">
    <el-card shadow="never" style="margin-bottom: 16px">
      <el-row :gutter="12">
        <el-col :span="5">
          <el-input v-model="query.building" clearable placeholder="建筑名称" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="query.period" placeholder="统计周期" style="width: 100%">
            <el-option label="年" value="year" />
            <el-option label="月" value="month" />
            <el-option label="日" value="day" />
          </el-select>
        </el-col>
        <el-col :span="3">
          <el-input-number v-model="query.year" :min="2020" :max="2030" placeholder="年" style="width: 100%" controls-position="right" />
        </el-col>
        <el-col :span="3">
          <el-select v-model="query.month" clearable placeholder="月" style="width: 100%">
            <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadOverview">查询</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 碳排放总量卡片 -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="8">
        <el-card shadow="never" style="background: linear-gradient(135deg, #667eea, #764ba2); color: #fff">
          <div style="text-align: center; padding: 8px 0">
            <div style="font-size: 36px; font-weight: bold">{{ overview.totalEmission }}</div>
            <div style="font-size: 14px; margin-top: 4px; opacity: 0.9">碳排放总量（tCO₂e）</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" style="background: linear-gradient(135deg, #f093fb, #f5576c); color: #fff">
          <div style="text-align: center; padding: 8px 0">
            <div style="font-size: 36px; font-weight: bold">{{ overview.directEmission }}</div>
            <div style="font-size: 14px; margin-top: 4px; opacity: 0.9">直接排放量（tCO₂e）</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" style="background: linear-gradient(135deg, #4facfe, #00f2fe); color: #fff">
          <div style="text-align: center; padding: 8px 0">
            <div style="font-size: 36px; font-weight: bold">{{ overview.indirectEmission }}</div>
            <div style="font-size: 14px; margin-top: 4px; opacity: 0.9">间接排放量（tCO₂e）</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 历史曲线（表格形式） -->
    <el-card shadow="never">
      <template #header>
        <span>碳排放历史趋势</span>
        <span style="color: #999; font-size: 12px; margin-left: 8px">（基于电力消耗计算，排放因子：0.581 kgCO₂/kWh）</span>
      </template>
      <el-table :data="overview.history" border stripe>
        <el-table-column prop="period" label="时间" width="120" />
        <el-table-column prop="value" label="碳排放量（tCO₂e）" />
        <el-table-column label="趋势" width="200">
          <template #default="{ row, $index }">
            <div style="display: flex; align-items: center; gap: 8px">
              <el-progress
                :percentage="maxEmission > 0 ? Math.round((row.value / maxEmission) * 100) : 0"
                :stroke-width="8"
                style="flex: 1"
              />
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getCarbonOverview } from '/@/api/energy'

const query = ref<any>({ period: 'year', year: new Date().getFullYear() })
const overview = ref<any>({
  totalEmission: 0,
  directEmission: 0,
  indirectEmission: 0,
  history: [],
})

const maxEmission = computed(() => {
  if (!overview.value.history?.length) return 1
  return Math.max(...overview.value.history.map((h: any) => h.value))
})

async function loadOverview() {
  const res = await getCarbonOverview(query.value)
  if (res.code === 200) overview.value = res.data
}

onMounted(loadOverview)
</script>

<template>
  <div class="carbon-trade-container">
    <el-row :gutter="12" style="margin-bottom: 16px">
      <el-col :span="5">
        <el-input v-model="query.building" clearable placeholder="建筑名称" @keyup.enter="loadList" />
      </el-col>
      <el-col :span="5">
        <el-select v-model="query.purchaseType" clearable placeholder="购买类型" style="width: 100%" @change="loadList">
          <el-option label="核证减排量(CER)" value="核证减排量" />
          <el-option label="绿色电力证书(绿证)" value="绿证" />
          <el-option label="国家核证减排量(CCER)" value="CCER" />
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="交易开始日期"
          end-placeholder="交易结束日期"
          value-format="YYYY-MM-DD"
          style="width: 100%"
          @change="onDateChange"
        />
      </el-col>
      <el-col :span="6">
        <el-button type="primary" @click="loadList">查询</el-button>
        <el-button type="success" @click="openDialog()">新增交易</el-button>
        <el-button @click="exportData">导出</el-button>
      </el-col>
    </el-row>

    <el-table :data="list" border stripe>
      <el-table-column prop="building" label="建筑名称" width="120" />
      <el-table-column prop="tradeTime" label="交易时间" width="120">
        <template #default="{ row }">{{ formatDate(row.tradeTime) }}</template>
      </el-table-column>
      <el-table-column prop="effectTime" label="生效时间" width="120">
        <template #default="{ row }">{{ formatDate(row.effectTime) }}</template>
      </el-table-column>
      <el-table-column prop="purchaseType" label="购买类型" width="130" />
      <el-table-column prop="carbonAmount" label="购入碳量（tCO₂e）" width="150" />
      <el-table-column prop="tradePlatform" label="交易平台" min-width="120" />
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
            {{ row.status === 'completed' ? '已完成' : '进行中' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="120" />
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="deleteItem(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="query.pageNo"
      v-model:page-size="query.pageSize"
      :total="total"
      layout="total, prev, pager, next"
      style="margin-top: 12px"
      @change="loadList"
    />

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑碳交易' : '新增碳交易'" width="560px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="建筑名称">
          <el-input v-model="form.building" />
        </el-form-item>
        <el-form-item label="交易时间">
          <el-date-picker v-model="form.tradeTime" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="生效时间">
          <el-date-picker v-model="form.effectTime" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="购买类型">
          <el-select v-model="form.purchaseType" style="width: 100%">
            <el-option label="核证减排量(CER)" value="核证减排量" />
            <el-option label="绿色电力证书(绿证)" value="绿证" />
            <el-option label="国家核证减排量(CCER)" value="CCER" />
          </el-select>
        </el-form-item>
        <el-form-item label="购入碳量（tCO₂e）" required>
          <el-input-number v-model="form.carbonAmount" :min="0" :precision="3" style="width: 100%" controls-position="right" />
        </el-form-item>
        <el-form-item label="交易平台">
          <el-input v-model="form.tradePlatform" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="已完成" value="completed" />
            <el-option label="进行中" value="processing" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCarbonTransactionList, doEditCarbonTransaction, doDeleteCarbonTransaction } from '/@/api/energy'

const list = ref<any[]>([])
const total = ref(0)
const query = ref<any>({ pageNo: 1, pageSize: 20 })
const dateRange = ref<any[]>([])
const dialogVisible = ref(false)
const form = ref<any>({ status: 'completed' })

function formatDate(d: string) {
  return d ? d.slice(0, 10) : '-'
}
function onDateChange(val: any) {
  if (val) {
    query.value.startTime = val[0]
    query.value.endTime = val[1]
  } else {
    delete query.value.startTime
    delete query.value.endTime
  }
}

async function loadList() {
  const res = await getCarbonTransactionList(query.value)
  if (res.code === 200) {
    list.value = res.data.list
    total.value = res.data.total
  }
}

function openDialog(row?: any) {
  form.value = row ? { ...row } : { status: 'completed' }
  dialogVisible.value = true
}

async function save() {
  if (!form.value.carbonAmount) return ElMessage.warning('请输入购入碳量')
  const res = await doEditCarbonTransaction(form.value)
  if (res.code === 200) {
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadList()
  }
}

async function deleteItem(id: string) {
  await ElMessageBox.confirm('确认删除该碳交易记录？', '提示', { type: 'warning' })
  const res = await doDeleteCarbonTransaction({ id })
  if (res.code === 200) {
    ElMessage.success('删除成功')
    loadList()
  }
}

function exportData() {
  ElMessage.info('导出功能开发中')
}

onMounted(loadList)
</script>

<template>
  <div class="carbon-footprint-container">
    <el-row :gutter="12" style="margin-bottom: 16px">
      <el-col :span="5">
        <el-input v-model="query.building" clearable placeholder="建筑名称" @keyup.enter="loadList" />
      </el-col>
      <el-col :span="6">
        <el-button type="primary" @click="loadList">查询</el-button>
        <el-button type="success" @click="openDialog()">新增碳足迹</el-button>
        <el-button @click="exportData">导出</el-button>
      </el-col>
    </el-row>

    <el-table :data="list" border stripe>
      <el-table-column prop="building" label="建筑名称" width="120" />
      <el-table-column prop="productName" label="产品名称" width="120" />
      <el-table-column prop="carbonAmount" label="碳足迹量（tCO₂e）" width="150" />
      <el-table-column prop="perProductCarbon" label="单位产品碳足迹" width="140" />
      <el-table-column prop="unit" label="单位" width="80" />
      <el-table-column label="生产起止时间" width="200">
        <template #default="{ row }">{{ formatDate(row.productStartTime) }} ~ {{ formatDate(row.productEndTime) }}</template>
      </el-table-column>
      <el-table-column label="盘查起止时间" width="200">
        <template #default="{ row }">{{ formatDate(row.checkStartTime) }} ~ {{ formatDate(row.checkEndTime) }}</template>
      </el-table-column>
      <el-table-column prop="conclusion" label="核查结论" min-width="120" />
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="deleteItem(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="query.pageNo"
      v-model:page-size="query.pageSize"
      :total="total"
      layout="total, prev, pager, next"
      style="margin-top: 12px"
      @change="loadList"
    />

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑碳足迹' : '新增碳足迹'" width="600px">
      <el-form :model="form" label-width="130px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="建筑名称">
              <el-input v-model="form.building" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="产品名称">
              <el-input v-model="form.productName" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="碳足迹量（tCO₂e）" required>
              <el-input-number v-model="form.carbonAmount" :min="0" :precision="3" style="width: 100%" controls-position="right" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位产品碳足迹">
              <el-input-number v-model="form.perProductCarbon" :min="0" :precision="4" style="width: 100%" controls-position="right" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="form.unit" placeholder="如：kgCO₂e/件" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="生产起始时间">
              <el-date-picker v-model="form.productStartTime" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="生产结束时间">
              <el-date-picker v-model="form.productEndTime" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="盘查起始时间">
              <el-date-picker v-model="form.checkStartTime" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="盘查结束时间">
              <el-date-picker v-model="form.checkEndTime" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="核查结论">
              <el-input v-model="form.conclusion" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input v-model="form.remark" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCarbonFootprintList, doEditCarbonFootprint, doDeleteCarbonFootprint } from '/@/api/energy'

const list = ref<any[]>([])
const total = ref(0)
const query = ref<any>({ pageNo: 1, pageSize: 20 })
const dialogVisible = ref(false)
const form = ref<any>({})

function formatDate(d: string) {
  return d ? d.slice(0, 10) : '-'
}

async function loadList() {
  const res = await getCarbonFootprintList(query.value)
  if (res.code === 200) {
    list.value = res.data.list
    total.value = res.data.total
  }
}

function openDialog(row?: any) {
  form.value = row ? { ...row } : {}
  dialogVisible.value = true
}

async function save() {
  if (!form.value.carbonAmount) return ElMessage.warning('请输入碳足迹量')
  const res = await doEditCarbonFootprint(form.value)
  if (res.code === 200) {
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadList()
  }
}

async function deleteItem(id: string) {
  await ElMessageBox.confirm('确认删除该碳足迹记录？', '提示', { type: 'warning' })
  const res = await doDeleteCarbonFootprint({ id })
  if (res.code === 200) {
    ElMessage.success('删除成功')
    loadList()
  }
}

function exportData() {
  ElMessage.info('导出功能开发中')
}

onMounted(loadList)
</script>

<template>
  <div class="carbon-curve-container">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="预测设置" name="settings">
        <el-card shadow="never">
          <el-form :model="settingsForm" label-width="140px" style="max-width: 600px">
            <el-form-item label="建筑名称">
              <el-input v-model="settingsForm.building" />
            </el-form-item>
            <el-form-item label="预测场景">
              <el-radio-group v-model="settingsForm.scenario">
                <el-radio value="simulation">模拟场景（每年节能3%）</el-radio>
                <el-radio value="plan">规划场景（每年节能5%）</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="目标达峰年份">
              <el-input-number v-model="settingsForm.targetYear" :min="2025" :max="2060" style="width: 200px" controls-position="right" />
            </el-form-item>
            <el-form-item label="整体节能率（%）">
              <el-input-number v-model="settingsForm.energySavingRate" :min="0" :max="100" style="width: 200px" controls-position="right" />
            </el-form-item>
            <el-form-item label="建筑范围">
              <el-input v-model="settingsForm.buildingScope" placeholder="全部建筑" />
            </el-form-item>
            <el-form-item label="分类节能率">
              <el-input v-model="settingsForm.subItemSavingRate" placeholder="如：空调:30%,照明:20%,新风:15%" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSettings">保存并预测</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="曲线展示" name="curve">
        <el-card shadow="never" style="margin-bottom: 16px">
          <el-row :gutter="12">
            <el-col :span="5">
              <el-input v-model="curveQuery.building" clearable placeholder="建筑名称" />
            </el-col>
            <el-col :span="5">
              <el-select v-model="curveQuery.scenario" placeholder="预测场景" style="width: 100%">
                <el-option label="模拟场景" value="simulation" />
                <el-option label="规划场景" value="plan" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-button type="primary" @click="loadCurve">查询</el-button>
            </el-col>
          </el-row>
        </el-card>

        <el-card shadow="never">
          <template #header>
            <span>双碳预测曲线（{{ curveData.scenario === 'plan' ? '规划场景' : '模拟场景' }}）</span>
          </template>
          <el-table :data="curveData.data" border stripe>
            <el-table-column prop="year" label="年份" width="100" />
            <el-table-column prop="emission" label="预测碳排放（tCO₂e）" />
            <el-table-column label="变化趋势" width="200">
              <template #default="{ row, $index }">
                <div style="display: flex; align-items: center; gap: 8px">
                  <el-progress
                    :percentage="maxCurveVal > 0 ? Math.round((row.emission / maxCurveVal) * 100) : 0"
                    :stroke-width="8"
                    :color="row.emission < 30 ? '#52c41a' : '#409EFF'"
                    style="flex: 1"
                  />
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCarbonCurve, doEditCarbonCurve } from '/@/api/energy'

const activeTab = ref('settings')
const settingsForm = ref<any>({
  scenario: 'simulation',
  targetYear: 2060,
  energySavingRate: 3,
})
const curveQuery = ref<any>({ scenario: 'simulation' })
const curveData = ref<any>({ scenario: 'simulation', data: [] })

const maxCurveVal = computed(() => {
  if (!curveData.value.data?.length) return 1
  return Math.max(...curveData.value.data.map((d: any) => d.emission))
})

async function saveSettings() {
  const res = await doEditCarbonCurve(settingsForm.value)
  if (res.code === 200) {
    ElMessage.success('设置已保存')
    curveQuery.value.scenario = settingsForm.value.scenario
    loadCurve()
    activeTab.value = 'curve'
  }
}

async function loadCurve() {
  const res = await getCarbonCurve(curveQuery.value)
  if (res.code === 200) curveData.value = res.data
}

onMounted(loadCurve)
</script>

<template>
  <div class="carbon-evaluation-container">
    <el-card shadow="never" style="margin-bottom: 16px">
      <el-row :gutter="12">
        <el-col :span="5">
          <el-input v-model="query.building" clearable placeholder="建筑名称" />
        </el-col>
        <el-col :span="5">
          <el-select v-model="query.scenario" clearable placeholder="统计范围" style="width: 100%">
            <el-option label="全部建筑" value="" />
            <el-option label="办公楼" value="office" />
            <el-option label="商业楼" value="commercial" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadData">刷新</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 核心指标 -->
    <el-row :gutter="24" style="margin-bottom: 24px">
      <el-col :span="10">
        <el-card shadow="hover" style="border-left: 4px solid #409eff">
          <div style="display: flex; align-items: center; gap: 16px">
            <div style="font-size: 48px">⚡</div>
            <div>
              <div style="font-size: 36px; font-weight: bold; color: #409eff">{{ evaluation.energyPerArea }}</div>
              <div style="font-size: 16px; color: #666; margin-top: 4px">单位面积能源消耗量（kgace/m²）</div>
              <div style="font-size: 12px; color: #999; margin-top: 4px">1 kWh = 0.1229 kgace（千克标准煤当量）</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover" style="border-left: 4px solid #67c23a">
          <div style="display: flex; align-items: center; gap: 16px">
            <div style="font-size: 48px">👤</div>
            <div>
              <div style="font-size: 36px; font-weight: bold; color: #67c23a">{{ evaluation.energyPerCapita }}</div>
              <div style="font-size: 16px; color: #666; margin-top: 4px">人均能源消耗量（kgace/人）</div>
              <div style="font-size: 12px; color: #999; margin-top: 4px">基于建筑人员数量（默认500人）计算</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 说明 -->
    <el-card shadow="never">
      <template #header><span>评价说明</span></template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="建筑范围">{{ evaluation.building || '全部建筑' }}</el-descriptions-item>
        <el-descriptions-item label="计量单位">{{ evaluation.unit || 'kgace' }}</el-descriptions-item>
        <el-descriptions-item label="单位面积能耗">{{ evaluation.energyPerArea }} kgace/m²</el-descriptions-item>
        <el-descriptions-item label="人均能耗">{{ evaluation.energyPerCapita }} kgace/人</el-descriptions-item>
        <el-descriptions-item label="参考标准" :span="2">
          《民用建筑能耗标准》GB/T 51161-2016：办公建筑约束值 ≤45 kWh/(m²·年)
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCarbonEvaluation } from '/@/api/energy'

const query = ref<any>({})
const evaluation = ref<any>({
  energyPerArea: 0,
  energyPerCapita: 0,
  unit: 'kgace',
})

async function loadData() {
  const res = await getCarbonEvaluation(query.value)
  if (res.code === 200) evaluation.value = res.data
}

onMounted(loadData)
</script>

<template>
  <div class="carbon-decision-container">
    <el-row :gutter="12" style="margin-bottom: 16px">
      <el-col :span="5">
        <el-input v-model="query.building" clearable placeholder="建筑名称" @keyup.enter="loadList" />
      </el-col>
      <el-col :span="6">
        <el-button type="primary" @click="loadList">查询</el-button>
        <el-button type="success" @click="openDialog()">新增决策计划</el-button>
      </el-col>
    </el-row>

    <el-table :data="list" border stripe>
      <el-table-column prop="building" label="建筑名称" width="120" />
      <el-table-column prop="energyConsumption" label="能源消耗值（tce）" width="150" />
      <el-table-column prop="investmentValue" label="预计投资值（万元）" width="150" />
      <el-table-column prop="energySavingRate" label="预计节能率（%）" width="140" />
      <el-table-column prop="energySavingAmount" label="预计节能量（tce）" width="150" />
      <el-table-column prop="carbonReductionAmount" label="预计减碳量（tCO₂e）" width="170" />
      <el-table-column prop="remark" label="备注" min-width="120" />
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="deleteItem(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="query.pageNo"
      v-model:page-size="query.pageSize"
      :total="total"
      layout="total, prev, pager, next"
      style="margin-top: 12px"
      @change="loadList"
    />

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑辅助决策' : '新增辅助决策'" width="560px">
      <el-form :model="form" label-width="160px">
        <el-form-item label="建筑名称">
          <el-input v-model="form.building" />
        </el-form-item>
        <el-form-item label="能源消耗值（tce）">
          <el-input-number v-model="form.energyConsumption" :min="0" :precision="2" style="width: 100%" controls-position="right" />
        </el-form-item>
        <el-form-item label="预计投资值（万元）">
          <el-input-number v-model="form.investmentValue" :min="0" :precision="2" style="width: 100%" controls-position="right" />
        </el-form-item>
        <el-form-item label="预计节能率（%）">
          <el-input-number
            v-model="form.energySavingRate"
            :min="0"
            :max="100"
            :precision="1"
            style="width: 100%"
            controls-position="right"
          />
        </el-form-item>
        <el-form-item label="预计节能量（tce）">
          <el-input-number v-model="form.energySavingAmount" :min="0" :precision="2" style="width: 100%" controls-position="right" />
        </el-form-item>
        <el-form-item label="预计减碳量（tCO₂e）">
          <el-input-number v-model="form.carbonReductionAmount" :min="0" :precision="2" style="width: 100%" controls-position="right" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCarbonDecisionList, doEditCarbonDecision, doDeleteCarbonDecision } from '/@/api/energy'

const list = ref<any[]>([])
const total = ref(0)
const query = ref<any>({ pageNo: 1, pageSize: 20 })
const dialogVisible = ref(false)
const form = ref<any>({})

async function loadList() {
  const res = await getCarbonDecisionList(query.value)
  if (res.code === 200) {
    list.value = res.data.list
    total.value = res.data.total
  }
}

function openDialog(row?: any) {
  form.value = row ? { ...row } : {}
  dialogVisible.value = true
}

async function save() {
  const res = await doEditCarbonDecision(form.value)
  if (res.code === 200) {
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadList()
  }
}

async function deleteItem(id: string) {
  await ElMessageBox.confirm('确认删除该决策记录？', '提示', { type: 'warning' })
  const res = await doDeleteCarbonDecision({ id })
  if (res.code === 200) {
    ElMessage.success('删除成功')
    loadList()
  }
}

onMounted(loadList)
</script>

<template>
  <div class="carbon-assets-container">
    <el-card shadow="never" style="margin-bottom: 16px">
      <el-row :gutter="12">
        <el-col :span="5">
          <el-input v-model="query.building" clearable placeholder="建筑名称" />
        </el-col>
        <el-col :span="6">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
            @change="onDateChange"
          />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 核心指标卡片 -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <el-card shadow="never" style="background: #f0f9ff">
          <div style="text-align: center">
            <div style="font-size: 28px; font-weight: bold; color: #0ea5e9">{{ assets.emissionTarget }}</div>
            <div style="color: #0ea5e9; margin-top: 4px">碳排放目标（tCO₂e）</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" :style="{ background: assets.actualEmission > assets.emissionTarget ? '#fff1f0' : '#f6ffed' }">
          <div style="text-align: center">
            <div
              :style="{
                fontSize: '28px',
                fontWeight: 'bold',
                color: assets.actualEmission > assets.emissionTarget ? '#f5222d' : '#52c41a',
              }"
            >
              {{ assets.actualEmission }}
            </div>
            <div :style="{ color: assets.actualEmission > assets.emissionTarget ? '#f5222d' : '#52c41a', marginTop: '4px' }">
              实际碳排放量（tCO₂e）
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" style="background: #f6ffed">
          <div style="text-align: center">
            <div style="font-size: 28px; font-weight: bold; color: #52c41a">{{ assets.tradeAmount }}</div>
            <div style="color: #52c41a; margin-top: 4px">碳交易量（tCO₂e）</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" style="background: #f9f0ff">
          <div style="text-align: center">
            <div style="font-size: 28px; font-weight: bold; color: #722ed1">{{ assets.carbonNeutral }}</div>
            <div style="color: #722ed1; margin-top: 4px">碳中和量（tCO₂e）</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 对比说明 -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>碳资产 vs 碳排放</span></template>
          <div style="padding: 8px">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px">
              <span>碳排放目标</span>
              <span style="color: #0ea5e9">{{ assets.emissionTarget }} tCO₂e</span>
            </div>
            <el-progress :percentage="100" :stroke-width="14" color="#0ea5e9" />
            <div style="display: flex; justify-content: space-between; margin: 12px 0 8px">
              <span>实际碳排放</span>
              <span :style="{ color: assets.actualEmission > assets.emissionTarget ? '#f5222d' : '#52c41a' }">
                {{ assets.actualEmission }} tCO₂e
              </span>
            </div>
            <el-progress
              :percentage="assets.emissionTarget > 0 ? Math.min(Math.round((assets.actualEmission / assets.emissionTarget) * 100), 100) : 0"
              :stroke-width="14"
              :color="assets.actualEmission > assets.emissionTarget ? '#f5222d' : '#52c41a'"
            />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>碳交易走势</span></template>
          <el-table :data="assets.trend" border size="small">
            <el-table-column prop="period" label="月份" width="100" />
            <el-table-column prop="tradeAmount" label="碳交易量（tCO₂e）" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCarbonAssets } from '/@/api/energy'

const query = ref<any>({})
const dateRange = ref<any[]>([])
const assets = ref<any>({
  emissionTarget: 0,
  actualEmission: 0,
  tradeAmount: 0,
  carbonNeutral: 0,
  trend: [],
})

function onDateChange(val: any) {
  if (val) {
    query.value.startTime = val[0]
    query.value.endTime = val[1]
  } else {
    delete query.value.startTime
    delete query.value.endTime
  }
}

async function loadData() {
  const res = await getCarbonAssets(query.value)
  if (res.code === 200) assets.value = res.data
}

onMounted(loadData)
</script>
```
