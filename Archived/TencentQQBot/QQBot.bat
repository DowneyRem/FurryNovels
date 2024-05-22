@echo off
chcp 65001 > Nul

set Folder=%~dp0%
REM echo %Folder%
cd %Folder%

set QQBot="%Folder%Bot.py"
REM set QQBot="%Folder%task.py"
set CQHTTP="%Folder%GOCQHTTP\go-cqhttp_windows_amd64.exe"
REM echo %QQBot:"=%
REM echo %CQHTTP:"=%

for %%a in (%CQHTTP%) do set ParentPath=%%~dpa
REM echo %ParentPath%
cd %ParentPath%
start cmd /K call go-cqhttp_windows_amd64.exe -faststart

for %%a in (%QQBot%) do set ParentPath=%%~dpa
REM echo %ParentPath%
cd %ParentPath%
cmd /K call %QQBot%
start cmd /K call %QQBot%

