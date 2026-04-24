# github-trending-source

这是 `github-trending` 项目的源码快照，来自当前用于生成 GitHub Trending 日报的脚本目录。

## 目录说明

- `fetch_trending.py`：抓取 GitHub Trending 数据
- `diff_and_insight.py`：对比历史数据并生成新增项目洞察
- `generate_html.py`：生成 HTML 日报页面
- `run_daily.sh`：日更主脚本
- `auto_update.sh`：自动更新脚本
- `data.json`：当前抓取结果
- `insights.json`：洞察结果
- `seen_repos.json`：历史项目记录
- `github_trending.html`：生成的 HTML 示例

## 本地运行

### 1. 安装依赖

确保环境里有：
- Python 3
- `requests`
- `beautifulsoup4`

例如：

```bash
pip install requests beautifulsoup4
```

### 2. 运行抓取与生成

```bash
python3 fetch_trending.py
python3 diff_and_insight.py
python3 generate_html.py
```

或者直接运行：

```bash
bash run_daily.sh
```

## 环境变量

如果你要推送到 GitHub，请设置：

```bash
export GITHUB_TOKEN=your_github_token
```

## 注意

当前目录是 **源码备份/快照**，不是独立仓库。
如果后续需要更规范的维护方式，建议把它拆成单独 repo。
