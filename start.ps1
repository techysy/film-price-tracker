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
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python版本: $pythonVersion"
} catch [Exception] {
    Write-Host "错误: 无法找到Python，请确保Python已安装并添加到环境变量"
    Read-Host "按 Enter 键退出..."
    exit 1
}

# 检查pip是否可用
Write-Host "检查pip是否可用..."
try {
    $pipVersion = python -m pip --version 2>&1
    Write-Host "pip版本: $pipVersion"
} catch [Exception] {
    Write-Host "错误: 无法找到pip，请确保Python已正确安装"
    Read-Host "按 Enter 键退出..."
    exit 1
}

# 安装依赖
Write-Host "安装依赖..."
try {
    # 尝试使用--user参数安装
    Write-Host "尝试使用--user参数安装依赖..."
    python -m pip install --user -r requirements.txt
    Write-Host "依赖安装完成"
} catch [Exception] {
    Write-Host "错误: 依赖安装失败: $($_.Exception.Message)"
    Write-Host "请尝试以管理员身份运行终端，或者检查Python安装目录的权限"
    Read-Host "按 Enter 键退出..."
    exit 1
}

# 启动定时任务
Write-Host "启动定时任务..."
try {
    Start-Process python -ArgumentList "scheduler.py" -WorkingDirectory "$PWD"
    Write-Host "定时任务已启动"
} catch [Exception] {
    Write-Host "错误: 定时任务启动失败: $($_.Exception.Message)"
}

# 启动Flask应用
Write-Host "启动Flask应用..."
try {
    python app.py
} catch [Exception] {
    Write-Host "错误: Flask应用启动失败: $($_.Exception.Message)"
    Read-Host "按 Enter 键退出..."
    exit 1
}