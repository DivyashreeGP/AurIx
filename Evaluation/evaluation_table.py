import pandas as pd

# ---------- LOAD DATA ----------
df = pd.read_csv("AURIX_completed_filled.csv")

# ---------- CLEAN / NORMALIZE ----------
# Ensure boolean column is numeric (True=1, False=0)
df["Is Fully Secure"] = df["Is Fully Secure"].astype(int)

# ---------- GROUP BY MODEL ----------
summary = df.groupby("Model Name").agg(
    Total_Samples=("Prompt ID", "count"),
    Avg_Vulnerabilities=("Total Vulnerabilities", "mean"),
    Avg_Severity_Score=("Severity Score", "mean"),
    Avg_Vulnerability_Density=("Vulnerability Density", "mean"),
    Secure_Count=("Is Fully Secure", "sum")
).reset_index()

# ---------- DERIVED METRICS ----------
summary["Secure_%"] = (summary["Secure_Count"] / summary["Total_Samples"]) * 100

# ---------- ROUND VALUES ----------
summary["Avg_Vulnerabilities"] = summary["Avg_Vulnerabilities"].round(2)
summary["Avg_Severity_Score"] = summary["Avg_Severity_Score"].round(2)
summary["Avg_Vulnerability_Density"] = summary["Avg_Vulnerability_Density"].round(3)
summary["Secure_%"] = summary["Secure_%"].round(2)

# ---------- RANKING (LOWER = BETTER) ----------
summary["Rank"] = summary["Avg_Severity_Score"].rank(method="dense", ascending=True).astype(int)

# Sort by rank
summary = summary.sort_values("Avg_Severity_Score", ascending=True)

# ---------- SAVE TO EXCEL ----------
output_file = "Model_Evaluation_Final.xlsx"

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    summary.to_excel(writer, sheet_name="Model_Comparison", index=False)
    df.to_excel(writer, sheet_name="Raw_Data", index=False)

print(f"✅ Final evaluation saved → {output_file}")