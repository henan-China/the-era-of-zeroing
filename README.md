# 《归零纪元——人类的选择》AI 漫剧视觉资源站

小组共同创作《归零纪元》漫剧的视觉资产站。末日废土体系：角色设定、场景设定、分镜帧、环境资产清单、制作进度看板、分工表、更新日志。

**在线地址（GitHub Pages）：** https://henan-china.github.io/the-era-of-zeroing/

## 文件结构

| 文件 | 作用 |
|---|---|
| `index.html` | 页面骨架与样式（**一般不用动**） |
| `content.js` | ⭐ **全部内容数据**（角色/场景/分镜/进度/分工/日志），小组更新都改这个文件 |
| `assets/` | 图片文件夹（角色图、场景图、分镜帧、封面） |
| `归零.html` | 早期版本文件（可忽略或删除） |

## 小组更新步骤（全程浏览器，无需任何软件）

### 改文字内容
1. 打开 https://github.com/henan-China/the-era-of-zeroing/blob/main/content.js
2. 点右上角铅笔图标（Edit this file）
3. 修改对应区块数据（文件内有中文注释说明每个字段）
4. 页面底部 Commit changes → 直接点 Commit
5. 等约 1 分钟，刷新 https://henan-china.github.io/the-era-of-zeroing/ 查看

### 传新图片
1. 打开仓库 `assets/` 文件夹 → **Add file → Upload files** → 拖入图片 → Commit
2. 在 `content.js` 中把对应条目的 `img` 字段改成新文件名（如 `"new_pic.jpg"`）→ Commit
3. 建议图片：长边 1280px、JPG、宽高比 16:9（与现有卡片一致）

### 新增一条数据
复制一行现有条目，粘贴后修改，注意：
- 每条之间用 **逗号** 分隔
- **最后一条后面不要加逗号**
- 引号用英文半角 `"`，文字里要用引号时写 `\u201c` 和 `\u201d`（或直接省略）

### 环境资产清单状态
`state` 字段：`"ok"` = 已有（绿色），`"todo"` = 待补画（红色）。

### 制作进度状态
`status` 可选：`未开始` / `脚本完成` / `分镜完成` / `设定图完成` / `生图中` / `待配音` / `已完成`。

## 相关文档

- 小说：《归零纪元——人类的选择》 https://my.feishu.cn/docx/GzoddQgwWon5FixotffcKiAT6tW
- 漫剧制作脚本：https://my.feishu.cn/docx/Dth2dZ3d4odLdQxP6OncKKX26df
- Gitee 镜像仓库：https://gitee.com/li8066/the-era-of-zeroing
