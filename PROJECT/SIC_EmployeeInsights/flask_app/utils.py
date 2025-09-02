
import pandas as pd

def clean_employee_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Standardize column names if needed
    expected = ["EmpID","Name","Department","JobTitle","Salary","JoiningDate"]
    missing_cols = [c for c in expected if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Remove duplicates
    df = df.drop_duplicates()

    # Handle missing values
    if df["Salary"].dtype == object:
        # try to coerce salary to numeric if it's string
        df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")
    df["Salary"] = df["Salary"].fillna(df["Salary"].mean())

    df["JobTitle"] = df["JobTitle"].fillna("Unknown")

    # Standardize text fields
    df["Department"] = df["Department"].astype(str).str.strip().str.title()
    df["JobTitle"] = df["JobTitle"].astype(str).str.strip().str.title()

    # Normalize common abbreviations
    df["JobTitle"] = df["JobTitle"].replace({
        "Software Engg": "Software Engineer",
        "Hr Manager": "HR Manager"
    })

    # Parse dates and add YearsOfService
    df["JoiningDate"] = pd.to_datetime(df["JoiningDate"], errors="coerce")
    current_year = pd.Timestamp.now().year
    df["YearsOfService"] = current_year - df["JoiningDate"].dt.year

    return df

def compute_insights(df: pd.DataFrame) -> dict:
    # 4.1 Average salary per department
    dept_avg_salary = df.groupby("Department")["Salary"].mean().reset_index()

    # 4.2 Highest paid employee in each department
    idx = df.groupby("Department")["Salary"].idxmax()
    highest_paid = df.loc[idx, ["EmpID","Name","Department","JobTitle","Salary"]].reset_index(drop=True)

    # 4.3 Total salary expenditure per department
    dept_total_salary = df.groupby("Department")["Salary"].sum().reset_index()

    # 4.4 Average salary per job title
    job_avg_salary = df.groupby("JobTitle")["Salary"].mean().reset_index()

    # 4.5 Employee count per department
    dept_employee_count = df["Department"].value_counts().reset_index()
    dept_employee_count.columns = ["Department","EmployeeCount"]

    return {
        "dept_avg_salary": dept_avg_salary,
        "highest_paid": highest_paid,
        "dept_total_salary": dept_total_salary,
        "job_avg_salary": job_avg_salary,
        "dept_employee_count": dept_employee_count,
    }
