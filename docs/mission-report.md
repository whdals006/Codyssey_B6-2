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

* GitChanges 클래스

GitChanges 클래스의 메서드로 변경 사항 존재 여부를 확인할 수 있다.

```python
@property
def changed(self) -> bool:
    return bool(self.status.strip() or self.diff.strip())
```

즉,

```python
if changes.changed:
    print("변경 사항 있음")
else:
    print("변경 사항 없음")
```

처럼 사용할 수 있다.

테스트:

```bash
python3 -c "from app.git_service import collect_git_changes; x=collect_git_changes(); print('변경 사항 있음' if x.changed else '변경 사항 없음')"
```

예상 결과:

```
변경 사항이 있으면 '변경 사항 있음' 이 출력되고,
변경 사항이 없으면 '변경 사항 없음' 이 출력된다.
```

## 3. Gemini REST API 연동

### WSL에서 API Key 설정

* `export` 명령어로 API Key 환경변수에 저장

```bash
export GEMINI_API_KEY="여기에_본인의_API_KEY"
```

* 환경변수에 저장된 API Key 확인하는 방법

```bash
echo $GEMINI_API_KEY
```

* API Key가 환경변수 설정됬는지 확인하는 방법

```bash
python3 -c "import os; print('설정됨' if os.getenv('GEMINI_API_KEY') else '설정되지 않음')"
```

### 실제 Gemini API 호출 테스트

```bash
python3 -c "from app.gemini_service import generate_text; print(generate_text('Python에서 REST API가 무엇인지 한 문장으로 설명해줘.', max_tokens=100))"
```

### AI 모델 확인하는 방법

```bash
python3 -c "from app.gemini_service import DEFAULT_MODEL; print(DEFAULT_MODEL)"
```

### `export` 방식과 `.env` 방식의 차이

| 구분 | `export` | `.env` |
| :--- | :--- | :--- |
| 적용 범위 | 현재 열려있는 터미널 창에서만 유효 | .env 파일이 있는 프로젝트 폴더 내 |
| 지속성 | 터미널 닫으면 삭제됨 | 파일로 저장되어 있어 계속 유지됨 |
| 적용 방법 | 명령어 실행 즉시 적용 | `python-dotenv` 같은 라이브러리로 로드 |

### AI API 파라미터

1. `temperature`

    AI가 답변을 작성할 때 "얼마나 창의적/무작위적으로 단어를 선택할 것인가"를 결정하는 조절바.

    * 값이 낮을 때 (0.0~0.2)
        - 특징 : 가장 확률이 높은 단어만 선택. 정답이 정해져 있음.
        - 장점 : 정교함, 정확성 높음, 일관성 유지
        - 추천 용도 : 코드 작성, 수학 계산

    * 값이 높을 때 (0.7~1.0)
        - 특징 : 확률이 낮더라도 다양한 단어를 시도. 답변이 다양해지고 창의적으로 변함
        - 장점 : 독창적이고 풍부한 표현
        - 추천 용도 : 소설/시 쓰기, 아이디어 브레인스토밍

2. `max tokens`

    AI가 한 번의 응답에서 생성할 수 있는 최대 단어/글자 수의 제한.

    * token이란?
        - AI가 텍스트를 처리하는 기본 단위
        - 영문은 1단어=1.3토큰, 국문은 1글자=1~3토큰
    * 설정하는 이유
        - 비용 절감
        - 응답 시간 단축

3. `Top-K` (K: 변수 K)

    `Temperature`와 함께 작동하여 AI가 다음 단어를 선택할 때 후보군을 얼마나 좁힐지 결정하는 샘플링(Sampling) 파라미터

    * 동작 방식
        - 확률이 가장 높은 상위 K개의 단어만 후보로 남기고 나머지는 잘라내는 방식
        - 예를 들어 `Top-K = 5`로 설정하면, AI는 확률 상위 1~5위 단어 중에서만 다음 단어를 선택한다. 6위 이하의 단어는 아무리 확률이 높아도 무시된다.
    * Top-K가 작을 때 (예: 5~10)
        - 매우 뻔하고 확실한 단어만 선택하므로 답변이 안정적이고 예측 가능.
    * Top-K가 클 때 (예: 40~100)
        - 다양한 단어가 후보에 오르므로 답변이 다채로진다.

4. `Top-P` (P: Probability)

    `Temperature`와 함께 작동하여 AI가 다음 단어를 선택할 때 후보군을 얼마나 좁힐지 결정하는 샘플링(Sampling) 파라미터

    * 동작 방식
        - 단어의 개수를 고정하는 대신, 상위 단어들의 확률을 더해 나가다가 누적 합이 P(0.0~1.0)에 도달할 때까지만 후보로 포함하는 방식
        - `Top-P = 0.9`로 설정하면, 확률 상위 단어부터 더해서 누적 확률이 90%가 되는 지점까지만 후보군에 넣는다.
    * 특징
        - 상황에 따라 후보 단어의 개수가 가변적으로 조절된다.
        - 정답이 확실한 문맥(확률 90%짜리 단어 1개 존재)에서는 후보가 1개로 줄어들고, 정답이 모호한 문맥에서는 후보가 10개 이상으로 늘어난다.

### API 오류 처리

1. HTTP 오류

    ```python
    except urllib.error.HTTPError
    ```

    예를 들어:

    ```
    401, 403, 429, 500
    ```

    등의 HTTP 오류가 발생했을 때 Gemini가 반환한 오류 메시지를 가져온다.

2. 네트워크 오류

    ```python
    except urllib.error.URLError
    ```

    인터넷 연결이나 DNS 등의 문제가 생겼을 때 사용된다.

3. 응답 형식 오류

    Gemini가 정상적으로 응답했어도 우리가 예상한 구조가 아니면

    ```python
    data["candidates"][0]["content"]["parts"][0]["text"]
    ```

    에서 오류가 발생할 수 있기 때문에 별도로 처리한다.

## 4. Commit / PR 프롬프트 설계

### Commit 프롬프트 설계

* AI한테 전달하는 내용

    ```
    COMMON_INSTRUCTIONS
    git status
    git diff
    작성 규칙
    ```

* COMMON_INSTRUCTIONS

    : Commit 과 PR 프롬프트에 공동으로 사용되는 Instruction.

* `git status` 와 `git diff`를 전달하는 이유

    - `git status` : 변경된 파일의 상태를 알 수 있다.
    - `git diff` : 실제 어떤 코드가 변경됬는지 알 수 있다.

* Commit 작성 규칙

    * Commit 제목 규칙

        ```
        1. 첫 번째 줄은 커밋 제목이다.
        2. 커밋 제목은 50자 이내를 권장하며 최대 72자로 작성한다.
        3. 제목은 feat, fix, docs, refactor 등 변경 성격이 드러나도록 작성한다.
        ```

    * Commit 본문 규칙

        ```
        4. 본문을 작성한다면 핵심 변경 내용을 1~2개의 불릿으로 작성한다.
        5. 본문에는 변경된 파일 또는 모듈을 1~3개 언급한다.
        ```

* AI한테 전달되는 Commit 프롬프트 확인

```python
python3 -c "from app.prompt import build_commit_prompt; print(build_commit_prompt(' M main.py', 'diff --git a/main.py b/main.py\n+print(\"hello\")'))"
```

### PR 프롬프트 설계

* AI한테 전달하는 내용

    ```
    COMMON_INSTRUCTIONS
    현재 브랜치
    git status
    git diff
    PR 템플릿 구조
    작성 규칙
    ```

* AI한테 전달되는 PR 프롬프트 확인

```python
python3 -c "from app.prompt import build_pr_prompt; print(build_pr_prompt(' M main.py', 'diff --git a/main.py b/main.py\n+print(\"hello\")', 'feature/test'))"
```

## 5. cli.py 에 commit 기능 추가


## 6. cli.py 에 pr 기능 추가


## 7. 출력 형식 검증

이번 단계에서 추가되는 기능

```
1. Commit 결과 검증
2. PR 결과 검증
```


## 8. Safe Mode


## 9. cli.py 에 옵션 통합