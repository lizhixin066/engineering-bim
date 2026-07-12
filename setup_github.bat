@echo off
REM ============================================================
REM Engineering BIM - GitHub 初始化脚本
REM 用法: setup_github.bat <your-github-username>
REM 示例: setup_github.bat myusername
REM ============================================================

if "%1"=="" (
    echo 用法: setup_github.bat ^<github-username^>
    echo 示例: setup_github.bat myusername
    exit /b 1
)

set USERNAME=%1
set REPO=engineering-bim

echo ============================================================
echo   初始化并推送 engineering-bim 到 GitHub
echo ============================================================
echo.

REM 初始化 Git 仓库
git init
echo [OK] Git 仓库已初始化

REM 添加所有文件
git add .
echo [OK] 文件已暂存

REM 首次提交
git commit -m "feat: initial commit - engineering-bim skill framework"
echo [OK] 初始提交完成

REM 添加远程仓库
git remote add origin https://github.com/%USERNAME%/%REPO%.git
echo [OK] 远程仓库已配置

REM 设置主分支
git branch -M main

REM 推送到 GitHub
echo.
echo 正在推送到 GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo   推送成功！
    echo   仓库地址: https://github.com/%USERNAME%/%REPO%
    echo ============================================================
) else (
    echo.
    echo 推送失败。请确保:
    echo   1. 已在 GitHub 上创建仓库: %REPO%
    echo   2. 已配置 GitHub 认证
    echo   3. 网络连接正常
)