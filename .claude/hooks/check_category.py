#!/usr/bin/env python3
"""응대 초안의 CATEGORY가 허용 목록에 있는지, URGENCY 값이 유효한지 검증한다."""
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

ALLOWED_CATEGORIES = {
    "REFUND_REQUEST",
    "PAYMENT_INQUIRY",
    "SIGNUP_ISSUE",
    "DELIVERY_INQUIRY",
    "PRODUCT_INQUIRY",
    "COMPLAINT",
    "OTHER",
}
ALLOWED_URGENCY = {"HIGH", "MEDIUM", "LOW"}

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

cat_match = re.search(r"^CATEGORY:\s*(\S+)", content, re.MULTILINE)
urg_match = re.search(r"^URGENCY:\s*(\S+)", content, re.MULTILINE)

if not cat_match:
    print(f"🚨 메타데이터 누락: {file_path} 에 CATEGORY 줄 없음", file=sys.stderr)
    sys.exit(2)
if not urg_match:
    print(f"🚨 메타데이터 누락: {file_path} 에 URGENCY 줄 없음", file=sys.stderr)
    sys.exit(2)

cat = cat_match.group(1)
urg = urg_match.group(1)

if cat not in ALLOWED_CATEGORIES:
    print(f"🚨 카테고리 위반: {file_path} 의 '{cat}' 는 허용되지 않습니다.", file=sys.stderr)
    print(f"허용: {sorted(ALLOWED_CATEGORIES)}", file=sys.stderr)
    sys.exit(2)

if urg not in ALLOWED_URGENCY:
    print(f"🚨 긴급도 위반: {file_path} 의 '{urg}' 는 허용되지 않습니다.", file=sys.stderr)
    print(f"허용: {sorted(ALLOWED_URGENCY)}", file=sys.stderr)
    sys.exit(2)

sys.exit(0)
