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

## 2026-02-26 Server (192.168.50.250) — 운영 템플릿/체크리스트 검증
- 반영 파일:
  - `.env.production.template`
  - `scripts/check_real_integration_env.py`
  - `docs/E2E_REAL_OAUTH_GITHUB_CHECKLIST.md`
  - `README.md`, `docs/CHANGELOG.md`
- 검증 명령:
  - `python3 -m py_compile scripts/check_real_integration_env.py`
  - (실패 경로) env 미주입 상태로 `python3 scripts/check_real_integration_env.py`
  - (성공 경로) 필수 env 주입 + `ALLOW_MOCK_AUTH=false`로 동일 스크립트 실행
- 결과:
  - `SERVER250_ENV_CHECK_FAIL_PATH_OK`
  - `SERVER250_ENV_CHECK_PASS_PATH_OK`
  - `SERVER250_TEMPLATE_SYNC_OK`

## 2026-02-26 Server (192.168.50.250) + Traefik (192.168.50.253) — nexus.ddok.ai 연결
- 250 서버 조치:
  - `~/.config/systemd/user/gws-deepagent-workspace.service` 생성/enable
  - uvicorn 상시 실행: `0.0.0.0:18090`
- Traefik 조치:
  - `~/traefik/dynamic/nexus-ddok-ai.yaml` 추가
  - router: `Host(nexus.ddok.ai)` → service `http://192.168.50.250:18090`
- 검증:
  - 250 로컬: `curl http://127.0.0.1:18090/health` → `{"ok":true}`
  - Traefik 노드(253)에서 백엔드 연결: `curl http://192.168.50.250:18090/health` → `{"ok":true}`
  - 외부 도메인: `curl https://nexus.ddok.ai/health` → HTTP `200` + `{"ok":true}`

## 2026-02-26 Server (192.168.50.250) — Google OAuth 우선 실연동 검증
- 설정 반영:
  - source: `/Volumes/BAEM1N/260222/startup-google-base/.env`의 Google client 값
  - target: `~/deployments/gws-deepagent-workspace/.env`
  - `GOOGLE_REDIRECT_URI=https://nexus.ddok.ai/oauth/google/callback`
  - `ALLOW_MOCK_AUTH=false`
- 서비스 상태:
  - `systemctl --user restart gws-deepagent-workspace.service` 후 `active`
- API 검증:
  - `GOOGLE_CONNECT_CHECK {"client_id_set": true, "redirect_uri_ok": true, "scope_has_calendar": true}`
  - `GOOGLE_CALLBACK_BAD_STATUS 400`
  - `GOOGLE_CALLBACK_BAD_TEXT ... \"error\": \"invalid_grant\" ...`
  - `SERVER250_GOOGLE_REAL_PATH_TEST_DONE`
  - `NEXUS_GOOGLE_CONNECT_OK` (도메인 경유 connect 확인)
