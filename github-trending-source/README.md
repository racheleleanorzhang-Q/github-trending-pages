# GitHub Trending 日报项目

## 📖 项目简介

这是一个用于**自动抓取 GitHub Trending 热门项目并生成每日日报**的轻量脚本集。  
每天自动执行以下流程：

1. **抓取** GitHub Trending 每日 & 每周热门项目
2. **对比** 历史数据，识别新增项目
3. **生成洞察** 对新增项目进行一句话解读
4. **生成 HTML** 生成美观的可视化日报页面
5. **推送更新** 自动推送到 GitHub Pages 仓库发布

## 📁 目录结构

```
github-trending-source/
├── README.md              # 本文档
├── requirements.txt       # Python 依赖
├── .gitignore             # Git 忽略规则
│
├── run_daily.sh           # 🚀 主入口：一键运行全流程
├── auto_update.sh         # 🔄 定时自动更新脚本
│
├── fetch_trending.py      # 🕷️ 数据抓取
├── diff_and_insight.py    # 🔍 差异对比 & 洞察生成
├── generate_html.py       # 🎨 HTML 页面生成
├── generate_report.py     # 📊 报告生成（可选）
│
├── data.json              # 当前抓取数据
├── insights.json          # 洞察数据
├── seen_repos.json        # 历史项目追踪记录
└── github_trending.html   # 生成的 HTML 日报
```

## 🚀 快速开始

### 前置要求

- Python 3.7+
- Git

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行完整流程

```bash
bash run_daily.sh
```

运行后会自动执行：
1. 抓取 GitHub Trending 数据 → `data.json`
2. 对比并生成洞察 → `insights.json`
3. 生成 HTML 日报 → `github_trending.html`
4. 推送更新到 GitHub Pages

## ⚙️ 配置说明

### GitHub Token

如果你需要自动推送更新，请在 `run_daily.sh` 或 `auto_update.sh` 中设置你的 GitHub Token：

```bash
export GITHUB_TOKEN=your_token_here
```

或者在脚本里直接替换 `GITHUB_USERNAME` 和仓库地址。

### 定时任务（可选）

如果你想每天自动运行，可以添加 cron 任务：

```bash
crontab -e
# 每天早上 9 点运行
0 9 * * * /path/to/auto_update.sh >> /path/to/update.log 2>&1
```

## 🎨 输出示例

生成的 `github_trending.html` 是一个完整的静态页面，包含：

- 今日 Top 3 热门项目
- 每日 & 每周完整列表
- 新增项目解读
- 一键跳转到 GitHub 仓库

## 📝 数据说明

- `data.json`：当天抓取的所有项目数据
- `insights.json`：每个新增项目的一句话洞察
- `seen_repos.json`：已记录项目的历史，用于判断哪些是"新增"

## ⚠️ 注意事项

- GitHub Trending 页面结构可能变化，如果抓取失败可能需要调整 `fetch_trending.py`
- `data.json` / `insights.json` / `seen_repos.json` 已在 `.gitignore` 中排除
- HTML 页面会包含所有数据（内联）
