@echo off
chcp 65001 >nul
cd /d "%~dp0..\..\Redis"
echo 正在启动 Redis 服务器...
echo Redis 将在端口 6379 上运行
echo 按 Ctrl+C 停止 Redis 服务器
redis-server.exe
pause

