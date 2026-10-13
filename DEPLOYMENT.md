# 科哞哞部署指南

桌面端安装包和入口见 [README](README.md#桌面端安装)。本指南介绍独立网页伙伴，不需要 API Key，不连接桌面任务。

## 本地预览

在仓库根目录运行：

```bash
python -m http.server 8080 --bind 127.0.0.1 --directory web
```

打开 <http://127.0.0.1:8080/>，可测试点击、拖动、动作和设置。

## 集成到网站

最小运行文件：

```text
assets/
├── pet.js
├── pet.css
└── pet/
    ├── spritesheet.webp
    ├── spritesheet.png
    └── cutouts/           # 九个场景 WebP
```

`scenes.json`、`cutouts/manifest.json` 和 `scenes/` 是素材来源与参考资料，运行时不会读取这些 JSON。

在页面中引入（`defer` 确保页面内容已经解析）：

```html
<link rel="stylesheet" href="/assets/pet.css">
<script src="/assets/pet.js" data-site-base="../" defer></script>
```

`pet/` 始终相对于脚本定位；`data-site-base` 相对于脚本 URL 解析。脚本放在 `assets/` 时，`../` 代表网站根目录；不设置时默认使用脚本所在目录。部署到 `/my-site/` 时改用 `/my-site/assets/pet.css` 和 `/my-site/assets/pet.js`，`data-site-base="../"` 不变。不要使用 `type="module"`：这是通过 `document.currentScript` 定位资源的普通脚本。

默认导航仅列出当前页面的真实章节，不依赖作者个人站的目录。原 Cutus 网站可加 `data-site-profile="cutus"` 恢复其专属文案和链接；其他网站不应启用此选项。

## 自定义

`pageProfile` 返回场景、标题、介绍和可选推荐链接。若自行替换该函数，使用完整示例：

```javascript
function pageProfile(path) {
  const entry = (scene, title, intro, recommendation = []) =>
    ({ scene, title, intro, recommendation });
  if (path === 'about.html') return entry('mentor', '关于我们', '一起认识这个项目。');
  return entry('auto', '欢迎', '我是科哞哞。');
}
```

`auto` 表示精灵动画待机；可选场景为 `welcome`、`mentor`、`project`、`resource`、`achievement`、`notice`、`lecture`、`recruit`、`thinking`。场景标签在 `SCENES` 中配置。

`scale` 默认为桌面 85%、窄屏 65%，允许 50%–120%。`keys` 定义 localStorage 键名；同源不同项目若需隔离偏好，可更换前缀。一个页面只支持一个科哞哞实例，重复加载脚本不会再创建一个。

## 从页面触发

等待桌宠加载后发送事件；加载前的事件不会排队：

```javascript
document.dispatchEvent(new CustomEvent('cutus:pet', {
  detail: { state: 'waving' }
}));
document.dispatchEvent(new CustomEvent('cutus:pet', {
  detail: { scene: 'achievement', duration: 5000 }
}));
```

动作结束、场景时长结束后返回当前页面姿态。`duration` 限制为 500–10000 毫秒。九种动作见下表；视线方向由鼠标驱动，不是事件动作名。

## 精灵图与替换素材

网页精灵图为 1536×2288、RGBA、8 列×11 行，每格 192×208：

| 行 | 状态 | 有效帧 |
| --- | --- | --- |
| 0 | idle | 6 |
| 1 | running-right | 8 |
| 2 | running-left | 8 |
| 3 | waving | 4 |
| 4 | jumping | 5 |
| 5 | failed | 8 |
| 6 | waiting | 6 |
| 7 | running | 6 |
| 8 | review | 6 |
| 9 | 视线：0°–157.5° | 8 |
| 10 | 视线：180°–337.5° | 8 |

每行从第 0 列开始排列，未使用格子透明。视线从正上方起，顺时针每 22.5° 一个方向。九行桌面包为 1536×1872，不可直接替换网页的十一行图。

更换角色时同时替换 `spritesheet.webp`、`spritesheet.png` 和九张 `cutouts/*.webp`。保持尺寸与帧布局即可，无需修改尺寸校验。场景抠图为 512×512 透明图。代码允许 MIT 复用，现有角色素材的商业使用仍需授权。

## 交互与兼容性

- 待机图循环播放；场景抠图使用轻微 CSS 动画。页面不可见时暂停。
- 尊重系统减少动态设置，也可手动暂停动画、关闭视线跟随和章节介绍。
- 支持鼠标、触摸拖动；聚焦桌宠后可用方向键移动、Enter 打开面板、Escape 关闭面板。
- 导航面板为非模态 dialog，不锁住页面其他区域。
- 使用现代浏览器 API，包括 Pointer Events、AbortController、Object.hasOwn 和 Array.at；不支持 IE。当前回归覆盖 Chromium，未逐一实测 Firefox/Safari。

## 故障排查

- 不显示：检查资源 HTTP 状态，或点击「叫回科哞哞」。请通过 HTTP 服务器预览。
- WebP 请求失败或尺寸错误：自动尝试 PNG；两者均失败时显示重试按钮。
- 场景抠图失败：回退到待机精灵图。
- 动画不播放：检查系统减少动态设置和面板的待机动画开关。
- 偏好不保存：浏览器可能禁用 localStorage；仍可使用，但刷新后不保留设置。

发布检查见 [TESTING.md](TESTING.md)。

## 本仓库公网发布

演示地址：<https://yxycutus.github.io/kemoomoo-codex-pet/>。

`.github/workflows/check.yml` 先运行资源校验和浏览器回归，再将 `web/` 发布到 GitHub Pages。只有 `main` 分支的推送或手动运行会部署；PR 只做检查。运行产物附带代码与素材许可，不包含内部制作日志。
