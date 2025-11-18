@echo off
chcp 65001 >nul
cd /d "%~dp0DjangoProject"
echo 正在激活虚拟环境并启动 Django 服务器...
call venv\Scripts\activate.bat
python manage.py runserver
pause

