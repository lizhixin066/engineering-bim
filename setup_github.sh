#!/bin/bash
# ============================================================
# Engineering BIM - GitHub 初始化脚本
# 用法: bash setup_github.sh <your-github-username>
# ============================================================

set -e

if [ -z "$1" ]; then
    echo "用法: bash setup_github.sh <github-username>"
    echo "示例: bash setup_github.sh myusername"
    exit 1
fi

USERNAME="$1"
REPO="engineering-bim"

echo "============================================================"
echo "  初始化并推送 engineering-bim 到 GitHub"
echo "============================================================"
echo ""

# 初始化 Git 仓库
git init
echo "[OK] Git 仓库已初始化"

# 添加所有文件
git add .
echo "[OK] 文件已暂存"

# 首次提交
git commit -m "feat: initial commit - engineering-bim skill framework"
echo "[OK] 初始提交完成"

# 添加远程仓库
git remote add origin "https://github.com/${USERNAME}/${REPO}.git"
echo "[OK] 远程仓库已配置"

# 设置主分支
git branch -M main

# 推送到 GitHub
echo ""
echo "正在推送到 GitHub..."
git push -u origin main

echo ""
echo "============================================================"
echo "  推送成功！"
echo "  仓库地址: https://github.com/${USERNAME}/${REPO}"
echo "============================================================"