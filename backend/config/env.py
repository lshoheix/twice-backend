"""
PM-LSH-1: 환경 변수 로딩을 위한 config/env 초기화.
애플리케이션 시작 시 .env 파일이 1회 로드되며, 로딩 책임은 config 패키지에만 위치한다.
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def load_env() -> None:
    """프로젝트 루트의 .env 파일을 1회 로드한다. Service/Controller에서는 호출하지 않는다."""
    # main.py가 있는 디렉터리 = backend 루트
    root = Path(__file__).resolve().parent.parent
    env_path = root / ".env"

    if not env_path.exists():
        print(
            f"[config] .env 파일을 찾을 수 없습니다. 다음 경로에 .env를 두세요: {env_path}",
            file=sys.stderr,
        )
    loaded = load_dotenv(dotenv_path=env_path, override=False)
    if loaded:
        print(f"[config] .env 로드됨: {env_path}")
    elif env_path.exists():
        print(f"[config] .env 파일은 있으나 비어있거나 읽기 실패: {env_path}", file=sys.stderr)

    # Kakao 설정 확인 (디버깅용)
    if not os.environ.get("KAKAO_CLIENT_ID") or not os.environ.get("KAKAO_REDIRECT_URI"):
        print(
            "[config] KAKAO_CLIENT_ID 또는 KAKAO_REDIRECT_URI가 없습니다. .env에 설정하세요.",
            file=sys.stderr,
        )
