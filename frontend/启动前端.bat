@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动 Vue 前端开发服务器...

REM 检查 Node.js 是否在 PATH 中
where.exe node >nul 2>&1
if %errorlevel% neq 0 (
    REM 如果 node 不在 PATH 中，使用完整路径
    if exist "F:\nodejs\node.exe" (
        echo 使用 F:\nodejs\ 路径
        set "PATH=F:\nodejs\;%PATH%"
    ) else (
        echo [错误] 未找到 Node.js，请确保已安装 Node.js
        echo 或修改此脚本中的 Node.js 路径
        pause
        exit /b 1
    )
)

if not exist node_modules (
    echo 检测到 node_modules 不存在，正在安装依赖...
    call npm install
    if %errorlevel% neq 0 (
        echo [错误] npm install 失败
        pause
        exit /b 1
    )
)

echo 启动开发服务器...
call npm run dev
pause

