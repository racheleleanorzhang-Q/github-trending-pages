#!/bin/bash
# GitHub Trending 日报 - 每日自动刷新脚本
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$SCRIPT_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始抓取 GitHub Trending..."
python3 fetch_trending.py

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 生成增量解读（Shell 层优先 Claude，失败回退 GPT）..."
if [ -n "${ANTHROPIC_AUTH_TOKEN:-${ANTHROPIC_API_KEY:-}}" ]; then
  if python3 diff_and_insight.py; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Claude 解读生成完成"
  else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] Claude 解读失败，切换 GPT"
    if python3 diff_and_insight_gpt.py; then
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] GPT 解读生成完成"
    else
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] GPT 解读也失败，继续生成 HTML"
    fi
  fi
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] 未配置 Claude 凭证，直接使用 GPT"
  if python3 diff_and_insight_gpt.py; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] GPT 解读生成完成"
  else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] GPT 解读也失败，继续生成 HTML"
  fi
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 生成 HTML..."
python3 generate_html.py
cp "$SCRIPT_DIR/github_trending.html" "$REPO_ROOT/index.html"

if [ "${GITHUB_ACTIONS:-false}" = "true" ] || [ "${SKIP_EXTERNAL_PUSH:-0}" = "1" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] CI 模式，跳过脚本内 push，由工作流统一提交"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] 已生成页面，请手动检查并提交变更"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 完成！"
