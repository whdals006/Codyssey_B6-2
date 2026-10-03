from __future__ import annotations

import re


MAX_SAFE_FILES = 10
MAX_SAFE_LINES = 200


SECRET_PATTERNS = [
    (
        re.compile(
            r"(?i)(api[_-]?key|token|secret|password)"
            r"(\s*[:=]\s*)([^\s\"']+)"
        ),
        r"\1\2***MASKED***",
    ),
    (
        re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
        "***MASKED_API_KEY***",
    ),
]


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@"
    r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


def mask_sensitive_data(text: str) -> str:
    """민감할 가능성이 있는 문자열을 마스킹한다."""
    result = text

    for pattern, replacement in SECRET_PATTERNS:
        result = pattern.sub(
            replacement,
            result,
        )

    result = EMAIL_PATTERN.sub(
        "***MASKED_EMAIL***",
        result,
    )

    return result


def limit_diff(diff: str) -> str:
    """Safe Mode용으로 diff 파일 수와 줄 수를 제한한다."""
    if not diff.strip():
        return ""

    chunks = diff.split("diff --git ")

    chunks = chunks[
        1 : MAX_SAFE_FILES + 1
    ]

    selected = "\n".join(
        f"diff --git {chunk}"
        for chunk in chunks
    )

    lines = selected.splitlines()[
        :MAX_SAFE_LINES
    ]

    return "\n".join(lines)


def prepare_context(
    status: str,
    diff: str,
    safe_mode: bool,
) -> tuple[str, str]:
    """AI에게 전달할 Git 컨텍스트를 준비한다."""
    if not safe_mode:
        return status, diff

    safe_status = mask_sensitive_data(
        status
    )

    safe_diff = limit_diff(diff)

    safe_diff = mask_sensitive_data(
        safe_diff
    )

    return safe_status, safe_diff