from __future__ import annotations


COMMON_INSTRUCTIONS = """
너는 Git 변경 사항을 분석하는 개발 보조 AI다.

반드시 제공된 git status와 git diff에 있는 정보만 사용한다.
변경 내용에 없는 사실을 추측하거나 만들어내지 않는다.
출력은 한국어로 작성한다.
불필요한 설명이나 코드 블록을 사용하지 않는다.
"""


def build_commit_prompt(status: str, diff: str) -> str:
    return f"""
{COMMON_INSTRUCTIONS}

다음 Git 변경 사항을 바탕으로 커밋 메시지를 작성한다.

[git status]
{status}

[git diff]
{diff}

작성 규칙:
1. 첫 번째 줄은 커밋 제목이다.
2. 커밋 제목은 50자 이내를 권장하며 최대 72자로 작성한다.
3. 제목은 feat, fix, docs, refactor 등 변경 성격이 드러나도록 작성한다.
4. 본문을 작성한다면 핵심 변경 내용을 1~2개의 불릿으로 작성한다.
5. 본문에는 변경된 파일 또는 모듈을 1~3개 언급한다.
6. 제목과 본문만 출력한다.
7. "커밋 제목:", "본문:" 같은 설명용 접두어는 사용하지 않는다.
"""


def build_pr_prompt(
    status: str,
    diff: str,
    branch: str,
) -> str:
    return f"""
{COMMON_INSTRUCTIONS}

현재 브랜치는 {branch} 이다.

다음 Git 변경 사항을 바탕으로 Pull Request 초안을 작성한다.

[git status]
{status}

[git diff]
{diff}

반드시 아래 구조를 그대로 사용한다.

첫 번째 줄:
PR 제목 한 줄

그 다음:
## Why
- 변경 배경 또는 목적

## What
- 핵심 변경 사항

## How to Test
- 실제로 확인할 수 있는 테스트 방법

작성 규칙:
1. PR 제목은 최대 80자다.
2. Why, What, How to Test 섹션은 반드시 모두 작성한다.
3. 각 섹션에는 최소 1개의 불릿을 작성한다.
4. 제공된 변경 사항에서 확인할 수 없는 내용을 사실처럼 만들지 않는다.
5. 실제 테스트 코드가 확인되지 않는 경우 확인 가능한 범위에서 테스트 방법을 작성한다.
6. 설명용 접두어 없이 결과만 출력한다.
"""