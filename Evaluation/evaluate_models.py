import pandas as pd
import subprocess
import json
import uuid
from pathlib import Path

# ---------------- PATH SETUP ----------------
ROOT = Path(__file__).resolve().parent
TEMP_DIR = ROOT / "temp_files"
RESULTS_DIR = ROOT / "results"

TEMP_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# ---------------- LOAD CSV ----------------
df = pd.read_csv("AURIX_completed.csv")

# Anchor = 8th column (Lines of Code)
anchor_index = 7

# 🔥 IMPORTANT: Fix dtype issues
for col in df.columns[anchor_index+1:]:
    df[col] = df[col].astype(object)


# ---------------- RULE ENGINE ----------------
def run_rule_engine(code: str):
    uid = str(uuid.uuid4())

    temp_file = TEMP_DIR / f"temp_{uid}.py"
    out_file = RESULTS_DIR / f"temp_{uid}.json"

    temp_file.write_text(code, encoding="utf-8")

    subprocess.run([
        "python",
        str(ROOT.parent / "detect.py"),
        str(temp_file),
        "--only-issues",
        "--compact",
        "-o",
        str(out_file)
    ], cwd=ROOT.parent)

    if not out_file.exists():
        return []

    data = json.loads(out_file.read_text(encoding="utf-8"))

    issues = []
    for file in data:
        for item in data[file]:
            issues.append({
                "type": item.get("rules", ["Unknown"])[0],
                "line": item.get("line", 1),
                "description": item.get("code", "")
            })

    # cleanup
    temp_file.unlink(missing_ok=True)
    out_file.unlink(missing_ok=True)

    return issues


# ---------------- SEVERITY LOGIC ----------------
def categorize_severity(v):
    v = v.upper()

    if "SQL" in v or "INJECTION" in v:
        return "Critical"
    elif "EXEC" in v or "IMPORT" in v:
        return "High"
    elif "OPEN" in v or "FILE" in v:
        return "Medium"
    else:
        return "Low"


# ---------------- TARGET COLUMNS ----------------
target_cols = [
    "Total Vulnerabilities",
    "Critical Vulnerabilities",
    "High Vulnerabilities",
    "Medium Vulnerabilities",
    "Low Vulnerabilities",
    "Vulnerability Types Detected",
    "Vulnerability Density",
    "Is Fully Secure",
    "Severity Score"
]


# ---------------- MAIN PROCESS ----------------
for idx, row in df.iterrows():

    code = str(row.get("Generated Code", "")).strip()

    if not code:
        continue

    print(f"[{idx+1}/{len(df)}] Processing...")

    try:
        issues = run_rule_engine(code)
    except Exception as e:
        print(f"❌ Error at row {idx}: {e}")
        continue

    total = len(issues)
    critical = high = medium = low = 0
    vuln_types = set()

    for issue in issues:
        sev = categorize_severity(issue["type"])
        vuln_types.add(issue["type"])

        if sev == "Critical":
            critical += 1
        elif sev == "High":
            high += 1
        elif sev == "Medium":
            medium += 1
        else:
            low += 1

    lines = max(len(code.splitlines()), 1)

    density = total / lines
    is_secure = total == 0

    severity_score = (
        critical * 10 +
        high * 7 +
        medium * 4 +
        low * 1
    )

    values = [
        total,
        critical,
        high,
        medium,
        low,
        ", ".join(vuln_types) if vuln_types else None,  # 🔥 FIX
        round(density, 3),
        is_secure,
        severity_score
    ]

    # -------- WRITE ONLY AFTER 8th COLUMN --------
    for i, col in enumerate(target_cols):
        col_index = anchor_index + 1 + i

        value = values[i]

        # 🔥 FIX: prevent dtype crash
        if value == "" or value is None:
            value = None

        if col_index < len(df.columns):
            df.iat[idx, col_index] = value
        else:
            df[col] = None
            df.at[idx, col] = value

    # 🔥 Save progress every 50 rows
    if idx % 50 == 0:
        df.to_csv("AURIX_partial.csv", index=False)
        print("💾 Partial save done...")


# ---------------- SAVE FINAL OUTPUT ----------------
df.to_csv("AURIX_completed_filled.csv", index=False)

print("\n✅ DONE: AURIX_completed_filled.csv generated successfully")