@echo off
chcp 65001 > Nul


set QQBot="D:\Download\Github\FFF\bot.py"
set CQHTTP="D:\Program Files\CQHTTPGO1.0\go-cqhttp_windows_amd64.exe"


for %%a in (%QQBot%) do set ParentPath=%%~dpa
REM echo %ParentPath%
cd %ParentPath%
start cmd /K call %QQBot%


for %%a in (%CQHTTP%) do set ParentPath=%%~dpa
REM echo %ParentPath%
cd %ParentPath%
cmd /K call go-cqhttp_windows_amd64.exe -faststart




