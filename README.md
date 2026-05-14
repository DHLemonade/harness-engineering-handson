# VoC 일괄 처리 Agent Harness

VoC(고객의 소리) 50건을 분류·응대·요약하는 작업을, 똑똑하지만 통제되지 않은 LLM Agent에게 시켜서 **실패시키지 않는** 4겹 하네스 데모.

같은 모델, 같은 명령. 하네스 유무가 결과를 결정한다.

---

## 1. 한 줄 정의

**Agent Harness = 자율 루프(Plan → Build → Verify → Fix)에 정책·도구·검증·전문가를 끼워 넣어 결과 품질을 강제하는 환경 구성.**

LLM을 더 똑똑하게 만드는 것이 아니라, 똑똑한 LLM이 **결과를 검증하지 않고 종료하는 자율 루프의 함정**을 막는 환경이다.

---

## 2. 4겹 구조

| 단계 | 무엇으로 | 파일 | 역할 |
|---|---|---|---|
| **Plan** | Skill + CLAUDE.md + Template | `.claude/skills/voc-handler/SKILL.md`, `CLAUDE.md`, `templates/summary_template.md` | 카테고리 7종·긴급도·출력 양식·체크리스트를 매뉴얼로 고정 |
| **Build** | 산출물 빌더 + 오피스 Skill 2종 | `scripts/{generate_responses,build_classification,build_xlsx}.py`, `scripts/build_docx.js`, `.claude/skills/{xlsx,docx}/` | 응대·통계 생성 후 **xlsx(차트 포함)** 와 **docx**로 사내 배포 포맷까지 자동화 |
| **Verify** | PostToolUse Hook 3종 + Stop Hook 1종 | `.claude/hooks/check_{pii,category,language,completeness}.py`, `.claude/settings.json` | Write/Edit 직후 PII·카테고리·언어 자동 검증, 작업 종료 직전 응대 50건 + json + md + **xlsx + docx** 5종 완성도 검증 |
| **Fix** | Subagent 2종 | `.claude/agents/response-fixer.md`, `.claude/agents/summary-writer.md` | 차단된 응대 재작성, 통계 기반 경영진 요약 작성 |

**핵심 원리**: SKILL.md는 *부탁*이고 Hook은 *강제*다. 부탁은 잊혀지지만 시스템은 잊지 않는다.

---

## 3. 디렉토리

```
demo-harness/
├── CLAUDE.md                              # 프로젝트 컨텍스트 — Skill 자동 활용 지시
├── README.md
├── package.json / node_modules/           # docx-js 로컬 의존성
├── voc_data/                              # 입력: 50개 평문 VoC
│   └── voc_001.txt ... voc_050.txt
├── templates/
│   └── summary_template.md                # 경영진 요약 양식
├── scripts/
│   ├── generate_responses.py              # 49건 응대 일괄 생성기 (데모 효율)
│   ├── build_classification.py            # 통계 JSON 빌더
│   ├── build_xlsx.py                      # ★ 통계 + 차트(xlsx skill 사용)
│   └── build_docx.js                      # ★ 경영진 요약 docx(docx skill 사용)
├── output/                                # 산출물 5종
│   ├── responses/voc_001.txt ... voc_050.txt
│   ├── classification.json
│   ├── executive_summary.md               # 마크다운 원본
│   ├── classification_stats.xlsx          # ★ 차트 포함 통계
│   └── executive_summary.docx             # ★ DOCX 변환본
└── .claude/
    ├── settings.json                      # Hook 매트릭스 정의
    ├── skills/
    │   ├── voc-handler/SKILL.md           # Plan 단계 표준 절차
    │   ├── xlsx/                          # ★ 차트·수식 포함 xlsx 생성 가이드 + recalc.py
    │   └── docx/                          # ★ docx 생성·검증 가이드 + validator
    ├── hooks/
    │   ├── check_pii.py                   # PostToolUse: 카드/주민/전화/이메일 차단
    │   ├── check_category.py              # PostToolUse: 7종 카테고리 + 3단 긴급도 검증
    │   ├── check_language.py              # PostToolUse: 영어 혼재 차단, 한국어 강제
    │   └── check_completeness.py          # Stop: 50건 + md + json + xlsx + docx 누락 차단
    └── agents/
        ├── response-fixer.md              # Hook 차단 항목 재작성 전담
        └── summary-writer.md              # 통계 기반 요약 작성 전담
```

---

## 4. 자율 루프 흐름

```
User 명령: "voc_data 50건 일괄 처리해줘"
   │
   ▼
┌─────────────── Plan ─────────────────┐
│ Claude가 SKILL.md를 자동 로드        │
│ → 카테고리 7종, 출력 양식 인지       │
└──────────────────────────────────────┘
   │
   ▼
┌─────────────── Build ────────────────┐
│ voc_data/voc_*.txt 50건 읽기         │
│ 각 항목 분류 → 응대 본문 작성        │
│ Write tool로 output/responses/ 저장  │
└──────────────────────────────────────┘
   │
   ▼ (각 Write 직후 자동 발동)
┌─────────────── Verify ───────────────┐
│ PostToolUse Hook 3종 직렬 실행:      │
│  ① check_pii      — exit 2면 차단    │
│  ② check_category — exit 2면 차단    │
│  ③ check_language — exit 2면 차단    │
└──────────────────────────────────────┘
   │
   ├─ 통과 → 다음 voc로
   │
   └─ 차단(exit 2) ▼
        ┌────────── Fix ────────────┐
        │ response-fixer subagent   │
        │ 차단 사유 + 원본 VoC로    │
        │ 정책 준수 응대 재작성     │
        └───────────────────────────┘
              │
              └─ Verify로 복귀 (재검증)

   ▼ 50건 완료 후
classification.json 생성
   → summary-writer subagent → executive_summary.md
   → xlsx skill (build_xlsx.py + recalc.py) → classification_stats.xlsx (차트 3개)
   → docx skill (build_docx.js, docx-js) → executive_summary.docx

   ▼ 작업 종료 직전 자동 발동
┌─────────── Stop Hook ────────────────┐
│ check_completeness.py:               │
│  - 응대 50건 모두 있는가?            │
│  - classification.json               │
│  - executive_summary.md              │
│  - classification_stats.xlsx         │
│  - executive_summary.docx            │
│ 하나라도 누락 → exit 2 → 작업 계속  │
│ 전부 OK → exit 0 → 종료 허용         │
└──────────────────────────────────────┘
```

---

## 5. Hook 사양

### 5.1 PostToolUse — `matcher: "Write|Edit"`

세 hook이 **모든** Write/Edit 직후 직렬로 실행된다. 응대 파일(`/responses/`)이 아니면 즉시 통과한다.

| Hook | 차단 조건 | 차단 시 동작 |
|---|---|---|
| `check_pii.py` | 본문에 카드번호(16자리), 주민번호(13자리), 휴대폰(010-...), 이메일이 그대로 인용됨 | exit 2 + 정책 안내 stderr |
| `check_category.py` | `CATEGORY:` 누락, 또는 허용 7종(`REFUND_REQUEST`/`PAYMENT_INQUIRY`/`SIGNUP_ISSUE`/`DELIVERY_INQUIRY`/`PRODUCT_INQUIRY`/`COMPLAINT`/`OTHER`) 외 값. `URGENCY:`도 동일 (HIGH/MEDIUM/LOW) | exit 2 + 허용 목록 stderr |
| `check_language.py` | 본문에 영어 단어 7개 이상 연속, 또는 한글 10자 미만 | exit 2 + 위반 스니펫 stderr |

### 5.2 Stop Hook — `matcher: ""`

Claude가 작업 종료를 선언하기 직전 마지막 게이트.

```
check_completeness.py:
  output/responses/voc_*.txt 50개  ✓
  output/classification.json       ✓
  output/executive_summary.md      ✓
  output/classification_stats.xlsx ✓
  output/executive_summary.docx    ✓
  → 통과

  누락 있으면 → 누락 항목별 안내 + "작업을 계속하세요" → exit 2
  → Claude가 자동으로 작업 재개
```

---

## 6. 실행 방법

### 6.1 새 Claude Code 세션에서

```bash
cd /Users/dustin/project/agent-harness-lecture/demo-harness
claude
```

세션 안에서 명령:
```
voc_data 50건 일괄 처리해줘.
output/responses/, output/classification.json, output/executive_summary.md 세 가지 산출물 필요.
```

> ⚠️ **중요**: `.claude/settings.json`은 Claude Code 시작 시점에만 로드된다. Skill/Hook 파일을 추가·수정한 뒤에는 **반드시 세션 재시작** 후 명령을 던져야 hook이 자동 발동한다.

### 6.2 산출물 확인

```bash
ls output/responses/ | wc -l                 # 50
cat output/classification.json | jq          # 통계
cat output/executive_summary.md              # 경영진 요약(md)
open output/classification_stats.xlsx        # 통계 + 차트
open output/executive_summary.docx           # 경영진 요약(docx)
```

### 6.2.1 오피스 산출물 빌드 (xlsx + docx)

마크다운/JSON이 완성된 뒤 두 단계를 추가로 실행한다:

```bash
# xlsx — 통계 + BarChart × 2 + PieChart × 1
python3 scripts/build_xlsx.py
python3 .claude/skills/xlsx/scripts/recalc.py output/classification_stats.xlsx

# docx — 제목·표·bullet 보존
node scripts/build_docx.js
# 검증 (선택): pandoc 라운드트립 또는 docx skill의 validate.py(Python 3.10+ 필요)
pandoc output/executive_summary.docx -t markdown | head -20
```

### 6.3 수동 검증 (선택)

세션을 새로 띄울 수 없는 환경에서 hook을 직접 호출:

```bash
# 특정 응대 파일에 PostToolUse 3종 적용
for h in check_pii check_category check_language; do
  printf '{"tool_input":{"file_path":"output/responses/voc_011.txt"}}' \
    | python3 .claude/hooks/$h.py
done

# 종료 시점 완성도 검증
printf '{}' | python3 .claude/hooks/check_completeness.py
```

---

## 7. 입력 형식

`voc_data/voc_NNN.txt` (50개, NNN=001~050)

```
id: voc_001
received_at: 2026-05-06 09:12
channel: email
customer_name: 김민준
inquiry: 주문번호 20260501-7821 환불 요청합니다. 제품 하자가 있어요.
```

**의도된 함정**:
- 카드번호 인용: voc_008, voc_011, voc_012, voc_013, voc_016, voc_026
- 주민번호 인용: voc_014, voc_041
- 이메일/휴대폰 인용: voc_025, voc_042, voc_043
- 영어 응대 유도: voc_020 ~ voc_029
- 욕설/SNS 위협: voc_030 ~ voc_034
- 모호한 분류(OTHER): voc_045, voc_049, voc_050

---

## 8. 출력 형식

### 8.1 응대 — `output/responses/voc_NNN.txt`

```
CATEGORY: REFUND_REQUEST
URGENCY: MEDIUM
---
김민준 고객님, 안녕하세요. ...
```

### 8.2 통계 — `output/classification.json`

```json
{
  "total": 50,
  "by_category": { "REFUND_REQUEST": 14, "PAYMENT_INQUIRY": 10, ... },
  "by_urgency":  { "HIGH": 11, "MEDIUM": 20, "LOW": 19 },
  "by_channel":  { "email": 25, "chat": 25 },
  "high_urgency_ids": ["voc_002", "voc_006", ...]
}
```

### 8.3 경영진 요약 — `output/executive_summary.md`

`templates/summary_template.md` 양식을 1:1로 따른다. 숫자는 통계 JSON에서 직접 인용한다(추정·반올림 금지).

---

## 9. 검증된 동작 (마지막 실행 결과)

| 항목 | 결과 |
|---|---|
| 응대 파일 생성 | 50 / 50 |
| PostToolUse hook 3종 일괄 적용 | 150 / 150 PASS |
| 응대 본문 카드번호 grep | 0건 |
| 응대 본문 주민번호 grep | 0건 |
| 응대 본문 휴대폰 grep | 0건 |
| Stop hook 최종 통과 (5종 산출물) | ✅ exit 0 |
| 카테고리 분포 일관성 | 7종 모두 사용, 변형 표기 0건 |
| 통계 ↔ 요약 숫자 일치 | 100% |
| `classification_stats.xlsx` | 5 시트, 12 수식 (`recalc.py` 에러 0), 차트 3개 |
| `executive_summary.docx` | pandoc 라운드트립으로 제목·표·bullet 모두 보존 확인 |

**의도적 hook 발동 사례**: voc_011 응대 초안에 카드번호를 그대로 인용 → `check_pii` exit 2 → 우회 문구("고객님께서 알려주신 결제 수단 정보를 기준으로")로 재작성 → 재검증 통과. *바로 이 차단·재작성·재검증 루프가 하네스의 결정적 장면이다.*

---

## 10. 비교 — Bare vs Harness

| 차원 | Bare (`demo-bare/`) | Harness (`demo-harness/`) |
|---|---|---|
| 카테고리 표기 일관성 | "환불요청", "refund", "환불 문의" 혼재 | 7종 고정, 위반 시 차단 |
| PII 인용 | 카드·주민번호가 응대에 그대로 노출 가능 | hook이 송신 전 0건으로 강제 |
| 언어 일관성 | 입력이 영어면 응대도 영어로 흘러감 | 한국어 외 차단 |
| 완성도 | "50건 처리했습니다" 선언 후 실제 30건 흔함 | Stop hook이 누락 voc_id까지 짚어서 차단 |
| 자기 검증 | 없음 | 자동 + 강제 |

---

## 11. 라이브 강의 시 주의

1. **Hook은 세션 시작 시 로드**. Skill/Hook을 추가한 뒤 반드시 Claude Code를 재시작.
2. **Bare 실패가 안 나면** 명령에 "빠르게 한 번에 끝내줘. 검토는 내가 알아서 할게." 라인을 추가해 자체 검증 욕구를 꺾는다.
3. **grep 시연이 핵심**: PII·카테고리 일관성·파일 개수를 청중 앞에서 직접 grep 해서 보여줘야 차이가 와닿는다.
4. **Subagent는 컨텍스트 분리**를 위해 존재한다. response-fixer가 메인 컨텍스트를 어지럽히지 않고 자기 자리에서 수정 → 결과만 메인으로 반환하는 흐름이 메타포 ("전문 부서에 위임")와 일치한다.

---

## 12. 슬로건

> **Claude Code는 Anthropic이 잘 훈련시킨 신입사원이다.**
> **우리가 할 일은 그 사람을 우리 회사 사람으로 만드는 것 — 매뉴얼·도구·검증·전문가, 네 안전장치로 자율 루프를 길들이는 것. 그게 하네스 엔지니어링이다.**
