from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


class GeminiAPIError(RuntimeError):
    """Gemini API 호출 중 발생한 오류."""


DEFAULT_MODEL = "gemini-3.5-flash-lite"
DEFAULT_TEMPERATURE = 1.0
DEFAULT_MAX_TOKENS = 1000


def get_api_key() -> str:
    """환경변수에서 Gemini API Key를 가져온다."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise GeminiAPIError(
            "GEMINI_API_KEY 환경변수가 설정되지 않았습니다.\n"
            '예: export GEMINI_API_KEY="YOUR_KEY"'
        )

    return api_key


def generate_text(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    """Gemini REST API를 호출하고 생성된 텍스트를 반환한다."""
    api_key = get_api_key()

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{model}:generateContent"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt,
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }

    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw_data = response.read().decode("utf-8")

    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")

        try:
            error_data = json.loads(error_body)
            error_message = (
                error_data.get("error", {}).get("message")
                or error_body
            )
        except json.JSONDecodeError:
            error_message = error_body

        raise GeminiAPIError(
            f"Gemini API 요청 실패 ({exc.code}): {error_message}"
        ) from exc

    except urllib.error.URLError as exc:
        raise GeminiAPIError(
            f"Gemini API 네트워크 오류: {exc.reason}"
        ) from exc

    except TimeoutError as exc:
        raise GeminiAPIError(
            "Gemini API 요청 시간이 초과되었습니다."
        ) from exc

    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError as exc:
        raise GeminiAPIError(
            "Gemini API 응답을 JSON으로 해석하지 못했습니다."
        ) from exc

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise GeminiAPIError(
            "Gemini API 응답에서 생성된 텍스트를 찾을 수 없습니다."
        ) from exc

    if not text.strip():
        raise GeminiAPIError(
            "Gemini API가 빈 응답을 반환했습니다."
        )

    return text.strip()