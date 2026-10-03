* git_service.py

    - `class GitError(RuntimeError)` : 예외 클래스
    - `class GitChanges` : 변경 사항 데이터 구조 정의
    - `run_git_command()` : Git 명령어 실행 Wrapper
    - `get_repo_root()` : 현재 디렉토리가 속한 Git 최상위 저장소 경로
    - `ensure_project_root()` : 실행 위치 검증
    - `collect_git_changes()` : Git 변경 사항 수집 (status, diff, branch)

* gemini_service.py

    - `class GeminiAPIError(RuntimeError)` :
    - `get_api_key()` : 인증 및 환경변수 검증
    - `generate_text()` : Gemini REST API 호출 및 텍스트 생성

* cli.py

    - `build_parser()` : CLI 명령어 파서(ArgumentParser) 구성
    - `print_git_info()` : 콘솔 출력용 유틸리티 함수
    - `run_commit()` : commit 서브 커맨드 실행 로직
    - `run_pr()` : pr 서브 커맨드 실행 로직
    - `main()` : CLI 메인 엔트리포인트 및 Global Error 핸들링

* prompt.py

    - `build_commit_prompt()` : 커밋 메시지용 프롬프트
    - `build_pr_prompt()` : PR 제목 + 본문 초안 생성을 위한 프롬프트

* formatter.py

    - `clean_text()` : AI 응답 텍스트 전처리
    - `shorten_title()` : 제목 길이기반 자르기
    - `extract_changed_files()` : 변경 파일 목록 추출
    - `normalize_commit()` : 커밋 메시지 정형화
    - `extract_pr_sections()` : PR 본문 섹션 파싱
    - `ensure_bullets()` : 불릿 포인트 형식 보장 및 기본값 적용
    - `normalize_pr()` : PR 제목 및 본문 정형화
    - `validate_commit()` : 커밋 메시지 검증
    - `validate_pr()` : PR 유효성 검증

* security.py

    - `mask_sensitive_data()` : 민감 정보 마스킹
    - `limit_diff()` : Diff 글자 수 제한 (Safe Mode 전용)
    - `prepare_context()` : AI 전달용 Git 컨텍스트 전처리