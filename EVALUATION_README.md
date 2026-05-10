"""
Sample Excel structure for evaluation

Create an Excel file with this column structure:

| Code | (your Python code here) |
|------|------------------------|
| def vulnerable(): ... |  # Row 1: Code to evaluate |
| print("hello") |        # Row 2: Code to evaluate |

The script will automatically add these columns to the output:

| Vulnerabilities Found | Severity | Categories | Rule IDs | Is Secure |
|----------------------|----------|------------|----------|-----------|
| 2 | HIGH | INJC,BRAC | SQL-001,CMD-001 | NO |
| 0 | none | | | YES |
"""

# Example usage:
# python evaluate_excel.py Evaluation/samples.xlsx Evaluation/results.xlsx

# Or with custom code column:
# python evaluate_excel.py Evaluation/samples.xlsx Evaluation/results.xlsx --code-column "Source Code"