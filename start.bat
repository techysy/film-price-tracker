@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo 启动胶卷价格追踪应用...

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt --quiet

REM 检查 OCR 引擎
python -c "from rapidocr_onnxruntime import RapidOCR; print('  OCR 引擎就绪')" 2>nul
if errorlevel 1 (
    echo 警告: OCR 引擎未安装，截图识别功能将不可用
)

REM 启动Flask应用
echo.
echo 启动 Flask 应用...
echo 访问 http://127.0.0.1:5000
echo 按 Ctrl+C 停止
echo.
python app.py
