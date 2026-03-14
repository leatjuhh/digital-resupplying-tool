from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUTPUT_PATH = Path("docs/generated/drt-app-summary-one-page.pdf")


def build_story():
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleCompact",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=20,
        textColor=colors.HexColor("#123B5D"),
        spaceAfter=6,
    )
    subtitle = ParagraphStyle(
        "SubtitleCompact",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=10,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=8,
    )
    heading = ParagraphStyle(
        "HeadingCompact",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=12,
        textColor=colors.HexColor("#123B5D"),
        spaceBefore=1,
        spaceAfter=4,
    )
    body = ParagraphStyle(
        "BodyCompact",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.4,
        leading=10.2,
        spaceAfter=2,
    )
    bullet = ParagraphStyle(
        "BulletCompact",
        parent=body,
        leftIndent=0,
        firstLineIndent=0,
        bulletIndent=0,
        spaceAfter=1,
    )

    left_flow = [
        Paragraph("Digital Resupplying Tool", title),
        Paragraph(
            "Repo-based one-page summary generated from README, app routes, API routers, models, and quick-start docs.",
            subtitle,
        ),
        Paragraph("What It Is", heading),
        Paragraph(
            "A full-stack retail operations app for managing stock redistribution between store locations. "
            "It combines PDF inventory ingest, proposal generation, review workflows, and role-based admin/auth features.",
            body,
        ),
        Paragraph("Who It's For", heading),
        Paragraph(
            "Primary persona: head-office inventory or merchandising staff who upload stock reports and review redistribution proposals. "
            "The repo also includes admin and store-user flows.",
            body,
        ),
        Paragraph("What It Does", heading),
        ListFlowable(
            [
                ListItem(Paragraph("Uploads one or more inventory PDFs into named processing batches.", bullet)),
                ListItem(Paragraph("Parses PDF records into store, size, stock, and sales data.", bullet)),
                ListItem(Paragraph("Generates redistribution proposals automatically after successful PDF ingest.", bullet)),
                ListItem(Paragraph("Shows proposal batches, proposal detail views, and editable proposal screens.", bullet)),
                ListItem(Paragraph("Supports approve, reject, and move-edit proposal actions through the API.", bullet)),
                ListItem(Paragraph("Provides JWT login plus user, role, and permission management endpoints.", bullet)),
                ListItem(Paragraph("Stores configurable app, rules, and API settings in the backend database.", bullet)),
            ],
            bulletType="bullet",
            leftIndent=9,
            bulletFontName="Helvetica",
            bulletFontSize=7,
            bulletOffsetY=1,
        ),
    ]

    right_flow = [
        Paragraph("How It Works", heading),
        ListFlowable(
            [
                ListItem(
                    Paragraph(
                        "<b>Frontend:</b> Next.js 14 app with routes for dashboard, uploads, proposals, assignments, settings, and login.",
                        bullet,
                    )
                ),
                ListItem(
                    Paragraph(
                        "<b>Client/API layer:</b> <font name='Courier'>frontend/lib/api.ts</font> calls FastAPI endpoints at <font name='Courier'>http://localhost:8000</font>.",
                        bullet,
                    )
                ),
                ListItem(
                    Paragraph(
                        "<b>Backend:</b> FastAPI mounts routers for articles, PDF ingest, redistribution, auth, users, roles, settings, and legacy batches.",
                        bullet,
                    )
                ),
                ListItem(
                    Paragraph(
                        "<b>Data:</b> SQLAlchemy writes to SQLite <font name='Courier'>backend/database.db</font>; models include users, roles, settings, PDF batches, voorraad records, parse logs, and proposals.",
                        bullet,
                    )
                ),
                ListItem(
                    Paragraph(
                        "<b>Flow:</b> PDF upload -> save under <font name='Courier'>backend/uploads/pdf_batches</font> -> parse to records -> persist voorraad/logs -> run redistribution algorithm -> save proposal moves -> review in frontend.",
                        bullet,
                    )
                ),
            ],
            bulletType="bullet",
            leftIndent=9,
            bulletFontName="Helvetica",
            bulletFontSize=7,
            bulletOffsetY=1,
        ),
        Spacer(1, 4),
        Paragraph("How To Run", heading),
        ListFlowable(
            [
                ListItem(Paragraph("From the repo root, run <font name='Courier'>npm run setup</font> for backend/frontend dependencies and DB init.", bullet)),
                ListItem(Paragraph("Start both servers with <font name='Courier'>.\\dev.ps1</font> (recommended) or <font name='Courier'>npm run dev</font>.", bullet)),
                ListItem(Paragraph("Open <font name='Courier'>http://localhost:3000</font> for the UI and <font name='Courier'>http://localhost:8000/docs</font> for API docs.", bullet)),
            ],
            bulletType="bullet",
            leftIndent=9,
            bulletFontName="Helvetica",
            bulletFontSize=7,
            bulletOffsetY=1,
        ),
        Spacer(1, 6),
        Paragraph("Usage Context", heading),
        Paragraph("Intended for internal local use.", body),
    ]

    table = Table(
        [[left_flow, right_flow]],
        colWidths=[94 * mm, 88 * mm],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return [table]


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        leftMargin=10 * mm,
        rightMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )
    doc.build(build_story())
    print(OUTPUT_PATH.resolve())


if __name__ == "__main__":
    main()
