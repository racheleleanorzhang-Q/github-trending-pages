#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Trending 日报 HTML 生成脚本
读取 data.json + insights.json -> 生成 github_trending.html
解读按项目首次出现时间倒序排列
"""
import json, re
from datetime import datetime

DATA_FILE     = "/workspace/github-trending/data.json"
INSIGHTS_FILE = "/workspace/github-trending/insights.json"
OUTPUT_FILE   = "/workspace/github-trending/github_trending.html"

def load(path, default={}):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def clean(s):
    s = re.sub(r"Star [A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+ ", "", s or "")
    return s.strip()[:90]

def lc(lang):
    return " lang-"+lang if lang in ["Python","TypeScript","Rust","Kotlin","C++"] else ""

def table_rows(repos):
    out = ""
    for i, r in enumerate(repos, 1):
        n = r["full_name"]
        parts = n.split("/")
        owner = parts[0] if len(parts) > 1 else n
        repo  = parts[1] if len(parts) > 1 else n
        desc  = clean(r.get("description", ""))
        lang  = r.get("language", "") or "—"
        ps    = r.get("period_stars", 0)
        ts    = r.get("total_stars", 0)
        fk    = r.get("forks", 0)
        url   = r.get("url", "#")
        rc    = "rank top3" if i <= 3 else "rank"
        lcc   = lc(lang)
        out  += f'<tr><td class="{rc}">{i}</td><td><a class="proj-name" href="{url}" target="_blank">{owner} / {repo}</a><div class="proj-sub">{desc}</div></td><td><span class="lang-tag{lcc}">{lang}</span></td><td class="stars-new">+{ps:,}</td><td class="stars">{ts:,}</td><td>{fk:,}</td></tr>\n'
    return out

def insight_list(repos, insights):
    """生成解读列表，有解读的显示，没有的跳过"""
    out = ""
    for i, r in enumerate(repos[:5], 1):
        name = r["full_name"]
        repo_short = name.split("/")[1] if "/" in name else name
        info = insights.get(name)
        if not info:
            continue
        signal = info.get("signal", "")
        text   = info.get("insight", "")
        out += f'<div class="insight-item"><div class="insight-repo">#{i} {repo_short}{"  · " + signal if signal else ""}</div><div class="insight-text">{text}</div></div>\n'
    return out or '<div class="insight-item"><div class="insight-text">暂无解读</div></div>'

def signal_tags_from(repos, insights):
    """从榜单里收集信号标签"""
    signals = []
    seen_s = set()
    for r in repos:
        info = insights.get(r["full_name"])
        if info and info.get("signal"):
            s = info["signal"]
            if s not in seen_s:
                seen_s.add(s)
                signals.append(s)
    return signals[:5]

def invest_cards(insights):
    """按信号分组，生成投资信号卡片"""
    groups = {}
    for name, info in insights.items():
        s = info.get("signal", "其他")
        if s not in groups:
            groups[s] = []
        groups[s].append(name.split("/")[1] if "/" in name else name)

    # 按项目数量排序取前4
    top = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)[:4]
    bar_map = ["bar-strong", "bar-strong", "bar-mid", "bar-watch"]
    str_map = ["str-strong", "str-strong", "str-mid", "str-watch"]
    label_map = ["强", "强", "中", "观察中"]
    icons = ["🤖", "🛠️", "📱", "🎓"]

    out = ""
    for idx, (signal, projs) in enumerate(top):
        bar = bar_map[idx]
        strc = str_map[idx]
        label = label_map[idx]
        icon = icons[idx]
        proj_str = " · ".join(projs[:3])
        out += f'''<div class="invest-card">
  <div class="invest-dir">{icon} {signal}</div>
  <div class="invest-proj">代表项目：{proj_str}</div>
  <div class="invest-bar-wrap"><div class="invest-bar {bar}"></div></div>
  <div class="invest-strength {strc}">信号强度：{label}</div>
</div>\n'''
    return out


# ── 主程序 ──────────────────────────────────────────────
data     = load(DATA_FILE)
insights = load(INSIGHTS_FILE)

updated  = data.get("updated_at", "")
parts    = updated[:10].split("-") if updated else ["","",""]
date_nice = f"{parts[0]}年{parts[1]}月{parts[2]}日" if len(parts)==3 else updated[:10]
time_str  = updated[11:16] if len(updated) > 15 else ""

d_top = data.get("daily", {}).get("top10", [])
d_ai  = data.get("daily", {}).get("ai_top10", [])
w_top = data.get("weekly", {}).get("top10", [])

# 摘要
top3 = "、".join(r["full_name"].split("/")[1] for r in d_top[:3]) if d_top else ""
max_r = max(d_top, key=lambda r: r.get("period_stars",0)) if d_top else {}
max_s = max_r.get("period_stars", 0)
max_n = max_r.get("full_name","").split("/")[1] if max_r else ""
summary = f"今日热榜：{top3} 领衔，{max_n} 单日涨星 {max_s:,}"

# 解读区（倒序：按 first_seen 倒序排，所有有解读的项目）
sorted_insights = sorted(insights.items(), key=lambda x: x[1].get("first_seen",""), reverse=True)

insight_all_html = ""
for name, info in sorted_insights:
    repo_short = name.split("/")[1] if "/" in name else name
    signal = info.get("signal","")
    text   = info.get("insight","")
    first  = info.get("first_seen","")
    insight_all_html += f'<div class="insight-item"><div class="insight-repo">{repo_short}{"  · "+signal if signal else ""}  <span class="insight-date">首次上榜 {first}</span></div><div class="insight-text">{text}</div></div>\n'


CSS = """*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;background:#f5f5f0;color:#1a1a1a;line-height:1.7;}
.header{background:#fff;border-bottom:3px solid #1a1a1a;padding:24px 0 16px;text-align:center;}
.header-inner{max-width:960px;margin:0 auto;padding:0 24px;}
.header-top{display:flex;align-items:baseline;justify-content:center;gap:16px;margin-bottom:8px;}
.logo{font-size:28px;font-weight:900;letter-spacing:-1px;color:#1a1a1a;}
.logo span{color:#e63946;}
.date{font-size:14px;color:#666;border-left:1px solid #ccc;padding-left:16px;}
.summary{font-size:14px;color:#444;background:#fffbf0;border:1px solid #f0d060;border-radius:4px;padding:8px 16px;display:inline-block;margin-top:8px;}
.tabs{background:#fff;border-bottom:2px solid #eee;position:sticky;top:0;z-index:10;}
.tabs-inner{max-width:960px;margin:0 auto;padding:0 24px;display:flex;}
.tab{padding:14px 24px;font-size:15px;font-weight:600;color:#666;cursor:pointer;border-bottom:3px solid transparent;margin-bottom:-2px;transition:all .2s;}
.tab:hover{color:#1a1a1a;}
.tab.active{color:#e63946;border-bottom-color:#e63946;}
.content{max-width:960px;margin:0 auto;padding:32px 24px;}
.panel{display:none;}
.panel.active{display:block;}
.section{background:#fff;border:1px solid #e8e8e8;border-radius:4px;margin-bottom:24px;overflow:hidden;}
.section-header{padding:16px 20px;border-bottom:1px solid #f0f0f0;display:flex;align-items:center;gap:8px;}
.section-title{font-size:17px;font-weight:700;}
.section-icon{font-size:18px;}
table{width:100%;border-collapse:collapse;}
th{background:#fafafa;padding:10px 14px;text-align:left;font-size:13px;font-weight:600;color:#666;border-bottom:1px solid #eee;}
td{padding:12px 14px;font-size:14px;border-bottom:1px solid #f5f5f5;vertical-align:middle;}
tr:last-child td{border-bottom:none;}
tr:hover td{background:#fafffe;}
.rank{font-weight:700;color:#999;font-size:13px;width:36px;}
.rank.top3{color:#e63946;}
.proj-name{font-weight:600;color:#0066cc;text-decoration:none;}
.proj-name:hover{text-decoration:underline;}
.proj-sub{font-size:12px;color:#999;margin-top:2px;}
.lang-tag{display:inline-block;padding:2px 8px;border-radius:10px;font-size:12px;font-weight:500;background:#f0f0f0;color:#555;}
.lang-Python{background:#e8f4fd;color:#2980b9;}
.lang-TypeScript{background:#e8f8f0;color:#27ae60;}
.lang-Rust{background:#fdf0e8;color:#e67e22;}
.lang-Kotlin{background:#f0e8fd;color:#8e44ad;}
.stars{font-weight:600;color:#f39c12;}
.stars-new{color:#e63946;font-weight:700;}
.insight-list{padding:20px;}
.insight-item{margin-bottom:20px;padding-bottom:20px;border-bottom:1px solid #f5f5f5;}
.insight-item:last-child{border-bottom:none;margin-bottom:0;padding-bottom:0;}
.insight-repo{font-size:13px;font-weight:700;color:#e63946;margin-bottom:6px;}
.insight-date{font-weight:400;color:#aaa;font-size:12px;}
.insight-text{font-size:14px;color:#333;line-height:1.8;}
.signal-tags{padding:20px;display:flex;flex-wrap:wrap;gap:10px;}
.signal-tag{padding:6px 14px;border-radius:20px;font-size:13px;font-weight:600;}
.tag-hot{background:#ffeef0;color:#e63946;border:1px solid #ffcdd2;}
.tag-rising{background:#fff8e1;color:#f57c00;border:1px solid #ffe082;}
.tag-watch{background:#e8f5e9;color:#2e7d32;border:1px solid #c8e6c9;}
.invest-cards{padding:20px;display:grid;grid-template-columns:repeat(2,1fr);gap:16px;}
.invest-card{border:1px solid #e8e8e8;border-radius:6px;padding:16px;}
.invest-dir{font-size:15px;font-weight:700;margin-bottom:8px;}
.invest-proj{font-size:12px;color:#666;margin-bottom:8px;}
.invest-bar-wrap{background:#f0f0f0;border-radius:4px;height:6px;margin-bottom:10px;}
.invest-bar{height:6px;border-radius:4px;}
.bar-strong{background:#e63946;width:90%;}
.bar-mid{background:#f39c12;width:60%;}
.bar-watch{background:#27ae60;width:35%;}
.invest-strength{font-size:12px;margin-bottom:4px;}
.str-strong{color:#e63946;font-weight:700;}
.str-mid{color:#f39c12;font-weight:700;}
.str-watch{color:#27ae60;font-weight:700;}
.footer{text-align:center;padding:24px;color:#aaa;font-size:12px;border-top:1px solid #eee;margin-top:8px;}
@media(max-width:640px){.invest-cards{grid-template-columns:1fr;}.tab{padding:10px 14px;font-size:13px;}}"""


# Signal tags
d_sigs = signal_tags_from(d_top, insights)
ai_sigs = signal_tags_from(d_ai, insights)
tag_styles = ["tag-hot","tag-hot","tag-rising","tag-rising","tag-watch"]
icons_sig = ["🔥","🔥","📈","📈","👀"]
def render_tags(sigs):
    out=""
    for i,s in enumerate(sigs):
        ic = icons_sig[min(i,4)]
        tc = tag_styles[min(i,4)]
        out += f'<span class="signal-tag {tc}">{ic} {s}</span>\n'
    return out or '<span class="signal-tag tag-watch">👀 暂无信号</span>'

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>GitHub Trending 日报</title>
<style>{CSS}</style>
</head>
<body>
<div class="header">
<div class="header-inner">
  <div class="header-top">
    <div class="logo">GitHub <span>Trending</span> 日报</div>
    <div class="date">{date_nice} · 数据更新于 {time_str}</div>
  </div>
  <div class="summary">📌 {summary}</div>
</div>
</div>
<div class="tabs">
<div class="tabs-inner">
  <div class="tab active" onclick="showTab(0)">📊 今日全站热榜</div>
  <div class="tab" onclick="showTab(1)">🤖 AI / ML 专题</div>
  <div class="tab" onclick="showTab(2)">📈 本周趋势 &amp; 投资信号</div>
  <div class="tab" onclick="showTab(3)">📚 历史解读库</div>
</div>
</div>
<div class="content">

<div class="panel active" id="panel-0">
  <div class="section">
    <div class="section-header"><span class="section-icon">🏆</span><span class="section-title">榜单总览</span></div>
    <table><thead><tr><th>#</th><th>项目</th><th>语言</th><th>今日新增 ⭐</th><th>总 ⭐</th><th>Forks</th></tr></thead>
    <tbody>{table_rows(d_top)}</tbody></table>
  </div>
  <div class="section">
    <div class="section-header"><span class="section-icon">📝</span><span class="section-title">深度解读 · Top 5</span></div>
    <div class="insight-list">{insight_list(d_top, insights)}</div>
  </div>
  <div class="section">
    <div class="section-header"><span class="section-icon">📡</span><span class="section-title">今日技术信号</span></div>
    <div class="signal-tags">{render_tags(d_sigs)}</div>
  </div>
</div>

<div class="panel" id="panel-1">
  <div class="section">
    <div class="section-header"><span class="section-icon">🤖</span><span class="section-title">AI / ML 今日热榜</span></div>
    <table><thead><tr><th>#</th><th>项目</th><th>语言</th><th>今日新增 ⭐</th><th>总 ⭐</th><th>Forks</th></tr></thead>
    <tbody>{table_rows(d_ai)}</tbody></table>
  </div>
  <div class="section">
    <div class="section-header"><span class="section-icon">🔬</span><span class="section-title">AI 视角深度解读 · Top 5</span></div>
    <div class="insight-list">{insight_list(d_ai, insights)}</div>
  </div>
  <div class="section">
    <div class="section-header"><span class="section-icon">📡</span><span class="section-title">AI 今日核心信号</span></div>
    <div class="signal-tags">{render_tags(ai_sigs)}</div>
  </div>
</div>

<div class="panel" id="panel-2">
  <div class="section">
    <div class="section-header"><span class="section-icon">📅</span><span class="section-title">本周全站热榜</span></div>
    <table><thead><tr><th>#</th><th>项目</th><th>语言</th><th>本周新增 ⭐</th><th>总 ⭐</th><th>Forks</th></tr></thead>
    <tbody>{table_rows(w_top)}</tbody></table>
  </div>
  <div class="section">
    <div class="section-header"><span class="section-icon">📝</span><span class="section-title">本周深度解读 · Top 5</span></div>
    <div class="insight-list">{insight_list(w_top, insights)}</div>
  </div>
  <div class="section">
    <div class="section-header"><span class="section-icon">💡</span><span class="section-title">本周投资信号拆解</span></div>
    <div class="invest-cards">{invest_cards(insights)}</div>
  </div>
</div>

<div class="panel" id="panel-3">
  <div class="section">
    <div class="section-header"><span class="section-icon">📚</span><span class="section-title">历史解读库 · 按首次上榜时间倒序</span></div>
    <div class="insight-list">{insight_all_html}</div>
  </div>
</div>

</div>
<div class="footer">数据来源：GitHub Trending · 更新于 {updated} · 由 小R 自动生成</div>
<script>
function showTab(idx){{
  document.querySelectorAll(".tab").forEach((t,i)=>t.classList.toggle("active",i===idx));
  document.querySelectorAll(".panel").forEach((p,i)=>p.classList.toggle("active",i===idx));
}}
</script>
</body></html>"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"✅ 生成完成：{OUTPUT_FILE}（{len(HTML):,} 字节）")
