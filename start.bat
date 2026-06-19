@echo off

REM 启动胶卷价格追踪应用

echo 启动胶卷价格追踪应用...

REM 检查是否安装了依赖
if not exist "requirements.txt" (
    echo 错误: 找不到requirements.txt文件
    pause
    exit /b 1
)

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt

REM 启动定时任务
echo 启动定时任务...
start python scheduler.py

REM 启动Flask应用
echo 启动Flask应用...
python app.py
