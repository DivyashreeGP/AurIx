import ast
from typing import Tuple, List


def get_call_chain(node: ast.AST) -> Tuple[str, ...]:
    if isinstance(node, ast.Name):
        return (node.id,)

    if isinstance(node, ast.Attribute):
        chain: List[str] = []
        while isinstance(node, ast.Attribute):
            chain.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            chain.append(node.id)
        return tuple(reversed(chain))

    if isinstance(node, ast.Call):
        return get_call_chain(node.func)

    return ()


def get_line_text(lines: List[str], lineno: int) -> str:
    if 1 <= lineno <= len(lines):
        return lines[lineno - 1].rstrip("\n")
    return ""


def is_string_literal(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def any_name_in_expr(node: ast.AST, names: Tuple[str, ...]) -> bool:
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and sub.id in names:
            return True
    return False
