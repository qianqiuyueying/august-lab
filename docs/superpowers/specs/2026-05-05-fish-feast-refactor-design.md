# Fish Feast — 工程化重构设计

## 目标

将 `tmp-game/index.html`（600 行单文件 demo）重构为模块化 TypeScript 工程，
不改变游戏行为和外观，只改变代码组织方式，使其具备可维护、可扩展的工程底盘。

## 技术栈

- **Vite** — 开发服务器（HMR）、生产构建
- **TypeScript** — 类型安全
- **原生 DOM + CSS** — UI 层
- **Canvas API** — 游戏渲染
- **零框架** — 不引入 React 等 UI 框架

构建产物为纯静态文件（`index.html` + `assets/`），部署方式不变。

## 目录结构

```
fish-feast/
├── index.html              # 入口 HTML（UI 骨架）
├── package.json             # Vite + TypeScript
├── tsconfig.json
├── vite.config.ts           # base: './'
└── src/
    ├── main.ts              # 入口：初始化 + 启动游戏循环
    ├── constants.ts         # 游戏常量（颜色表、尺寸范围、阈值）
    ├── types.ts             # 共享类型定义
    ├── game/
    │   ├── engine.ts        # requestAnimationFrame 主循环
    │   ├── state.ts         # 全局 GameState 单例（create/get/reset）
    │   ├── player.ts        # 玩家鱼 — 输入 → 加速度/摩擦力 → 位置
    │   ├── enemy.ts         # 敌方鱼 — AI 行为 + 移动
    │   ├── collision.ts     # 碰撞检测 + 吃鱼/死亡逻辑
    │   ├── renderer.ts      # Canvas 绘制（背景/鱼/粒子/气泡）
    │   ├── spawner.ts       # 工厂函数（createFish/createBubble/createParticles）
    │   └── input.ts         # 键盘事件管理 → InputState
    ├── ui/
    │   ├── hud.ts           # 分数/等级/经验条 DOM 更新
    │   ├── overlay.ts       # 开始/死亡/暂停弹窗管理
    │   └── effects.ts       # 升级文字 + 闪光特效
    └── styles/
        └── main.css         # 全部 UI 样式
```

## 模块架构

```
input.ts ──→ player.ts ──→ GameState ──→ collision.ts
                ↑              │
            enemy.ts ←─────────┘
                                │ (只读)
                    ┌───────────┼───────────┐
                    ↓           ↓           ↓
                 hud.ts    overlay.ts   effects.ts
```

### 规则

1. **game/ 不碰 DOM** — 所有模块通过纯数据交互
2. **ui/ 只读 GameState** — 可以读，绝对不能直接修改游戏状态
3. **game/ 不引用 ui/** — 游戏逻辑不依赖 UI
4. **main.ts 是唯一胶水层** — 组装 game + ui，启动循环

## 核心类型

```typescript
interface Fish {
  x: number; y: number; size: number;
  vx: number; vy: number;
  dir: 1 | -1; color: string;
  tailPhase: number; wobble: number;
  speed: number; alive: boolean;
  behavior: 'wander' | 'flee' | 'chase';
}

interface PlayerFish extends Fish {
  isPlayer: true;
}

interface Particle {
  x: number; y: number;
  vx: number; vy: number;
  r: number; color: string;
  life: number; decay: number;
}

interface Bubble {
  x: number; y: number;
  r: number; speed: number;
  alpha: number;
}

interface GameState {
  player: PlayerFish;
  fishes: Fish[];
  particles: Particle[];
  bubbles: Bubble[];
  score: number; level: number;
  gameTime: number; difficulty: number;
  running: boolean; paused: boolean;
}

interface InputState {
  up: boolean; down: boolean;
  left: boolean; right: boolean;
  pauseTriggered: boolean; // 单帧有效，处理后重置
}
```

## 实施约束

- **游戏行为 100% 不变** — 移动手感、AI 行为、碰撞判定、数值成长完全一致
- **UI 外观 100% 不变** — 颜色、动画、布局、特效与原 demo 一致
- **构建产物不变** — 仍是 `dist/` 下的纯静态文件
- **不涉及新功能** — 不添加音效、新鱼种、道具等（后续迭代）
- **不涉及测试** — 本次只做模块化拆分（后续补）
