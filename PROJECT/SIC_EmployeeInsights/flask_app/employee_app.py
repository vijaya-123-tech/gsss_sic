import os
from flask import Flask, request, flash, redirect, url_for, send_from_directory, render_template_string
import pandas as pd

app = Flask(__name__)
app.secret_key = "secret-key-change-me"

# -------------------------
# Folders
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------
# Utility Functions
# -------------------------
def clean_employee_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    expected = ["EmpID","Name","Department","JobTitle","Salary","JoiningDate"]
    missing_cols = [c for c in expected if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    df = df.drop_duplicates()
    if df["Salary"].dtype == object:
        df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")
    df["Salary"] = df["Salary"].fillna(df["Salary"].mean())
    df["JobTitle"] = df["JobTitle"].fillna("Unknown")
    df["Department"] = df["Department"].astype(str).str.strip().str.title()
    df["JobTitle"] = df["JobTitle"].astype(str).str.strip().str.title()
    df["JobTitle"] = df["JobTitle"].replace({
        "Software Engg": "Software Engineer",
        "Hr Manager": "HR Manager"
    })
    df["JoiningDate"] = pd.to_datetime(df["JoiningDate"], errors="coerce")
    current_year = pd.Timestamp.now().year
    df["YearsOfService"] = current_year - df["JoiningDate"].dt.year
    return df

def compute_insights(df: pd.DataFrame) -> dict:
    dept_avg_salary = df.groupby("Department")["Salary"].mean().reset_index()
    idx = df.groupby("Department")["Salary"].idxmax()
    highest_paid = df.loc[idx, ["EmpID","Name","Department","JobTitle","Salary"]].reset_index(drop=True)
    dept_total_salary = df.groupby("Department")["Salary"].sum().reset_index()
    job_avg_salary = df.groupby("JobTitle")["Salary"].mean().reset_index()
    dept_employee_count = df["Department"].value_counts().reset_index()
    dept_employee_count.columns = ["Department","EmployeeCount"]
    return {
        "dept_avg_salary": dept_avg_salary,
        "highest_paid": highest_paid,
        "dept_total_salary": dept_total_salary,
        "job_avg_salary": job_avg_salary,
        "dept_employee_count": dept_employee_count,
    }

# -------------------------
# HTML Templates
# -------------------------
index_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Employee Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
  <div class="container-fluid">
    <a class="navbar-brand" href="#">Employee Dashboard</a>
  </div>
</nav>
<div class="container">
    <h3>Upload Employee CSV</h3>
    <form method="post" enctype="multipart/form-data" class="mb-3">
        <input type="file" name="file" class="form-control mb-2">
        <button type="submit" class="btn btn-success">Upload</button>
    </form>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="alert alert-warning">
        {% for msg in messages %}
          <div>{{ msg }}</div>
        {% endfor %}
        </div>
      {% endif %}
    {% endwith %}
</div>
</body>
</html>
"""

results_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Employee Insights</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
  <div class="container-fluid">
    <a class="navbar-brand" href="{{ url_for('index') }}">Employee Dashboard</a>
  </div>
</nav>
<div class="container">
    <h2 class="mb-4">Dashboard</h2>

    <!-- KPI Cards -->
    <div class="row mb-4">
        {% for kpi in kpis %}
        <div class="col-md-3 mb-2">
            <div class="card text-white {{ kpi.color }} mb-3">
                <div class="card-header">{{ kpi.title }}</div>
                <div class="card-body">
                    <h5 class="card-title">{{ kpi.value }}</h5>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>

    <!-- Collapsible Charts -->
    <div class="accordion mb-4" id="chartAccordion">
        {% for chart in charts %}
        <div class="accordion-item">
            <h2 class="accordion-header" id="heading{{ loop.index }}">
                <button class="accordion-button {% if not loop.first %}collapsed{% endif %}" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{{ loop.index }}" aria-expanded="{% if loop.first %}true{% else %}false{% endif %}" aria-controls="collapse{{ loop.index }}">
                    {{ chart.title }}
                </button>
            </h2>
            <div id="collapse{{ loop.index }}" class="accordion-collapse collapse {% if loop.first %}show{% endif %}" aria-labelledby="heading{{ loop.index }}" data-bs-parent="#chartAccordion">
                <div class="accordion-body">
                    <canvas id="{{ chart.id }}"></canvas>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>

    <!-- Tabs for Tables -->
    <h4 class="mt-4">Detailed Insights</h4>
    <ul class="nav nav-tabs" id="insightTabs" role="tablist">
        {% for name in tables.keys() %}
        {% set loop_index = loop.index0 %}
        <li class="nav-item" role="presentation">
            <button class="nav-link {% if loop.first %}active{% endif %}" id="tab-{{ loop_index }}" data-bs-toggle="tab" data-bs-target="#content-{{ loop_index }}" type="button" role="tab" aria-controls="content-{{ loop_index }}" aria-selected="{% if loop.first %}true{% else %}false{% endif %}">{{ name.replace('_',' ').title() }}</button>
        </li>
        {% endfor %}
    </ul>
    <div class="tab-content border border-top-0 p-3 mb-4" id="insightTabsContent">
        {% for name, table in tables.items() %}
        {% set loop_index = loop.index0 %}
        <div class="tab-pane fade {% if loop.first %}show active{% endif %}" id="content-{{ loop_index }}" role="tabpanel" aria-labelledby="tab-{{ loop_index }}">
            {{ table | safe }}
        </div>
        {% endfor %}
    </div>

    <!-- Download Buttons -->
    <h4>Download CSV Outputs</h4>
    {% for file in outputs %}
        <a href="{{ url_for('download_file', filename=file) }}" class="btn btn-success btn-sm mb-1">{{ file }}</a>
    {% endfor %}
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
$(document).ready(function() {
    $('table').DataTable();
});

// Generate charts dynamically
{% for chart in charts %}
var ctx{{ loop.index }} = document.getElementById('{{ chart.id }}').getContext('2d');
new Chart(ctx{{ loop.index }}, {
    type: '{{ chart.type }}',
    data: {
        labels: {{ chart.labels | safe }},
        datasets: [{
            label: '{{ chart.label }}',
            data: {{ chart.data | safe }},
            backgroundColor: {{ chart.colors | safe }}
        }]
    },
    options: { responsive: true }
});
{% endfor %}
</script>
</body>
</html>
"""

# -------------------------
# Routes
# -------------------------
@app.route("/", methods=["GET","POST"])
def index():
    if request.method=="POST":
        file = request.files.get("file")
        if not file or file.filename=="":
            flash("Please choose a CSV file to upload.")
            return redirect(url_for("index"))
        if not file.filename.lower().endswith(".csv"):
            flash("Only CSV files are allowed.")
            return redirect(url_for("index"))
        filepath = os.path.join(UPLOAD_DIR, file.filename)
        file.save(filepath)
        try:
            df = pd.read_csv(filepath)
            cleaned = clean_employee_df(df)
            insights = compute_insights(cleaned)
        except Exception as e:
            flash(f"Error processing file: {e}")
            return redirect(url_for("index"))

        # Save outputs
        cleaned.to_csv(os.path.join(OUTPUT_DIR,"cleaned_employees.csv"), index=False)
        filenames = []
        for k,v in insights.items():
            path = os.path.join(OUTPUT_DIR,f"{k}.csv")
            v.to_csv(path,index=False)
            filenames.append(f"{k}.csv")

        # Tables
        tables_html = {k: v.to_html(classes="table table-striped table-hover table-sm", index=False) for k,v in insights.items()}

        # KPIs
        kpis = [
            {"title":"Total Employees","value":len(cleaned),"color":"bg-primary"},
            {"title":"Total Salary","value":f"${cleaned['Salary'].sum():,.2f}","color":"bg-success"},
            {"title":"Highest Paid Employee","value":f"{cleaned.loc[cleaned['Salary'].idxmax(),'Name']} (${cleaned['Salary'].max():,.2f})","color":"bg-warning"},
            {"title":"Average Salary","value":f"${cleaned['Salary'].mean():,.2f}","color":"bg-info"},
            {"title":"Median Salary","value":f"${cleaned['Salary'].median():,.2f}","color":"bg-secondary"},
            {"title":"Number of Departments","value":cleaned['Department'].nunique(),"color":"bg-dark"},
            {"title":"Number of Job Titles","value":cleaned['JobTitle'].nunique(),"color":"bg-danger"},
            {"title":"Longest-Serving Employee","value":f"{cleaned.loc[cleaned['YearsOfService'].idxmax(),'Name']} ({cleaned['YearsOfService'].max()} yrs)","color":"bg-success"}
        ]

        # Charts
        charts = []
        charts.append({
            "id":"chartDeptAvg",
            "title":"Average Salary per Department",
            "type":"bar",
            "labels":insights['dept_avg_salary']['Department'].tolist(),
            "data":insights['dept_avg_salary']['Salary'].tolist(),
            "label":"Average Salary",
            "colors":["rgba(54, 162, 235, 0.6)"]*len(insights['dept_avg_salary'])
        })
        top5 = insights['highest_paid'].nlargest(5,'Salary')
        charts.append({
            "id":"chartHighestPaid",
            "title":"Top 5 Highest Paid Employees",
            "type":"bar",
            "labels":top5['Name'].tolist(),
            "data":top5['Salary'].tolist(),
            "label":"Salary",
            "colors":["rgba(255, 99, 132, 0.6)"]*len(top5)
        })
        charts.append({
            "id":"chartDeptTotal",
            "title":"Total Salary per Department",
            "type":"pie",
            "labels":insights['dept_total_salary']['Department'].tolist(),
            "data":insights['dept_total_salary']['Salary'].tolist(),
            "label":"Total Salary",
            "colors":["#FF6384","#36A2EB","#FFCE56","#4BC0C0","#9966FF"]*5
        })
        charts.append({
            "id":"chartJobAvg",
            "title":"Average Salary per Job Title",
            "type":"bar",
            "labels":insights['job_avg_salary']['JobTitle'].tolist(),
            "data":insights['job_avg_salary']['Salary'].tolist(),
            "label":"Average Salary",
            "colors":["rgba(75, 192, 192, 0.6)"]*len(insights['job_avg_salary'])
        })
        charts.append({
            "id":"chartDeptEmpCount",
            "title":"Employee Count per Department",
            "type":"doughnut",
            "labels":insights['dept_employee_count']['Department'].tolist(),
            "data":insights['dept_employee_count']['EmployeeCount'].tolist(),
            "label":"Employee Count",
            "colors":["#FF6384","#36A2EB","#FFCE56","#4BC0C0","#9966FF"]*5
        })

        return render_template_string(results_html,
            tables=tables_html,
            outputs=["cleaned_employees.csv"]+filenames,
            kpis=kpis,
            charts=charts
        )

    return render_template_string(index_html)

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

if __name__=="__main__":
    app.run(debug=True)
