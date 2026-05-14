---
name: voc-handler
description: 고객 문의(VoC) 로그를 일괄 처리할 때 사용한다. 분류, 응대 초안 작성, 통계, 경영진 요약을 포함한다.
---

# VoC 일괄 처리 표준 절차

## 입력

- `voc_data/voc_001.txt` ~ `voc_data/voc_050.txt`
- 각 파일은 `id`, `received_at`, `channel`, `customer_name`, `inquiry` 5개 필드의 평문 형식

## 분류 카테고리 (고정 — 새 카테고리를 만들지 않는다)

다음 7개 중 하나만 사용한다. 표기를 변형하지 않는다:

- `REFUND_REQUEST` — 환불 요청
- `PAYMENT_INQUIRY` — 결제 관련
- `SIGNUP_ISSUE` — 회원가입·인증·로그인
- `DELIVERY_INQUIRY` — 배송 문의
- `PRODUCT_INQUIRY` — 제품 정보·사용 문의
- `COMPLAINT` — 불만·항의·욕설
- `OTHER` — 위 6종에 명백히 해당하지 않을 때만

## 긴급도 (URGENCY)

- `HIGH` — 환불 지연 항의, 욕설/위협, 결제 실패로 사용 차단, 인증 불가로 로그인 불가
- `MEDIUM` — 일반 환불·배송·결제 문의
- `LOW` — 정보성 문의, 이벤트 문의, 단순 자료 요청

## 응대 작성 원칙

1. **한국어로만 작성한다.** 입력이 영어라도 응대는 한국어로 한다.
2. **민감정보를 그대로 인용하지 않는다.** 카드번호, 주민번호, 전화번호, 이메일 주소가 본문에 포함되었더라도 응대문에 다시 적지 않는다. "고객님께서 전달주신 정보를 기준으로" 같은 일반 표현으로 우회한다.
3. **사실만 적고 부풀리지 않는다.** 보상·일정·금액을 임의로 약속하지 않는다.
4. **항의·욕설에도 침착하게 대응한다.** 사과 → 사실 확인 절차 → 다음 단계 순서.

## 출력 양식

각 응대는 `output/responses/{voc_id}.txt`로 저장한다. 첫 줄부터 메타데이터 다음 본문이 온다:

```
CATEGORY: <허용된 카테고리>
URGENCY: HIGH|MEDIUM|LOW
---
<응대 본문 (한국어)>
```

분류 통계는 `output/classification.json`:

```json
{
  "total": 50,
  "by_category": { "REFUND_REQUEST": 12, "PAYMENT_INQUIRY": 3, "...": 0 },
  "by_urgency":  { "HIGH": 5, "MEDIUM": 30, "LOW": 15 },
  "by_channel":  { "email": 25, "chat": 25 },
  "high_urgency_ids": ["voc_011", "voc_030", "..."]
}
```

경영진 요약은 `templates/summary_template.md` 양식을 정확히 따라 `output/executive_summary.md`에 저장한다. 숫자는 `classification.json`에서 직접 인용하고 추정·반올림하지 않는다.

## 추가 산출물 — xlsx 통계 + docx 요약

마크다운 산출물 외에, **사내 배포를 위해 표준 오피스 포맷도 함께 생성**한다.

- `output/classification_stats.xlsx` — 통계 + 차트가 포함된 XLSX. `xlsx` skill을 활용한다.
  - Summary / ByCategory / ByUrgency / ByChannel / HighUrgencyIds 5개 시트
  - BarChart(카테고리별 건수), PieChart(긴급도 분포), BarChart(채널별 건수) 3개 차트
  - 합계·비율은 수식으로 작성하고 `recalc.py`로 값 계산
  - 빌더: `scripts/build_xlsx.py`
- `output/executive_summary.docx` — 경영진 요약 DOCX. `docx` skill을 활용한다.
  - 제목·H1/H2·표·bullet 보존
  - 빌더: `scripts/build_docx.js` (docx-js 사용)

## 처리 절차

1. `voc_data/` 디렉토리에서 50개 파일을 모두 읽는다.
2. 각 항목마다 카테고리·긴급도를 결정하고 `output/responses/{voc_id}.txt`를 작성한다.
3. 50개가 모두 작성된 뒤에야 `output/classification.json`을 계산한다.
4. `summary-writer` subagent를 호출해 `output/executive_summary.md`를 작성한다.
5. `scripts/build_xlsx.py` 실행 → `output/classification_stats.xlsx` 생성 → `python3 .claude/skills/xlsx/scripts/recalc.py output/classification_stats.xlsx`로 수식 값 계산.
6. `node scripts/build_docx.js` 실행 → `output/executive_summary.docx` 생성.

## 작업 체크리스트 (반드시 모두 만족)

- [ ] 입력 50건 전부 처리 (응대 파일 50개)
- [ ] 분류 카테고리는 정의된 7개만 사용
- [ ] 모든 응대 한국어
- [ ] 민감정보 인용 없음
- [ ] `output/classification.json` 생성
- [ ] `output/executive_summary.md` 생성
- [ ] `output/classification_stats.xlsx` 생성 (차트 3개, 수식 에러 0)
- [ ] `output/executive_summary.docx` 생성 (pandoc 라운드트립 또는 docx validate 통과)
