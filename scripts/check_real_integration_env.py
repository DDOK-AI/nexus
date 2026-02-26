from __future__ import annotations

import os
import sys

REQUIRED = [
    "APP_SECRET",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REDIRECT_URI",
    "ALLOW_MOCK_AUTH",
    "GITHUB_APP_ID",
    "GITHUB_APP_SLUG",
    "GITHUB_APP_PRIVATE_KEY",
    "GITHUB_WEBHOOK_SECRET",
]


def main() -> int:
    missing: list[str] = []
    for key in REQUIRED:
        if not os.getenv(key, "").strip():
            missing.append(key)

    allow_mock = os.getenv("ALLOW_MOCK_AUTH", "true").strip().lower()
    if allow_mock != "false":
        missing.append("ALLOW_MOCK_AUTH=false (현재 real mode 아님)")

    private_key = os.getenv("GITHUB_APP_PRIVATE_KEY", "")
    if private_key:
        if "BEGIN" not in private_key:
            print("[WARN] GITHUB_APP_PRIVATE_KEY 형식 점검 필요 (PEM 헤더 없음)")

    if missing:
        print("[FAIL] 실연동 필수 환경변수 누락/설정 오류")
        for item in missing:
            print(" -", item)
        return 1

    print("[OK] 실연동 필수 환경변수 점검 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
