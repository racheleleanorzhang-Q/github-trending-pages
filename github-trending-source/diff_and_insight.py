#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增量解读脚本
1. 读取 data.json（当日榜单）
2. 对比 seen_repos.json，找出新项目
3. 对新项目调用 OpenClaw LLM 生成中文解读
4. 写入 insights.json（追加，不覆盖）
5. 更新 seen_repos.json
"""

import json
import os
import sys
from datetime import date
import anthropic

DATA_FILE     = "/workspace/github-trending/data.json"
SEEN_FILE     = "/workspace/github-trending/seen_repos.json"
INSIGHTS_FILE = "/workspace/github-trending/insights.json"
TODAY         = str(date.today())

def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default

def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def ask_llm(prompt):
    """调用 Anthropic Claude 生成文本"""
    try:
        client = anthropic.Anthropic(
            base_url=os.environ.get("ANTHROPIC_BASE_URL", "https://llm-gateway-proxy.inner.chj.cloud/llm-gateway"),
            api_key=os.environ.get("ANTHROPIC_AUTH_TOKEN", "123456")
        )
        msg = client.messages.create(
            model="aws-claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text.strip()
    except Exception as e:
        print(f"[WARN] LLM 调用失败: {e}", file=sys.stderr)
        return ""

def generate_insight(repo):
    """为单个项目生成解读"""
    name = repo["full_name"]
    desc = repo.get("description", "").replace(f"Star {name} ", "").strip()
    lang = repo.get("language", "") or "未知"
    pstars = repo.get("period_stars", 0)
    tstars = repo.get("total_stars", 0)

    prompt = f"""你是一位技术分析师，请对以下 GitHub 项目写一段简洁的中文解读（2-3句话），包含：项目价值/应用场景、为什么值得关注、所在技术赛道。直接输出解读文字，不要加项目名称前缀，不要加引号。

项目：{name}
描述：{desc}
语言：{lang}
今日新增星标：{pstars:,}
总星标：{tstars:,}"""

    insight = ask_llm(prompt)
    # 同时生成信号标签
    signal_prompt = f"用4个字以内概括这个项目所属的技术方向（如：AI Agent基础设施、金融AI量化、边端推理），只输出标签文字：\n项目：{name}\n描述：{desc}"
    signal = ask_llm(signal_prompt)
    return insight, signal

def main():
    data     = load_json(DATA_FILE, {})
    seen     = load_json(SEEN_FILE, {})
    insights = load_json(INSIGHTS_FILE, {})

    # 收集当日所有上榜项目
    all_repos = {}
    for section in ["daily", "weekly"]:
        for key in ["top10", "ai_top10"]:
            for r in data.get(section, {}).get(key, []):
                name = r["full_name"]
                if name not in all_repos:
                    all_repos[name] = r

    # 找新项目
    new_repos = {name: r for name, r in all_repos.items() if name not in seen}
    print(f"[INFO] 今日上榜 {len(all_repos)} 个项目，其中新项目 {len(new_repos)} 个")

    if not new_repos:
        print("[INFO] 无新项目，跳过 LLM 调用")
    else:
        for name, repo in new_repos.items():
            print(f"[INFO] 生成解读：{name} ...")
            insight_text, signal = generate_insight(repo)
            if insight_text:
                insights[name] = {
                    "first_seen": TODAY,
                    "signal": signal or "待分类",
                    "insight": insight_text
                }
                print(f"  → 解读完成，信号标签：{signal}")
            else:
                print(f"  → 解读失败，跳过")

    # 更新 seen_repos
    for name in all_repos:
        if name not in seen:
            seen[name] = TODAY

    save_json(SEEN_FILE, seen)
    save_json(INSIGHTS_FILE, insights)
    print(f"[INFO] 已更新 seen_repos.json（{len(seen)} 项）和 insights.json（{len(insights)} 项）")

    return len(new_repos)

if __name__ == "__main__":
    new_count = main()
    print(f"\n=== 完成：新增解读 {new_count} 个项目 ===")
