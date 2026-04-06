import os, re, json, shutil, time
from pathlib import Path

RULESET_DIR = Path("version_2.0/ruleset")

VALID_ESCAPES = set(list("AbBdDsSwWZfnrtvu0123456789") + [ "\\", ".", "^", "$", "*", "+", "?", "{", "}", "[", "]", "(", ")", "|"])

def fix_bad_ranges(p: str) -> str:
    # Fix [a-Z] -> [A-Za-z]; also common typos like [A-z] -> [A-Za-z]
    def repl(m):
        content = m.group(1)
        content = content.replace("a-Z", "A-Za-z")
        content = content.replace("A-z", "A-Za-z")
        return "[" + content + "]"
    return re.sub(r"\[([^\]]+)\]", repl, p)

def fix_weird_var_placeholder_escapes(p: str) -> str:
    # Turn \VAR_PLACEHOLDER -> VAR_PLACEHOLDER (causes \V error)
    p = p.replace(r"\VAR_PLACEHOLDER", "VAR_PLACEHOLDER")
    return p

def fix_unknown_escapes(p: str) -> str:
    # Remove backslash before letters that are not valid regex escapes
    # Example: \e -> e, \c -> c, \url -> url
    def repl(m):
        ch = m.group(1)
        return ch
    return re.sub(r"\\([A-Za-ik-mo-qs-tvwyxz])", repl, p)  # skip valid escapes and u/n/r/t/f/d/s/w/etc.

def escape_lonely_backslashes(p: str) -> str:
    # Replace a single backslash before non-meta with literal char (same as above but broad)
    return re.sub(r"\\(?![\\AbBdDsSwWZfnrtvu0-9\.\^\$\*\+\?\{\}\[\]\(\)\|])", r"", p)

def balance_brackets(p: str) -> str:
    # Best-effort add missing closing bracket/paren if clearly unbalanced
    opens = {"(": ")", "[": "]", "{": "}"}
    closes = {")", "]", "}"}
    stack = []
    for ch in p:
        if ch in opens:
            stack.append(opens[ch])
        elif ch in closes and stack and ch == stack[-1]:
            stack.pop()
    # append missing closers at end
    return p + "".join(reversed(stack))

def tidy_spaces(p: str) -> str:
    # collapse accidental double spaces around operators that are literals in patterns we saw
    return p.replace("  ", " ")

def try_compile(rx: str) -> bool:
    try:
        re.compile(rx)
        return True
    except re.error:
        return False

def auto_fix(rx: str) -> str | None:
    original = rx
    # staged fixes
    for step in (
        fix_bad_ranges,
        fix_weird_var_placeholder_escapes,
        fix_unknown_escapes,
        escape_lonely_backslashes,
        balance_brackets,
        tidy_spaces,
    ):
        rx = step(rx)
        if try_compile(rx):
            return rx
    return None

def process_file(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    problems = []

    for rule in data:
        # fields to process: pattern + each pattern_not
        # 1) pattern
        pat = rule.get("pattern")
        if isinstance(pat, str):
            if not try_compile(pat):
                fixed = auto_fix(pat)
                if fixed is not None and fixed != pat:
                    rule["pattern"] = fixed
                    changed = True
                else:
                    problems.append(("pattern", rule.get("id"), pat))
        # 2) pattern_not list
        pn_list = rule.get("pattern_not", [])
        if isinstance(pn_list, list):
            new_list = []
            for pn in pn_list:
                if isinstance(pn, str) and not try_compile(pn):
                    fixed = auto_fix(pn)
                    if fixed is not None:
                        new_list.append(fixed)
                        changed = True
                    else:
                        problems.append(("pattern_not", rule.get("id"), pn))
                        new_list.append(pn)  # keep original if unfixable
                else:
                    new_list.append(pn)
            rule["pattern_not"] = new_list

    return data, changed, problems

def main():
    if not RULESET_DIR.exists():
        print(f"Ruleset dir not found: {RULESET_DIR}")
        return

    ts = time.strftime("%Y%m%d_%H%M%S")
    backup_dir = RULESET_DIR.parent / f"ruleset_backup_{ts}"
    shutil.copytree(RULESET_DIR, backup_dir)
    print(f"📦 Backup created at: {backup_dir}")

    total_changed = 0
    total_files = 0
    outstanding = []

    for fn in sorted(RULESET_DIR.glob("*.json")):
        total_files += 1
        fixed_data, changed, probs = process_file(fn)
        if changed:
            fn.write_text(json.dumps(fixed_data, indent=4, ensure_ascii=False), encoding="utf-8")
            total_changed += 1
            print(f"✅ Fixed: {fn.name}")
        else:
            print(f"OK: {fn.name}")
        outstanding.extend([(fn.name, kind, rid, pat) for (kind, rid, pat) in probs])

    print("\n──────── SUMMARY ────────")
    print(f"Files scanned: {total_files}")
    print(f"Files modified: {total_changed}")
    if outstanding:
        print("\n⚠️ Still problematic patterns (manual review needed):")
        for fname, kind, rid, pat in outstanding:
            print(f"[{fname}] {rid} -> {kind}\n  {pat}\n")
    else:
        print("All patterns compile ✅")

if __name__ == "__main__":
    main()
