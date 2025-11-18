@echo off
chcp 65001 >nul
echo ========================================
echo   多 LLM Agent 协作系统 - 服务启动脚本
echo ========================================
echo.

echo 请按照以下步骤启动服务：
echo.
echo 【终端 1】启动 Redis
echo   进入 Redis 目录，运行: redis-server.exe
echo.
echo 【终端 2】启动 Celery Worker
echo   cd DjangoProject
echo   venv\Scripts\activate
echo   celery -A dagenthub worker -l info -Q celery --pool=solo
echo.
echo 【终端 3】启动 Django 后端
echo   cd DjangoProject
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo 【终端 4】启动 Vue 前端
echo   cd DjangoProject\frontend
echo   npm run dev
echo.
echo 【终端 5】启动 LM Studio (可选)
echo   打开 LM Studio 软件并启动模型
echo.
echo ========================================
echo 访问地址: http://localhost:3000
echo ========================================
echo.
pause

