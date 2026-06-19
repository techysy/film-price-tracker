#!/bin/bash

# 启动胶卷价格追踪应用

echo "启动胶卷价格追踪应用..."

# 检查是否安装了依赖
if [ ! -f "requirements.txt" ]; then
    echo "错误: 找不到requirements.txt文件"
    exit 1
fi

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 启动定时任务
echo "启动定时任务..."
python scheduler.py &

# 启动Flask应用
echo "启动Flask应用..."
python app.py
