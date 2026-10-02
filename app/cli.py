from __future__ import annotations

import argparse

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
from app.prompt import build_commit_prompt


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

    commit_parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Gemini 모델 (기본값: {DEFAULT_MODEL})",
    )

    commit_parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"temperature (기본값: {DEFAULT_TEMPERATURE})",
    )

    commit_parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=f"최대 출력 토큰 수 (기본값: {DEFAULT_MAX_TOKENS})",
    )

    return parser


def print_git_info(status: str, diff: str) -> None:
    status_files = [
        line for line in status.splitlines()
        if line.strip()
    ]

    diff_lines = len(diff.splitlines())

    print(
        f"[INFO] Git status 수집 완료: "
        f"{len(status_files)}개 상태 항목"
    )

    print(
        f"[INFO] Git diff 수집 완료: "
        f"{diff_lines}줄"
    )


def run_commit(args: argparse.Namespace) -> None:
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

    prompt = build_commit_prompt(
        changes.status,
        changes.diff,
    )

    print("[INFO] AI API 요청 중...")

    result = generate_text(
        prompt=prompt,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    print("[INFO] AI API 요청 횟수: 1회")

    print("[DONE] 커밋 메시지 생성 완료")
    print()
    print("--- Commit Message ---")
    print(result)
    print("----------------------")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        ensure_project_root()

        if not 0.0 <= args.temperature <= 2.0:
            parser.error(
                "--temperature는 0.0~2.0 범위여야 합니다."
            )

        if args.max_tokens <= 0:
            parser.error(
                "--max-tokens는 1 이상이어야 합니다."
            )

        if args.command == "commit":
            run_commit(args)

    except GitError as exc:
        print(f"[ERROR] Git 오류: {exc}")

    except GeminiAPIError as exc:
        print(f"[ERROR] {exc}")