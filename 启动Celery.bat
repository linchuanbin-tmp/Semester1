@echo off
chcp 65001 >nul
cd /d "%~dp0DjangoProject"
echo 正在激活虚拟环境并启动 Celery Worker...
call venv\Scripts\activate.bat
celery -A dagenthub worker -l info -Q celery --pool=solo
pause

