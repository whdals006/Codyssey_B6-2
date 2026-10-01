#

## 1. 프로젝트 구조 만들기

* 프로젝트 기본 구조

```
B6-2/
├── app/
│   ├── __init__.py
│   ├── cli.py              ; CLI 명령 처리 (commit, pr)
│   ├── git_service.py      ; Git 명령 실행 (git status, git diff)
│   ├── gemini_service.py   ; Gemini REST API 호출
│   ├── prompt.py           ; AI에게 전달할 Commit/PR 프롬프트 생성
│   ├── formatter.py        ; AI 결과 검증 및 후처리
│   └── security.py         ; Safe Mode
├── main.py                 ; 프로그램 시작점
├── README.md
└── .gitignore
```

## 2. Git 변경 사항 수집 기능 만들기

이번 단계의 목표

```
① python에서 git status, git diff, 현재 브랜치 가져오기
② Git 프로젝트 루트가 아닌 곳에서 실행하면 오류가 나도록 만들기
```

### 2-1. app/git_service.py 생성

* `run_git_command()`

run_git_command("status", "--short") 를 실행하면 아래 명령어가 실행된다.

```bash
git status --short
```

* `get_repo_root()`

```bash
git rev-parse --show-toplevel
```

위 명령어를 실행해서 현재 Git 저장소의 최상위 디렉토리를 찾는다.

현재 프로젝트에서는

```
/home/jongmin006/codyssey/B6-2
```

가 나와야 한다.

* `ensure_project_root()`

미션 요구사항에 있는

> CLI 실행은 Git이 초기화된 프로젝트 루트 디렉토리에서 수행

을 검사하는 함수. B6-2 이외의 디렉토리에서 실행하면 오류가 발생한다.

테스트 방법:

```bash
python3 -c "from app.git_service import get_repo_root; print(get_repo_root())"
```

결과 예시:

```
/home/jongmin006/codyssey/B6-2
```

* `collect_git_changes()`

실제로 AI에게 전달할 데이터를 하나로 묶는다.

```python
GitChanges(
    status=status,
    diff=diff,
    branch=branch,
)
```

그래서 이후 단계에서는 다음처럼 사용한다.

```python
changes.status
changes.diff
changes.branch
```

테스트 방법:

```bash
python3 -c "from app.git_service import collect_git_changes; x=collect_git_changes(); print('--- STATUS ---'); print(x.status); print('--- DIFF ---'); print(x.diff); print('--- BRANCH ---'); print(x.branch)"
```

결과 예시:

```
--- STATUS ---
 M app/git_service.py

--- DIFF ---
diff --git a/app/git_service.py b/app/git_service.py
...

--- BRANCH ---
main
```

