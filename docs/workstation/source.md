# 源代码提交页（智能工位管理系统 buildingos.workstation）

## 提交要求
- 提供源程序的连续前30页与连续后30页；不足60页需提供全部源代码
- 每页不少于50行
- 源代码中不得包含公司名称、个人名称、文件名称
- 源代码总数量需与申请表保持一致

## 前30页
请在此粘贴前30页的连续源代码片段，按照页码顺序组织。

```
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

import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  CreateDateColumn,
  ManyToOne,
  JoinColumn,
} from 'typeorm';

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

  @Column({ name: 'start_time', type: 'timestamp' })
  startTime!: Date;

  @Column({ name: 'end_time', type: 'timestamp' })
  endTime!: Date;

  @Column({ length: 20, default: 'active' })
  status!: string;

  @Column({ name: 'check_in_time', type: 'timestamp', nullable: true })
  checkInTime?: Date;

  @Column({ name: 'release_type', length: 20, nullable: true })
  releaseType?: string;

  @CreateDateColumn({ name: 'created_at' })
  createdAt!: Date;
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

  @ApiProperty({
    description: '状态: vacant(空闲), occupied(占用), maintenance(维护中)',
    required: false,
  })
  @IsOptional()
  @IsString()
  status?: string;

  @ApiProperty({
    description: '类型: fixed(固定), shared(共享)',
    required: false,
  })
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
  async invoke<T>(service: string, method: string, ...args: any[]): Promise<T> {
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

import { Controller } from '@nestjs/common';
import { MessagePattern, Payload } from '@nestjs/microservices';

@Controller('workstation-mqtt')
export class WorkstationMqttController {
  @MessagePattern('workstation/#')
  handle(@Payload() data: any) {
    return { code: 200, data };
  }
}

import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { Transport, MicroserviceOptions } from '@nestjs/microservices';

async function startMicro() {
  const app = await NestFactory.create(AppModule);
  const url = process.env.MQTT_BROKER_URL || 'mqtt://localhost:1883';
  await app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.MQTT,
    options: { url, subscribeOptions: { qos: 1 } },
  });
  await app.startAllMicroservices();
}
startMicro();

import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as swagger from '@nestjs/swagger';
import { Transport, MicroserviceOptions } from '@nestjs/microservices';
import { Logger } from '@nestjs/common';

async function bootstrap() {
  const logger = new Logger('WorkstationBootstrap');
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
    logger.warn(`MQTT connect failed: ${String(e)}`);
  }

  const config = new swagger.DocumentBuilder()
    .setTitle('Workstation API')
    .setDescription('工位管理接口文档')
    .setVersion('1.0')
    .addBearerAuth()
    .build();
  const doc = swagger.SwaggerModule.createDocument(app, config);
  swagger.SwaggerModule.setup('workstation/docs', app, doc);

  const port = parseInt(process.env.PORT || '3024', 10);
  await app.listen(port);
  logger.log(`Workstation service running on port ${port}`);
}
void bootstrap();

import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { JwtModule } from '@nestjs/jwt';
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
    JwtModule.register({
      secret: process.env.JWT_SECRET || 'BuildingOS',
      signOptions: { expiresIn: '7d' },
    }),
    TypeOrmModule.forRootAsync({
      useFactory: () => {
        const dbType = (process.env.DB_TYPE || 'sqlite').toLowerCase();
        if (dbType === 'postgres') {
          return {
            type: 'postgres' as const,
            host: process.env.DB_HOST || 'localhost',
            port: parseInt(process.env.DB_PORT || '5432', 10),
            username: process.env.DB_USER || 'postgres',
            password: process.env.DB_PASSWORD || 'buildingos',
            database: process.env.DB_NAME || 'buildingos',
            entities: [WorkstationEntity, WorkstationBookingEntity],
            synchronize: true,
          };
        }
        if (dbType === 'mysql') {
          return {
            type: 'mysql' as const,
            host: process.env.DB_HOST || 'localhost',
            port: parseInt(process.env.DB_PORT || '3306', 10),
            username: process.env.DB_USER || 'root',
            password: process.env.DB_PASSWORD || '',
            database: process.env.DB_NAME || 'buildingos',
            entities: [WorkstationEntity, WorkstationBookingEntity],
            synchronize: true,
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
            url: config.get('MQTT_BROKER_URL') || 'mqtt://localhost:1883',
            username: config.get('MQTT_USERNAME'),
            password: config.get('MQTT_PASSWORD'),
            subscribeOptions: { qos: 1 },
            clientId:
              'buildingos_microservice_workstation_' +
              Math.random().toString(16).slice(2, 8),
          },
        }),
      },
    ]),
  ],
  controllers: [WorkstationController, WorkstationMqttController],
  providers: [WorkstationService, HostBridge],
})
export class AppModule {}

import {
  Controller,
  Get,
  Post,
  Body,
  Query,
  UseGuards,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBody, ApiQuery, ApiBearerAuth } from '@nestjs/swagger';
import { WorkstationService } from './workstation.service';
import { QueryWorkstationDto } from './dto/query-workstation.dto';
import { AllocateWorkstationDto } from './dto/allocate-workstation.dto';
import { CreateBookingDto } from './dto/create-booking.dto';
import { QueryBookingDto } from './dto/query-booking.dto';
import { JwtAuthGuard } from './auth/jwt.guard';
import { Public } from './auth/public.decorator';

@ApiTags('工位管理')
@Controller()
@UseGuards(JwtAuthGuard)
export class WorkstationController {
  constructor(private readonly service: WorkstationService) {}

  @Get('health')
  @Public()
  @ApiOperation({ summary: '健康检查' })
  health() {
    return { status: 'ok' };
  }

  @Get('menu.json')
  @Public()
  @ApiOperation({ summary: '获取菜单' })
  menuJson() {
    return require('../menu.json');
  }

  @Get('fixed')
  @ApiBearerAuth()
  @ApiOperation({ summary: '查询固定工位列表' })
  async findAll(@Query() query: QueryWorkstationDto) {
    const result = await this.service.findAll(query);
    return { code: 200, data: result };
  }

  @Post('fixed/allocate')
  @ApiBearerAuth()
  @ApiOperation({ summary: '批量分配固定工位' })
  async allocate(@Body() dto: AllocateWorkstationDto) {
    await this.service.allocate(dto);
    return { code: 200, message: 'success' };
  }

  @Post('fixed/release')
  @ApiBearerAuth()
  @ApiOperation({ summary: '释放固定工位' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: { id: { type: 'string', description: '工位ID或编号' } },
    },
  })
  async release(@Body() body: { id: string | number }) {
    await this.service.release(body.id);
    return { code: 200, message: 'success' };
  }

  @Get('shared/available')
  @ApiBearerAuth()
  @ApiOperation({ summary: '查询可用共享工位' })
  @ApiQuery({ name: 'date', required: true, description: '日期 (YYYY-MM-DD)' })
  @ApiQuery({ name: 'startTime', required: false, description: '开始时间' })
  @ApiQuery({ name: 'endTime', required: false, description: '结束时间' })
  async findAvailable(
    @Query('date') date: string,
    @Query('startTime') startTime?: string,
    @Query('endTime') endTime?: string,
  ) {
    const result = await this.service.findAvailable(date, startTime, endTime);
    return { code: 200, data: result };
  }

  @Post('booking')
  @ApiBearerAuth()
  @ApiOperation({ summary: '预定共享工位' })
  async createBooking(@Body() dto: CreateBookingDto) {
    const result = await this.service.createBooking(dto);
    return { code: 200, data: result };
  }

  @Get('bookings')
  @ApiBearerAuth()
  @ApiOperation({ summary: '查询预定记录' })
  async findBookings(@Query() query: QueryBookingDto) {
    const result = await this.service.findBookings(query);
    return { code: 200, data: result };
  }

  @Post('booking/cancel')
  @ApiBearerAuth()
  @ApiOperation({ summary: '取消预定' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: { id: { type: 'string', description: '预定记录ID' } },
    },
  })
  async cancelBooking(@Body() body: { id: string | number }) {
    await this.service.cancelBooking(body.id);
    return { code: 200, message: 'success' };
  }

  @Get('stats')
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取工位统计数据' })
  async getStatistics() {
    const result = await this.service.getStatistics();
    return { code: 200, data: result };
  }
}

import {
  Injectable,
  Logger,
  OnModuleInit,
  BadRequestException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import {
  Repository,
  DataSource,
  In,
} from 'typeorm';
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

  async findAll(query: QueryWorkstationDto) {
    const page = query.page || 1;
    const pageSize = query.pageSize || 10;
    const skip = (page - 1) * pageSize;

    const qb = this.workstationRepo.createQueryBuilder('ws');

    if (query.code) {
      qb.andWhere('ws.code LIKE :code', { code: `%${query.code}%` });
    }
    if (query.department) {
      qb.andWhere('ws.departmentId LIKE :dept', {
        dept: `%${query.department}%`,
      });
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
    const workstations = await this.workstationRepo.findBy({
      code: In(dto.ids),
    });

    if (workstations.length === 0) {
      const numericIds = dto.ids
        .map((id) => parseInt(id))
        .filter((n) => !isNaN(n));
      if (numericIds.length > 0) {
        const byId = await this.workstationRepo.findBy({ id: In(numericIds) });
        workstations.push(...byId);
      }
    }

    const uniqueWs = Array.from(new Set(workstations.map((w) => w.id))).map(
      (id) => workstations.find((w) => w.id === id)!,
    );

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

  async findAvailable(date: string, startTime?: string, endTime?: string) {
    const sharedWs = await this.workstationRepo.find({
      where: { type: 'shared' },
    });

    if (!startTime || !endTime) {
      return { list: sharedWs };
    }

    const start = new Date(startTime);
    const end = new Date(endTime);

    const conflictingBookings = await this.bookingRepo
      .createQueryBuilder('booking')
      .where('booking.status = :status', { status: 'active' })
      .andWhere('booking.startTime < :end', { end })
      .andWhere('booking.endTime > :start', { start })
      .select('booking.workstationId')
      .getRawMany();

    const busyIds = conflictingBookings.map((b) => {
      return Object.values(b)[0];
    });

    const available = sharedWs.filter((ws) => !busyIds.includes(ws.id));

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

    const conflict = await this.bookingRepo
      .createQueryBuilder('booking')
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

    const qb = this.bookingRepo
      .createQueryBuilder('booking')
      .leftJoinAndSelect('booking.workstation', 'ws')
      .orderBy('booking.createdAt', 'DESC');

    if (query.user) {
      qb.andWhere('booking.userId LIKE :user', { user: `%${query.user}%` });
    }

    if (query.date) {
      const dStart = new Date(query.date);
      dStart.setHours(0, 0, 0, 0);
      const dEnd = new Date(query.date);
      dEnd.setHours(23, 59, 59, 999);
      qb.andWhere('booking.startTime BETWEEN :dStart AND :dEnd', {
        dStart,
        dEnd,
      });
    }

    qb.skip(skip).take(pageSize);
    const [list, total] = await qb.getManyAndCount();
    return { list, total, page, pageSize };
  }

  async cancelBooking(id: string | number) {
    const booking = await this.bookingRepo.findOne({
      where: { id: Number(id) },
    });
    if (!booking) throw new BadRequestException('Booking not found');

    booking.status = 'cancelled';
    await this.bookingRepo.save(booking);

    const now = new Date();
    if (now >= booking.startTime && now <= booking.endTime) {
      await this.workstationRepo.update(booking.workstationId, {
        status: 'vacant',
      });
    }

    return { success: true };
  }

  async getStatistics() {
    const total = await this.workstationRepo.count();
    const occupied = await this.workstationRepo.count({
      where: { status: 'occupied' },
    });

    const releaseCount = 25;

    const bookingTrend = [{ date: '2023-10-14', count: 45 }];

    const departmentUsage = await this.workstationRepo
      .createQueryBuilder('ws')
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
        releaseCount,
      },
      bookingTrend,
      departmentUsage,
    };
  }
}

[
  {
    "path": "/workstation",
    "name": "WorkStation",
    "component": "Layout",
    "meta": {
      "title": "工位",
      "icon": "pass-valid-line",
      "guard": ["Admin"]
    },
    "children": [
      {
        "path": "map",
        "name": "MapManagement",
        "component": "/@/views/workstation/map/index.vue",
        "meta": {
          "title": "地图管理",
          "guard": ["Admin"]
        }
      },
      {
        "path": "fixed",
        "name": "FixedAllocation",
        "component": "/@/views/workstation/fixed/index.vue",
        "meta": {
          "title": "固定工位",
          "guard": ["Admin"]
        }
      },
      {
        "path": "booking",
        "name": "SharedBooking",
        "component": "/@/views/workstation/booking/index.vue",
        "meta": {
          "title": "共享预定",
          "guard": ["Admin"]
        }
      },
      {
        "path": "screen",
        "name": "StatusScreen",
        "component": "/@/views/workstation/screen/index.vue",
        "meta": {
          "title": "工位大屏",
          "guard": ["Admin"]
        }
      },
      {
        "path": "statistics",
        "name": "WorkstationStatistics",
        "component": "/@/views/workstation/statistics/index.vue",
        "meta": {
          "title": "工位统计",
          "guard": ["Admin"]
        }
      }
    ]
  }
]
```

## 后30页
请在此粘贴后30页的连续源代码片段，按照页码顺序组织。

```
<template>
  <div>
    <vab-card>
      <div class="header-row">
        <span class="page-title">工位可视化</span>
        <div class="header-right">
          <el-select v-model="currentFloor" placeholder="选择楼层" @change="handleFloorChange">
            <el-option v-for="item in floorList" :key="item.floorCode" :label="item.floorName" :value="item.floorCode" />
          </el-select>
          <el-button type="primary" :icon="Refresh" @click="refreshMap">刷新</el-button>
        </div>
      </div>

      <el-row :gutter="16" class="stats-row">
        <el-col :span="6">
          <div class="stat-card stat-total" @click="pointFilter = 'all'">
            <div class="stat-value">{{ allWorkstations.length }}</div>
            <div class="stat-label">总工位</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card stat-vacant" @click="pointFilter = 'vacant'">
            <div class="stat-value">{{ vacantCount }}</div>
            <div class="stat-label">空闲工位</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card stat-occupied" @click="pointFilter = 'occupied'">
            <div class="stat-value">{{ occupiedCount }}</div>
            <div class="stat-label">已占用</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card stat-rate">
            <div class="stat-value">{{ usageRate }}%</div>
            <div class="stat-label">使用率</div>
          </div>
        </el-col>
      </el-row>

      <div class="legend-bar">
        <div class="legend-item">
          <span class="dot dot-vacant"></span>空闲
        </div>
        <div class="legend-item">
          <span class="dot dot-occupied"></span>占用
        </div>
        <div class="legend-item">
          <span class="dot dot-maintenance"></span>维修中
        </div>
        <div class="legend-item">
          <span class="dot dot-selected"></span>已选中
        </div>
      </div>

      <el-row :gutter="16">
        <el-col :xs="24" :lg="17">
          <div id="workstationMap" class="map-container"></div>
        </el-col>

        <el-col :xs="24" :lg="7">
          <el-tabs v-model="activeTab" class="right-tabs">
            <el-tab-pane label="工位列表" name="list">
              <div class="filter-bar">
                <el-radio-group v-model="pointFilter" size="small">
                  <el-radio-button value="all">全部</el-radio-button>
                  <el-radio-button value="vacant">空闲</el-radio-button>
                  <el-radio-button value="occupied">占用</el-radio-button>
                  <el-radio-button value="maintenance">维修中</el-radio-button>
                </el-radio-group>
              </div>
              <el-scrollbar max-height="calc(100vh - 380px)">
                <div v-for="item in filteredWorkstations" :key="item.id" class="ws-item">
                  <div class="ws-left">
                    <span class="ws-dot" :class="'dot-' + item.status"></span>
                    <div class="ws-info">
                      <div class="ws-code">{{ item.code }}</div>
                      <div class="ws-meta">
                        <span class="ws-location">{{ item.location }}</span>
                        <el-tag :type="statusTagMap[item.status]" size="small">{{ statusLabelMap[item.status] }}</el-tag>
                      </div>
                      <div v-if="item.userName" class="ws-user">
                        <el-icon><user /></el-icon>
                        {{ item.userName }}
                      </div>
                    </div>
                  </div>
                  <div class="ws-actions">
                    <el-button size="small" @click="flyToWorkstation(item)">定位</el-button>
                    <el-button v-if="item.status === 'vacant'" size="small" type="primary" @click="handleQuickAllocate(item)">分配</el-button>
                    <el-button v-if="item.status === 'occupied'" size="small" type="warning" @click="handleQuickRelease(item)">释放</el-button>
                  </div>
                </div>
                <el-empty v-if="filteredWorkstations.length === 0" description="暂无工位" />
              </el-scrollbar>
            </el-tab-pane>

            <el-tab-pane label="快速操作" name="actions">
              <div class="action-panel">
                <el-button type="primary" size="large" style="width: 100%; margin-bottom: 12px" @click="handleQuickBook">
                  <el-icon><plus /></el-icon>
                  一键预定最近空闲工位
                </el-button>
                <el-button type="success" size="large" style="width: 100%; margin-bottom: 12px" @click="handleBatchRelease">
                  <el-icon><refresh /></el-icon>
                  批量释放当前楼层
                </el-button>
                <el-divider />
                <div class="floor-summary">
                  <p><strong>{{ currentFloor || '-' }}</strong>楼层概况</p>
                  <el-descriptions :column="1" size="small" border>
                    <el-descriptions-item label="总工位">{{ currentFloorWorkstations.length }}</el-descriptions-item>
                    <el-descriptions-item label="空闲">{{ currentFloorVacant }}</el-descriptions-item>
                    <el-descriptions-item label="占用">{{ currentFloorOccupied }}</el-descriptions-item>
                    <el-descriptions-item label="维修中">{{ currentFloorMaintenance }}</el-descriptions-item>
                  </el-descriptions>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-col>
      </el-row>
    </vab-card>

    <el-dialog v-model="allocateDialogVisible" title="分配工位" width="450px" destroy-on-close>
      <el-form :model="allocateForm" label-width="100px">
        <el-form-item label="工位编号">
          <el-input :model-value="allocateForm.code" disabled />
        </el-form-item>
        <el-form-item label="分配人员" prop="userName">
          <el-select v-model="allocateForm.userName" filterable placeholder="请选择人员">
            <el-option v-for="u in mockUsers" :key="u" :label="u" :value="u" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属部门" prop="department">
          <el-select v-model="allocateForm.department" filterable placeholder="请选择部门">
            <el-option v-for="d in mockDepts" :key="d" :label="d" :value="d" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="allocateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAllocate">确认分配</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { storeToRefs } from 'pinia'
import { getSpaceFloorList } from '/@/api/space'
import { useUserStore } from '/@/store/modules/user'
import { getFloorMapUrl } from '/@/utils/index'
import { Plus, Refresh, User } from '@element-plus/icons-vue'

defineOptions({ name: 'WorkstationScreen' })

const userStore = useUserStore()
const { spaceCode } = storeToRefs(userStore)
const $baseMessage = inject<any>('$baseMessage')
const $baseConfirm = inject<any>('$baseConfirm')

const map = ref<any>(null)
const floorList = ref<any[]>([])
const currentFloor = ref<string>('')
const activeTab = ref<string>('list')
const pointFilter = ref<string>('all')
const markersMap = new Map<string, any>()
const allocateDialogVisible = ref(false)
const allocateForm = reactive({ id: '', code: '', userName: '', department: '' })

const mockUsers = ['张三', '李四', '王五', '赵六', '陈七', '周八', '刘九', '吴十']
const mockDepts = ['研发部', '产品部', '设计部', '市场部', '行政部', '运营部']

const statusColors: Record<string, string> = {
  vacant: '#67C23A',
  occupied: '#F56C6C',
  maintenance: '#E6A23C',
}

const statusLabelMap: Record<string, string> = {
  vacant: '空闲',
  occupied: '占用',
  maintenance: '维修中',
}

const statusTagMap: Record<string, string> = {
  vacant: 'success',
  occupied: 'danger',
  maintenance: 'warning',
}

const mockWorkstations = [
  {
    id: 'ws-01', code: 'A-1F-001', type: 'fixed', floor: '1F',
    status: 'occupied', position: { x: -18, z: 10 },
    location: '1F 开放办公区A', userName: '张三', department: '研发部',
  },
  {
    id: 'ws-02', code: 'A-1F-002', type: 'fixed', floor: '1F',
    status: 'occupied', position: { x: -15, z: 10 },
    location: '1F 开放办公区A', userName: '李四', department: '产品部',
  },
  {
    id: 'ws-03', code: 'A-1F-003', type: 'shared', floor: '1F',
    status: 'vacant', position: { x: -12, z: 10 },
    location: '1F 开放办公区A', userName: '', department: '',
  },
  {
    id: 'ws-04', code: 'A-1F-004', type: 'fixed', floor: '1F',
    status: 'vacant', position: { x: -9, z: 10 },
    location: '1F 开放办公区A', userName: '', department: '',
  },
  {
    id: 'ws-05', code: 'A-1F-005', type: 'shared', floor: '1F',
    status: 'maintenance', position: { x: -6, z: 10 },
    location: '1F 开放办公区A', userName: '', department: '',
  },
  {
    id: 'ws-06', code: 'A-1F-006', type: 'fixed', floor: '1F',
    status: 'occupied', position: { x: -18, z: 6 },
    location: '1F 开放办公区B', userName: '王五', department: '研发部',
  },
  {
    id: 'ws-07', code: 'A-1F-007', type: 'shared', floor: '1F',
    status: 'vacant', position: { x: -15, z: 6 },
    location: '1F 开放办公区B', userName: '', department: '',
  },
  {
    id: 'ws-08', code: 'A-1F-008', type: 'fixed', floor: '1F',
    status: 'vacant', position: { x: -12, z: 6 },
    location: '1F 开放办公区B', userName: '', department: '',
  },
  {
    id: 'ws-09', code: 'A-1F-009', type: 'fixed', floor: '1F',
    status: 'occupied', position: { x: -9, z: 6 },
    location: '1F 开放办公区B', userName: '赵六', department: '设计部',
  },
  {
    id: 'ws-10', code: 'A-1F-010', type: 'shared', floor: '1F',
    status: 'vacant', position: { x: -6, z: 6 },
    location: '1F 开放办公区B', userName: '', department: '',
  },
  {
    id: 'ws-11', code: 'A-1F-011', type: 'fixed', floor: '1F',
    status: 'occupied', position: { x: 5, z: 10 },
    location: '1F 独立办公室', userName: '陈七', department: '市场部',
  },
  {
    id: 'ws-12', code: 'A-1F-012', type: 'fixed', floor: '1F',
    status: 'maintenance', position: { x: 8, z: 10 },
    location: '1F 独立办公室', userName: '', department: '',
  },
  {
    id: 'ws-21', code: 'A-2F-001', type: 'fixed', floor: '2F',
    status: 'occupied', position: { x: -10, z: 8 },
    location: '2F 开放办公区', userName: '周八', department: '研发部',
  },
  {
    id: 'ws-22', code: 'A-2F-002', type: 'fixed', floor: '2F',
    status: 'vacant', position: { x: -7, z: 8 },
    location: '2F 开放办公区', userName: '', department: '',
  },
  {
    id: 'ws-23', code: 'A-2F-003', type: 'shared', floor: '2F',
    status: 'occupied', position: { x: -4, z: 8 },
    location: '2F 开放办公区', userName: '刘九', department: '运营部',
  },
  {
    id: 'ws-24', code: 'A-2F-004', type: 'fixed', floor: '2F',
    status: 'vacant', position: { x: -1, z: 8 },
    location: '2F 开放办公区', userName: '', department: '',
  },
  {
    id: 'ws-25', code: 'A-2F-005', type: 'shared', floor: '2F',
    status: 'vacant', position: { x: 2, z: 8 },
    location: '2F 开放办公区', userName: '', department: '',
  },
  {
    id: 'ws-26', code: 'A-2F-006', type: 'fixed', floor: '2F',
    status: 'occupied', position: { x: 5, z: 8 },
    location: '2F 开放办公区', userName: '吴十', department: '行政部',
  },
  {
    id: 'ws-27', code: 'A-2F-007', type: 'fixed', floor: '2F',
    status: 'maintenance', position: { x: -10, z: 4 },
    location: '2F 独立办公室', userName: '', department: '',
  },
  {
    id: 'ws-28', code: 'A-2F-008', type: 'shared', floor: '2F',
    status: 'vacant', position: { x: -7, z: 4 },
    location: '2F 独立办公室', userName: '', department: '',
  },
  {
    id: 'ws-31', code: 'A-3F-001', type: 'fixed', floor: '3F',
    status: 'vacant', position: { x: 0, z: 5 },
    location: '3F 行政办公区', userName: '', department: '',
  },
  {
    id: 'ws-32', code: 'A-3F-002', type: 'shared', floor: '3F',
    status: 'occupied', position: { x: 3, z: 5 },
    location: '3F 行政办公区', userName: '张三', department: '研发部',
  },
  {
    id: 'ws-33', code: 'A-3F-003', type: 'fixed', floor: '3F',
    status: 'vacant', position: { x: 6, z: 5 },
    location: '3F 行政办公区', userName: '', department: '',
  },
]

const allWorkstations = computed(() => mockWorkstations)

const filteredWorkstations = computed(() => {
  const floor = currentFloor.value
  if (pointFilter.value === 'all') {
    return allWorkstations.value.filter((w) => w.floor === floor)
  }
  return allWorkstations.value.filter((w) => w.floor === floor && w.status === pointFilter.value)
})

const currentFloorWorkstations = computed(() =>
  allWorkstations.value.filter((w) => w.floor === currentFloor.value)
)

const vacantCount = computed(() => allWorkstations.value.filter((w) => w.status === 'vacant').length)
const occupiedCount = computed(() => allWorkstations.value.filter((w) => w.status === 'occupied').length)
const maintenanceCount = computed(() => allWorkstations.value.filter((w) => w.status === 'maintenance').length)

const currentFloorVacant = computed(() =>
  currentFloorWorkstations.value.filter((w) => w.status === 'vacant').length
)
const currentFloorOccupied = computed(() =>
  currentFloorWorkstations.value.filter((w) => w.status === 'occupied').length
)
const currentFloorMaintenance = computed(() =>
  currentFloorWorkstations.value.filter((w) => w.status === 'maintenance').length
)

const usageRate = computed(() => {
  const total = allWorkstations.value.length
  if (total === 0) return 0
  return ((occupiedCount.value / total) * 100).toFixed(1)
})

function createColorIcon(color: string, size = 36): string {
  const canvas = document.createElement('canvas')
  canvas.width = size
  canvas.height = size
  const ctx = canvas.getContext('2d')
  if (!ctx) return ''

  ctx.shadowColor = color
  ctx.shadowBlur = 6

  ctx.beginPath()
  ctx.arc(size / 2, size / 2, size / 2 - 3, 0, Math.PI * 2)
  ctx.fillStyle = color
  ctx.fill()

  ctx.shadowBlur = 0
  ctx.strokeStyle = '#ffffff'
  ctx.lineWidth = 2
  ctx.stroke()

  return canvas.toDataURL()
}

function getFloorName(floorCode: string): string {
  return floorCode.toLowerCase()
}

function initMap(floorCode: string) {
  if (map.value) {
    map.value.dispose()
    map.value = null
  }

  const container = document.getElementById('workstationMap')
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
    font: { fontscale: 200, iconScale: 5, indent: 100 },
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

  const color = statusColors[item.status] || '#909399'
  const iconUrl = createColorIcon(color, 36)

  const marker = new AirocovMap.covers.ImageMarker({
    name: 'workstation',
    imgSrc: iconUrl,
    size: 36,
    position: {
      x: Number(item.position.x),
      y: 2,
      z: Number(item.position.z || 0),
    },
    userData: item,
    canvasHeight: map.value.dom.offsetHeight,
    info: `${item.code}\n${statusLabelMap[item.status]}${item.userName ? ' | ' + item.userName : ''}`,
    fontSize: 24,
    callback: function (marker: any) {
      markersMap.set(item.id, marker)
      marker.material.depthTest = false
      map.value.addToMap({
        object: marker,
        floorName: getFloorName(item.floor),
        layerName: 'workstation',
        isClick: true,
      })
    },
  })
}

function addAllMarkers() {
  markersMap.clear()
  allWorkstations.value.forEach((item) => {
    if (item.floor === currentFloor.value) {
      addMarker(item)
    }
  })
}

function handleFloorChange(val: string) {
  currentFloor.value = val
  initMap(val)
}

function refreshMap() {
  if (currentFloor.value) {
    initMap(currentFloor.value)
    $baseMessage?.success('地图已刷新')
  }
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

function flyToWorkstation(item: any) {
  if (item.floor !== currentFloor.value) {
    currentFloor.value = item.floor
    initMap(item.floor)
    setTimeout(() => flyCameraTo(item.position), 2000)
  } else {
    flyCameraTo(item.position)
  }
}

function handleMapClick(e: any) {
  if (e.type === 'ImageMarker' && e.target && e.target.info === 'workstation') {
    const data = e.target.userData
    if (data) {
      $baseMessage?.info(
        `${data.code} — ${statusLabelMap[data.status]}${data.userName ? ' | ' + data.userName : ''}`
      )
    }
  }
}

function handleQuickAllocate(item: any) {
  allocateForm.id = item.id
  allocateForm.code = item.code
  allocateForm.userName = ''
  allocateForm.department = ''
  allocateDialogVisible.value = true
}

function confirmAllocate() {
  if (!allocateForm.userName || !allocateForm.department) {
    $baseMessage?.warning('请选择人员和部门')
    return
  }
  const ws = mockWorkstations.find((w) => w.id === allocateForm.id)
  if (ws) {
    ws.status = 'occupied'
    ws.userName = allocateForm.userName
    ws.department = allocateForm.department
  }
  $baseMessage?.success(`工位 ${allocateForm.code} 已分配给 ${allocateForm.userName}`)
  allocateDialogVisible.value = false
  refreshMap()
}

function handleQuickRelease(item: any) {
  $baseConfirm?.(`确认释放工位 ${item.code}（当前使用人：${item.userName}）？`, '释放确认', {
    type: 'warning',
  })
    .then(() => {
      const ws = mockWorkstations.find((w) => w.id === item.id)
      if (ws) {
        ws.status = 'vacant'
        ws.userName = ''
        ws.department = ''
      }
      $baseMessage?.success(`工位 ${item.code} 已释放`)
      refreshMap()
    })
    .catch(() => {})
}

function handleQuickBook() {
  const nearest = mockWorkstations.find((w) => w.floor === currentFloor.value && w.status === 'vacant')
  if (nearest) {
    $baseConfirm?.(`确认预定工位 ${nearest.code}（${nearest.location}）？`, '快速预定', {
      type: 'info',
    })
      .then(() => {
        nearest.status = 'occupied'
        nearest.userName = '当前用户'
        $baseMessage?.success(`已预定工位 ${nearest.code}`)
        refreshMap()
      })
      .catch(() => {})
  } else {
    $baseMessage?.warning('当前楼层暂无空闲工位')
  }
}

function handleBatchRelease() {
  const occupiedList = currentFloorWorkstations.value.filter((w) => w.status === 'occupied')
  if (occupiedList.length === 0) {
    $baseMessage?.info('当前楼层无已占用工位')
    return
  }
  $baseConfirm?.(
    `确认释放 ${currentFloor.value} 全部 ${occupiedList.length} 个已占用工位？`,
    '批量释放',
    { type: 'warning' },
  )
    .then(() => {
      occupiedList.forEach((w) => {
        w.status = 'vacant'
        w.userName = ''
        w.department = ''
      })
      $baseMessage?.success(`已释放 ${occupiedList.length} 个工位`)
      refreshMap()
    })
    .catch(() => {})
}

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

.stats-row {
  margin-bottom: 16px;

  .stat-card {
    padding: 16px;
    border-radius: 8px;
    cursor: pointer;
    text-align: center;
    transition: all 0.2s;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .stat-value {
      font-size: 28px;
      font-weight: 700;
    }

    .stat-label {
      font-size: 13px;
      color: var(--el-text-color-secondary);
      margin-top: 4px;
    }
  }

  .stat-total {
    background: rgba(64, 158, 255, 0.1);
    .stat-value { color: #409eff; }
  }
  .stat-vacant {
    background: rgba(103, 194, 58, 0.1);
    .stat-value { color: #67c23a; }
  }
  .stat-occupied {
    background: rgba(245, 108, 108, 0.1);
    .stat-value { color: #f56c6c; }
  }
  .stat-rate {
    background: rgba(230, 162, 60, 0.1);
    .stat-value { color: #e6a23c; }
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

    &-vacant { background: #67c23a; }
    &-occupied { background: #f56c6c; }
    &-maintenance { background: #e6a23c; }
    &-selected {
      background: #409eff;
      box-shadow: 0 0 6px #409eff;
    }
  }
}

.map-container {
  width: 100%;
  height: calc(100vh - 360px);
  min-height: 500px;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.right-tabs { height: 100%; }

.filter-bar { margin-bottom: 12px; }

.ws-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);

  &:last-child { border-bottom: none; }

  .ws-left {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    flex: 1;
    min-width: 0;
  }

  .ws-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 4px;

    &.dot-vacant { background: #67c23a; }
    &.dot-occupied { background: #f56c6c; }
    &.dot-maintenance { background: #e6a23c; }
  }

  .ws-info { flex: 1; min-width: 0; }

  .ws-code {
    font-size: 14px;
    font-weight: 500;
    color: var(--el-text-color-primary);
  }

  .ws-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 2px;
  }

  .ws-location {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .ws-user {
    font-size: 12px;
    color: var(--el-color-primary);
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 2px;
  }

  .ws-actions {
    display: flex;
    gap: 4px;
    flex-shrink: 0;
    margin-left: 8px;
  }
}

.action-panel { padding: 8px 0; }

.floor-summary {
  p { margin-bottom: 8px; font-size: 14px; }
}
</style>

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
              <el-col v-for="ws in workstations" :key="ws.id" :span="6">
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
  user: '',
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
    background-color: var(--el-bg-color);
    border: 1px solid var(--el-border-color-light);
    color: var(--el-text-color-primary);

    .ws-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: bold;
      margin-bottom: 10px;
    }
    .ws-info {
      font-size: 13px;
      color: var(--el-text-color-regular);
      margin-bottom: 15px;
      .features { margin-top: 5px; }
    }
    .ws-action {
      display: flex;
      justify-content: flex-end;
      align-items: center;
      .next-time {
        font-size: 12px;
        color: var(--el-text-color-secondary);
      }
    }

    &.available {
      border-top: 3px solid var(--el-color-success);
    }
    &.booked {
      border-top: 3px solid var(--el-text-color-secondary);
      background-color: var(--el-fill-color-light);
    }
  }
}
</style>

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
  status: '',
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
    type: 'warning',
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
  name: '',
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
  ElMessage.info(`进入地图设计器: ${row.name}`)
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm('确认删除?', '提示', {
    type: 'warning',
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
  <div class="statistics-container no-background-container">
    <el-row :gutter="20" style="margin-bottom: 20px">
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
            <div class="value">{{ data.bookingTrend ? data.bookingTrend[data.bookingTrend.length - 1].count : 0 }}</div>
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
          <div ref="trendChartRef" class="chart-container"></div>
        </vab-card>
      </el-col>
      <el-col :span="12">
        <vab-card title="部门使用分布">
          <div ref="deptChartRef" class="chart-container"></div>
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
      series: [{ data: counts, type: 'line', smooth: true, areaStyle: {} }],
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
            borderWidth: 2,
          },
          data: data.departmentUsage || [],
        },
      ],
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
  <el-dialog v-model="dialogVisible" title="预定工位" width="500px">
    <el-form ref="formRef" :model="form" label-width="80px">
      <el-form-item label="工位">
        <span>{{ form.workstationCode }}</span>
      </el-form-item>
      <el-form-item label="时间段">
        <el-time-select
          v-model="form.startTime" start="08:00" step="00:30" end="20:00"
          placeholder="开始时间" style="width: 150px; margin-right: 10px"
        />
        <el-time-select v-model="form.endTime" start="08:00" step="00:30"
          end="20:00" placeholder="结束时间" style="width: 150px" />
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
  user: '',
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
  ElMessage.success('预定成功')
  dialogVisible.value = false
  emit('success')
}

defineExpose({
  show,
})
</script>

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
  ids: [],
})

const show = (row: any) => {
  title.value = `分配工位: ${row.code}`
  form.ids = [row.id]
  form.department = row.department
  form.user = row.user
  dialogVisible.value = true
}

const showBatch = (rows: any[]) => {
  title.value = `批量分配 (${rows.length}个)`
  form.ids = rows.map((r) => r.id)
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
  showBatch,
})
</script>

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
  status: 'active',
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
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
```
