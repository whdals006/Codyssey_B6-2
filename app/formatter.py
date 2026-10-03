from __future__ import annotations

import re


COMMIT_TITLE_MAX = 72
PR_TITLE_MAX = 80


def clean_text(text: str) -> str:
    """AI가 반환한 코드 블록 등을 제거한다."""
    text = text.strip()

    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()

        if len(lines) >= 2:
            text = "\n".join(lines[1:-1])

    return text.strip()


def shorten_title(title: str, limit: int) -> str:
    """제목을 지정 길이 이하로 줄인다."""
    title = title.strip()

    if len(title) <= limit:
        return title

    return title[: limit - 3].rstrip() + "..."


def extract_changed_files(status: str, diff: str) -> list[str]:
    """status/diff에서 변경 파일명을 추출한다."""
    files: list[str] = []

    for line in status.splitlines():
        line = line.strip()

        if len(line) < 4:
            continue

        path = line[3:]

        if " -> " in path:
            path = path.split(" -> ", 1)[1]

        if path and path not in files:
            files.append(path)

    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]

            if path != "/dev/null" and path not in files:
                files.append(path)

    return files[:3]


def normalize_commit(text: str, status: str, diff: str) -> str:
    """커밋 메시지를 요구사항에 맞게 정리한다."""
    text = clean_text(text)

    lines = [
        line.rstrip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        raise ValueError("AI가 빈 커밋 메시지를 반환했습니다.")

    title = lines[0].strip()

    for prefix in (
        "커밋 제목:",
        "Commit:",
        "Title:",
    ):
        if title.startswith(prefix):
            title = title[len(prefix):].strip()

    title = shorten_title(
        title,
        COMMIT_TITLE_MAX,
    )

    body_lines = lines[1:]
    changed_files = extract_changed_files(
        status,
        diff,
    )

    if body_lines:
        has_bullet = any(
            line.lstrip().startswith("-")
            for line in body_lines
        )

        if not has_bullet:
            body_lines = [
                f"- {line}"
                for line in body_lines[:2]
            ]

        body = "\n".join(body_lines)

        if changed_files and not any(
            filename in body
            for filename in changed_files
        ):
            body += (
                "\n- 변경 파일: "
                + ", ".join(changed_files)
            )
    else:
        if changed_files:
            body = (
                "- 변경 파일: "
                + ", ".join(changed_files)
            )
        else:
            body = (
                "- Git diff를 기반으로 "
                "변경 내용을 요약했습니다."
            )

    return f"{title}\n\n{body}"


def extract_pr_sections(body: str) -> dict[str, str]:
    """PR 본문에서 요구된 세 섹션을 추출한다."""
    pattern = re.compile(
        r"^##\s+(Why|What|How to Test)\s*$",
        re.MULTILINE,
    )

    matches = list(pattern.finditer(body))

    sections = {
        "Why": "",
        "What": "",
        "How to Test": "",
    }

    if not matches:
        sections["What"] = body.strip()
        return sections

    for index, match in enumerate(matches):
        section_name = match.group(1)

        start = match.end()

        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(body)
        )

        sections[section_name] = body[
            start:end
        ].strip()

    return sections


def ensure_bullets(
    text: str,
    fallback: str,
) -> str:
    """섹션에 최소 한 개의 불릿이 있도록 만든다."""
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return f"- {fallback}"

    result = []

    for line in lines:
        if line.startswith("-"):
            result.append(line)
        else:
            result.append(f"- {line}")

    return "\n".join(result)


def normalize_pr(
    text: str,
    status: str,
    diff: str,
) -> str:
    """PR 제목과 본문을 요구사항에 맞게 정리한다."""
    text = clean_text(text)

    lines = text.splitlines()

    non_empty = [
        line.strip()
        for line in lines
        if line.strip()
    ]

    if not non_empty:
        raise ValueError(
            "AI가 빈 PR 초안을 반환했습니다."
        )

    title = non_empty[0]

    for prefix in (
        "PR 제목:",
        "PR Title:",
        "Title:",
    ):
        if title.startswith(prefix):
            title = title[len(prefix):].strip()

    title = shorten_title(
        title,
        PR_TITLE_MAX,
    )

    body_start = 1

    for index, line in enumerate(non_empty):
        if line.startswith("## "):
            body_start = index
            break

    body = "\n".join(
        non_empty[body_start:]
    )

    sections = extract_pr_sections(body)

    changed_files = extract_changed_files(
        status,
        diff,
    )

    file_text = (
        ", ".join(changed_files)
        or "변경된 파일"
    )

    why = ensure_bullets(
        sections["Why"],
        "제공된 Git 변경 사항을 기준으로 "
        "변경 목적을 정리했습니다.",
    )

    what = ensure_bullets(
        sections["What"],
        f"변경 파일: {file_text}",
    )

    how = ensure_bullets(
        sections["How to Test"],
        "변경 사항을 확인한 뒤 CLI 명령으로 "
        "결과를 검증합니다.",
    )

    return (
        f"{title}\n\n"
        f"## Why\n"
        f"{why}\n\n"
        f"## What\n"
        f"{what}\n\n"
        f"## How to Test\n"
        f"{how}"
    )


def validate_commit(text: str) -> bool:
    """커밋 메시지의 최소 형식을 검증한다."""
    lines = text.splitlines()

    if not lines or not lines[0].strip():
        return False

    if len(lines[0].strip()) > COMMIT_TITLE_MAX:
        return False

    return True


def validate_pr(text: str) -> bool:
    """PR 제목/본문의 최소 형식을 검증한다."""
    lines = text.splitlines()

    if not lines or not lines[0].strip():
        return False

    if len(lines[0].strip()) > PR_TITLE_MAX:
        return False

    required_sections = (
        "## Why",
        "## What",
        "## How to Test",
    )

    return all(
        section in text
        for section in required_sections
    )