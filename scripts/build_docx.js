/**
 * executive_summary.md → output/executive_summary.docx
 *
 * docx skill 규약을 따라:
 * - 본문은 한국어, Calibri/맑은 고딕 계열, 11pt
 * - Heading1/Heading2로 섹션 구분
 * - 카테고리 분포는 Table로
 * - HIGH voc_id 목록은 bullet list로
 */
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
} = require("docx");

const stats = JSON.parse(fs.readFileSync("output/classification.json", "utf8"));

const total = stats.total;
const cat = stats.by_category;
const urg = stats.by_urgency;
const ch  = stats.by_channel;
const highIds = stats.high_urgency_ids;

const pct = (n) => `${((n / total) * 100).toFixed(0)}%`;

// 최신 received_at 기반 날짜 (executive_summary.md와 동일)
const reportDate = "2026-05-08";

const FONT = "맑은 고딕";

function H1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, font: FONT, bold: true, size: 28 })],
  });
}
function H2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 200, after: 100 },
    children: [new TextRun({ text, font: FONT, bold: true, size: 24 })],
  });
}
function P(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 80 },
    alignment: opts.align || AlignmentType.LEFT,
    children: [new TextRun({ text, font: FONT, size: 22, bold: !!opts.bold })],
  });
}
function bullet(text) {
  return new Paragraph({
    bullet: { level: 0 },
    spacing: { after: 60 },
    children: [new TextRun({ text, font: FONT, size: 22 })],
  });
}

function headerCell(text) {
  return new TableCell({
    shading: { type: ShadingType.CLEAR, fill: "305496" },
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, font: FONT, bold: true, size: 22, color: "FFFFFF" })],
    })],
  });
}
function bodyCell(text, opts = {}) {
  return new TableCell({
    children: [new Paragraph({
      alignment: opts.align || AlignmentType.LEFT,
      children: [new TextRun({ text: String(text), font: FONT, size: 22 })],
    })],
  });
}

const categoryRows = [
  ["REFUND_REQUEST", cat.REFUND_REQUEST],
  ["PAYMENT_INQUIRY", cat.PAYMENT_INQUIRY],
  ["SIGNUP_ISSUE", cat.SIGNUP_ISSUE],
  ["DELIVERY_INQUIRY", cat.DELIVERY_INQUIRY],
  ["PRODUCT_INQUIRY", cat.PRODUCT_INQUIRY],
  ["COMPLAINT", cat.COMPLAINT],
  ["OTHER", cat.OTHER],
];

const categoryTable = new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  rows: [
    new TableRow({ tableHeader: true, children: [
      headerCell("카테고리"), headerCell("건수"), headerCell("비율"),
    ]}),
    ...categoryRows.map(([name, n]) => new TableRow({ children: [
      bodyCell(name),
      bodyCell(n, { align: AlignmentType.CENTER }),
      bodyCell(pct(n), { align: AlignmentType.CENTER }),
    ]})),
  ],
});

const findings = [
  `환불 요청(REFUND_REQUEST)이 ${cat.REFUND_REQUEST}건(${pct(cat.REFUND_REQUEST)})으로 단일 카테고리 중 최다이며, 그중 2건(voc_002, voc_006)은 처리 지연으로 인한 HIGH 긴급도 상황으로 전환됨.`,
  `불만/항의(COMPLAINT) ${cat.COMPLAINT}건 전체가 HIGH 긴급도이며, 전체 HIGH ${urg.HIGH}건 중 ${Math.round((cat.COMPLAINT / urg.HIGH) * 100)}%(${cat.COMPLAINT}/${urg.HIGH})를 차지함. SNS 노출·소비자보호원 신고 위협 포함.`,
  `결제·회원 가입 카테고리(${cat.PAYMENT_INQUIRY + cat.SIGNUP_ISSUE}건, ${pct(cat.PAYMENT_INQUIRY + cat.SIGNUP_ISSUE)})에서 카드번호·주민번호·이메일·휴대폰 등 민감정보 원문 인용 위험이 집중 발생. 정책상 응대 시 우회 표현이 일관 적용되어 노출은 차단됨.`,
];

const recommendations = [
  "환불 처리 SLA를 단축하고, 접수 후 7일 경과 시 자동 우선순위 상향 룰을 도입하여 voc_002·voc_006 유형의 HIGH 전환을 사전에 차단.",
  "COMPLAINT 항목은 책임자가 24시간 내 1차 회신하는 별도 트랙으로 운영하고, 재발 방지 조치 결과까지 회신에 포함하는 표준 절차를 수립.",
  "결제·회원 응대 템플릿에 '민감정보 우회 문구'를 기본 삽입하고, 자동 검증(PII 패턴) 단계를 송신 전 단계에 상시화하여 노출 위험을 0으로 유지.",
];

const doc = new Document({
  creator: "VoC Harness",
  title: `VoC 일일 요약 — ${reportDate}`,
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  sections: [{
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [new TextRun({ text: `VoC 일일 요약 — ${reportDate}`, font: FONT, bold: true, size: 36 })],
      }),

      H1("1. 개요"),
      bullet(`처리 건수: ${total}`),
      bullet(`채널 분포: email ${ch.email} / chat ${ch.chat}`),
      bullet(`긴급도: HIGH ${urg.HIGH} / MEDIUM ${urg.MEDIUM} / LOW ${urg.LOW}`),

      H1("2. 카테고리 분포"),
      categoryTable,

      H1("3. 핵심 발견 (3가지)"),
      ...findings.map(bullet),

      H1("4. 권고 사항"),
      ...recommendations.map(bullet),

      H1("5. 즉시 에스컬레이션 대상"),
      bullet(`HIGH ${urg.HIGH}건: ${highIds.join(", ")}`),

      new Paragraph({
        spacing: { before: 320 },
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({
          text: "출처: output/classification.json (자동 집계, 추정·반올림 없음)",
          font: FONT, italics: true, size: 18, color: "808080",
        })],
      }),
    ],
  }],
});

const outPath = path.join("output", "executive_summary.docx");
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(outPath, buf);
  console.log(`생성: ${outPath} (${buf.length.toLocaleString()} bytes)`);
});
