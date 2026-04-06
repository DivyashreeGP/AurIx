#!/usr/bin/env python3
"""TESTING GUIDE - Follow these steps to debug the issue"""

instructions = """
=================================================================
DEBUGGING: Why Secure Code Is Not Showing
=================================================================

STEP 1: Reload Extension
---------------------------
1. Click on Extension Dev Host window/terminal
2. Press Ctrl+F5 (or F5, then Ctrl+R) to force reload
3. Wait for "DeVAIC extension activating" logs to appear

STEP 2: Open Developer Console  
---------------------------
1. In the Extension Dev Host (NOT main VS Code), press Ctrl+Shift+I
2. Go to "Console" tab
3. This is where you'll see DeVAIC debug logs

STEP 3: Test with Vulnerable Code
----------------------------------
1. Create/open test_vulns.py in the editor
2. Paste this code:

   import pickle
   data = request.args.get('x')
   obj = pickle.loads(data)

3. Save the file (Ctrl+S) - this triggers AI analysis
4. Watch the Console for logs

STEP 4: Read the Console Logs
------------------------------
Look for these console messages (in order):

✓ "DeVAIC: Sending to AI analysis engine..."
✓ "DeVAIC AI: response from http://..."
✓ "DeVAIC AI: analysis result received"
✓ "(Shows secure_code in response)"
✓ "DeVAIC: showAnalysisPanel called with:"
✓ "=== DeVAIC HTML GENERATION ==="
✓ "(Shows secureCode length and sample)"

STEP 5: Check Console Output
-----------------------------
In the "DeVAIC AI: analysis result received" section, you should see:
  - secure_code: "import json\\ndata = request..."

In the "DeVAIC HTML GENERATION" section, you should see:
  - secureCode length: 63 (or similar)
  - secureCode sample: "import json\\ndata..."
  - secureCode check (...> 0): true

STEP 6: Look at the Panel
--------------------------
Click on "✅ Secure Code" tab in the analysis panel
You should see the TRANSFORMED code with:
  - pickle.loads → json.loads
  - OR eval() → ast.literal_eval()
  - OR shell=True → shell=False
  - etc.

STEP 7: Report Findings
------------------------
Check Console and tell me:
1. What does "secure_code" say in the response?
2. What does "secureCode length" say after "HTML GENERATION"?
3. Is the "Secure Code" tab showing:
   a) The transformed secure code? ✅
   b) "No secure code available" message? ❌
   c) Original code (unchanged)? ❌

=================================================================
COMMON ISSUES & SOLUTIONS
=================================================================

Issue: Console shows "secure_code: undefined"
→ Backend is not returning secure_code field
→ Solution: Restart backend (Ctrl+C in terminal, then run again)

Issue:"secureCode length: 0" in HTML GENERATION
→ Response received but secure_code is empty
→ Solution: Check backend logs for errors

Issue: Showing "No secure code available" 
→ HTML condition (secureCode && secureCode.length > 0) is FALSE
→ Check console to see actual secureCode received

Issue: Secure Code tab shows ORIGINAL code (not transformed)
→ secure_code IS being received but it's same as original
→ This is expected if Ollama is not running
→ Backend uses template transformations which only handle specific patterns

=================================================================
"""

print(instructions)

# Also save to file for reference
with open('DEBUG_INSTRUCTIONS.txt', 'w') as f:
    f.write(instructions)

print("\n✓ Instructions saved to DEBUG_INSTRUCTIONS.txt")
