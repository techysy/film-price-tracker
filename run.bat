@echo off
chcp 65001 >nul

cd /d "%~dp0"

REM 简单的启动脚本

echo 检查Python是否可用...
python --version
if %errorlevel% neq 0 (
    echo 错误: 无法找到Python，请确保Python已安装并添加到环境变量
    pause
    exit /b 1
)

echo 检查pip是否可用...
python -m pip --version
if %errorlevel% neq 0 (
    echo 错误: 无法找到pip，请确保Python已正确安装
    pause
    exit /b 1
)

echo 安装依赖...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo 启动Flask应用...
python app.py