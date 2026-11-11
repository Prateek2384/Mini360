from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models import Assessment, DevelopmentGoal


def _num(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{round(value, 1) + 0.0:.1f}"


def _gap(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{round(value, 1) + 0.0:+.1f}"


def _date(value) -> str:
    return value.strftime("%d/%m/%Y") if value else "-"


def _table(rows: list[list[str]]) -> Table:
    table = Table(rows, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def render_report_pdf(
    assessment: Assessment,
    leader_name: str,
    results: dict,
    goals: list[DevelopmentGoal],
) -> bytes:
    styles = getSampleStyleSheet()
    body = styles["BodyText"]
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm, title="Mini 360 Report",
    )

    story = [
        Paragraph("Mini 360 Leadership Report", styles["Title"]),
        Paragraph(f"<b>Assessment:</b> {escape(assessment.title)}", body),
        Paragraph(f"<b>Leader:</b> {escape(leader_name)}", body),
        Paragraph(f"<b>Closed on:</b> {_date(assessment.closed_at)}", body),
        Paragraph(f"<b>Rater responses:</b> {results['rater_response_count']}", body),
        Spacer(1, 6 * mm),
        Paragraph("Overall", styles["Heading2"]),
    ]

    o = results["overall"]
    story.append(_table([
        ["", "Self", "Others", "Gap (self - others)"],
        ["Overall", _num(o["self_score"]), _num(o["others_mean"]), _gap(o["gap"])],
    ]))

    story += [Spacer(1, 6 * mm), Paragraph("By category", styles["Heading2"])]
    rows = [["Category", "Self", "Others", "Gap"]]
    for c in results["categories"]:
        rows.append([c["category"].capitalize(), _num(c["self_score"]),
                     _num(c["others_mean"]), _gap(c["gap"])])
    story.append(_table(rows))

    weakest = sorted(results["categories"], key=lambda c: c["others_mean"])[:2]
    names = " and ".join(c["category"].capitalize() for c in weakest)
    story += [
        Spacer(1, 6 * mm),
        Paragraph("Areas to improve", styles["Heading2"]),
        Paragraph(f"Focus on improving <b>{names}</b>.", body),
        Paragraph("<i>Based on the two lowest-rated categories in others' feedback. "
                  "This is a simple suggestion, not a validated assessment.</i>", body),
    ]

    story += [Spacer(1, 6 * mm), Paragraph("Development commitments", styles["Heading2"])]
    if goals:
        rows = [["Commitment", "Due date", "Status"]]
        for g in goals:
            text = escape(g.title)
            if g.description:
                text += f"<br/>{escape(g.description)}"
            rows.append([Paragraph(text, body), _date(g.due_date),
                         g.status.replace("_", " ")])
        story.append(_table(rows))
    else:
        story.append(Paragraph("No commitments recorded yet.", body))

    doc.build(story)
    return buffer.getvalue()
