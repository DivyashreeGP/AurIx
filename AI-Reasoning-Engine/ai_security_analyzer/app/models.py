from typing import List, Dict


class Vulnerability:
    def __init__(self, vuln_type: str, line: int, description: str):
        self.type = vuln_type
        self.line = line
        self.description = description

    def to_dict(self):
        return {
            "type": self.type,
            "line": self.line,
            "description": self.description
        }


def serialize_vulnerabilities(vulns: List[Vulnerability]) -> List[Dict]:
    return [v.to_dict() for v in vulns]