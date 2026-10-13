# 科哞哞——Codex 桌宠部署指南

本文档详细说明如何将科哞哞桌宠部署到你的网站。

---

## 一、快速开始

### 1.1 文件清单

部署所需的最小文件集：

`
web/
+-- pet.js              # 桌宠核心逻辑（307 行）
+-- pet.css             # 桌宠样式（49 行）
+-- pet/
    +-- spritesheet.webp    # 精灵图（WebP 格式，推荐）
    +-- spritesheet.png     # 精灵图（PNG 格式，备用）
    +-- scenes.json         # 场景配置
    +-- cutouts/            # 场景抠图（WebP）
    +-- scenes/             # 场景图（WebP）
`

### 1.2 三步集成

**第一步**：复制文件到你的网站资源目录

`ash
# 假设你的网站资源在 assets/ 下
cp -r web/pet.js web/pet.css web/pet/ your-site/assets/
`

**第二步**：在 HTML 中引入

`html
<!DOCTYPE html>
<html>
<head>
  <!-- 其他 head 内容 -->
  <link rel="stylesheet" href="assets/pet.css">
</head>
<body>
  <!-- 你的页面内容 -->
  
  <!-- 在 body 结束前引入 -->
  <script src="assets/pet.js" defer></script>
</body>
</html>
`

**第三步**：完成！桌宠会自动初始化并显示在页面右下角。

---

## 二、自定义配置

### 2.1 修改页面感知

`pet.js` 中的 `pageProfile` 函数决定了桌宠在不同页面的行为。
修改此函数以适配你的网站结构：

`javascript
function pageProfile(path) {
  // path 是相对于 siteBase 的路径
  if (path === 'index.html') return entry(
    'auto',          // 场景 ID：'auto' 表示使用 spritesheet 动画
    '首页标题',       // 面板标题
    '介绍语...',      // 首次出现时的引导语
    ['推荐文字', '推荐链接']  // 推荐内容
  );
  if (path === 'about.html') return entry(
    'mentor',         // 场景 ID：对应 cutouts/ 和 scenes/ 中的文件
    '关于页面',
    '这是关于页面...'
  );
  // ... 更多页面
  return entry('thinking', '未找到', '默认提示');
}
`

可用的场景 ID：
- `auto`：使用 spritesheet 动画循环
- `welcome`、`mentor`、`project`、`resource`
- `achievement`、`notice`、`lecture`、`recruit`、`thinking`

### 2.2 修改场景描述

`SCENES` 数组定义了每个场景的标签和描述：

`javascript
const SCENES = [
  ['welcome', '欢迎探索', '好奇心，是出发的第一步。'],
  ['mentor', '找导师', '带着问题，认识新的研究方向。'],
  // ... 修改这里的文字以适配你的网站
].map(([id, label, note]) => ({id, label, note}));
`

### 2.3 调整初始大小

找到 `savedScale` 相关代码，修改默认值：

`javascript
// 原始代码
let scale = Number.isFinite(savedScale) && savedScale >= .5 && savedScale <= 1.2
  ? savedScale
  : innerWidth < 600 ? .65 : .85;

// 修改默认值（例如桌面端 1.0，移动端 0.75）
let scale = Number.isFinite(savedScale) && savedScale >= .5 && savedScale <= 1.2
  ? savedScale
  : innerWidth < 600 ? .75 : 1.0;
`

### 2.4 修改 localStorage 键名

如果你的网站可能有多个桌宠实例，修改键名避免冲突：

`javascript
const keys = {
  hidden: 'YOUR-PREFIX-pet-dismissed',
  scale: 'YOUR-PREFIX-pet-scale',
  position: 'YOUR-PREFIX-pet-position',
  paused: 'YOUR-PREFIX-pet-paused',
  gaze: 'YOUR-PREFIX-pet-gaze',
  guide: 'YOUR-PREFIX-pet-guide'
};
`

### 2.5 修改导航链接

`renderNavigation` 函数中的快速导航链接需要适配你的网站：

`javascript
[
  ['回到首页', 'index.html', '看看正在做的事'],
  ['知识与论文', 'knowledge/index.html', '从问题出发'],
  // ... 修改为你的网站链接
]
`

---

## 三、高级集成

### 3.1 从页面触发桌宠动画

使用自定义事件让桌宠响应页面交互：

`javascript
// 触发动画
document.dispatchEvent(new CustomEvent('cutus:pet', {
  detail: { state: 'waving' }  // 任意动画状态名
}));

// 触发场景
document.dispatchEvent(new CustomEvent('cutus:pet', {
  detail: { scene: 'achievement', duration: 5000 }
}));
`

### 3.2 精灵图格式说明

精灵图 `spritesheet.webp` 的布局：

`
+--------+--------+--------+--------+--------+--------+--------+--------+
| idle 0 | runR 0 | runL 0 | wave 0 | jump 0 | fail 0 | wait 0 | run  0 |  row 0
+--------+--------+--------+--------+--------+--------+--------+--------+
| idle 1 | runR 1 | runL 1 | wave 1 | jump 1 | fail 1 | wait 1 | run  1 |  row 1
...
+--------+--------+--------+--------+--------+--------+--------+--------+
| look9  | look10 |                                                          row 10
+--------+--------+--------+--------+--------+--------+--------+--------+
`

- 每格：192 x 208 像素
- 总共：8 列 x 11 行 = 1536 x 2288 像素
- 第 0-8 行：9 种动画状态
- 第 9-10 行：16 方向视线跟随

### 3.3 适配自己的角色

如果你想用科哞哞的框架但换成自己的角色：

1. 准备你的精灵图（1536 x 2288，8 列 x 11 行，每格 192 x 208）
2. 替换 `pet/spritesheet.webp` 和 `pet/spritesheet.png`
3. 替换 `pet/cutouts/` 和 `pet/scenes/` 中的图片
4. 修改 `pet.js` 中的验证逻辑（`loadSprite` 函数中的尺寸检查）

---

## 四、性能与兼容性

### 4.1 性能考虑

- 精灵图使用 WebP 格式，体积更小
- 仅在需要时播放动画，闲置时暂停
- 支持 `prefers-reduced-motion` 系统设置
- 页面不可见时自动暂停所有动画
- 使用 `requestAnimationFrame` 优化视线跟随

### 4.2 浏览器兼容

- 支持所有现代浏览器（Chrome、Firefox、Safari、Edge）
- 需要支持 CSS Custom Properties（CSS 变量）
- 需要支持 ES6+（`const`、`let`、箭头函数等）
- 不支持 IE

### 4.3 无障碍

- 桌宠按钮具有 `aria-label`
- 导航面板使用 `role="dialog"`
- 支持键盘操作（Tab、方向键、Escape）
- 支持 `focus-visible` 样式
- 尊重 `prefers-reduced-motion` 设置

---

## 五、故障排除

### 桌宠不显示

- 检查 `pet.js` 和 `pet.css` 路径是否正确
- 检查浏览器控制台是否有错误
- 确认精灵图 `spritesheet.webp` 已正确加载
- 桌宠可能之前被关闭了（检查 localStorage 中的 `cutus-pet-dismissed`）

### 精灵图加载失败

- 确认精灵图尺寸为 1536 x 2288
- 检查 WebP 格式是否被浏览器支持
- 如果 WebP 不支持，代码会尝试 PNG 备用

### 动画不播放

- 检查是否开启了 `prefers-reduced-motion`
- 检查设置面板中"待机动画"是否开启
- 确认浏览器未限制动画执行

### 位置不保存

- 检查浏览器是否禁用了 localStorage
- 确认没有其他脚本覆盖相同的键名
