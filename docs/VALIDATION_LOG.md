# VALIDATION LOG

## 2026-02-26 Local
- 명령:
  - `python3 -m compileall apps/api/app apps/api/tests`
  - TestClient 기반 inline smoke script
- 결과:
  - `LOCAL_P0_SMOKE_OK`
  - `LOCAL_OAUTH_GITHUB_UPDATES_OK`
- 검증 범위:
  - Workspace/RBAC 생성·멤버·권한
  - Google OAuth connect/callback (mock fallback)
  - GitHub App install-url/callback/repo-link/webhook/event 조회
  - HITL 승인 후 Agent 실행/스트리밍/로그
  - HITL 승인 후 Invoice issue

## 2026-02-26 Server (192.168.50.250)
- 배포:
  - `/tmp/gws-deepagent-workspace-p0.tgz` 생성 후 `scp -O`로 서버 전송
  - `~/deployments/gws-deepagent-workspace`에 압축 해제
- 선행 조치:
  - 서버에 `python3-pip`, `python3.12-venv` 설치
- 검증 명령:
  - 원격 venv 생성 후 `pip install fastapi uvicorn httpx`
  - TestClient 기반 inline smoke script 실행
- 결과:
  - `SERVER250_P0_SMOKE_OK`
- 검증 포인트:
  - RBAC + OAuth + HITL + GitHub App 연결 + Agent 실행로그 + Billing issue 승인 플로우

## 2026-02-26 Server (192.168.50.250) — OAuth/GitHub 실연동 경로 검증
- 배포: `~/deployments/gws-deepagent-workspace` 최신 코드 반영
- 실행:
  - 계약 API 전체 회귀: `SERVER250_API_FULL_TEST_OK` (51 calls)
  - 실연동 경로 테스트: `SERVER250_REAL_OAUTH_GITHUB_PATH_TEST_OK`
- 실연동 경로 검증 내용:
  - `ALLOW_MOCK_AUTH=false` + 실제 `GOOGLE_CLIENT_ID/SECRET` 주입
  - `/oauth/google/connect`에서 실제 client_id 반영 확인
  - `/oauth/google/callback` 호출 시 Google 토큰 엔드포인트 실호출(잘못된 code로 400 확인)
  - GitHub App installation token 경로(`/github/app/installations/{id}/repos`) 실호출 루트 확인(가짜 app id로 400 확인)
