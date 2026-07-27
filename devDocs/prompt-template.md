# 软著文档生成提示词模板

> 使用方法：复制下方提示词，将 `{...}` 占位符替换为实际值后，直接粘贴给 Claude Code。

---

## 步骤一：填充产品参数

在下方表格中填入新产品的信息：

| 参数 | 示例值（工位系统） | 你的产品 |
|------|-------------------|----------|
| 系统全称 | 智能工位管理系统 | |
| 系统简称 | buildingos.workstation | |
| 目录名 | workstation | |
| 开发完成日期 | 2025年09月30日 | |
| 发表时间 | 2025年10月31日 | |
| 源程序量 | 约3200行 | |
| 开发目的 (≤50字) | 实现固定与共享工位的统一分配、预定与可视化监控，提升空间利用率。 | |
| 面向领域 (≤50字) | 智慧楼宇、园区工位资源管理行业。 | |
| 主要功能 (≤200字) | 本软件以三维室内地图为载体，提供工位资源全生命周期管理功能… | |
| 技术特点 (≤100字) | 采用Vue3+NestJS+TypeScript微服务架构；集成AirocovMap三维室内地图引擎… | |
| 后端源码路径 | C:\project\buildingos\apps\workstation\src\ | |
| 前端源码路径 | C:\project\buildingos_web\src\views\workstation\ | |
| 后端端口 | 3024 | |
| 功能模块列表 | 工位大屏可视化、共享工位预定、固定工位管理、地图管理、工位统计分析 | |
| 核心术语(2-4个) | 固定工位/共享工位/工位预定/空间利用率 | |
| 运行硬件环境 | 服务端x86 8核/边缘网关/工位传感器/客户端PC | |

---

## 步骤二：粘贴提示词

填完上方参数后，将下面的提示词连同参数一起发给 Claude Code：

```
## 任务：为 {系统全称}（{系统简称}）生成软著申请文档

请按照以下规范，在 `docs/{目录名}/` 下生成三个文件。

### 参考标准

- 版权信息模板：`ref/requirment.md`
- 操作手册模板：`ref/manual.md`
- 已成功申请的 5 个范例：`docs/visitor/`、`docs/access/`、`docs/reservation/`、`docs/meetingroom/`、`docs/toilet/`
- 已完成的工作站范例：`docs/workstation/`

### 源码路径

- 后端源码：`{后端源码路径}`
- 前端源码：`{前端源码路径}`

---

### 文件一：copyright.md

格式严格参照 `docs/visitor/copyright.md`。字段值如下：

- 软件全称：{系统全称}
- 软件简称：{系统简称}
- 版本号：V1.0
- 软件作品说明：原创
- 开发完成日期：{开发完成日期}
- 发表情况：已发表
- 发表时间：{发表时间}
- 发表城市：成都
- 开发方式：独立开发
- 著作权人：成都极企科技有限公司 / 企业法人 / 营业执照
- 软件开发硬件环境：PC机 Intel Core i7，RAM≥16GB，硬盘≥512GB
- 软件运行硬件环境：{运行硬件环境，需具体列出每类设备的CPU/内存/存储规格}
- 开发操作系统：Windows 11 / macOS 14
- 开发工具：Node.js 20.x、Vite、Vue 3、TypeScript 5.x、NestJS 10.x、pnpm/npm
- 运行平台：Linux（Ubuntu 22.04）
- 支撑软件：Nginx、PostgreSQL 15、Redis 7、MQTT Broker（EMQX/Mosquitto）、Docker
- 编程语言：TypeScript 5.x
- 源程序量：{源程序量}
- 开发目的：{开发目的}
- 面向领域/行业：{面向领域}
- 软件主要功能：{主要功能}
- 软件主要技术特点分类：人工智能软件 物联网软件 智慧城市软件
- 技术特点详细说明：{技术特点}

---

### 文件二：manual.md

格式严格参照 `docs/visitor/manual.md`。

结构要求：
1. 引言（1.1 编写目的、1.2 定义）
2. 系统概述（2.1 系统用途、2.2 软件功能概述、2.3 软件运行环境）
3. 系统操作使用（3.1 登录与首页 → 3.2~3.N 各功能模块，至少 10 个子节）

内容要求：
- 每个功能模块包含：功能说明 + 操作步骤 + 界面展示
- 界面展示使用占位格式：`![description](image-N.png)` 后跟 `*图 X-Y 界面描述*`
- 每个子节都需要配图占位，不少于 10 张
- 功能模块的划分基于系统实际功能，如：
  {功能模块列表}

核心术语定义：
{核心术语}

系统用途描述应包含：
- 系统定位（专为智慧楼宇设计的…）
- 核心能力（取代传统方式，通过…实现…）
- 核心价值（提升…降低…保障…）

---

### 文件三：source.md

格式严格参照 `docs/visitor/source.md`。

关键规则：
1. 只有两个代码块：`## 前30页` 和 `## 后30页`，不要添加 `## 第N页` 之类的页码标记
2. 每个代码块内的代码是连续的，将多个源码文件合并放入
3. 前30页放后端代码，后30页放前端代码
4. 代码中不得包含公司名称、个人名称、文件名称（替换为通用占位符）
5. 目标：每部分尽量达到 1500 行以上

需要读取并纳入的源码文件范围：
- 后端：所有 .ts 实体、DTO、守卫、装饰器、控制器、服务、模块配置，以及 menu.json
- 前端：所有 .vue 页面组件和对话框组件

---

### 文件四：更新配置

- 在 `docs/.vitepress/config.ts` 的 sidebar 中取消注释（或新增）该系统对应的条目
- 在 `docs/index.md` 中取消注释（或新增）该系统对应的导航链接
```

---

## 附录：已有的5个成功范例对照

| 系统 | 目录 | 特点 |
|------|------|------|
| 智能楼宇访客系统 | visitor | 功能模块最多（5模块16子节），适合复杂系统参考 |
| 智能楼宇通行系统 | access | 门禁设备联动，适合硬件集成类系统 |
| 智能楼宇空间预约系统 | reservation | 预约/审批流程，适合预定类系统 |
| 智能楼宇会议室系统 | meetingroom | 会议室+平板联动，适合资源管理类 |
| 智能楼宇智能卫生间系统 | toilet | IoT传感器联动，适合物联网类系统 |
| 智能工位管理系统 | workstation | 三维地图+传感器，适合空间可视化类（最新范例） |


--- workstation

 现在按照对齐的标准，生成第一个新的软件产品：buildingos.workstation 智能工位管理系统。参考描述为：C:\project\building
  os_web\devDocs\ZP\工位管理.md，代码参考在：前端：C:\project\buildingos_web\src\views\workstation，后端：C:\project\b
  uildingos\apps\workstation。注意：1，开发时按照微服务开发，但是申请文档要按照独立的系统来描述。2：输出在C:\project\b
  uildingos.software\docs下的workstation，里面按照规范生产copyright.md manual.md source.md。字数不能少于要求。

 其中source按照C:\project\buildingos.software\docs\visitor\source.md来改写，分前30页，和后30页。代码可以多个文件合并
  ，没40页至少4000行的量



  生成的新产品：workstation按照最终交付物参考：C:\project\buildingos.software\devDocs\2026年极企软著申请材料（计划15
  个）\2026年极企软著申请材料（计划15个）\极企5个软著源代码及使用手册（已申请）\①软著：智能楼宇访客系统\三个docx文件。
  要按照一样的格式要求来将生成的md文件来转写到：C:\project\buildingos.software\devDocs\2026年极企软著申请材料（计划15
  个）\2026年极企软著申请材料（计划15个）\计划软著申请材料（10个）未申请\7月软著申请材料（6个）\智能工位系统。md生成docx用C:\project\buildingos.software\devDocs\convert_to_docx.py


  ---- parking
  智能楼宇智能停车管理系统  

   现在按照对齐的标准，生成第一个新的软件产品：buildingos.parking 智能楼宇智能停车管理系统。参考描述为：C:\project\building
  os_web\devDocs\ZP\停车管理.md，代码参考在：前端：C:\project\buildingos_web\src\views\parking，后端：C:\project\b
  uildingos\apps\parking。注意：1，开发时按照微服务开发，但是申请文档要按照独立的系统来描述。2：输出在C:\project\b
  uildingos.software\docs下的parking，里面按照规范生产copyright.md manual.md source.md。字数不能少于要求。  

 其中source按照C:\project\buildingos.software\docs\visitor\source.md来改写，分前30页，和后30页。代码可以多个文件合并
  ，没40页至少4000行的量



  生成的新产品：parking按照最终交付物参考：C:\project\buildingos.software\devDocs\2026年极企软著申请材料（计划15
  个）\2026年极企软著申请材料（计划15个）\极企5个软著源代码及使用手册（已申请）\①软著：智能楼宇停车系统\三个docx文件。
  要按照一样的格式要求来将生成的md文件来转写到：C:\project\buildingos.software\devDocs\2026年极企软著申请材料（计划15
  个）\2026年极企软著申请材料（计划15个）\计划软著申请材料（10个）未申请\7月软著申请材料（6个）\智能停车系统。md生成docx用C:\project\buildingos.software\devDocs\convert_to_docx.py

  ---- maintenance

  智能楼宇智能维护管理系统  

   现在按照对齐的标准，生成第一个新的软件产品：buildingos.maintenance 智能楼宇智能维护管理系统。参考描述为：C:\project\building
  os_web\devDocs\ZP\工单管理.md，代码参考在：前端：C:\project\buildingos_web\src\views\workorder，后端：C:\project\buildingos\apps\maintance
  注意：1，开发时按照微服务开发，但是申请文档要按照独立的系统来描述。2：输出在C:\project\b
  uildingos.software\docs下的maintenance，里面按照规范生产copyright.md manual.md source.md。字数不能少于要求。  

 其中source按照C:\project\buildingos.software\docs\visitor\source.md来改写，分前30页，和后30页。代码可以多个文件合并
  ，没40页至少4000行的量



  生成的新产品：maintenance按照最终交付物参考：C:\project\buildingos.software\devDocs\2026年极企软著申请材料（计划15
  个）\2026年极企软著申请材料（计划15个）\极企5个软著源代码及使用手册（已申请）\①软著：智能楼宇维护系统\三个docx文件。
  要按照一样的格式要求来将生成的md文件来转写到：C:\project\buildingos.software\devDocs\2026年极企软著申请材料（计划15
  个）\2026年极企软著申请材料（计划15个）\计划软著申请材料（10个）未申请\7月软著申请材料（6个）\智能维护系统。md生成docx用C:\project\buildingos.software\devDocs\convert_to_docx.py


  

  ---- green

  智能楼宇智能维护管理系统  

   现在按照对齐的标准，生成第一个新的软件产品：buildingos.green 智能楼宇智能绿色能源管理系统。参考描述为：C:\project\buildingos_web\devDocs\energyModule.md，代码参考在：前端：C:\project\buildingos_web\src\views\sence\energy，后端：C:\project\buildingos\apps\energy
  注意：1，开发时按照微服务开发，但是申请文档要按照独立的系统来描述。2：输出在C:\project\b
  uildingos.software\docs下的green，里面按照规范生产copyright.md manual.md source.md。字数不能少于要求。  

 其中source按照C:\project\buildingos.software\docs\visitor\source.md来改写，分前30页，和后30页。代码可以多个文件合并
  ，没40页至少4000行的量



  生成的新产品：maintenance按照最终交付物参考：C:\project\buildingos.software\devDocs\2026年极企软著申请材料（计划15
  个）\2026年极企软著申请材料（计划15个）\极企5个软著源代码及使用手册（已申请）\①软著：智能楼宇绿色能源系统\三个docx文件。
  要按照一样的格式要求来将生成的md文件来转写到：C:\project\buildingos.software\devDocs\2026年极企软著申请材料（计划15
  个）\2026年极企软著申请材料（计划15个）\计划软著申请材料（10个）未申请\7月软著申请材料（6个）\智能绿色能源系统。md生成docx用C:\project\buildingos.software\devDocs\convert_to_docx.py

  ---- security
  智能楼宇智慧安防管理系统  

   现在按照对齐的标准，生成第一个新的软件产品：buildingos.security 智能楼宇智慧安防管理系统。参考描述为：C:\project\buildingos_web\devDocs\ZP\安防管理.md，代码参考在：前端：C:\project\buildingos_web\src\views\sence\security，后端：C:\project\buildingos\apps\security
  注意：1，开发时按照微服务开发，但是申请文档要按照独立的系统来描述。2：输出在C:\project\buildingos.software\docs下的security，里面按照规范生产copyright.md manual.md source.md。字数不能少于要求。  

 其中source按照C:\project\buildingos.software\docs\visitor\source.md来改写，分前30页，和后30页。代码可以多个文件合并
  ，没40页至少4000行的量



  生成的新产品：security按照最终交付物参考：C:\project\buildingos.software\devDocs\2026年极企软著申请材料（计划15
  个）\2026年极企软著申请材料（计划15个）\极企5个软著源代码及使用手册（已申请）\①软著：智能楼宇安防系统\三个docx文件。
  要按照一样的格式要求来将生成的md文件来转写到：C:\project\buildingos.software\devDocs\2026年极企软著申请材料（计划15
  个）\2026年极企软著申请材料（计划15个）\计划软著申请材料（10个）未申请\7月软著申请材料（6个）\智能绿色能源系统。md生成docx用C:\project\buildingos.software\devDocs\convert_to_docx.py





  ---- ioc
  智能楼宇智慧运营系统  
其中
   现在按照对齐的标准，生成第一个新的软件产品：buildingos.ioc 智能楼宇智慧运营系统。参考描述为：C:\project\buildingos_web\devDocs\ioc.md，代码参考在：前端：C:\project\buildingos_web\src\views\sence\ioc，后端：无
  注意：1，开发时按照微服务开发，但是申请文档要按照独立的系统来描述。2：输出在C:\project\buildingos.software\docs下的ioc，里面按照规范生产copyright.md manual.md source.md。字数不能少于要求。  

 其中source按照C:\project\buildingos.software\docs\visitor\source.md来改写，分前30页，和后30页。代码可以多个文件合并
  ，没40页至少4000行的量



  生成的新产品：ioc按照最终交付物参考：C:\project\buildingos.software\devDocs\2026年极企软著申请材料（计划15
  个）\2026年极企软著申请材料（计划15个）\极企5个软著源代码及使用手册（已申请）\①软著：智能楼宇运营系统\三个docx文件。
  要按照一样的格式要求来将生成的md文件来转写到：C:\project\buildingos.software\devDocs\2026年极企软著申请材料（计划15
  个）\2026年极企软著申请材料（计划15个）\计划软著申请材料（10个）未申请\7月软著申请材料（6个）\智能绿色能源系统。md生成docx用C:\project\buildingos.software\devDocs\convert_to_docx.py
