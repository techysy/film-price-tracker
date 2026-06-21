# 启动胶卷价格追踪应用
Write-Host "启动胶卷价格追踪应用..." -ForegroundColor Cyan

# 检查是否安装了依赖
if (-not (Test-Path "requirements.txt")) {
    Write-Host "错误: 找不到 requirements.txt 文件" -ForegroundColor Red
    Read-Host "按 Enter 键退出..."
    exit 1
}

# 检查Python是否可用
Write-Host "检查 Python 版本..."
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 无法找到 Python，请确保已安装并添加到环境变量" -ForegroundColor Red
    Read-Host "按 Enter 键退出..."
    exit 1
}

# 检查虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
}

# 激活虚拟环境
Write-Host "激活虚拟环境..."
& ".\venv\Scripts\Activate.ps1"

# 安装依赖
Write-Host "安装依赖..."
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 依赖安装失败" -ForegroundColor Red
    Read-Host "按 Enter 键退出..."
    exit 1
}

# 检查 OCR 引擎
Write-Host "检查 OCR 引擎..."
python -c "from rapidocr_onnxruntime import RapidOCR; print('  OCR 引擎就绪')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: OCR 引擎未安装，截图识别功能将不可用" -ForegroundColor Yellow
}

# 启动Flask应用
Write-Host ""
Write-Host "启动 Flask 应用..." -ForegroundColor Cyan
Write-Host "访问 http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "按 Ctrl+C 停止" -ForegroundColor Gray
Write-Host ""
python app.py
