@echo off
cd /d C:\nginx-1.28.0
start nginx.exe

cd /d C:\PYTHON\Redis-x64-5.0.14.1
start redis-server.exe redis.conf

cd /d C:\Vue\Anime-Site-Project\Backend
call venv\Scripts\activate
cd taskmanager

start cmd /k celery -A taskmanager worker --pool=solo --loglevel=info

start cmd /k python manage.py runserver 0.0.0.0:8000

