from __future__ import annotations

import argparse

from app.formatter import (
    normalize_commit,
    normalize_pr,
    validate_commit,
    validate_pr,
)
from app.gemini_service import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    GeminiAPIError,
    generate_text,
)
from app.git_service import (
    GitError,
    collect_git_changes,
    ensure_project_root,
)
from app.prompt import (
    build_commit_prompt,
    build_pr_prompt,
)
from app.security import prepare_context


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Git 변경 사항 기반 AI Commit/PR 생성 도구"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    commit_parser = subparsers.add_parser(
        "commit",
        help="커밋 메시지를 생성합니다.",
    )

    pr_parser = subparsers.add_parser(
        "pr",
        help="PR 제목과 본문을 생성합니다.",
    )

    for command_parser in (
        commit_parser,
        pr_parser,
    ):
        command_parser.add_argument(
            "--model",
            default=DEFAULT_MODEL,
            help=(
                "Gemini 모델 "
                f"(기본값: {DEFAULT_MODEL})"
            ),
        )

        command_parser.add_argument(
            "--temperature",
            type=float,
            default=DEFAULT_TEMPERATURE,
            help=(
                "temperature "
                f"(기본값: {DEFAULT_TEMPERATURE})"
            ),
        )

        command_parser.add_argument(
            "--max-tokens",
            type=int,
            default=DEFAULT_MAX_TOKENS,
            help=(
                "최대 출력 토큰 수 "
                f"(기본값: {DEFAULT_MAX_TOKENS})"
            ),
        )

        command_parser.add_argument(
            "--safe-mode",
            action="store_true",
            help="민감정보 마스킹 및 diff 크기 제한",
        )

    return parser


def print_git_info(
    status: str,
    diff: str,
) -> None:
    status_files = [
        line
        for line in status.splitlines()
        if line.strip()
    ]

    diff_lines = len(
        diff.splitlines()
    )

    print(
        "[INFO] Git status 수집 완료: "
        f"{len(status_files)}개 상태 항목"
    )

    print(
        "[INFO] Git diff 수집 완료: "
        f"{diff_lines}줄"
    )


def run_commit(
    args: argparse.Namespace,
) -> None:
    changes = collect_git_changes()

    if not changes.changed:
        print(
            "[INFO] 변경 사항이 없습니다. "
            "커밋 메시지를 생성하지 않고 종료합니다."
        )
        return

    print_git_info(
        changes.status,
        changes.diff,
    )

    status, diff = prepare_context(
        changes.status,
        changes.diff,
        args.safe_mode,
    )

    if args.safe_mode:
        print("[INFO] Safe Mode 활성화")

    prompt = build_commit_prompt(
        status,
        diff,
    )

    print("[INFO] AI API 요청 중...")

    result = generate_text(
        prompt=prompt,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    print(
        "[INFO] AI API 요청 횟수: 1회"
    )

    final_result = normalize_commit(
        result,
        changes.status,
        changes.diff,
    )

    if not validate_commit(
        final_result
    ):
        raise ValueError(
            "생성된 커밋 메시지가 "
            "형식 검증에 실패했습니다."
        )

    print(
        "[DONE] 커밋 메시지 생성 완료"
    )

    print()
    print("--- Commit Message ---")
    print(final_result)
    print("----------------------")


def run_pr(
    args: argparse.Namespace,
) -> None:
    changes = collect_git_changes()

    if not changes.changed:
        print(
            "[INFO] 변경 사항이 없습니다. "
            "PR 초안을 생성하지 않고 종료합니다."
        )
        return

    print_git_info(
        changes.status,
        changes.diff,
    )

    print(
        f"[INFO] 현재 브랜치: "
        f"{changes.branch}"
    )

    status, diff = prepare_context(
        changes.status,
        changes.diff,
        args.safe_mode,
    )

    if args.safe_mode:
        print("[INFO] Safe Mode 활성화")

    prompt = build_pr_prompt(
        status,
        diff,
        changes.branch,
    )

    print("[INFO] AI API 요청 중...")

    result = generate_text(
        prompt=prompt,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    print(
        "[INFO] AI API 요청 횟수: 1회"
    )

    final_result = normalize_pr(
        result,
        changes.status,
        changes.diff,
    )

    if not validate_pr(
        final_result
    ):
        raise ValueError(
            "생성된 PR 초안이 "
            "형식 검증에 실패했습니다."
        )

    lines = final_result.splitlines()

    title = lines[0]

    body = "\n".join(
        lines[2:]
    ).strip()

    print(
        "[DONE] PR 초안 생성 완료"
    )

    print()
    print("--- PR Title ---")
    print(title)

    print()
    print("--- PR Body ---")
    print(body)

    print("----------------")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        ensure_project_root()

        if not 0.0 <= args.temperature <= 2.0:
            parser.error(
                "--temperature는 "
                "0.0~2.0 범위여야 합니다."
            )

        if args.max_tokens <= 0:
            parser.error(
                "--max-tokens는 "
                "1 이상이어야 합니다."
            )

        if args.command == "commit":
            run_commit(args)

        elif args.command == "pr":
            run_pr(args)

    except GitError as exc:
        print(
            f"[ERROR] Git 오류: {exc}"
        )

    except GeminiAPIError as exc:
        print(
            f"[ERROR] {exc}"
        )

    except ValueError as exc:
        print(
            f"[ERROR] {exc}"
        )