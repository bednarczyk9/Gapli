import pandas as pd
import glob
import os

def check_latest_report():
    reports = glob.glob("ai_report_*.xlsx")
    if not reports:
        print("No reports found.")
        return
    latest_report = max(reports, key=os.path.getmtime)
    print(f"Checking report: {latest_report}")
    df = pd.read_excel(latest_report)
    print(df.to_string())

if __name__ == "__main__":
    check_latest_report()
