#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共享的增量解读逻辑。
不同 provider 只负责实现 ask_llm(prompt)。
"""

import json
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"
SEEN_FILE = BASE_DIR / "seen_repos.json"
INSIGHTS_FILE = BASE_DIR / "insights.json"
TODAY = str(date.today())


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def generate_insight(repo, ask_llm):
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
    signal_prompt = f"用4个字以内概括这个项目所属的技术方向（如：AI Agent基础设施、金融AI量化、边端推理），只输出标签文字：\n项目：{name}\n描述：{desc}"
    signal = ask_llm(signal_prompt)
    return insight, signal


def run(ask_llm):
    data = load_json(DATA_FILE, {})
    seen = load_json(SEEN_FILE, {})
    insights = load_json(INSIGHTS_FILE, {})

    all_repos = {}
    for section in ["daily", "weekly"]:
        for key in ["top10", "ai_top10"]:
            for repo in data.get(section, {}).get(key, []):
                name = repo["full_name"]
                if name not in all_repos:
                    all_repos[name] = repo

    new_repos = {name: repo for name, repo in all_repos.items() if name not in seen}
    print(f"[INFO] 今日上榜 {len(all_repos)} 个项目，其中新项目 {len(new_repos)} 个")

    success_names = set()
    failed_names = set()

    if not new_repos:
        print("[INFO] 无新项目，跳过 LLM 调用")
    else:
        for name, repo in new_repos.items():
            print(f"[INFO] 生成解读：{name} ...")
            insight_text, signal = generate_insight(repo, ask_llm)
            if insight_text:
                insights[name] = {
                    "first_seen": TODAY,
                    "signal": signal or "待分类",
                    "insight": insight_text,
                }
                success_names.add(name)
                print(f"  -> 解读完成，信号标签：{signal}")
            else:
                failed_names.add(name)
                print("  -> 解读失败，跳过")

    for name in all_repos:
        if name not in seen and name in success_names:
            seen[name] = TODAY

    save_json(SEEN_FILE, seen)
    save_json(INSIGHTS_FILE, insights)
    print(f"[INFO] 已更新 seen_repos.json（{len(seen)} 项）和 insights.json（{len(insights)} 项）")
    if failed_names:
        print(f"[WARN] 本轮有 {len(failed_names)} 个项目解读失败，保留为未完成状态以便后续重试")
    return len(new_repos), len(success_names), len(failed_names)
