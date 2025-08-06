# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

from school_analysis import load_class_data, subject_performance_analysis_df, overall_school_performance_summary
from report_generator import generate_report_card


def get_grade(score):
    if score >= 75:
        return "A1"
    elif score >= 70:
        return "B2"
    elif score >= 65:
        return "B3"
    elif score >= 60:
        return "C4"
    elif score >= 55:
        return "C5"
    elif score >= 50:
        return "C6"
    elif score >= 45:
        return "D7"
    elif score >= 40:
        return "E8"
    else:
        return "F9"


def get_remark(grade):
    remarks = {
        "A1": "Excellent", "B2": "Very Good", "B3": "Good",
        "C4": "Credit", "C5": "Credit", "C6": "Credit",
        "D7": "Pass", "E8": "Pass", "F9": "Fail"
    }
    return remarks.get(grade, "")


st.set_page_config(page_title="📘 School Results Dashboard", layout="wide")
st.title("📊 School Results Analysis Dashboard")

uploaded_file = st.file_uploader("📤 Upload Excel File with Class Sheets", type=["xlsx"])
school_name = st.text_input("🏫 Enter School Name", "My Sample School")
term_of_year = st.text_input("🏫 Enter The Term", "First Term 2024 - 2025")


if uploaded_file and school_name and term_of_year:
    data = load_class_data(uploaded_file)
    class_selected = st.selectbox("Select Class", list(data.keys()))
    df = data[class_selected]

    st.subheader(f"📄 Results for {class_selected}")
    st.dataframe(df, use_container_width=True)

    # Class Summary
    st.subheader("📊 Class Summary")
    st.markdown(f"**Average Total Score:** {df['Total'].mean():.2f}")
    st.markdown(f"**Highest Score:** {df['Total'].max()}")
    st.markdown(f"**Lowest Score:** {df['Total'].min()}")
    st.markdown(f"**Top Performer:** {df.loc[df['Total'].idxmax()]['NAMES']}")
    st.markdown(f"**Failed Students:** {(df['Average'] < 45).sum()}")
    st.markdown(f"**Distinctions (≥75):** {(df['Average'] >= 75).sum()}")

    # Gender Performance
    if "GENDER" in df.columns:
        df["GENDER"] = df["GENDER"].map({"M": "Male", "F": "Female"})
        df["Performance"] = df["Average"].apply(lambda x: "Distinction" if x >= 75 else "Pass" if x >= 45 else "Fail")
        gender_perf = df.groupby(["GENDER", "Performance"]).size().unstack(fill_value=0)
        st.subheader("👩🏫 Gender-Based Performance")
        st.dataframe(gender_perf)

    # Subject Analysis
    st.subheader("📊 Subject-Wise Performance Analysis")
    subject_df = subject_performance_analysis_df(df)

    # Subject filter
    subject_options = subject_df['Subject'].unique().tolist()
    selected_subject = st.selectbox("Select Subject to View", ["All"] + subject_options)

    if selected_subject != "All":
        filtered_df = subject_df[subject_df["Subject"] == selected_subject]
    else:
        filtered_df = subject_df

    # Chart
    fig = px.bar(
        filtered_df,
        x="Subject",
        y="Count",
        color="Category",
        barmode="group",
        title="Performance per Subject",
        labels={"Count": "Number of Students"},
        color_discrete_map={
            "Distinction": "#4CAF50",
            "Pass": "#2196F3",
            "Fail": "#F44336"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

    # Table
    st.markdown("### 📋 Detailed Table")
    st.dataframe(filtered_df)

    # Download
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Summary as CSV",
        data=csv,
        file_name=f"{selected_subject.lower()}_performance_summary.csv"
        if selected_subject != "All"
        else "subject_performance_summary.csv",
        mime='text/csv'
    )

    # NEW PART
    st.markdown("## 🏫 Overall School Performance Summary")

    # Get summary from function
    overall_df = overall_school_performance_summary(data)

    # KPIs
    total_students = len(overall_df)
    distinction_count = len(overall_df[overall_df["Performance Category"] == "Distinction"])
    pass_count = len(overall_df[overall_df["Performance Category"] == "Pass"])
    fail_count = len(overall_df[overall_df["Performance Category"] == "Fail"])

    st.metric("👨‍🎓 Total Students", total_students)
    st.metric("🎖️ Distinction", f"{distinction_count} ({distinction_count / total_students * 100:.1f}%)")
    st.metric("✅ Pass", f"{pass_count} ({pass_count / total_students * 100:.1f}%)")
    st.metric("❌ Fail", f"{fail_count} ({fail_count / total_students * 100:.1f}%)")

    # Bar chart
    perf_summary = overall_df["Performance Category"].value_counts().reset_index()
    perf_summary.columns = ["Category", "Count"]

    fig = px.bar(
        perf_summary,
        x="Category",
        y="Count",
        color="Category",
        title="Overall Performance Distribution",
        color_discrete_map={
            "Distinction": "#4CAF50",
            "Pass": "#2196F3",
            "Fail": "#F44336"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detailed table
    st.markdown("### 📝 Student Performance Table")
    st.dataframe(overall_df)

    # Download button
    csv = overall_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Overall Summary as CSV",
        data=csv,
        file_name="overall_school_performance_summary.csv",
        mime='text/csv'
    )

    # LAST PART

    # Top 5
    df['Rank'] = df['Total'].rank(ascending=False, method='min').astype(int)
    st.subheader("🏅 Top 5 Students")
    st.dataframe(df.sort_values("Rank")[["NAMES", "Average", "Rank"]].head(5))

    # Report Card
    st.subheader("🎓 Download Report Card")
    student_name = st.selectbox("Select Student", df["NAMES"])
    student_row = df[df["NAMES"] == student_name]
    if not student_row.empty:
        st.markdown(f"**Total Score:** {student_row['Total'].values[0]}")
        st.markdown(f"**Average Score:** {student_row['Average'].values[0]}")
        st.markdown(f"**Rank in Class:** {student_row['Rank'].values[0]}")
    gender = student_row["GENDER"].values[0] if "GENDER" in student_row.columns else ""

    non_subject_cols = ['NAMES', 'Total', 'Average', 'Rank', 'GENDER', 'Performance']
    subjects = [col for col in df.columns if col not in non_subject_cols]

    report_data = []
    for subject in subjects:
        raw_score = student_row[subject].values[0]
        try:
            score = float(raw_score)
        except (ValueError, TypeError):
            score = 0
        grade = get_grade(score)
        remark = get_remark(grade)
        report_data.append({
            'Subject': subject,
            'Score': score,
            'Grade': grade,
            'Remarks': remark
        })

    report_df = pd.DataFrame(report_data)
    st.table(report_df)

    if st.button("📥 Generate PDF Report Card"):
        filepath = generate_report_card(
            student_name,
            class_selected,
            school_name,
            term_of_year,
            report_df,
            student_row["Average"].values[0],
            student_row["Rank"].values[0],
            gender
        )
        with open(filepath, "rb") as f:
            st.download_button(
                label="Download Report",
                data=f,
                file_name=filepath.split("/")[-1],
                mime="application/pdf"
            )
