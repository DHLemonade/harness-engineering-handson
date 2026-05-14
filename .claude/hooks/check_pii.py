#!/usr/bin/env python3
"""응대 초안에 카드번호·주민번호·전화번호·이메일이 그대로 포함되면 차단한다."""
import json
import os
import re
import sys

data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
file_path = tool_input.get("file_path", "")

# 응대 파일에만 적용
if not file_path.endswith(".txt") or "/responses/" not in file_path:
    sys.exit(0)
if not os.path.exists(file_path):
    sys.exit(0)

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 메타데이터(첫 구분선 위)는 제외, 응대 본문만 검사
body = content.split("---", 1)[1] if "---" in content else content

patterns = {
    "카드번호": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "주민번호": r"\b\d{6}[\s-]?[1-4]\d{6}\b",
    "전화번호": r"\b01[0-9]-?\d{3,4}-?\d{4}\b",
    "이메일":   r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
}

violations = []
for name, pattern in patterns.items():
    m = re.search(pattern, body)
    if m:
        violations.append(f"{name}: '{m.group(0)}'")

if violations:
    print(f"🚨 PII 차단: {file_path}", file=sys.stderr)
    for v in violations:
        print(f"   - {v}", file=sys.stderr)
    print("정책: 응대 본문에 민감정보를 그대로 인용하면 안 됩니다.", file=sys.stderr)
    print("우회: '고객님께서 알려주신 정보를 기준으로' 같은 일반 표현 사용.", file=sys.stderr)
    sys.exit(2)

sys.exit(0)
