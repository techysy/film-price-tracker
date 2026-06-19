# 胶卷价格追踪应用

## 项目介绍

这是一个胶卷价格追踪应用，用于监控不同平台上胶卷的价格变化，并通过Web界面展示价格历史趋势。

## 技术栈

- Python 3.8+
- Flask (Web框架)
- Scrapy (爬虫)
- SQLAlchemy (ORM)
- APScheduler (定时任务)

## 快速开始

### 前提条件

- Python 3.8+ 已安装
- pip 已安装并配置

### Windows环境启动指南

由于Windows环境的特殊性，以下提供两种启动方式：

#### 方法1：使用PowerShell脚本

1. 打开PowerShell终端
2. 导航到项目目录：
   ```powershell
   cd f:\Files\GitHub Files\film-price-tracker
   ```
3. 执行启动脚本：
   ```powershell
   powershell -ExecutionPolicy Bypass -File start.ps1
   ```

#### 方法2：使用cmd.exe

1. 打开cmd.exe终端
2. 导航到项目目录：
   ```cmd
   cd f:\Files\GitHub Files\film-price-tracker
   ```
3. 执行启动脚本：
   ```cmd
   start.bat
   ```

#### 方法3：手动启动

1. 安装依赖：
   ```powershell
   python -m pip install -r requirements.txt
   ```
2. 启动定时任务：
   ```powershell
   python scheduler.py
   ```
3. 启动Flask应用：
   ```powershell
   python app.py
   ```

## 访问应用

启动成功后，在浏览器中访问：
```
http://localhost:5000
```

## 常见问题

### 1. Python命令无法识别

**解决方案**：
- 确保Python已安装
- 确保Python已添加到系统环境变量
- 尝试使用完整的Python路径，例如：
  ```powershell
  C:\Python39\python.exe app.py
  ```

### 2. pip命令无法识别

**解决方案**：
- 使用`python -m pip`代替`pip`，例如：
  ```powershell
  python -m pip install -r requirements.txt
  ```

### 3. Flask应用无法启动

**解决方案**：
- 检查依赖是否已正确安装
- 检查端口5000是否被占用
- 尝试使用不同的端口，修改app.py中的端口配置

### 4. 爬虫无法运行

**解决方案**：
- 检查scheduler.py中的路径配置是否正确
- 确保Scrapy已正确安装
- 尝试手动运行爬虫：
  ```powershell
  scrapy crawl jd
  ```

## 项目结构

```
film-price-tracker/
├── film_price_tracker/  # Scrapy项目配置
│   └── settings.py
├── models/  # 数据模型
│   ├── __init__.py
│   └── film.py
├── spiders/  # 爬虫
│   ├── base_spider.py
│   └── jd_spider.py
├── templates/  # 前端模板
│   ├── film_detail.html
│   └── index.html
├── app.py  # Flask应用
├── requirements.txt  # 依赖
├── scheduler.py  # 定时任务
├── scrapy.cfg  # Scrapy配置
├── start.bat  # Windows启动脚本
└── start.ps1  # PowerShell启动脚本
```

## 功能说明

- **首页**：展示所有监控的胶卷列表
- **胶卷详情页**：展示胶卷的价格历史趋势图表
- **定时任务**：每天凌晨2点自动运行爬虫抓取价格数据
- **API接口**：提供价格历史数据的API访问

## 扩展建议

- 添加更多平台的爬虫（淘宝、亚马逊等）
- 实现价格提醒功能
- 添加用户认证系统
- 优化前端界面
