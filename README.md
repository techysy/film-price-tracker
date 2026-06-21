# 🎞️ 胶卷价格追踪应用

基于 OCR 截图识别的胶卷价格追踪工具。📸 粘贴或上传淘宝购物车截图，自动识别商品名称和价格，保存到数据库并展示趋势图表。

支持 🌙 深色 / ☀️ 浅色 / 🔄 跟随系统主题切换，按画幅分类筛选胶卷。

## ✨ 功能特点

- 📸 **截图识别**：支持 Ctrl+V 粘贴、拖拽、点击上传购物车截图
- 🔍 **OCR 识别**：基于 RapidOCR 自动提取商品名称和价格
- 📊 **价格趋势**：Chart.js 折线图展示各店铺价格历史
- 🎨 **主题切换**：深色 / 浅色 / 跟随系统，偏好本地保存
- 📁 **分类筛选**：按画幅分类（135/120/拍立得/宝丽来/其他）
- 📦 **数据导出**：支持导出为 JSON / 自包含 HTML 文件
- 🏪 **店铺管理**：管理淘宝店铺列表，快速跳转访问
- 🖥️ **交互式启动**：PowerShell 脚本支持菜单选择前台/后台运行

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
5. 确认无误后点击「确认保存」，数据写入数据库

### 🏪 店铺管理

访问 `/stores` 管理淘宝店铺列表（仅作为记录参考，不涉及自动抓取）。

### 📦 导出

首页或详情页点击导出按钮：

- 📄 **JSON** — 结构化数据，包含胶卷信息和价格记录
- 🌐 **HTML** — 自包含单文件，内联 CSS + Chart.js，可部署到 GitHub Pages

## 📁 项目结构

```
film-price-tracker/
├── 📄 app.py                  # Flask 入口
├── 🏭 app_factory.py          # Flask 工厂
├── 🛤️ app_routes.py           # 路由（首页/详情/店铺管理/截图OCR）
├── ⚙️ config.py               # 配置（DB URI, Secret Key）
├── 📋 requirements.txt        # Python 依赖
├── 🔵 start.ps1               # PowerShell 启动脚本（交互式菜单）
├── 🟢 start.bat               # CMD 启动脚本
│
├── 📂 models/
│   ├── __init__.py
│   └── 🎞️ film.py             # ORM 模型：Film, PriceHistory, TaobaoStore
│
├── 📂 templates/
│   ├── 🏠 base.html           # 布局模板（导航栏、主题切换）
│   ├── 📋 index.html          # 首页（胶卷列表、分类过滤、导出按钮）
│   ├── 📊 film_detail.html    # 详情页（价格趋势图表）
│   ├── 📦 export.html         # 导出模板（自包含单文件 HTML）
│   ├── 🏪 stores.html         # 店铺管理（卡片式布局）
│   └── 📸 upload.html         # 截图识别（粘贴/拖拽/上传）
│
└── 🎨 static/css/style.css    # 全局样式（深色/浅色双主题）
```

## 💾 数据模型

SQLite 数据库 `film_prices.db`，包含三张表：

| 表 | 字段 | 说明 |
|---|---|---|
| `films` | id, brand, model, iso, format, description | 🎞️ 胶卷信息 |
| `price_histories` | id, film_id(FK), platform, price, url, timestamp | 💰 价格记录 |
| `taobao_stores` | id, name, url, created_at | 🏪 店铺记录 |

## 🎯 功能详情

### 🏠 首页

- 🎞️ 胶卷卡片列表，点击进入详情
- 📁 分类过滤：全部 / 135(35mm) / 120 / 拍立得 / 宝丽来 / 其他
- 📦 批量导出所有胶卷数据（JSON / HTML）

### 📊 详情页

- 📝 胶卷基本信息（ISO、画幅、描述）
- 📈 统计卡片（监控店铺数、数据点数）
- 📉 Chart.js 折线图展示各店铺价格历史趋势
- 🎨 图表随主题切换实时更新

### 📸 截图识别 `/upload`

- 📋 支持 Ctrl+V 粘贴截图
- 🖱️ 支持拖拽上传图片
- 📁 支持点击选择文件
- 🔍 OCR 识别后展示商品列表，可逐条删除
- 💾 识别结果保存到 films + price_histories

### 🏪 店铺管理 `/stores`

- ➕ 添加淘宝店铺（名称 + 店铺主页 URL）
- ✏️ 编辑店铺信息
- 🗑️ 删除店铺
- 🔗 快速跳转访问店铺

### 📦 导出

- 📄 **JSON** — `/export/json`，结构化数据
- 🌐 **HTML** — `/export/html`，自包含文件，内联 CSS 变量 + 主题切换 JS

### 🎨 主题切换

导航栏右侧按钮循环切换：

- 🌙 深色模式
- ☀️ 海色模式
- 🔄 跟随系统（自动匹配 `prefers-color-scheme`）

💾 偏好保存在 localStorage，页面加载无闪烁。

## 🛤️ 路由

| 路由 | 方法 | 说明 |
|---|---|---|
| `/` | GET | 🏠 首页，胶卷列表 |
| `/film/<id>` | GET | 📊 胶卷详情 + 价格图表 |
| `/stores` | GET | 🏪 店铺管理页面 |
| `/stores/add` | POST | ➕ 添加店铺 |
| `/stores/edit/<id>` | POST | ✏️ 编辑店铺 |
| `/stores/delete/<id>` | POST | 🗑️ 删除店铺 |
| `/upload` | GET | 📸 截图识别页面 |
| `/api/ocr` | POST | 🔤 OCR 识别接口（base64 图片） |
| `/api/save` | POST | 💾 保存识别结果 |
| `/api/price_history/<film_id>` | GET | 📈 价格历史 JSON API |
| `/export/json` | GET | 📄 导出全部数据 JSON |
| `/export/html` | GET | 🌐 导出全部数据 HTML |

## 🔤 OCR 说明

使用 [RapidOCR](https://github.com/RapidAI/RapidOCR) (ONNX Runtime) 进行文字识别，无需安装 Tesseract。

支持的截图格式：

- 🛒 淘宝购物车截图（单店铺 / 多店铺混排）
- 📦 淘宝商品详情截图
- 🧾 淘宝订单截图

识别流程：📸 截图 → 🔤 OCR 提取文字 → 🔍 正则匹配价格 → 🏷️ 关键词匹配胶卷品牌 → 💾 保存到数据库

### 🏷️ 支持识别的胶卷品牌

Kodak/柯达, Fujifilm/富士, Ilford/伊尔福, Agfa/爱克发, Lomography/乐魔, ORWO, Cinestill, Fomapan, Ilford HP5, Ilford Delta, Wolfen, Flic Film 等

### 📐 识别的画幅关键词

| 关键词 | 归类 |
|---|---|
| `35mm`, `135` | 🎞️ 35mm |
| `120` | 📷 120 |
| `instax`, `拍立得` | 📸 拍立得 |
| `polaroid`, `宝丽来` | 🖼️ 宝丽来 |

## 📄 许可证

MIT License

---

**Made with ❤️ for 胶卷摄影爱好者**
