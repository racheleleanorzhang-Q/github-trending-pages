#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import anthropic

from insight_runner import run

def ask_llm(prompt):
    try:
        api_key = os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("[WARN] 未配置 ANTHROPIC_AUTH_TOKEN/ANTHROPIC_API_KEY，跳过 Claude", file=sys.stderr)
            return ""

        client = anthropic.Anthropic(
            base_url=os.environ.get("ANTHROPIC_BASE_URL", "https://llm-gateway-proxy.inner.chj.cloud/llm-gateway"),
            api_key=api_key
        )
        msg = client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", "aws-claude-sonnet-4-6"),
            max_tokens=int(os.environ.get("INSIGHT_MAX_TOKENS", "300")),
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text.strip()
    except Exception as e:
        print(f"[WARN] LLM 调用失败: {e}", file=sys.stderr)
        return ""

if __name__ == "__main__":
    new_count, success_count, failed_count = run(ask_llm)
    print(f"\n=== 完成：新增解读 {new_count} 个项目 ===")
    if failed_count:
        sys.exit(1)
