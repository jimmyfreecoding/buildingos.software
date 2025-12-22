# 源代码提交页（智能楼宇通行系统 Buildingos.ai.access）

## 提交要求
- 连续前30页与后30页，每页≥50行
- 不得包含公司、个人、文件名称
- 数量与申请表一致
## 实体代码
```
import { Entity, Column, PrimaryGeneratedColumn, PrimaryColumn } from 'typeorm';
import { ApiProperty } from '@nestjs/swagger';

/**
 * door_pass_log 表
 */
@Entity('door_pass_log')
export class DoorPassLog {
  @ApiProperty({ description: 'id' })
  @PrimaryGeneratedColumn()
  id: number;

  @ApiProperty({ description: '属地' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '属地',
  })
  spaceId: string;

  @ApiProperty({ description: '平台，海康，旷视' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '平台，海康，旷视',
    nullable: true,
    default: '',
  })
  platform: string;

  @ApiProperty({ description: '人员姓名' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '人员姓名',
    nullable: true,
    default: '',
  })
  personName: string;

  @ApiProperty({ description: '人员ID，访客ID或员工ID' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '人员ID，访客ID或员工ID',
    nullable: true,
    default: '',
  })
  personId: string;

  @ApiProperty({ description: '人员类型，visitor-访客，user-员工' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '人员类型，visitor-访客，user-员工',
    nullable: true,
    default: '',
  })
  personType: string;

  @ApiProperty({ description: '手机号' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '手机号',
    nullable: true,
    default: '',
  })
  personPhone: string;

  @ApiProperty({ description: '邮箱' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '邮箱',
    nullable: true,
    default: '',
  })
  personEmail: string;

  @ApiProperty({ description: '工号' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '工号',
    nullable: true,
    default: '',
  })
  personEmpNo: string;

  @ApiProperty({ description: '业务ID，旷视-historyId，海康-eventId' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '业务ID，旷视-historyId，海康-eventId',
    nullable: true,
    default: '',
  })
  serviceId: string;

  @ApiProperty({ description: '业务ID，旷视-historyId，海康-eventName' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '业务ID，旷视-historyId，海康-eventName',
    nullable: true,
    default: '',
  })
  serviceName: string;

  @ApiProperty({ description: '门禁ID' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '门禁ID',
    nullable: true,
    default: '',
  })
  doorId: string;

  @ApiProperty({ description: '门禁索引码' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '门禁索引码',
    nullable: true,
    default: '',
  })
  doorIndexCode: string;

  @ApiProperty({ description: '门禁名称' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '门禁名称',
    nullable: true,
    default: '',
  })
  doorName: string;

  @ApiProperty({ description: '通过方式，card-刷卡，face-人脸' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '通过方式，card-刷卡，face-人脸',
    nullable: true,
    default: '',
  })
  passType: string;

  @ApiProperty({ description: '通过方向，in-进，out-出' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '通过方向，in-进，out-出',
    nullable: true,
    default: '',
  })
  passDirection: string;

  @ApiProperty({ description: '抓拍人脸' })
  @Column({
    type: 'varchar',
    comment: '抓拍人脸',
    nullable: true,
  })
  faceUrl: string;

  @ApiProperty({ description: 'IC卡' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: 'IC卡',
    nullable: true,
    default: '',
  })
  cardNum: string;

  @ApiProperty({ description: '通过时间' })
  @Column({
    type: 'varchar',
    length: 20,
    comment: '通过时间',
    nullable: true,
    default: '',
  })
  passTime: string;

  @ApiProperty({ description: '通过时间格式话' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '通过时间格式话',
    nullable: true,
    default: '',
  })
  passTimeStr: string;

}
import { Entity, Column, PrimaryGeneratedColumn, PrimaryColumn } from 'typeorm';
import { ApiProperty } from '@nestjs/swagger';

/**
 * door_pass_final_log 表
 */
@Entity('door_pass_final_log')
export class DoorPassFinalLog {
  @ApiProperty({ description: 'id' })
  @PrimaryGeneratedColumn()
  id: number;

  @ApiProperty({ description: '属地' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '属地',
  })
  spaceId: string;

  @ApiProperty({ description: '平台，海康，旷视' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '平台，海康，旷视',
    nullable: true,
    default: '',
  })
  platform: string;

  @ApiProperty({ description: '人员姓名' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '人员姓名',
    nullable: true,
    default: '',
  })
  personName: string;

  @ApiProperty({ description: '人员ID，访客ID或员工ID' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '人员ID，访客ID或员工ID',
    nullable: true,
    default: '',
  })
  personId: string;

  @ApiProperty({ description: '人员类型，visitor-访客，user-员工' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '人员类型，visitor-访客，user-员工',
    nullable: true,
    default: '',
  })
  personType: string;

  @ApiProperty({ description: '手机号' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '手机号',
    nullable: true,
    default: '',
  })
  personPhone: string;

  @ApiProperty({ description: '邮箱' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '邮箱',
    nullable: true,
    default: '',
  })
  personEmail: string;

  @ApiProperty({ description: '工号' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '工号',
    nullable: true,
    default: '',
  })
  personEmpNo: string;

  @ApiProperty({ description: '业务ID，旷视-historyId，海康-eventId' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '业务ID，旷视-historyId，海康-eventId',
    nullable: true,
    default: '',
  })
  serviceId: string;

  @ApiProperty({ description: '业务ID，旷视-historyId，海康-eventName' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '业务ID，旷视-historyId，海康-eventName',
    nullable: true,
    default: '',
  })
  serviceName: string;

  @ApiProperty({ description: '门禁ID' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '门禁ID',
    nullable: true,
    default: '',
  })
  doorId: string;

  @ApiProperty({ description: '门禁名称' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '门禁名称',
    nullable: true,
    default: '',
  })
  doorName: string;

  @ApiProperty({ description: '通过方式，card-刷卡，face-人脸' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '通过方式，card-刷卡，face-人脸',
    nullable: true,
    default: '',
  })
  passType: string;

  @ApiProperty({ description: '通过方向，in-进，out-出' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '通过方向，in-进，out-出',
    nullable: true,
    default: '',
  })
  passDirection: string;

  @ApiProperty({ description: '抓拍人脸' })
  @Column({
    type: 'varchar',
    comment: '抓拍人脸',
    nullable: true,
  })
  faceUrl: string;

  @ApiProperty({ description: 'IC卡' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: 'IC卡',
    nullable: true,
    default: '',
  })
  cardNum: string;

  @ApiProperty({ description: '通过时间' })
  @Column({
    type: 'varchar',
    length: 20,
    comment: '通过时间',
    nullable: true,
    default: '',
  })
  passTime: string;

  @ApiProperty({ description: '通过时间格式话' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '通过时间格式话',
    nullable: true,
    default: '',
  })
  passTimeStr: string;

}

```
## 控制器
```
import { Controller, Get, Post, Query, Body, UseGuards, Logger, Request } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { PassService } from './pass.service';
import { SyncLogListRequestDto, SyncLogListResponseDto } from './dto/sync-log.dto';
import { SyncLogDetailListRequestDto, SyncLogDetailListResponseDto } from './dto/sync-log-detail.dto';
import { FaceUserListRequestDto, FaceUserListResponseDto } from './dto/face-user.dto';
import { DoorPassLogListRequestDto, DoorPassLogListResponseDto } from './dto/door-pass-log.dto';
import { DoorPassLogStatRequestDto, DoorPassLogStatResponseDto } from './dto/door-pass-log-stat.dto';
import { UserGroupListRequestDto, UserGroupListResponseDto } from './dto/user-group.dto';
import { ElevatorUserListRequestDto, ElevatorUserListResponseDto } from './dto/elevator-user.dto';
import { DoorPassHistoryLogListRequestDto, DoorPassHistoryLogListResponseDto } from './dto/door-pass-history-log.dto';
import { DoorPassHistoryLogStatRequestDto, DoorPassHistoryLogStatResponseDto } from './dto/door-pass-history-log-stat.dto';

@ApiTags('通行管理')
@Controller()
@UseGuards(JwtAuthGuard)
export class PassController {
  private readonly logger = new Logger(PassController.name);

  constructor(private readonly passService: PassService) {}

  @Get('sense/getSyncLogList')
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取人脸同步日志列表' })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    type: SyncLogListResponseDto,
  })
  async getSyncLogList(@Query() dto: SyncLogListRequestDto): Promise<SyncLogListResponseDto> {
    try {
      const result = await this.passService.getSyncLogList(dto);
      return {
        code: '200',
        msg: 'success',
        data: result,
      };
    } catch (error) {
      this.logger.error(`获取同步日志列表失败: ${error.message}`, error.stack);
      return {
        code: '500',
        msg: `获取失败: ${error.message}`,
        data: { total: 0, list: [] },
      };
    }
  }

  @Get('sense/getSyncLogDetailList')
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取人脸同步日志详情列表' })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    type: SyncLogDetailListResponseDto,
  })
  async getSyncLogDetailList(@Query() dto: SyncLogDetailListRequestDto): Promise<SyncLogDetailListResponseDto> {
    try {
      const result = await this.passService.getSyncLogDetailList(dto);
      return {
        code: '200',
        msg: 'success',
        data: result,
      };
    } catch (error) {
      this.logger.error(`获取同步日志详情列表失败: ${error.message}`, error.stack);
      return {
        code: '500',
        msg: `获取失败: ${error.message}`,
        data: { total: 0, list: [] },
      };
    }
  }

  @Get('sense/getFaceUserList')
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取人脸用户列表' })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    type: FaceUserListResponseDto,
  })
  async getFaceUserList(@Query() dto: FaceUserListRequestDto): Promise<FaceUserListResponseDto> {
    try {
      const result = await this.passService.getFaceUserList(dto);
      return {
        code: '200',
        msg: 'success',
        data: result,
      };
    } catch (error) {
      this.logger.error(`获取人脸用户列表失败: ${error.message}`, error.stack);
      return {
        code: '500',
        msg: `获取失败: ${error.message}`,
        data: { total: 0, list: [] },
      };
    }
  }

  @Get('sense/getDoorPassLogList')
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取门禁通行记录列表' })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    type: DoorPassLogListResponseDto,
  })
  async getDoorPassLogList(
    @Query() dto: DoorPassLogListRequestDto,
    @Request() req: { user: { spaceId: string } }
  ): Promise<DoorPassLogListResponseDto> {
    try {
      const result = await this.passService.getDoorPassLogList(dto, req.user.spaceId);
      return {
        code: '200',
        msg: 'success',
        data: result,
      };
    } catch (error) {
      this.logger.error(`获取门禁通行记录列表失败: ${error.message}`, error.stack);
      return {
        code: '500',
        msg: `获取失败: ${error.message}`,
        data: { total: 0, list: [] },
      };
    }
  }

  @Get('sense/getDoorPassLogStat')
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取门禁通行记录统计' })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    type: DoorPassLogStatResponseDto,
  })
  async getDoorPassLogStat(
    @Query() dto: DoorPassLogStatRequestDto,
    @Request() req: { user: { spaceId: string } }
  ): Promise<DoorPassLogStatResponseDto> {
    try {
      const result = await this.passService.getDoorPassLogStat(dto, req.user.spaceId);
      return {
        code: '200',
        msg: 'success',
        data: result,
      };
    } catch (error) {
      this.logger.error(`获取门禁通行记录统计失败: ${error.message}`, error.stack);
      return {
        code: '500',
        msg: `获取失败: ${error.message}`,
        data: { total: 0, list: [] },
      };
    }
  }

  @Post('sense/getUserGroupList')
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取用户分组列表' })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    type: UserGroupListResponseDto,
  })
  async getUserGroupList(
    @Query() dto: UserGroupListRequestDto,
    @Request() req: { user: { spaceId: string } }
  ): Promise<UserGroupListResponseDto> {
    try {
      const result = await this.passService.getUserGroupList(dto, req.user.spaceId);
      return {
        code: '200',
        msg: 'success',
        data: result,
      };
    } catch (error) {
      this.logger.error(`获取用户分组列表失败: ${error.message}`, error.stack);
      return {
        code: '500',
        msg: `获取失败: ${error.message}`,
        data: { total: 0, list: [] },
      };
    }
  }

  @Get('sense/getElevatorUserList')
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取电梯用户列表' })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    type: ElevatorUserListResponseDto,
  })
  async getElevatorUserList(
    @Query() dto: ElevatorUserListRequestDto,
    @Request() req: { user: { spaceCode: string } },
  ): Promise<ElevatorUserListResponseDto> {
    try {
      const spaceCode = req.user.spaceCode;
      const result = await this.passService.getElevatorUserList(dto, spaceCode);
      return {
        code: '200',
        msg: 'success',
        data: result,
      };
    } catch (error) {
      this.logger.error(`获取电梯用户列表失败: ${error.message}`, error.stack);
      return {
        code: '500',
        msg: `获取失败: ${error.message}`,
        data: { total: 0, list: [] },
      };
    }
  }

  @Post('sense/getElevatorUserList')
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取电梯用户列表（POST）' })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    type: ElevatorUserListResponseDto,
  })
  async getElevatorUserListPost(
    @Body() body: ElevatorUserListRequestDto,
    @Query() query: ElevatorUserListRequestDto,
    @Request() req: { user: { spaceCode: string } },
  ): Promise<ElevatorUserListResponseDto> {
    try {
      const dto = { ...query, ...body };
      const spaceCode = req.user.spaceCode;
      const result = await this.passService.getElevatorUserList(dto, spaceCode);
      return {
        code: '200',
        msg: 'success',
        data: result,
      };
    } catch (error) {
      this.logger.error(`获取电梯用户列表失败: ${error.message}`, error.stack);
      return {
        code: '500',
        msg: `获取失败: ${error.message}`,
        data: { total: 0, list: [] },
      };
    }
  }

  @Get('sense/getDoorPassHistoryLogList')
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取门禁历史通行记录列表' })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    type: DoorPassHistoryLogListResponseDto,
  })
  async getDoorPassHistoryLogList(
    @Query() dto: DoorPassHistoryLogListRequestDto,
    @Request() req: { user: { spaceId: string } }
  ): Promise<DoorPassHistoryLogListResponseDto> {
    try {
      const result = await this.passService.getDoorPassHistoryLogList(dto, req.user.spaceId);
      return {
        code: '200',
        msg: 'success',
        data: result,
      };
    } catch (error) {
      this.logger.error(`获取门禁历史通行记录失败: ${error.message}`, error.stack);
      return {
        code: '500',
        msg: `获取失败: ${error.message}`,
        data: { total: 0, list: [] },
      };
    }
  }

  @Get('sense/getDoorPassHistoryLogStat')
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取门禁历史通行统计' })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    type: DoorPassHistoryLogStatResponseDto,
  })
  async getDoorPassHistoryLogStat(
    @Query() dto: DoorPassHistoryLogStatRequestDto,
    @Request() req: { user: { spaceId: string } }
  ): Promise<DoorPassHistoryLogStatResponseDto> {
    try {
      const data = await this.passService.getDoorPassHistoryLogStat(dto, req.user.spaceId);
      return { code: '200', msg: 'success', data };
    } catch (error) {
      this.logger.error(`获取门禁历史通行统计失败: ${error.message}`, error.stack);
      return { code: '500', msg: `获取失败: ${error.message}`, data: { visitor: 0, servicer: 0, employee: 0 } };
    }
  }
}

```

## 模块代码
```
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { PassController } from './pass.controller';
import { PassService } from './pass.service';
import { FacePlatformSyncLog } from '../entities/FacePlatformSyncLog';
import { FacePlatformSyncClog } from '../entities/FacePlatformSyncClog';
import { User } from '../entities/User';
import { Department } from '../entities/Department';
import { DoorPassLog } from '../entities/DoorPassLog';
import { HikDevice } from '../entities/HikDevice';
import { UserGroup } from '../entities/UserGroup';
import { UserGroupUser } from '../entities/UserGroupUser';
import { UserFaceImages } from '../entities/UserFaceImages';
import { MegviiGroup } from '../entities/MegviiGroup';
import { UserDoorAuthGroup } from '../entities/UserDoorAuthGroup';
import { Floor } from '../entities/Floor';
import { UserElevatorAuthFloor } from '../entities/UserElevatorAuthFloor';
import { Space } from '../entities/Space';
import { DoorPassFinalLog } from '../entities/DoorPassFinalLog';

@Module({
  imports: [
    TypeOrmModule.forFeature([
      FacePlatformSyncLog, 
      FacePlatformSyncClog, 
      User, 
      Department,
      DoorPassLog,
      HikDevice,
      UserGroup,
      UserGroupUser,
      UserFaceImages,
      MegviiGroup,
      UserDoorAuthGroup,
      Floor,
      UserElevatorAuthFloor,
      Space,
      DoorPassFinalLog
    ]),
  ],
  controllers: [PassController],
  providers: [PassService],
  exports: [PassService],
})
export class PassModule {}

```

## 服务代码
```
import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, Like, In } from 'typeorm';
import { FacePlatformSyncLog } from '../entities/FacePlatformSyncLog';
import { FacePlatformSyncClog } from '../entities/FacePlatformSyncClog';
import { User } from '../entities/User';
import { Department } from '../entities/Department';
import { DoorPassLog } from '../entities/DoorPassLog';
import { HikDevice } from '../entities/HikDevice';
import { UserGroup } from '../entities/UserGroup';
import { UserGroupUser } from '../entities/UserGroupUser';
import { MegviiGroup } from '../entities/MegviiGroup';
import { UserDoorAuthGroup } from '../entities/UserDoorAuthGroup';
import { SyncLogListRequestDto, SyncLogItemDto } from './dto/sync-log.dto';
import { SyncLogDetailListRequestDto, SyncLogDetailItemDto } from './dto/sync-log-detail.dto';
import { FaceUserListRequestDto, FaceUserItemDto } from './dto/face-user.dto';
import { DoorPassLogListRequestDto, DoorPassLogItemDto } from './dto/door-pass-log.dto';
import { DoorPassLogStatRequestDto, DoorPassLogStatItemDto } from './dto/door-pass-log-stat.dto';
import { UserGroupListRequestDto, UserGroupItemDto } from './dto/user-group.dto';
import { ElevatorUserListRequestDto } from './dto/elevator-user.dto';
import { UserFaceImages } from '../entities/UserFaceImages';
import { Floor } from '../entities/Floor';
import { UserElevatorAuthFloor } from '../entities/UserElevatorAuthFloor';
import { Space } from '../entities/Space';
import { DoorPassFinalLog } from '../entities/DoorPassFinalLog';
import { DoorPassHistoryLogListRequestDto } from './dto/door-pass-history-log.dto';
import { DoorPassHistoryLogStatRequestDto } from './dto/door-pass-history-log-stat.dto';

@Injectable()
export class PassService {
  private readonly logger = new Logger(PassService.name);

  constructor(
    @InjectRepository(FacePlatformSyncLog)
    private facePlatformSyncLogRepository: Repository<FacePlatformSyncLog>,
    @InjectRepository(FacePlatformSyncClog)
    private facePlatformSyncLogDetailRepository: Repository<FacePlatformSyncClog>,
    @InjectRepository(User)
    private userRepository: Repository<User>,
    @InjectRepository(Department)
    private departmentRepository: Repository<Department>,
    @InjectRepository(DoorPassLog)
    private doorPassLogRepository: Repository<DoorPassLog>,
    @InjectRepository(HikDevice)
    private hikDeviceRepository: Repository<HikDevice>,
    @InjectRepository(UserGroup)
    private userGroupRepository: Repository<UserGroup>,
    @InjectRepository(UserGroupUser)
    private userGroupUserRepository: Repository<UserGroupUser>,
    @InjectRepository(UserFaceImages)
    private userFaceImagesRepository: Repository<UserFaceImages>,
    @InjectRepository(MegviiGroup)
    private megviiGroupRepository: Repository<MegviiGroup>,
    @InjectRepository(UserDoorAuthGroup)
    private userDoorAuthGroupRepository2: Repository<UserDoorAuthGroup>,
    @InjectRepository(Floor)
    private floorRepository: Repository<Floor>,
    @InjectRepository(UserElevatorAuthFloor)
    private userElevatorAuthFloorRepository: Repository<UserElevatorAuthFloor>,
    @InjectRepository(Space)
    private spaceRepository: Repository<Space>,
    @InjectRepository(DoorPassFinalLog)
    private doorPassFinalLogRepository: Repository<DoorPassFinalLog>,
  ) {}

  /**
   * 获取同步日志列表
   * @param dto 查询参数
   * @returns 同步日志列表和总数
   */
  async getSyncLogList(dto: SyncLogListRequestDto): Promise<{ total: number; list: SyncLogItemDto[] }> {
    try {
      const page = dto.pageNo || 1;
      const pageSize = dto.pageSize || 20;
      const skip = (page - 1) * pageSize;

      // 构建查询条件
      const whereCondition: any = {};
      
      // 如果提供了用户名，添加到查询条件
      if (dto.username) {
        whereCondition.operator = Like(`%${dto.username}%`);
      }
      
      // 如果提供了部门ID，添加到查询条件
      // 注意：这里假设部门ID存储在某个字段中，可能需要根据实际情况调整
      if (dto.depid) {
        whereCondition.departmentId = dto.depid;
      }

      // 查询数据库
      const [logs, total] = await this.facePlatformSyncLogRepository.findAndCount({
        where: whereCondition,
        skip,
        take: pageSize,
        order: { synctime : 'DESC' },
      });

      // 转换为DTO格式
      const list = logs.map(log => ({
        id: log.id,
        spaceId: log.spaceId,
        spaceName: log.spaceName,
        type: log.type,
        platform: log.syncTo ,
        status: log.status,
        content: log.desc ,
        createtime: log.synctime ,
        operator: log.type,
      }));

      return { total, list };
    } catch (error) {
      this.logger.error(`获取同步日志列表失败: ${error.message}`, error.stack);
      throw error;
    }
  }

  /**
   * 获取同步日志详情列表
   * @param dto 查询参数
   * @returns 同步日志详情列表和总数
   */
  async getSyncLogDetailList(dto: SyncLogDetailListRequestDto): Promise<{ total: number; list: SyncLogDetailItemDto[] }> {
    try {
      const page = dto.pageNo || 1;
      const pageSize = dto.pageSize || 20;
      const skip = (page - 1) * pageSize;

      // 构建查询条件
      const whereCondition: any = {};
      
      // 如果提供了同步日志ID，添加到查询条件
      if (dto.id) {
        whereCondition.id = dto.id;
      }
      
      // 如果提供了日志ID，添加到查询条件
      if (dto.logID) {
        whereCondition.logID = dto.logID;
      }
      
      // 根据查询类型过滤
      if (dto.queryType && dto.queryType !== 'all') {
        whereCondition.status = dto.queryType === 'success' ? 'success' : 'fail';
      }
      
      // 如果提供了错误代码，添加到查询条件
      if (dto.errorCode) {
        whereCondition.errorCode = dto.errorCode;
      }

      // 查询数据库
      const [logs, total] = await this.facePlatformSyncLogDetailRepository.findAndCount({
        where: whereCondition,
        skip,
        take: pageSize,
        order: { id: 'DESC' },
      });

      // 转换为DTO格式
      const list = logs.map(log => ({
        id: log.id,
        syncLogId: log.logID || '',
        personId: log.syncObjID || '',
        personName: log.syncObjName || '',
        departmentId: log.syncObjID || '',
        departmentName: log.syncObjName || '',
        status: log.type || '',
        errorCode: log.errorCode || '',
        errorMsg: log.errorMessage || '',
        syncTime: log.syncTime || '',
      }));

      return { total, list };
    } catch (error) {
      this.logger.error(`获取同步日志详情列表失败: ${error.message}`, error.stack);
      throw error;
    }
  }

  /**
   * 获取人脸用户列表
   * @param dto 查询参数
   * @returns 人脸用户列表和总数
   */
  async getFaceUserList(dto: FaceUserListRequestDto): Promise<{ total: number; list: FaceUserItemDto[] }> {
    try {
      const page = dto.pageNo || 1;
      const pageSize = dto.pageSize || 20;
      const skip = (page - 1) * pageSize;

      // 构建查询条件，过滤：删除标识=1、启用、在职、排除admin
      const queryBuilder = this.userRepository
        .createQueryBuilder('user')
        .where('user.deleteFlag = :deleteFlag', { deleteFlag: 1 })
        .andWhere('user.userStatus = :userStatus', { userStatus: 0 })
        .andWhere('user.quitStatus = :quitStatus', { quitStatus: 0 })
        .andWhere('user.userName != :admin', { admin: 'admin' });

      // 用户名搜索范围：userName/realName/flowerName/empNo
      if (dto.username) {
        const kw = `%${dto.username}%`;
        queryBuilder.andWhere(
          '(user.userName LIKE :kw OR user.realName LIKE :kw OR user.flowerName LIKE :kw OR user.empNo LIKE :kw)',
          { kw },
        );
      }

      // 组织ID过滤
      if (dto.orgid) {
        queryBuilder.andWhere('user.orgId = :orgId', { orgId: Number(dto.orgid) });
      }

      // 部门ID过滤
      if (dto.depid) {
        queryBuilder.andWhere('user.departmentId = :departmentId', {
          departmentId: Number(dto.depid),
        });
      }

      // 获取总数
      const total = await queryBuilder.getCount();

      // 分页与排序
      queryBuilder.orderBy('user.createtime', 'DESC').skip(skip).take(pageSize);

      // 获取用户列表
      const users = await queryBuilder.getMany();

      // 转换为DTO格式
      const list: FaceUserItemDto[] = await Promise.all(
        users.map(async (user) => {
          const departmentNamePath = await this.buildDepartmentPath(user.departmentId);
          const faceInfo = await this.getLatestFaceInfo(user.userId ?? user.id);

          // 头像：优先人脸URL，其次用户头像
          const preferredFaceUrl = faceInfo?.faceUrl || '';
          const avatar = preferredFaceUrl || user.avatar || '';

          return {
            id: user.id,
            userId: user.userId,
            orgId: user.orgId,
            departmentId: user.departmentId,
            departmentName: departmentNamePath,
            username: user.userName || '',
            empNo: user.empNo || '',
            virtualEmpNo: user.virtualEmpNo || '',
            cardNum: user.cardNum || '',
            realName: user.realName || '',
            flowerName: user.flowerName || '',
            gender: user.gender ?? 2,
            avatar,
            email: user.email || '',
            quitStatus: user.quitStatus ?? 0,
            userStatus: user.userStatus ?? 0,
            userType: user.userType ?? 0,
            domainAccount: user.domainAccount || '',
            datetime: user.createtime || '',
            faceInfo,
          };
        }),
      );

      return { total, list };
    } catch (error) {
      this.logger.error(`获取人脸用户列表失败: ${error.message}`, error.stack);
      throw error;
    }
  }

  // 构建部门路径字符串：根据 orgPath 拼接部门名称
  private async buildDepartmentPath(departmentId?: number): Promise<string> {
    if (!departmentId) return '';
    const department = await this.departmentRepository.findOne({
      where: { departmentId, deleteFlag: 1 },
    });
    if (!department) return '';

    const orgPath = department.orgPath || '';
    const ids = orgPath
      .split('|')
      .filter(Boolean)
      .map((s) => parseInt(s, 10))
      .filter((n) => !isNaN(n));

    if (ids.length === 0) {
      return department.departmentName || '';
    }

    const depList = await this.departmentRepository.find({
      where: { departmentId: In(ids), deleteFlag: 1 },
    });
    const depNameMap = new Map<number, string>();
    depList.forEach((d) => depNameMap.set(d.departmentId, d.departmentName));

    const names: string[] = ids
      .map((id) => depNameMap.get(id))
      .filter((name): name is string => !!name);

    // 确保包含当前部门名称
    if (!names.includes(department.departmentName)) {
      names.push(department.departmentName);
    }

    return names.join('/');
  }

  // 查询最新的人脸图片记录并构建 faceInfo
  private async getLatestFaceInfo(userId?: number | string): Promise<any | undefined> {
    if (!userId) return undefined;
    const uid = String(userId);

    const record = await this.userFaceImagesRepository
      .createQueryBuilder('f')
      .where('f.userId = :userId', { userId: uid })
      .orderBy('f.id', 'DESC')
      .getOne();

    if (!record) return undefined;

    const faceUrl = record.hikFaceUrl || record.megviiFaceUrl || record.hikSHHFaceUrl || record.hikHZWFaceUrl || '';

    // 返回实体的全部列属性，并额外附加 faceUrl 字段
    return { ...(record as any), faceUrl };
  }

  /**
   * 获取门禁通行记录列表
   * @param dto 查询参数
   * @param spaceId 空间ID
   * @returns 门禁通行记录列表和总数
   */
  async getDoorPassLogList(dto: DoorPassLogListRequestDto, spaceId: string): Promise<{ total: number; list: DoorPassLogItemDto[] }> {
    try {
      const page = dto.pageNo || 1;
      const pageSize = dto.pageSize || 20;
      const skip = (page - 1) * pageSize;

      // 构建查询条件
      const queryBuilder = this.doorPassLogRepository
        .createQueryBuilder('log')
        .where('log.spaceId = :spaceId', { spaceId });

      // 如果提供了门禁名称，添加到查询条件
      if (dto.title) {
        // 先查询匹配名称的门禁设备
        const devices = await this.hikDeviceRepository.find({
          where: { name: Like(`%${dto.title}%`), spaceId, resourceType: 'door' },
          select: ['indexCode']
        });
        
        if (devices.length > 0) {
          const doorIds = devices.map(device => device.indexCode);
          queryBuilder.andWhere('log.doorIndexCode IN (:...doorIds)', { doorIds });
        } else {
          // 如果没有找到匹配的门禁，返回空结果
          return { total: 0, list: [] };
        }
      }

      // 添加时间范围条件
      if (dto.startDate) {
        const startTime = Math.floor(new Date(dto.startDate).getTime() / 1000);
        queryBuilder.andWhere('log.passTime >= :startTime', { startTime });
      }
      
      if (dto.stopDate) {
        const stopTime = Math.floor(new Date(dto.stopDate).getTime() / 1000);
        queryBuilder.andWhere('log.passTime <= :stopTime', { stopTime });
      }

      // 获取总数
      const total = await queryBuilder.getCount();

      // 添加分页和排序
      queryBuilder.orderBy('log.passTime', 'DESC').skip(skip).take(pageSize);

      // 获取通行记录
      const logs = await queryBuilder.getMany();

      // 获取所有涉及的门禁设备信息
      const doorIndexCodes = [...new Set(logs.map(log => log.doorId))];
      const doors = await this.hikDeviceRepository.find({
        where: { indexCode: In(doorIndexCodes), resourceType: 'door' },
        select: ['indexCode', 'name']
      });
      
      // 创建门禁索引码到名称的映射
      const doorMap = new Map();
      doors.forEach(door => {
        doorMap.set(door.indexCode, door.name);
      });

      // 转换为DTO格式
      const list = logs.map(log => ({
        id: log.id.toString(),
        doorId: log.doorId || '',
        doorName: doorMap.get(log.doorId) || log.doorId || '',
        personId: log.personId || '',
        personName: log.personName || '',
        passTime: log.passTime ,
        passType: log.passType || '',
        passStatus: log.passType === 'success' ? '成功' : '失败',
        photoUrl: log.faceUrl || '',
      }));

      return { total, list };
    } catch (error) {
      this.logger.error(`获取门禁通行记录列表失败: ${error.message}`, error.stack);
      throw error;
    }
  }

  /**
   * 获取门禁通行记录统计
   * @param dto 查询参数
   * @param spaceId 空间ID
   * @returns 门禁通行记录统计和总数
   */
  async getDoorPassLogStat(dto: DoorPassLogStatRequestDto, spaceId: string): Promise<{ total: number; list: DoorPassLogStatItemDto[] }> {
    try {
      const page = dto.pageNo || 1;
      const pageSize = dto.pageSize || 20;
      const skip = (page - 1) * pageSize;

      // 构建基础查询条件
      let doorDevicesQuery = this.hikDeviceRepository
        .createQueryBuilder('device')
        .where('device.spaceId = :spaceId', { spaceId })
        .andWhere('device.resourceType = :resourceType', { resourceType: 'door' });

      // 如果提供了门禁名称，添加到查询条件
      if (dto.title) {
        doorDevicesQuery = doorDevicesQuery.andWhere('device.name LIKE :title', { title: `%${dto.title}%` });
      }

      // 获取符合条件的门禁设备总数
      const total = await doorDevicesQuery.getCount();

      // 添加分页
      doorDevicesQuery = doorDevicesQuery.skip(skip).take(pageSize);

      // 获取门禁设备
      const doorDevices = await doorDevicesQuery.getMany();

      // 构建时间范围条件
      let timeCondition = '';
      const params: any = {};
      
      if (dto.startDate) {
        const startTime = Math.floor(new Date(dto.startDate).getTime() / 1000);
        timeCondition += ' AND passTime >= :startTime';
        params.startTime = startTime;
      }
      
      if (dto.stopDate) {
        const stopTime = Math.floor(new Date(dto.stopDate).getTime() / 1000);
        timeCondition += ' AND passTime <= :stopTime';
        params.stopTime = stopTime;
      }

      // 获取每个门禁的通行记录统计
      const list = await Promise.all(
        doorDevices.map(async (device) => {
          // 获取总通行次数
          const totalCountQuery = `
            SELECT COUNT(*) as count 
            FROM door_pass_log 
            WHERE doorIndexCode = '${device.indexCode}' 
            AND spaceId = '${spaceId}'
            ${timeCondition}
          `;
          const totalCountResult = await this.doorPassLogRepository.query(totalCountQuery, params);
          const totalCount = parseInt(totalCountResult[0]?.count || '0');

          // 获取成功通行次数
          const successCountQuery = `
            SELECT COUNT(*) as count 
            FROM door_pass_log 
            WHERE doorIndexCode = '${device.indexCode}' 
            AND spaceId = '${spaceId}'
            AND eventType = 'success'
            ${timeCondition}
          `;
          const successCountResult = await this.doorPassLogRepository.query(successCountQuery, params);
          const successCount = parseInt(successCountResult[0]?.count || '0');

          // 计算失败次数
          const failCount = totalCount - successCount;

          return {
            doorId: device.indexCode,
            doorName: device.name,
            totalCount,
            successCount,
            failCount,
          };
        })
      );

      return { total, list };
    } catch (error) {
      this.logger.error(`获取门禁通行记录统计失败: ${error.message}`, error.stack);
      throw error;
    }
  }

  /**
   * 获取用户分组列表
   * @param dto 查询参数
   * @param spaceId 空间ID
   * @returns 用户分组列表和总数
   */
  async getUserGroupList(dto: UserGroupListRequestDto, spaceId: string): Promise<{ total: number; list: any[] }> {
    try {
      const page = dto.pageNo || 1;
      const pageSize = dto.pageSize || 20;
      const offset = (page - 1) * pageSize;
      const baseQb = this.megviiGroupRepository
        .createQueryBuilder('mg')
        .where('mg.deleteFlag = :df', { df: 1 })
        .andWhere('mg.spaceId = :spaceId', { spaceId });
      const total = await baseQb.getCount();
      const groups = await baseQb.orderBy('mg.id', 'DESC').skip(offset).take(pageSize).getMany();
      const groupIds = groups.map((g) => g.groupId).filter(Boolean);
      if (groupIds.length === 0) return { total, list: [] };
      const qb = this.megviiGroupRepository
        .createQueryBuilder('mg')
        .leftJoin(UserDoorAuthGroup, 'ug', 'mg.groupId = ug.groupId')
        .where('mg.deleteFlag = :df', { df: 1 })
        .andWhere('mg.groupId IN (:...gids)', { gids: groupIds })
        .andWhere('mg.spaceId = :spaceId', { spaceId });
      const anyDto: any = dto as any;
      if (anyDto.userName) {
        qb.andWhere('ug.userName LIKE :uname', { uname: `%${anyDto.userName}%` });
      }
      if (anyDto.empNo) {
        qb.andWhere('ug.empNo LIKE :empno', { empno: `%${anyDto.empNo}%` });
      }
      const rows = await qb
        .select([
          'mg.id AS id',
          'mg.spaceId AS spaceId',
          'mg.groupId AS groupId',
          'mg.groupName AS groupName',
          'mg.createtime AS createtime',
          'ug.userId AS userId',
          'ug.userName AS userName',
          'ug.empNo AS empNo',
        ])
        .getRawMany();
      const temp: Record<string, any> = {};
      for (const r of rows) {
        const gid = r.groupId;
        if (!temp[gid]) temp[gid] = { ...r, userIds: [], userNames: [], userList: [] };
        if (!temp[gid].userIds.includes(r.userId) && r.userId) {
          temp[gid].userIds.push(r.userId);
          temp[gid].userNames.push(r.userName);
          temp[gid].userList.push({ userId: r.userId, userName: r.userName, empNo: r.empNo });
        }
      }
      const result = Object.values(temp).map((v: any) => {
        delete v.userId;
        delete v.userName;
        delete v.empNo;
        delete v.id;
        return v;
      });
      return { total, list: result };
    } catch (error) {
      this.logger.error(`获取用户分组列表失败: ${error.message}`, error.stack);
      throw error;
    }
  }

  /**
   * 获取电梯用户列表
   * @param dto 查询参数
   * @returns 电梯用户列表和总数
   */
  async getElevatorUserList(dto: ElevatorUserListRequestDto, spaceCode: string): Promise<{ total: number; list: any[] }> {
    try {
      const space = await this.spaceRepository.findOne({ where: { code: spaceCode, deleteFlag: 1 as any } });
      if (!space) {
        return { total: 0, list: [] };
      }
      const page = dto.pageNo || 1;
      const pageSize = dto.pageSize || 20;
      const offset = (page - 1) * pageSize;
      const baseQb = this.floorRepository
        .createQueryBuilder('f')
        .where('f.deleteFlag = :df', { df: 1 })
        .andWhere('f.spaceCode = :spaceCode', { spaceCode });
      const total = await baseQb.getCount();
      const floors = await baseQb.orderBy('f.sortOrder', 'ASC').skip(offset).take(pageSize).getMany();
      const floorCodes = floors.map(f => f.code).filter(Boolean);
      if (floorCodes.length === 0) {
        return { total, list: [] };
      }
      const rows = await this.floorRepository
        .createQueryBuilder('f')
        .leftJoin(UserElevatorAuthFloor, 'uf', 'f.code = uf.floorCode')
        .where('f.code IN (:...codes)', { codes: floorCodes })
        .andWhere('f.spaceCode = :spaceCode', { spaceCode })
        .orderBy('f.sortOrder', 'ASC')
        .select([
          'f.code AS code',
          'f.name AS name',
          'uf.userId AS userId',
          'uf.userName AS userName',
        ])
        .getRawMany();
      const temp: Record<string, any> = {};
      for (const r of rows) {
        const code = r.code;
        if (!temp[code]) temp[code] = { code: r.code, name: r.name, userIds: [], userNameList: [], userList: [] };
        if (r.userId && !temp[code].userIds.includes(r.userId)) {
          temp[code].userIds.push(r.userId);
          temp[code].userNameList.push(r.userName);
          temp[code].userList.push({ userId: r.userId, userName: r.userName });
        }
      }
      const list = Object.values(temp);
      return { total, list };
    } catch (error) {
      this.logger.error(`获取电梯用户列表失败: ${error.message}`, error.stack);
      throw error;
    }
  }

  async getDoorPassHistoryLogList(
    dto: DoorPassHistoryLogListRequestDto,
    spaceId: string,
  ): Promise<{ total: number; list: any[] }> {
    try {
      const page = dto.pageNo || 1;
      const pageSize = dto.pageSize || 20;
      const skip = (page - 1) * pageSize;
      const qb = this.doorPassFinalLogRepository
        .createQueryBuilder('l')
        .where('l.spaceId = :spaceId', { spaceId });
      if (dto.startDate) {
        const start = Math.floor(new Date(dto.startDate.replace(' ', 'T')).getTime() / 1000);
        if (!isNaN(start)) qb.andWhere('l.passTime >= :start', { start: String(start) });
      }
      if (dto.stopDate) {
        const stop = Math.floor(new Date(dto.stopDate.replace(' ', 'T')).getTime() / 1000);
        if (!isNaN(stop)) qb.andWhere('l.passTime <= :stop', { stop: String(stop) });
      }
      if (dto.title) {
        qb.andWhere('(l.doorName LIKE :kw OR l.personName LIKE :kw OR l.personEmpNo LIKE :kw)', {
          kw: `%${dto.title}%`,
        });
      }
      const total = await qb.getCount();
      const list = await qb.orderBy('l.passTime', 'DESC').skip(skip).take(pageSize).getMany();
      return { total, list };
    } catch (error) {
      this.logger.error(`获取门禁历史记录失败: ${error.message}`, error.stack);
      throw error;
    }
  }

  async getDoorPassHistoryLogStat(
    dto: DoorPassHistoryLogStatRequestDto,
    spaceId: string,
  ): Promise<{ visitor: number; servicer: number; employee: number }> {
    const buildQb = () => {
      const qb = this.doorPassFinalLogRepository.createQueryBuilder('l').where('l.spaceId = :spaceId', { spaceId }).andWhere('l.passDirection = :dir', { dir: 'in' });
      if (dto.startDate) {
        const start = Math.floor(new Date(dto.startDate.replace(' ', 'T')).getTime() / 1000);
        if (!isNaN(start)) qb.andWhere('l.passTime >= :start', { start: String(start) });
      }
      if (dto.stopDate) {
        const stop = Math.floor(new Date(dto.stopDate.replace(' ', 'T')).getTime() / 1000);
        if (!isNaN(stop)) qb.andWhere('l.passTime <= :stop', { stop: String(stop) });
      }
      if (dto.title) {
        qb.andWhere('(l.doorName LIKE :kw OR l.personName LIKE :kw OR l.personEmpNo LIKE :kw)', { kw: `%${dto.title}%` });
      }
      return qb;
    };
    const visitorRow = await buildQb().andWhere("l.personType = 'visitor'").andWhere("l.personEmpNo = ''").select('COUNT(DISTINCT l.personId)', 'num').getRawOne();
    const employeeRow = await buildQb().andWhere("l.personType = 'user'").andWhere("l.personEmpNo NOT LIKE 'w%'").andWhere("l.personEmpNo NOT LIKE 'WB%'").select('COUNT(DISTINCT l.personEmpNo)', 'num').getRawOne();
    const servicerRow = await buildQb().andWhere("l.personType = 'user'").andWhere("(l.personEmpNo LIKE 'w%' OR l.personEmpNo LIKE 'WB%')").select('COUNT(DISTINCT l.personEmpNo)', 'num').getRawOne();
    const toNum = (x: any) => parseInt(x?.num || '0', 10);
    return { visitor: toNum(visitorRow), employee: toNum(employeeRow), servicer: toNum(servicerRow) };
  }
}

```

## 前端代码
```
<template>
  <div class="no-background-container table-auto-height">
    <el-tabs v-model="activeName" type="border-card" @tab-click="handleTabClick">
      <el-tab-pane class="" label="今日通行" name="today">
        <vab-query-form>
          <vab-query-form-top-panel>
            <el-form inline label-width="60px" :model="queryForm" @submit.prevent>
              <el-form-item label="关键字">
                <el-input v-model.trim="queryForm.title" clearable placeholder="姓名/工号/门禁点" />
              </el-form-item>
              <el-form-item label="周期">
                <el-date-picker
                  v-model="queryForm.searchDate"
                  :disabled-date="isToday"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  end-placeholder="结束时间"
                  start-placeholder="开始时间"
                  type="datetimerange"
                  :default-time="defaultTime"
                  />
              </el-form-item>
              <el-form-item>
                <el-button :icon="Search" :loading="listLoading" type="primary" @click="queryData">查询</el-button>
              </el-form-item>
              <el-form-item>
                <el-button :loading="exportLoading" type="primary" @click="exportData">
                  <vab-icon icon="export-fill" />
                  <span>导出</span>
                </el-button>
              </el-form-item>
            </el-form>
          </vab-query-form-top-panel>
        </vab-query-form>
        <div class="vistor-statistic-form-container no-background-container">
          <el-row :gutter="20">
            <el-col :span="6">
              <car-num
                background="blue"
                icon="account-circle-line"
                :countConfig="{ endValue: employee + visitor + servicer }"
                percentage="10%"
                title="进场总人数"
              />
            </el-col>
            <el-col :span="6">
              <car-num
                background="white"
                percentage="30%"
                :countConfig="{ endValue: employee }"
                icon="account-circle-fill"
                title="正编人数"
              >
                <!-- <template #tag>
              <el-tag type="danger">{{ queryForm.startDate - queryForm.stopDate }}</el-tag>
            </template> -->
                <template #chart>
                  <active-users-bar />
                </template>
              </car-num>
            </el-col>
            <el-col :span="6">
              <car-num background="white" percentage="30%" :countConfig="{ endValue: visitor }" icon="account-circle-fill" title="访客人数">
                <!-- <template #tag>
              <el-tag type="danger">{{ queryForm.startDate - queryForm.stopDate }}</el-tag>
            </template> -->
                <template #chart>
                  <active-users-bar />
                </template>
              </car-num>
            </el-col>
            <el-col :span="6">
              <car-num
                background="white"
                percentage="30%"
                :countConfig="{ endValue: servicer }"
                icon="account-circle-fill"
                title="外包人数"
              >
                <!-- <template #tag>
              <el-tag type="danger">{{ queryForm.startDate - queryForm.stopDate }}</el-tag>
            </template> -->
                <template #chart>
                  <active-users-bar />
                </template>
              </car-num>
            </el-col>
          </el-row>
        </div>
        <br />
        <el-col :span="24">
          <vab-card :body-style="{ height: '210px' }" skeleton>
            <template #header>
              <vab-icon icon="line-chart-fill" />
              分时进出人流
            </template>
            <vab-chart :option="option" />
          </vab-card>
        </el-col>
        <el-table ref="tableSortRef" v-loading="listLoading" border :data="list">
          <el-table-column align="center" label="序号" width="55">
            <template #default="{ $index }">
              {{ $index + 1 }}
            </template>
          </el-table-column>
          <el-table-column align="center" label="姓名" prop="personName" sortable />
          <el-table-column align="center" label="工号" prop="personEmpNo" sortable />
          <el-table-column align="center" label="平台" min-width="100" prop="platform" sortable />
          <el-table-column align="left" label="门禁点" min-width="100" prop="doorName" sortable width="300" />
          <el-table-column align="center" label="进出" prop="passDirection" sortable>
            <template #default="{ row }">
              {{ row.passDirection === 'in' ? '进' : '出' }}
            </template>
          </el-table-column>

          <el-table-column align="left" label="时间" min-width="200" prop="passTime" sortable>
            <template #default="{ row }">
              {{ moment.unix(row.passTime).format('YYYY-MM-DD HH:mm:ss') }}
            </template>
          </el-table-column>
          <el-table-column align="center" label="方式" prop="serviceName" sortable />

          <template #empty>
            <el-empty class="vab-data-empty" description="暂无数据" />
          </template>
        </el-table>
        <el-pagination
          background
          :current-page="queryForm.pageNo"
          :layout="layout"
          :page-size="queryForm.pageSize"
          :total="total"
          @current-change="handleCurrentChange"
          @size-change="handleSizeChange"
        />
      </el-tab-pane>
      <el-tab-pane class="" label="历史通行" name="history">
        <vab-query-form>
          <vab-query-form-top-panel>
            <el-form inline label-width="60px" :model="historyQueryForm" @submit.prevent>
              <el-form-item label="关键字">
                <el-input v-model.trim="historyQueryForm.title" clearable placeholder="姓名/工号/门禁点" />
              </el-form-item>
              <el-form-item label="周期">
                <el-date-picker
                  v-model="historyQueryForm.searchDate"
                  :disabled-date="isHistory"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  end-placeholder="结束时间"
                  start-placeholder="开始时间"
                  type="datetimerange"
                  :default-time="defaultTime"
                />
              </el-form-item>
              <el-form-item>
                <el-button :icon="Search" :loading="listLoading" type="primary" @click="historyQueryData">查询</el-button>
              </el-form-item>
              <el-form-item>
                <el-button :loading="exportLoading" type="primary" @click="exportHistoryData">
                  <vab-icon icon="export-fill" />
                  <span>导出</span>
                </el-button>
              </el-form-item>
            </el-form>
          </vab-query-form-top-panel>
        </vab-query-form>
        <div class="vistor-statistic-form-container no-background-container">
          <el-row :gutter="20">
            <el-col :span="6">
              <car-num
                background="blue"
                icon="account-circle-line"
                :countConfig="{ endValue: historyEmployee + historyVisitor + historyServicer }"
                percentage="10%"
                title="进场总人数"
              />
            </el-col>
            <el-col :span="6">
              <car-num
                background="white"
                percentage="30%"
                :countConfig="{ endValue: historyEmployee }"
                icon="account-circle-fill"
                title="正编人数"
              >
                <!-- <template #tag>
              <el-tag type="danger">{{ historyQueryForm.startDate - historyQueryForm.stopDate }}</el-tag>
            </template> -->
                <template #chart>
                  <active-users-bar />
                </template>
              </car-num>
            </el-col>
            <el-col :span="6">
              <car-num
                background="white"
                percentage="30%"
                :countConfig="{ endValue: historyVisitor }"
                icon="account-circle-fill"
                title="访客人数"
              >
                <!-- <template #tag>
              <el-tag type="danger">{{ historyQueryForm.startDate - historyQueryForm.stopDate }}</el-tag>
            </template> -->
                <template #chart>
                  <active-users-bar />
                </template>
              </car-num>
            </el-col>
            <el-col :span="6">
              <car-num
                background="white"
                percentage="30%"
                :countConfig="{ endValue: historyServicer }"
                icon="account-circle-fill"
                title="外包人数"
              >
                <!-- <template #tag>
              <el-tag type="danger">{{ historyQueryForm.startDate - historyQueryForm.stopDate }}</el-tag>
            </template> -->
                <template #chart>
                  <active-users-bar />
                </template>
              </car-num>
            </el-col>
          </el-row>
        </div>
        <br />
        <el-table ref="tableSortRef" v-loading="historyListLoading" border :data="historyList">
          <el-table-column align="center" label="序号" width="55">
            <template #default="{ $index }">
              {{ $index + 1 }}
            </template>
          </el-table-column>
          <el-table-column align="center" label="姓名" prop="personName" sortable />
          <el-table-column align="center" label="工号" prop="personEmpNo" sortable />
          <el-table-column align="center" label="平台" min-width="100" prop="platform" sortable />
          <el-table-column align="left" label="门禁点" min-width="100" prop="doorName" sortable width="300" />
          <el-table-column align="center" label="进出" prop="passDirection" sortable>
            <template #default="{ row }">
              {{ row.passDirection === 'in' ? '进' : '出' }}
            </template>
          </el-table-column>

          <el-table-column align="left" label="时间" min-width="200" prop="passTime" sortable>
            <template #default="{ row }">
              {{ moment.unix(row.passTime).format('YYYY-MM-DD HH:mm:ss') }}
            </template>
          </el-table-column>
          <el-table-column align="center" label="方式" prop="serviceName" sortable />

          <template #empty>
            <el-empty class="vab-data-empty" description="暂无数据" />
          </template>
        </el-table>
        <el-pagination
          background
          :current-page="historyQueryForm.pageNo"
          :layout="layout"
          :page-size="historyQueryForm.pageSize"
          :total="historyTotal"
          @current-change="historyHandleCurrentChange"
          @size-change="historyHandleSizeChange"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script lang="ts" setup>
import { Search } from '@element-plus/icons-vue'
import { useSettingsStore } from '/@/store/modules/settings.ts'
import {
  exportDoorPassLog,
  getDoorPassLogList,
  getDoorPassLogStat,
  getDoorPassLogByTime,
  getDoorPassHistoryLogList,
  getDoorPassHistoryLogStat,
} from '/@/api/sense.ts'
import moment from 'moment'
import { omit, get } from 'lodash-es'
import type { TabsPaneContext } from 'element-plus'
import { ElMessage } from 'element-plus'
import { lightenColor } from '/@/utils/lightenColor.ts'
import download from '/@/utils/download'
const settingsStore = useSettingsStore()
const { color } = storeToRefs(settingsStore)

defineOptions({
  name: 'PassLog',
})
const defaultTime: [Date, Date] = [
  new Date(2000, 1, 1, 0, 0, 0),
  new Date(2000, 2, 1, 23, 59, 59),
]
const activeName = ref('today')
const editRef = ref<any>(null)
const tableSortRef = ref<any>(null)
const list = ref<any>([])
const listLoading = ref<boolean>(false)
const exportLoading = ref<boolean>(false)
const layout = ref<string>('total, sizes, prev, pager, next, jumper')
const total = ref<any>(0)
const historyList = ref<any>([])
const historyListLoading = ref<boolean>(false)
const historyTotal = ref<any>(0)
const employee = ref<any>(0)
const servicer = ref<any>(0)
const visitor = ref<any>(0)
const historyEmployee = ref<any>(0)
const historyServicer = ref<any>(0)
const historyVisitor = ref<any>(0)
const queryForm = reactive<any>({
  title: '',
  searchDate: '',
  startDate: '',
  stopDate: '',
  pageNo: 1,
  pageSize: 20,
})

const historyQueryForm = reactive<any>({
  title: '',
  searchDate: [moment().subtract(1,'week').format('YYYY-MM-DD 00:00:00'), moment().format('YYYY-MM-DD 23:59:59')],
  startDate: moment().subtract(1,'week').format('YYYY-MM-DD 00:00:00'),
  stopDate: moment().format('YYYY-MM-DD 23:59:59'),
  pageNo: 1,
  pageSize: 20,
})
const echartData = ref<any>([])
const echartLabel = ref<any>([])

const option = reactive<any>({
  tooltip: {
    trigger: 'axis',
    extraCssText: 'z-index:1',
  },
  grid: {
    top: '4%',
    left: '2%',
    right: '50px',
    bottom: '0%',
    containLabel: true,
  },
  axisLabel: {
    interval: 0,
    showMaxLabel: true, //显示最大值
    showMinLabel: true, //显示最小值
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
      name: '进出人次',
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
  color,
  () => {
    option.color = [color.value, lightenColor(color.value, 50)]
  },
  { immediate: true }
)
onActivated(() => {
  tableSortRef.value.doLayout()
  // fetchData()
})

const isToday = (date: Record<string, any> | any): boolean => {
  return moment(date).format('YYYY-MM-DD').valueOf() !== moment().format('YYYY-MM-DD').valueOf()
}

const isHistory = (date: Record<string, any> | any): boolean => {
  return moment(date).format('YYYY-MM-DD').valueOf() >= moment().format('YYYY-MM-DD').valueOf()
}

const handleTabClick = (tab: TabsPaneContext, event: Event) => {
  activeName.value = tab.paneName as string
  if (activeName.value === 'today') {
    if (list.value.length === 0) {
      fetchData()
      fetchStatData()
      fetchRangeData()
    }
  } else if (activeName.value === 'history') {
    if (historyList.value.length === 0) {
      fetchHistoryData()
      fetchHistoryStatData()
    }
  }
}
const fetchData = async () => {
  try {
    listLoading.value = true
    const { data } = await getDoorPassLogList(omit(queryForm, 'searchDate'))
    list.value = data.list
    total.value = data.total
    listLoading.value = false
  } catch (err) {
    listLoading.value = false
  }
}
const fetchStatData = async () => {
  const { data } = await getDoorPassLogStat(omit(queryForm, 'searchDate'))
  employee.value = data.employee
  servicer.value = data.servicer
  visitor.value = data.visitor
}
const fetchRangeData = async () => {
  const { data } = await getDoorPassLogByTime(omit(queryForm, 'searchDate'))
  echartData.value = []
  echartLabel.value = []
  data.forEach(function (p: any) {
    echartData.value.push(p.total)
    echartLabel.value.push(p.range)
  })
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
  if (queryForm.searchDate) {
    queryForm.startDate = get(queryForm, ['searchDate', 0])
    queryForm.stopDate = get(queryForm, ['searchDate', 1])
  }
  queryForm.pageNo = 1
  fetchData()
  fetchStatData()
  fetchRangeData()
}

const exportData = async () => {
  exportLoading.value = true
  const params = {
    title: get(queryForm, 'title'),
    startDate: get(queryForm, ['searchDate', 0]) ? get(queryForm, ['searchDate', 0]) : moment().format('YYYY-MM-DD') + ' 00:00:00',
    stopDate: get(queryForm, ['searchDate', 1]) ? get(queryForm, ['searchDate', 1]) : moment().format('YYYY-MM-DD HH:mm:ss'),
  }
  const data: any = await exportDoorPassLog(params)
  download.excel(data, `通行记录-${moment().format('YYYYMMDD')}.xls`)
  exportLoading.value = false
}

const exportHistoryData = async () => {
  if (!get(historyQueryForm, 'searchDate')) {
    ElMessage.warning('请选择查询日期')
    return
  } else {
    // if (
    //   moment(get(historyQueryForm, ['searchDate', 1])).valueOf() >=
    //   moment(get(historyQueryForm, ['searchDate', 0])).valueOf() + 24 * 60 * 60 * 1000
    // ) {
    //   ElMessage.error('查询日期范围不能超过一天')
    //   return
    // }
  }
  exportLoading.value = true
  const params = {
    type: 2,
    title: get(historyQueryForm, 'title') ? get(historyQueryForm, 'title') : undefined,
    startDate: get(historyQueryForm, ['searchDate', 0]) ? get(historyQueryForm, ['searchDate', 0]) : undefined,
    stopDate: get(historyQueryForm, ['searchDate', 1]) ? get(historyQueryForm, ['searchDate', 1]) : undefined,
  }
  const data: any = await exportDoorPassLog(params)
  download.excel(data, `通行记录-${params.startDate}-${params.stopDate}.xls`)
  exportLoading.value = false
}
const fetchHistoryData = async () => {
  console.log("historyQueryForm",historyQueryForm)
  historyListLoading.value = true
  const { data } = await getDoorPassHistoryLogList(omit(historyQueryForm, 'searchDate'))
  historyList.value = data.list
  historyTotal.value = data.total
  historyListLoading.value = false
}
const fetchHistoryStatData = async () => {
  console.log("historyQueryForm",historyQueryForm)

  const { data } = await getDoorPassHistoryLogStat(omit(historyQueryForm, 'searchDate'))
  historyEmployee.value = data.employee
  historyServicer.value = data.servicer
  historyVisitor.value = data.visitor
}

const historyHandleSizeChange = (value: number) => {
  historyQueryForm.pageNo = 1
  historyQueryForm.pageSize = value
  fetchHistoryData()
}

const historyHandleCurrentChange = (value: number) => {
  historyQueryForm.pageNo = value
  fetchHistoryData()
}

const historyQueryData = () => {
  console.log(historyQueryForm)
  if (historyQueryForm.searchDate) {
    historyQueryForm.startDate = get(historyQueryForm, ['searchDate', 0])
    historyQueryForm.stopDate = get(historyQueryForm, ['searchDate', 1])
  }
  historyQueryForm.pageNo = 1
  fetchHistoryData()
  fetchHistoryStatData()
}

onBeforeMount(() => {
  fetchData()
  fetchStatData()
  fetchRangeData()
})
</script>
<template>

  <div class="passgroup-table-container table-auto-height">
    <vab-query-form>

      <vab-query-form-left-panel>
        <div class="custom-table-right-tools">
              旷视分组：
          <el-radio-group v-model="queryForm.type" @change="changeType">
            <el-radio-button v-for="(item, index) in list" :key="index" :label="item.groupId">{{ item.groupName }}</el-radio-button>
          </el-radio-group>
        </div>
      </vab-query-form-left-panel>
      <vab-query-form-right-panel>
        <el-button  type="danger" @click="handleEdit(retrunList)">编辑</el-button>
        <el-button  type="danger" @click="handleAdd(retrunList)">添加</el-button>
        <el-button  type="danger" @click="exportData">导出全部</el-button>

        <el-form inline label-width="49px" :model="queryForm" @submit.prevent>
          <el-form-item label="名称">
            <el-input v-model="queryForm.userName" clearable placeholder="请输入人员名称" />
          </el-form-item>
          <el-form-item label="">
            <el-button type="primary" @click="fetchData">查询</el-button>
          </el-form-item>
        </el-form>
      </vab-query-form-right-panel>
    </vab-query-form>
    <el-table ref="tableSortRef" v-loading="listLoading" :data="retrunList.userList">
      <el-table-column label="人员名称" prop="userName" />
      <el-table-column label="工号" prop="empNo" />
    </el-table>





    <!-- <el-table ref="tableSortRef" v-loading="listLoading" :data="list">
      <el-table-column label="分组名称" prop="groupName" width="100" />
      <el-table-column label="人员">
        <template #default="{ row }">
          <div>{{ row.userList?.map((item) => item.userName).join(',') }}</div>
        </template>
      </el-table-column>
      <el-table-column align="center" label="操作" width="150">
        <template #default="{ row }">
          <el-button text type="danger" @click="handleEdit(row)">编辑</el-button>
          <el-button text type="danger" @click="handleAdd(row)">添加</el-button>
        </template>
      </el-table-column>
      <template #empty>
        <el-empty class="vab-data-empty" description="暂无数据" />
      </template>
    </el-table>
    <el-pagination
      background
      :current-page="queryForm.pageNo"
      :layout="layout"
      :page-size="queryForm.pageSize"
      :total="total"
      @current-change="handleCurrentChange"
      @size-change="handleSizeChange"
    /> -->
    <vab-dialog v-model="dialogVisible" append-to-body destroy-on-close :title="title">
      <el-form :model="form" label-width="100px" v-if="title === '添加人员'">
        <el-form-item label="人员">
          <el-select
            v-model="form.userIds"
            filterable
            :loading="searchLoading"
            multiple
            placeholder="请输入姓名"
            remote
            :remote-method="remoteMethod"
            reserve-keyword
          >
            <el-option
              v-for="item in options"
              :key="item.userId"
              :label="item.realName + `(${item?.empNo || item?.virtualEmpNo})-->${item.departmentName}`"
              :value="item.userId"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <div v-if="title === '编辑人员'" class="tags">
        <el-tag v-for="tag in currentItem?.userList" :key="tag.userId" closable type="primary" @close="handleClose(tag.userId)">
          {{ tag.userName }}
        </el-tag>
      </div>
      <el-empty v-if="title === '编辑人员' && currentItem?.userList?.length == 0" description="暂无数据" />
      <template #footer>
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitForm">确 定</el-button>
      </template>
    </vab-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ElMessage } from 'element-plus'
import { doSearchUser } from '~/src/api/operate'
import { getAuthGroup, addUserGroup, updateUserGroup,exportUserGroup } from '/@/api/sence'




import moment from 'moment'
import download from '/@/utils/download'
defineOptions({
  name: 'PassGroup',
})
const exportLoading = ref<boolean>(false)
const retrunList = ref<any>({})
const title = ref<string>('添加人员')
const tableSortRef = ref<any>(null)
const list = ref<any>([])
const dialogVisible = ref<boolean>(false)
const searchLoading = ref(false)
const options = ref<any>([])
const listLoading = ref<boolean>(false)
const layout = ref<string>('total, sizes, prev, pager, next, jumper')
const total = ref<any>(0)
const currentItem = ref<any>({})
const queryForm = reactive<any>({
  userName:'',
  type:'',
  pageNo: 1,
  pageSize: 20,
})
const form = ref<any>({ userIds: [] })
const handleClose = (id) => {
  currentItem.value.userList = currentItem.value.userList.filter((item) => item.userId !== id)
}
const exportData = async () => {
  exportLoading.value = true
  const data: any = await exportUserGroup(queryForm)
  download.excel(data, `门禁权限组-${moment().format('YYYYMMDD')}.xls`)
  exportLoading.value = false
}
const remoteMethod = async (query: string) => {
  if (query) {
    searchLoading.value = true
    const res = await doSearchUser({ name: query })
    options.value = res.data.list
    searchLoading.value = false
  } else {
    options.value = []
    searchLoading.value = false
  }
}
const getList = () =>{
  list.value.forEach(function (ilist: any) {
    if(ilist.groupId === queryForm.type){
      retrunList.value =  ilist
      return
    }
  })
}
const changeType = () => {
  // console.log("type",queryForm.type)
  getList()
  // fetchData()
  // console.info(value)
}
const fetchData = async () => {
  try {
    listLoading.value = true
    const { data } = await getAuthGroup(queryForm)
    list.value = data.list
    total.value = data.total
    if(data.list.length!=0){
      queryForm.type = list.value[0].groupId
      getList()
    }

    console.log("list",list)
  } finally {
    listLoading.value = false
  }
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
const submitForm = async () => {
  if (title.value === '添加人员' && !form.value.userIds) {
    ElMessage.error('请选择人员')
    return
  }
  console.log("groupId",{ ...form.value, groupId: currentItem.value.groupId })
  const res =
    title.value === '添加人员'
      ? await addUserGroup({ ...form.value, groupId: currentItem.value.groupId })
      : await updateUserGroup({
          userIds: currentItem.value.userList?.map((item: { userId: any }) => item.userId),
          groupId: currentItem.value.groupId,
        })
  if (res.code === '200') {
    ElMessage.success(title.value === '添加人员' ? '添加成功' : '修改成功')
    dialogVisible.value = false
    form.value.userIds = []
    fetchData()
  } else {
    ElMessage.error(res.msg)
  }
}
const handleAdd = (row) => {
  title.value = '添加人员'
  currentItem.value = row
  dialogVisible.value = true
}
const handleEdit = (row) => {
  currentItem.value = row
  title.value = '编辑人员'
  dialogVisible.value = true
}
onBeforeMount(() => {
  fetchData()
})
</script>
<style scoped>
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>
<template>
  <div class="passgroup-table-container table-auto-height">
    <!-- <vab-query-form>
      <vab-query-form-top-panel>
        <el-form inline label-width="49px" :model="queryForm" @submit.prevent>
          <el-form-item label="名称">
            <el-input v-model="queryForm.title" clearable placeholder="请输入组名称" />
          </el-form-item>
          <el-form-item label="">
            <el-button type="primary" @click="fetchData">查询</el-button>
          </el-form-item>
        </el-form>
      </vab-query-form-top-panel>
    </vab-query-form> -->

    <el-table ref="tableSortRef" v-loading="listLoading" :data="list">
      <el-table-column label="楼层" prop="name" width="100" />
      <el-table-column label="授权人员名单">
        <template #default="{ row }">
          <div>{{ row.userList?.map((item) => item.userName).join(',') }}</div>
        </template>
      </el-table-column>
      <el-table-column align="center" label="操作" width="150">
        <template #default="{ row }">
          <el-button text type="danger" @click="handleEdit(row)">编辑</el-button>
          <el-button text type="danger" @click="handleAdd(row)">添加</el-button>
        </template>
      </el-table-column>
      <template #empty>
        <el-empty class="vab-data-empty" description="暂无数据" />
      </template>
    </el-table>
    <el-pagination
      background
      :current-page="queryForm.pageNo"
      :layout="layout"
      :page-size="queryForm.pageSize"
      :total="total"
      @current-change="handleCurrentChange"
      @size-change="handleSizeChange"
    />
    <vab-dialog v-model="dialogVisible" append-to-body destroy-on-close :title="title">
      <el-form :model="form" label-width="100px" v-if="title === '添加人员'">
        <el-form-item label="人员">
          <el-select
            v-model="form.userIds"
            filterable
            :loading="searchLoading"
            multiple
            placeholder="请输入姓名"
            remote
            :remote-method="remoteMethod"
            reserve-keyword
          >
            <el-option
              v-for="item in options"
              :key="item.userId"
              :label="item.realName + `(${item?.empNo || item?.virtualEmpNo})-->${item.departmentName}`"
              :value="item.userId"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <div v-if="title === '编辑人员'" class="tags">
        <el-tag v-for="tag in currentItem?.userList" :key="tag.userId" closable type="primary" @close="handleClose(tag.userId)">
          {{ tag.userName }}
        </el-tag>
      </div>
      <el-empty v-if="title === '编辑人员' && currentItem?.userList?.length == 0" description="暂无数据" />
      <template #footer>
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitForm">确 定</el-button>
      </template>
    </vab-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ElMessage } from 'element-plus'
import { doSearchUser } from '~/src/api/operate'
import { getElevatorUserList, addUserElevator, updateUserElevator } from '/@/api/sence'

defineOptions({
  name: 'PassGroup',
})
const title = ref<string>('添加人员')
const tableSortRef = ref<any>(null)
const list = ref<any>([])
const dialogVisible = ref<boolean>(false)
const searchLoading = ref(false)
const options = ref<any>([])
const listLoading = ref<boolean>(false)
const layout = ref<string>('total, sizes, prev, pager, next, jumper')
const total = ref<any>(0)
const currentItem = ref<any>({})
const queryForm = reactive<any>({
  pageNo: 1,
  pageSize: 20,
})
const form = ref<any>({ userIds: [] })
const handleClose = (id) => {
  currentItem.value.userList = currentItem.value.userList.filter((item) => item.userId !== id)
}
const remoteMethod = async (query: string) => {
  if (query) {
    searchLoading.value = true
    const res = await doSearchUser({ name: query })
    options.value = res.data.list
    searchLoading.value = false
  } else {
    options.value = []
    searchLoading.value = false
  }
}
const fetchData = async () => {
  try {
    listLoading.value = true
    const { data } = await getElevatorUserList(queryForm)
    list.value = data.list
    total.value = data.total
  } finally {
    listLoading.value = false
  }
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
const submitForm = async () => {
  if (title.value === '添加人员' && !form.value.userIds) {
    ElMessage.error('请选择人员')
    return
  }
  const res =
    title.value === '添加人员'
      ? await addUserElevator({ ...form.value, floor: currentItem.value.name })
      : await updateUserElevator({
          userIds: currentItem.value.userList?.map((item: { userId: any }) => item.userId),
          floor: currentItem.value.name,
        })
  if (res.code === '200') {
    ElMessage.success(title.value === '添加人员' ? '添加成功' : '修改成功')
    dialogVisible.value = false
    form.value.userIds = []
    fetchData()
  } else {
    ElMessage.error(res.msg)
  }
}
const handleAdd = (row) => {
  title.value = '添加人员'
  currentItem.value = row
  dialogVisible.value = true
}
const handleEdit = (row) => {
  currentItem.value = row
  title.value = '编辑人员'
  dialogVisible.value = true
}
onBeforeMount(() => {
  fetchData()
})
</script>
<style scoped>
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>
<template>
  <div class="facelib-container no-background-container auto-height-container">
    <vab-pane-split class="hidden-xs-only" ratio="4/20">
      <template #one>
        <vab-card class="auto-height-card" style="overflow-y:auto">
          <!--          <el-button @click="showTeamEdit">添加自定义分组</el-button>-->
          <org-tree :default-expand-all="false" style="overflow-y: auto" @handle-dep-select="handleDepSelect" />
        </vab-card>
      </template>
      <template #two>
        <vab-card class="auto-height-card">
          <el-row :gutter="20">
            <el-col :span="16">
              <el-breadcrumb separator-class="el-icon-arrow-right" style="padding-bottom: 30px">
                <el-breadcrumb-item v-for="(item, index) in crumblist" :key="index">
                  {{ item.title }}
                </el-breadcrumb-item>
              </el-breadcrumb>
            </el-col>
            <el-col :span="8" style="text-align: right">
              <el-button
                v-permissions="{ role: ['Admin'], permission: ['delete:system'], mode: 'allOf' }"
                :icon="Delete"
                type="danger"
                @click="handleDelete"
              >
                批量删除
              </el-button>
            </el-col>
          </el-row>

          <vab-query-form>
            <vab-query-form-left-panel :span="12">
              <el-form inline :model="queryForm" @submit.prevent>
                <el-form-item>
                  <el-button v-if="currentDep && currentDep.sourceFrom === 'self'" :icon="Plus" type="primary" @click="handleAdd">
                    添加临时人员
                  </el-button>
<!--                  <el-button type="primary" @click="uploadDialogFormVisible = true">批量上传人脸</el-button>-->
<!--                  <el-button type="primary" @click="uploadDialogFormVisible = true">下发日志</el-button>-->
                </el-form-item>
              </el-form>
            </vab-query-form-left-panel>
            <vab-query-form-right-panel :span="12">
              <el-form inline :model="queryForm" @submit.prevent>
                <el-form-item style="padding-left: 20px">
                  <el-input v-model.trim="queryForm.username" clearable placeholder="请输入姓名" />
                </el-form-item>
                <el-form-item>
                  <el-button :icon="Search" :loading="listLoading" type="primary" @click="queryData">查询</el-button>
                </el-form-item>
              </el-form>
            </vab-query-form-right-panel>
          </vab-query-form>
          <el-table v-loading="listLoading" border :data="list" @selection-change="setSelectRows">
            <el-table-column type="selection" width="38" />
            <el-table-column align="center" label="id" prop="id" show-overflow-tooltip />
            <el-table-column align="center" label="人脸照片" width="100">
              <template #default="{ row }">
                <el-image fit="contain" lazy :src="row.faceInfo && row.faceInfo.faceUrl ? getUrl(row.faceInfo.faceUrl) : 'blank'" @click="row.faceInfo && row.faceInfo.faceUrl && showPic(getUrl(row.faceInfo.faceUrl))">
                  <div class="image-slot">
                    <i class="el-icon-picture-outline"></i>
                  </div>
                </el-image>
              </template>
            </el-table-column>
            <el-table-column align="center" label="姓名"  width="100">
              <template #default="{ row }">
                <div style="display: flex; justify-content: center">
                  <div>{{ row.realName }}</div>
                  <vab-icon v-if="row.gender == 1" icon="women-line" style="color: pink" />
                  <vab-icon v-if="row.gender == 0" icon="men-line" style="color: dodgerblue" />
                </div>
              </template>
            </el-table-column>
            <el-table-column align="center" label="旷视" prop="status2" show-overflow-tooltip width="200">
              <template #default="{ row }">
                <span v-if="!row.faceInfo || (row.faceInfo && row.faceInfo.megviiPushFlag === '0')">
                  <span class="vab-dot vab-dot-error"><span></span></span>
                  待下发
                </span>
                <span v-else-if="row.faceInfo && row.faceInfo.megviiPushFlag === '1'">
                  <span class="vab-dot vab-dot-success"><span></span></span>
                </span>
                <span v-else-if="row.faceInfo && row.faceInfo.megviiPushFlag === '2'">
                  <span class="vab-dot vab-dot-error"><span></span></span>
                  {{ row.faceInfo.megviiPushMsg }}
                </span>
              </template>
            </el-table-column>
            <el-table-column align="center" label="海康" prop="status2" show-overflow-tooltip width="200">
              <template #default="{ row }">
                <span v-if="!row.faceInfo || (row.faceInfo && row.faceInfo.hikPushFlag === '0')">
                  <span class="vab-dot vab-dot-error"><span></span></span>
                  待下发
                </span>
                <span v-else-if="row.faceInfo && row.faceInfo.hikPushFlag  === '1'">
                  <span class="vab-dot vab-dot-success"><span></span></span>
                  下发成功
                </span>
                <span v-else-if="row.faceInfo && row.faceInfo.hikPushFlag  === '2'">
                  <span class="vab-dot vab-dot-error"><span></span></span>
                  {{ row.faceInfo.hikPushMsg }}
                </span>
              </template>
            </el-table-column>
            <el-table-column align="center" label="卡号" prop="cardNum" show-overflow-tooltip width="200" />
            <el-table-column align="center" label="工号" prop="empNo" show-overflow-tooltip width="200" />
            <el-table-column align="center" label="虚拟工号" prop="virtualEmpNo" show-overflow-tooltip width="200" />
            <el-table-column align="center" label="邮箱" prop="email" show-overflow-tooltip width="200"/>
            <el-table-column align="center" label="部门" width="200" prop="departmentName" />
            <el-table-column align="center" label="状态">
              <template #default="{ row }">
                <el-tag :type="statusFilter(row.quitStatus)">
                  {{ statusTextFilter(row.quitStatus) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column align="center" fixed="right" label="操作" width="300">
              <template #default="{ row }">
                <el-button text type="primary" @click="faceUpload(row)">人脸</el-button>
                <el-button text type="primary" @click="handleEdit(row)">卡号</el-button>
                <el-button text type="primary" @click="pushface(row)">下发</el-button>
                <el-button v-if="currentDep && currentDep.sourceFrom === 'self'" text type="primary" @click="handleDelete(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
            <template #empty>
              <el-empty class="vab-data-empty" description="暂无数据" />
            </template>
          </el-table>
          <el-pagination
            background
            :current-page="queryForm.pageNo"
            :layout="layout"
            :page-size="queryForm.pageSize"
            :total="total"
            @current-change="handleCurrentChange"
            @size-change="handleSizeChange"
          />
        </vab-card>
<!--        <el-dialog v-model="uploadDialogFormVisible" append-to-body draggable title="批量上传" width="500px" @close="close">-->
<!--          <template #header>拖拽上传</template>-->
<!--          <sync-script-upload-drag-and-drop />-->
<!--          <template #footer>-->
<!--            <el-button @click="close">取 消</el-button>-->
<!--            <el-button type="primary" @click="uploadsave">确 定</el-button>-->
<!--          </template>-->
<!--        </el-dialog>-->
<!--        <el-drawer v-model="syncArea" append-to-body draggable title="选择同步范围" width="500px" @close="close">-->
<!--          <org-tree ref="syncTree" :default-expand-all="false" :show-checkbox="true" style="overflow-y: auto" />-->
<!--          <template #footer>-->
<!--            <el-button @click="close">取 消</el-button>-->
<!--            <el-button type="primary" @click="saveSync">确 定</el-button>-->
<!--          </template>-->
<!--        </el-drawer>-->
        <el-dialog v-model="faceUplad" append-to-body draggable title="人脸上传" width="250px" @close="close">
          <el-upload
            accept="image/png,image/jpeg"
            :action="uploadUrl"
            :before-upload="beforeAvatarUpload"
            class="avatar-uploader"
            :data="userObj"
            :headers="customHeaders"
            :on-success="handleAvatarSuccess"
            :show-file-list="false"
          >
            <img v-if="imageUrl" alt="" class="avatar" :src="imageUrl" />
            <el-icon v-else class="avatar-uploader-icon"><plus /></el-icon>
          </el-upload>
          <template #footer>
            <el-button @click="close">取 消</el-button>
            <el-button type="primary" @click="uploadsave">确 定</el-button>
          </template>
        </el-dialog>
      </template>
    </vab-pane-split>
<!--    <team-edit ref="teamDialog" />-->
    <face-user-management-edit ref="editRef" @fetch-data="fetchData" />
    <el-dialog v-model="showViewer" style="text-align: center">
      <el-image fit="contain" :src="imgValue" />
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { Delete, Plus, Search } from '@element-plus/icons-vue'
import { getFaceUserList,doUserDelete } from '/@/api/sense'
import type { UploadProps } from 'element-plus'
import { ElMessage } from 'element-plus'
import { inject, ref } from 'vue'
import { useUserStore } from '/@/store/modules/user.ts'
defineOptions({
  name: 'FaceLib',
})
const showViewer = ref<boolean>(false)
const imgValue = ref<string>('')
const editRef = ref<any>(null)
const publish = inject('publish') // 发布信息
const userObj = ref<any>({})
const customHeaders = ref<any>({})
const uploadUrl = ref<any>('')
// const uploadDialogFormVisible = ref<boolean>(false)
const faceUplad = ref<boolean>(false)
// const syncTree = ref<any>(null)
const $baseConfirm: any = inject('$baseConfirm')
const $baseMessage = inject<any>('$baseMessage')
const list = ref<any>([])
const listLoading = ref<boolean>(true)
// const teamDialog = ref<any>(null)
const currentDep = ref<any>(null)
const layout = ref<string>('total, sizes, prev, pager, next, jumper')
const total = ref<any>(0)
const selectRows = ref<any>([])
const queryForm = reactive<any>({
  pageNo: 1,
  pageSize: 20,
  username: '',
  depid: '',
})
const handleAdd = () => {
  // console.info(currentDep.value)
  editRef.value.showEdit(currentDep.value)
}
const handleEdit = (row: any = {}) => {
  // console.info(currentDep.value)
  editRef.value.showEdit(currentDep.value, row)
}
const crumblist = ref<any>([])
//tree
const getUrl = (url: string) => {
  // console.info(url)
  // console.info(`${import.meta.env.VITE_APP_BASE_URL}${url}`)
  return `https://buildingos.ai${url}?t=${new Date()}`
  // return `http://10.205.66.4${url}?t=${new Date()}`
}
const dialogFormVisible = ref<boolean>(false)
// const syncArea = ref<boolean>(false)

const close = () => {
  imageUrl.value = ''
  faceUplad.value = false
  // dialogFormVisible.value = false
}
//tree end
const setSelectRows = (value: string) => {
  selectRows.value = value
}

const faceUpload = (row: any = {}) => {
  // editRef.value.showEdit(currentDep.value, row)
  if(row.faceInfo&&row.faceInfo.faceUrl){
    imageUrl.value = getUrl(row.faceInfo.faceUrl)
  }
  // console.info(imageUrl.value)
  userObj.value = { userId: row.userId }
  faceUplad.value = true
}

const pushface = (row: any) => {
  ElMessage.success('重新下发成功!')
  publish('/iot/action/user/face/push', JSON.stringify({ userId: row.userId }))
}
// const showTeamEdit = () => {
//   teamDialog.value.showEdit()
// }
const uploadsave = () => {}
const statusFilter = (status: number) => {
  const statusArry = ['success', 'danger', 'info']
  // const statusMap: any = {
  //   published: 'success',
  //   draft: '',
  //   deleted: 'danger',
  // }
  //在职状态:0.在职;1.离职;2.转岗
  return statusArry[status]
}
const statusTextFilter = (status: number) => {
  const statusArry = ['在职', '离职', '转岗']
  // const statusMap: any = {
  //   published: 'success',
  //   draft: '',
  //   deleted: 'danger',
  // }
  //在职状态:0.在职;1.离职;2.转岗
  return statusArry[status]
}
const handleDepSelect = (node: any = {}, tree: any = {}, crumb: any = {}) => {
  if (node.type == 'org') {
    queryForm.orgid = node.value
    queryForm.depid = ''
  } else {
    queryForm.orgid = node.orgId
    queryForm.depid = node.value
  }

  currentDep.value = node

  crumblist.value = currentDepCrumbMake(node, crumb)

  fetchData()
}
const saveSync = () => {
  // const checkedKeys = syncTree.value.getSyncReturn()
  // const checkedNodes = treeData.value.filter(node =>
  //   checkedKeys.includes(node.id)
  // );
  // console.log('选中的节点:', checkedKeys)
}
const currentDepCrumbMake = (org: any, crumbObj: any) => {
  const pathArr = org.orgPath.split('|')
  const crumbs = []
  for (let i = 0; i < pathArr.length; i++) {
    if (pathArr[i] == '0' && crumbObj['org'][org.orgId]) {
      crumbs.push({ title: crumbObj['org'][org.orgId] })
    } else if (crumbObj['department'][pathArr[i]]) {
      crumbs.push({ title: crumbObj['department'][pathArr[i]] })
    }
  }
  return crumbs
}
const showPic = (src: string) => {
  console.info(src)
  showViewer.value = true
  imgValue.value = src
}
const handleDelete = (row: any = {}) => {
  if (row.id) {
    $baseConfirm('您确定要删除当前员工吗', null, async () => {
      const { msg }: any = await doUserDelete({ ids: row.id })
      const userObj = { userId: row.id }
      publish('/iot/action/user/remove', JSON.stringify(userObj))
      $baseMessage(msg, 'success', 'hey')
      await fetchData()
    })
  } else {
    if (selectRows.value.length > 0) {
      const ids = selectRows.value.map((item: { id: any }) => item.id).join()
      $baseConfirm('您确定要删除选中员工吗', null, async () => {
        const { msg }: any = await doUserDelete({ ids })
        const userObj = { userId: row.id }
        publish('/iot/action/user/remove', JSON.stringify(userObj))
        $baseMessage(msg, 'success', 'hey')
        await fetchData()
      })
    } else {
      $baseMessage('您未选中任何员工', 'warning', 'hey')
    }
  }
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
  queryForm.depid = ''
  fetchData()
}

const fetchData = async () => {
  listLoading.value = true
  try {
    const { data } = await getFaceUserList(queryForm)
    console.info(data)
    list.value = data.list
    total.value = data.total
    listLoading.value = false
  } catch {
    listLoading.value = false
  }
}

const imageUrl = ref('')

const handleAvatarSuccess: UploadProps['onSuccess'] = (response, uploadFile) => {
  // imageUrl.value = URL.createObjectURL(uploadFile.raw!)
  ElMessage.success('上传成功!')
  publish('/iot/action/user/face/push', JSON.stringify(userObj.value))
  imageUrl.value = ""
  faceUplad.value = false
  fetchData()
}

const beforeAvatarUpload: UploadProps['beforeUpload'] = (rawFile) => {

  const imgType = ["image/jpeg","image/png"]
  if (!imgType.includes(rawFile.type)){
    ElMessage.error("上传图片不符合所需的格式！")
    return false
  }

  if (rawFile.size / 1024 / 1024 / 10 > 2) {
    ElMessage.error('图片文件大小超过200KB!')
    return false
  }
  return true
}
onBeforeMount(() => {
  const userStore = useUserStore()
  const { token } = userStore
  if (token) {
    customHeaders.value = {
      Authorization: `Bearer ${token}`,
    }
  }
  uploadUrl.value = `${import.meta.env.VITE_APP_BASE_URL}/sense/uploadFaceImage`
  fetchData()
})
</script>
<style lang="scss" scoped>
.avatar-uploader .avatar {
  width: 178px;
  height: 178px;
  display: block;
}
.facelib-container {
  width: 100%;

  :deep() {
    .el-card {
      margin-bottom: 0;
    }
    .split {
      .resizer {
        height: var(--el-container-height) !important;
        margin-right: calc(var(--el-margin) / 2);
        margin-left: calc(var(--el-margin) / 2);
      }
    }
  }
}
</style>
<style>
.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
}
</style>
<template>
  <div class="door-auth-container no-background-container">
    <el-tabs v-model="activeName" type="border-card">
      <el-tab-pane label="授权" name="first">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-tabs v-model="orgActiveName" type="border-card">
              <el-tab-pane label="部门" name="org-first">
                <org-tree default-expand-all="true" />
              </el-tab-pane>
              <el-tab-pane label="组" name="team-first">
                <team-tree default-expand-all="true" />
              </el-tab-pane>
              <el-tab-pane label="员工" name="org-second">
                <vab-query-form>
                  <vab-query-form-top-panel :span="12">
                    <el-form inline label-width="49px" :model="queryForm" @submit.prevent>
                      <el-form-item label="姓名">
                        <el-input v-model="queryForm.title" clearable placeholder="姓名" />
                      </el-form-item>
                      <el-form-item v-show="!fold" label="邮箱">
                        <el-input v-model="queryForm.title" clearable placeholder="邮箱" />
                      </el-form-item>
                      <el-form-item v-show="!fold" label="手机">
                        <el-input v-model="queryForm.title" clearable placeholder="手机" />
                      </el-form-item>
                      <el-form-item v-show="!fold" label="工号">
                        <el-input v-model="queryForm.title" clearable placeholder="工号" />
                      </el-form-item>
                      <el-form-item>
                        <el-button :icon="Search" native-type="submit" type="primary">查询</el-button>
                        <el-button class="hidden-xs-only" text type="primary" @click="handleFold">
                          <span v-if="fold">展开</span>
                          <span v-else>合并</span>
                          <vab-icon class="vab-dropdown" :class="{ 'vab-dropdown-active': fold }" icon="arrow-up-s-line" />
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </vab-query-form-top-panel>
                </vab-query-form>
                <el-row :gutter="20">
                  <el-col v-for="(item, index) in iconList" :key="index" :span="24">
                    <vab-link :to="item.link">
                      <vab-card class="icon-panel" style="display: flex">
                        <el-image fit="contain" lazy :src="item.imgUrl" style="width: 50px" />
                        <div class="icon-panel-title">
                          {{ item.title }}
                          <div class="icon-panel-tips">{{ item.tips }}</div>
                        </div>
                      </vab-card>
                    </vab-link>
                  </el-col>
                </el-row>
              </el-tab-pane>
            </el-tabs>
          </el-col>
          <el-col :span="12">
            <el-card
              shadow="hover"
              style="overflow-y: auto; height: calc(var(--el-container-height) - var(--el-padding) - 52px) !important"
            >
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-breadcrumb separator-class="el-icon-arrow-right" style="padding-bottom: 30px">
                    <el-breadcrumb-item v-for="(item, index) in crumblist" :key="index">
                      {{ item.title }}
                    </el-breadcrumb-item>
                  </el-breadcrumb>
                </el-col>
                <el-col :span="12">
                  <el-button style="float: right" type="primary">保存</el-button>
                </el-col>
              </el-row>
              <vab-card skeleton>
                <template #header>大楼通行权限</template>
                <el-form ref="formRef" class="demo-form">
                  <el-form-item label="时间表" prop="region">
                    <el-select placeholder="请此权限生效的时间表">
                      <el-option label="全部时间" value="shanghai" />
                      <el-option label="工作" value="beijing" />
                      <el-option label="周末" value="beijing" />
                      <el-option label="节假日" value="beijing" />
                    </el-select>
                  </el-form-item>
                </el-form>
                <el-transfer v-model="value2" :data="data2" :filter-method="filterMethod" filterable :titles="['门禁组', '已授权门禁组']" />
              </vab-card>
              <vab-card>
                <template #header>楼层通行权限</template>
                <el-form ref="formRef" class="demo-form">
                  <el-form-item label="时间表" prop="region">
                    <el-select placeholder="请此权限生效的时间表">
                      <el-option label="全部时间" value="shanghai" />
                      <el-option label="工作" value="beijing" />
                      <el-option label="周末" value="beijing" />
                      <el-option label="节假日" value="beijing" />
                    </el-select>
                  </el-form-item>
                </el-form>
                <el-transfer v-model="value3" :data="data3" filterable :titles="['门禁组', '已授权门禁组']" />
              </vab-card>
              <vab-card>
                <template #header>层内通行权限</template>
                <el-form ref="formRef" class="demo-form">
                  <el-form-item label="时间表" prop="region">
                    <el-select placeholder="请此权限生效的时间表">
                      <el-option label="全部时间" value="shanghai" />
                      <el-option label="工作" value="beijing" />
                      <el-option label="周末" value="beijing" />
                      <el-option label="节假日" value="beijing" />
                    </el-select>
                  </el-form-item>
                </el-form>
                <el-transfer v-model="value4" :data="data4" filterable :titles="['门禁组', '已授权门禁组']" />
              </vab-card>
            </el-card>
          </el-col>
          <el-col :span="6">
            <vab-card skeleton>
              <template #header>当前权限门禁</template>
              <el-tag v-for="i in 40" :key="i" style="margin: 10px">23F 大门{{ i }}</el-tag>
            </vab-card>
          </el-col>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="时间表" name="second">
        <el-empty class="vab-data-empty" description="暂无数据" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script lang="ts" setup>
import { Search } from '@element-plus/icons-vue'

defineOptions({
  name: 'DoorAuthTable',
})
/* 可搜索过滤 */

interface Option2 {
  key: number
  label: string
  initial: string
}

const generateData2 = () => {
  const data: Option2[] = []
  const states = ['大楼门禁组']
  const initials = ['BUILDALL']
  states.forEach((city, index) => {
    data.push({
      label: city,
      key: index,
      initial: initials[index],
    })
  })
  return data
}
const generateData3 = () => {
  const data: Option2[] = []
  const states = ['全楼门禁组', '三区楼层组', '四区楼层组', '五区楼层组']
  const initials = ['ALL', 'TH', 'THOUR', 'FIVE']
  states.forEach((city, index) => {
    data.push({
      label: city,
      key: index,
      initial: initials[index],
    })
  })
  return data
}
const generateData4 = () => {
  const data: Option2[] = []
  const states = ['22F储物室', '23F储物室', '32F储物室', '34F储物室']
  const initials = ['22F', '23F', '32F', '34F']
  states.forEach((city, index) => {
    data.push({
      label: city,
      key: index,
      initial: initials[index],
    })
  })
  return data
}
const data2 = ref<Option2[]>(generateData2())
const value2 = ref([])

const data3 = ref<Option2[]>(generateData3())
const value3 = ref([])

const data4 = ref<Option2[]>(generateData4())
const value4 = ref([])

const filterMethod = (query: any, item: any) => {
  return item.initial.toLowerCase().includes(query.toLowerCase())
}
const iconList = [
  {
    icon: 'bank-line',
    imgUrl: 'https://face.gemdale.com/pub/face/20230515/ganlin@gemdalepi.com.jpg',
    title: '何铮',
    tips: 'jimmy@buildingos.ai',
    link: '',
  },
  {
    icon: 'copyright-line',
    imgUrl: 'https://face.gemdale.com/pub/face/20230515/ganlin@gemdalepi.com.jpg',
    title: '何成',
    tips: 'hezheng@buildingos.ai',
    link: '',
  },
  {
    icon: 'book-3-line',
    imgUrl: 'https://face.gemdale.com/pub/face/20230515/ganlin@gemdalepi.com.jpg',
    title: '何文革',
    tips: 'hewg@buildingos.ai',
    link: '',
  },
  {
    icon: 'check-double-line',
    imgUrl: 'https://face.gemdale.com/pub/face/20230515/ganlin@gemdalepi.com.jpg',
    title: '何清风',
    tips: 'heqf@buildingos.ai',
    link: '',
  },
  {
    icon: 'codepen-line',
    imgUrl: 'https://face.gemdale.com/pub/face/20230515/ganlin@gemdalepi.com.jpg',
    title: '何骥',
    tips: 'heji@buildingos.ai',
    link: '',
  },
]
const activeName = ref<string>('first')
const orgActiveName = ref<string>('org-first')
const queryForm = reactive<any>({
  pageNo: 1,
  pageSize: 20,
})
const fold = ref<boolean>(true)
const crumblist = ref<any>([{ title: '极企总部' }, { title: '行政IT' }, { title: '技术部门' }])
const handleFold = () => {
  fold.value = !fold.value
}
</script>

<style lang="scss" scoped>
.door-auth-container {
  :deep() {
    .el-tabs {
      border-radius: var(--el-border-radius-base);

      &__nav-wrap {
        border-radius: var(--el-border-radius-base);
      }

      .el-tab-pane {
        display: flex;
        flex-direction: column;
        height: calc(var(--el-container-height) - var(--el-padding) - 52px) !important;

        .vab-query-form {
          .el-form {
            .el-form-item:first-child {
              margin: 0 !important;

              .el-check-tag,
              .el-form-item__label {
                margin: 0 10px 5px 0;
                border-radius: 99px;
              }
            }
          }
        }

        .el-table {
          flex: 1;
        }
      }
    }
  }
}
</style>
<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="24">
        <vab-card style="background-color: transparent !important">
          <el-button-group style="padding-left: 10px">
            <el-button type="info">三区</el-button>
            <el-button type="info">四区</el-button>
            <el-button type="info">五区</el-button>
          </el-button-group>
          <el-button-group style="padding-left: 10px">
            <el-button :icon="Menu" type="default" @click="viewtype = 'sand'">沙盘</el-button>
            <el-button :icon="Reading" type="default" @click="viewtype = 'map'">地图</el-button>
          </el-button-group>
          <space-panel v-if="viewtype == 'sand'" :spaces-data="floors" spaces-type="door" @open-dialog="hideAddPanel" />
          <map-panel v-if="viewtype == 'map'" map-id="doordevice" />
        </vab-card>
      </el-col>
<!--      <el-col :span="6">-->
<!--        <head-card background="white" icon="" :mainnumber="443" percentage="10%" title="今日进入次数" />-->
<!--        <head-card background="white" icon="" :mainnumber="443" percentage="10%" title="今日离开次数" />-->
<!--        <head-card background="white" icon="" :mainnumber="99" percentage="10%" pix="%" title="设备在线率" />-->
<!--        <head-card background="white" icon="" :mainnumber="4343" percentage="10%" title="总开门次数" />-->
<!--        <head-card background="white" icon="" :mainnumber="132" percentage="10%" title="总设备数" />-->
<!--      </el-col>-->
    </el-row>
    <door-device-detail-panel ref="editRef" @fetch-data="fetchData" />
  </div>
</template>

<script lang="ts" setup>
import { Reading, Menu } from '@element-plus/icons-vue'
import DoorDeviceDetailPanel from '/@/views/sence/pass/parsonpass/doordevice/vabAutoComponents/DoorDeviceDetailPanel.vue'
import SpacePanel from '/@vab/components/SpacePanel/index.vue'
import { getDoorList } from "/@/api/sense.ts";
import { ref } from "vue";
const userStore = useUserStore()
const { spaceCode } = storeToRefs(userStore)
import { getSpaceFloorList } from "/@/api/space.ts";
import { useUserStore } from "/@/store/modules/user.ts";
defineOptions({
  name: 'DoorDevice',
})
const queryForm = reactive<any>({
  pageNo: 1,
  pageSize: 1000,
  username: '',
  depid: '',
})
const total = ref<any>(0)
const listLoading = ref<boolean>(true)
const list = ref<any>([])

const editRef = ref<any>(null)
const viewtype = ref<string>('sand')
const floors = ref([
  {
    floorName: '1f',
    floorNum: 1,
    areaId: 1,
    floorSquare: 1223.2,
  },
  {
    floorName: '2f',
    floorNum: 2,
    areaId: 1,
    floorSquare: 1323.2,
  },
])
const spacedata = [
  {
    floor: '23F',
    desc: '2321m²',
    rooms: [],
  },
  {
    floor: '24F',
    desc: '1321m²',
    rooms: [],
  },
  {
    floor: '25F',
    desc: '1321m²',
    rooms: [],
  },
  {
    floor: '26F',
    desc: '1321m²',
    rooms: [
      { name: '机房', hasperson: false, sensor: [], desc: '人脸门禁' },
      { name: '消防楼梯间', hasperson: false, sensor: [], desc: '人脸门禁' },
      { name: '货梯楼梯间', hasperson: false, sensor: [], desc: '人脸门禁' },
      { name: 'VIP电梯厅', hasperson: false, sensor: [], desc: '人脸门禁' },
      { name: '储物间1', hasperson: false, sensor: [], desc: '人脸门禁' },
      { name: '储物间2', hasperson: false, sensor: [], desc: '人脸门禁' },
      { name: '储物间3', hasperson: false, sensor: [], desc: '人脸门禁' },
    ],
  },
  {
    floor: '27F',
    desc: '1321m²',
    rooms: [],
  },
  {
    floor: '28F',
    desc: '1321m²',
    rooms: [],
  },
  {
    floor: '29F',
    desc: '1321m²',
    rooms: [],
  },
  {
    floor: '30F',
    desc: '1321m²',
    rooms: [],
  },
  {
    floor: '31F',
    desc: '1321m²',
    rooms: [],
  },
  {
    floor: '32F',
    desc: '2321m²',
    rooms: [],
  },
]
const hideAddPanel = (item: any) => {
  console.info(item)
  console.info('+++++++++++++++++++++++++++')
  // this.fetchData();
  editRef.value.showEdit()
  // editRef.value.showEdit()
}
const fetchData = async () => {
  console.info('+++++-------------------++++')
  listLoading.value = true
  try {
    const { data } = await getDoorList(queryForm)
    console.info(data)
    list.value = data.list
    total.value = data.total
    listLoading.value = false
  } catch {
    listLoading.value = false
  }

}

const fetchFloorsData = async () => {
  listLoading.value = true
  const { data } = await getSpaceFloorList({ spaceCode: spaceCode.value })
  floors.value = data.SpaceFloorList
  listLoading.value = false
  console.info(floors.value)
}
onBeforeMount(() => {
  fetchFloorsData()
  fetchData()
})
</script>

```