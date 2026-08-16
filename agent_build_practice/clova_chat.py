#!/usr/bin/env python3
"""터미널에서 CLOVA Studio HyperCLOVA X와 대화하는 간단한 CLI."""

from __future__ import annotations

import argparse
import getpass
import sys
from dataclasses import dataclass, field
from typing import Any


BASE_URL = "https://clovastudio.stream.ntruss.com/v1/openai"
DEFAULT_MODEL = "HCX-005"
DEFAULT_SYSTEM_PROMPT = (
    "당신은 정확하고 친절한 한국어 AI 어시스턴트입니다. "
    "확실하지 않은 사실은 추측하지 말고 불확실하다고 밝히세요."
)


def create_client(api_key: str) -> Any:
    """OpenAI 호환 SDK로 CLOVA Studio 클라이언트를 생성합니다."""
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "openai 패키지가 없습니다. 가상환경에서 `python -m pip install openai`를 실행하세요."
        ) from exc
    return OpenAI(api_key=api_key, base_url=BASE_URL)


@dataclass
class ClovaTerminalChat:
    client: Any
    model: str = DEFAULT_MODEL
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    max_tokens: int = 1000
    history: list[dict[str, str]] = field(default_factory=list)

    def clear(self) -> None:
        """현재 터미널 세션의 대화 기록을 지웁니다."""
        self.history.clear()

    def ask(self, user_text: str) -> str:
        """기존 대화 기록과 새 질문을 보내고 답변을 기록합니다."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.history,
            {"role": "user", "content": user_text},
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=self.max_tokens,
        )
        answer = response.choices[0].message.content or ""
        self.history.extend(
            [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": answer},
            ]
        )
        return answer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HyperCLOVA X 터미널 대화")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"모델명 (기본값: {DEFAULT_MODEL})")
    parser.add_argument("--max-tokens", type=int, default=1000, help="답변 최대 토큰 수")
    parser.add_argument("--system", default=DEFAULT_SYSTEM_PROMPT, help="시스템 프롬프트")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = getpass.getpass("CLOVA Studio API Key (화면에 표시되지 않음): ").strip()
    if not api_key:
        print("API 키가 입력되지 않았습니다.", file=sys.stderr)
        return 2

    try:
        chat = ClovaTerminalChat(
            client=create_client(api_key),
            model=args.model,
            system_prompt=args.system,
            max_tokens=max(16, args.max_tokens),
        )
    except RuntimeError as exc:
        print(f"설정 오류: {exc}", file=sys.stderr)
        return 2
    finally:
        # 키는 클라이언트 생성 뒤 일반 변수에서 제거합니다.
        api_key = ""

    print(f"\nHyperCLOVA X 대화를 시작합니다. 모델: {args.model}")
    print("명령어: /clear 대화 초기화, /help 도움말, /exit 종료\n")

    while True:
        try:
            user_text = input("나 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n대화를 종료합니다.")
            return 0

        if not user_text:
            continue
        if user_text.lower() in {"/exit", "/quit", "종료"}:
            print("대화를 종료합니다.")
            return 0
        if user_text.lower() == "/clear":
            chat.clear()
            print("대화 기록을 초기화했습니다.\n")
            continue
        if user_text.lower() == "/help":
            print("/clear: 대화 기록 초기화 | /exit: 종료\n")
            continue

        try:
            answer = chat.ask(user_text)
            print(f"클로바X > {answer}\n")
        except Exception as exc:
            # 인증·요청 오류를 보여주되 API 키나 전체 요청 본문은 출력하지 않습니다.
            print(f"요청 실패: {type(exc).__name__}: {str(exc)[:500]}\n", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
