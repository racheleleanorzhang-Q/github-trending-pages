#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 OpenAI GPT 生成增量解读。
"""

import os
import sys

from openai import OpenAI

from insight_runner import run


def ask_llm(prompt):
    try:
        client_kwargs = {"api_key": os.environ["OPENAI_API_KEY"]}
        base_url = os.environ.get("OPENAI_BASE_URL")
        if base_url:
            client_kwargs["base_url"] = base_url

        client = OpenAI(**client_kwargs)
        resp = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[WARN] GPT 调用失败: {e}", file=sys.stderr)
        return ""


if __name__ == "__main__":
    new_count, success_count, failed_count = run(ask_llm)
    print(f"\n=== 完成：新增解读 {new_count} 个项目 ===")
    if failed_count:
        sys.exit(1)
