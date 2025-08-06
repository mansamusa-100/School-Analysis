# report_generator.py
from fpdf import FPDF
import os

REMARKS = {
    "A1": "Excellent",
    "B2": "Very Good",
    "B3": "Good",
    "C4": "Credit",
    "C5": "Credit",
    "C6": "Credit",
    "D7": "Pass",
    "E8": "Weak Pass",
    "F9": "Fail"
}


def generate_report_card(student_name, class_name, school_name, term_of_year, report_df, average, rank, gender):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title and Student Info
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, school_name, ln=True, align='C')
    pdf.cell(0, 10, term_of_year, ln=True, align='C')

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Report Card for {student_name}", ln=True)
    pdf.cell(0, 10, f"Class: {class_name}", ln=True)
    pdf.cell(0, 10, f"Gender: {gender}", ln=True)
    pdf.cell(0, 10, f"Average Score: {average:.2f}", ln=True)
    pdf.cell(0, 10, f"Position in Class: {rank}", ln=True)

    pdf.ln(5)

    # Table header
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Subject", 1)
    pdf.cell(30, 10, "Score", 1)
    pdf.cell(30, 10, "Grade", 1)
    pdf.cell(70, 10, "Remark", 1)
    pdf.ln()

    # Table rows
    pdf.set_font("Arial", '', 12)
    for index, row in report_df.iterrows():
        subject = row["Subject"]
        score = row["Score"]
        grade = row["Grade"]
        remark = REMARKS.get(grade, "")

        pdf.cell(50, 10, subject, 1)
        pdf.cell(30, 10, str(score), 1)
        pdf.cell(30, 10, grade, 1)
        pdf.cell(70, 10, remark, 1)
        pdf.ln()

    # Comments & Attendance Section
    pdf.ln(10)
    pdf.cell(0, 10, "Days Present: _____     Days Absent: _____     Days Late: _____", ln=True)

    pdf.ln(10)
    pdf.cell(0, 10, "Class Teacher's Comment: ________________________________________________________", ln=True)
    pdf.cell(0, 10, "_____________________________________________________________________________", ln=True)
    pdf.cell(0, 10, "Principal's Comment: ________________________________________________________", ln=True)
    pdf.cell(0, 10, "_________________________________________________________________________________", ln=True)

    pdf.ln(15)
    pdf.cell(0, 10, "Principal's Signature: _______________________", ln=True)
    pdf.cell(0, 10, "Next Term Begins: ____________________________", ln=True)

    # Save PDF
    os.makedirs("reports", exist_ok=True)
    filepath = f"reports/{student_name.replace(' ', '_')}_{class_name}.pdf"
    pdf.output(filepath)
    return filepath
