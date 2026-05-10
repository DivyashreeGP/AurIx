"""
Excel Evaluation Automation Script
===================================
Reads code from Excel, evaluates using AurIx rule engine, 
and fills vulnerability details in the Excel file.

Usage:
    python evaluate_excel.py <input_excel> <output_excel>
    
Expected Excel columns:
    - Code: The Python code to evaluate (column name or index)
    - Output columns will be auto-created:
        * Vulnerabilities Found (count)
        * Severity (HIGH/MEDIUM/LOW/none)
        * Categories (comma-separated)
        * Rule IDs (comma-separated)
        * Is Secure (YES/NO)
"""

import pandas as pd
import subprocess
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import tempfile
import uuid

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
DETECT_SCRIPT = PROJECT_ROOT / "detect.py"


def evaluate_code(code: str) -> Dict[str, Any]:
    """
    Evaluate a piece of code using the AurIx rule engine.
    
    Returns:
        dict with keys: vuln_count, severity, categories, rule_ids, is_secure
    """
    # Create temp file for the code
    uid = str(uuid.uuid4())[:8]
    temp_dir = PROJECT_ROOT / "temp_files"
    temp_dir.mkdir(exist_ok=True)
    
    temp_file = temp_dir / f"eval_{uid}.py"
    out_file = PROJECT_ROOT / "results" / f"eval_{uid}.json"
    out_file.parent.mkdir(exist_ok=True)
    
    # Write code to temp file
    temp_file.write_text(code, encoding="utf-8")
    
    try:
        # Run detect.py
        result = subprocess.run(
            ["python", str(DETECT_SCRIPT), str(temp_file), 
             "--only-issues", "--compact", "-o", str(out_file)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if not out_file.exists():
            return {
                "vuln_count": 0,
                "severity": "none",
                "categories": "",
                "rule_ids": "",
                "is_secure": "YES"
            }
        
        # Parse results
        data = json.loads(out_file.read_text(encoding="utf-8"))
        
        # Aggregate results from all files
        total_vulns = 0
        all_categories = set()
        all_rule_ids = set()
        
        for file_path, items in data.items():
            for item in items:
                total_vulns += 1
                if "categories" in item:
                    all_categories.update(item.get("categories", []))
                if "rules" in item:
                    all_rule_ids.update(item.get("rules", []))
        
        # Determine severity
        severity = "none"
        if all_categories:
            if "INJC" in all_categories or "IDAF" in all_categories or "SDIF" in all_categories:
                severity = "HIGH"
            elif "CRYF" in all_categories or "BRAC" in all_categories:
                severity = "HIGH"
            elif "SECM" in all_categories:
                severity = "MEDIUM"
            else:
                severity = "LOW"
        
        return {
            "vuln_count": total_vulns,
            "severity": severity,
            "categories": ", ".join(sorted(all_categories)) if all_categories else "",
            "rule_ids": ", ".join(sorted(all_rule_ids)) if all_rule_ids else "",
            "is_secure": "NO" if total_vulns > 0 else "YES"
        }
        
    except Exception as e:
        print(f"Error evaluating code: {e}")
        return {
            "vuln_count": -1,
            "severity": "ERROR",
            "categories": str(e),
            "rule_ids": "",
            "is_secure": "ERROR"
        }
    finally:
        # Cleanup temp files
        try:
            temp_file.unlink(missing_ok=True)
            out_file.unlink(missing_ok=True)
        except:
            pass


def process_excel(input_file: str, output_file: str, code_column: str = None):
    """
    Process Excel file and evaluate all code samples.
    
    Args:
        input_file: Path to input Excel file
        output_file: Path to output Excel file
        code_column: Name of column containing code (auto-detect if None)
    """
    print(f"📊 Loading Excel file: {input_file}")
    
    # Read Excel
    df = pd.read_excel(input_file)
    print(f"   Found {len(df)} rows")
    
    # Auto-detect code column if not specified
    if code_column is None:
        # Look for common column names
        possible_names = ["code", "Code", "python", "Python", "source", "Source", "script", "Script"]
        for col in df.columns:
            if col in possible_names:
                code_column = col
                break
        
        # If still not found, use first column
        if code_column is None:
            code_column = df.columns[0]
            print(f"   ⚠️ Using first column as code column: {code_column}")
    else:
        print(f"   📝 Using code column: {code_column}")
    
    # Initialize output columns
    output_columns = {
        "Vulnerabilities Found": [],
        "Severity": [],
        "Categories": [],
        "Rule IDs": [],
        "Is Secure": []
    }
    
    # Process each row
    print(f"\n🔍 Evaluating {len(df)} code samples...")
    
    for idx, row in df.iterrows():
        code = str(row[code_column]) if pd.notna(row[code_column]) else ""
        
        # Skip empty code
        if not code.strip():
            result = {
                "vuln_count": 0,
                "severity": "none",
                "categories": "",
                "rule_ids": "",
                "is_secure": "YES"
            }
        else:
            # Evaluate code
            result = evaluate_code(code)
        
        # Store results
        output_columns["Vulnerabilities Found"].append(result["vuln_count"])
        output_columns["Severity"].append(result["severity"])
        output_columns["Categories"].append(result["categories"])
        output_columns["Rule IDs"].append(result["rule_ids"])
        output_columns["Is Secure"].append(result["is_secure"])
        
        # Progress indicator
        if (idx + 1) % 10 == 0 or idx == len(df) - 1:
            print(f"   Processed {idx + 1}/{len(df)} rows...")
    
    # Add output columns to dataframe
    for col_name, col_data in output_columns.items():
        df[col_name] = col_data
    
    # Save to Excel
    print(f"\n💾 Saving results to: {output_file}")
    df.to_excel(output_file, index=False)
    
    # Summary
    total_vulns = sum(output_columns["Vulnerabilities Found"])
    secure_count = sum(1 for x in output_columns["Is Secure"] if x == "YES")
    
    print(f"\n✅ Evaluation Complete!")
    print(f"   Total vulnerabilities found: {total_vulns}")
    print(f"   Secure code samples: {secure_count}/{len(df)}")
    print(f"   Vulnerable code samples: {len(df) - secure_count}/{len(df)}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nExample:")
        print("  python evaluate_excel.py input.xlsx output.xlsx")
        print("  python evaluate_excel.py input.xlsx output.xlsx --code-column my_code")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "evaluation_results.xlsx"
    
    # Parse optional arguments
    code_column = None
    for i, arg in enumerate(sys.argv):
        if arg == "--code-column" and i + 1 < len(sys.argv):
            code_column = sys.argv[i + 1]
    
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file not found: {input_file}")
        sys.exit(1)
    
    process_excel(input_file, output_file, code_column)


if __name__ == "__main__":
    main()