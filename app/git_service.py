from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


class GitError(RuntimeError):
    """Git 명령 실행 중 발생한 오류."""


@dataclass
class GitChanges:
    status: str
    diff: str
    branch: str

    @property
    def changed(self) -> bool:
        return bool(self.status.strip() or self.diff.strip())


def run_git_command(*args: str) -> str:
    """Git 명령을 실행하고 stdout을 반환한다."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise GitError("Git이 설치되어 있지 않습니다.") from exc
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or "Git 명령 실행에 실패했습니다."
        raise GitError(message) from exc

    return result.stdout.strip()


def get_repo_root() -> Path:
    """현재 Git 저장소의 루트 경로를 반환한다."""
    root = run_git_command("rev-parse", "--show-toplevel")
    return Path(root).resolve()


def ensure_project_root() -> Path:
    """CLI가 Git 프로젝트 루트에서 실행되었는지 확인한다."""
    repo_root = get_repo_root()
    current_dir = Path.cwd().resolve()

    if current_dir != repo_root:
        raise GitError(
            "Git 프로젝트 루트 디렉토리에서 실행해야 합니다.\n"
            f"현재 위치: {current_dir}\n"
            f"프로젝트 루트: {repo_root}"
        )

    return repo_root


def collect_git_changes() -> GitChanges:
    """현재 Git 상태, diff, 브랜치를 수집한다."""
    status = run_git_command("status", "--short")
    diff = run_git_command("diff", "--no-ext-diff", "--unified=3")
    branch = run_git_command("branch", "--show-current")

    return GitChanges(
        status=status,
        diff=diff,
        branch=branch or "detached",
    )