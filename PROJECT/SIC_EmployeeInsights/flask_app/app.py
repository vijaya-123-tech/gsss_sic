
import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import pandas as pd
from utils import clean_employee_df, compute_insights

app = Flask(__name__)
app.secret_key = "secret-key-change-me"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
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
        cleaned_path = os.path.join(OUTPUT_DIR, "cleaned_employees.csv")
        cleaned.to_csv(cleaned_path, index=False)

        filenames = []
        for key, dfo in insights.items():
            path = os.path.join(OUTPUT_DIR, f"{key}.csv")
            dfo.to_csv(path, index=False)
            filenames.append(f"{key}.csv")

        # Prepare data for Chart.js (dept_avg_salary)
        dept_avg = insights["dept_avg_salary"]
        labels = dept_avg["Department"].tolist()
        values = [float(x) for x in dept_avg["Salary"].tolist()]

        # Render results page
        tables_html = {
            "dept_avg_salary": insights["dept_avg_salary"].to_html(classes="table table-striped table-sm", index=False),
            "highest_paid": insights["highest_paid"].to_html(classes="table table-striped table-sm", index=False),
            "dept_total_salary": insights["dept_total_salary"].to_html(classes="table table-striped table-sm", index=False),
            "job_avg_salary": insights["job_avg_salary"].to_html(classes="table table-striped table-sm", index=False),
            "dept_employee_count": insights["dept_employee_count"].to_html(classes="table table-striped table-sm", index=False),
        }

        return render_template(
            "results.html",
            tables=tables_html,
            outputs=["cleaned_employees.csv"] + filenames,
            chart_labels=labels,
            chart_values=values
        )

    return render_template("index.html")

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
