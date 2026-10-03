# 내가 고친 코드 설명을 AI가 대신 써주는 도우미 만들기

## 프로젝트 개요

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

* `commit` 메세지 / `pr` 제목 + 본문 생성

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

```bash
python3 main.py commit --safe-mode
```

```bash
python3 main.py pr --safe-mode
```