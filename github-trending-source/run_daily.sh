#!/bin/bash
# GitHub Trending 日报 - 每日自动刷新脚本
set -e
cd /workspace/github-trending

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始抓取 GitHub Trending..."
python3 fetch_trending.py

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 生成 HTML..."
python3 generate_html.py

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 推送到 GitLab Pages..."
TOKEN="1ARy9QFcShRhrTOt3Zdg2G86MQp1OmYzaQk.01.0z0lngfug"
REPO_DIR="/tmp/rachel2026"

if [ -d "$REPO_DIR" ]; then
  cd "$REPO_DIR" && git pull --rebase
else
  git clone "https://zhangrui3:${TOKEN}@gitlab.chehejia.com/zhangrui3/rachel2026.git" "$REPO_DIR"
  cd "$REPO_DIR"
fi

cp /workspace/github-trending/github_trending.html "$REPO_DIR/github_trending.html"
cd "$REPO_DIR"
git config user.email "rich@liwork.ai"
git config user.name "小R"
git add github_trending.html
git diff --staged --quiet || git commit -m "chore: 自动更新 GitHub Trending $(date '+%Y-%m-%d')"
git push origin master

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 推送到 GitHub Pages..."
GITHUB_TOKEN="${GITHUB_TOKEN}"
GITHUB_REPO_DIR="/tmp/github-trending-pages"

if [ -d "$GITHUB_REPO_DIR" ]; then
  cd "$GITHUB_REPO_DIR" && git pull --rebase
else
  git clone "https://racheleleanorzhang-Q:${GITHUB_TOKEN}@github.com/racheleleanorzhang-Q/github-trending-pages.git" "$GITHUB_REPO_DIR"
  cd "$GITHUB_REPO_DIR"
fi

cp /workspace/github-trending/github_trending.html "$GITHUB_REPO_DIR/index.html"
cd "$GITHUB_REPO_DIR"
git config user.email "rich@liwork.ai"
git config user.name "小R"
git add index.html
git diff --staged --quiet || git commit -m "chore: 自动更新 GitHub Trending $(date '+%Y-%m-%d')"
git push origin main

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 完成！"
