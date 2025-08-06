# school_analysis.py
import pandas as pd


def get_grade(score):
    if score >= 75:
        return 'A1'
    elif score >= 70:
        return 'B2'
    elif score >= 65:
        return 'B3'
    elif score >= 60:
        return 'C4'
    elif score >= 55:
        return 'C5'
    elif score >= 50:
        return 'C6'
    elif score >= 45:
        return 'D7'
    elif score >= 40:
        return 'E8'
    else:
        return 'F9'


def categorize_grade(grade):
    if grade in ["A1", "B2", "B3"]:
        return "Distinction"
    elif grade in ["C4", "C5", "C6"]:
        return "Pass"
    else:
        return "Fail"


def load_class_data(file):
    xl = pd.ExcelFile(file)
    data = {}

    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        subject_cols = [col for col in df.columns if col not in ['NAMES', 'GENDER']]

        df['Total'] = df[subject_cols].sum(axis=1)
        df['Average'] = df['Total'] / len(subject_cols)
        df['Rank'] = df['Total'].rank(ascending=False, method='min').astype(int)

        data[sheet] = df

    return data


def subject_performance_analysis_df(df):
    subject_cols = [col for col in df.columns if col not in [
        'NAMES', 'GENDER', 'Total', 'Average', 'Rank', 'Performance']]

    # Melt into long-form
    melted_df = df.melt(id_vars=['NAMES'], value_vars=subject_cols,
                        var_name='Subject', value_name='Score')

    # Assign grade and category
    melted_df['Grade'] = melted_df['Score'].apply(get_grade)
    melted_df['Category'] = melted_df['Grade'].apply(categorize_grade)

    # Count per Subject-Category
    summary = (
        melted_df.groupby(['Subject', 'Category'])
        .size()
        .reset_index(name='Count')
    )

    return summary


def overall_school_performance_summary(data_dict):
    summary = []
    for class_name, df in data_dict.items():
        for _, row in df.iterrows():
            average_score = row['Average']
            if average_score >= 75:
                category = "Distinction"
            elif average_score >= 40:
                category = "Pass"
            else:
                category = "Fail"

            summary.append({
                "Class": class_name,
                "Name": row['NAMES'],
                "Gender": row['GENDER'],
                "Average": average_score,
                "Performance Category": category
            })

    return pd.DataFrame(summary)
