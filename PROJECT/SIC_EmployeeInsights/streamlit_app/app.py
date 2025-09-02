
import io
import pandas as pd
import streamlit as st
from utils import clean_employee_df, compute_insights

st.set_page_config(page_title="Employee Salary Insights", page_icon="💼", layout="wide")

st.title("💼 Employee Salary Insights")
st.write("Upload your **employees.csv** to clean the data and generate HR summaries.")

uploaded = st.file_uploader("Upload CSV", type=["csv"])

if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        st.stop()

    with st.spinner("Cleaning data..."):
        try:
            cleaned = clean_employee_df(df)
        except Exception as e:
            st.error(f"Data cleaning error: {e}")
            st.stop()

    st.subheader("Preview (Cleaned)")
    st.dataframe(cleaned.head(20), use_container_width=True)

    st.subheader("Insights")
    insights = compute_insights(cleaned)

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Average Salary per Department**")
        st.dataframe(insights["dept_avg_salary"], use_container_width=True)
        st.bar_chart(insights["dept_avg_salary"].set_index("Department"))
    with col2:
        st.write("**Total Salary Expenditure per Department**")
        st.dataframe(insights["dept_total_salary"], use_container_width=True)
        st.bar_chart(insights["dept_total_salary"].set_index("Department"))

    st.write("**Highest Paid Employee in Each Department**")
    st.dataframe(insights["highest_paid"], use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.write("**Average Salary per Job Title**")
        st.dataframe(insights["job_avg_salary"], use_container_width=True)
    with c2:
        st.write("**Employee Count per Department**")
        st.dataframe(insights["dept_employee_count"], use_container_width=True)

    st.subheader("Download Outputs")
    for key, df_out in insights.items():
        csv_bytes = df_out.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"Download {key}.csv",
            data=csv_bytes,
            file_name=f"{key}.csv",
            mime="text/csv"
        )

    st.subheader("Download Cleaned Dataset")
    st.download_button(
        label="Download cleaned_employees.csv",
        data=cleaned.to_csv(index=False).encode("utf-8"),
        file_name="cleaned_employees.csv",
        mime="text/csv"
    )

st.caption("Tip: Use descriptive variable names and comments for clean, readable code.")
