@echo off
chcp 65001 >nul
echo ========================================
echo    Node.js 配置检查工具
echo ========================================
echo.

echo [1] 检查 node 命令...
where.exe node >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] node 命令可用
    node --version
) else (
    echo [错误] node 命令不可用
    echo 尝试使用完整路径: F:\nodejs\node.exe
    if exist "F:\nodejs\node.exe" (
        echo [找到] F:\nodejs\node.exe
        "F:\nodejs\node.exe" --version
    ) else (
        echo [未找到] F:\nodejs\node.exe
    )
)

echo.
echo [2] 检查 npm 命令...
where.exe npm >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] npm 命令可用
    npm --version
) else (
    echo [错误] npm 命令不可用
    echo 尝试使用完整路径: F:\nodejs\npm.cmd
    if exist "F:\nodejs\npm.cmd" (
        echo [找到] F:\nodejs\npm.cmd
        "F:\nodejs\npm.cmd" --version
    ) else (
        echo [未找到] F:\nodejs\npm.cmd
    )
)

echo.
echo [3] 检查 PATH 环境变量中的 Node.js 路径...
echo %PATH% | findstr /i "node" >nul
if %errorlevel% equ 0 (
    echo [找到] PATH 中包含 Node.js 相关路径:
    echo %PATH% | findstr /i "node"
) else (
    echo [警告] PATH 中未找到 Node.js 路径
    echo 建议: 将 F:\nodejs\ 添加到系统 PATH 环境变量
)

echo.
echo ========================================
pause

