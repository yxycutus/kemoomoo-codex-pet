# 发布检查

所有命令从仓库根目录执行。Python 3.10+、Node.js 20+；测试不会安装或切换账户中的宠物。

## 资源和文档

```bash
python -m pip install Pillow==12.3.0
python scripts/validate_assets.py
node --check web/pet.js
```

检查纳入 Git 的文件及未忽略的新文件：图像解码、精灵图尺寸/透明度/帧占用、桌面包、QA 哈希、JSON、Markdown 本地链接、常见私人路径和凭据特征。凭据检查不是完整安全审计。

## 浏览器回归

```bash
npm install --no-save --package-lock=false playwright@1.62.1
npx playwright install chromium
node tests/web.cjs
```

测试自行启动仅监听 `127.0.0.1` 的临时服务器并在结束后关闭。覆盖演示、动作、拖动与触摸、键盘焦点、设置持久化、禁用存储、减少动态、窄屏、子目录部署和资源失败回退。

可设置 `PLAYWRIGHT_MODULE` 指向已有 Playwright 模块，`CHROME_PATH` 指向本机 Chromium 浏览器，`SCREENSHOT_DIR` 指向临时截图目录。默认不产生截图。自动检查配置见 `.github/workflows/check.yml`。

## 检查边界

- 浏览器回归使用 Chromium，不代表所有 Firefox/Safari 版本均已验证。
- 桌面包检查 `pet.json` 和九行 PNG，与本机已有桌宠格式一致；自动测试不操作桌面应用，也不验证所有版本的导入 UI。
- `sprites/qa/` 是原制作期间的报告，扩展图哈希已核对。方向细节、透明孔隙及连续性警告保留在 `pet-quality.json`，不是零警告认证。
- `sprites/制作记录/` 保存历史脚本，部分需要额外 work-pets 工具和未公开中间图，不属于上面的独立发布检查。

## 本次审查记录（2026-10-13）

审查基线：远端 `main` 的 `87ea805`。

- 资源检查：310 个发布文件，232 个图像文件、11 个 JSON、11 处 Markdown 本地链接；精灵图帧占用与透明度、桌面包清单、报告哈希均通过。
- 浏览器：Windows 本机 Chrome/Chromium，桌面与触摸模拟；全部功能回归通过，包括真实 CDP 触摸事件、四种宽度及短屏、禁用存储、WebP/PNG 故障、PNG 重试、无推荐链接的面板和宿主样式冲突。
- JS/Python 语法与 `git diff --check` 通过。两个已有历史提交的常见令牌/私钥特征检查未发现匹配。
- CI 所用 Pillow 12.3.0 与 Playwright 1.62.1 已核实可从官方包仓库取得。GitHub Actions 尚未在远端执行；推送后以远端运行结果为准。
- 桌面包仅完成格式和资源验证，未安装到用户的实际桌宠目录；未实测跨版本导入。原有视觉局限仍见上节。
