# 启动胶卷价格追踪应用
Write-Host "启动胶卷价格追踪应用..."

# 检查是否安装了依赖
if (-not (Test-Path "requirements.txt")) {
    Write-Host "错误: 找不到requirements.txt文件"
    Read-Host "按 Enter 键退出..."
    exit 1
}

# 检查Python是否可用
Write-Host "检查Python版本..."
python --version

# 检查pip是否可用
Write-Host "检查pip是否可用..."
python -m pip --version

# 安装依赖
Write-Host "安装依赖..."
python -m pip install --user -r requirements.txt

# 启动定时任务
Write-Host "启动定时任务..."
Start-Process python -ArgumentList "scheduler.py" -WorkingDirectory "$PWD"

# 启动Flask应用
Write-Host "启动Flask应用..."
python app.py