import pandas as pd
import subprocess
import json
import tempfile
import os
import uuid
from pathlib import Path

# -------- PATH CONFIG --------
ROOT = Path(__file__).resolve().parent.parent
DETECT_PATH = ROOT / "detect.py"

# -------- DATA --------
df = pd.read_csv("AURIX_completed.csv")
codes = df["Generated Code"].dropna().tolist()

TEMP_DIR = ROOT / "temp_eval"
RESULT_DIR = ROOT / "results_eval"

TEMP_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)


# -------- AURIX (detect.py) --------
def run_aurix(code: str):
    uid = str(uuid.uuid4())

    temp_file = TEMP_DIR / f"{uid}.py"
    out_file = RESULT_DIR / f"{uid}.json"

    temp_file.write_text(code, encoding="utf-8")

    subprocess.run([
        "python",
        str(DETECT_PATH),
        str(temp_file),
        "--only-issues",
        "--compact",
        "-o",
        str(out_file)
    ], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not out_file.exists():
        temp_file.unlink(missing_ok=True)
        return False

    data = json.loads(out_file.read_text(encoding="utf-8"))

    # if any issue exists → vulnerable
    vulnerable = any(len(v) > 0 for v in data.values())

    temp_file.unlink(missing_ok=True)
    out_file.unlink(missing_ok=True)

    return vulnerable


# -------- BANDIT --------
def run_bandit(code: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode())
        path = f.name

    result = subprocess.run(
        ["bandit", "-f", "json", path],
        capture_output=True,
        text=True
    )

    os.unlink(path)

    try:
        data = json.loads(result.stdout)
        return len(data.get("results", [])) > 0
    except:
        return False


# -------- METRICS --------
TP = FP = FN = TN = 0


# -------- PROCESS --------
for i, code in enumerate(codes):
    print(f"[{i+1}/{len(codes)}] Processing...")

    aurix_pred = run_aurix(code)
    bandit_pred = run_bandit(code)

    if aurix_pred and bandit_pred:
        TP += 1
    elif aurix_pred and not bandit_pred:
        FP += 1
    elif not aurix_pred and bandit_pred:
        FN += 1
    else:
        TN += 1


# -------- CALCULATIONS --------
total = TP + FP + FN + TN

precision = TP / (TP + FP) if (TP + FP) else 0
recall = TP / (TP + FN) if (TP + FN) else 0
accuracy = (TP + TN) / total if total else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0


# -------- PRINT --------
print("\n=== BINARY EVALUATION (AurIx vs Bandit) ===")
print(f"TP: {TP}")
print(f"FP: {FP}")
print(f"FN: {FN}")
print(f"TN: {TN}")

print("\nMetrics:")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"Accuracy: {accuracy:.3f}")
print(f"F1 Score: {f1:.3f}")