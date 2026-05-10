from dataclasses import dataclass


@dataclass
class Vulnerability:
    vuln_type: str
    line: int
    description: str