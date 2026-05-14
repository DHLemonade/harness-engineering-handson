#!/usr/bin/env python3
"""응대 본문이 한국어인지 검증한다. 영어 단어가 7개 이상 연속이면 차단한다."""
import json
import os
import re
import sys

data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
file_path = tool_input.get("file_path", "")

if not file_path.endswith(".txt") or "/responses/" not in file_path:
    sys.exit(0)
if not os.path.exists(file_path):
    sys.exit(0)

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 본문만 검사 (메타데이터 제외)
body = content.split("---", 1)[1] if "---" in content else content

# 영어 단어가 7개 이상 연속하면 영어 문장으로 간주
english_run = re.findall(r"(?:[A-Za-z]+\s+){6,}[A-Za-z]+", body)
if english_run:
    print(f"🚨 언어 위반: {file_path} 응대 본문에 영어 문장이 포함됨", file=sys.stderr)
    snippet = english_run[0][:80]
    print(f"   발견: {snippet}...", file=sys.stderr)
    print("정책: 응대는 반드시 한국어로 작성합니다.", file=sys.stderr)
    sys.exit(2)

# 본문이 사실상 비어 있는지 확인 (한글 글자 0개)
korean_chars = re.findall(r"[가-힣]", body)
if len(korean_chars) < 10:
    print(f"🚨 본문 부족: {file_path} 응대 본문에 한국어가 거의 없습니다(<10자).", file=sys.stderr)
    sys.exit(2)

sys.exit(0)
