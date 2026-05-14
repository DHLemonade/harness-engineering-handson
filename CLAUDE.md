# 프로젝트 컨텍스트

VoC 50건을 일괄 처리하는 작업이다.

입력은 `voc_data/voc_001.txt` ~ `voc_data/voc_050.txt` 50개 파일.
각 파일은 다음 형식의 평문이다:

```
id: voc_001
received_at: 2026-05-06 09:12
channel: email
customer_name: 김민준
inquiry: <고객 문의 본문>
```

산출물은 다섯 가지다:

1. `output/responses/{voc_id}.txt` — voc_id별 응대 초안 (50개 파일)
2. `output/classification.json` — 카테고리·긴급도·채널별 통계
3. `output/executive_summary.md` — 경영진 보고용 요약 (마크다운 원본)
4. `output/classification_stats.xlsx` — 통계 + 차트(xlsx skill 사용)
5. `output/executive_summary.docx` — 경영진 요약 DOCX(docx skill 사용)

## 규칙

- VoC 처리 요청 시 `voc-handler` skill을 자동 활용한다.
- 모든 응대는 한국어로 작성한다.
- 응대 본문에 카드번호·주민번호·전화번호·이메일 같은 민감정보를 그대로 인용하지 않는다.
- 분류 카테고리는 SKILL.md에 정의된 6개(+OTHER) 외에 임의로 만들지 않는다.
- 50건 전체를 처리하기 전에 `완료` 보고를 하지 않는다.
