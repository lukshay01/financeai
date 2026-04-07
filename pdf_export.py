from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
<<<<<<< HEAD
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import io
from datetime import datetime

# Colour palette
DARK_BG = HexColor("#0f1117")
ACCENT_GREEN = HexColor("#4ade80")
ACCENT_BLUE = HexColor("#60a5fa")
LIGHT_GREY = HexColor("#94a3b8")
WHITE = HexColor("#ffffff")
CARD_BG = HexColor("#1e2130")
RED = HexColor("#f87171")
YELLOW = HexColor("#fbbf24")

def clean_markdown(text):
    import re
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    return text.strip()

def generate_pdf(user_profile, messages):
    buffer = io.BytesIO()
=======
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
import re
from datetime import datetime

ACCENT_GREEN = HexColor(”#4ade80”)
ACCENT_BLUE = HexColor(”#60a5fa”)
LIGHT_GREY = HexColor(”#94a3b8”)
WHITE = HexColor(”#ffffff”)
YELLOW = HexColor(”#fbbf24”)
RED = HexColor(”#f87171”)

def clean_text(text):
if not text:
return “”
text = re.sub(r’**(.*?)**’, r’\1’, str(text))
text = re.sub(r’*(.*?)*’, r’\1’, text)
text = re.sub(r’#{1,6}\s*’, ‘’, text)
text = re.sub(r’`(.*?)`’, r’\1’, text)
text = re.sub(r’[^\x20-\x7E\n]’, ‘’, text)
return text.strip()

def safe_paragraph(text, style):
try:
clean = clean_text(text)
if not clean:
return None
clean = clean[:2000]
return Paragraph(clean, style)
except Exception:
try:
return Paragraph(”(content unavailable)”, style)
except Exception:
return None

def generate_pdf(user_profile, messages):
buffer = io.BytesIO()

```
try:
>>>>>>> 6329ea03904e19c2904fc78063e1d57f1ddc2986
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
<<<<<<< HEAD
        "Title",
        parent=styles["Normal"],
        fontSize=28,
        fontName="Helvetica-Bold",
        textColor=WHITE,
        alignment=TA_LEFT,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=12,
        fontName="Helvetica",
        textColor=LIGHT_GREY,
        alignment=TA_LEFT,
        spaceAfter=2,
    )
    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontSize=14,
        fontName="Helvetica-Bold",
        textColor=ACCENT_GREEN,
        spaceBefore=16,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=WHITE,
        spaceAfter=6,
        leading=16,
    )
    label_style = ParagraphStyle(
        "Label",
=======
        "FATitle",
        parent=styles["Normal"],
        fontSize=24,
        fontName="Helvetica-Bold",
        textColor=WHITE,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "FASubtitle",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica",
        textColor=LIGHT_GREY,
        spaceAfter=4,
    )
    section_style = ParagraphStyle(
        "FASection",
        parent=styles["Normal"],
        fontSize=13,
        fontName="Helvetica-Bold",
        textColor=ACCENT_GREEN,
        spaceBefore=14,
        spaceAfter=6,
    )
    label_style = ParagraphStyle(
        "FALabel",
>>>>>>> 6329ea03904e19c2904fc78063e1d57f1ddc2986
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica",
        textColor=LIGHT_GREY,
<<<<<<< HEAD
        spaceAfter=2,
    )
    value_style = ParagraphStyle(
        "Value",
=======
        spaceAfter=1,
    )
    value_style = ParagraphStyle(
        "FAValue",
>>>>>>> 6329ea03904e19c2904fc78063e1d57f1ddc2986
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica-Bold",
        textColor=WHITE,
<<<<<<< HEAD
        spaceAfter=4,
    )
    chat_user_style = ParagraphStyle(
        "ChatUser",
=======
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "FABody",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=WHITE,
        spaceAfter=4,
        leading=15,
    )
    user_label_style = ParagraphStyle(
        "FAUserLabel",
>>>>>>> 6329ea03904e19c2904fc78063e1d57f1ddc2986
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=ACCENT_BLUE,
<<<<<<< HEAD
        spaceAfter=2,
        spaceBefore=8,
    )
    chat_ai_style = ParagraphStyle(
        "ChatAI",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica",
        textColor=WHITE,
        spaceAfter=4,
        leading=14,
=======
        spaceBefore=10,
        spaceAfter=2,
    )
    ai_label_style = ParagraphStyle(
        "FAAILabel",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=ACCENT_GREEN,
        spaceBefore=6,
        spaceAfter=2,
    )
    footer_style = ParagraphStyle(
        "FAFooter",
        parent=styles["Normal"],
        fontSize=8,
        fontName="Helvetica",
        textColor=LIGHT_GREY,
        alignment=TA_CENTER,
>>>>>>> 6329ea03904e19c2904fc78063e1d57f1ddc2986
    )

    story = []

<<<<<<< HEAD
    # ---- HEADER ----
    story.append(Paragraph("💰 FinanceAI", title_style))
    story.append(Paragraph("Personal Financial Plan", subtitle_style))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%d %B %Y at %I:%M %p')}",
        subtitle_style
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_GREEN))
    story.append(Spacer(1, 0.4*cm))

    # ---- PROFILE SECTION ----
    story.append(Paragraph("Your Profile", section_header_style))

    profile_data = []
=======
    # HEADER
    p = safe_paragraph("FinanceAI - Personal Financial Plan", title_style)
    if p:
        story.append(p)

    p = safe_paragraph(f"Generated on {datetime.now().strftime('%d %B %Y at %I:%M %p')}", subtitle_style)
    if p:
        story.append(p)

    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_GREEN))
    story.append(Spacer(1, 0.3*cm))

    # PROFILE
>>>>>>> 6329ea03904e19c2904fc78063e1d57f1ddc2986
    profile_items = [
        ("Name", user_profile.get("Name")),
        ("Age", user_profile.get("Age")),
        ("Monthly Income", user_profile.get("Monthly Income")),
        ("Monthly Expenses", user_profile.get("Monthly Expenses")),
        ("Financial Goals", user_profile.get("Financial Goals")),
        ("Risk Tolerance", user_profile.get("Risk Tolerance")),
    ]

<<<<<<< HEAD
    row = []
    for label, value in profile_items:
        if value:
            cell = [
                Paragraph(label, label_style),
                Paragraph(str(value), value_style)
            ]
            row.append(cell)
            if len(row) == 2:
                profile_data.append(row)
                row = []
    if row:
        row.append(["", ""])
        profile_data.append(row)

    if profile_data:
        flat_data = []
        for pair in profile_data:
            flat_row = []
            for cell in pair:
                if isinstance(cell, list):
                    flat_row.append(cell)
                else:
                    flat_row.append([""])
            flat_data.append(flat_row)

        profile_table = Table(
            [[pair[0], pair[1]] for pair in profile_data],
            colWidths=[8.5*cm, 8.5*cm]
        )
        profile_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), CARD_BG),
            ("ROWBACKGROUND", (0, 0), (-1, -1), CARD_BG),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ("ROUNDEDCORNERS", [8, 8, 8, 8]),
            ("LINEABOVE", (0, 0), (-1, 0), 0.5, ACCENT_GREEN),
        ]))
        story.append(profile_table)

    # ---- FINANCIAL SUMMARY ----
=======
    has_profile = any(v for _, v in profile_items)
    if has_profile:
        p = safe_paragraph("Your Profile", section_style)
        if p:
            story.append(p)

        for label, value in profile_items:
            if value:
                p = safe_paragraph(label, label_style)
                if p:
                    story.append(p)
                p = safe_paragraph(str(value), value_style)
                if p:
                    story.append(p)

    # FINANCIAL SUMMARY
>>>>>>> 6329ea03904e19c2904fc78063e1d57f1ddc2986
    income_str = user_profile.get("Monthly Income")
    expenses_str = user_profile.get("Monthly Expenses")

    if income_str and expenses_str:
<<<<<<< HEAD
        import re
        def get_num(s):
            nums = re.findall(r'[\d,]+', s)
            if nums:
                return float(nums[0].replace(",", ""))
            return 0

        income = get_num(income_str)
        expenses = get_num(expenses_str)
        savings = income - expenses
        savings_rate = (savings / income * 100) if income > 0 else 0

        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("Financial Summary", section_header_style))

        if savings_rate >= 20:
            health_color = ACCENT_GREEN
            health_label = "Excellent"
        elif savings_rate >= 10:
            health_color = YELLOW
            health_label = "Good"
        else:
            health_color = RED
            health_label = "Needs Attention"

        summary_data = [
            [
                Paragraph("Monthly Savings", label_style),
                Paragraph("Savings Rate", label_style),
                Paragraph("Financial Health", label_style),
            ],
            [
                Paragraph(f"${int(savings):,}", value_style),
                Paragraph(f"{savings_rate:.1f}%", value_style),
                Paragraph(health_label, ParagraphStyle(
                    "Health", parent=value_style, textColor=health_color
                )),
            ]
        ]

        summary_table = Table(summary_data, colWidths=[5.6*cm, 5.6*cm, 5.6*cm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), CARD_BG),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ("LINEABOVE", (0, 0), (-1, 0), 0.5, ACCENT_BLUE),
        ]))
        story.append(summary_table)

    # ---- CONVERSATION ----
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Your Financial Plan", section_header_style))
    story.append(Paragraph(
        "Below is your full conversation with FinanceAI including your personalised financial plan.",
        body_style
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GREY))

    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        clean_content = clean_markdown(content)

        if role == "user":
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph("You:", chat_user_style))
            story.append(Paragraph(clean_content, chat_ai_style))
        elif role == "assistant":
            story.append(Paragraph("FinanceAI:", ParagraphStyle(
                "AILabel", parent=chat_user_style, textColor=ACCENT_GREEN
            )))
            lines = clean_content.split("\n")
            for line in lines:
                line = line.strip()
                if line:
                    story.append(Paragraph(line, chat_ai_style))

    # ---- FOOTER ----
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GREY))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Generated by FinanceAI — This is for educational purposes only and does not constitute professional financial advice.",
        ParagraphStyle("Footer", parent=label_style, alignment=TA_CENTER, fontSize=8)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
=======
        try:
            def get_num(s):
                nums = re.findall(r'[\d,]+', str(s))
                return float(nums[0].replace(",", "")) if nums else 0

            income = get_num(income_str)
            expenses = get_num(expenses_str)
            savings = income - expenses
            savings_rate = (savings / income * 100) if income > 0 else 0

            story.append(Spacer(1, 0.2*cm))
            p = safe_paragraph("Financial Summary", section_style)
            if p:
                story.append(p)

            p = safe_paragraph(f"Monthly Savings: ${int(savings):,}", value_style)
            if p:
                story.append(p)

            p = safe_paragraph(f"Savings Rate: {savings_rate:.1f}%", value_style)
            if p:
                story.append(p)

            if savings_rate >= 20:
                health = "Excellent"
            elif savings_rate >= 10:
                health = "Good"
            else:
                health = "Needs Attention"

            p = safe_paragraph(f"Financial Health: {health}", value_style)
            if p:
                story.append(p)
        except Exception:
            pass

    # CONVERSATION
    story.append(Spacer(1, 0.2*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GREY))

    p = safe_paragraph("Your Financial Plan", section_style)
    if p:
        story.append(p)

    p = safe_paragraph("Below is your full conversation with FinanceAI.", body_style)
    if p:
        story.append(p)

    story.append(Spacer(1, 0.2*cm))

    for msg in messages:
        try:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if not content:
                continue

            if role == "user":
                p = safe_paragraph("You:", user_label_style)
                if p:
                    story.append(p)
                lines = clean_text(content).split("\n")
                for line in lines:
                    line = line.strip()
                    if line:
                        p = safe_paragraph(line, body_style)
                        if p:
                            story.append(p)

            elif role == "assistant":
                p = safe_paragraph("FinanceAI:", ai_label_style)
                if p:
                    story.append(p)
                lines = clean_text(content).split("\n")
                for line in lines:
                    line = line.strip()
                    if line:
                        p = safe_paragraph(line, body_style)
                        if p:
                            story.append(p)
        except Exception:
            continue

    # FOOTER
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GREY))
    story.append(Spacer(1, 0.2*cm))
    p = safe_paragraph(
        "Generated by FinanceAI. For educational purposes only. Not professional financial advice.",
        footer_style
    )
    if p:
        story.append(p)

    doc.build(story)

except Exception as e:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    doc.build([Paragraph("FinanceAI Financial Plan - Error generating full PDF.", styles["Normal"])])

buffer.seek(0)
return buffer
``
>>>>>>> 6329ea03904e19c2904fc78063e1d57f1ddc2986
