# 源代码提交页（智能楼宇物联网边缘网关系统 buildingos.edge）

## 提交要求
- 提供源程序的连续前30页与连续后30页；不足60页需提供全部源代码
- 每页不少于50行
- 源代码中不得包含公司名称、个人名称、文件名称
- 源代码总数量需与申请表保持一致

## 前30页
以下为前30页的连续源代码片段（边缘平台后端服务）。

```
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.setGlobalPrefix('api');
  app.enableCors();
  app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));
  await app.listen(process.env.PORT ?? 7829);
}
bootstrap();

import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { AuthModule } from './auth/auth.module';
import { MonitorModule } from './monitor/monitor.module';
import { MqttModule } from './mqtt/mqtt.module';
import { StreamingModule } from './streaming/streaming.module';
import { DevicesModule } from './devices/devices.module';
import { PlatformModule } from './platform/platform.module';
import { DatabaseModule } from './database/database.module';

@Module({
  imports: [AuthModule, MonitorModule, MqttModule, StreamingModule, DevicesModule, PlatformModule, DatabaseModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}

import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';

@Injectable()
export class AuthService {
  constructor(private jwtService: JwtService) {}

  async login(username: string, pass: string) {
    if (username === 'admin' && pass === 'admin123') {
      const payload = { username: 'admin', sub: '1' };
      return {
        access_token: this.jwtService.sign(payload),
      };
    }
    throw new UnauthorizedException();
  }
}

import { ExtractJwt, Strategy } from 'passport-jwt';
import { PassportStrategy } from '@nestjs/passport';
import { Injectable } from '@nestjs/common';
import { jwtConstants } from './constants';

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor() {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: jwtConstants.secret,
    });
  }

  async validate(payload: any) {
    return { userId: payload.sub, username: payload.username };
  }
}

import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import * as si from 'systeminformation';
import Docker from 'dockerode';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

function detectHostIp(): string {
  // 1. Explicit env var override
  if (process.env.EDGE_HOST_IP) return process.env.EDGE_HOST_IP;

  // 2. Auto-detect from network interfaces (first non-internal IPv4)
  const ifaces = os.networkInterfaces();
  for (const name of Object.keys(ifaces)) {
    if (!ifaces[name]) continue;
    for (const iface of ifaces[name]) {
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return '127.0.0.1';
}

function defaultConfig(): Record<string, any> {
  return {
    hostIp: detectHostIp(),
    spaceCode: '',
    isIntegrated: false,
    hqConnected: false,
    deviceCount: 0,
    platformUrl: '',
    platformToken: '',
    connectionStatus: 'UNCONFIGURED',
    platform: null,
    platformHistory: [],
  };
}

@Injectable()
export class MonitorService implements OnModuleInit {
  private readonly logger = new Logger(MonitorService.name);
  private docker: Docker;
  private readonly configPath = path.join(process.cwd(), 'config', 'config.json');
  private readonly composeProjectName = 'buildingos-edge';

  constructor() {
    this.docker = new Docker({ socketPath: '/var/run/docker.sock' });
  }

  async onModuleInit() {
    // Auto-create config.json on first deploy — no manual steps needed.
    // If config.json is a directory (Docker bind-mount artifact when host file
    // doesn't exist), log a clear error — the deploy script must fix this on the host.
    try {
      if (!fs.existsSync(this.configPath)) {
        const cfg = defaultConfig();
        fs.writeFileSync(this.configPath, JSON.stringify(cfg, null, 2), 'utf8');
        this.logger.log(`config.json auto-created with hostIp=${cfg.hostIp}`);
      } else if (!fs.statSync(this.configPath).isFile()) {
        this.logger.error(
          `config.json is a directory, not a file. ` +
          `Docker likely created it because the host file doesn't exist. ` +
          `Run: docker compose stop backend && rm -rf config.json && touch config.json && docker compose up -d backend`,
        );
      }
    } catch (e) {
      this.logger.warn('Could not auto-create config.json, will fall back to in-memory defaults', e);
    }
  }

  async getEdgeConfig() {
    try {
      if (fs.existsSync(this.configPath) && fs.statSync(this.configPath).isFile()) {
        const configStr = fs.readFileSync(this.configPath, 'utf8');
        const config = JSON.parse(configStr);
        // Auto-correct hostIp if it's a legacy dev placeholder
        if (!config.hostIp || config.hostIp === '192.168.1.100' || config.hostIp === '127.0.0.1') {
          config.hostIp = detectHostIp();
        }
        return config;
      }
      return defaultConfig();
    } catch (e) {
      this.logger.error('Failed to read edge config', e);
      return null;
    }
  }

  async updateEdgeConfig(config: any) {
    const currentConfig = await this.getEdgeConfig() || {};
    const newConfig = { ...currentConfig, ...config };
    try {
      if (fs.statSync(this.configPath).isFile()) {
        fs.writeFileSync(this.configPath, JSON.stringify(newConfig, null, 2), 'utf8');
      } else {
        this.logger.error(
          `Cannot write config: ${this.configPath} is not a regular file. ` +
          `Fix on host with: rm -rf config.json && touch config.json`,
        );
      }
    } catch (e) {
      this.logger.error('Failed to update edge config', e);
      throw e;
    }
    return newConfig;
  }

  async getSystemStats() {
    try {
      const cpu = await si.currentLoad();
      const mem = await si.mem();
      const disk = await si.fsSize();
      const time = si.time();

      return {
        cpu: {
          load: cpu.currentLoad,
        },
        memory: {
          percentage: (mem.active / mem.total) * 100,
          used: mem.active,
          total: mem.total,
        },
        disk: {
          percentage: disk[0] ? disk[0].use : 0,
          used: disk[0] ? disk[0].used : 0,
          total: disk[0] ? disk[0].size : 0,
        },
        uptime: time.uptime,
      };
    } catch (e) {
      this.logger.error('Failed to get system stats', e);
      return {
        cpu: { load: 0 },
        memory: { percentage: 0, used: 0, total: 0 },
        disk: { percentage: 0, used: 0, total: 0 },
        uptime: 0,
      };
    }
  }

  async getContainers() {
    try {
      const allContainers = await this.docker.listContainers({ all: true });
      const containers = allContainers.filter((container) => {
        const projectName = container.Labels?.['com.docker.compose.project'];
        return projectName?.toLowerCase() === this.composeProjectName;
      });
      const statsPromises = containers.map((c) => this.docker.getContainer(c.Id).stats({ stream: false }));
      const allStats = await Promise.all(statsPromises);

      const mappedContainers = containers.map((c, index) => {
        const stats = allStats[index];
        const sortedPorts = [...c.Ports].sort((a, b) => {
          const aPort = a.PublicPort ?? a.PrivatePort ?? Number.MAX_SAFE_INTEGER;
          const bPort = b.PublicPort ?? b.PrivatePort ?? Number.MAX_SAFE_INTEGER;
          return aPort - bPort;
        });
        
        // Calculate CPU usage percentage
        let cpuPercent = 0;
        if (stats.cpu_stats && stats.precpu_stats) {
          const cpuDelta = stats.cpu_stats.cpu_usage.total_usage - stats.precpu_stats.cpu_usage.total_usage;
          const systemDelta = stats.cpu_stats.system_cpu_usage - stats.precpu_stats.system_cpu_usage;
          const onlineCpus = stats.cpu_stats.online_cpus || stats.cpu_stats.cpu_usage.percpu_usage?.length || 1;
          if (systemDelta > 0 && cpuDelta > 0) {
            cpuPercent = (cpuDelta / systemDelta) * onlineCpus * 100;
          }
        }

        // Calculate Memory usage
        const memUsed = stats.memory_stats.usage || 0;
        const memLimit = stats.memory_stats.limit || 0;
        const memPercent = memLimit > 0 ? (memUsed / memLimit) * 100 : 0;

        // Disk I/O (Placeholder as it's complex to aggregate from blkio_stats)
        const diskRead = stats.blkio_stats?.io_service_bytes_recursive?.find(i => i.op === 'Read')?.value || 0;
        const diskWrite = stats.blkio_stats?.io_service_bytes_recursive?.find(i => i.op === 'Write')?.value || 0;

        // Network I/O
        let netIn = 0;
        let netOut = 0;
        if (stats.networks) {
          Object.values(stats.networks).forEach((net: any) => {
            netIn += net.rx_bytes;
            netOut += net.tx_bytes;
          });
        }

        return {
          id: c.Id.substring(0, 12),
          name: c.Names[0].replace('/', ''),
          image: c.Image,
          status: c.State,
          state: c.Status,
          ports: sortedPorts
            .map((p) => {
              if (p.PublicPort && p.PrivatePort) {
                return `${p.PublicPort}:${p.PrivatePort}`;
              }
              if (p.PrivatePort) {
                return `${p.PrivatePort}`;
              }
              return '--';
            })
            .join(', '),
          sortPort: sortedPorts[0]?.PublicPort ?? sortedPorts[0]?.PrivatePort ?? Number.MAX_SAFE_INTEGER,
          version: c.Labels['org.opencontainers.image.version'] || 'latest',
          metrics: {
            cpu: cpuPercent,
            memUsed,
            memLimit,
            memPercent,
            diskRead,
            diskWrite,
            netIn,
            netOut,
            pids: stats.pids_stats?.current || 0,
          }
        };
      });
      return mappedContainers.sort((a, b) => a.sortPort - b.sortPort || a.name.localeCompare(b.name));
    } catch (e) {
      this.logger.error('Failed to get containers', e);
      return [];
    }
  }

  async restartContainer(containerId: string) {
    try {
      const container = this.docker.getContainer(containerId);
      await container.restart();
      return { success: true };
    } catch (e) {
      this.logger.error(`Failed to restart container ${containerId}`, e);
      throw e;
    }
  }

  async getContainerLogs(containerId: string) {
    try {
      const container = this.docker.getContainer(containerId);
      const logs = await container.logs({
        stdout: true,
        stderr: true,
        tail: 100,
        follow: false,
      });
      return logs.toString('utf8');
    } catch (e) {
      this.logger.error(`Failed to get logs for container ${containerId}`, e);
      return 'Failed to fetch logs';
    }
  }

  async getServiceStatus() {
    const containers = await this.getContainers();
    const services = ['emqx', 'tdengine', 'zlmediakit', 'nodered'];
    const result = {};

    services.forEach((s) => {
      const container = containers.find((c) => c.name.includes(s));
      result[s] = container ? container.status : 'stopped';
    });

    return result;
  }

  async getZlmStreams() {
    return [];
  }

  /**
   * Return a Map of container IP → friendly name for MQTT client source identification.
   * Cached for the request lifetime to avoid hammering Docker API.
   */
  async getContainerNetworkMap(): Promise<Map<string, { name: string; role: string }>> {
    const map = new Map<string, { name: string; role: string }>();
    try {
      const containers = await this.docker.listContainers({ all: false });
      for (const c of containers) {
        const projectName = c.Labels?.['com.docker.compose.project'];
        if (projectName?.toLowerCase() !== this.composeProjectName) continue;

        const containerName = (c.Names[0] || '').replace(/^\//, '');
        const inspect = await this.docker.getContainer(c.Id).inspect();
        const networks = inspect.NetworkSettings?.Networks || {};

        for (const ip of Object.values(networks).map((n: any) => n.IPAddress).filter(Boolean)) {
          map.set(ip as string, {
            name: containerName,
            role: this.getContainerRole(containerName),
          });
        }
      }
    } catch (e) {
      this.logger.error('Failed to build container network map', e);
    }
    return map;
  }

  private getContainerRole(name: string): string {
    if (name.includes('nodered-lighting')) return 'Node-RED (照明/空调)';
    if (name.includes('nodered-sensor')) return 'Node-RED (传感器)';
    if (name.includes('nodered-integration')) return 'Node-RED (系统集成)';
    if (name.includes('backend')) return 'Edge Backend';
    if (name.includes('emqx')) return 'EMQX Broker';
    if (name.includes('tdengine')) return 'TDengine';
    if (name.includes('zlmediakit')) return 'ZLMediaKit';
    if (name.includes('postgres')) return 'PostgreSQL';
    if (name.includes('frontend')) return 'Nginx Frontend';
    return name;
  }
}

import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import axios from 'axios';
import * as mqtt from 'mqtt';
import { MonitorService } from '../monitor/monitor.service';

@Injectable()
export class MqttService implements OnModuleInit {
  private readonly logger = new Logger(MqttService.name);

  constructor(private readonly monitorService: MonitorService) {}

  // ── 桥接实时日志（连接事件 + 收发消息 + 计数） ───────────────────────────────

  private bridgeLogState = new Map<
    string,
    {
      server: string;
      status: string;
      statusReason: string;
      counters: { received: number; success: number; failed: number; dropped: number; matched: number; rate: number } | null;
      events: { ts: number; status: string; reason: string }[];
      messages: { ts: number; direction: 'in' | 'out'; topic: string; payload: string }[];
      missingSince: number;
    }
  >();
  private bridgeMsgSubs = new Map<string, mqtt.MqttClient>();
  private bridgeMsgTopics = new Map<string, string>();
  private lastCounters = new Map<string, string>();
  private bridgeLogListeners = new Set<(snapshot: any) => void>();
  private bridgeLogTimer: ReturnType<typeof setInterval> | null = null;
  private emqxTokenCache: { token: string; at: number } | null = null;

  private getEmqxApiUrl(): string {
    return process.env.EMQX_API_URL || 'http://emqx:18083';
  }

  private async getEmqxToken(): Promise<string> {
    // 高频轮询共用同一 token，避免每秒重新登录挤占 EMQX Dashboard API
    const cached = this.emqxTokenCache;
    if (cached && Date.now() - cached.at < 5 * 60 * 1000) return cached.token;

    const apiUrl = this.getEmqxApiUrl();
    const password = process.env.EMQX_ADMIN_PASSWORD || 'admin123';
    try {
      const res = await axios.post(
        `${apiUrl}/api/v5/login`,
        { username: 'admin', password },
        { timeout: 5000 },
      );
      this.emqxTokenCache = { token: res.data.token, at: Date.now() };
      return res.data.token;
    } catch (err: any) {
      this.logger.error(`EMQX login failed: ${err.message}`);
      throw err;
    }
  }

  /** Bootstrap EMQX authentication and create internal service users on startup. */
  async onModuleInit() {
    const backendUser = process.env.MQTT_BACKEND_USER || 'buildingos';
    const backendPass = process.env.MQTT_BACKEND_PASS || 'buildingos_edge_2024';

    // Wait for EMQX to be ready
    const apiUrl = this.getEmqxApiUrl();
    this.logger.log(`Waiting for EMQX API at ${apiUrl} ...`);
    for (let i = 0; i < 60; i++) {
      try {
        await axios.get(`${apiUrl}/api/v5/status`, { timeout: 3000 });
        this.logger.log('EMQX API is ready');
        break;
      } catch {
        if (i === 59) {
          this.logger.warn('EMQX API not ready after 120s, skipping bootstrap');
          return;
        }
        await new Promise((r) => setTimeout(r, 2000));
      }
    }

    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };

      // Check / configure authentication
      const authRes = await axios.get(`${apiUrl}/api/v5/authentication`, { headers, timeout: 5000 });
      const authCount = authRes.data?.count ?? 0;

      let authId: string;
      if (authCount > 0) {
        authId = authRes.data.authenticators?.[0]?.id;
        this.logger.log(`EMQX authentication already configured (id=${authId})`);
      } else {
        const createRes = await axios.post(`${apiUrl}/api/v5/authentication`,
          { mechanism: 'password_based', backend: 'built_in_database', user_id_type: 'username', enable: true },
          { headers, timeout: 5000 },
        );
        authId = createRes.data.id;
        this.logger.log(`Created EMQX built_in_database authentication (id=${authId})`);
      }

      if (authId) {
        // Create internal service user (idempotent)
        try {
          await axios.get(`${apiUrl}/api/v5/authentication/${authId}/users/${backendUser}`, { headers, timeout: 5000 });
          this.logger.log(`EMQX user '${backendUser}' already exists`);
        } catch {
          await axios.post(`${apiUrl}/api/v5/authentication/${authId}/users`,
            { user_id: backendUser, password: backendPass, is_superuser: false },
            { headers, timeout: 5000 },
          );
          this.logger.log(`Created EMQX user '${backendUser}' for internal services`);
        }
      }
    } catch (err: any) {
      this.logger.warn(`EMQX bootstrap failed (non-fatal): ${err.message}`);
    }

    // 桥接实时日志轮询器：独立于认证 bootstrap，EMQX 未就绪时静默重试
    // 1 秒轮询以捕捉桥接被整桥删除重建的短暂间隙（重建流程间隙约 2.5 秒）
    this.pollBridgeLogs().catch(() => {});
    this.bridgeLogTimer = setInterval(() => this.pollBridgeLogs().catch(() => {}), 1000);
  }

  async getStats() {
    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      const apiUrl = this.getEmqxApiUrl();

      const [metricsRes, nodesRes, bridgesRes] = await Promise.all([
        axios.get(`${apiUrl}/api/v5/metrics`, { headers, timeout: 5000 }).catch(() => ({ data: {} })),
        axios.get(`${apiUrl}/api/v5/nodes`, { headers, timeout: 5000 }).catch(() => ({ data: [] })),
        axios.get(`${apiUrl}/api/v5/bridges`, { headers, timeout: 5000 }).catch(() => ({ data: [] })),
      ]);

      const metrics = metricsRes.data;
      const nodes = Array.isArray(nodesRes.data) ? nodesRes.data : [];
      const bridges = Array.isArray(bridgesRes.data) ? bridgesRes.data : [];

      return {
        inflowRate: metrics['messages.received.rate'] ?? 0,
        outflowRate: metrics['messages.sent.rate'] ?? 0,
        totalConnections: nodes.reduce((sum: number, n: any) => sum + (n.connections ?? 0), 0),
        nodeCount: nodes.length,
        bridges: bridges.filter((b: any) => b.enable).length,
      };
    } catch (err: any) {
      this.logger.error(`getStats failed: ${err.message}`);
      return { inflowRate: 0, outflowRate: 0, totalConnections: 0, nodeCount: 0, bridges: 0 };
    }
  }

  async getTopics() {
    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      const apiUrl = this.getEmqxApiUrl();

      const subsRes = await axios.get(`${apiUrl}/api/v5/subscriptions`, { headers, timeout: 5000 });
      const subs: any[] = subsRes.data?.data ?? (Array.isArray(subsRes.data) ? subsRes.data : []);

      // Group by topic: collect client details
      const topicMap = new Map<string, { clientid: string; username: string }[]>();
      for (const s of subs) {
        const t = s.topic;
        if (!topicMap.has(t)) topicMap.set(t, []);
        topicMap.get(t)!.push({ clientid: s.clientid, username: s.username || '' });
      }
      return Array.from(topicMap.entries()).map(([topic, consumers]) => ({
        topic,
        subscribers: consumers.length,
        consumers,
      }));
    } catch (err: any) {
      this.logger.error(`getTopics failed: ${err.message}`);
      return [];
    }
  }

  /** 拉取 EMQX 规则，解析「bridge_id -> 源主题」映射 */
  private async getEmqxRulesWithMapping(): Promise<Map<string, string>> {
    const map = new Map<string, string>();
    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      const apiUrl = this.getEmqxApiUrl();
      const res = await axios.get(`${apiUrl}/api/v5/rules?limit=1000`, { headers, timeout: 5000 });
      for (const r of res.data?.data || []) {
        const m = (r.sql || '').match(/FROM\s+"([^"]+)"/);
        if (!m) continue;
        for (const a of r.actions || []) {
          const target = typeof a === 'string' ? a : a?.args?.bridge_id || a?.type;
          if (target) {
            map.set(target, m[1]);
          }
        }
      }
    } catch (err: any) {
      this.logger.warn(`getEmqxRulesWithMapping failed: ${err.message}`);
    }
    return map;
  }

  async getForwardingRules() {
    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      const apiUrl = this.getEmqxApiUrl();

      const res = await axios.get(`${apiUrl}/api/v5/rules?limit=1000`, { headers, timeout: 5000 });
      return (res.data?.data || []).map((r: any) => ({
        name: r.name,
        enable: r.enable,
        sql: r.sql,
        targets: (r.actions || []).map((a: any) =>
          typeof a === 'string' ? a : a?.args?.bridge_id || a?.type,
        ),
      }));
    } catch (err: any) {
      this.logger.error(`getForwardingRules failed: ${err.message}`);
      return [];
    }
  }

  /** 获取桥接详细状态，含流量指标 */
  async getBridgeDetails() {
    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      const apiUrl = this.getEmqxApiUrl();

      const bridgesRes = await axios.get(`${apiUrl}/api/v5/bridges`, { headers, timeout: 5000 });
      const bridges = Array.isArray(bridgesRes.data) ? bridgesRes.data : [];

      const ruleTopics = await this.getEmqxRulesWithMapping();

      const details = await Promise.all(
        bridges.map(async (b: any) => {
          try {
            const metricsRes = await axios.get(
              `${apiUrl}/api/v5/bridges/${b.type}:${b.name}/metrics`,
              { headers, timeout: 5000 },
            );
            const m = metricsRes.data.metrics || {};
            return {
              name: b.name,
              type: b.type,
              status: b.status,
              status_reason: b.status_reason,
              server: b.server,
              enable: b.enable,
              egress: b.egress ? { source: ruleTopics.get(`mqtt:${b.name}`) || b.egress.local?.topic, target: b.egress.remote?.topic } : undefined,
              ingress: b.ingress ? { source: b.ingress.remote?.topic, target: b.ingress.local?.topic } : undefined,
              metrics: {
                received: m.received ?? 0,
                success: m.success ?? 0,
                failed: m.failed ?? 0,
                dropped: m.dropped ?? 0,
                matched: m.matched ?? 0,
                rate: m.rate ?? 0,
                rateLast5m: m.rate_last5m ?? 0,
              },
            };
          } catch {
            return { name: b.name, status: b.status, error: 'metrics unavailable' };
          }
        }),
      );

      return details;
    } catch (err: any) {
      this.logger.error(`getBridgeDetails failed: ${err.message}`);
      return [];
    }
  }

  /** 桥接日志轮询：状态变化记录连接事件，拉取计数，维护每桥消息订阅 */
  private async pollBridgeLogs() {
    let token: string;
    try {
      token = await this.getEmqxToken();
    } catch {
      return;
    }
    const headers = { Authorization: `Bearer ${token}` };
    const apiUrl = this.getEmqxApiUrl();

    let bridges: any[] = [];
    try {
      const res = await axios.get(`${apiUrl}/api/v5/bridges`, { headers, timeout: 5000 });
      bridges = Array.isArray(res.data) ? res.data : [];
    } catch {
      return;
    }

    const relevant = bridges.filter((b: any) => b.name?.startsWith('platform_bridge_'));
    const ruleTopics = await this.getEmqxRulesWithMapping();
    const seen = new Set<string>();

    for (const b of relevant) {
      seen.add(b.name);
      let st = this.bridgeLogState.get(b.name);
      if (!st) {
        st = { server: '', status: '', statusReason: '', counters: null, events: [], messages: [], missingSince: 0 };
        this.bridgeLogState.set(b.name, st);
      }
      st.server = b.server || '';
      if (st.missingSince) st.missingSince = 0;

      const status = b.status || 'unknown';
      const reason = b.status_reason || '';
      if (status !== st.status || reason !== st.statusReason) {
        st.status = status;
        st.statusReason = reason;
        st.events.push({ ts: Date.now(), status, reason });
        if (st.events.length > 30) st.events.shift();
        if (status !== 'connected') {
          this.logger.warn(`Bridge ${b.name} status changed: ${status}${reason ? ` (${reason})` : ''}`);
        }
      }

      try {
        const mRes = await axios.get(`${apiUrl}/api/v5/bridges/${b.type}:${b.name}/metrics`, {
          headers, timeout: 3000,
        });
        const m = mRes.data.metrics || {};
        const counters = {
          received: m.received ?? 0,
          success: m.success ?? 0,
          failed: m.failed ?? 0,
          dropped: m.dropped ?? 0,
          matched: m.matched ?? 0,
          rate: m.rate ?? 0,
        };
        const sig = JSON.stringify(counters);
        if (sig !== this.lastCounters.get(b.name)) {
          this.lastCounters.set(b.name, sig);
          st.counters = counters;
        }
      } catch { /* metrics unavailable */ }

      const msgTopic = b.egress
        ? (ruleTopics.get(`mqtt:${b.name}`) || b.egress?.local?.topic || '')
        : (b.ingress?.remote?.topic || '');
      const direction: 'in' | 'out' = b.egress ? 'out' : 'in';
      this.ensureBridgeMsgSub(b.name, msgTopic, direction);
    }

    for (const name of [...this.bridgeLogState.keys()]) {
      const st = this.bridgeLogState.get(name)!;
      if (!seen.has(name)) {
        // 桥从 EMQX 列表消失 = 被整桥删除（自愈重建），记为事件而非静默清理
        if (st.status !== 'deleted') {
          st.status = 'deleted';
          st.statusReason = '';
          st.events.push({ ts: Date.now(), status: 'deleted', reason: 'bridge removed from EMQX' });
          if (st.events.length > 30) st.events.shift();
          this.logger.warn(`Bridge ${name} disappeared from EMQX bridge list`);
        }
        if (!st.missingSince) st.missingSince = Date.now();
        // 消失超过 10 分钟才真正清理（保留历史便于界面观察）
        if (Date.now() - st.missingSince > 10 * 60 * 1000) {
          this.bridgeLogState.delete(name);
          const sub = this.bridgeMsgSubs.get(name);
          if (sub) {
            sub.end(true);
            this.bridgeMsgSubs.delete(name);
          }
          this.bridgeMsgTopics.delete(name);
          this.lastCounters.delete(name);
        }
      }
    }

    if (this.bridgeLogListeners.size > 0) {
      const snapshot = this.getBridgeLogs();
      for (const fn of this.bridgeLogListeners) fn(snapshot);
    }
  }

  /** 为单个桥维护 MQTT 订阅，捕获经它转发的消息（egress 看本地 topic，ingress 看远端 topic） */
  private ensureBridgeMsgSub(name: string, topic: string, direction: 'in' | 'out') {
    if (!topic) return;
    if (this.bridgeMsgTopics.get(name) === topic) return;

    const existing = this.bridgeMsgSubs.get(name);
    if (existing) {
      existing.end(true);
      this.bridgeMsgSubs.delete(name);
    }

    const brokerUrl = process.env.MQTT_BROKER_URL || 'mqtt://emqx:1883';
    const username = process.env.MQTT_BACKEND_USER || 'buildingos';
    const password = process.env.MQTT_BACKEND_PASS || 'buildingos_edge_2024';

    const client = mqtt.connect(brokerUrl, {
      clientId: `backend-bridgelog-${name}`,
      username,
      password,
      clean: true,
      connectTimeout: 5000,
    });
    client.on('error', () => { /* transient */ });
    client.on('connect', () => {
      client.subscribe(topic, { qos: 1 }, (err) => {
        if (err) this.logger.warn(`bridge log subscribe failed (${name} ${topic}): ${err.message}`);
      });
    });
    client.on('message', (t, payload) => {
      const st = this.bridgeLogState.get(name);
      if (!st) return;
      let text = payload.toString();
      if (text.length > 300) text = text.slice(0, 300) + '…';
      st.messages.push({ ts: Date.now(), direction, topic: t, payload: text });
      if (st.messages.length > 50) st.messages.shift();
    });
    this.bridgeMsgSubs.set(name, client);
    this.bridgeMsgTopics.set(name, topic);
  }

  /** 当前桥接日志快照（供 REST 与 SSE 共用） */
  getBridgeLogs() {
    return {
      bridges: [...this.bridgeLogState.entries()].map(([name, st]) => ({
        name,
        server: st.server,
        status: st.status,
        statusReason: st.statusReason,
        counters: st.counters,
        events: st.events,
        messages: st.messages,
      })),
    };
  }

  /** 订阅桥接日志 SSE 推送，返回取消函数；订阅时立即推送一次快照 */
  subscribeBridgeLogs(onSnapshot: (snapshot: any) => void): () => void {
    this.bridgeLogListeners.add(onSnapshot);
    onSnapshot(this.getBridgeLogs());
    return () => {
      this.bridgeLogListeners.delete(onSnapshot);
    };
  }

  /** 获取已连接的 MQTT 客户端列表，附带来源容器信息 */
  async getClients() {
    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      const apiUrl = this.getEmqxApiUrl();

      const [res, ipMap] = await Promise.all([
        axios.get(`${apiUrl}/api/v5/clients?limit=200`, { headers, timeout: 5000 }),
        this.monitorService.getContainerNetworkMap(),
      ]);

      const clients: any[] = Array.isArray(res.data.data) ? res.data.data : Array.isArray(res.data) ? res.data : [];

      return clients.map((c: any) => {
        const ip = c.ip_address || '';
        const container = ipMap.get(ip);
        return {
          clientid: c.clientid,
          username: c.username,
          ipAddress: ip,
          connected: c.connected,
          protocol: c.proto_name,
          keepalive: c.keepalive,
          connectedAt: c.connected_at,
          subscriptions: c.subscriptions_cnt ?? 0,
          source: container?.name || this.guessSource(c.clientid),
          sourceRole: container?.role || '',
        };
      });
    } catch (err: any) {
      this.logger.error(`getClients failed: ${err.message}`);
      return [];
    }
  }

  /** Fallback source guess from clientid when Docker IP match is unavailable */
  private guessSource(clientid: string): string {
    if (!clientid) return '';
    if (clientid.startsWith('nodered')) return 'nodered';
    if (clientid.startsWith('edge-') && clientid.includes('egress')) return 'edge-bridge-egress';
    if (clientid.startsWith('edge-') && clientid.includes('ingress')) return 'edge-bridge-ingress';
    if (clientid.includes('go-bridge')) return 'go-bridge';
    return '';
  }

  /** 踢掉指定客户端 */
  async kickClient(clientid: string) {
    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      const apiUrl = this.getEmqxApiUrl();
      await axios.delete(`${apiUrl}/api/v5/clients/${encodeURIComponent(clientid)}`, { headers, timeout: 5000 });
      return { ok: true };
    } catch (err: any) {
      this.logger.error(`kickClient failed: ${err.message}`);
      return { ok: false, error: err.message };
    }
  }

  /** 为指定客户端订阅主题 */
  async subscribeClient(clientid: string, topic: string, qos: number = 1) {
    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      const apiUrl = this.getEmqxApiUrl();
      await axios.post(
        `${apiUrl}/api/v5/clients/${encodeURIComponent(clientid)}/subscribe`,
        { topic, qos },
        { headers, timeout: 5000 },
      );
      return { ok: true };
    } catch (err: any) {
      this.logger.error(`subscribeClient failed: ${err.message}`);
      return { ok: false, error: err.message };
    }
  }

  /** 取消指定客户端对某主题的订阅 */
  async unsubscribeClient(clientid: string, topic: string) {
    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      const apiUrl = this.getEmqxApiUrl();
      await axios.post(
        `${apiUrl}/api/v5/clients/${encodeURIComponent(clientid)}/unsubscribe`,
        { topic },
        { headers, timeout: 5000 },
      );
      return { ok: true };
    } catch (err: any) {
      this.logger.error(`unsubscribeClient failed: ${err.message}`);
      return { ok: false, error: err.message };
    }
  }

  /** 向指定主题发布消息 */
  async publish(topic: string, payload: string, qos: number = 1, retain: boolean = false) {
    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      const apiUrl = this.getEmqxApiUrl();
      await axios.post(
        `${apiUrl}/api/v5/publish`,
        { topic, payload: Buffer.from(payload).toString('base64'), qos, retain, payload_encoding: 'base64' },
        { headers, timeout: 5000 },
      );
      return { ok: true };
    } catch (err: any) {
      this.logger.error(`publish failed: ${err.message}`);
      return { ok: false, error: err.message };
    }
  }

  /** 获取云端订阅主题（ingress bridge 的 remote topic），含消息计数 */
  async getCloudSubscription() {
    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      const apiUrl = this.getEmqxApiUrl();

      const bridgesRes = await axios.get(`${apiUrl}/api/v5/bridges`, { headers, timeout: 5000 });
      const bridges = Array.isArray(bridgesRes.data) ? bridgesRes.data : [];

      // Find ingress bridges (cloud → edge) that are enabled
      const ingressBridges = await Promise.all(
        bridges
          .filter((b: any) => b.enable && b.ingress && b.name.includes('ingress'))
          .map(async (b: any) => {
            let metrics = { received: 0, matched: 0, success: 0 };
            try {
              const mRes = await axios.get(
                `${apiUrl}/api/v5/bridges/${b.type}:${b.name}/metrics`,
                { headers, timeout: 3000 },
              );
              metrics = mRes.data.metrics || metrics;
            } catch {}
            return {
              bridgeName: b.name,
              remoteTopic: b.ingress.remote?.topic || '',
              localTopic: b.ingress.local?.topic || '',
              server: b.server || '',
              status: b.status,
              statusReason: b.status_reason || '',
              received: metrics.received || 0,
              matched: metrics.matched || 0,
              success: metrics.success || 0,
            };
          }),
      );

      return ingressBridges;
    } catch (err: any) {
      this.logger.error(`getCloudSubscription failed: ${err.message}`);
      return [];
    }
  }

  /** 启用/禁用指定桥接 */
  async enableBridge(type: string, name: string, enable: boolean) {
    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      const apiUrl = this.getEmqxApiUrl();
      await axios.put(
        `${apiUrl}/api/v5/bridges/${type}:${name}/enable/${enable}`,
        {},
        { headers, timeout: 5000 },
      );
      this.logger.log(`Bridge ${name} ${enable ? 'enabled' : 'disabled'}`);
      return { ok: true };
    } catch (err: any) {
      this.logger.error(`enableBridge ${name} failed: ${err.message}`);
      return { ok: false, error: err.message };
    }
  }

  /** 获取云端转发（egress bridge 的 local topic → cloud），含消息计数 */
  async getCloudEgress() {
    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      const apiUrl = this.getEmqxApiUrl();

      const bridgesRes = await axios.get(`${apiUrl}/api/v5/bridges`, { headers, timeout: 5000 });
      const bridges = Array.isArray(bridgesRes.data) ? bridgesRes.data : [];

      const ruleTopics = await this.getEmqxRulesWithMapping();

      const egressBridges = await Promise.all(
        bridges
          .filter((b: any) => b.enable && b.egress && b.name.includes('egress'))
          .map(async (b: any) => {
            let metrics = { received: 0, matched: 0, success: 0, failed: 0 };
            try {
              const mRes = await axios.get(
                `${apiUrl}/api/v5/bridges/${b.type}:${b.name}/metrics`,
                { headers, timeout: 3000 },
              );
              metrics = mRes.data.metrics || metrics;
            } catch {}
            return {
              bridgeName: b.name,
              localTopic: ruleTopics.get(`mqtt:${b.name}`) || b.egress.local?.topic || '',
              remoteTopic: b.egress.remote?.topic || '',
              server: b.server || '',
              status: b.status,
              statusReason: b.status_reason || '',
              received: metrics.received || 0,
              matched: metrics.matched || 0,
              success: metrics.success || 0,
              failed: metrics.failed || 0,
            };
          }),
      );

      return egressBridges;
    } catch (err: any) {
      this.logger.error(`getCloudEgress failed: ${err.message}`);
      return [];
    }
  }

  /** 订阅指定主题并流式返回消息，返回取消订阅函数 */
  async subscribeTopic(
    topic: string,
    onMessage: (topic: string, payload: string) => void,
    onReady?: () => void,
  ): Promise<{ unsubscribe: () => Promise<void> }> {
    const brokerUrl = process.env.MQTT_BROKER_URL || 'mqtt://emqx:1883';
    const username = process.env.MQTT_BACKEND_USER || 'buildingos';
    const password = process.env.MQTT_BACKEND_PASS || 'buildingos_edge_2024';

    const clientId = `backend-topic-viewer-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

    const client = await mqtt.connectAsync(brokerUrl, {
      clientId,
      username,
      password,
      clean: true,
      connectTimeout: 5000,
    });

    client.on('error', (e) => {
      this.logger.warn(`SSE MQTT client error (${clientId}): ${e.message}`);
    });

    await client.subscribeAsync(topic, { qos: 1 });

    client.on('message', (t, payload) => {
      onMessage(t, payload.toString());
    });

    this.logger.log(`Subscribed to topic "${topic}" for SSE streaming (clientId=${clientId})`);
    onReady?.();

    return {
      unsubscribe: async () => {
        try {
          await client.unsubscribeAsync(topic);
          await client.endAsync();
        } catch (e: any) {
          this.logger.warn(`Error unsubscribing topic stream: ${e.message}`);
        }
      },
    };
  }

}

import { Injectable, Logger } from '@nestjs/common';
import { Client as PgClient } from 'pg';

@Injectable()
export class DevicesService {
  private readonly logger = new Logger(DevicesService.name);

  private createPgClient(): PgClient {
    return new PgClient({
      host: process.env.PG_HOST || 'postgres',
      port: parseInt(process.env.PG_PORT || '5432', 10),
      user: process.env.PG_USER || 'buildingos',
      password: process.env.PG_PASSWORD || 'buildingos_edge_2024',
      database: process.env.PG_DATABASE || 'buildingos',
    });
  }

  async getDevices(page = 1, pageSize = 20, type?: string) {
    const client = this.createPgClient();
    try {
      await client.connect();
      const offset = (page - 1) * pageSize;
      const COLS = `id, code, "serialNumber", name, type, "iotType",
        protocol, channel, "gatewayID", "gatewayName",
        layer, "spaceCode", "spaceName", "areaCode", "areaName",
        "floorCode", "floorName", "floorAreaType", "floorAreaCode", "floorAreaName",
        "posX", "posY", "posZ", status, "statusUptime",
        "desc", "deleteFlag", createtime`;

      let dataResult, countResult;
      if (type) {
        [dataResult, countResult] = await Promise.all([
          client.query(
            `SELECT ${COLS} FROM iot_device WHERE "deleteFlag" = 1 AND type = $1 ORDER BY id LIMIT $2 OFFSET $3`,
            [type, pageSize, offset],
          ),
          client.query(
            `SELECT COUNT(*) AS total FROM iot_device WHERE "deleteFlag" = 1 AND type = $1`,
            [type],
          ),
        ]);
      } else {
        [dataResult, countResult] = await Promise.all([
          client.query(
            `SELECT ${COLS} FROM iot_device WHERE "deleteFlag" = 1 ORDER BY id LIMIT $1 OFFSET $2`,
            [pageSize, offset],
          ),
          client.query(`SELECT COUNT(*) AS total FROM iot_device WHERE "deleteFlag" = 1`),
        ]);
      }

      return {
        total: parseInt(countResult.rows[0].total, 10),
        data: dataResult.rows,
      };
    } catch (err: any) {
      this.logger.error(`Failed to query iot_device: ${err.message}`);
      return { total: 0, data: [] };
    } finally {
      await client.end().catch(() => {});
    }
  }

  async getDeviceTypes() {
    const client = this.createPgClient();
    try {
      await client.connect();
      const result = await client.query(`
        SELECT type, COUNT(*) AS count
        FROM iot_device
        WHERE "deleteFlag" = 1
        GROUP BY type
        ORDER BY count DESC
      `);
      return result.rows.map((r) => ({ type: r.type, count: parseInt(r.count, 10) }));
    } catch (err: any) {
      this.logger.error(`Failed to query device types: ${err.message}`);
      return [];
    } finally {
      await client.end().catch(() => {});
    }
  }

  async getGateways() {
    const client = this.createPgClient();
    try {
      await client.connect();
      const result = await client.query(`
        SELECT
          id, type, "typeName", name,
          macaddr, ipaddr, port,
          "spaceCode", "spaceName", "floorCode", "floorName",
          "floorAreaCode", "floorAreaName",
          "desc", "deleteFlag", "heartbeatTime", createtime
        FROM iot_gateway
        WHERE "deleteFlag" = 1
        ORDER BY id
      `);
      return result.rows;
    } catch (err: any) {
      this.logger.error(`Failed to query iot_gateway: ${err.message}`);
      return [];
    } finally {
      await client.end().catch(() => {});
    }
  }

  async getDeviceStats() {
    const client = this.createPgClient();
    try {
      await client.connect();
      const [devResult, gwResult] = await Promise.all([
        client.query(`SELECT COUNT(*) AS total FROM iot_device WHERE "deleteFlag" = 1`),
        client.query(`SELECT COUNT(*) AS total FROM iot_gateway WHERE "deleteFlag" = 1`),
      ]);
      return {
        deviceTotal: parseInt(devResult.rows[0].total, 10),
        gatewayTotal: parseInt(gwResult.rows[0].total, 10),
      };
    } catch (err: any) {
      this.logger.error(`Failed to query device stats: ${err.message}`);
      return { deviceTotal: 0, gatewayTotal: 0 };
    } finally {
      await client.end().catch(() => {});
    }
  }
}

import { Injectable, Logger } from '@nestjs/common';
import { Client as PgClient } from 'pg';
import * as fs from 'fs';
import * as path from 'path';
import { EdgeSyncService } from '../platform/edge-sync.service';

const CONFIG_PATH = path.resolve(process.cwd(), 'config', 'config.json');

const SHADOW_TABLES = [
  'space', 'floor', 'floor_area',
  'floor_room', 'floor_mroom', 'floor_pub_area', 'floor_toilet', 'floor_workstation',
  'area', 'iot_device', 'iot_gateway',
  'scene_policy',
];

const STATE_LABEL: Record<string, string> = {
  r: '就绪',
  d: '复制中',
  s: '同步中',
  i: '初始化',
  f: '已完成',
};

@Injectable()
export class DatabaseService {
  private readonly logger = new Logger(DatabaseService.name);

  constructor(private readonly edgeSyncService: EdgeSyncService) {}

  private createLocalClient(): PgClient {
    return new PgClient({
      host: process.env.PG_HOST || 'postgres',
      port: parseInt(process.env.PG_PORT || '5432', 10),
      user: process.env.PG_USER || 'buildingos',
      password: process.env.PG_PASSWORD || 'buildingos_edge_2024',
      database: process.env.PG_DATABASE || 'buildingos',
      connectionTimeoutMillis: 5000,
    });
  }

  private readConfig(): any {
    try {
      return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
    } catch {
      return {};
    }
  }

  async getStatus() {
    const cfg = this.readConfig();
    // app_sync（应用层同步，百度 RDS 等无法开逻辑复制的场景）与 pg_logical 展示不同：
    // app_sync 没有 PG 订阅/复制槽，"云端主库"改为展示 outbox 拉取状态。
    const syncMode = cfg.platform?.syncMode || 'pg_logical';

    const [localResult, cloudResult] = await Promise.allSettled([
      this.queryLocalPg(syncMode),
      this.queryCloudPg(syncMode),
    ]);

    return {
      checkedAt: new Date().toISOString(),
      syncMode,
      localPg: localResult.status === 'fulfilled' ? localResult.value : { connected: false, error: String(localResult.reason) },
      cloudPg: cloudResult.status === 'fulfilled' ? cloudResult.value : { connected: false, error: String(cloudResult.reason) },
    };
  }

  private async queryLocalPg(syncMode: string) {
    const client = this.createLocalClient();
    try {
      await client.connect();

      // app_sync 无 PG 订阅；pg_logical 读取订阅与表同步状态
      let sub: any = null;
      let relRows: { rows: Array<{ table_name: string; state: string; srsublsn: string }> } = { rows: [] };
      if (syncMode !== 'app_sync') {
        const subRow = await client.query(
          `SELECT subname, subenabled, subslotname, subconninfo
           FROM pg_subscription WHERE subname = 'platform_sub'`,
        );
        sub = subRow.rows[0] ?? null;

        relRows = await client.query<{
          table_name: string; state: string; srsublsn: string;
        }>(
          `SELECT srrelid::regclass AS table_name, srsubstate AS state, srsublsn
           FROM pg_subscription_rel sr
           JOIN pg_subscription s ON s.oid = sr.srsubid
           WHERE s.subname = 'platform_sub'
           ORDER BY srrelid`,
        );
      }

      // 各表行数（并行查询）
      const countQueries = SHADOW_TABLES.map(t =>
        client.query(`SELECT COUNT(*)::int AS n FROM ${t}`).then(r => ({ table: t, count: r.rows[0]?.n ?? 0 })).catch(() => ({ table: t, count: -1 })),
      );
      const counts = await Promise.all(countQueries);
      const countMap = Object.fromEntries(counts.map(c => [c.table, c.count]));

      // 合并 state + count（app_sync 无订阅状态，state 置 n/a）
      const stateMap = Object.fromEntries(relRows.rows.map(r => [r.table_name, { state: r.state, lsn: r.srsublsn }]));
      const tables = SHADOW_TABLES.map(t => ({
        name: t,
        state: stateMap[t]?.state ?? (syncMode === 'app_sync' ? 'n/a' : 'unknown'),
        stateLabel: STATE_LABEL[stateMap[t]?.state ?? ''] ?? (syncMode === 'app_sync' ? '—' : '未知'),
        lsn: stateMap[t]?.lsn ?? null,
        rowCount: countMap[t] ?? 0,
      }));

      const readyCount = syncMode === 'app_sync'
        ? tables.filter(t => t.rowCount >= 0).length
        : tables.filter(t => t.state === 'r').length;

      return {
        connected: true,
        host: process.env.PG_HOST || 'postgres',
        port: parseInt(process.env.PG_PORT || '5432', 10),
        database: process.env.PG_DATABASE || 'buildingos',
        user: process.env.PG_USER || 'buildingos',
        subscription: sub ? {
          name: sub.subname,
          enabled: sub.subenabled,
          slotName: sub.subslotname,
          connInfo: sub.subconninfo,
        } : null,
        tables,
        readyCount,
        totalCount: SHADOW_TABLES.length,
      };
    } catch (err: any) {
      return { connected: false, error: err.message };
    } finally {
      await client.end().catch(() => {});
    }
  }

  private async queryCloudPg(syncMode: string) {
    // app_sync：没有云端 PG 直连，"云端主库"展示应用层同步工作器状态
    if (syncMode === 'app_sync') {
      const stats = this.edgeSyncService.getStats();
      const lastErrorAt = stats.lastErrorAt ? new Date(stats.lastErrorAt).getTime() : 0;
      const lastSuccessAt = stats.lastSuccessAt ? new Date(stats.lastSuccessAt).getTime() : 0;
      return {
        connected: stats.running && !!stats.lastSuccessAt && lastSuccessAt >= lastErrorAt,
        ...stats,
      };
    }

    const cfg = this.readConfig();
    const p = cfg.platform;
    if (!p?.pgHost) return { connected: false, error: '未配置云端连接' };

    const client = new PgClient({
      host: p.pgHost,
      port: p.pgPort,
      user: p.pgReplicationUser,
      password: p.pgReplicationPassword,
      database: 'buildingos',
      connectionTimeoutMillis: 5000,
    });

    try {
      await client.connect();

      const slotRow = await client.query(
        `SELECT slot_name, active,
                pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes
         FROM pg_replication_slots WHERE slot_name = 'platform_sub'`,
      );

      const slot = slotRow.rows[0] ?? null;

      return {
        connected: true,
        host: p.pgHost,
        port: p.pgPort,
        user: p.pgReplicationUser,
        publication: p.pgPublication,
        slot: slot ? {
          name: slot.slot_name,
          active: slot.active,
          lagBytes: parseInt(slot.lag_bytes ?? '0', 10),
        } : null,
      };
    } catch (err: any) {
      return {
        connected: false,
        host: p.pgHost,
        port: p.pgPort,
        user: p.pgReplicationUser,
        publication: p.pgPublication,
        error: err.message,
      };
    } finally {
      await client.end().catch(() => {});
    }
  }
}

import {
  Injectable,
  Logger,
  BadRequestException,
  OnModuleInit,
} from '@nestjs/common';
import axios from 'axios';
import * as fs from 'fs';
import * as path from 'path';
import { Client as PgClient } from 'pg';
import { RegisterDto } from './dto/platform.dto';
import { SHADOW_TABLES, SHADOW_TABLE_DDL } from './shadow-tables';
import { EdgeSyncService } from './edge-sync.service';

const CONFIG_PATH = path.resolve(process.cwd(), 'config', 'config.json');

// 启动后等待 PG 就绪的延迟（ms）
const PG_READY_DELAY_MS = 6000;

// 周期心跳间隔（ms）：上报在线状态 + 同步云端 broker 变更自愈桥接
const HEARTBEAT_INTERVAL_MS = 60000;

// 桥接/规则自愈检查间隔（ms）：EMQX 状态丢失后自动补桥补规则
const BRIDGE_HEALTH_INTERVAL_MS = 5 * 60 * 1000;

@Injectable()
export class PlatformService implements OnModuleInit {
  private readonly logger = new Logger(PlatformService.name);

  constructor(private readonly edgeSyncService: EdgeSyncService) {}

  // ── NestJS 生命周期：模块初始化时自动修复订阅 / 启动同步 worker ──────────────

  async onModuleInit() {
    const cfg = this.readConfig();

    // 周期心跳：上报在线状态，并自动同步云端 broker 入口变更（桥接自愈）
    setInterval(() => {
      if (this.readConfig().connectionStatus !== 'ACTIVE') return;
      this.heartbeat().catch(() => {});
    }, HEARTBEAT_INTERVAL_MS);

    if (cfg.connectionStatus !== 'ACTIVE' || !cfg.platform) {
      this.logger.log('No active platform connection, skipping sync startup');
      return;
    }

    this.logger.log(`Active platform detected (${cfg.platform.url}), sync startup scheduled in ${PG_READY_DELAY_MS / 1000}s...`);
    // 异步执行，不阻塞 NestJS 启动
    setTimeout(() => {
      if (cfg.platform?.syncMode === 'app_sync') {
        this.edgeSyncService.start({
          url: cfg.platform.url,
          jwt: cfg.platform.jwt,
          spaceCode: cfg.spaceCode,
        });
      } else {
        this.ensureSubscriptionHealthy().catch(err =>
          this.logger.error(`Subscription health check error: ${err.message}`),
        );
      }
    }, PG_READY_DELAY_MS);

    // 桥接自愈：启动 30s 后首检，此后每 5 分钟幂等检查（桥缺失→重建，规则缺失→补齐）
    setTimeout(() => {
      this.ensureBridgesHealthy().catch(() => {});
    }, 30000);
    setInterval(() => {
      this.ensureBridgesHealthy().catch(() => {});
    }, BRIDGE_HEALTH_INTERVAL_MS);
  }

  // ── 配置文件读写 ─────────────────────────────────────────────────────────────

  readConfig(): any {
    try {
      return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
    } catch {
      return {};
    }
  }

  private writeConfig(data: any) {
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(data, null, 2), 'utf-8');
  }

  getStatus() {
    const cfg = this.readConfig();
    const p = cfg.platform || {};
    return {
      connectionStatus: cfg.connectionStatus || 'UNCONFIGURED',
      spaceCode: cfg.spaceCode || null,
      platformUrl: p.url || null,
      registeredAt: p.registeredAt || null,
      lastHeartbeat: p.lastHeartbeat || null,
      mqttBroker: p.mqttBroker || null,
      pgHost: p.pgHost || null,
      syncMode: p.syncMode || 'pg_logical',
      license: p.license || null,
    };
  }

  getHistory() {
    const cfg = this.readConfig();
    return cfg.platformHistory || [];
  }

  // ── 连接测试 ──────────────────────────────────────────────────────────────────

  private resolveUrl(base: string, ...paths: string[]): string {
    const u = new URL(base.replace(/\/+$/, ''));
    u.pathname = [u.pathname.replace(/\/+$/, ''), ...paths.map(p => p.replace(/^\/+/, ''))].join('/');
    return u.toString();
  }

  async testConnection(platformUrl: string) {
    try {
      const targetUrl = this.resolveUrl(platformUrl, '/api/');
      const res = await axios.get(targetUrl, { timeout: 5000 });
      return { reachable: true, status: res.status };
    } catch (err: any) {
      return { reachable: false, error: err.message };
    }
  }

  // ── 注册 ──────────────────────────────────────────────────────────────────────

  async register(dto: RegisterDto) {
    const cfg = this.readConfig();
    if (cfg.connectionStatus === 'ACTIVE') {
      throw new BadRequestException('当前已有激活的平台对接，请先解绑或强制替换');
    }

    const registerUrl = this.resolveUrl(dto.platformUrl, '/api/edge/register');

    let resp: any;
    try {
      const { data } = await axios.post(
        registerUrl,
        {
          registrationToken: dto.registrationToken,
          spaceCode: dto.spaceCode,
          edgeIp: dto.edgeIp,
        },
        { timeout: 10000 },
      );
      resp = data.data;
    } catch (err: any) {
      throw new BadRequestException(`平台注册失败: ${err.response?.data?.message || err.message}`);
    }

    const preview = this.buildConfigPreview(dto.platformUrl, resp);
    return { preview, credentials: resp };
  }

  // ── 应用配置（注册后调用，建立 MQTT 桥接 + PG 订阅） ─────────────────────────

  async applyConfig(credentials: any, platformUrl: string) {
    const cfg = this.readConfig();

    const syncMode = credentials.pg?.syncMode || 'pg_logical';
    const oldPlatform = cfg.platform;
    cfg.spaceCode = credentials.spaceCode;
    cfg.connectionStatus = 'ACTIVE';
    cfg.platform = {
      url: platformUrl,
      jwt: credentials.jwt,
      jwtExpiresAt: credentials.jwtExpiresAt,
      mqttBroker: credentials.mqtt.broker,
      mqttUsername: credentials.mqtt.username,
      mqttPassword: credentials.mqtt.password,
      syncMode,
      pgHost: credentials.pg?.host,
      pgPort: credentials.pg?.port,
      pgReplicationUser: credentials.pg?.replicationUser,
      pgReplicationPassword: credentials.pg?.replicationPassword,
      pgPublication: credentials.pg?.publicationName,
      license: credentials.license || null,
      registeredAt: new Date().toISOString(),
      lastHeartbeat: new Date().toISOString(),
    };

    if (!cfg.platformHistory) cfg.platformHistory = [];
    if (oldPlatform?.url) {
      cfg.platformHistory.unshift({
        url: oldPlatform.url,
        spaceCode: cfg.spaceCode,
        connectedAt: oldPlatform.registeredAt,
        disconnectedAt: new Date().toISOString(),
        reason: 'replaced',
      });
    }
    this.writeConfig(cfg);

    const emqxResult = await this.setupEmqxBridge(credentials.mqtt, credentials.spaceCode);
    let pgResult: any;
    if (syncMode === 'app_sync') {
      // 应用层同步：无需 PG 订阅，启动 HTTP 拉取 worker
      this.edgeSyncService.start({
        url: platformUrl,
        jwt: credentials.jwt,
        spaceCode: credentials.spaceCode,
      });
      pgResult = { ok: true, mode: 'app_sync', note: '应用层同步：边缘通过平台 HTTP 拉取 outbox 增量' };
    } else {
      pgResult = await this.setupPgSubscription(credentials.pg, platformUrl, credentials.jwt);
    }

    return { emqxBridge: emqxResult, pgSubscription: pgResult };
  }

  // ── 解绑（正常） ──────────────────────────────────────────────────────────────

  async unbind() {
    const cfg = this.readConfig();
    const p = cfg.platform || {};

    if (p.url && p.jwt) {
      try {
        const unbindUrl = this.resolveUrl(p.url, `/api/edge/nodes/${cfg.spaceCode}/unbind`);
        await axios.delete(unbindUrl, {
          headers: { Authorization: `Bearer ${p.jwt}` },
          timeout: 8000,
        });
      } catch (err: any) {
        this.logger.warn(`Platform unbind notification failed: ${err.message}`);
      }
    }

    await this.cleanupLocalConfigs(cfg.spaceCode);
    this.clearPlatformConfig(cfg);
    return { ok: true };
  }

  // ── 强制替换（平台不可达时） ──────────────────────────────────────────────────

  async forceReplace() {
    const cfg = this.readConfig();
    await this.cleanupLocalConfigs(cfg.spaceCode);
    this.clearPlatformConfig(cfg);
    return { ok: true };
  }

  // ── 心跳 ──────────────────────────────────────────────────────────────────────

  /** 从现有 config.json 重建 EMQX 桥接，无需重新注册 */
  async rebuildBridges() {
    const cfg = this.readConfig();
    if (!cfg.platform?.mqttBroker || !cfg.spaceCode) {
      throw new BadRequestException('无有效的平台对接配置，请先注册');
    }
    // 保持与原始注册一致的 server 格式（用 config 中存储的原始值去掉协议前缀）
    const broker = cfg.platform.mqttBroker.replace(/^mqtt:\/\//, '');
    const mqtt = {
      broker,
      username: cfg.platform.mqttUsername,
      password: cfg.platform.mqttPassword,
    };
    return await this.setupEmqxBridge(mqtt, cfg.spaceCode);
  }

  /** 幂等自愈：桥缺失→整组重建；桥在而规则缺失→只补规则。无需人工命令 */
  private async ensureBridgesHealthy() {
    const cfg = this.readConfig();
    if (cfg.connectionStatus !== 'ACTIVE' || !cfg.platform?.mqttBroker || !cfg.spaceCode) return;
    const emqxApi = process.env.EMQX_API_URL || 'http://emqx:18083';
    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      const sc = cfg.spaceCode.toLowerCase();
      const res = await axios.get(`${emqxApi}/api/v5/bridges`, { headers, timeout: 5000 });
      const names = new Set((res.data || []).map((b: any) => b.name));
      const expected = [
        `platform_bridge_${sc}_egress`,
        `platform_bridge_${sc}_egress_report`,
        `platform_bridge_${sc}_egress_data`,
        `platform_bridge_${sc}_ingress`,
      ];
      const missing = expected.filter((n) => !names.has(n));
      if (missing.length > 0) {
        this.logger.warn(`Bridges missing (${missing.join(', ')}), rebuilding...`);
        await this.rebuildBridges();
        return;
      }
      await this.ensureEmqxRules(token, headers, sc, cfg.spaceCode, emqxApi);
    } catch (err: any) {
      this.logger.warn(`Bridge health check failed: ${err.message}`);
    }
  }

  async heartbeat() {
    const cfg = this.readConfig();
    const p = cfg.platform;
    if (!p?.url || !p?.jwt) return { reachable: false };
    try {
      const heartbeatUrl = this.resolveUrl(p.url, `/api/edge/nodes/${cfg.spaceCode}/heartbeat`);
      const { data } = await axios.post(
        heartbeatUrl,
        {},
        { headers: { Authorization: `Bearer ${p.jwt}` }, timeout: 5000 },
      );
      p.lastHeartbeat = new Date().toISOString();

      // 自愈：云端 MQTT 入口变更时（如 Broker 地址从种子默认值纠正），
      // 同步本地配置并重建桥接，无需人工重新注册
      const remote = data?.data;
      if (remote?.mqttBroker && remote.mqttBroker !== p.mqttBroker) {
        this.logger.log(
          `Cloud mqtt broker changed: ${p.mqttBroker} -> ${remote.mqttBroker}, rebuilding bridges`,
        );
        p.mqttBroker = remote.mqttBroker;
        this.writeConfig(cfg);
        await this.rebuildBridges();
        return { reachable: true, mqttBroker: p.mqttBroker, bridgesRebuilt: true };
      }

      this.writeConfig(cfg);
      return { reachable: true, mqttBroker: p.mqttBroker };
    } catch {
      return { reachable: false };
    }
  }

  // ── EMQX 桥接 ─────────────────────────────────────────────────────────────────

  /**
   * EMQX 5.8 要求 Bearer Token 认证（Dashboard 登录），不支持 Basic Auth。
   * 且不允许同一桥接同时包含 ingress + egress，需拆为两个独立桥接。
   */
  private async getEmqxToken(): Promise<string> {
    const emqxApi = process.env.EMQX_API_URL || 'http://emqx:18083';
    const password = process.env.EMQX_ADMIN_PASSWORD || 'admin123';
    const res = await axios.post(`${emqxApi}/api/v5/login`, {
      username: 'admin',
      password,
    }, { timeout: 5000 });
    return res.data.token;
  }

  private async setupEmqxBridge(mqtt: any, spaceCode: string) {
    const emqxApi = process.env.EMQX_API_URL || 'http://emqx:18083';

    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      const sc = spaceCode.toLowerCase();

      // EMQX MQTT bridge 需要使用 TCP 端口（不同于 WebSocket）
      // tcpBroker 优先，其次从 broker URL 解析
      const server = mqtt.tcpBroker
        ? mqtt.tcpBroker
        : this.parseMqttHostPort(mqtt.broker || '');

      // Clean up old rules first (they reference bridge ids)
      await this.deleteEmqxRules(token, headers, sc, emqxApi);

      // Clean up old bridges (both v1 combined + v2 split)
      await axios.delete(`${emqxApi}/api/v5/bridges/mqtt:platform_bridge_${sc}`, { headers }).catch(() => {});
      await axios.delete(`${emqxApi}/api/v5/bridges/mqtt:platform_bridge_${sc}_egress`, { headers }).catch(() => {});
      await axios.delete(`${emqxApi}/api/v5/bridges/mqtt:platform_bridge_${sc}_egress_report`, { headers }).catch(() => {});
      await axios.delete(`${emqxApi}/api/v5/bridges/mqtt:platform_bridge_${sc}_egress_data`, { headers }).catch(() => {});
      await axios.delete(`${emqxApi}/api/v5/bridges/mqtt:platform_bridge_${sc}_ingress`, { headers }).catch(() => {});

      // 等待旧桥接资源池完全释放，避免 EMQX 5.8 start_ecpool_error
      await new Promise((r) => setTimeout(r, 2000));

      // Egress 1: edge → cloud for space-scoped status (auto from spaceCode).
      const egressStatusConfig = {
        type: 'mqtt',
        name: `platform_bridge_${sc}_egress`,
        enable: true,
        server,
        clientid: `edge-${spaceCode}-egress`,
        username: mqtt.username,
        password: mqtt.password,
        clean_start: true,
        keepalive: '60s',
        retry_interval: '15s',
        max_inflight: 100,
        egress: {
          remote: { topic: `\${topic}`, qos: 1, retain: false, payload: `\${payload}` },
        },
      };
      const er = await axios.post(`${emqxApi}/api/v5/bridges`, egressStatusConfig, { headers, timeout: 10000 });
      this.logger.log(`EMQX egress bridge created: platform_bridge_${sc}_egress (status: ${er.data.status})`);

      // Egress 2: edge → cloud for global status/report.
      const egressReportConfig = {
        type: 'mqtt',
        name: `platform_bridge_${sc}_egress_report`,
        enable: true,
        server,
        clientid: `edge-${spaceCode}-egress-report`,
        username: mqtt.username,
        password: mqtt.password,
        clean_start: true,
        keepalive: '60s',
        retry_interval: '15s',
        max_inflight: 100,
        egress: {
          remote: { topic: `\${topic}`, qos: 1, retain: false, payload: `\${payload}` },
        },
      };
      const err = await axios.post(`${emqxApi}/api/v5/bridges`, egressReportConfig, { headers, timeout: 10000 });
      this.logger.log(`EMQX egress bridge created: platform_bridge_${sc}_egress_report (status: ${err.data.status})`);

      // Egress 3: edge → cloud for sensor data report (go-bridge topics).
      const egressDataConfig = {
        type: 'mqtt',
        name: `platform_bridge_${sc}_egress_data`,
        enable: true,
        server,
        clientid: `edge-${spaceCode}-egress-data`,
        username: mqtt.username,
        password: mqtt.password,
        clean_start: true,
        keepalive: '60s',
        retry_interval: '15s',
        max_inflight: 100,
        egress: {
          remote: { topic: `\${topic}`, qos: 1, retain: false, payload: `\${payload}` },
        },
      };
      const edr = await axios.post(`${emqxApi}/api/v5/bridges`, egressDataConfig, { headers, timeout: 10000 });
      this.logger.log(`EMQX egress bridge created: platform_bridge_${sc}_egress_data (status: ${edr.data.status})`);

      // Ingress: cloud → edge. bridge_mode=true required for EMQX 5.8 ingress to work.
      const ingressConfig = {
        type: 'mqtt',
        name: `platform_bridge_${sc}_ingress`,
        enable: true,
        bridge_mode: true,
        server,
        clientid: `edge-${spaceCode}-ingress`,
        username: mqtt.username,
        password: mqtt.password,
        clean_start: true,
        keepalive: '60s',
        retry_interval: '15s',
        max_inflight: 100,
        ingress: {
          remote: { topic: `/iot/action/+/${spaceCode}/#`, qos: 1 },
          local: { topic: `\${topic}`, qos: 1, retain: false, payload: `\${payload}` },
        },
      };
      const ir = await axios.post(`${emqxApi}/api/v5/bridges`, ingressConfig, { headers, timeout: 10000 });
      this.logger.log(`EMQX ingress bridge created: platform_bridge_${sc}_ingress (status: ${ir.data.status})`);

      // 规则是 egress 桥的唯一消息入口（桥不建本地订阅），幂等补齐
      await this.ensureEmqxRules(token, headers, sc, spaceCode, emqxApi);

      return { ok: true, egressBridge: er.data.status, ingressBridge: ir.data.status };
    } catch (err: any) {
      this.logger.error(`EMQX bridge setup failed: ${err.message}`);
      return { ok: false, error: err.message };
    }
  }

  private async removeEmqxBridge(spaceCode: string) {
    if (!spaceCode) return;
    const emqxApi = process.env.EMQX_API_URL || 'http://emqx:18083';
    const sc = spaceCode.toLowerCase();
    try {
      const token = await this.getEmqxToken();
      const headers = { Authorization: `Bearer ${token}` };
      await this.deleteEmqxRules(token, headers, sc, emqxApi);
      await axios.delete(`${emqxApi}/api/v5/bridges/mqtt:platform_bridge_${sc}`, { headers, timeout: 5000 }).catch(() => {});
      await axios.delete(`${emqxApi}/api/v5/bridges/mqtt:platform_bridge_${sc}_egress`, { headers, timeout: 5000 }).catch(() => {});
      await axios.delete(`${emqxApi}/api/v5/bridges/mqtt:platform_bridge_${sc}_egress_report`, { headers, timeout: 5000 }).catch(() => {});
      await axios.delete(`${emqxApi}/api/v5/bridges/mqtt:platform_bridge_${sc}_egress_data`, { headers, timeout: 5000 }).catch(() => {});
      await axios.delete(`${emqxApi}/api/v5/bridges/mqtt:platform_bridge_${sc}_ingress`, { headers, timeout: 5000 }).catch(() => {});
      this.logger.log(`EMQX bridges removed for spaceCode: ${spaceCode}`);
    } catch (err: any) {
      this.logger.warn(`Remove EMQX bridges failed: ${err.message}`);
    }
  }

  /** 删除 3 条上行转发规则（幂等，按名字匹配） */
  private async deleteEmqxRules(token: string, headers: any, sc: string, emqxApi: string) {
    const names = [
      `platform_rule_${sc}_egress`,
      `platform_rule_${sc}_egress_report`,
      `platform_rule_${sc}_egress_data`,
    ];
    try {
      const res = await axios.get(`${emqxApi}/api/v5/rules?limit=1000`, { headers, timeout: 5000 });
      for (const r of res.data?.data || []) {
        if (names.includes(r.name)) {
          await axios.delete(`${emqxApi}/api/v5/rules/${r.id}`, { headers, timeout: 5000 }).catch(() => {});
          this.logger.log(`EMQX rule removed: ${r.name}`);
        }
      }
    } catch (err: any) {
      const detail = err.response?.data ? ` | ${JSON.stringify(err.response.data)}` : '';
      this.logger.warn(`EMQX rule cleanup failed: ${err.message}${detail}`);
    }
  }

  /** 幂等补齐 3 条上行转发规则：存在则跳过，不存在则创建 */
  private async ensureEmqxRules(token: string, headers: any, sc: string, spaceCode: string, emqxApi: string) {
    const ruleDefs = [
      {
        name: `platform_rule_${sc}_egress`,
        sql: `SELECT * FROM "/iot/status/+/${spaceCode}/#"`,
        bridgeId: `mqtt:platform_bridge_${sc}_egress`,
      },
      {
        name: `platform_rule_${sc}_egress_report`,
        sql: `SELECT * FROM "/iot/status/report"`,
        bridgeId: `mqtt:platform_bridge_${sc}_egress_report`,
      },
      {
        name: `platform_rule_${sc}_egress_data`,
        sql: `SELECT * FROM "/iot/+/+/report"`,
        bridgeId: `mqtt:platform_bridge_${sc}_egress_data`,
      },
    ];
    try {
      const res = await axios.get(`${emqxApi}/api/v5/rules?limit=1000`, { headers, timeout: 5000 });
      const existing = new Set((res.data?.data || []).map((r: any) => r.name));
      for (const def of ruleDefs) {
        if (existing.has(def.name)) continue;
        await axios.post(
          `${emqxApi}/api/v5/rules`,
          {
            name: def.name,
            enable: true,
            sql: def.sql,
            actions: [def.bridgeId],
          },
          { headers, timeout: 5000 },
        );
        this.logger.log(`EMQX rule created: ${def.name} (${def.sql} -> ${def.bridgeId})`);
      }
    } catch (err: any) {
      const detail = err.response?.data ? ` | ${JSON.stringify(err.response.data)}` : '';
      this.logger.error(`EMQX rule setup failed: ${err.message}${detail}`);
    }
  }

  // ── PG 影子订阅 ───────────────────────────────────────────────────────────────

  /**
   * 完整建立订阅：本地建表 → 安全删旧订阅 → 截断旧数据 → 建新订阅
   * DDL 内嵌于 SHADOW_TABLE_DDL，不依赖云端 API。
   */
  private async setupPgSubscription(pg: any, _platformUrl: string, _jwt: string) {
    const client = this.createPgClient();
    try {
      await client.connect();

      // 1. 幂等建所有影子表
      await this.ensureShadowTablesExist(client);

      // 2. 安全删旧订阅
      await this.safeDropSubscription(client);

      // 3. 截断旧数据（换平台时保证干净）
      await this.truncateShadowTables(client);

      // 4. 用干净连接建新订阅（DDL 需独立连接避免状态污染）
      await client.end().catch(() => {});
      const subClient = this.createPgClient();
      try {
        await subClient.connect();
        const connStr = this.buildConnStr(pg.host, pg.port, pg.replicationUser, pg.replicationPassword);
        await subClient.query(
          `CREATE SUBSCRIPTION platform_sub
           CONNECTION '${connStr}'
           PUBLICATION "${pg.publicationName}"
           WITH (copy_data = true, connect = true)`,
        );
        this.logger.log(`PG subscription created: platform_sub → ${pg.host}:${pg.port}`);
      } finally {
        await subClient.end().catch(() => {});
      }

      return { ok: true };
    } catch (err: any) {
      this.logger.error(`PG subscription setup failed: ${err.message}`);
      return { ok: false, error: err.message };
    } finally {
      await client.end().catch(() => {});
    }
  }

  /**
   * 启动时自动检查订阅健康。流程：
   *   1. 影子表部分缺失 → 补建缺失表 + REFRESH PUBLICATION（追加新表数据）
   *   2. 影子表全部缺失 → 全量重建订阅
   *   3. 订阅不存在 → 重建
   *   4. 订阅存在但远端 slot 丢失 → 安全重建
   *   5. 远端不可达 → 跳过（PG worker 自动重试）
   */
  async repairSubscription() {
    this.logger.log('Manual subscription repair triggered');
    await this.ensureSubscriptionHealthy();
    return { ok: true };
  }

  private async ensureSubscriptionHealthy() {
    const cfg = this.readConfig();
    const p = cfg.platform;
    if (!p) return;

    const client = this.createPgClient();
    try {
      await client.connect();

      // 检查所有影子表存在情况
      const tableCheck = await client.query<{ cnt: string }>(
        `SELECT COUNT(*) AS cnt FROM information_schema.tables
         WHERE table_schema = 'public' AND table_name = ANY($1)`,
        [SHADOW_TABLES],
      );
      const existingCount = parseInt(tableCheck.rows[0].cnt, 10);

      if (existingCount === 0) {
        // 全部缺失，走全量重建
        this.logger.warn('All shadow tables missing on startup, running full setup...');
        await client.end().catch(() => {});
        await this.setupPgSubscription(
          { host: p.pgHost, port: p.pgPort, replicationUser: p.pgReplicationUser,
            replicationPassword: p.pgReplicationPassword, publicationName: p.pgPublication },
          p.url, p.jwt,
        );
        return;
      }

      // 补建缺失的表
      if (existingCount < SHADOW_TABLES.length) {
        this.logger.warn(`Shadow tables partial: ${existingCount}/${SHADOW_TABLES.length}, creating missing tables...`);
        await this.ensureShadowTablesExist(client);
      }

      // 检查本地订阅是否存在
      const subResult = await client.query(
        `SELECT subname FROM pg_subscription WHERE subname = 'platform_sub'`,
      );

      if (subResult.rows.length === 0) {
        this.logger.warn('Subscription missing on startup, recreating...');
        await this.recreateSubscriptionInClient(client, p);
        return;
      }

      // 订阅已存在：检查订阅的表数量，若少于 SHADOW_TABLES 则 REFRESH
      const subRelCount = await client.query<{ cnt: string }>(
        `SELECT COUNT(*) AS cnt FROM pg_subscription_rel sr
         JOIN pg_subscription s ON s.oid = sr.srsubid
         WHERE s.subname = 'platform_sub'`,
      );
      const subscribedTables = parseInt(subRelCount.rows[0].cnt, 10);
      if (subscribedTables < SHADOW_TABLES.length) {
        // 新增同步表：REFRESH PUBLICATION 只更新表清单、不复制存量数据，
        // 必须全量重建订阅（copy_data=true）才能拿到新表数据。
        this.logger.log(`Subscription has ${subscribedTables} tables, expected ${SHADOW_TABLES.length}. Recreating with copy_data...`);
        await this.recreateSubscriptionInClient(client, p);
        return;
      }

      // 检查远端 slot
      await this.repairIfSlotMissing(client, p);

    } catch (err: any) {
      this.logger.error(`Subscription health check failed: ${err.message}`);
    } finally {
      await client.end().catch(() => {});
    }
  }

  /**
   * 检查远端 slot 是否存在，不存在则安全重建。
   * 若远端不可达，跳过（worker 会自动重试）。
   */
  private async repairIfSlotMissing(client: PgClient, p: any) {
    const pubClient = new PgClient({
      host: p.pgHost,
      port: p.pgPort,
      user: p.pgReplicationUser,
      password: p.pgReplicationPassword,
      database: 'buildingos',
      connectionTimeoutMillis: 5000,
    });

    let publisherReachable = false;
    let slotExists = false;

    try {
      await pubClient.connect();
      publisherReachable = true;
      const result = await pubClient.query(
        `SELECT slot_name FROM pg_replication_slots WHERE slot_name = 'platform_sub'`,
      );
      slotExists = result.rows.length > 0;
    } catch (err: any) {
      this.logger.warn(`Cannot reach publisher to verify slot (will retry automatically): ${err.message}`);
      return;
    } finally {
      await pubClient.end().catch(() => {});
    }

    if (!slotExists) {
      this.logger.warn('Replication slot missing on publisher, safely recreating subscription...');
      await this.recreateSubscriptionInClient(client, p);
    } else {
      this.logger.log('Subscription healthy: slot exists on publisher');
    }
  }

  /**
   * 安全重建订阅：用独立连接执行 CREATE SUBSCRIPTION，
   * 避免 DDL 命令与普通查询共用连接产生状态污染/死锁。
   */
  private async recreateSubscriptionInClient(checkClient: PgClient, p: any) {
    // 步骤1：在 checkClient 上安全删旧订阅并清数据
    await this.safeDropSubscription(checkClient);
    await this.truncateShadowTables(checkClient);

    // 步骤2：用全新连接执行 CREATE SUBSCRIPTION（DDL 需要干净连接）
    const freshClient = this.createPgClient();
    try {
      await freshClient.connect();
      const connStr = this.buildConnStr(p.pgHost, p.pgPort, p.pgReplicationUser, p.pgReplicationPassword);
      await freshClient.query(
        `CREATE SUBSCRIPTION platform_sub
         CONNECTION '${connStr}'
         PUBLICATION "${p.pgPublication}"
         WITH (copy_data = true, connect = true)`,
      );
      this.logger.log(`Subscription recreated: platform_sub → ${p.pgHost}:${p.pgPort}`);
    } finally {
      await freshClient.end().catch(() => {});
    }
  }

  /**
   * 幂等建所有影子表（CREATE TABLE IF NOT EXISTS），不影响已有数据。
   */
  private async ensureShadowTablesExist(client: PgClient) {
    for (const tbl of SHADOW_TABLES) {
      const ddl = SHADOW_TABLE_DDL[tbl];
      if (ddl) {
        await client.query(ddl).catch((err) =>
          this.logger.warn(`Create table ${tbl} warning: ${err.message}`),
        );
      }
    }
    this.logger.log(`Shadow tables ensured (${SHADOW_TABLES.length} tables)`);
  }

  /**
   * 安全删除订阅：先 DISABLE + 解除 slot 绑定，再 DROP。
   * 无论远端 slot 是否存在都不会报错。
   */
  private async safeDropSubscription(client: PgClient) {
    await client.query(`ALTER SUBSCRIPTION platform_sub DISABLE`).catch(() => {});
    await client.query(`ALTER SUBSCRIPTION platform_sub SET (slot_name = NONE)`).catch(() => {});
    await client.query(`DROP SUBSCRIPTION IF EXISTS platform_sub`).catch(() => {});
  }

  /**
   * 解绑/换绑时清空全部影子表，保证下次绑定新平台时数据干净。
   */
  private async truncateShadowTables(client: PgClient) {
    for (const tbl of SHADOW_TABLES) {
      // PostgreSQL does NOT support TRUNCATE TABLE IF EXISTS.
      // Tables are guaranteed to exist (created by ensureShadowTablesExist before this call).
      await client.query(`TRUNCATE TABLE "${tbl}" CASCADE`).catch((err) => {
        this.logger.warn(`Truncate ${tbl} skipped: ${err.message}`);
      });
    }
    this.logger.log('Shadow tables truncated');
  }

  /**
   * 解绑时在独立 client 上执行：删订阅 + 清数据。
   */
  private async removeSubscription() {
    const client = this.createPgClient();
    try {
      await client.connect();
      await this.safeDropSubscription(client);
      await this.truncateShadowTables(client);
    } catch (err: any) {
      this.logger.warn(`Remove subscription failed: ${err.message}`);
    } finally {
      await client.end().catch(() => {});
    }
  }

  private createPgClient(): PgClient {
    return new PgClient({
      host: process.env.PG_HOST || 'postgres',
      port: parseInt(process.env.PG_PORT || '5432', 10),
      user: process.env.PG_USER || 'buildingos',
      password: process.env.PG_PASSWORD || 'buildingos_edge_2024',
      database: process.env.PG_DATABASE || 'buildingos',
    });
  }

  private buildConnStr(host: string, port: number, user: string, password: string): string {
    return `host=${host} port=${port} user=${user} password=${password} dbname=buildingos sslmode=disable`;
  }

  /**
   * 从 MQTT broker URL 中提取 host:port，兼容多种格式：
   *   mqtt://host:port → host:port
   *   ws://host:port/path → host:port
   *   host:port → host:port
   */
  private parseMqttHostPort(broker: string): string {
    if (!broker) return '';
    // 如果有协议前缀，去掉
    let stripped = broker.replace(/^(mqtt|ws|wss|tcp):\/\//, '');
    // 去掉路径部分
    const slashIdx = stripped.indexOf('/');
    if (slashIdx >= 0) {
      stripped = stripped.substring(0, slashIdx);
    }
    return stripped;
  }

  // ── 工具方法 ──────────────────────────────────────────────────────────────────

  private async cleanupLocalConfigs(spaceCode: string) {
    await this.edgeSyncService.stop();
    await this.removeEmqxBridge(spaceCode);
    await this.removeSubscription(); // 内含安全删订阅 + 截断影子表
  }

  private clearPlatformConfig(cfg: any) {
    if (!cfg.platformHistory) cfg.platformHistory = [];
    if (cfg.platform?.url) {
      cfg.platformHistory.unshift({
        url: cfg.platform.url,
        spaceCode: cfg.spaceCode,
        connectedAt: cfg.platform.registeredAt,
        disconnectedAt: new Date().toISOString(),
        reason: 'unbound',
      });
    }
    cfg.connectionStatus = 'UNCONFIGURED';
    cfg.platform = null;
    this.writeConfig(cfg);
  }

  private buildConfigPreview(platformUrl: string, credentials: any) {
    return {
      emqxBridge: {
        server: credentials.mqtt.broker,
        egress: {
          clientid: `edge-${credentials.spaceCode}-egress`,
          username: credentials.mqtt.username,
          defaultTopic: `/${credentials.spaceCode}/#`,
          route: `edge → platform`,
          note: '可在 MQTT 管理 → 主题管理 → 云端转发中修改',
        },
        ingress: {
          clientid: `edge-${credentials.spaceCode}-ingress`,
          username: credentials.mqtt.username,
          defaultTopic: `/iot/action/+/${credentials.spaceCode}/#`,
          note: '可在 MQTT 管理 → 主题管理 → 云端订阅中修改',
        },
      },
      pgSubscription: credentials.pg?.syncMode === 'app_sync'
        ? {
            mode: 'app_sync',
            note: '应用层同步：边缘定期从平台拉取增量（无需 PG 逻辑复制）',
          }
        : {
            connection: `${credentials.pg.host}:${credentials.pg.port}`,
            user: credentials.pg.replicationUser,
            publication: credentials.pg.publicationName,
            tables: credentials.pg.tables,
          },
      license: credentials.license || null,
    };
  }
}

import { Injectable } from '@nestjs/common';
import axios from 'axios';

@Injectable()
export class StreamingService {
  async addStream(streamInfo: any) {
    // Logic to add stream to ZLM
    // Example: axios.get(`http://localhost:8080/index/api/addStreamProxy?secret=buildingos&vhost=__defaultVhost__&app=live&stream=${streamInfo.id}&url=${streamInfo.url}`)
    return { success: true, message: 'Stream added' };
  }

  async getStreams() {
    return [];
  }
}

```

## 后30页
以下为后30页的连续源代码片段（边缘管理Web前端）。

```
import { createRouter, createWebHistory } from 'vue-router';
import Layout from '../layout/index.vue';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
      },
      {
        path: 'mqtt',
        name: 'MQTT',
        component: () => import('../views/Mqtt.vue'),
      },
      {
        path: 'streaming',
        name: 'Streaming',
        component: () => import('../views/Streaming.vue'),
      },
      {
        path: 'devices',
        name: 'Devices',
        component: () => import('../views/Devices.vue'),
      },
      {
        path: 'database',
        name: 'Database',
        component: () => import('../views/Database.vue'),
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/Settings.vue'),
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token');
  if (to.name !== 'Login' && !token) next({ name: 'Login' });
  else next();
});

export default router;

import { defineStore } from 'pinia';
import api from '../api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null,
  }),
  actions: {
    async login(credentials: any) {
      const data: any = await api.post('/auth/login', credentials);
      this.token = data.access_token;
      localStorage.setItem('token', this.token);
    },
    logout() {
      this.token = '';
      localStorage.removeItem('token');
      this.user = null;
    },
  },
});

<template>
  <div class="login-container">
    <div class="lang-switch-login">
      <el-dropdown @command="handleLangCommand">
        <span class="lang-link">
          <el-icon><MagicStick /></el-icon>
          {{ currentLangName }}
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="zh">中文</el-dropdown-item>
            <el-dropdown-item command="en">English</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
    <el-card class="login-card">
      <template #header>
        <div class="login-header">
          <img src="/images/logo.png" alt="Logo" class="login-logo" />
          <h2>{{ $t('login.title') }}</h2>
        </div>
      </template>
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-position="top">
        <el-form-item :label="$t('login.username')" prop="username">
          <el-input v-model="loginForm.username" :placeholder="$t('login.usernamePlaceholder')" :prefix-icon="User" />
        </el-form-item>
        <el-form-item :label="$t('login.password')" prop="password">
          <el-input v-model="loginForm.password" type="password" :placeholder="$t('login.passwordPlaceholder')" :prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width: 100%" @click="handleLogin">{{ $t('login.loginButton') }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { User, Lock, MagicStick } from '@element-plus/icons-vue'
import { useAuthStore } from '../store/auth'

const { t, locale } = useI18n()
const router = useRouter()
const authStore = useAuthStore()
const loginFormRef = ref<any>(null)
const loading = ref(false)

const currentLangName = computed(() => {
  return locale.value === 'zh' ? '中文' : 'English'
})

const handleLangCommand = (lang: string) => {
  locale.value = lang
  localStorage.setItem('lang', lang)
}

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = computed(() => ({
  username: [{ required: true, message: t('login.usernamePlaceholder'), trigger: 'blur' }],
  password: [{ required: true, message: t('login.passwordPlaceholder'), trigger: 'blur' }]
}))

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.login(loginForm)
        ElMessage.success(t('login.loginSuccess'))
        router.push('/dashboard')
      } catch (err: any) {
        // Error handled by interceptor
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  position: relative;
}

.lang-switch-login {
  position: absolute;
  top: 20px;
  right: 20px;
}

.lang-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  color: #606266;
  font-size: 14px;
}

.lang-link:hover {
  color: #409eff;
}

.login-card {
  width: 400px;
}

.login-header {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.login-logo {
  width: 80px;
  height: 80px;
  margin-bottom: 20px;
}

.login-header h2 {
  margin: 0;
  color: #409eff;
}
</style>

<template>
  <div class="dashboard-container">
    <el-row :gutter="20" class="top-row">
            <!-- System Status Card -->
      <el-col :span="16" class="top-col" style="margin-bottom: 20px;">
        <el-card class="box-card system-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Monitor /></el-icon> {{ $t('dashboard.nodeStatus') }}</span>
              <el-tag size="small" type="success">{{ $t('dashboard.refreshPerSec') }}</el-tag>
            </div>
          </template>
          <div v-loading="loading" class="sys-content">
            <el-row :gutter="10" class="sys-metrics">
              <el-col :span="6" class="metric-item">
                <el-progress type="dashboard" :percentage="stats.cpu.load" :color="customColors" :width="96">
                  <template #default="{ percentage }">
                    <span class="percentage-value small">{{ percentage.toFixed(1) }}%</span>
                    <span class="percentage-label small">{{ $t('dashboard.cpuLoad') }}</span>
                  </template>
                </el-progress>
                <div class="metric-detail">--</div>
              </el-col>
              <el-col :span="6" class="metric-item">
                <el-progress type="dashboard" :percentage="stats.memory.percentage" :color="customColors" :width="96">
                  <template #default="{ percentage }">
                    <span class="percentage-value small">{{ percentage.toFixed(1) }}%</span>
                    <span class="percentage-label small">{{ $t('dashboard.ramUsage') }}</span>
                  </template>
                </el-progress>
                <div class="metric-detail">{{ formatBytes(stats.memory.used) }} / {{ formatBytes(stats.memory.total) }}</div>
              </el-col>
              <el-col :span="6" class="metric-item">
                <el-progress type="dashboard" :percentage="stats.disk.percentage" :color="customColors" :width="96">
                  <template #default="{ percentage }">
                    <span class="percentage-value small">{{ percentage.toFixed(1) }}%</span>
                    <span class="percentage-label small">{{ $t('dashboard.diskUsage') }}</span>
                  </template>
                </el-progress>
                <div class="metric-detail">{{ formatBytes(stats.disk.used) }} / {{ formatBytes(stats.disk.total) }}</div>
              </el-col>
              <el-col :span="6" class="metric-item">
                <div class="uptime-box small">
                  <span class="uptime-value small">{{ formatUptime(stats.uptime) }}</span>
                  <span class="percentage-label small">{{ $t('dashboard.uptime') }}</span>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
      <!-- Edge Details Card -->
      <el-col :span="8" class="top-col" style="margin-bottom: 20px;">
        <el-card class="box-card info-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><InfoFilled /></el-icon> {{ $t('dashboard.edgeInfo') }}</span>
            </div>
          </template>
          <div class="info-content">
            <el-row :gutter="10">
              <el-col :span="12">
                <div class="info-row grid-item">
                  <span class="label">{{ $t('dashboard.hostIp') }}</span>
                  <span class="value">{{ edgeConfig.hostIp }}</span>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="info-row grid-item">
                  <span class="label">{{ $t('dashboard.spaceCodeStatus') }}</span>
                  <span class="value">
                    {{ edgeConfig.spaceCode || '--' }} 
                    <el-tag size="small" :type="isPlatformConfigured ? 'success' : 'info'">
                      {{ isPlatformConfigured ? $t('settings.integrated') : $t('dashboard.notIntegrated') }}
                    </el-tag>
                  </span>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="info-row grid-item">
                  <span class="label">{{ $t('dashboard.hqStatus') }}</span>
                  <span class="value">
                    <span :class="['status-text', isPlatformConfigured ? 'success' : 'warning']">
                      {{ isPlatformConfigured ? $t('dashboard.connected') : $t('dashboard.notConnected') }}
                    </span>
                  </span>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="info-row grid-item">
                  <span class="label">{{ $t('dashboard.managedDevices') }}</span>
                  <span class="value"><span class="number">{{ edgeConfig.deviceCount }}</span> {{ $t('dashboard.unit') }}</span>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>

    </el-row>

    <!-- License Status Card -->
    <el-row :gutter="20" v-if="platformStatus.license">
      <el-col :span="24">
        <el-card class="box-card license-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><CircleCheck /></el-icon> {{ $t('dashboard.licenseStatus') }}</span>
              <el-tag :type="licenseTagColor" size="small" effect="dark">
                {{ licenseStatusText }}
              </el-tag>
            </div>
          </template>
          <div class="license-content">
            <div class="license-usage">
              <span class="license-label">{{ $t('dashboard.licenseDeviceUsage') }}</span>
              <el-progress
                :percentage="licenseUsagePct"
                :color="licenseProgressColor"
                :stroke-width="16"
              />
              <span class="license-usage-text">{{ platformStatus.license.currentDeviceCount.toLocaleString() }} / {{ platformStatus.license.deviceLimit.toLocaleString() }}</span>
            </div>
            <div class="license-days-info">
              <span class="license-label">{{ $t('dashboard.licenseDaysRemaining') }}</span>
              <span class="license-days-value">{{ formatLicenseDays(platformStatus.license.daysRemaining) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Container Management Card -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="box-card container-list-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Connection /></el-icon> {{ $t('dashboard.serviceStatus') }}</span>
              <div class="header-ops">
                <el-button type="warning" size="small" @click="handleOp('restart_container')">{{ $t('dashboard.restartContainer') }}</el-button>
                <el-button type="danger" size="small" @click="handleOp('restart_server')">{{ $t('dashboard.restartServer') }}</el-button>
              </div>
            </div>
          </template>
          <el-table :data="containers" style="width: 100%" size="small" border stripe class="container-table">
            <el-table-column prop="name" :label="$t('dashboard.containerName')" width="160" fixed>
              <template #default="{ row }">
                <div class="container-name-cell">
                  <span class="status-dot" :class="row.status === 'running' ? 'green' : 'red'"></span>
                  <span class="name-text">{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="id" label="ID" width="100" />
            <el-table-column prop="image" label="Image" width="180" show-overflow-tooltip />
            <el-table-column prop="ports" label="Port(s)" width="150" show-overflow-tooltip />
            
            <el-table-column label="CPU (%)" width="90" align="right">
              <template #default="{ row }">
                <span class="metric-text">{{ row.metrics.cpu.toFixed(2) }}%</span>
              </template>
            </el-table-column>
            <el-table-column label="Memory usage / limit" width="180" align="right">
              <template #default="{ row }">
                <span class="metric-text">{{ formatBytes(row.metrics.memUsed) }} / {{ formatBytes(row.metrics.memLimit) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Memory (%)" width="90" align="right">
              <template #default="{ row }">
                <span class="metric-text">{{ row.metrics.memPercent.toFixed(2) }}%</span>
              </template>
            </el-table-column>
            <el-table-column label="Disk R/W" width="140" align="right">
              <template #default="{ row }">
                <span class="metric-text">{{ formatBytes(row.metrics.diskRead) }} / {{ formatBytes(row.metrics.diskWrite) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Network I/O" width="140" align="right">
              <template #default="{ row }">
                <span class="metric-text">{{ formatBytes(row.metrics.netIn) }} / {{ formatBytes(row.metrics.netOut) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="PIDS" width="70" align="right">
              <template #default="{ row }">
                <span class="metric-text">{{ row.metrics.pids }}</span>
              </template>
            </el-table-column>

            <el-table-column :label="$t('streaming.actions')" width="200" align="center" fixed="right">
              <template #default="{ row }">
                <el-button-group>
                  <el-button type="primary" size="small" @click="handleRestart(row)">
                    <el-icon><RefreshRight /></el-icon>
                  </el-button>
                  <el-button type="info" size="small" @click="handleViewLogs(row)">
                    <el-icon><Document /></el-icon>
                  </el-button>
                  <el-button type="success" size="small" v-if="getLink(row)" @click="openLink(row)">
                    <el-icon><Link /></el-icon>
                  </el-button>
                </el-button-group>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Log Dialog -->
    <el-dialog
      v-model="logVisible"
      :title="selectedContainer?.name + ' ' + $t('dashboard.logTitle')"
      width="70%"
      destroy-on-close
    >
      <div class="log-viewer">
        <pre>{{ currentLogs }}</pre>
      </div>
      <template #footer>
        <el-button @click="logVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleViewLogs(selectedContainer)">{{ $t('dashboard.refreshPerSec') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import api from '../api';
import { ElMessageBox, ElMessage } from 'element-plus';
import { Monitor, Connection, Link, InfoFilled, RefreshRight, Document, CircleCheck } from '@element-plus/icons-vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const loading = ref(false);
const stats = ref({ 
  cpu: { load: 0 }, 
  memory: { percentage: 0, used: 0, total: 0 }, 
  disk: { percentage: 0, used: 0, total: 0 }, 
  uptime: 0 
});
const edgeConfig = ref({
  hostIp: '--',
  spaceCode: '--',
  isIntegrated: false,
  hqConnected: false,
  deviceCount: 0,
  platformUrl: '',
  platformToken: ''
});
const containers = ref<any>([]);
const logVisible = ref(false);
const selectedContainer = ref<any>(null);
const currentLogs = ref('');
const platformStatus = ref<any>({ license: null });
let timer: any = null;

const customColors = [
  { color: '#67C23A', percentage: 60 },
  { color: '#E6A23C', percentage: 80 },
  { color: '#F56C6C', percentage: 100 },
];

const isPlatformConfigured = computed(() => {
  return Boolean(
    edgeConfig.value.platformUrl &&
      edgeConfig.value.platformToken &&
      edgeConfig.value.spaceCode
  );
});

const formatUptime = (seconds: number) => {
  if (!seconds) return '0s';
  const d = Math.floor(seconds / (3600 * 24));
  const h = Math.floor((seconds % (3600 * 24)) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (d > 0) return `${d}d ${h}h`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m ${s}s`;
};

const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// ── 许可状态计算 ──────────────────────────────────────────────────────────────

const licenseStatusText = computed(() => {
  const l = platformStatus.value.license
  if (!l) return ''
  if (l.daysRemaining === 0) return '已过期'
  if (!l.valid) return '设备超限'
  if (l.daysRemaining === -1) return '永久有效'
  if (l.daysRemaining <= 30) return '即将过期'
  return '有效'
})

const licenseTagColor = computed(() => {
  const l = platformStatus.value.license
  if (!l) return 'info'
  if (l.daysRemaining === 0) return 'danger'
  if (!l.valid) return 'warning'
  if (l.daysRemaining === -1) return 'success'
  if (l.daysRemaining <= 30) return 'warning'
  return 'success'
})

const licenseUsagePct = computed(() => {
  const l = platformStatus.value.license
  if (!l?.deviceLimit) return 0
  return Math.round((l.currentDeviceCount / l.deviceLimit) * 100)
})

const licenseProgressColor = computed(() => {
  const pct = licenseUsagePct.value
  if (pct > 90) return '#F56C6C'
  if (pct > 70) return '#E6A23C'
  return '#67C23A'
})

const formatLicenseDays = (days: number): string => {
  if (days === -1) return '永久许可'
  if (days === 0) return '已过期'
  if (days <= 30) return `${days} 天（即将过期）`
  return `${days} 天`
}

const fetchData = async () => {
  try {
    const [res, conts, config, platStatus]: any = await Promise.all([
      api.get('/monitor/stats'),
      api.get('/monitor/containers'),
      api.get('/monitor/config'),
      api.get('/platform/status').catch(() => ({ data: { license: null } })),
    ]);
    stats.value = res;
    containers.value = conts;
    edgeConfig.value = config;
    platformStatus.value = platStatus.data ?? platStatus;
  } catch (e) {}
};

const handleOp = (action: string) => {
  ElMessageBox.confirm(
    t(`dashboard.${action === 'restart_container' ? 'restartContainer' : 'restartServer'}`) + '?',
    t('common.warning'),
    { type: 'warning' }
  ).then(() => {
    ElMessage.success(t('common.confirm'));
  });
};

const handleRestart = async (container: any) => {
  try {
    await api.post(`/monitor/containers/${container.id}/restart`);
    ElMessage.success(t('dashboard.restart') + ' ' + t('common.confirm'));
    fetchData();
  } catch (e) {
    ElMessage.error('Restart failed');
  }
};

const handleViewLogs = async (container: any) => {
  selectedContainer.value = container;
  try {
    const res: any = await api.get(`/monitor/containers/${container.id}/logs`);
    currentLogs.value = res.logs;
    logVisible.value = true;
  } catch (e) {
    ElMessage.error('Fetch logs failed');
  }
};

const getLink = (row: any) => {
  const name = row.name.toLowerCase();
  if (name.includes('frontend')) return `http://${window.location.hostname}:7828`;
  if (name.includes('backend')) return `http://${window.location.hostname}:7829`;
  if (name.includes('emqx')) return `http://${window.location.hostname}:18083`;
  if (name.includes('nodered')) return `http://${window.location.hostname}:1880`;
  if (name.includes('tdengine')) return `http://${window.location.hostname}:6041`;
  if (name.includes('zlmediakit')) return `http://${window.location.hostname}:8080/swagger/`;
  return null;
};

const openLink = (row: any) => {
  const url = getLink(row);
  if (url) window.open(url, '_blank');
};

onMounted(() => {
  loading.value = true;
  fetchData().finally(() => (loading.value = false));
  timer = setInterval(fetchData, 2000); // Refresh every 2 seconds to avoid excessive load
});

onBeforeUnmount(() => {
  if (timer) clearInterval(timer);
});
</script>

<style scoped>
.dashboard-container {
  padding: 10px;
}
.box-card {
  margin-bottom: 20px;
}
.top-row {
  align-items: stretch;
}
.top-col {
  display: flex;
}
.top-col :deep(.el-card) {
  width: 100%;
  height: 100%;
}
.system-card :deep(.el-card__body),
.info-card :deep(.el-card__body) {
  padding-top: 12px;
  padding-bottom: 12px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
.info-card {
  height: 100%;
}
.info-content {
  padding: 4px 0;
}
.info-row {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  font-size: 14px;
}
.info-row.grid-item {
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: 12px;
}
.info-row .label {
  color: var(--el-text-color-secondary);
  width: 120px;
  font-size: 15px;
}
.info-row.grid-item .label {
  width: auto;
  margin-bottom: 5px;
}
.info-row .value {
  color: var(--el-text-color-primary);
  font-weight: 500;
  font-size: 17px;
}
.info-row .status-text.warning {
  color: var(--el-color-warning);
}
.info-row .number {
  font-size: 22px;
  font-weight: bold;
  color: var(--el-color-primary);
}

.sys-metrics {
  text-align: center;
  margin-top: 0;
}
.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 6px;
}
.percentage-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
}
.percentage-value.small {
  font-size: 20px;
}
.percentage-label {
  display: block;
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}
.percentage-label.small {
  font-size: 13px;
}
.metric-detail {
  margin-top: 3px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  font-family: monospace;
}
.uptime-box {
  height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.uptime-box.small {
  height: 70px;
}
.uptime-value {
  font-size: 22px;
  font-weight: bold;
  color: var(--el-color-primary);
}
.uptime-value.small {
  font-size: 18px;
}
.container-table {
  font-family: 'Inter', sans-serif;
}
.container-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.green { background-color: #67C23A; box-shadow: 0 0 5px #67C23A; }
.status-dot.red { background-color: #F56C6C; box-shadow: 0 0 5px #F56C6C; }
.metric-text {
  font-family: 'Courier New', Courier, monospace;
  font-weight: 500;
  color: var(--el-text-color-primary);
}
.container-table :deep(.el-button) {
  gap: 4px;
}
.log-viewer {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 15px;
  max-height: 400px;
  overflow-y: auto;
  font-family: 'Courier New', Courier, monospace;
  border-radius: 4px;
}
.log-viewer pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.license-card { }
.license-content { display: flex; gap: 40px; align-items: flex-start; flex-wrap: wrap; }
.license-usage { flex: 1; min-width: 280px; }
.license-label { display: block; font-size: 13px; color: var(--el-text-color-secondary); margin-bottom: 8px; }
.license-usage-text { display: block; text-align: center; font-size: 12px; color: var(--el-text-color-secondary); margin-top: 6px; }
.license-days-info { }
.license-days-value { font-size: 20px; font-weight: 700; color: var(--el-color-primary); }
</style>

<template>
  <div class="devices-container">
    <el-card class="main-card">
      <el-tabs v-model="mainTab" @tab-change="handleMainTabChange">

        <!-- ===== All Devices Tab ===== -->
        <el-tab-pane name="all">
          <template #label>
            全部设备
            <el-badge v-if="totalDevices > 0" :value="totalDevices" :max="99999" type="info" class="tab-badge" />
          </template>

          <!-- Type sub-tabs -->
          <el-tabs v-model="typeTab" type="card" class="type-tabs" @tab-change="handleTypeChange">
            <el-tab-pane label="全部" name="" />
            <el-tab-pane v-for="t in deviceTypes" :key="t.type" :name="t.type">
              <template #label>
                {{ typeLabel(t.type) }}<span class="type-count">({{ t.count }})</span>
              </template>
            </el-tab-pane>
          </el-tabs>

          <el-table
            v-loading="loading"
            :data="devices"
            border
            size="small"
            class="device-table"
            highlight-current-row
            @row-click="openDeviceDetail"
          >
            <el-table-column type="index" width="50" />
            <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
            <el-table-column prop="type" label="类型" width="110">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ typeLabel(row.type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="iotType" label="IoT类型" width="95" />
            <el-table-column prop="protocol" label="协议" width="80" />
            <el-table-column prop="gatewayName" label="所属网关" min-width="130" show-overflow-tooltip />
            <el-table-column prop="floorName" label="楼层" width="75" show-overflow-tooltip />
            <el-table-column prop="floorAreaName" label="区域" min-width="110" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <div class="status-cell">
                  <span class="status-dot" :class="row.status === 'online' ? 'green' : 'red'" />
                  {{ row.status || '-' }}
                </div>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-bar">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="totalDevices"
              :page-sizes="[20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              background
              @current-change="fetchDevices"
              @size-change="handlePageSizeChange"
            />
          </div>
        </el-tab-pane>

        <!-- ===== Gateways Tab ===== -->
        <el-tab-pane name="gateways">
          <template #label>
            边缘网关
            <el-badge v-if="gateways.length > 0" :value="gateways.length" :max="999" type="warning" class="tab-badge" />
          </template>

          <el-table
            v-loading="gatewayLoading"
            :data="gateways"
            border
            size="small"
            class="device-table"
            highlight-current-row
            @row-click="openGatewayDetail"
          >
            <el-table-column type="index" width="50" />
            <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
            <el-table-column prop="typeName" label="类型" width="100" />
            <el-table-column prop="ipaddr" label="IP地址" width="130" />
            <el-table-column prop="macaddr" label="MAC地址" width="145" />
            <el-table-column prop="port" label="端口" width="75" />
            <el-table-column prop="floorName" label="楼层" width="75" show-overflow-tooltip />
            <el-table-column prop="floorAreaName" label="区域" min-width="110" show-overflow-tooltip />
            <el-table-column prop="heartbeatTime" label="最后心跳" min-width="155" show-overflow-tooltip />
          </el-table>
        </el-tab-pane>

      </el-tabs>
    </el-card>

    <!-- ===== Detail Dialog ===== -->
    <el-dialog
      v-model="detailVisible"
      :title="detailTitle"
      width="680px"
      destroy-on-close
    >
      <!-- Device detail -->
      <el-descriptions v-if="selectedDevice" :column="2" border size="small">
        <el-descriptions-item label="ID">{{ selectedDevice.id }}</el-descriptions-item>
        <el-descriptions-item label="编码">{{ selectedDevice.code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="名称" :span="2">{{ selectedDevice.name }}</el-descriptions-item>
        <el-descriptions-item label="序列号">{{ selectedDevice.serialNumber || '-' }}</el-descriptions-item>
        <el-descriptions-item label="通道">{{ selectedDevice.channel || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">
          <el-tag size="small" type="info">{{ typeLabel(selectedDevice.type) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="IoT类型">{{ selectedDevice.iotType || '-' }}</el-descriptions-item>
        <el-descriptions-item label="通信协议">{{ selectedDevice.protocol || '-' }}</el-descriptions-item>
        <el-descriptions-item label="网关ID">{{ selectedDevice.gatewayID || '-' }}</el-descriptions-item>
        <el-descriptions-item label="网关名称" :span="2">{{ selectedDevice.gatewayName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="空间">{{ selectedDevice.spaceName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="空间代码">{{ selectedDevice.spaceCode || '-' }}</el-descriptions-item>
        <el-descriptions-item label="楼层">{{ selectedDevice.floorName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="楼层代码">{{ selectedDevice.floorCode || '-' }}</el-descriptions-item>
        <el-descriptions-item label="区域">{{ selectedDevice.floorAreaName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="区域代码">{{ selectedDevice.floorAreaCode || '-' }}</el-descriptions-item>
        <el-descriptions-item label="坐标 (X/Y/Z)">
          {{ selectedDevice.posX ?? '-' }} / {{ selectedDevice.posY ?? '-' }} / {{ selectedDevice.posZ ?? '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="楼层层数">{{ selectedDevice.layer ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="运行状态">
          <div class="status-cell">
            <span class="status-dot" :class="selectedDevice.status === 'online' ? 'green' : 'red'" />
            {{ selectedDevice.status || '-' }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="上线时间">{{ selectedDevice.statusUptime || '-' }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ selectedDevice.desc || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">{{ formatTime(selectedDevice.createtime) }}</el-descriptions-item>
      </el-descriptions>

      <!-- Gateway detail -->
      <el-descriptions v-if="selectedGateway" :column="2" border size="small">
        <el-descriptions-item label="ID">{{ selectedGateway.id }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ selectedGateway.typeName || selectedGateway.type }}</el-descriptions-item>
        <el-descriptions-item label="名称" :span="2">{{ selectedGateway.name }}</el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ selectedGateway.ipaddr || '-' }}</el-descriptions-item>
        <el-descriptions-item label="端口">{{ selectedGateway.port || '-' }}</el-descriptions-item>
        <el-descriptions-item label="MAC地址" :span="2">{{ selectedGateway.macaddr || '-' }}</el-descriptions-item>
        <el-descriptions-item label="空间">{{ selectedGateway.spaceName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="空间代码">{{ selectedGateway.spaceCode || '-' }}</el-descriptions-item>
        <el-descriptions-item label="楼层">{{ selectedGateway.floorName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="楼层代码">{{ selectedGateway.floorCode || '-' }}</el-descriptions-item>
        <el-descriptions-item label="区域">{{ selectedGateway.floorAreaName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="区域代码">{{ selectedGateway.floorAreaCode || '-' }}</el-descriptions-item>
        <el-descriptions-item label="最后心跳" :span="2">{{ selectedGateway.heartbeatTime || '-' }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ selectedGateway.desc || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">{{ formatTime(selectedGateway.createtime) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../api';

const TYPE_LABELS: Record<string, string> = {
  light: '照明',
  airconditioning: '空调',
  pad: '智能面板',
  aicamerasensor: 'AI摄像头',
  powersensor: '电量传感器',
  wcsensor: '卫生间传感器',
  airsensor: '空气传感器',
  door: '门控',
  humensensor: '人员传感器',
  watersensor: '水传感器',
  blind: '遮阳帘',
  smokesensor: '烟感',
  aircleaner: '空气净化器',
  airfan: '新风机',
  dlight: '调光灯',
  inundationsensor: '积水传感器',
};

const typeLabel = (type: string) => TYPE_LABELS[type] || type;
const formatTime = (t: any) => (t ? new Date(t).toLocaleString('zh-CN') : '-');

// Main tabs
const mainTab = ref('all');

// Device list state
const loading = ref(false);
const devices = ref<any[]>([]);
const deviceTypes = ref<{ type: string; count: number }[]>([]);
const totalDevices = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);
const typeTab = ref('');

// Gateway state
const gatewayLoading = ref(false);
const gateways = ref<any[]>([]);

// Detail dialog
const detailVisible = ref(false);
const detailTitle = ref('');
const selectedDevice = ref<any>(null);
const selectedGateway = ref<any>(null);

const fetchDevices = async () => {
  loading.value = true;
  try {
    const params: Record<string, any> = { page: currentPage.value, pageSize: pageSize.value };
    if (typeTab.value) params.type = typeTab.value;
    const res: any = await api.get('/devices', { params });
    devices.value = res.data;
    totalDevices.value = res.total;
  } catch (_) {
    /* errors shown by interceptor */
  } finally {
    loading.value = false;
  }
};

const fetchDeviceTypes = async () => {
  try {
    const res: any = await api.get('/devices/types');
    deviceTypes.value = res;
  } catch (_) {}
};

const fetchGateways = async () => {
  if (gatewayLoading.value) return;
  gatewayLoading.value = true;
  try {
    const res: any = await api.get('/devices/gateways');
    gateways.value = res;
  } catch (_) {
  } finally {
    gatewayLoading.value = false;
  }
};

const handleMainTabChange = (tab: string) => {
  if (tab === 'gateways' && gateways.value.length === 0) {
    fetchGateways();
  }
};

const handleTypeChange = () => {
  currentPage.value = 1;
  fetchDevices();
};

const handlePageSizeChange = () => {
  currentPage.value = 1;
  fetchDevices();
};

const openDeviceDetail = (row: any) => {
  selectedDevice.value = row;
  selectedGateway.value = null;
  detailTitle.value = `设备详情 — ${row.name}`;
  detailVisible.value = true;
};

const openGatewayDetail = (row: any) => {
  selectedGateway.value = row;
  selectedDevice.value = null;
  detailTitle.value = `网关详情 — ${row.name}`;
  detailVisible.value = true;
};

onMounted(() => {
  fetchDeviceTypes();
  fetchDevices();
  fetchGateways();
});
</script>

<style scoped>
.devices-container {
  padding: 10px;
}
.main-card {
  min-height: calc(100vh - 80px);
}
.tab-badge {
  margin-left: 6px;
  vertical-align: middle;
}
.type-tabs {
  margin-bottom: 12px;
}
.type-count {
  font-size: 11px;
  color: #909399;
  margin-left: 2px;
}
.device-table {
  width: 100%;
  cursor: pointer;
}
.pagination-bar {
  display: flex;
  justify-content: flex-end;
  padding: 14px 0 4px;
}
.status-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}
.status-dot.green {
  background-color: #67c23a;
  box-shadow: 0 0 5px #67c23a;
}
.status-dot.red {
  background-color: #f56c6c;
  box-shadow: 0 0 5px #f56c6c;
}
</style>

<template>
  <div class="mqtt-container">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 监控 -->
      <el-tab-pane :label="$t('mqtt.monitor')" name="monitor">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="box-card">
              <template #header>
                <div class="card-header">
                  <span><el-icon><DataLine /></el-icon> {{ $t('mqtt.traffic') }}</span>
                  <el-tag size="small" type="info">{{ $t('mqtt.autoRefresh') }}</el-tag>
                </div>
              </template>
              <div class="traffic-content">
                <div class="rate-item">
                  <span class="label">{{ $t('mqtt.inflow') }}</span>
                  <span class="value">{{ stats.inflowRate?.toFixed(1) }} <small>msg/s</small></span>
                </div>
                <div class="rate-item">
                  <span class="label">{{ $t('mqtt.outflow') }}</span>
                  <span class="value">{{ stats.outflowRate?.toFixed(1) }} <small>msg/s</small></span>
                </div>
                <el-divider />
                <div class="stat-grid">
                  <div class="stat-item">
                    <span class="stat-value">{{ stats.totalConnections }}</span>
                    <span class="stat-label">{{ $t('mqtt.connections') }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">{{ stats.nodeCount }}</span>
                    <span class="stat-label">{{ $t('mqtt.nodes') }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">{{ stats.bridges }}</span>
                    <span class="stat-label">{{ $t('mqtt.bridgeCount') }}</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>

          <el-col :span="16">
            <el-card class="box-card">
              <template #header>
                <div class="card-header">
                  <span><el-icon><Connection /></el-icon> {{ $t('mqtt.bridgeStatus') }}</span>
                  <el-button size="small" :loading="rebuilding" @click="handleRebuildBridges">
                    {{ $t('mqtt.rebuildBridges') }}
                  </el-button>
                </div>
              </template>
              <el-table :data="bridgeDetails" size="small" border>
                <el-table-column prop="name" :label="$t('mqtt.bridgeName')" width="240" />
                <el-table-column :label="$t('mqtt.bridgeDirection')" width="80" align="center">
                  <template #default="{ row }">
                    <el-tag v-if="row.egress" size="small" type="warning">↑ {{ $t('mqtt.egress') }}</el-tag>
                    <el-tag v-if="row.ingress" size="small" type="primary">↓ {{ $t('mqtt.ingress') }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column :label="$t('mqtt.bridgeRoute')" min-width="200">
                  <template #default="{ row }">
                    <template v-if="row.egress">
                      <span class="route-text">{{ row.egress.source }}</span>
                      <el-icon class="route-arrow"><Right /></el-icon>
                      <span class="route-text route-remote">{{ row.egress.target }}</span>
                    </template>
                    <template v-if="row.ingress">
                      <span class="route-text route-remote">{{ row.ingress.source }}</span>
                      <el-icon class="route-arrow"><Right /></el-icon>
                      <span class="route-text">{{ row.ingress.target }}</span>
                    </template>
                  </template>
                </el-table-column>
                <el-table-column :label="$t('mqtt.status')" width="110" align="center">
                  <template #default="{ row }">
                    <el-tag size="small" :type="row.status === 'connected' ? 'success' : 'danger'">
                      {{ row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column :label="$t('common.actions')" width="100" align="center">
                  <template #default="{ row }">
                    <el-switch
                      :model-value="row.enable"
                      size="small"
                      :loading="bridgeToggling.has(row.name)"
                      @change="(val: boolean) => handleToggleBridge(row, val)"
                    />
                  </template>
                </el-table-column>
                <el-table-column :label="$t('mqtt.bridgeMetrics')" min-width="160">
                  <template #default="{ row }">
                    <template v-if="row.metrics">
                      <div class="metrics-inline">
                        <span :title="$t('mqtt.metricSuccess')">发:{{ row.metrics.success }}</span>
                        <span :title="$t('mqtt.metricFailed')" class="metric-warn">败:{{ row.metrics.failed }}</span>
                      </div>
                    </template>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" class="mt-20">
          <el-col :span="24">
            <el-card class="box-card">
              <template #header>
                <div class="card-header">
                  <span><el-icon><User /></el-icon> {{ $t('mqtt.connectedClients') }}</span>
                  <span class="header-count">{{ clients.length }} {{ $t('mqtt.online') }}</span>
                </div>
              </template>
              <el-table :data="clients" size="small" border max-height="300">
                <el-table-column prop="clientid" label="Client ID" min-width="200" />
                <el-table-column :label="$t('mqtt.source')" width="180">
                  <template #default="{ row }">
                    <el-tag v-if="row.sourceRole" size="small" type="primary">{{ row.sourceRole }}</el-tag>
                    <span v-else-if="row.source" class="source-text">{{ row.source }}</span>
                    <span v-else class="source-unknown">—</span>
                  </template>
                </el-table-column>
                <el-table-column prop="username" label="Username" width="120" />
                <el-table-column prop="ipAddress" label="IP" width="140" />
                <el-table-column prop="protocol" label="Protocol" width="80" />
                <el-table-column prop="subscriptions" :label="$t('mqtt.subscriptions')" width="100" align="center" />
                <el-table-column :label="$t('mqtt.connected')" width="100" align="center">
                  <template #default="{ row }">
                    <el-tag size="small" :type="row.connected ? 'success' : 'info'">
                      {{ row.connected ? $t('mqtt.online') : $t('mqtt.offline') }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column :label="$t('common.actions')" width="90" align="center">
                  <template #default="{ row }">
                    <el-popconfirm :title="$t('mqtt.kickConfirm')" @confirm="handleKick(row.clientid)">
                      <template #reference>
                        <el-button size="small" type="danger" text>{{ $t('mqtt.kick') }}</el-button>
                      </template>
                    </el-popconfirm>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- Tab 2: 主题订阅 -->
      <el-tab-pane :label="$t('mqtt.topicManage')" name="topics">
        <!-- 云端订阅（bridge ingress） -->
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card class="box-card cloud-sub-card">
              <template #header>
                <div class="card-header">
                  <span><el-icon><Download /></el-icon> {{ $t('mqtt.cloudSubscription') }}</span>
                  <el-tag v-if="cloudSubs.length === 0" size="small" type="info">{{ $t('mqtt.noCloudSubscription') }}</el-tag>
                </div>
              </template>
              <div v-if="cloudSubs.length === 0" class="cloud-sub-hint">{{ $t('mqtt.cloudSubHint') }}</div>
              <div v-for="cs in cloudSubs" :key="cs.bridgeName">
                <div class="cloud-sub-item">
                  <div class="cloud-sub-row">
                    <span class="label">{{ $t('mqtt.cloudTopic') }}</span>
                    <code>{{ cs.remoteTopic }}</code>
                    <el-tag size="small" :type="cs.status === 'connected' ? 'success' : 'danger'">{{ cs.status }}</el-tag>
                  </div>
                  <div class="cloud-sub-row">
                    <span class="label">{{ $t('mqtt.bridgeServer') }}</span>
                    <code>{{ cs.server || '—' }}</code>
                    <span v-if="cs.statusReason" class="status-reason">{{ cs.statusReason }}</span>
                  </div>
                  <div class="cloud-sub-row">
                    <span class="label">{{ $t('mqtt.messages') }}</span>
                    <span class="metric-val">{{ $t('mqtt.msgReceived') }}: {{ cs.received || 0 }}</span>
                  </div>
                </div>
                <div class="bridge-log">
                  <div class="bridge-log-head">
                    <span class="bridge-log-title">{{ $t('mqtt.bridgeLiveLog') }}</span>
                    <span v-if="logView(cs.bridgeName).counters" class="bridge-log-counters">
                      <span :title="$t('mqtt.metricSuccess')">{{ $t('mqtt.msgSuccess') }} {{ logView(cs.bridgeName).counters.success }}</span>
                      <span :title="$t('mqtt.metricFailed')" class="metric-warn">{{ $t('mqtt.metricFailed') }} {{ logView(cs.bridgeName).counters.failed }}</span>
                    </span>
                  </div>
                  <div
                    v-if="logView(cs.bridgeName).events.length || logView(cs.bridgeName).messages.length"
                    class="bridge-log-list"
                  >
                    <div v-for="(ev, i) in logView(cs.bridgeName).events" :key="'e' + i" class="log-line">
                      <span class="log-time">{{ formatTime(ev.ts) }}</span>
                      <el-tag size="small" :type="ev.status === 'connected' ? 'success' : 'danger'">{{ ev.status }}</el-tag>
                      <span v-if="ev.status === 'deleted'" class="log-reason">{{ $t('mqtt.bridgeRemoved') }}</span>
                      <span v-else-if="ev.reason" class="log-reason">{{ ev.reason }}</span>
                    </div>
                    <div v-for="(m, i) in logView(cs.bridgeName).messages.slice(0, 20)" :key="'m' + i" class="log-line log-msg">
                      <span class="log-time">{{ formatTime(m.ts) }}</span>
                      <el-tag size="small" :type="m.direction === 'out' ? 'warning' : 'primary'">
                        {{ m.direction === 'out' ? $t('mqtt.bridgeMsgOut') : $t('mqtt.bridgeMsgIn') }}
                      </el-tag>
                      <code class="log-topic">{{ m.topic }}</code>
                      <span class="log-payload">{{ m.payload }}</span>
                    </div>
                  </div>
                  <div v-else class="log-empty">{{ $t('mqtt.bridgeNoLog') }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 云端转发（bridge egress） -->
        <el-row :gutter="20" class="mt-20">
          <el-col :span="24">
            <el-card class="box-card egress-sub-card">
              <template #header>
                <div class="card-header">
                  <span><el-icon><Upload /></el-icon> {{ $t('mqtt.cloudEgress') }}</span>
                  <el-tag v-if="egressBridges.length === 0" size="small" type="info">{{ $t('mqtt.noCloudEgress') }}</el-tag>
                </div>
              </template>
              <div v-if="egressBridges.length === 0" class="cloud-sub-hint">{{ $t('mqtt.egressHint') }}</div>
              <div v-for="eb in egressBridges" :key="eb.bridgeName">
                <div class="cloud-sub-item">
                  <div class="cloud-sub-row">
                    <span class="label">{{ $t('mqtt.egressTopic') }}</span>
                    <code>{{ eb.localTopic }}</code>
                    <el-tag size="small" :type="eb.status === 'connected' ? 'success' : 'danger'">{{ eb.status }}</el-tag>
                  </div>
                  <div class="cloud-sub-row">
                    <span class="label">{{ $t('mqtt.bridgeServer') }}</span>
                    <code>{{ eb.server || '—' }}</code>
                    <span v-if="eb.statusReason" class="status-reason">{{ eb.statusReason }}</span>
                  </div>
                  <div class="cloud-sub-row">
                    <span class="label">{{ $t('mqtt.messages') }}</span>
                    <span class="metric-val">{{ $t('mqtt.msgSuccess') }}: {{ eb.success || 0 }}</span>
                    <span class="metric-val">{{ $t('mqtt.metricFailed') }}: {{ eb.failed || 0 }}</span>
                  </div>
                </div>
                <div class="bridge-log">
                  <div class="bridge-log-head">
                    <span class="bridge-log-title">{{ $t('mqtt.bridgeLiveLog') }}</span>
                    <span v-if="logView(eb.bridgeName).counters" class="bridge-log-counters">
                      <span :title="$t('mqtt.metricSuccess')">{{ $t('mqtt.msgSuccess') }} {{ logView(eb.bridgeName).counters.success }}</span>
                      <span :title="$t('mqtt.metricFailed')" class="metric-warn">{{ $t('mqtt.metricFailed') }} {{ logView(eb.bridgeName).counters.failed }}</span>
                    </span>
                  </div>
                  <div
                    v-if="logView(eb.bridgeName).events.length || logView(eb.bridgeName).messages.length"
                    class="bridge-log-list"
                  >
                    <div v-for="(ev, i) in logView(eb.bridgeName).events" :key="'e' + i" class="log-line">
                      <span class="log-time">{{ formatTime(ev.ts) }}</span>
                      <el-tag size="small" :type="ev.status === 'connected' ? 'success' : 'danger'">{{ ev.status }}</el-tag>
                      <span v-if="ev.status === 'deleted'" class="log-reason">{{ $t('mqtt.bridgeRemoved') }}</span>
                      <span v-else-if="ev.reason" class="log-reason">{{ ev.reason }}</span>
                    </div>
                    <div v-for="(m, i) in logView(eb.bridgeName).messages.slice(0, 20)" :key="'m' + i" class="log-line log-msg">
                      <span class="log-time">{{ formatTime(m.ts) }}</span>
                      <el-tag size="small" :type="m.direction === 'out' ? 'warning' : 'primary'">
                        {{ m.direction === 'out' ? $t('mqtt.bridgeMsgOut') : $t('mqtt.bridgeMsgIn') }}
                      </el-tag>
                      <code class="log-topic">{{ m.topic }}</code>
                      <span class="log-payload">{{ m.payload }}</span>
                    </div>
                  </div>
                  <div v-else class="log-empty">{{ $t('mqtt.bridgeNoLog') }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" class="mt-20">
          <el-col :span="24">
            <el-card class="box-card">
              <template #header>
                <div class="card-header">
                  <span><el-icon><MagicStick /></el-icon> {{ $t('mqtt.activeTopics') }}</span>
                  <div class="header-actions">
                    <span class="header-count">{{ filteredTopics.length }} {{ $t('mqtt.bridgeTopics') }}</span>
                    <el-button size="small" @click="() => { fetchCloudSubs(); fetchEgress(); }"><el-icon><Refresh /></el-icon></el-button>
                  </div>
                </div>
              </template>
              <el-table :data="filteredTopics" size="small" border max-height="400">
                <el-table-column prop="topic" label="Topic" min-width="400" />
                <el-table-column :label="$t('mqtt.messageCount')" width="120" align="center">
                  <template #default="{ row }">
                    <el-tag size="small" type="success">{{ row.msgCount }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column :label="$t('mqtt.bridgeDirection')" width="80" align="center">
                  <template #default="{ row }">
                    <el-tag v-if="row.direction === 'ingress'" size="small" type="primary">↓ {{ $t('mqtt.ingress') }}</el-tag>
                    <el-tag v-if="row.direction === 'egress'" size="small" type="warning">↑ {{ $t('mqtt.egress') }}</el-tag>
                    <el-tag v-if="row.direction === 'both'" size="small" type="success">↓↑ Both</el-tag>
                  </template>
                </el-table-column>
                <el-table-column :label="$t('common.actions')" width="100" align="center">
                  <template #default="{ row }">
                    <el-button size="small" type="primary" text @click="openMessageViewer(row.topic)">
                      <el-icon><View /></el-icon> {{ $t('mqtt.viewMessages') }}
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

    </el-tabs>

    <!-- 消息查看器 Dialog -->
    <el-dialog
      v-model="msgViewer.visible"
      :title="$t('mqtt.msgViewerTitle', { topic: msgViewer.topic })"
      width="800px"
      :close-on-click-modal="false"
      @close="closeMessageViewer"
    >
      <div class="msg-viewer-toolbar">
        <el-tag size="small" :type="msgViewer.connected ? 'success' : 'danger'">
          {{ msgViewer.connected ? $t('mqtt.msgStreaming') : $t('mqtt.msgDisconnected') }}
        </el-tag>
        <span class="msg-count">{{ $t('mqtt.msgCount', { count: msgViewer.messages.length }) }}</span>
        <el-button size="small" @click="msgViewer.messages = []" :disabled="msgViewer.messages.length === 0">
          <el-icon><Delete /></el-icon> {{ $t('mqtt.clearMsgs') }}
        </el-button>
      </div>
      <div class="msg-viewer-list" ref="msgListRef">
        <div v-if="msgViewer.messages.length === 0" class="empty-hint">
          {{ msgViewer.connected ? $t('mqtt.waitingMsgs') : $t('mqtt.noMessages') }}
        </div>
        <div v-for="(m, i) in msgViewer.messages" :key="i" class="msg-item">
          <div class="msg-item-header">
            <span class="msg-time">{{ formatTime(m.timestamp) }}</span>
          </div>
          <pre class="msg-payload">{{ formatPayload(m.payload) }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import {
  DataLine, Connection, MagicStick, User, Refresh,
  Right, Download, Upload, View, Delete,
} from '@element-plus/icons-vue';
import api from '../api';

const activeTab = ref('monitor');

// Stats
const stats = ref<any>({ inflowRate: 0, outflowRate: 0, totalConnections: 0, nodeCount: 0, bridges: 0 });
const bridgeDetails = ref<any[]>([]);
const clients = ref<any[]>([]);

// Cloud subscription (bridge ingress remote topic)
const cloudSubs = ref<any[]>([]);

// Cloud egress (bridge egress local topic → cloud)
const egressBridges = ref<any[]>([]);

// Per-bridge live logs (SSE snapshot, keyed by bridge name)
const bridgeLogs = ref<Record<string, any>>({});
let bridgeLogAbort: AbortController | null = null;

const logView = (name: string) => {
  const log = bridgeLogs.value[name];
  if (!log) return { counters: null, events: [] as any[], messages: [] as any[] };
  return {
    counters: log.counters || null,
    events: [...(log.events || [])].reverse(),
    messages: [...(log.messages || [])].reverse(),
  };
};

const startBridgeLogStream = async () => {
  bridgeLogAbort = new AbortController();
  const token = localStorage.getItem('token');
  try {
    const res = await fetch('/api/mqtt/bridges/logs/stream', {
      headers: { Authorization: `Bearer ${token}` },
      signal: bridgeLogAbort.signal,
    });
    if (!res.ok) return;
    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            const map: Record<string, any> = {};
            for (const b of data.bridges || []) map[b.name] = b;
            bridgeLogs.value = map;
          } catch { /* parse error, skip */ }
        }
      }
    }
  } catch { /* abort or network error */ }
};

const stopBridgeLogStream = () => {
  if (bridgeLogAbort) {
    bridgeLogAbort.abort();
    bridgeLogAbort = null;
  }
};

const fetchEgress = async () => {
  try {
    egressBridges.value = await api.get('/mqtt/cloud-egress');
  } catch (e) { /* silent */ }
};

const filteredTopics = computed(() => {
  const rows: any[] = [];

  // Cloud subscription (ingress) — show bridge pattern with message counts
  for (const cs of cloudSubs.value) {
    if (!cs.remoteTopic) continue;
    rows.push({
      topic: cs.remoteTopic,
      msgCount: cs.received || 0,
      direction: 'ingress',
    });
  }

  // Cloud egress — show bridge pattern with message counts
  for (const eb of egressBridges.value) {
    if (!eb.localTopic) continue;
    rows.push({
      topic: eb.localTopic,
      msgCount: eb.success || 0,
      direction: 'egress',
    });
  }

  return rows;
});

// Message viewer
const MAX_CACHED_MSGS = 50;
const messageCache = new Map<string, { topic?: string; timestamp: number; payload: string }[]>();
const msgListRef = ref<HTMLElement | null>(null);
const msgViewer = ref({
  visible: false,
  topic: '',
  connected: false,
  messages: [] as { topic?: string; timestamp: number; payload: string }[],
});
let msgAbortController: AbortController | null = null;

const openMessageViewer = async (topic: string) => {
  const cached = messageCache.get(topic) || [];
  msgViewer.value = { visible: true, topic, connected: false, messages: [...cached] };
  await nextTick();
  startMessageStream(topic);
};

const closeMessageViewer = () => {
  stopMessageStream();
  msgViewer.value.visible = false;
};

const startMessageStream = async (topic: string) => {
  stopMessageStream();
  msgAbortController = new AbortController();
  const token = localStorage.getItem('token');
  try {
    const res = await fetch(`/api/mqtt/topics/messages?topic=${encodeURIComponent(topic)}`, {
      headers: { Authorization: `Bearer ${token}` },
      signal: msgAbortController.signal,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    msgViewer.value.connected = true;
    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.type === 'ready') continue; // skip heartbeat/ready events
            const msg = { topic: data.topic, timestamp: data.timestamp, payload: data.payload };
            msgViewer.value.messages.push(msg);
            // Write to topic cache
            if (!messageCache.has(msgViewer.value.topic)) messageCache.set(msgViewer.value.topic, []);
            const cache = messageCache.get(msgViewer.value.topic)!;
            cache.push(msg);
            if (cache.length > MAX_CACHED_MSGS) cache.shift();
            if (msgViewer.value.messages.length > 200) msgViewer.value.messages.shift();
            nextTick(() => {
              if (msgListRef.value) msgListRef.value.scrollTop = msgListRef.value.scrollHeight;
            });
          } catch { /* parse error, skip */ }
        }
      }
    }
  } catch (e: any) {
    if (e.name !== 'AbortError') {
      msgViewer.value.connected = false;
    }
  }
};

const stopMessageStream = () => {
  if (msgAbortController) {
    msgAbortController.abort();
    msgAbortController = null;
  }
  msgViewer.value.connected = false;
};

const formatTime = (ts: number) => {
  const d = new Date(ts);
  return d.toLocaleTimeString() + '.' + String(d.getMilliseconds()).padStart(3, '0');
};

const formatPayload = (payload: string) => {
  try {
    return JSON.stringify(JSON.parse(payload), null, 2);
  } catch {
    return payload;
  }
};

const bridgeToggling = ref(new Set<string>());

const handleToggleBridge = async (row: any, enable: boolean) => {
  bridgeToggling.value.add(row.name);
  try {
    await api.put('/mqtt/bridges/enable', { type: row.type, name: row.name, enable });
    ElMessage.success(enable ? `桥接 ${row.name} 已启用` : `桥接 ${row.name} 已停用`);
    // 立即刷新状态
    fetchAll();
  } catch (e: any) {
    ElMessage.error(e?.message || '操作失败');
  } finally {
    bridgeToggling.value.delete(row.name);
  }
};

let timer: ReturnType<typeof setInterval> | null = null;

const fetchAll = async () => {
  try {
    const [s, b, c]: any = await Promise.all([
      api.get('/mqtt/stats'),
      api.get('/mqtt/bridges/detail'),
      api.get('/mqtt/clients'),
    ]);
    stats.value = s;
    bridgeDetails.value = b;
    clients.value = c;
  } catch (e) { /* silent */ }
};

const fetchCloudSubs = async () => {
  try {
    cloudSubs.value = await api.get('/mqtt/cloud-subscription');
  } catch (e) { /* silent */ }
};

const { t } = useI18n();
const rebuilding = ref(false);

const handleRebuildBridges = async () => {
  rebuilding.value = true;
  try {
    await api.post('/platform/rebuild-bridges');
    ElMessage.success(t('mqtt.rebuildBridgesDone'));
    setTimeout(() => { fetchAll(); fetchCloudSubs(); fetchEgress(); }, 3000);
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || t('mqtt.rebuildBridgesFailed'));
  } finally {
    rebuilding.value = false;
  }
};

const handleKick = async (clientid: string) => {
  try {
    await api.delete(`/mqtt/clients/${encodeURIComponent(clientid)}`);
    ElMessage.success(`${clientid} kicked`);
    fetchAll();
  } catch (e: any) {
    ElMessage.error(e?.message || 'Failed');
  }
};

onMounted(() => {
  fetchAll();
  fetchCloudSubs();
  fetchEgress();
  startBridgeLogStream();
  timer = setInterval(() => { fetchAll(); fetchCloudSubs(); fetchEgress(); }, 5000);
});

onUnmounted(() => {
  if (timer) { clearInterval(timer); timer = null; }
  stopBridgeLogStream();
  stopMessageStream();
});
</script>

<style scoped>
.mqtt-container { padding: 10px; }
.box-card { margin-bottom: 0; height: 100%; }
.mt-20 { margin-top: 20px; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.card-header > span { display: flex; align-items: center; gap: 8px; font-weight: bold; }
.header-count { font-size: 12px; color: #909399; font-weight: normal; }
.traffic-content { padding: 10px 0; }
.rate-item { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.rate-item .label { color: #909399; font-size: 14px; }
.rate-item .value { font-size: 22px; font-weight: bold; color: var(--el-color-primary); }
.rate-item .value small { font-size: 12px; font-weight: normal; color: #909399; }
.stat-grid { display: flex; gap: 12px; }
.stat-item { flex: 1; text-align: center; }
.stat-value { display: block; font-size: 20px; font-weight: bold; color: var(--el-color-primary); }
.stat-label { display: block; font-size: 12px; color: #909399; margin-top: 2px; }
.route-text { font-family: monospace; font-size: 12px; padding: 2px 6px; background: #f5f7fa; border-radius: 3px; }
.route-remote { color: var(--el-color-warning); }
.route-arrow { margin: 0 4px; color: #909399; }
.metrics-inline { display: flex; gap: 10px; font-size: 12px; font-family: monospace; }
.metrics-inline span { padding: 1px 4px; background: #f5f7fa; border-radius: 2px; }
.metric-warn { color: var(--el-color-warning); }
.empty-hint { text-align: center; color: #c0c4cc; padding: 40px 0; }
.source-text { color: #606266; font-size: 12px; }
.source-unknown { color: #c0c4cc; }
.cloud-sub-card { border-left: 3px solid var(--el-color-primary); margin-bottom: 0; }
.cloud-sub-item { display: flex; align-items: center; justify-content: space-between; padding: 4px 0; }
.cloud-sub-row { display: flex; align-items: center; gap: 12px; }
.cloud-sub-row .label { color: #909399; font-size: 13px; }
.cloud-sub-row code { font-family: monospace; font-size: 13px; padding: 3px 8px; background: #f0f9eb; border-radius: 4px; color: var(--el-color-primary); }
.cloud-sub-hint { font-size: 12px; color: #909399; margin-left: 8px; }
.status-reason { font-size: 12px; color: #e6a23c; font-family: monospace; }
.metric-val { font-size: 12px; color: #606266; font-family: monospace; margin-right: 12px; }

/* Bridge live log */
.bridge-log { margin-top: 6px; border: 1px solid #ebeef5; border-radius: 4px; background: #fafafa; overflow: hidden; }
.bridge-log-head { display: flex; align-items: center; justify-content: space-between; padding: 4px 10px; background: #f5f7fa; border-bottom: 1px solid #ebeef5; }
.bridge-log-title { font-size: 12px; font-weight: bold; color: #606266; }
.bridge-log-counters { display: flex; gap: 10px; font-size: 11px; font-family: monospace; color: #606266; }
.bridge-log-counters .metric-warn { color: var(--el-color-warning); }
.bridge-log-list { max-height: 220px; overflow-y: auto; padding: 4px 10px; }
.log-line { display: flex; align-items: center; gap: 8px; padding: 3px 0; border-bottom: 1px dashed #ebeef5; font-size: 12px; }
.log-line:last-child { border-bottom: none; }
.log-time { color: #909399; font-family: monospace; font-size: 11px; white-space: nowrap; }
.log-reason { color: #e6a23c; font-family: monospace; font-size: 11px; }
.log-topic { font-family: monospace; font-size: 11px; padding: 1px 6px; background: #f0f9eb; border-radius: 3px; color: var(--el-color-primary); white-space: nowrap; }
.log-payload { color: #606266; font-family: monospace; font-size: 11px; word-break: break-all; }
.log-empty { text-align: center; color: #c0c4cc; font-size: 12px; padding: 10px 0; }

/* Message viewer */
.msg-viewer-toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.msg-count { font-size: 12px; color: #909399; }
.msg-viewer-list { max-height: 480px; overflow-y: auto; border: 1px solid #ebeef5; border-radius: 4px; padding: 8px; background: #fafafa; }
.msg-item { margin-bottom: 8px; background: #fff; border-radius: 4px; border: 1px solid #ebeef5; overflow: hidden; }
.msg-item-header { display: flex; align-items: center; padding: 4px 8px; background: #f5f7fa; border-bottom: 1px solid #ebeef5; }
.msg-time { font-size: 11px; color: #909399; font-family: monospace; }
.msg-payload { margin: 0; padding: 8px; font-size: 12px; font-family: monospace; white-space: pre-wrap; word-break: break-all; max-height: 300px; overflow-y: auto; }

.header-actions { display: flex; align-items: center; gap: 12px; }
.header-count { font-size: 12px; color: #909399; }
</style>

<template>
  <div class="db-container">

    <!-- Header bar -->
    <div class="page-header">
      <span class="page-title">数据库服务</span>
      <div class="header-actions">
        <el-switch
          v-model="autoRefresh"
          active-text="自动刷新 30s"
          inactive-text=""
          @change="toggleAutoRefresh"
        />
        <el-button :icon="Refresh" :loading="loading" @click="fetchStatus" style="margin-left:12px">
          刷新
        </el-button>
      </div>
    </div>

    <div v-loading="loading && !status" class="content-grid">

      <!-- ── 连接状态卡片 ─────────────────────────────────── -->
      <el-row :gutter="16" class="row-gap">

        <!-- 本地影子库 -->
        <el-col :span="12">
          <el-card shadow="never" class="status-card">
            <template #header>
              <div class="card-header">
                <span>本地影子库</span>
                <el-tag :type="localConnected ? 'success' : 'danger'" size="small">
                  {{ localConnected ? '已连接' : '连接失败' }}
                </el-tag>
              </div>
            </template>
            <el-descriptions :column="2" size="small" border v-if="status">
              <el-descriptions-item label="主机">
                {{ status.localPg.host }}:{{ status.localPg.port }}
              </el-descriptions-item>
              <el-descriptions-item label="数据库">
                {{ status.localPg.database }}
              </el-descriptions-item>
              <el-descriptions-item label="用户">
                {{ status.localPg.user }}
              </el-descriptions-item>
              <el-descriptions-item label="设备 / 网关">
                {{ deviceCount }} / {{ gatewayCount }}
              </el-descriptions-item>
            </el-descriptions>
            <div v-if="status?.localPg?.error" class="error-text">{{ status.localPg.error }}</div>
          </el-card>
        </el-col>

        <!-- 云端主库 -->
        <el-col :span="12">
          <el-card shadow="never" class="status-card">
            <template #header>
              <div class="card-header">
                <span>云端主库（{{ isAppSync ? '应用层同步' : '复制源' }}）</span>
                <el-tag :type="cloudConnected ? 'success' : 'danger'" size="small">
                  {{ cloudConnected ? (isAppSync ? '同步正常' : '已连接') : (isAppSync ? '同步异常' : '无法连接') }}
                </el-tag>
              </div>
            </template>
            <!-- app_sync：outbox 拉取工作器状态 -->
            <el-descriptions :column="2" size="small" border v-if="status && isAppSync">
              <el-descriptions-item label="同步模式">
                <el-tag size="small" type="primary">应用层同步（outbox 拉取）</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="工作器">
                {{ status.cloudPg.running ? '运行中' : '已停止' }}
              </el-descriptions-item>
              <el-descriptions-item label="平台" :span="2">
                {{ status.cloudPg.platform?.url || '—' }}
              </el-descriptions-item>
              <el-descriptions-item label="空间">
                {{ status.cloudPg.platform?.spaceCode || '—' }}
              </el-descriptions-item>
              <el-descriptions-item label="游标 / 云端最新">
                {{ status.cloudPg.cursor ?? '—' }} / {{ status.cloudPg.cloudHi ?? '—' }}
              </el-descriptions-item>
              <el-descriptions-item label="滞后">
                <span :class="syncLagClass">{{ syncLagLabel }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="最后拉取">
                {{ formatTime(status.cloudPg.lastPullAt) }}
              </el-descriptions-item>
              <el-descriptions-item label="累计应用">
                {{ status.cloudPg.appliedTotal ?? 0 }} 条
              </el-descriptions-item>
            </el-descriptions>
            <!-- pg_logical：复制槽状态 -->
            <el-descriptions :column="2" size="small" border v-else-if="status">
              <el-descriptions-item label="主机">
                {{ status.cloudPg.host }}:{{ status.cloudPg.port }}
              </el-descriptions-item>
              <el-descriptions-item label="复制用户">
                {{ status.cloudPg.user }}
              </el-descriptions-item>
              <el-descriptions-item label="Publication">
                {{ status.cloudPg.publication || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="Slot 状态" v-if="status.cloudPg.slot">
                <span :class="status.cloudPg.slot.active ? 'tag-green' : 'tag-red'">
                  {{ status.cloudPg.slot.active ? '活跃' : '不活跃' }}
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="WAL Lag" v-if="status.cloudPg.slot" :span="2">
                <span :class="lagClass">{{ lagLabel }}</span>
              </el-descriptions-item>
            </el-descriptions>
            <div v-if="status?.cloudPg?.error" class="error-text">{{ status.cloudPg.error }}</div>
            <div v-if="status?.cloudPg?.lastError" class="error-text">
              最近错误：{{ status.cloudPg.lastError }}
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- ── 逻辑订阅（pg_logical）/ 同步工作器（app_sync） ──── -->
      <el-card shadow="never" class="row-gap">
        <template #header>
          <div class="card-header">
            <span>{{ isAppSync ? '同步工作器' : '逻辑订阅' }}</span>
            <el-button
              v-if="!isAppSync"
              type="warning"
              size="small"
              :loading="repairing"
              @click="handleRepair"
            >
              修复订阅
            </el-button>
          </div>
        </template>

        <template v-if="isAppSync">
          <el-descriptions :column="4" size="small" border>
            <el-descriptions-item label="工作器状态">
              <el-tag :type="status?.cloudPg?.running ? 'success' : 'danger'" size="small">
                {{ status?.cloudPg?.running ? '运行中' : '已停止' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="启动时间">
              {{ formatTime(status?.cloudPg?.startedAt) }}
            </el-descriptions-item>
            <el-descriptions-item label="拉取间隔">
              5 秒
            </el-descriptions-item>
            <el-descriptions-item label="检查时间">
              {{ formatTime(status?.checkedAt) }}
            </el-descriptions-item>
          </el-descriptions>
        </template>

        <template v-else-if="status?.localPg?.subscription">
          <el-descriptions :column="4" size="small" border>
            <el-descriptions-item label="订阅名">
              {{ status.localPg.subscription.name }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="status.localPg.subscription.enabled ? 'success' : 'danger'" size="small">
                {{ status.localPg.subscription.enabled ? '启用' : '已禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Slot">
              {{ status.localPg.subscription.slotName }}
            </el-descriptions-item>
            <el-descriptions-item label="检查时间">
              {{ formatTime(status.checkedAt) }}
            </el-descriptions-item>
          </el-descriptions>
        </template>
        <el-empty v-else description="未找到订阅 platform_sub" :image-size="48" />
      </el-card>

      <!-- ── 表同步状态 ─────────────────────────────────────── -->
      <el-card shadow="never" class="row-gap">
        <template #header>
          <div class="card-header">
            <span>
              表同步状态
              <el-tag
                :type="allReady ? 'success' : 'warning'"
                size="small"
                style="margin-left:8px"
              >
                {{ status?.localPg?.readyCount ?? 0 }} / {{ status?.localPg?.totalCount ?? 11 }}
                {{ isAppSync ? '已同步' : '就绪' }}
              </el-tag>
            </span>
          </div>
        </template>

        <el-table
          :data="status?.localPg?.tables ?? []"
          size="small"
          border
          class="sync-table"
        >
          <el-table-column prop="name" label="表名" width="180" />
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <el-tag :type="stateType(row.state)" size="small">
                {{ row.stateLabel }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="rowCount" label="行数" width="100" align="right">
            <template #default="{ row }">
              {{ row.rowCount < 0 ? '—' : row.rowCount.toLocaleString() }}
            </template>
          </el-table-column>
          <el-table-column
            v-if="!isAppSync"
            prop="lsn"
            label="LSN 位置"
            min-width="160"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <span class="lsn-text">{{ row.lsn ?? '—' }}</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { Refresh } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import api from '../api';

const loading = ref(false);
const repairing = ref(false);
const autoRefresh = ref(false);
const status = ref<any>(null);
let timer: ReturnType<typeof setInterval> | null = null;

const localConnected = computed(() => status.value?.localPg?.connected === true);
const cloudConnected = computed(() => status.value?.cloudPg?.connected === true);
const isAppSync = computed(() => status.value?.syncMode === 'app_sync');
const allReady = computed(() => {
  const s = status.value?.localPg;
  return s && s.readyCount === s.totalCount;
});

const deviceCount = computed(() =>
  status.value?.localPg?.tables?.find((t: any) => t.name === 'iot_device')?.rowCount ?? '—',
);
const gatewayCount = computed(() =>
  status.value?.localPg?.tables?.find((t: any) => t.name === 'iot_gateway')?.rowCount ?? '—',
);

const lagClass = computed(() => {
  const lag = status.value?.cloudPg?.slot?.lagBytes ?? 0;
  if (lag === 0) return 'tag-green';
  if (lag < 1024 * 1024) return 'tag-yellow';
  return 'tag-red';
});

const lagLabel = computed(() => {
  const lag = status.value?.cloudPg?.slot?.lagBytes;
  if (lag == null) return '—';
  if (lag === 0) return '0 B（实时）';
  if (lag < 1024) return `${lag} B`;
  if (lag < 1024 * 1024) return `${(lag / 1024).toFixed(1)} KB`;
  return `${(lag / 1024 / 1024).toFixed(1)} MB`;
});

// app_sync 滞后 = 云端最新 seq 与本地游标之差（outbox 记录条数）
const syncLagClass = computed(() => {
  const lag = status.value?.cloudPg?.lag;
  if (lag == null || lag <= 0) return 'tag-green';
  if (lag < 10) return 'tag-yellow';
  return 'tag-red';
});

const syncLagLabel = computed(() => {
  const lag = status.value?.cloudPg?.lag;
  if (lag == null) return '—';
  if (lag <= 0) return '0（实时）';
  return `${lag} 条`;
});

const stateType = (state: string) => {
  const map: Record<string, string> = { r: 'success', d: 'warning', s: 'primary', i: 'info', 'n/a': 'info' };
  return (map[state] ?? 'danger') as any;
};

const formatTime = (iso: string) =>
  iso ? new Date(iso).toLocaleString('zh-CN') : '-';

const fetchStatus = async () => {
  loading.value = true;
  try {
    status.value = await api.get('/database/status');
  } catch {
    // interceptor shows error
  } finally {
    loading.value = false;
  }
};

const handleRepair = async () => {
  await ElMessageBox.confirm(
    '将检查并重建逻辑订阅，订阅中断期间边端数据库将停止更新。是否继续？',
    '修复订阅',
    { confirmButtonText: '确认修复', cancelButtonText: '取消', type: 'warning' },
  );
  repairing.value = true;
  try {
    await api.post('/database/repair');
    ElMessage.success('修复指令已触发，正在重新建立订阅...');
    setTimeout(fetchStatus, 3000);
  } catch {
    // interceptor shows error
  } finally {
    repairing.value = false;
  }
};

const toggleAutoRefresh = (val: boolean) => {
  if (val) {
    timer = setInterval(fetchStatus, 30000);
  } else {
    if (timer) { clearInterval(timer); timer = null; }
  }
};

onMounted(fetchStatus);
onBeforeUnmount(() => { if (timer) clearInterval(timer); });
</script>

<style scoped>
.db-container {
  padding: 10px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-title {
  font-size: 18px;
  font-weight: 600;
}
.header-actions {
  display: flex;
  align-items: center;
}
.content-grid {
  min-height: 200px;
}
.row-gap {
  margin-bottom: 16px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.status-card {
  height: 100%;
}
.error-text {
  color: var(--el-color-danger);
  font-size: 12px;
  margin-top: 8px;
}
.sync-table {
  width: 100%;
}
.lsn-text {
  font-family: monospace;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.tag-green  { color: #67c23a; font-weight: 600; }
.tag-yellow { color: #e6a23c; font-weight: 600; }
.tag-red    { color: #f56c6c; font-weight: 600; }
</style>

<template>
  <div class="settings-container">
    <!-- 状态总览卡片 -->
    <el-card class="status-card" :class="statusClass">
      <div class="status-header">
        <div class="status-left">
          <el-icon :size="32" class="status-icon"><Connection /></el-icon>
          <div>
            <div class="status-title">{{ $t('settings.platform') }}</div>
            <el-tag :type="statusTagType" size="large" effect="dark">
              {{ statusLabel }}
            </el-tag>
          </div>
        </div>
        <div class="status-meta" v-if="status.connectionStatus === 'ACTIVE'">
          <div class="meta-item">
            <span class="label">空间码</span>
            <span class="value">{{ status.spaceCode }}</span>
          </div>
          <div class="meta-item">
            <span class="label">平台地址</span>
            <span class="value">{{ status.platformUrl }}</span>
          </div>
          <div class="meta-item">
            <span class="label">注册时间</span>
            <span class="value">{{ formatDate(status.registeredAt) }}</span>
          </div>
          <div class="meta-item">
            <span class="label">上次心跳</span>
            <span class="value" :class="{ 'stale': isHeartbeatStale }">
              {{ status.lastHeartbeat ? timeAgo(status.lastHeartbeat) : '—' }}
            </span>
          </div>
        </div>
      </div>

      <!-- ACTIVE 状态的许可信息 -->
      <div v-if="status.connectionStatus === 'ACTIVE' && status.license" class="license-section">
        <el-divider />
        <div class="license-header">
          <span class="license-title">{{ $t('settings.license') }}</span>
          <el-tag :type="licenseTagType" size="small" effect="dark">
            {{ licenseLabel }}
          </el-tag>
        </div>
        <div class="license-body">
          <div class="license-item">
            <span class="license-item-label">{{ $t('settings.licenseDeviceUsage') }}</span>
            <div class="license-progress-wrap">
              <el-progress
                :percentage="licenseUsagePercent"
                :color="licenseBarColor"
                :stroke-width="14"
              />
              <span class="progress-nums">{{ status.license.currentDeviceCount.toLocaleString() }} / {{ status.license.deviceLimit.toLocaleString() }}</span>
            </div>
          </div>
          <div class="license-item">
            <span class="license-item-label">{{ $t('settings.licenseDaysRemaining') }}</span>
            <span class="license-item-value" :class="licenseDaysClass">{{ formatLicenseDays(status.license.daysRemaining) }}</span>
          </div>
        </div>
      </div>

      <!-- ACTIVE 状态的操作按钮 -->
      <div v-if="status.connectionStatus === 'ACTIVE'" class="action-row">
        <el-button @click="doHeartbeat" :loading="heartbeatLoading" plain>
          <el-icon><Refresh /></el-icon> 测试心跳
        </el-button>
        <el-button @click="doRebuildBridges" :loading="rebuildLoading" plain type="success">
          <el-icon><RefreshRight /></el-icon> 重建桥接
        </el-button>
        <el-button type="warning" @click="confirmUnbind" :loading="unbindLoading">
          <el-icon><SwitchButton /></el-icon> 解绑平台
        </el-button>
        <el-button type="danger" plain @click="confirmForceReplace">
          <el-icon><Warning /></el-icon> 强制替换
        </el-button>
      </div>
    </el-card>

    <!-- 注册向导（UNCONFIGURED 状态） -->
    <el-card v-if="status.connectionStatus !== 'ACTIVE'" class="register-card">
      <template #header>
        <span><el-icon><Key /></el-icon> 注册对接平台</span>
      </template>

      <el-steps :active="registerStep" finish-status="success" class="steps">
        <el-step title="填写信息" />
        <el-step title="配置预览" />
        <el-step title="应用完成" />
      </el-steps>

      <!-- Step 0：填写注册信息 -->
      <div v-if="registerStep === 0" class="step-content">
        <el-form :model="registerForm" label-width="140px" label-position="left">
          <el-form-item label="平台地址">
            <el-input v-model="registerForm.platformUrl" placeholder="https://platform.buildingos.com">
              <template #append>
                <el-button @click="doTestConnection" :loading="testLoading">测试</el-button>
              </template>
            </el-input>
            <div v-if="testResult" class="test-result" :class="testResult.reachable ? 'ok' : 'fail'">
              {{ testResult.reachable ? '✓ 平台可达' : '✗ 无法连接: ' + testResult.error }}
            </div>
          </el-form-item>
          <el-form-item label="空间码 (spaceCode)">
            <el-input v-model="registerForm.spaceCode" placeholder="如 CDSD1" />
          </el-form-item>
          <el-form-item label="注册 Token">
            <el-input v-model="registerForm.registrationToken" type="password" show-password
              placeholder="由平台管理员生成的一次性 token" />
          </el-form-item>
          <el-form-item label="本机 IP（可选）">
            <el-input v-model="registerForm.edgeIp" placeholder="自动检测" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="doRegister" :loading="registerLoading"
              :disabled="!registerForm.platformUrl || !registerForm.spaceCode || !registerForm.registrationToken">
              向平台注册
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- Step 1：配置预览 -->
      <div v-if="registerStep === 1" class="step-content">
        <el-alert type="success" show-icon :closable="false" title="注册成功！以下是将要应用的配置，确认后点击「应用配置」" />
        <el-tabs class="preview-tabs">
          <el-tab-pane label="EMQX 桥接">
            <pre class="code-preview">{{ JSON.stringify(preview?.emqxBridge, null, 2) }}</pre>
          </el-tab-pane>
          <el-tab-pane label="PG 影子订阅">
            <pre class="code-preview">{{ JSON.stringify(preview?.pgSubscription, null, 2) }}</pre>
          </el-tab-pane>
          <el-tab-pane v-if="preview?.license" label="许可信息">
            <pre class="code-preview">{{ JSON.stringify(preview?.license, null, 2) }}</pre>
          </el-tab-pane>
        </el-tabs>
        <div class="step-actions">
          <el-button @click="registerStep = 0">返回修改</el-button>
          <el-button type="primary" @click="doApplyConfig" :loading="applyLoading">
            应用配置
          </el-button>
        </div>
      </div>

      <!-- Step 2：应用完成 -->
      <div v-if="registerStep === 2" class="step-content result-step">
        <el-result icon="success" title="对接完成" sub-title="EMQX 桥接和 PG 影子订阅均已建立">
          <template #extra>
            <div class="apply-detail">
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="EMQX 桥接">
                  <el-tag :type="applyResult?.emqxBridge?.ok ? 'success' : 'danger'">
                    {{ applyResult?.emqxBridge?.ok ? '已建立' : '失败: ' + applyResult?.emqxBridge?.error }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="PG 影子订阅">
                  <el-tag :type="applyResult?.pgSubscription?.ok ? 'success' : 'warning'">
                    {{ applyResult?.pgSubscription?.ok ? '已建立' : '失败: ' + applyResult?.pgSubscription?.error }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>
              <el-alert v-if="!applyResult?.pgSubscription?.ok" type="warning" show-icon :closable="false"
                title="PG 订阅失败通常是 pg_hba.conf 未允许外部 replication 连接，参考 K3s 部署文档手动修复" style="margin-top:12px" />
            </div>
            <el-button type="primary" @click="refreshStatus" style="margin-top:16px">查看对接状态</el-button>
          </template>
        </el-result>
      </div>
    </el-card>

    <!-- 历史记录 -->
    <el-card class="history-card" v-if="history.length">
      <template #header>
        <span><el-icon><Clock /></el-icon> 历史连接记录</span>
      </template>
      <el-table :data="history" size="small">
        <el-table-column label="平台地址" prop="url" />
        <el-table-column label="空间码" prop="spaceCode" width="100" />
        <el-table-column label="连接时间" prop="connectedAt" width="160">
          <template #default="{ row }">{{ formatDate(row.connectedAt) }}</template>
        </el-table-column>
        <el-table-column label="断开时间" prop="disconnectedAt" width="160">
          <template #default="{ row }">{{ formatDate(row.disconnectedAt) }}</template>
        </el-table-column>
        <el-table-column label="原因" prop="reason" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.reason === 'force_replace' ? 'danger' : 'info'">
              {{ row.reason }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Connection, Key, Refresh, SwitchButton, Warning, Clock } from '@element-plus/icons-vue'
import api from '../api'

const status = ref<any>({ connectionStatus: 'UNCONFIGURED' })
const history = ref<any[]>([])
const registerStep = ref(0)
const preview = ref<any>(null)
const pendingCredentials = ref<any>(null)
const pendingPlatformUrl = ref('')
const applyResult = ref<any>(null)

const testLoading = ref(false)
const testResult = ref<any>(null)
const registerLoading = ref(false)
const applyLoading = ref(false)
const unbindLoading = ref(false)
const heartbeatLoading = ref(false)
const rebuildLoading = ref(false)

const registerForm = ref({
  platformUrl: '',
  spaceCode: '',
  registrationToken: '',
  edgeIp: '',
})

let heartbeatTimer: any = null

// ── 计算属性 ──────────────────────────────────────────────────────────────────

const statusLabel = computed(() => {
  const map: any = { ACTIVE: '已对接', UNCONFIGURED: '未配置', REGISTERING: '注册中' }
  return map[status.value.connectionStatus] ?? status.value.connectionStatus
})

const statusTagType = computed(() => {
  return status.value.connectionStatus === 'ACTIVE' ? 'success' : 'info'
})

const statusClass = computed(() => ({
  'status-active': status.value.connectionStatus === 'ACTIVE',
  'status-unconfigured': status.value.connectionStatus !== 'ACTIVE',
}))

const isHeartbeatStale = computed(() => {
  if (!status.value.lastHeartbeat) return false
  return Date.now() - new Date(status.value.lastHeartbeat).getTime() > 120000
})

// ── 许可状态计算 ──────────────────────────────────────────────────────────────

const licenseLabel = computed(() => {
  const l = status.value.license
  if (!l) return ''
  if (l.daysRemaining === 0) return '已过期'
  if (!l.valid) return '设备超限'
  if (l.daysRemaining === -1) return '永久有效'
  if (l.daysRemaining <= 30) return '即将过期'
  return '有效'
})

const licenseTagType = computed(() => {
  const l = status.value.license
  if (!l) return 'info'
  if (l.daysRemaining === 0) return 'danger'
  if (!l.valid) return 'warning'
  if (l.daysRemaining === -1) return 'success'
  if (l.daysRemaining <= 30) return 'warning'
  return 'success'
})

const licenseUsagePercent = computed(() => {
  const l = status.value.license
  if (!l?.deviceLimit) return 0
  return Math.round((l.currentDeviceCount / l.deviceLimit) * 100)
})

const licenseBarColor = computed(() => {
  const pct = licenseUsagePercent.value
  if (pct > 90) return '#F56C6C'
  if (pct > 70) return '#E6A23C'
  return '#67C23A'
})

const licenseDaysClass = computed(() => {
  const l = status.value.license
  if (!l) return ''
  if (l.daysRemaining === 0 || !l.valid) return 'license-danger'
  if (l.daysRemaining <= 30) return 'license-warning'
  return 'license-ok'
})

const formatLicenseDays = (days: number): string => {
  if (days === -1) return '永久许可'
  if (days === 0) return '已过期'
  if (days <= 30) return `${days} 天（即将过期）`
  return `${days} 天`
}

// ── 数据加载 ──────────────────────────────────────────────────────────────────

const refreshStatus = async () => {
  try {
    const res: any = await api.get('/platform/status')
    status.value = res.data ?? res
    if (status.value.connectionStatus === 'ACTIVE') registerStep.value = 0
  } catch { /* ignore */ }
}

const loadHistory = async () => {
  try {
    const res: any = await api.get('/platform/history')
    history.value = res.data ?? res ?? []
  } catch { /* ignore */ }
}

// ── 注册流程 ──────────────────────────────────────────────────────────────────

const doTestConnection = async () => {
  if (!registerForm.value.platformUrl) return
  testLoading.value = true
  testResult.value = null
  try {
    const res: any = await api.post('/platform/test-connection', { platformUrl: registerForm.value.platformUrl })
    testResult.value = res.data ?? res
  } catch { testResult.value = { reachable: false, error: '请求失败' } }
  finally { testLoading.value = false }
}

const doRegister = async () => {
  registerLoading.value = true
  try {
    const res: any = await api.post('/platform/register', registerForm.value)
    const d = res.data ?? res
    preview.value = d.preview
    pendingCredentials.value = d.credentials
    pendingPlatformUrl.value = registerForm.value.platformUrl
    registerStep.value = 1
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || err.message || '注册失败')
  } finally {
    registerLoading.value = false
  }
}

const doApplyConfig = async () => {
  applyLoading.value = true
  try {
    const res: any = await api.post('/platform/apply-config', {
      credentials: pendingCredentials.value,
      platformUrl: pendingPlatformUrl.value,
    })
    applyResult.value = res.data ?? res
    registerStep.value = 2
    await refreshStatus()
    await loadHistory()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || '应用配置失败')
  } finally {
    applyLoading.value = false
  }
}

// ── 心跳 ──────────────────────────────────────────────────────────────────────

const doHeartbeat = async () => {
  heartbeatLoading.value = true
  try {
    const res: any = await api.post('/platform/heartbeat', {})
    const d = res.data ?? res
    if (d.reachable) {
      ElMessage.success('平台可达，心跳正常')
    } else {
      ElMessage.warning('平台不可达，请检查网络')
    }
    await refreshStatus()
  } finally {
    heartbeatLoading.value = false
  }
}

const doRebuildBridges = async () => {
  rebuildLoading.value = true
  try {
    const res: any = await api.post('/platform/rebuild-bridges')
    const d = res.data ?? res
    ElMessage.success('桥接已重建：3 个 Egress + 1 个 Ingress')
    console.log(d)
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || err.message || '重建失败')
  } finally {
    rebuildLoading.value = false
  }
}

// ── 解绑 / 强制替换 ───────────────────────────────────────────────────────────

const confirmUnbind = () => {
  ElMessageBox.confirm(
    '将正常解绑当前平台，会通知平台侧清理关联数据，并在本地删除 EMQX 桥接和 PG 订阅。继续？',
    '解绑平台',
    { confirmButtonText: '确认解绑', cancelButtonText: '取消', type: 'warning' }
  ).then(async () => {
    unbindLoading.value = true
    try {
      await api.delete('/platform/unbind')
      ElMessage.success('解绑成功')
      await refreshStatus()
      await loadHistory()
    } catch (err: any) {
      ElMessage.error(err.message || '解绑失败')
    } finally {
      unbindLoading.value = false
    }
  }).catch(() => {})
}

const confirmForceReplace = () => {
  ElMessageBox.prompt(
    '平台不可达时使用。本地配置将被强制清除，但平台侧可能需要手动清理遗留记录。\n\n请输入 CONFIRM 确认：',
    '强制替换平台',
    {
      confirmButtonText: '执行强制替换',
      cancelButtonText: '取消',
      type: 'error',
      inputPattern: /^CONFIRM$/,
      inputErrorMessage: '请输入 CONFIRM',
    }
  ).then(async () => {
    try {
      await api.post('/platform/force-replace', {})
      ElMessage.success('强制替换完成，可重新注册新平台')
      await refreshStatus()
      await loadHistory()
    } catch (err: any) {
      ElMessage.error(err.message || '强制替换失败')
    }
  }).catch(() => {})
}

// ── 工具方法 ──────────────────────────────────────────────────────────────────

const formatDate = (d: string) => d ? new Date(d).toLocaleString('zh-CN') : '—'

const timeAgo = (d: string) => {
  const sec = Math.floor((Date.now() - new Date(d).getTime()) / 1000)
  if (sec < 60) return `${sec}秒前`
  if (sec < 3600) return `${Math.floor(sec / 60)}分钟前`
  return `${Math.floor(sec / 3600)}小时前`
}

// ── 生命周期 ──────────────────────────────────────────────────────────────────

onMounted(async () => {
  await refreshStatus()
  await loadHistory()
  heartbeatTimer = setInterval(refreshStatus, 30000)
})

onBeforeUnmount(() => {
  if (heartbeatTimer) clearInterval(heartbeatTimer)
})
</script>

<style scoped>
.settings-container { padding: 10px; display: flex; flex-direction: column; gap: 16px; }

.status-card { }
.status-active { border-top: 3px solid var(--el-color-success); }
.status-unconfigured { border-top: 3px solid var(--el-color-info); }

.status-header { display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 16px; }
.status-left { display: flex; align-items: center; gap: 16px; }
.status-icon { color: var(--el-color-primary); }
.status-title { font-size: 16px; font-weight: 600; margin-bottom: 6px; }

.status-meta { display: flex; flex-wrap: wrap; gap: 20px; }
.meta-item { display: flex; flex-direction: column; }
.meta-item .label { font-size: 11px; color: var(--el-text-color-secondary); }
.meta-item .value { font-size: 13px; font-weight: 500; }
.meta-item .value.stale { color: var(--el-color-warning); }

.action-row { margin-top: 16px; display: flex; gap: 10px; flex-wrap: wrap; }

.register-card { }
.steps { margin: 0 0 24px; }
.step-content { padding: 8px 0; }

.test-result { margin-top: 6px; font-size: 13px; }
.test-result.ok { color: var(--el-color-success); }
.test-result.fail { color: var(--el-color-danger); }

.preview-tabs { margin: 16px 0; }
.code-preview {
  background: var(--el-fill-color-lighter);
  border-radius: 6px;
  padding: 12px;
  font-family: monospace;
  font-size: 13px;
  overflow: auto;
  max-height: 260px;
  white-space: pre-wrap;
}

.step-actions { margin-top: 16px; display: flex; gap: 10px; }
.result-step { text-align: center; }
.apply-detail { text-align: left; max-width: 500px; margin: 0 auto; }

.history-card { }

.license-section { margin-top: 4px; }
.license-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.license-title { font-size: 14px; font-weight: 600; }
.license-body { display: flex; gap: 32px; flex-wrap: wrap; }
.license-item { display: flex; flex-direction: column; gap: 6px; min-width: 200px; }
.license-item-label { font-size: 12px; color: var(--el-text-color-secondary); }
.license-item-value { font-size: 15px; font-weight: 600; }
.license-item-value.license-ok { color: var(--el-color-success); }
.license-item-value.license-warning { color: var(--el-color-warning); }
.license-item-value.license-danger { color: var(--el-color-danger); }
.license-progress-wrap { min-width: 200px; }
.license-progress-wrap .progress-nums { display: block; text-align: center; font-size: 12px; color: var(--el-text-color-secondary); margin-top: 4px; }

</style>

<template>
  <div class="streaming-container">
    <el-row :gutter="20">
      <el-col :span="10">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Plus /></el-icon> {{ $t('streaming.addProxy') }}</span>
            </div>
          </template>
          <el-form :model="newStream" label-position="top" @submit.prevent="handleAdd">
            <el-form-item :label="$t('streaming.streamId')">
              <el-input v-model="newStream.id" placeholder="e.g. office_camera_01" />
            </el-form-item>
            <el-form-item :label="$t('streaming.sourceUrl')">
              <el-input v-model="newStream.url" placeholder="rtsp://admin:password@192.168.1.100:554/ch1" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit" style="width: 100%">Add Proxy</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><VideoCamera /></el-icon> {{ $t('streaming.list') }}</span>
            </div>
          </template>
          <el-table :data="streams" size="small" border height="400">
            <el-table-column prop="id" :label="$t('streaming.streamId')" width="150" />
            <el-table-column prop="url" :label="$t('streaming.sourceUrl')" show-overflow-tooltip />
            <el-table-column :label="$t('streaming.actions')" width="100">
              <template #default="{ row }">
                <el-button type="danger" size="small" link @click="handleDelete(row.id)">{{ $t('streaming.remove') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import api from '../api';
import { ElMessage } from 'element-plus';
import { Plus, VideoCamera } from '@element-plus/icons-vue';

const streams = ref([]);
const newStream = reactive({ id: '', url: '' });

const handleAdd = async () => {
  if (!newStream.id || !newStream.url) {
    return ElMessage.warning('Please fill in all fields');
  }
  try {
    await api.post('/streaming/add', newStream);
    ElMessage.success('Stream added');
    newStream.id = '';
    newStream.url = '';
    fetchStreams();
  } catch (e) {}
};

const fetchStreams = async () => {
  try {
    const data: any = await api.get('/streaming/list');
    streams.value = data;
  } catch (e) {}
};

const handleDelete = (id: string) => {
  ElMessage.warning(`Removing ${id}...`);
};

onMounted(fetchStreams);
</script>

<style scoped>
.streaming-container { padding: 10px; }
.box-card { margin-bottom: 20px; }
.card-header { display: flex; align-items: center; gap: 8px; font-weight: bold; }
</style>

<template>
  <div v-if="$route.name === 'Login'">
    <router-view></router-view>
  </div>
  <el-container v-else class="layout-container" v-loading.fullscreen.lock="isRebooting" :element-loading-text="$t('common.rebooting')">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar-container">
      <div class="logo-container" :class="{ 'collapsed': isCollapse }">
        <img src="/images/logo.png" alt="Logo" class="logo-img" />
        <h3 v-if="!isCollapse" class="logo-text">{{ $t('header.title') }}</h3>
      </div>
      <el-menu
        active-text-color="#409eff"
        background-color="#304156"
        text-color="#bfcbd9"
        router
        :default-active="$route.path"
        :collapse="isCollapse"
        class="el-menu-vertical"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Monitor /></el-icon>
          <template #title>{{ $t('menu.dashboard') }}</template>
        </el-menu-item>
        <el-menu-item index="/mqtt">
          <el-icon><Connection /></el-icon>
          <template #title>{{ $t('menu.mqtt') }}</template>
        </el-menu-item>
        <el-menu-item index="/streaming">
          <el-icon><VideoCamera /></el-icon>
          <template #title>{{ $t('menu.streaming') }}</template>
        </el-menu-item>
        <el-menu-item index="/devices">
          <el-icon><Cpu /></el-icon>
          <template #title>{{ $t('menu.devices') }}</template>
        </el-menu-item>
        <el-menu-item index="/database">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>数据库服务</template>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>{{ $t('menu.settings') }}</template>
        </el-menu-item>
        <el-menu-item @click="handleReboot">
          <el-icon><SwitchButton /></el-icon>
          <template #title>{{ $t('menu.reboot') }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header-container">
        <div class="header-left">
          <el-button type="text" @click="isCollapse = !isCollapse">
            <el-icon :size="20">
              <Expand v-if="isCollapse" />
              <Fold v-else />
            </el-icon>
          </el-button>
          
          <div class="header-metrics" v-if="sysInfo">
            <span class="metric-badge">
              <span class="label">CPU</span>
              <span class="value">{{ sysInfo.cpu?.load?.toFixed(1) }}%</span>
            </span>
            <span class="metric-badge">
              <span class="label">RAM</span>
              <span class="value">{{ sysInfo.memory?.percentage?.toFixed(1) }}%</span>
            </span>
            <span class="metric-badge">
              <span class="label">DISK</span>
              <span class="value">{{ sysInfo.disk?.percentage?.toFixed(1) }}%</span>
            </span>
          </div>
        </div>
        <div class="header-right">
          <div class="header-item">
            <el-switch
              v-model="isDark"
              inline-prompt
              :active-icon="Moon"
              :inactive-icon="Sunny"
              @change="toggleTheme"
            />
          </div>
          <div class="header-item">
            <el-dropdown @command="handleLangCommand">
              <span class="lang-dropdown">
                <el-icon :size="18"><MagicStick /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="zh">中文</el-dropdown-item>
                  <el-dropdown-item command="en">English</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <div class="header-item">
            <el-dropdown @command="handleUserCommand">
              <span class="user-dropdown">
                Admin
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="logout">{{ $t('header.logout') }}</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  VideoCamera, Setting, Connection, SwitchButton, Monitor,
  Cpu, Expand, Fold, Moon, Sunny, MagicStick, ArrowDown, DataAnalysis
} from '@element-plus/icons-vue'
import api from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useDark, useToggle } from '@vueuse/core'

const { t, locale } = useI18n()
const router = useRouter()

const isRebooting = ref(false)
const isCollapse = ref(false)
const isDark = useDark()
const toggleTheme = useToggle(isDark)
const sysInfo = ref<any>(null)
let sysTimer: any = null

const fetchSysInfo = async () => {
  try {
    const res = await api.get('/monitor/stats')
    sysInfo.value = res
  } catch (e) {
    // Ignore errors for header
  }
}

const handleLangCommand = (lang: string) => {
  locale.value = lang
  localStorage.setItem('lang', lang)
  ElMessage.success(t('common.langSwitched'))
}

const handleUserCommand = (command: string) => {
  if (command === 'logout') {
    localStorage.removeItem('token')
    router.push('/login')
  }
}

const handleReboot = () => {
  ElMessageBox.confirm(
    t('common.rebootConfirm'),
    t('common.warning'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    }
  ).then(async () => {
    try {
      // In a real scenario, this would call the backend to reboot
      ElMessage.success(t('common.rebooting'))
      isRebooting.value = true
      setTimeout(() => {
        isRebooting.value = false
        ElMessage.success(t('common.rebootSuccess'))
        window.location.reload()
      }, 5000)
    } catch (e) {
      ElMessage.error('Reboot failed')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchSysInfo()
  sysTimer = setInterval(fetchSysInfo, 3000)
})

onBeforeUnmount(() => {
  if (sysTimer) clearInterval(sysTimer)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar-container {
  background-color: #304156;
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  background-color: #2b2f3a;
  overflow: hidden;
  transition: all 0.3s;
}

.logo-container.collapsed {
  padding: 0;
  justify-content: center;
}

.logo-img {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}

.logo-text {
  margin: 0 0 0 12px;
  color: white;
  font-weight: 600;
  font-size: 16px;
  white-space: nowrap;
}

.el-menu-vertical {
  border-right: none;
  flex: 1;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background-color: var(--el-bg-color);
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-metrics {
  display: flex;
  margin-left: 20px;
  gap: 15px;
}

.metric-badge {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
  font-family: monospace;
}

.metric-badge .label {
  font-size: 10px;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
}

.metric-badge .value {
  font-size: 13px;
  font-weight: bold;
  color: var(--el-color-primary);
}

.header-right {
  display: flex;
  align-items: center;
}

.header-item {
  margin-left: 20px;
  display: flex;
  align-items: center;
}

.lang-dropdown, .user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
  color: var(--el-text-color-primary);
}

.lang-dropdown:hover, .user-dropdown:hover {
  color: var(--el-color-primary);
}
</style>

<style>
.dark body {
  background-color: #1a1a1a;
}
</style>

```

