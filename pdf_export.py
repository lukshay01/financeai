from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
import re
from datetime import datetime

ACCENT_GREEN = HexColor("#4ade80")
ACCENT_BLUE = HexColor("#60a5fa")
LIGHT_GREY = HexColor("#94a3b8")
WHITE = HexColor("#ffffff")
YELLOW = HexColor("#fbbf24")
RED = HexColor("#f87171")

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', str(text))
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
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
            return Paragraph("(content unavailable)", style)
        except Exception:
            return None

def generate_pdf(user_profile, messages):
    buffer = io.BytesIO()

    try:
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
            parent=styles["Normal"],
            fontSize=9,
            fontName="Helvetica",
            textColor=LIGHT_GREY,
            spaceAfter=1,
        )
        value_style = ParagraphStyle(
            "FAValue",
            parent=styles["Normal"],
            fontSize=11,
            fontName="Helvetica-Bold",
            textColor=WHITE,
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
            parent=styles["Normal"],
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=ACCENT_BLUE,
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
        )

        story = []

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
        profile_items = [
            ("Name", user_profile.get("Name")),
            ("Age", user_profile.get("Age")),
            ("Monthly Income", user_profile.get("Monthly Income")),
            ("Monthly Expenses", user_profile.get("Monthly Expenses")),
            ("Financial Goals", user_profile.get("Financial Goals")),
            ("Risk Tolerance", user_profile.get("Risk Tolerance")),
        ]

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
        income_str = user_profile.get("Monthly Income")
        expenses_str = user_profile.get("Monthly Expenses")

        if income_str and expenses_str:
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