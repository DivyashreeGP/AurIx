# AurIx Secure Code Display - Visual Mockup

## Complete UI Example

This file shows the exact visual layout and structure for the secure code display feature.

---

## 📺 FULL SCREEN LAYOUT

```
═══════════════════════════════════════════════════════════════════════════════
                    AURIX - VULNERABILITY DETAIL VIEW
═══════════════════════════════════════════════════════════════════════════════

┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│  ⓘ  SECURITY DISCLAIMER                                                      │
│  ───────────────────────────────────────────────────────────────────────────  │
│                                                                               │
│  Generated secure code is a REFERENCE IMPLEMENTATION only. Security         │
│  depends on:                                                                 │
│                                                                               │
│  • Your specific application architecture & requirements                    │
│  • Proper input validation and sanitization                                 │
│  • Network security and access control measures                             │
│  • Regular security audits and penetration testing                          │
│  • Keeping libraries and frameworks up-to-date                              │
│                                                                               │
│  Hover for more information ⓘ                                               │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│  ❌ ORIGINAL VULNERABLE CODE (Line 23 of auth/login.py)                     │
│  ───────────────────────────────────────────────────────────────────────────  │
│                                                                               │
│  23  def authenticate_user(username, password):                             │
│  24      query = "SELECT * FROM users WHERE username='" + username + "'"   │
│  25      user = db.execute(query)                                           │
│  26      if user and check_password(user.password, password):               │
│  27          return user                                                     │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│  � HOW TO FIX THIS VULNERABILITY                                           │
│  ───────────────────────────────────────────────────────────────────────────  │
│                                                                               │
│  Follow these steps to fix SQL Injection vulnerabilities:                    │
│                                                                               │
│  1. Use parameterized queries or prepared statements                        │
│     → Separate SQL structure from data                                      │
│                                                                               │
│  2. Never concatenate user input directly into SQL                          │
│     → Always treat user input as data, never as code                        │
│                                                                               │
│  3. Validate and sanitize input types and lengths                           │
│     → Enforce constraints (username ≤ 50 chars, alphanumeric)              │
│                                                                               │
│  4. Use ORM frameworks when possible (SQLAlchemy, Django ORM)               │
│     → These handle parameterization automatically                           │
│                                                                               │
│  5. Apply principle of least privilege to database user                     │
│     → DB user should only have permissions it needs                         │
│                                                                               │
│  6. Implement logging and monitoring                                         │
│     → Alert on suspicious query patterns                                    │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│  🔍 VULNERABILITY ANALYSIS                                                   │
│  ───────────────────────────────────────────────────────────────────────────  │
│                                                                               │
│  Type: SQL Injection                                                        │
│                                                                               │
│  Severity: [  🔴 CRITICAL  ]                                                │
│                                                                               │
│  Issue:                                                                      │
│  User input (username) is directly concatenated into the SQL query without   │
│  any parameterization or escaping. This allows attackers to inject          │
│  arbitrary SQL code.                                                         │
│                                                                               │
│  ⚠️ Risk:                                                                     │
│  • Attackers can bypass authentication by entering: ' OR '1'='1            │
│  • Sensitive data can be extracted or modified                              │
│  • Entire database could be compromised                                     │
│  • Privilege escalation possible through UNION-based attacks                │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│  ✅ SECURE CODE REFERENCE                                                    │
│  ───────────────────────────────────────────────────────────────────────────  │
│                                                                               │
│  Choose from multiple secure implementation patterns:                        │
│                                                                               │
│  ┌─ [Option 1: sqlite3]  [Option 2: PostgreSQL]  [Option 3: ORM] ──┐       │
│  └────────────────────────────────────────────────────────────────┘        │
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ METHOD 1: Using Parameterized Query (sqlite3)                        │  │
│  │ ─────────────────────────────────────────────────────────────────── │  │
│  │                                                                       │  │
│  │ Principle: Use ? placeholders and pass values separately             │  │
│  │                                                                       │  │
│  │ def authenticate_user(username, password):                          │  │
│  │     # Parameters are passed separately from SQL                     │  │
│  │     cursor.execute(                                                 │  │
│  │         "SELECT * FROM users WHERE username = ?",                   │  │
│  │         (username,)  # ← Data goes here, NOT in SQL string          │  │
│  │     )                                                                │  │
│  │     user = cursor.fetchone()                                        │  │
│  │     if user and check_password(user.password, password):            │  │
│  │         return user                                                 │  │
│  │     return None                                                     │  │
│  │                                                                       │  │
│  │ ✓ Why this is secure:                                              │  │
│  │   • The ? tells database to expect a value                         │  │
│  │   • Anything in (username,) is treated as data, not code           │  │
│  │   • Database driver handles escaping internally                    │  │
│  │   • Attacker input like ' OR '1'='1 is treated literally          │  │
│  │                                                                       │  │
│  │ [📋 COPY CODE]                                                      │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ METHOD 2: Using ORM (SQLAlchemy) - RECOMMENDED                        │  │
│  │ ─────────────────────────────────────────────────────────────────── │  │
│  │                                                                       │  │
│  │ Principle: ORM handles all parameterization automatically            │  │
│  │                                                                       │  │
│  │ from sqlalchemy import create_engine, select                        │  │
│  │ from sqlalchemy.orm import Session                                  │  │
│  │                                                                       │  │
│  │ def authenticate_user(username, password):                          │  │
│  │     with Session(engine) as session:                               │  │
│  │         # ORM automatically parameterizes the query                 │  │
│  │         stmt = select(User).where(User.username == username)       │  │
│  │         user = session.scalars(stmt).first()                       │  │
│  │                                                                       │  │
│  │         if user and check_password(user.password, password):        │  │
│  │             return user                                             │  │
│  │     return None                                                     │  │
│  │                                                                       │  │
│  │ ✓ Why this is secure:                                              │  │
│  │   • SQLAlchemy uses prepared statements internally                 │  │
│  │   • No raw SQL strings means no injection possible                 │  │
│  │   • Type safety: username must be string, validated                │  │
│  │   • Database schema is defined in code (auditable)                 │  │
│  │                                                                       │  │
│  │ [📋 COPY CODE]                                                      │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ METHOD 3: Named Parameters (PostgreSQL)                              │  │
│  │ ─────────────────────────────────────────────────────────────────── │  │
│  │                                                                       │  │
│  │ import psycopg2                                                     │  │
│  │                                                                       │  │
│  │ def authenticate_user(username, password, conn):                   │  │
│  │     with conn.cursor() as cur:                                     │  │
│  │         # Named parameters with %(name)s placeholder              │  │
│  │         cur.execute(                                               │  │
│  │             "SELECT * FROM users WHERE username = %(user)s",       │  │
│  │             {"user": username}                                     │  │
│  │         )                                                           │  │
│  │         user = cur.fetchone()                                      │  │
│  │                                                                       │  │
│  │         if user and check_password(user.password, password):        │  │
│  │             return user                                             │  │
│  │     return None                                                     │  │
│  │                                                                       │  │
│  │ ✓ Why this is secure:                                              │  │
│  │   • Named parameters are more readable                             │  │
│  │   • psycopg2 automatically parameterizes                           │  │
│  │   • Prevents SQL injection effectively                             │  │
│  │                                                                       │  │
│  │ [📋 COPY CODE]                                                      │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│  ⚠️  SECURITY WARNING & DISCLAIMER                                          │
│  ───────────────────────────────────────────────────────────────────────────  │
│                                                                               │
│  Even with these secure code examples, the following are ALSO required:     │
│                                                                               │
│  ✓ Input Validation                                                         │
│    Validate username format, length (< 50 chars), allowed characters        │
│    Example: if not re.match(r'^[a-zA-Z0-9_]+$', username):                │
│                                                                               │
│  ✓ Error Handling                                                           │
│    Never expose database errors to users. Log internally.                   │
│    Example: except DatabaseError: log_error(); return generic_msg()        │
│                                                                               │
│  ✓ Database Permissions                                                     │
│    DB user should only SELECT from users table, no DELETE/DROP.             │
│    Use GRANT SELECT ON users TO app_user;                                  │
│                                                                               │
│  ✓ Rate Limiting & Account Lockout                                          │
│    Limit login attempts: 5 tries, then lock for 15 minutes                  │
│                                                                               │
│  ✓ Encryption in Transit                                                    │
│    Use HTTPS/TLS for all authentication endpoints                           │
│                                                                               │
│  ✓ Encryption at Rest                                                       │
│    Hash passwords with bcrypt/Argon2 (never MD5/SHA1)                      │
│                                                                               │
│  ✓ Security Audits                                                          │
│    Professional penetration testing recommended                             │
│                                                                               │
│  🔴 CRITICAL DISCLAIMER:                                                     │
│                                                                               │
│  100% SECURITY CANNOT BE GUARANTEED                                         │
│                                                                               │
│  This tool helps identify common vulnerabilities and provides reference     │
│  secure code examples. However, security is multi-layered and context       │
│  specific. You must:                                                         │
│                                                                               │
│  1. Have qualified security team review code                                │
│  2. Conduct regular security audits & penetration testing                   │
│  3. Monitor for security vulnerabilities in dependencies                    │
│  4. Implement incident response procedures                                  │
│  5. Keep all software updated with security patches                         │
│  6. Follow OWASP Top 10 and your industry standards                         │
│                                                                               │
│  This generated code is a GUIDE only. Test thoroughly in YOUR context.     │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                              END OF VULNERABILITY DETAIL
═══════════════════════════════════════════════════════════════════════════════
```

---

## 📱 MOBILE VIEW (Stacked Layout)

```
‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
  AURIX VULNERABILITY
‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾

┌──────────────────────────┐
│ ⓘ Security Disclaimer    │
│ [Expandable]             │
└──────────────────────────┘

┌──────────────────────────┐
│ ❌ Original Code Line 23 │
│──────────────────────────│
│ def authenticate...      │
│     query = "SELECT...   │
│ [code continues]         │
└──────────────────────────┘

┌──────────────────────────┐
│ � How to Fix            │
│ 1. Use parameterized...  │
│ 2. Never concatenate...  │
│ 3. Validate input...     │
│ [more items]             │
└──────────────────────────┘

┌──────────────────────────┐
│ 🔍 Vulnerability         │
│ Type: SQL Injection      │
│ Severity: 🔴 CRITICAL   │
│──────────────────────────│
│ Issue: Direct concat...  │
│ Risk: Attacker can...    │
└──────────────────────────┘

┌──────────────────────────┐
│ ✅ Secure Code           │
│ [Opt 1] [Opt 2] [Opt 3]  │
│─ Option 1: sqlite3 ──   │
│ cursor.execute(          │
│   "SELECT * WHERE id=?", │
│   (user_id,)             │
│ )                        │
│ [📋 Copy]                │
└──────────────────────────┘

┌──────────────────────────┐
│ ⚠️ Security Warning      │
│ • Input validation       │
│ • Error handling         │
│ • Database permissions   │
│ [more items]             │
│──────────────────────────│
│ 100% SECURITY CANNOT BE  │
│ GUARANTEED               │
└──────────────────────────┘
```

---

## 🎨 COLOR & STYLING REFERENCE

### Vulnerability Severity Colors
```
CRITICAL:  Background #ffebee (light red 50)
           Text: #c62828 (red 800)
           Badge: Circle + text

HIGH:      Background #fff3e0 (light orange 50)
           Text: #e65100 (orange 900)

MEDIUM:    Background #fce4ec (light pink 50)
           Text: #ad1457 (pink 800)

LOW:       Background #f3e5f5 (light purple 50)
           Text: #6a1b9a (purple 800)
```

### Code Block Colors
```
Vulnerable Code:
  Background: #fff3f3 (very light red)
  Border: 1px solid #ffcdd2 (light red)
  Text: #c62828 (dark red)
  Font: 'Courier New', monospace, 13px

Secure Code:
  Background: #f1f8e9 (very light green)
  Border: 1px solid #c5e1a5 (light green)
  Text: #33691e (dark green)
  Font: 'Courier New', monospace, 13px
```

### Icon Colors
```
ⓘ Information: #2196F3 (blue)
🔍 Analysis:   #1976D2 (dark blue)
🔧 Tools:      #4CAF50 (green)
✅ Success:    #4CAF50 (green)
⚠️  Warning:   #FF9800 (orange)
🔴 Critical:   #c62828 (red)
```

---

## 🔲 STATE VARIATIONS

### When Secure Code is Generated
```
SHOWN:
✓ All 4 method tabs
✓ Code examples with syntax highlighting
✓ Copy button (active)
✓ Method explanations
```

### When NO Secure Code Can Be Generated
```
SHOWN:
✓ Vulnerability explanation
✓ How to fix (steps)
✓ "No Secure Code Generated" message
✓ Reason: "This vulnerability requires architectural changes"
✓ Recommendation to consult security team
✓ Warning disclaimer (ALWAYS SHOWN)

HIDDEN:
✗ Code tabs
✗ Code examples
```

### On Hover (Interactive States)
```
Copy Button:
  Normal:  Green (#4CAF50)
  Hover:   Darker green (#45a049)
  Clicked: "✓ Copied" text, disable for 2 seconds

Tab Button:
  Normal:        Gray text, no underline
  Hover:         Darker text, light background
  Active (click): Blue text, blue underline

Disclaimer "ⓘ":
  Hover: Show tooltip with full disclaimer text
```

---

## ✨ ANIMATIONS & TRANSITIONS

```css
Tab switching:    100ms fade-in
Copy feedback:    200ms (instant feedback)
Warning expand:   300ms smooth height transition
Hover effects:    200ms color transition
Color changes:    150ms smooth animation
```

---

## 📊 RESPONSIVE BREAKPOINTS

```
Desktop (> 1200px):
  - 2-column layout possible
  - Full width code blocks
  - Sidebar for navigation

Tablet (768px - 1200px):
  - Single column, full width
  - Code slightly smaller
  - Tabs responsive

Mobile (< 768px):
  - Single column, 100% width
  - Code font: 12px (was 13px)
  - Padding reduced
  - Tabs scroll horizontally
  - Warning inline (not side-by-side)
```

---

## ♿ ACCESSIBILITY FEATURES

```
✓ Semantic HTML (section, article, button, span)
✓ ARIA labels for icons
✓ Color not only visual cue (text + icons)
✓ Focus states on buttons
✓ Keyboard navigation (Tab through tabs)
✓ High contrast mode support
✓ Screen reader friendly headings
✓ Copy button feedback (visual + text)
```

Example ARIA:
```html
<div role="region" aria-label="Security Disclaimer">
<button aria-label="Copy SQL code to clipboard">📋 Copy</button>
<div role="tablist">
  <button role="tab" aria-selected="true">Option 1</button>
</div>
```

---

## 🎯 UX FLOW

1. User sees vulnerability report
2. Click vulnerability → Opens detail panel
3. **Disclaimer banner visible** (always at top)
4. See **original vulnerable code** highlighted in red
5. Read **vulnerability explanation** and **risk**
6. See **step-by-step fix guide**
7. View **secure code options** in tabs
8. **Copy button** allows easy code reuse
9. **Warning footer** explains additional context
10. Can review disclaimer by hovering ⓘ icon

---

This mockup should serve as your visual reference while implementing the component. All layouts are responsive and accessibility-compliant! 🎨
