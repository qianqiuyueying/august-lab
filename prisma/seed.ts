import { PrismaClient } from "@prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";

const adapter = new PrismaPg(process.env.DATABASE_URL!);
const prisma = new PrismaClient({ adapter });

async function main() {
  // 清理旧数据
  await prisma.article.deleteMany();
  await prisma.product.deleteMany();
  await prisma.media.deleteMany();
  await prisma.siteInfo.deleteMany();

  // 种子文章
  await prisma.article.createMany({
    data: [
      {
        slug: "building-space-with-light",
        title: "用光影构建空间感",
        excerpt: "关于如何在数字界面中通过光影对比建立视觉层次，而不是依赖颜色。",
        content: `## 光影即空间

在设计数字界面时，我们常常过度依赖颜色来区分层级。但真正有深度的设计，依靠的是光影对比。

### 从摄影中学习

摄影中最基本的原则之一：光影定义形体。高光让元素浮现，阴影让元素后退。

在界面设计中，这套逻辑同样成立：

- **表面抬高** = 更亮（或者更暗，取决于你的设计系统基底）
- **表面凹陷** = 反之

深色主题的优势在于：我们可以更精细地控制光影层次，因为深色空间天然暗示着光源的存在。

### 几何的作用

当色彩被剥离，几何就成为了骨架。不是所有的几何都是装饰——精准的比例和间距系统，本身就是一种语言。

在 Atelier 的设计中，我们使用了一个极简的间距系统：

\`\`\`
sp-2xs: 0.25rem
sp-xs:  0.5rem
sp-sm:  0.75rem
sp-md:  1.25rem
sp-lg:  2.25rem
sp-xl:  4rem
sp-2xl: 7rem
sp-3xl: 10rem
\`\`\`

这些数值不是随机的。它们遵循一个非线性递增序列——从 0.25 到 10，每一步的增幅都在变化，制造出一种自然生长的节奏感。

### 结语

光影和几何不是设计的手段，而是设计的本质。当你不再依赖颜色，你才会真正开始设计空间。`,
        coverImage: "/uploads/venetian-blind-shadow.png",
        tags: ["设计", "思考"],
        readingTime: 6,
        featured: true,
        published: true,
        publishedAt: new Date("2026-06-09"),
      },
      {
        slug: "comfyui-workflow",
        title: "ComfyUI 本地生图工作流",
        excerpt: "搭建了一套本地化的图像生成管线，从快速出图到高清超分的完整记录。",
        content: `## 本地生图管线

记录搭建 ComfyUI + RTX 4060 的工作流。

### 硬件配置

- GPU: NVIDIA RTX 4060 (12GB VRAM)
- 框架: ComfyUI
- 模型: SDXL + 各种 LoRA

### 工作流节点

1. **快速出图**: z_image_turbo 节点，低步数（4-6步）快速产出概念图
2. **高清超分**: 4x 放大 + detailer 修复
3. **色彩调整**: 在 ComfyUI 中用色调节点统一输出风格

### 效果

本地出图速度约 2-3 秒/张（快速模式），8-10 秒/张（高清模式）。完全离线运行，不依赖任何云服务。`,
        coverImage: "/uploads/perforated-metal-shadow.png",
        tags: ["技术", "AI"],
        readingTime: 4,
        featured: true,
        published: true,
        publishedAt: new Date("2026-06-05"),
      },
      {
        slug: "poetry-of-everyday-objects",
        title: "日常物件的诗意",
        excerpt: "摄影如何改变了设计的理解——从日常物件中提取质感与叙事。",
        content: `## 日常物件的诗意

摄影教会我最重要的一件事：美不在远方，就在你手边。

### 金属尺的启示

一把普通的金属尺，在侧面光的照射下，刻度产生了微妙的高光和阴影。每一道刻痕都有了立体感。

这让我思考界面设计中的分割线——它们不需要颜色，只需要一束"光"。

### 玻璃杯的透明性

玻璃杯的阴影不是黑色，而是半透明的、带有扭曲的。这提醒我：在设计中，阴影不应该是纯黑的，它们应该带有环境色的信息。`,
        coverImage: "/uploads/glass-shadow.png",
        tags: ["摄影", "灵感"],
        readingTime: 8,
        featured: false,
        published: true,
        publishedAt: new Date("2026-06-01"),
      },
    ],
  });

  // 种子作品
  await prisma.product.createMany({
    data: [
      {
        slug: "tools-2026",
        title: "工具集 · 2026",
        description: "一组日常开发工具的摄影记录。从键盘到精密工具，通过俯拍和均匀打光，呈现工具本身的几何美感和材质细节。",
        content: "一组日常开发工具的摄影记录。从键盘到精密工具，通过俯拍和均匀打光，呈现工具本身的几何美感和材质细节。",
        coverImage: "/uploads/metal-ruler.png",
        tags: ["摄影", "工具"],
        status: "online",
        featured: true,
        published: true,
        publishedAt: new Date("2026-06-01"),
      },
      {
        slug: "keycap-macro",
        title: "键帽微距",
        description: "细节中的构成 — 键帽表面的纹理和光影。",
        content: "细节中的构成 — 键帽表面的纹理和光影。",
        coverImage: "/uploads/plaster-geometric.png",
        tags: ["摄影", "细节"],
        status: "online",
        featured: false,
        published: true,
        publishedAt: new Date("2026-05-20"),
      },
      {
        slug: "shadow-study",
        title: "阴影研究",
        description: "透明物体的光线行为。",
        content: "透明物体的光线行为。",
        coverImage: "/uploads/glass-shadow.png",
        tags: ["摄影", "实验"],
        status: "developing",
        featured: false,
        published: true,
        publishedAt: new Date("2026-05-15"),
      },
    ],
  });

  // 种子站点信息
  await prisma.siteInfo.create({
    data: {
      id: 1,
      aboutBio: "一个喜欢动手折腾的创作者。写代码、拍照片、做实验是日常。\n\n工具不拘，想法先行。只要灵光一闪，就搭个东西出来看看。",
      siteTitle: "August's Lab",
      siteDescription: "写点代码，拍点照片，偶尔做出点什么。",
      aboutLinks: [
        { label: "GitHub", url: "https://github.com/august" },
        { label: "Twitter", url: "https://twitter.com/august" },
      ],
      socialLinks: [
        { label: "GitHub", url: "https://github.com/august" },
        { label: "Twitter", url: "https://twitter.com/august" },
      ],
    },
  });

  console.log("✅ Seed data inserted successfully");
}

main()
  .catch((e) => { console.error(e); process.exit(1); })
  .finally(() => prisma.$disconnect());
