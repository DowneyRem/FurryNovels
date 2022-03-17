@echo off
chcp 65001 >nul
rem 切换成UTF8
rem 测试：Windows10
rem 部分空行用于更好地解析代码，请勿随意删除


set ver=1.6
title TXT合并(ver%ver%).bat
echo TXT合并批处理脚本 版本：%ver%
echo 制作者：唐门/唐尼瑞姆
echo 请将本文件放在含有以【阿拉伯数字】序号命名的单章小说文件夹中，双击即可批量合并TXT
echo 默认项：【添加合并时间】并保存在【上级文件夹】中并【不打开】合并后的TXT
echo.
echo.


set /p input=请输入1或2来选择是否要在合并的TXT中自动添加合并时间：（1）是；（2）否；（3）退出；
if "%input%"=="1" goto one
if "%input%"=="2" goto two
if "%input%"=="3" goto three
if not "%input%"=="2" if not "%input%"=="3" goto one


:one
echo 输出合并时间：【是】
echo.
echo.
set timefilename=第00章A 合并时间
if exist "%timefilename%.txt" del "%timefilename%.txt" /f/s/q/a >nul

echo 第00章 合并时间> "%timefilename%.txt"
echo 这是用Batch脚本自动合并的TXT合集>> "%timefilename%.txt"
echo TXT合并批处理脚本 版本：%ver%>> "%timefilename%.txt"
echo 合并时间：%date:~0,10%　%time:~0,5%>> "%timefilename%.txt"
echo.>> "%timefilename%.txt"
echo.>> "%timefilename%.txt"

set /p input=请输入1或2来选择合并后TXT的存放位置：（1）上级文件夹；（2）当前文件夹；（3）退出；
if "%input%"=="1" goto four
if "%input%"=="2" goto five
if "%input%"=="3" goto three
if not "%input%"=="2" if not "%input%"=="3" goto four


:two
echo 输出合并时间：【否】
echo.
echo.
set timefilename=第00章A 合并时间
if exist "%timefilename%.txt" del "%timefilename%.txt" /f/s/q/a >nul

set /p input=请输入1或2来选择合并后TXT的存放位置：（1）上级文件夹；（2）当前文件夹；（3）退出；
if "%input%"=="1" goto four
if "%input%"=="2" goto five
if "%input%"=="3" goto three
if not "%input%"=="2" if not "%input%"=="3" goto four


:four
for %%a in ("%cd%") do set path=%%~dpa
for %%a in ("%cd%") do set name=%%~nxa
set "pathname=%path%%name%"
echo 合并位置：【上级文件夹】
echo.
echo.
echo 正在按照以下顺序进行TXT合并：

echo ——————————————
if exist %name%.txt del %name%.txt /f/s/q/a >nul >nul
if exist %pathname%.txt del %pathname%.txt /f/s/q/a >nul
copy *.txt "%pathname%.txt"
if exist "%timefilename%.txt" del "%timefilename%.txt" /f/s/q/a >nul
echo ——————————————

echo 上述txt已合并为：%name%.txt
echo 文件位置：%pathname%.txt
echo.
echo.
set /p input=请输入1或2来选择是否打开合并的TXT：（1）直接退出；（2）打开TXT；（3）退出并删除合并TXT；
if "%input%"=="1" exit
if "%input%"=="2" start notepad "%pathname%.txt" & exit
if "%input%"=="3" goto three
if not "%input%"=="2" if not "%input%"=="3" exit


:five
set path=%cd%
for %%a in ("%cd%") do set name=%%~nxa
set "pathname=%path%\%name%"
echo 合并位置：【当前文件夹】
echo.
echo.
echo 正在按照以下顺序进行TXT合并：

echo ——————————————
if exist %name%.txt del %name%.txt /f/s/q/a >nul
copy *.txt "%name%.txt"
if exist "%timefilename%.txt" del "%timefilename%.txt" /f/s/q/a >nul
echo ——————————————

echo 上述txt已合并为：%name%.txt
echo 文件位置：%pathname%.txt
echo.
echo.
set /p input=请输入1或2来选择是否打开合并的TXT：（1）直接退出；（2）打开TXT；（3）删除合并TXT并退出；
if "%input%"=="1" exit
if "%input%"=="2" start notepad "%pathname%.txt" & exit
if "%input%"=="3" goto three
if not "%input%"=="2" if not "%input%"=="3" exit


:three
echo 删除相关文件并退出
set timefilename=第00章A 合并时间
if exist %name%.txt del %name%.txt /f/s/q/a >nul >nul
if exist "%pathname%.txt" del "%pathname%.txt" /f/s/q/a >nul
if exist "%timefilename%.txt" del "%timefilename%.txt" /f/s/q/a >nul
exit
