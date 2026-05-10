import ast
from pathlib import Path
from typing import List, Tuple
from .taint import SemanticTaintAnalyzer
from .report import build_finding


class SemanticScanner:
    def __init__(self, source: str, lines: List[str], file_path: Path = None):
        self.source = source
        self.lines = lines
        self.file_path = file_path

    def scan(self) -> List[dict]:
        try:
            tree = ast.parse(self.source, filename=str(self.file_path) if self.file_path else "<string>")
        except SyntaxError:
            return []

        analyzer = SemanticTaintAnalyzer(self.lines)
        analyzer.visit(tree)
        return self._format_findings(analyzer.findings)

    def _format_findings(self, findings: List[dict]) -> List[dict]:
        results = []
        seen = set()
        for finding in findings:
            signature = (finding["line"], finding["rule_id"], finding["title"])
            if signature in seen:
                continue
            seen.add(signature)
            code_line = finding.get("code", "")
            results.append(build_finding(
                finding["line"],
                code_line,
                finding["rule_id"],
                finding["title"],
                finding["confidence"],
                finding["comment"],
            ))
        return results


def scan_file(path: Path) -> Tuple[List[dict], List[str]]:
    with open(path, "r", encoding="utf-8", errors="ignore") as source_file:
        lines = source_file.readlines()

    source = "".join(lines)
    scanner = SemanticScanner(source, lines, file_path=path)
    return scanner.scan(), lines
