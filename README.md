# 내가 고친 코드 설명을 AI가 대신 써주는 도우미 만들기

## 프로젝트 개요

Git의 변경 사항을 수집하고 Gemini REST API를 이용해
커밋 메시지와 Pull Request 초안을 자동으로 생성하는
터미널 기반 CLI 도구입니다.

## 개발 환경

- Python 3.12.3 (Python 표준 라이브러리만 사용)
- git version 2.43.0
- Gemini API Key

## 프로젝트 구조

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

## 파일 역할

* main.py
    - 프로그램 시작점
* app/cli.py
    - commit, pr CLI 명령 처리
* app/git_service.py
    - Git status, diff, 현재 브랜치 수집
* app/gemini_service.py
    - Gemini REST API 호출
    - API Key 확인
    - HTTP 오류 처리
* app/prompt.py
    - Commit / PR 프롬프트 생성
* app/formatter.py
    - Commit / PR 결과 검증 및 후처리
* app/security.py
    - Safe Mode
    - 민감정보 마스킹
    - diff 파일/줄 수 제한

## 주요 기능

- `git status` 수집
- `git diff` 수집
- 현재 Git 브랜치 확인
- Gemini REST API 연동
- Commit 메시지 자동 생성
- PR 제목/본문 자동 생성
- Commit/PR 결과 형식 검증 및 후처리
- Safe Mode를 통한 민감정보 마스킹
- diff 전송 범위 제한
- 모델 및 생성 파라미터 CLI 옵션 제공

## 사용방법

* AI API Key 환경변수로 등록 (1회용)

```bash
export GEMINI_API_KEY="본인의_API_KEY"
```

* 도움말 출력

```bash
python3 main.py --help
```

```bash
python3 main.py commit --help
```

```bash
python3 main.py pr --help
```

* `commit` 메세지 생성 / `pr` 제목 + 본문 생성

```bash
python3 main.py commit
```

```bash
python3 main.py pr
```

* Gemini AI 모델 변경 (default: gemini-3.5-flash-lite)

```bash
python3 main.py commit --model gemini-3.5-flash-lite
```

* `--temperature` 수치 변경 (default:)(범위: 0.0~2.0)

```bash
python3 main.py commit --temperature 0.5
```

* `--max-tokens` 수치 변경 (default: )

```bash
python3 main.py commit --max-tokens 500
```

* `safe mode`

```
Safe Mode 정책:

- API Key 형태의 문자열 마스킹
- token, secret, password 형태 값 마스킹
- 이메일 주소 마스킹
- 최대 10개 diff 파일만 전달
- 최대 200줄만 전달
```

```bash
python3 main.py commit --safe-mode
```

```bash
python3 main.py pr --safe-mode
```