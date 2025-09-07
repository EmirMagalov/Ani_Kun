@echo off
cd /d C:\nginx-1.28.0
start nginx.exe
cd /d C:\PYTHON\Redis-x64-5.0.14.1
start redis-server.exe redis.conf