"""Lightweight sanity checks for generated Pine Script.

This is not a full Pine compiler — it catches the structural mistakes a
generator can make (missing version pragma, unbalanced brackets, no entry call)
so we never hand the user obviously-broken code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ValidationResult:
    ok: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.ok


def _balanced(text: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: List[str] = []
    in_str = False
    quote = ""
    for ch in text:
        if in_str:
            if ch == quote:
                in_str = False
            continue
        if ch in ('"', "'"):
            in_str = True
            quote = ch
        elif ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack and not in_str


def validate_pine(code: str) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []

    if "//@version=" not in code:
        errors.append("missing //@version pragma")
    if "strategy(" not in code and "indicator(" not in code:
        errors.append("no strategy() or indicator() declaration")
    if "strategy(" in code:
        if "strategy.entry" not in code:
            errors.append("strategy has no strategy.entry call")
        if "strategy.exit" not in code and "strategy.close" not in code:
            warnings.append("strategy has no exit/close — positions never close")
    if not _balanced(code):
        errors.append("unbalanced brackets or unterminated string")
    if "= false\n" in code or "longEntry  = false" in code:
        warnings.append("an entry/exit condition is constant false (no rules?)")

    return ValidationResult(ok=not errors, errors=errors, warnings=warnings)
