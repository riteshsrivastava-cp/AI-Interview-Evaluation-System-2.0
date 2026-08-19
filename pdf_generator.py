from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import os

def generate_pdf(candidate_name, topic, overall_report, all_results):
    doc = SimpleDocTemplate("Interview_Report.pdf")
    styles = getSampleStyleSheet()
    story = []

    title = styles["Title"]
    title.alignment = TA_CENTER

    story.append(Paragraph("AI Interview Evaluation Report", title))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"<b>Candidate Name: </b> {candidate_name}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Topic:</b> {topic}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Date :</b> {datetime.now().strftime('%d-%m-%y')}", styles["BodyText"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Overall Evaluation", styles["Heading1"]))
    story.append(Paragraph(f"<b>Overall AI Score:</b> {overall_report['overall_ai_score']}/10", styles["BodyText"]))
    story.append(Paragraph(f"<b>Overall NLP Score:</b> {overall_report['overall_nlp_score']}%", styles["BodyText"]))
    story.append(Paragraph(f"<b>Overall Status: </b>{overall_report['overall_status']}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Hiring Recommendation: </b> {overall_report['hiring_recommendation']}", styles['BodyText']))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Strengths", styles["Heading2"]))
    for strength in overall_report['overall_strengths']:
        story.append(Paragraph(f"• {strength}", styles['BodyText']))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Weaknesses", styles["Heading2"]))
    for weakness in overall_report["overall_weaknesses"]:
        story.append(Paragraph(f"• {weakness}", styles["BodyText"])) # FIXED: BodyTtext -> BodyText
    story.append(Spacer(1, 20))

    story.append(Paragraph("Overall Summary", styles["Heading2"]))
    story.append(Paragraph(overall_report["overall_summary"], styles["BodyText"]))
    story.append(Spacer(1, 15))

    story.append(Paragraph("Learning Roadmap", styles["Heading2"]))
    for topic in overall_report["learning_roadmap"]:
        story.append(Paragraph(f"• {topic}", styles["BodyText"])) # FIXED: BodyTetx -> BodyText
    story.append(Spacer(1, 20))

    story.append(Paragraph("Question-wise Performance", styles["Heading1"]))
    story.append(Spacer(1, 20))

    table_data = [
        ["Question ID", "Difficulty", "AI Score", "NLP Score", "Status"]
    ]

    for item in all_results:
        table_data.append([
            item["question_id"],
            item["difficulty"],
            item["evaluation"]["ai_score"],
            f'{item["evaluation"]["nlp_score"]:.2f}%',
            item["evaluation"]["status"]
        ])

    table = Table(table_data)
    table.setStyle(
        TableStyle([
             ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
             ("TEXTCOLOR", (0,0), (-1,0), colors.white),
             ("GRID", (0,0), (-1,-1), 1, colors.black),
             ("BACKGROUND", (0,1), (-1,-1), colors.beige),
             ("ALIGN", (0,0), (-1,-1), "CENTER"),
             ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
             ("BOTTOMPADDING", (0,0), (-1,0), 12)
        ])
    )
    story.append(table)
    story.append(Spacer(1, 30))

    # --- NEW CODE: ADDING CHARTS TO PDF ---
    story.append(Paragraph("Visual Analytics", styles["Heading1"]))
    story.append(Spacer(1, 10))

    # List of the charts we want to include, and where they are saved
    chart_files = [
        ("AI Score Distribution", "charts/ai_score.png"),
        ("Performance Trend", "charts/trend.png"),
        ("Status Distribution", "charts/status.png")
    ]

    for chart_title, file_path in chart_files:
        # Check if the image file actually exists on the computer first
        if os.path.exists(file_path):
            story.append(Paragraph(chart_title, styles["Heading2"]))
            story.append(Spacer(1, 10))
            
            # Add the image. We scale it nicely using the 'inch' measurement
            story.append(Image(file_path, width=6*inch, height=3.5*inch))
            story.append(Spacer(1, 20))

    doc.build(story)
    return "Interview_Report.pdf"