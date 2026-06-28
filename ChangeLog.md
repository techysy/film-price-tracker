# 📋 更新日志

## 2026-06-28

### 🔧 OCR 配置系统（移植自 inspection-visualizer）

**新增可配置 OCR 引擎**
- 支持调节文本置信度阈值（text_score）
- 支持启用/禁用文本检测（use_det）、分类（use_cls）、识别（use_rec）
- 支持最小高度约束和最大边长缩放
- 支持忽略图片顶部/底部区域（过滤标题栏、水印等）
- 配置持久化到 `ocr_config.json` 文件

**新增 API 端点**
- `GET /api/ocr-config` — 获取当前 OCR 配置
- `POST /api/ocr-config` — 实时应用配置（不持久化）
- `POST /api/ocr-config/save` — 保存配置到文件并重建引擎
- `GET /api/ocr/model-info` — 获取 OCR 模型信息
- `POST /api/ocr/test` — 测试 OCR 识别（返回原始文本）

**新增 OCR 管理面板**
- 隐藏页面 `/ocr-admin`，用于调优 OCR 参数
- 实时预览配置效果
- 上传截图测试识别，显示原始文本
- 支持复制识别结果

---

### 🎨 Toast 通知系统

**新增全局 Toast 通知**
- 在 `base.html` 添加 toast 容器和 `showToast()` 全局函数
- 支持 success/error/info/warning 四种类型
- 3.5 秒自动消失，可手动关闭
- 替代 `alert()` 提供更好的用户体验

---

### 🎨 UI/UX 改进

**导航栏增强**
- 新增「OCR」导航链接，指向 OCR 管理面板
- 链接样式较小且半透明，不干扰主要功能

**CSS 优化**
- `.nav-link.active` 增加底部边框和加粗效果（标签式激活状态）
- `.card` 过渡动画从 `all 0.3s ease` 优化为 `border-color 0.3s, background 0.3s`
- `.form-control` 过渡动画优化，添加 `outline: 0` 到 focus 状态
- `.store-info` 添加 `flex: 1` 改善布局
- `.tag-format` 从绿色改为紫色，增加 font-weight

---

### 📁 新增文件

- `ocr_config.json` — OCR 引擎配置文件（默认参数）
- `templates/ocr_admin.html` — OCR 管理面板模板

---

## 2026-06-22

### 🎨 UI 统一：胶片管理与店铺管理对齐

**问题**：胶片管理页面使用了 `.store-*` CSS 类，但这些样式仅在 `stores.html` 内联定义，导致胶片页面完全无样式（无卡片边框、无按钮颜色、无输入框背景）。

**修复**：
- 将 `.store-*` 和 `.film-tag` 所有 CSS 从 HTML 内联 `<style>` 迁移到共享 `static/css/style.css`
- 从 `stores.html` 和 `films.html` 中移除重复的 `<style>` 块
- 添加移动端响应式样式（`@media max-width: 640px`）

**效果**：两个管理页面现在共用同一份样式，UI 完全统一。

---

### 🎞️ 胶片模型增强

**Film 表新增 `created_at` 字段**
- 类型：`DateTime`，默认值 `datetime.datetime.utcnow`
- 胶片管理卡片新增创建时间显示（`store-card-meta` + `store-date`）
- 与店铺管理卡片结构对齐
- `init_db()` 自动迁移：已有数据库会自动添加该列

---

### 🐛 已知问题记录

**胶片类型与价格追踪逻辑重叠**
- 当前：首页展示胶卷列表，价格记录通过 `price_histories.platform`（字符串）关联店铺名
- 问题：未关联 `taobao_stores` 表，首页无法平铺展示所有店铺价格
- 正确逻辑：一种胶卷 → 对应多个店铺的价格，首页应平铺展示所有店铺
- 状态：待后续迭代重构

---

## 2026-06-21

### 🏗️ 架构重构：爬虫 → OCR 截图识别

**放弃爬虫方案**
- 淘宝使用 secfont1 动态字体加密，DOM 中价格文字无法直接读取
- 商品详情页触发验证码，无头浏览器无法绕过
- 删除文件：`run_spider.py`、`scheduler.py`、`spiders/`、`scrapy.cfg`、`cookies.json`

**新增 OCR 截图识别**
- 引入 `rapidocr-onnxruntime` 作为 OCR 引擎
- 新增路由 `/upload` — 截图识别页面（支持 Ctrl+V 粘贴、拖拽、点击上传）
- 新增 API `/api/ocr` — 接收 base64 图片，OCR 识别后返回商品列表
- 新增 API `/api/save` — 保存识别结果到 films + price_histories 表
- 导航栏新增「截图识别」入口

**OCR 解析增强**
- `parse_ocr_lines()`：从 OCR 文本中提取店铺名、商品标题、价格
- 过滤 88VIP/退货/退款/商品规格 等无关行
- 支持标题和价格分行的购物车截图格式

---

### 🎞️ 胶片管理

**新增胶片管理页面** `/films`
- 卡片式布局，显示品牌/型号/画幅/类型/ISO/有效期
- 添加表单：品牌、型号、画幅(下拉)、类型(下拉)、ISO
- 编辑弹窗：完整字段编辑
- 删除：同时清除关联的价格记录
- 品牌头像颜色：柯达黄、富士绿、伊尔福灰

**OCR 智能匹配**
- 识别后自动匹配数据库已有胶片（品牌+ISO+画幅+类型综合评分）
- 匹配成功：显示绿色标签
- 匹配失败：显示下拉框手动选择胶片
- 未选择胶片的记录自动跳过，提示跳过数量

**新路由**
- `GET /films` — 胶片管理页面
- `POST /films/add` — 添加胶片
- `POST /films/edit/<id>` — 编辑胶片
- `POST /films/delete/<id>` — 删除胶片（含关联价格记录）
- `GET /api/films/list` — 胶片列表 JSON（前端匹配用）
- `POST /api/films/match` — 胶片匹配 API

---

### 🏪 店铺管理增强

**批量导入**
- 展开式导入区域，粘贴表格数据（Tab/多空格分隔）
- 自动识别 `名称 + URL` 格式
- 按 URL 去重，跳过已存在店铺
- 导入成功后自动收起，页面右上角显示「批量导入更多」按钮
- 导入区域支持展开/收起切换，箭头同步旋转

**UI 改进**
- 卡片式布局（头像+名称+URL+操作按钮）
- 新增「访问」按钮直接跳转店铺网页
- 移除爬虫相关的「启用/禁用」开关

---

### 🎨 UI/UX 改进

**主题系统**
- CSS 变量驱动的深色/浅色/跟随系统三模式
- 主题切换按钮在导航栏右侧，偏好保存在 localStorage
- 页面加载无闪烁（内联 JS 预设置）

**导出功能**
- 导出按钮改为下拉菜单（`导出 ▾` → HTML / JSON）
- 首页和详情页均支持
- 导出 HTML 内联 CSS 变量 + 主题切换 JS，可直接部署 GitHub Pages

**首页**
- 胶卷卡片列表 + 双维度筛选（画幅 + 类型）
- 空状态引导上传截图识别

**详情页**
- Chart.js 折线图展示各店铺价格历史趋势
- 图表颜色随主题切换实时更新（MutationObserver）
- 统计卡片（监控店铺数、数据点数）

**截图识别页**
- 左右分栏：左侧上传区 + 右侧识别结果
- 识别结果显示匹配胶片（绿色标签）或手动选择下拉框
- 支持逐条删除不需要的商品
- 保存后提示成功数量和跳过数量

**导航栏**
- 新增「胶片管理」入口

---

### 🔧 启动脚本

**PowerShell (`start.ps1`)**
- 交互式菜单：S(前台) / B(后台) / T(停止) / C(状态) / Q(退出)
- 支持参数直接调用：`-Action start` / `-Action start-bg` / `-Action stop` / `-Action status`
- 自动创建虚拟环境、安装依赖、检查 OCR 引擎

**CMD (`start.bat`)**
- 双击直接启动，自动创建虚拟环境、安装依赖
- 使用英文输出避免中文乱码导致脚本闪退

---

### 🗄️ 数据模型

**Film 表**
| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer | 主键 |
| brand | String(50) | 品牌（柯达/富士/伊尔福等） |
| model | String(100) | 商品名称 |
| iso | Integer | 感光度（100/200/400/800） |
| format | String(20) | 画幅（35mm/120/拍立得Mini/宝丽来等） |
| film_type | String(30) | 类型（彩负/黑白/反转/电影卷/一次成像） |
| expiry | String(10) | 有效期（YYYY-MM） |
| description | String(255) | 描述 |
| created_at | DateTime | 创建时间 |

**PriceHistory 表**
| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer | 主键 |
| film_id | Integer(FK) | 关联胶卷 |
| platform | String(50) | 店铺名称 |
| price | Float | 价格 |
| url | String(255) | 商品链接 |
| timestamp | DateTime | 记录时间 |

**TaobaoStore 表**
| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer | 主键 |
| name | String(100) | 店铺名称 |
| url | String(500) | 店铺主页 URL |
| created_at | DateTime | 创建时间 |

---

### 🔤 OCR 解析规则

**品牌识别**
- kodak/柯达, fujifilm/富士/fuji, ilford/伊尔福, agfa/爱克发
- lomography/乐魔, cinestill, fomapan, wolfen, orwo, flic film

**画幅识别**
| 关键词 | 归类 |
|---|---|
| `135`, `35mm` | 35mm |
| `120` | 120 |
| `220` | 220 |
| `4x5`, `5x7`, `8x10` | 大画幅 |
| `instax mini` | 拍立得Mini |
| `instax sq` | 拍立得SQ |
| `instax wide` | 拍立得Wide |
| `polaroid`, `宝丽来` | 宝丽来 |

**类型识别**
| 关键词 | 归类 |
|---|---|
| 彩负/彩色负片/color/colorplus/gold/ultra | 彩负 |
| 黑白/b&w/bw/pan/hp5/delta/fomapan | 黑白 |
| 反转/slide/reversal/chrome/provia/velvia/ektar | 反转 |
| 电影卷/vision/5207/5219 | 电影卷 |
| 一次成像/instax/polaroid | 一次成像 |

**ISO 识别**
- 显式：`ISO200`、`200度`
- 隐式：`金200`、`GOLD200`、`CP200`、`UltraMax400`、`800T`、`HP5 Plus 400`

**有效期识别**
- 格式：`27年9月` → `2027-09`
- 年份范围：20-35 → 2020-2035

---

### 📁 项目结构

```
film-price-tracker/
├── app.py                  # Flask 入口
├── app_factory.py          # Flask 工厂
├── app_routes.py           # 路由（首页/详情/胶片管理/店铺管理/截图OCR）
├── config.py               # 配置（DB URI, Secret Key）
├── requirements.txt        # Python 依赖
├── start.ps1               # PowerShell 启动脚本（交互式菜单）
├── start.bat               # CMD 启动脚本
│
├── models/
│   ├── __init__.py
│   └── film.py             # ORM 模型：Film, PriceHistory, TaobaoStore
│
├── templates/
│   ├── base.html           # 布局模板（导航栏、主题切换）
│   ├── index.html          # 首页（双维度筛选：画幅+类型）
│   ├── film_detail.html    # 详情页（价格趋势图表）
│   ├── export.html         # 导出模板（自包含单文件 HTML）
│   ├── films.html          # 胶片管理（卡片式布局）
│   ├── stores.html         # 店铺管理（卡片式+批量导入）
│   └── upload.html         # 截图识别（粘贴/拖拽/上传+胶片匹配）
│
└── static/css/style.css    # 全局样式（深色/浅色双主题）
```

---

### 🐛 修复

- **启动脚本闪退**：bat 文件中文乱码导致命令解析失败 → 改用英文输出
- **SQLAlchemy 兼容性**：2.0.25 不兼容 Python 3.14 → 升级到 2.0.51
- **临时文件冲突**：固定文件名 `temp_upload.png` 导致权限错误 → 改用 `tempfile.NamedTemporaryFile`
- **ISO 检测不全**：隐式 ISO（如 `金200`、`800T`）未识别 → 增加多种正则模式
- **运算符优先级**：`film_format and '拍立得' in film_format or '宝丽来' in film_format` → 加括号修复

---

### 📦 依赖

```
Flask>=3.0.2
SQLAlchemy>=2.0.51
Pillow>=10.0.0
rapidocr-onnxruntime>=1.2.0
```

---

### 🛤️ 路由总览

| 路由 | 方法 | 说明 |
|---|---|---|
| `/` | GET | 首页，胶卷列表（双维度筛选） |
| `/film/<id>` | GET | 胶卷详情 + 价格图表 |
| `/films` | GET | 胶片管理页面 |
| `/films/add` | POST | 添加胶片 |
| `/films/edit/<id>` | POST | 编辑胶片 |
| `/films/delete/<id>` | POST | 删除胶片 |
| `/stores` | GET | 店铺管理（卡片式+批量导入） |
| `/stores/add` | POST | 添加店铺 |
| `/stores/edit/<id>` | POST | 编辑店铺 |
| `/stores/delete/<id>` | POST | 删除店铺 |
| `/upload` | GET | 截图识别页面 |
| `/api/ocr` | POST | OCR 识别接口 |
| `/api/save` | POST | 保存识别结果（匹配胶片） |
| `/api/films/list` | GET | 胶片列表 JSON |
| `/api/films/match` | POST | 胶片匹配 API |
| `/api/stores/import` | POST | 批量导入店铺 |
| `/api/price_history/<film_id>` | GET | 价格历史 JSON API |
| `/export/json` | GET | 导出全部数据 JSON |
| `/export/html` | GET | 导出全部数据 HTML |
