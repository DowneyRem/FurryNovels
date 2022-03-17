@echo off
chcp 65001 >nul
rem 切换成UTF8
rem 测试：Windows10
rem 部分空行用于更好地解析代码，请勿随意删除

set ver=1.0
title TXT合并(ver%ver%).bat
echo TXT合并批处理脚本 版本：%ver%
echo 制作者：唐门/唐尼瑞姆
echo 请将本文件放在含有以【阿拉伯数字】序号命名的单章小说文件夹中，双击即可批量合并TXT
echo 默认项：保存在【上级文件夹】并【直接退出】
echo.
echo.

set /p input=请输入1或2来选择合并后TXT的存放位置：（1）上级文件夹；（2）当前文件夹；（3）退出；
if "%input%"=="1" goto one
if "%input%"=="2" goto two
if "%input%"=="3" goto exit
if not "%input%"=="2" if not "%input%"=="3" goto one


:one
for %%a in ("%cd%") do set path=%%~dpa
for %%a in ("%cd%") do set name=%%~nxa
set "pathname=%path%%name%"

echo.
echo 正在按照以下顺序进行合并txt
echo 合并位置：【上级文件夹】
echo.
echo.
echo ——————————————
if exist %name%.txt del %name%.txt /f/s/q/a >nul >nul
if exist %pathname%.txt del %pathname%.txt /f/s/q/a >nul
copy *.txt "%pathname%.txt"
echo ——————————————
echo.
echo 上述txt已合并为：%name%.txt
echo 文件位置：%pathname%.txt
echo.
echo.

set /p input=请输入1或2来选择是否打开合并的TXT：（1）直接退出；（2）打开TXT；
if "%input%"=="1" exit
if "%input%"=="2" start notepad "%pathname%.txt" & exit
if not "%input%"=="2" exit


:two
for %%a in ("%cd%") do set path=%%~dpa
for %%a in ("%cd%") do set name=%%~nxa
set "pathname=%path%%name%"

set path=%cd%
for %%a in ("%cd%") do set name=%%~nxa
set "pathname=%path%\%name%"

echo.
echo 正在按照以下顺序进行合并txt
echo 文件位置：%pathname%.txt
echo.
echo.
echo ——————————————
if exist %name%.txt del %name%.txt /f/s/q/a >nul >nul
if exist %pathname%.txt del %pathname%.txt /f/s/q/a >nul
copy *.txt %name%.txt
echo ——————————————
echo.
echo 上述txt已合并为：%name%.txt
echo 文件位置：%pathname%.txt
echo.
echo.

set /p input=请输入1或2来选择是否打开合并的TXT：（1）直接退出；（2）打开TXT；
if "%input%"=="1" exit
if "%input%"=="2" start notepad "%pathname%.txt" & exit
if not "%input%"=="2" exit

