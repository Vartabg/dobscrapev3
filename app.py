
from flask import Flask, render_template, request, send_file
import os
import scraper_async
import excel_generator
import asyncio

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_scraper():
    selected_range = request.form.get("date_range")
    start_date = {
        "Last 30 Days": "2024-03-13",
        "Last 3 Months": "2024-01-12",
        "Last 6 Months": "2023-10-12",
        "Past Year": "2023-04-12",
        "Past 2 Years": "2022-04-12",
        "All Since 2020": "2020-01-01"
    }.get(selected_range, "2020-01-01")

    # Call scraper and generator
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    violations = loop.run_until_complete(scraper_async.fetch_all_violations(start_date=start_date))
    excel_generator.generate_excel(violations)

    return send_file("violations.xlsx", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
