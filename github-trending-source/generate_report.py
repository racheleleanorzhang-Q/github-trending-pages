#!/usr/bin/env python3
# GitHub Trending HTML 日报生成脚本
import json
from datetime import datetime

def clean_desc(s):
    import re
    s = re.sub(r"Star [^/]+/[^\s]+ ", "", s)
    return s.strip()

def lang_class(lang):
    return "lang-" + lang if lang in ["Python","TypeScript","Rust","Kotlin"] else ""

def render_table(repos, period_label):
    rows = ""
    for i, r in enumerate(repos, 1):
        name = r["full_name"]
        repo_name = name.split("/")[1] if "/" in name else name
        owner = name.split("/")[0] if "/" in name else ""
        desc = clean_desc(r.get("description",""))[:80]
        lang = r.get("language","") or "—"
        lc = lang_class(lang)
        pstars = r.get("period_stars",0)
        tstars = r.get("total_stars",0)
        forks = r.get("forks",0)
        url = r.get("url","#")
        rank_cls = "rank top3" if i <= 3 else "rank"
        lc_str = f" {lc}" if lc else ""
        rows += f"""<tr><td class="{rank_cls}">{i}</td><td><a class="proj-name" href="{url}" target="_blank">{owner} / {repo_name}</a><div class="proj-sub">{desc}</div></td><td><span class="lang-tag{lc_str}">{lang}</span></td><td class="stars-new">+{pstars:,}</td><td class="stars">{tstars:,}</td><td>{forks:,}</td></tr>
"""
    return rows

with open("/workspace/github-trending/data.json", encoding="utf-8") as f:
    data = json.load(f)
