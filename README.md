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

##