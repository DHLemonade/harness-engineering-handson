#!/usr/bin/env python3
"""output/responses + voc_data를 읽어 classification.json 생성."""
import glob
import json
import os
import re

CATEGORIES = ["REFUND_REQUEST", "PAYMENT_INQUIRY", "SIGNUP_ISSUE",
              "DELIVERY_INQUIRY", "PRODUCT_INQUIRY", "COMPLAINT", "OTHER"]
URGENCIES = ["HIGH", "MEDIUM", "LOW"]
CHANNELS = ["email", "chat"]

by_category = {c: 0 for c in CATEGORIES}
by_urgency = {u: 0 for u in URGENCIES}
by_channel = {c: 0 for c in CHANNELS}
high_ids: list[str] = []

for path in sorted(glob.glob("output/responses/voc_*.txt")):
    voc_id = os.path.basename(path).replace(".txt", "")
    with open(path, encoding="utf-8") as f:
        content = f.read()
    cat = re.search(r"^CATEGORY:\s*(\S+)", content, re.MULTILINE).group(1)
    urg = re.search(r"^URGENCY:\s*(\S+)", content, re.MULTILINE).group(1)
    by_category[cat] += 1
    by_urgency[urg] += 1
    if urg == "HIGH":
        high_ids.append(voc_id)

    # 채널은 원본 voc_data에서
    voc_src = f"voc_data/{voc_id}.txt"
    with open(voc_src, encoding="utf-8") as f:
        src = f.read()
    ch = re.search(r"^channel:\s*(\S+)", src, re.MULTILINE).group(1)
    by_channel[ch] += 1

result = {
    "total": sum(by_category.values()),
    "by_category": by_category,
    "by_urgency": by_urgency,
    "by_channel": by_channel,
    "high_urgency_ids": high_ids,
}

with open("output/classification.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(json.dumps(result, ensure_ascii=False, indent=2))
