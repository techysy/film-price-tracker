# 胶卷价格追踪应用

实时监控淘宝店铺胶卷价格，通过 Web 界面查看历史趋势。支持深色/浅色/跟随系统主题切换，按画幅分类筛选胶卷。

## 技术栈

- Python 3.8+
- Flask — Web 框架
- Scrapy — 爬虫框架
- SQLAlchemy — ORM，SQLite 持久化
- APScheduler — 定时任务
- Bootstrap 5 + Chart.js — 前端

## 快速开始

### 安装依赖

```powershell
pip install -r requirements.txt
```

### 启动应用

```powershell
# 启动定时任务（后台）
python scheduler.py &

# 启动 Web 服务
python app.py
```

浏览器访问 `http://localhost:5001`

### 手动运行爬虫

```powershell
scrapy crawl taobao
```

## 项目结构

```
film-price-tracker/
├── app.py                  # Flask 入口
├── app_factory.py          # Flask 工厂
├── app_routes.py           # 路由（首页/详情/店铺管理）
├── config.py               # 配置（DB URI, Secret Key）
├── scheduler.py            # APScheduler 定时任务
├── scrapy.cfg              # Scrapy 配置
├── requirements.txt        # Python 依赖
│
├── models/
│   ├── __init__.py
│   └── film.py             # ORM 模型：Film, PriceHistory, TaobaoStore
│
├── spiders/
│   ├── __init__.py
│   ├── base_spider.py      # 爬虫基类（品牌识别、DB 写入）
│   └── taobao_spider.py    # 淘宝店铺爬虫（从 DB 读取店铺列表）
│
├── templates/
│   ├── base.html           # 布局模板（导航栏、主题切换）
│   ├── index.html          # 首页（胶卷列表、分类过滤）
│   ├── film_detail.html    # 详情页（价格趋势图表）
│   └── stores.html         # 店铺管理（增删改查）
│
└── static/css/style.css    # 全局样式（深色/浅色双主题）
```

## 数据模型

SQLite 数据库 `film_prices.db`，包含三张表：

| 表 | 字段 | 说明 |
|---|---|---|
| `films` | id, brand, model, iso, format, description | 胶卷信息 |
| `price_histories` | id, film_id(FK), platform, price, url, timestamp | 价格记录 |
| `taobao_stores` | id, name, url, enabled, created_at | 淘宝店铺配置 |

`platform` 字段存储店铺名称，与 `taobao_stores.name` 对应。

## 功能

### 首页

- 胶卷卡片列表，点击进入详情
- 分类过滤：全部 / 135(35mm) / 120 / 拍立得 / 宝丽来 / 其他
- 即时过滤，无需请求服务器

### 详情页

- 胶卷基本信息（ISO、画幅、描述）
- 统计卡片（监控店铺数、数据点数）
- Chart.js 折线图展示各店铺价格历史趋势
- 图表随主题切换实时更新

### 店铺管理 `/stores`

- 添加淘宝店铺（名称 + 店铺主页 URL）
- 编辑店铺信息、启用/禁用爬取
- 删除店铺

### 主题切换

导航栏右侧按钮循环切换：

- 深色模式
- 浅色模式
- 跟随系统（自动匹配 `prefers-color-scheme`）

偏好保存在 localStorage，页面加载无闪烁。

### 定时任务

每天凌晨 2:00 自动运行 `scrapy crawl taobao`，抓取所有启用店铺的胶卷商品价格。

## 路由

| 路由 | 方法 | 说明 |
|---|---|---|
| `/` | GET | 首页，胶卷列表 |
| `/film/<id>` | GET | 胶卷详情 + 价格图表 |
| `/stores` | GET | 店铺管理页面 |
| `/stores/add` | POST | 添加店铺 |
| `/stores/edit/<id>` | POST | 编辑店铺 |
| `/stores/delete/<id>` | POST | 删除店铺 |
| `/api/price_history/<film_id>` | GET | 价格历史 JSON API |

## 爬虫

### 淘宝爬虫 `taobao`

- 从 `taobao_stores` 表读取所有 `enabled=True` 的店铺
- 逐店爬取商品页面，识别胶卷品牌和型号
- 支持分页
- 自动识别：品牌、ISO、画幅（35mm / 120 / 拍立得 / 宝丽来）

### 支持的品牌

kodak/柯达, fujifilm/富士, ilford/伊尔福, agfa/爱克发, lomography/乐魔

### 识别的画幅关键词

| 关键词 | 归类 |
|---|---|
| `35mm`, `135` | 35mm |
| `120` | 120 |
| `instax`, `拍立得` | 拍立得 |
| `polaroid`, `宝丽来` | 宝丽来 |
