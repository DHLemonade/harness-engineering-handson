#!/usr/bin/env python3
"""Stop hook — 작업 종료 직전에 50건 + 통계 + 요약이 모두 만들어졌는지 검증한다."""
import glob
import json
import os
import sys

# Stop hook은 stdin으로 이벤트 데이터를 받지만 우리는 파일 시스템 상태만 본다.
try:
    _ = json.load(sys.stdin)
except Exception:
    pass

RESPONSES_DIR = "output/responses"
EXPECTED_COUNT = 50

if not os.path.isdir(RESPONSES_DIR):
    print(f"🚨 응대 폴더 없음: {RESPONSES_DIR}", file=sys.stderr)
    print("작업을 계속하여 50건의 응대 초안을 생성하세요.", file=sys.stderr)
    sys.exit(2)

files = sorted(glob.glob(f"{RESPONSES_DIR}/voc_*.txt"))
n = len(files)

if n < EXPECTED_COUNT:
    existing_ids = {os.path.basename(p).replace(".txt", "") for p in files}
    expected_ids = {f"voc_{i:03d}" for i in range(1, EXPECTED_COUNT + 1)}
    missing = sorted(expected_ids - existing_ids)
    print(f"🚨 미완성: 응대 초안 {n}건만 생성됨 ({EXPECTED_COUNT}건 필요)", file=sys.stderr)
    print(f"누락된 voc_id ({len(missing)}개): {missing[:10]}{'...' if len(missing) > 10 else ''}", file=sys.stderr)
    print("작업을 계속해 누락 항목을 채우세요.", file=sys.stderr)
    sys.exit(2)

REQUIRED_ARTIFACTS = [
    ("output/classification.json",       "50건 응대를 기반으로 분류 통계 JSON을 생성하세요."),
    ("output/executive_summary.md",      "summary-writer subagent를 호출해 경영진 요약(md)을 작성하세요."),
    ("output/classification_stats.xlsx", "xlsx skill로 통계 + 차트가 포함된 XLSX를 생성하세요. (scripts/build_xlsx.py)"),
    ("output/executive_summary.docx",    "docx skill로 경영진 요약을 DOCX로 변환하세요. (scripts/build_docx.js)"),
]

missing = []
for path, hint in REQUIRED_ARTIFACTS:
    if not os.path.exists(path):
        missing.append((path, hint))

if missing:
    print(f"🚨 미완성: {len(missing)}개 산출물 누락", file=sys.stderr)
    for path, hint in missing:
        print(f"   - {path}", file=sys.stderr)
        print(f"     → {hint}", file=sys.stderr)
    sys.exit(2)

print(
    f"✅ 결과물 완성 확인: 응대 {n}건 + classification.json + executive_summary.md "
    f"+ classification_stats.xlsx + executive_summary.docx",
    file=sys.stderr,
)
sys.exit(0)
