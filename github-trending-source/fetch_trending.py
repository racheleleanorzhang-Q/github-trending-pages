#!/usr/bin/env python3
"""
GitHub Trending 数据抓取脚本
抓取今日 + 本周 trending，区分全榜和 AI 专榜
输出：/workspace/github-trending/data.json
"""

import json
import re
import sys
import time
import subprocess
from datetime import datetime, timezone, timedelta

AI_KEYWORDS = [
    "ai", "llm", "gpt", "claude", "gemini", "agent", " ml ", "deep-learning",
    "machine-learning", "neural", "transformer", "diffusion", "stable-diffusion",
    "langchain", "openai", "anthropic", "mistral", "llama", "chatbot",
    "rag", "embedding", "vector", "inference", "training", "fine-tun",
    "copilot", "codegen", "code-generation", "multimodal", "vision-language",
    "text-to-", "whisper", "tts", "nlp",
    "hermes", "ollama", "litellm", "vllm", "pytorch", "tensorflow",
    "huggingface", "foundation model", "prompt", "rlhf", "sora",
    "image generation", "speech recognition", "language model",
    "agentic", "autonomous", "reasoning", "deepseek", "qwen", "kimi"
]

def fetch_url(url, retries=3):
    for i in range(retries):
        try:
            result = subprocess.run(
                ["curl", "-s", "--max-time", "20", "-A",
                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                 "-H", "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8",
                 url],
                capture_output=True, text=True, timeout=25
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout
            print(f"[WARN] curl attempt {i+1} failed: rc={result.returncode}", file=sys.stderr)
        except Exception as e:
            print(f"[WARN] attempt {i+1}: {e}", file=sys.stderr)
        if i < retries - 1:
            time.sleep(2)
    return ""

def parse_trending(html):
    """从 GitHub Trending 页面解析项目列表"""
    repos = []

    # 匹配每个 article.Box-row
    articles = re.findall(r'<article[^>]*class="[^"]*Box-row[^"]*"[^>]*>(.*?)</article>', html, re.DOTALL)
    print(f"[INFO] Found {len(articles)} article blocks", file=sys.stderr)

    for art in articles:
        try:
            # repo full name: href="/owner/repo"
            name_match = re.search(r'href="/([a-zA-Z0-9_.\-]+/[a-zA-Z0-9_.\-]+)"', art)
            if not name_match:
                continue
            full_name = name_match.group(1).strip()
            if full_name.count('/') != 1:
                continue

            # description - p tag with col-9 or text in article
            desc = ""
            desc_match = re.search(r'<p[^>]*>\s*(.*?)\s*</p>', art, re.DOTALL)
            if desc_match:
                desc = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip()
                desc = re.sub(r'\s+', ' ', desc)

            # language
            lang_match = re.search(r'itemprop="programmingLanguage"[^>]*>\s*([^<\n]+?)\s*<', art)
            language = lang_match.group(1).strip() if lang_match else ""

            # stars this period (today or this week)
            period_match = re.search(r'([\d,]+)\s+stars\s+(?:today|this\s+week)', art)
            period_stars = 0
            if period_match:
                period_stars = int(period_match.group(1).replace(",", ""))

            # total stars - look for stargazers link
            stars_match = re.search(
                r'href="/' + re.escape(full_name) + r'/stargazers"[^>]*>.*?<svg[^>]*>.*?</svg>\s*([\d,]+)',
                art, re.DOTALL
            )
            total_stars = 0
            if stars_match:
                total_stars = int(stars_match.group(1).replace(",", ""))

            # forks
            forks_match = re.search(
                r'href="/' + re.escape(full_name) + r'/forks"[^>]*>.*?<svg[^>]*>.*?</svg>\s*([\d,]+)',
                art, re.DOTALL
            )
            forks = 0
            if forks_match:
                forks = int(forks_match.group(1).replace(",", ""))

            repos.append({
                "full_name": full_name,
                "description": desc,
                "language": language,
                "total_stars": total_stars,
                "period_stars": period_stars,
                "forks": forks,
                "url": f"https://github.com/{full_name}",
            })
        except Exception as e:
            print(f"[WARN] parse error: {e}", file=sys.stderr)
            continue

    return repos

def is_ai_related(repo):
    """判断是否 AI 相关"""
    text = (repo["full_name"] + " " + repo["description"]).lower()
    for kw in AI_KEYWORDS:
        if kw in text:
            return True
    return False

def fetch_trending_data():
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz)

    print("[INFO] Fetching daily trending...", file=sys.stderr)
    daily_html = fetch_url("https://github.com/trending?since=daily")
    daily_repos = parse_trending(daily_html) if daily_html else []
    print(f"[INFO] Daily: {len(daily_repos)} repos found", file=sys.stderr)

    time.sleep(1)

    print("[INFO] Fetching weekly trending...", file=sys.stderr)
    weekly_html = fetch_url("https://github.com/trending?since=weekly")
    weekly_repos = parse_trending(weekly_html) if weekly_html else []
    print(f"[INFO] Weekly: {len(weekly_repos)} repos found", file=sys.stderr)

    # top 10
    daily_top10 = daily_repos[:10]
    weekly_top10 = weekly_repos[:10]

    # AI filtered
    daily_ai = [r for r in daily_repos if is_ai_related(r)][:10]
    weekly_ai = [r for r in weekly_repos if is_ai_related(r)][:10]

    print(f"[INFO] Daily AI: {len(daily_ai)}, Weekly AI: {len(weekly_ai)}", file=sys.stderr)

    data = {
        "updated_at": now.strftime("%Y-%m-%d %H:%M:%S GMT+8"),
        "updated_ts": int(now.timestamp()),
        "daily": {
            "top10": daily_top10,
            "ai_top10": daily_ai,
        },
        "weekly": {
            "top10": weekly_top10,
            "ai_top10": weekly_ai,
        }
    }

    out_path = "/workspace/github-trending/data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Data saved to {out_path}", file=sys.stderr)
    return data

if __name__ == "__main__":
    data = fetch_trending_data()
    # 打印摘要
    print(f"\n=== 抓取完成 ===")
    print(f"更新时间: {data['updated_at']}")
    print(f"今日全榜: {len(data['daily']['top10'])} 条")
    print(f"今日AI榜: {len(data['daily']['ai_top10'])} 条")
    print(f"本周全榜: {len(data['weekly']['top10'])} 条")
    print(f"本周AI榜: {len(data['weekly']['ai_top10'])} 条")
    if data['daily']['top10']:
        print(f"\n今日 Top 3:")
        for i, r in enumerate(data['daily']['top10'][:3], 1):
            print(f"  {i}. {r['full_name']} ⭐{r['period_stars']:,} today | {r['total_stars']:,} total")
