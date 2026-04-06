# AI Model Evaluation Prompt

## Project Context
You are evaluating AI models by having them solve real engineering problems on a **Python Vulnerability Detection System** project.

The project structure:
```
Testing/
├── unit_tests/test_detection.py
├── integration_tests/test_integration.py
├── tdd_tests/test_tdd.py
├── bdd_tests/test_bdd.py
├── fixtures/
├── reports/
└── run_all_tests.py
```

## Current Issues to Fix

### Issue #1: Import Errors in Test Files
**Problem**: Multiple test files are trying to import functions `scan_code` and `scan_file` from `detect.py`, but these functions don't exist. The correct function is `scan_line`.

**Files affected**:
- `integration_tests/test_integration.py` - imports `scan_file`
- `tdd_tests/test_tdd.py` - imports `scan_code`
- `bdd_tests/test_bdd.py` - imports `scan_code`

**Current behavior**: All TDD and BDD tests fail with:
```
ImportError: cannot import name 'scan_code' from 'detect'
```

### Issue #2: Backend API Response Format Mismatch
**Problem**: Integration tests expect response to include `"analysis"` field, but backend returns only `"issues"` field.

**Test expectations** (in `test_integration.py`):
```python
self.assertIn("analysis", data)  # This field doesn't exist
```

**Actual response structure**:
```json
{
  "issues": [
    {
      "type": "Security Vulnerability",
      "description": "...",
      "severity": "medium",
      "line": 1,
      "column": 1,
      "code": "import pickle",
      "rules": ["DEPENDENCY-CONFUSION-001"],
      "categories": ["SUPPLY"]
    }
  ]
}
```

### Issue #3: Encoding Errors During Scan
**Problem**: `charmap` codec errors when scanning code with special characters.

**Error message**:
```
Error scanning code: 'charmap' codec can't encode characters in position 2-5
```

---

## Evaluation Task - GIVE THIS PROMPT TO THE AI MODELS

### Task Description
You are given a Python vulnerability detection project with failing tests. Your goal is to fix the issues identified below to make all tests pass.

### Files to Analyze
The project root is at: `c:\Major_Project\Integration\vulnerability-detection-bhavani\`

Key files:
1. `detect.py` - Main vulnerability detection module (contains `scan_line` function)
2. `Testing/integration_tests/test_integration.py` - Integration tests
3. `Testing/tdd_tests/test_tdd.py` - TDD-style tests
4. `Testing/bdd_tests/test_bdd.py` - BDD-style tests
5. `Testing/unit_tests/test_detection.py` - Unit tests

### Specific Problems to Solve

#### Problem 1: Fix Import Errors
**Task**: Update the test files to import the correct function from `detect.py`.

**Requirements**:
- Analyze the `detect.py` file to identify available functions
- Replace incorrect imports (`scan_code`, `scan_file`) with the correct function name
- Ensure all test files can execute without import errors
- Provide the corrected test file code

**Success criteria**:
- No ImportError when running tests
- Tests execute to the point of assertion failures (not import failures)

#### Problem 2: Fix API Response Format
**Task**: Either update the tests to match the actual backend response format, or describe what changes the backend needs.

**Requirements**:
- Review the actual response structure from the backend
- Identify which tests expect `"analysis"` field vs what backend provides
- Provide a solution that aligns test expectations with backend reality
- Consider backward compatibility

**Success criteria**:
- Tests pass the response structure assertions
- Response includes all necessary vulnerability information

#### Problem 3: Handle Unicode/Encoding Issues
**Task**: Fix the encoding error when scanning code with special characters.

**Requirements**:
- Identify where the encoding error occurs in `detect.py`
- Propose a fix that handles UTF-8 and special characters properly
- Ensure the fix works across Windows, Linux, and macOS
- Provide specific code changes

**Success criteria**:
- No encoding errors when scanning code files
- Unicode characters are properly handled
- All tests complete without encoding-related failures

### Output Requirements

Generate Python code that:
1. **For Problem 1**: Provide corrected versions of:
   - `Testing/integration_tests/test_integration.py` (fix `scan_file` import)
   - `Testing/tdd_tests/test_tdd.py` (fix `scan_code` import)
   - `Testing/bdd_tests/test_bdd.py` (fix `scan_code` import)

2. **For Problem 2**: Provide either:
   - Updated test assertions that match real backend behavior, OR
   - Suggested backend response structure changes

3. **For Problem 3**: Provide:
   - Modified `detect.py` code with proper encoding handling
   - Specific line numbers and context for changes

### Constraints
- Don't change the core detection logic
- Maintain backward compatibility where possible
- Follow the existing code style and patterns
- Provide complete, working code (not pseudocode)
- Include explanatory comments for non-obvious fixes

### Deliverables
1. Complete corrected Python files (not just snippets)
2. Explanation of what each change fixes
3. Instructions for testing the changes
4. Details of any potential side effects or warnings

---

## Evaluation Metrics For Each Model

### Correctness Metrics
| Metric | Description | Score |
|--------|-------------|-------|
| **Import Fix Accuracy** | % of import statements correctly fixed | 0-25 pts |
| **Test Pass Rate** | % of tests that pass after fixes | 0-25 pts |
| **API Format Resolution** | Properly addresses response format issue | 0-25 pts |
| **Encoding Fix Quality** | Encoding errors resolved completely | 0-25 pts |
| **TOTAL CORRECTNESS** | | **0-100 pts** |

### Code Quality Metrics
| Metric | Description | Score |
|--------|-------------|-------|
| **Code Style Consistency** | Matches project conventions | 0-10 pts |
| **Error Handling** | Proper exception handling | 0-10 pts |
| **Documentation** | Clear comments and explanations | 0-10 pts |
| **Edge Cases** | Handles edge cases properly | 0-10 pts |
| **TOTAL CODE QUALITY** | | **0-40 pts** |

### Efficiency Metrics
| Metric | Description | Score |
|--------|-------------|-------|
| **Minimal Changes** | Only necessary changes made | 0-10 pts |
| **Performance Impact** | No significant performance degradation | 0-10 pts |
| **TOTAL EFFICIENCY** | | **0-20 pts** |

### FINAL SCORE: **0-160 points**

---

## How To Evaluate Each Model

### Step 1: Run Tests Before Fixes
```bash
cd c:\Major_Project\Integration\vulnerability-detection-bhavani\Testing
python run_all_tests.py 2>&1 | tee baseline_results.txt
```
Record baseline failures.

### Step 2: Apply Model's Proposed Changes
- Copy model output files
- Replace original test files and detect.py
- Save changes for comparison

### Step 3: Run Tests After Fixes
```bash
python run_all_tests.py 2>&1 | tee model_results.txt
```

### Step 4: Compare Results
```bash
# Count test results
grep -E "^(OK|FAILED)" model_results.txt
grep -E "ERROR|FAIL" model_results.txt | wc -l

# Compare import errors
grep "ImportError" model_results.txt
```

### Step 5: Score Each Category

**A. Correctness Testing**
```python
# Test Import Fixes
import sys
sys.path.insert(0, r'c:\Major_Project\Integration\vulnerability-detection-bhavani')
try:
    from detect import scan_line  # Should work
    if scan_line:
        print("✓ Import fix works")
except ImportError as e:
    print(f"✗ Import still broken: {e}")

# Test API Response Format
response_has_all_fields = "issues" in response and "analysis" in response
print(f"✓ Response format correct: {response_has_all_fields}")

# Test Encoding Handling
test_strings = ["Unicode: 你好", "Special: @#$%", "Long unicode: " + "😀" * 100]
for s in test_strings:
    try:
        result = scan_line(s)
        print(f"✓ Handled: {s[:20]}")
    except Exception as e:
        print(f"✗ Failed on: {s[:20]} - {e}")
```

### Step 6: Scoring Formula

```
Correctness Score = 
  (Import Fixes: 0-25) + 
  (Test Pass %: 0-25) + 
  (API Format: 0-25) + 
  (Encoding Fix: 0-25)

Code Quality Score = 
  (Style: 0-10) + 
  (Error Handling: 0-10) + 
  (Documentation: 0-10) + 
  (Edge Cases: 0-10)

Efficiency Score = 
  (Minimal Changes: 0-10) + 
  (Performance: 0-10)

FINAL SCORE = Correctness + Code Quality + Efficiency
```

### Step 7: Evaluation Template

```
MODEL: [Model Name]
DATE: [Date]

RESULTS:
- Unit Tests: [X/34 passed]
- Integration Tests: [X/15 passed]
- TDD Tests: [X/22 passed]
- BDD Tests: [X/11 passed]
- TOTAL: [X/82 passed]

SCORING:
- Import Fixes: [X/25]
- Test Pass Rate: [X/25]
- API Format Fix: [X/25]
- Encoding Fix: [X/25]
- Code Quality: [X/40]
- Efficiency: [X/20]
TOTAL SCORE: [X/160]

STRENGTHS:
- [...]

WEAKNESSES:
- [...]

NOTES:
- [...]
```

