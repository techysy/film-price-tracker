# 🎞️ 胶卷价格追踪应用

基于 OCR 截图识别的胶卷价格追踪工具。📸 粘贴或上传淘宝购物车截图，自动匹配数据库已有胶片，记录价格并展示趋势图表。

支持 🌙 深色 / ☀️ 浅色 / 🔄 跟随系统主题切换，按画幅和类型双维度筛选胶卷。

## ✨ 功能特点

- 📸 **截图识别**：支持 Ctrl+V 粘贴、拖拽、点击上传购物车截图
- 🔍 **OCR 识别**：基于 RapidOCR 自动提取商品名称和价格
- 🎞️ **胶片管理**：预录入胶片库，OCR 识别后自动匹配
- 📊 **价格趋势**：Chart.js 折线图展示各店铺价格历史
- 🎨 **主题切换**：深色 / 浅色 / 跟随系统，偏好本地保存
- 📁 **双维度筛选**：按画幅 + 类型组合筛选胶卷
- 📦 **数据导出**：下拉菜单导出为 JSON / 自包含 HTML 文件
- 🏪 **店铺管理**：管理淘宝店铺列表，支持批量导入
- 🔗 **快速跳转**：一键访问店铺网页

## 🛠️ 技术栈

- 🐍 Python 3.8+
- 🌐 Flask — Web 框架
- 🗄️ SQLAlchemy — ORM，SQLite 持久化
- 🔤 RapidOCR (ONNX Runtime) — 图片文字识别
- 🖼️ Pillow — 图片处理
- 🎨 Bootstrap 5 + Chart.js — 前端

## 🚀 快速开始

### 📦 安装依赖

```powershell
# 建议使用虚拟环境
python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### ▶️ 启动应用

```powershell
python app.py
```

🌐 浏览器访问 `http://127.0.0.1:5001`

### 🔧 方式二：PowerShell 脚本（推荐）

```powershell
.\start.ps1                  # 显示交互式菜单
.\start.ps1 -Action start    # 前台启动
.\start.ps1 -Action start-bg # 后台启动
.\start.ps1 -Action stop     # 停止服务
.\start.ps1 -Action status   # 查看状态
```

菜单选项：

| 按键 | 功能 |
|---|---|
| `S` | ▶️ 前台启动 |
| `B` | 🔙 后台启动（不占用终端） |
| `T` | ⏹️ 停止服务 |
| `C` | 📋 查看状态 |
| `Q` | 🚪 退出 |

### 🖱️ 方式三：CMD 双击启动

双击 `start.bat`，自动创建虚拟环境、安装依赖并启动。

## 📖 使用方法

### 📸 截图识别

1. 在淘宝购物车页面截图（或复制截图到剪贴板）
2. 点击导航栏「截图识别」
3. 粘贴 (Ctrl+V)、拖拽或点击上传截图
4. 点击「开始识别」，系统自动提取商品名称和价格
5. 系统自动匹配数据库中的胶片，匹配失败可手动选择
6. 确认无误后点击「确认保存」，数据写入数据库

### 🎞️ 胶片管理

访问 `/films` 管理胶片库：

- ➕ 添加胶片（品牌、型号、画幅、类型、ISO）
- ✏️ 编辑胶片信息
- 🗑️ 删除胶片（同时清除关联价格记录）
- 📊 按品牌分色显示头像（柯达黄/富士绿/伊尔福灰）

### 🏪 店铺管理

访问 `/stores` 管理淘宝店铺：

- ➕ 单个添加店铺
- 📋 **批量导入**：粘贴表格数据（Tab 分隔），自动识别名称和链接
- ✏️ 编辑店铺信息
- 🔗 快速跳转访问店铺网页

### 📦 导出

首页或详情页点击导出下拉菜单：

- 📄 **JSON** — 结构化数据，包含胶卷信息和价格记录
- 🌐 **HTML** — 自包含单文件，内联 CSS + Chart.js，可部署到 GitHub Pages

## 📁 项目结构

```
film-price-tracker/
├── 📄 app.py                  # Flask 入口
├── 🏭 app_factory.py          # Flask 工厂
├── 🛤️ app_routes.py           # 路由（首页/详情/胶片管理/店铺管理/截图OCR）
├── ⚙️ config.py               # 配置（DB URI, Secret Key）
├── 📋 requirements.txt        # Python 依赖
├── 🔵 start.ps1               # PowerShell 启动脚本（交互式菜单）
├── 🟢 start.bat               # CMD 启动脚本
├── 📋 更新日志.md              # 更新日志
│
├── 📂 models/
│   ├── __init__.py
│   └── 🎞️ film.py             # ORM 模型：Film, PriceHistory, TaobaoStore
│
├── 📂 templates/
│   ├── 🏠 base.html           # 布局模板（导航栏、主题切换）
│   ├── 📋 index.html          # 首页（双维度筛选：画幅+类型）
│   ├── 📊 film_detail.html    # 详情页（价格趋势图表）
│   ├── 📦 export.html         # 导出模板（自包含单文件 HTML）
│   ├── 🎞️ films.html          # 胶片管理（卡片式布局）
│   ├── 🏪 stores.html         # 店铺管理（卡片式+批量导入）
│   └── 📸 upload.html         # 截图识别（粘贴/拖拽/上传+胶片匹配）
│
└── 🎨 static/css/style.css    # 全局样式（深色/浅色双主题）
```

## 💾 数据模型

SQLite 数据库 `film_prices.db`，包含三张表：

### 🎞️ films（胶片信息）

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | Integer | 主键 |
| `brand` | String(50) | 品牌（柯达/富士/伊尔福等） |
| `model` | String(100) | 型号 |
| `iso` | Integer | 感光度（100/200/400/800） |
| `format` | String(20) | 画幅（35mm/120/拍立得Mini/宝丽来等） |
| `film_type` | String(30) | 类型（彩负/黑白/反转/电影卷/一次成像） |
| `expiry` | String(10) | 有效期（YYYY-MM） |
| `description` | String(255) | 描述 |
| `created_at` | DateTime | 创建时间 |

### 💰 price_histories（价格记录）

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | Integer | 主键 |
| `film_id` | Integer(FK) | 关联胶片 |
| `platform` | String(50) | 店铺名称 |
| `price` | Float | 价格 |
| `url` | String(255) | 商品链接 |
| `timestamp` | DateTime | 记录时间 |

### 🏪 taobao_stores（店铺记录）

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | Integer | 主键 |
| `name` | String(100) | 店铺名称 |
| `url` | String(500) | 店铺主页 URL |
| `created_at` | DateTime | 创建时间 |

## 🎯 功能详情

### 🏠 首页

- 🎞️ 胶卷卡片列表，点击进入详情
- 📐 **画幅筛选**：全部 / 135(35mm) / 120 / 拍立得 / 宝丽来 / 其他
- 🎞️ **类型筛选**：全部 / 彩负 / 黑白 / 反转 / 电影卷 / 一次成像
- 📦 导出下拉菜单（JSON / HTML）

### 📊 详情页

- 📝 胶卷基本信息（品牌、画幅、类型、ISO、有效期）
- 📈 统计卡片（监控店铺数、数据点数）
- 📉 Chart.js 折线图展示各店铺价格历史趋势
- 🎨 图表随主题切换实时更新

### 📸 截图识别 `/upload`

- 📋 支持 Ctrl+V 粘贴截图
- 🖱️ 支持拖拽上传图片
- 📁 支持点击选择文件
- 🔍 OCR 识别后自动匹配数据库胶片
- 🎯 匹配成功显示绿色标签，失败显示手动选择下拉框
- 💾 保存后提示成功数量和跳过数量

### 🎞️ 胶片管理 `/films`

- ➕ 添加胶片（品牌、型号、画幅、类型、ISO）
- ✏️ 编辑胶片信息
- 🗑️ 删除胶片（同时清除关联价格记录）
- 🔗 点击「详情」跳转胶卷详情页

### 🏪 店铺管理 `/stores`

- ➕ 添加淘宝店铺（名称 + 店铺主页 URL）
- 📋 **批量导入**：粘贴表格数据，自动识别名称和链接
- ✏️ 编辑店铺信息
- 🗑️ 删除店铺
- 🔗 快速跳转访问店铺

### 🎨 主题切换

导航栏右侧按钮循环切换：

- 🌙 深色模式
- ☀️ 浅色模式
- 🔄 跟随系统（自动匹配 `prefers-color-scheme`）

💾 偏好保存在 localStorage，页面加载无闪烁。

## 🛤️ 路由

| 路由 | 方法 | 说明 |
|---|---|---|
| `/` | GET | 🏠 首页，胶卷列表 |
| `/film/<id>` | GET | 📊 胶卷详情 + 价格图表 |
| `/films` | GET | 🎞️ 胶片管理页面 |
| `/films/add` | POST | ➕ 添加胶片 |
| `/films/edit/<id>` | POST | ✏️ 编辑胶片 |
| `/films/delete/<id>` | POST | 🗑️ 删除胶片 |
| `/stores` | GET | 🏪 店铺管理页面 |
| `/stores/add` | POST | ➕ 添加店铺 |
| `/stores/edit/<id>` | POST | ✏️ 编辑店铺 |
| `/stores/delete/<id>` | POST | 🗑️ 删除店铺 |
| `/upload` | GET | 📸 截图识别页面 |
| `/api/ocr` | POST | 🔤 OCR 识别接口 |
| `/api/save` | POST | 💾 保存识别结果 |
| `/api/films/list` | GET | 🎞️ 胶片列表 JSON |
| `/api/films/match` | POST | 🎯 胶片匹配 API |
| `/api/stores/import` | POST | 📋 批量导入店铺 |
| `/api/price_history/<film_id>` | GET | 📈 价格历史 JSON API |
| `/export/json` | GET | 📄 导出全部数据 JSON |
| `/export/html` | GET | 🌐 导出全部数据 HTML |

## 🔄 OCR 识别流程

📸 截图 → 🔤 OCR 提取文字 → 🔍 正则匹配价格 → 🎯 匹配数据库胶片 → 💾 保存到数据库

- 匹配成功：自动关联胶片，显示绿色标签
- 匹配失败：手动从下拉框选择胶片
- 未选择：自动跳过，提示跳过数量

## 🐛 已知问题

- **胶片类型与价格追踪逻辑重叠**：当前首页展示的胶卷列表与店铺管理是独立的，但正确逻辑应为「一种胶卷 → 对应多个店铺的价格」。目前 `price_histories.platform` 存的是店铺名称字符串，未关联 `taobao_stores` 表。后续需重构为：首页平铺展示所有店铺价格，胶卷详情页展示该胶卷在各店铺的价格对比。

## 📄 许可证

MIT License

---

**Made with ❤️ for 胶卷摄影爱好者**
