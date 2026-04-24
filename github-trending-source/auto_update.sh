#!/bin/bash
# GitHub Trending 日报自动更新脚本
# 每天早上 9:00 执行

set -e
LOG="/workspace/github-trending/update.log"
TOKEN="1ARy9QFcShRhrTOt3Zdg2G86MQp1OmYzaQk.01.0z0lngfug"
REPO_DIR="/tmp/rachel2026"
HTML_FILE="/workspace/github-trending/github_trending.html"

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 开始更新 ===" >> "$LOG"

# 1. 抓取最新数据
echo "[1/4] 抓取 GitHub Trending 数据..." >> "$LOG"
cd /workspace/github-trending
python3 fetch_trending.py >> "$LOG" 2>&1

# 2. 重新生成 HTML
echo "[2/4] 生成日报 HTML..." >> "$LOG"
python3 generate_report.py >> "$LOG" 2>&1

# 3. 推送到 GitLab
echo "[3/4] 推送到 GitLab..." >> "$LOG"
if [ -d "$REPO_DIR" ]; then
  cd "$REPO_DIR" && git pull >> "$LOG" 2>&1
else
  git clone "https://zhangrui3:${TOKEN}@gitlab.chehejia.com/zhangrui3/rachel2026.git" "$REPO_DIR" >> "$LOG" 2>&1
fi

cp "$HTML_FILE" "$REPO_DIR/github_trending.html"
cd "$REPO_DIR"
git config user.email "rich@liwork.ai"
git config user.name "小R"
git add github_trending.html
git commit -m "chore: auto update GitHub Trending $(date '+%Y-%m-%d')" >> "$LOG" 2>&1
git push origin master >> "$LOG" 2>&1

echo "[4/4] 完成！" >> "$LOG"
echo "=== $(date '+%Y-%m-%d %H:%M:%S') 更新完成 ===" >> "$LOG"
