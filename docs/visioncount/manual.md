# 操作说明（智能楼宇AI感知物联系统 Buildingos.ai.visionCount）

## 目录
1 引言
1.1 编写目的
1.2 名词定义
1.3 文档读者
1.4 文档约定
2 系统综述
2.1 设计目标
2.2 典型应用场景
2.3 架构与模块
2.4 部署拓扑与网络
3 硬件与软件环境
3.1 摄像机选型与参数
3.2 推理主机/GPU 配置建议
3.3 边缘设备与网络
3.4 操作系统与中间件
4 安装与部署
4.1 安装包与目录结构
4.2 服务启动与自检
4.3 首次初始化向导
4.4 版本升级与备份
5 权限与安全
5.1 角色与权限矩阵
5.2 认证与单点登录
5.3 审计日志与留痕
5.4 数据加密与隐私
6 基础配置
6.1 组织与站点
6.2 楼层与区域
6.3 设备与资源
6.4 通知与订阅
7 摄像头接入
7.1 通道与流地址
7.2 拉流与转码策略
7.3 断流重连与心跳
7.4 通道健康监测
8 模型管理
8.1 模型库与版本
8.2 阈值与置信度
8.3 输入预处理与后处理
8.4 性能参数与并发
9 任务编排
9.1 计数任务
9.2 在岗感知任务
9.3 多摄融合任务
9.4 计划与调度
10 区域配置
10.1 多边形区域编辑
10.2 楼层映射与坐标系
10.3 人流方向与通行线
10.4 遮挡与误报抑制
11 计算与缓存
11.1 实时计算通道
11.2 边缘缓存策略
11.3 断点续传与重试
11.4 数据落库与分层
12 联动与告警
12.1 规则与条件
12.2 阈值与时段
12.3 设备联动（照明/空调）
12.4 告警路由与抑制
13 报表与分析
13.1 趋势与对比
13.2 热力图与占用率
13.3 在岗统计与合规
13.4 导出与共享
14 运维与监控
14.1 指标与探针
14.2 健康检查与告警
14.3 日志与排障
14.4 资源与容量规划
15 最佳实践
15.1 机位布局建议
15.2 光线与遮挡处理
15.3 区域划分方法
15.4 误报与漏报治理
16 常见问题
16.1 视频卡顿
16.2 计数偏差
16.3 在岗识别不稳定
16.4 告警过多
17 合规与隐私
17.1 遮挡与脱敏
17.2 最小化采集原则
17.3 存储周期与删除
17.4 安全访问与隔离
18 变更与版本
18.1 版本命名规则
18.2 兼容性策略
18.3 功能变更说明
18.4 回滚与恢复
19 附录
19.1 指标名词表
19.2 接口字典
19.3 运维操作清单
19.4 示例配置

## 1 引言
### 1.1 编写目的
本操作说明用于指导部署与使用《智能楼宇AI感知物联系统 Buildingos.ai.visionCount》，覆盖安装、配置、使用、联动、运维与合规等完整生命周期。

### 1.2 名词定义
- 通道：摄像头的采集与转码通道
- 区域：在视频画面上定义的多边形区域
- 在岗：对人员处于岗位/区域状态的识别与统计
- 联动：感知结果触发的设备控制或通知

### 1.3 文档读者
- 运维人员、系统管理员、能源管理与节能策略编排人员

### 1.4 文档约定
- 所有示例参数仅用于说明，实际以现场配置为准

## 2 系统综述
### 2.1 设计目标
- 以边缘推理为核心，实现空间人数与在岗感知，为节能联动提供依据

### 2.2 典型应用场景
- 办公楼层、开放工位区、会议区、人行通道等场景的占用与在岗统计，联动照明与空调策略

### 2.3 架构与模块
- 摄像头接入、推理服务、任务编排、区域配置、联动规则、报表分析、运维监控与审计

### 2.4 部署拓扑与网络
- 推荐千兆/万兆交换机，PoE 供电，推理主机与边缘网关同网段，服务端与数据库专网访问

## 3 硬件与软件环境
### 3.1 摄像机选型与参数
- 1080p/4K、H.265、PoE、具备隐私遮挡与电子防抖，建议固定机位避免大幅移动

### 3.2 推理主机/GPU 配置建议
- x86 8核、32GB RAM、NVMe 1TB、NVIDIA GPU≥16GB 显存（RTX 系列或同级）

### 3.3 边缘设备与网络
- 边缘网关支持 MQTT/HTTP，稳定供电与 UPS 保障，心跳与断线重连机制

### 3.4 操作系统与中间件
- Ubuntu 22.04、Nginx、PostgreSQL 15、Redis 7、MQTT Broker、Docker、推理框架（ONNX/TensorRT/OpenVINO）

## 4 安装与部署
### 4.1 安装包与目录结构
- 二进制与容器部署；配置文件与日志目录分离，数据目录采用独立盘

### 4.2 服务启动与自检
- 启动后检查通道健康、模型加载、数据库连通与消息队列状态

### 4.3 首次初始化向导
- 创建组织/站点、楼层/区域、摄像头通道、默认模型与阈值、通知渠道

### 4.4 版本升级与备份
- 先备份数据库与对象存储；灰度升级与回滚预案

## 5 权限与安全
### 5.1 角色与权限矩阵
- 管理员、运维、策略编排、只读访客；最小权限原则

### 5.2 认证与单点登录
- 支持 OIDC/SSO，令牌有效期与刷新策略

### 5.3 审计日志与留痕
- 配置/任务/联动/告警/导出等关键操作审计

### 5.4 数据加密与隐私
- 传输层 TLS、存储脱敏与访问隔离

## 6 基础配置
### 6.1 组织与站点
- 按园区/楼宇划分站点，支持多站点管理

### 6.2 楼层与区域
- 支持自定义楼层、区域与布局映射

### 6.3 设备与资源
- 摄像头、推理主机、网关与联动设备统一纳管

### 6.4 通知与订阅
- 邮件/短信/企业IM 通知，阈值与抑制策略

## 7 摄像头接入
### 7.1 通道与流地址
- RTSP/GB28181 接入，支持鉴权与地址批量导入
![占位图](https://via.placeholder.com/1200x800?text=Camera+Channel)

### 7.2 拉流与转码策略
- 码率与分辨率匹配推理性能；关键帧间隔与延迟控制
![占位图](https://via.placeholder.com/1200x800?text=Streaming+Settings)

### 7.3 断流重连与心跳
- 指数退避重连与健康探针
![占位图](https://via.placeholder.com/1200x800?text=Heartbeat+Probe)

### 7.4 通道健康监测
- 丢帧率、延迟、错误率仪表盘
![占位图](https://via.placeholder.com/1200x800?text=Channel+Health)

## 8 模型管理
### 8.1 模型库与版本
- 人数计数/在岗分类模型版本化管理
![占位图](https://via.placeholder.com/1200x800?text=Model+Registry)

### 8.2 阈值与置信度
- 阈值对误报/漏报的影响与调参指南
![占位图](https://via.placeholder.com/1200x800?text=Thresholds)

### 8.3 输入预处理与后处理
- 去噪、缩放、ROI 裁剪；后处理过滤与聚合
![占位图](https://via.placeholder.com/1200x800?text=Pre%2FPost+Processing)

### 8.4 性能参数与并发
- Batch/并发/显存限制与负载均衡
![占位图](https://via.placeholder.com/1200x800?text=Performance+Tuning)

## 9 任务编排
### 9.1 计数任务
- 通道、区域、时间窗、阈值与输出配置
![占位图](https://via.placeholder.com/1200x800?text=Counting+Task)

### 9.2 在岗感知任务
- 目标区域定义与状态分类
![占位图](https://via.placeholder.com/1200x800?text=Presence+Task)

### 9.3 多摄融合任务
- 多机位合并与冲突消除策略
![占位图](https://via.placeholder.com/1200x800?text=Multi-Cam+Fusion)

### 9.4 计划与调度
- 定时/条件启动与暂停
![占位图](https://via.placeholder.com/1200x800?text=Scheduler)

## 10 区域配置
### 10.1 多边形区域编辑
- 顶点编辑/吸附/撤销与对齐
![占位图](https://via.placeholder.com/1200x800?text=Polygon+Editor)

### 10.2 楼层映射与坐标系
- 区域与楼层语义绑定
![占位图](https://via.placeholder.com/1200x800?text=Floor+Mapping)

### 10.3 人流方向与通行线
- 方向箭头与通行线配置
![占位图](https://via.placeholder.com/1200x800?text=Flow+Lines)

### 10.4 遮挡与误报抑制
- 遮挡区域与阈值动态调整
![占位图](https://via.placeholder.com/1200x800?text=Occlusion+Handling)

## 11 计算与缓存
### 11.1 实时计算通道
- 流水线与时序窗口
![占位图](https://via.placeholder.com/1200x800?text=Realtime+Pipeline)

### 11.2 边缘缓存策略
- 缓存大小与过期策略
![占位图](https://via.placeholder.com/1200x800?text=Edge+Cache)

### 11.3 断点续传与重试
- 失败队列与重试策略
![占位图](https://via.placeholder.com/1200x800?text=Retry+Mechanism)

### 11.4 数据落库与分层
- 时序与聚合表设计
![占位图](https://via.placeholder.com/1200x800?text=Data+Storage)

## 12 联动与告警
### 12.1 规则与条件
- 条件表达式与动作编排
![占位图](https://via.placeholder.com/1200x800?text=Rules)

### 12.2 阈值与时段
- 工作日/非工作日/假期时段
![占位图](https://via.placeholder.com/1200x800?text=Schedules)

### 12.3 设备联动（照明/空调）
- MQTT/HTTP 控制接口与防抖
![占位图](https://via.placeholder.com/1200x800?text=Device+Linkage)

### 12.4 告警路由与抑制
- 路由策略与合并抑制
![占位图](https://via.placeholder.com/1200x800?text=Alerting)

## 13 报表与分析
### 13.1 趋势与对比
- 周/月对比与峰谷分析
![占位图](https://via.placeholder.com/1200x800?text=Trends)

### 13.2 热力图与占用率
- 区域热力图与占用统计
![占位图](https://via.placeholder.com/1200x800?text=Heatmap)

### 13.3 在岗统计与合规
- 在岗时长与合规基线
![占位图](https://via.placeholder.com/1200x800?text=Presence+Stats)

### 13.4 导出与共享
- 导出 CSV/PNG/PDF 与共享链接
![占位图](https://via.placeholder.com/1200x800?text=Export)

## 14 运维与监控
### 14.1 指标与探针
- CPU/GPU/内存/显存/通道健康指标
![占位图](https://via.placeholder.com/1200x800?text=Metrics)

### 14.2 健康检查与告警
- 探针策略与通知
![占位图](https://via.placeholder.com/1200x800?text=Health+Check)

### 14.3 日志与排障
- 日志等级与定位方法
![占位图](https://via.placeholder.com/1200x800?text=Logs)

### 14.4 资源与容量规划
- 通道并发与存储规划
![占位图](https://via.placeholder.com/1200x800?text=Capacity+Planning)

## 15 最佳实践
### 15.1 机位布局建议
- 高度、角度、覆盖范围建议
![占位图](https://via.placeholder.com/1200x800?text=Layout)

### 15.2 光线与遮挡处理
- 逆光、强光、反射处理
![占位图](https://via.placeholder.com/1200x800?text=Lighting)

### 15.3 区域划分方法
- 基于功能/通行/工位划分
![占位图](https://via.placeholder.com/1200x800?text=Zoning)

### 15.4 误报与漏报治理
- 调参与规则优化
![占位图](https://via.placeholder.com/1200x800?text=Quality)

## 16 常见问题
### 16.1 视频卡顿
- 排查网络、码率与硬件瓶颈
![占位图](https://via.placeholder.com/1200x800?text=Lag)

### 16.2 计数偏差
- 阈值与区域优化
![占位图](https://via.placeholder.com/1200x800?text=Bias)

### 16.3 在岗识别不稳定
- 模型版本与参数调整
![占位图](https://via.placeholder.com/1200x800?text=Presence+Issues)

### 16.4 告警过多
- 抑制与去重策略
![占位图](https://via.placeholder.com/1200x800?text=Alert+Storm)

## 17 合规与隐私
### 17.1 遮挡与脱敏
- 遮挡区域与像素化处理
![占位图](https://via.placeholder.com/1200x800?text=Privacy)

### 17.2 最小化采集原则
- 仅采集必要数据与最短存储周期
![占位图](https://via.placeholder.com/1200x800?text=Minimization)

### 17.3 存储周期与删除
- 生命周期管理与自动清理
![占位图](https://via.placeholder.com/1200x800?text=Retention)

### 17.4 安全访问与隔离
- 角色隔离与网络隔离
![占位图](https://via.placeholder.com/1200x800?text=Isolation)

## 18 变更与版本
### 18.1 版本命名规则
- 语义化版本与变更日志
![占位图](https://via.placeholder.com/1200x800?text=Versioning)

### 18.2 兼容性策略
- 接口与模型兼容矩阵
![占位图](https://via.placeholder.com/1200x800?text=Compatibility)

### 18.3 功能变更说明
- 主要功能变更记录
![占位图](https://via.placeholder.com/1200x800?text=Changelog)

### 18.4 回滚与恢复
- 回滚策略与备份恢复
![占位图](https://via.placeholder.com/1200x800?text=Rollback)

## 19 附录
### 19.1 指标名词表
- 指标与定义索引
![占位图](https://via.placeholder.com/1200x800?text=Glossary)

### 19.2 接口字典
- 设备/联动/报表接口说明
![占位图](https://via.placeholder.com/1200x800?text=API+Reference)

### 19.3 运维操作清单
- 例行检查与巡检清单
![占位图](https://via.placeholder.com/1200x800?text=Ops+Checklist)

### 19.4 示例配置
- 示例参数与样例
![占位图](https://via.placeholder.com/1200x800?text=Samples)

