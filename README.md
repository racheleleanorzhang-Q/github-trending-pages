GitHub Trending 日报 · 业务逻辑
🗂️ 数据分层
数据层        文件                    内容            
原始榜单      data.json              每次抓取覆盖写入    
AI 解读库     insights.json          历史累积，只追加
上榜记录      seen_repos.json        去重用，只追加
最终页面      github_trending.html   每次全量重新生成

📊 榜单分类逻辑
数据来源： GitHub Trending 官网（非 API，直接抓 HTML）
抓取维度：
今日榜（since=daily）→ 取 Top 10
本周榜（since=weekly）→ 取 Top 10
AI 专榜筛选规则：
从全榜中过滤 full_name + description 包含约 40 个关键词的项目（如 llm / agent / rag / claude / embedding...），最多取 10 条

🤖 AI 解读生成逻辑（增量）
触发条件： 项目首次出现在榜单上（对比 seen_repos.json）
解读内容： 调用 Claude，每个项目生成约 100~150 字，格式固定为：
1. 项目是什么 / 解决什么问题
2. 为什么值得关注（技术价值/市场价值）
3. 所在赛道判断
设计意图： 同一个项目只解读一次，连续多天上榜不重复调用 LLM

📱 页面结构（4 个 Tab）
Tab                  数据来源                                 内容
今日全站热榜           data.daily.top10 + insights            榜单表格 + Top 5 解读 + 技术信号标签
AI/ML专题            data.daily.ai_top10 + insights          同上，仅 AI 项目
本周趋势 & 投资信号    data.weekly.top10 + insights           本周榜 + 投资方向卡片（由 LLM 归纳）
历史解读库            insights.json 全量                      按首次上榜时间倒序展示所有解读过的项目

⏰ 执行时序
每天定时触发 run_daily.sh
    ↓
fetch_trending.py     → 抓 GitHub，写 data.json
    ↓
diff_and_insight.py   → 增量对比，新项目调 LLM，写 insights.json
    ↓
generate_html.py      → 组装所有数据，生成 HTML
    ↓
git push              → 触发 GitLab Pages 自动部署

核心设计原则： 榜单数据每天全量刷新，AI 解读永久累积不重复生成，历史解读库随时间越来越丰富。
