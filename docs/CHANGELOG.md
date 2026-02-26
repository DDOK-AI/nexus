# CHANGELOG

## 2026-02-26 — P0 구현

### Added
- Workspace/RBAC API (`/workspaces/*`) 및 멤버 역할 관리
- Google OAuth real-ready (`/oauth/google/connect`, `/oauth/google/callback`)
- HITL 승인 API (`/approvals/*`)
- Agent 실행/스트리밍/로그 API (`/agent/execute`, `/agent/execute/stream`, `/agent/logs`)
- GitHub App 연결 API (`/github/app/install-url`, `/github/app/callback`, `/github/repos/link`)
- 실행 로그/승인/RBAC 관련 DB 스키마

### Changed
- 기존 workspace execute 경로를 `/workspaces/{workspace_id}/execute`로 정렬
- docs/chat/reports/billing를 workspace_id 기반 멀티테넌시로 전환
- billing issue를 승인 게이트 기반으로 전환

### Notes
- `ALLOW_MOCK_AUTH=true` 시 Google OAuth mock fallback 동작
- GitHub repo 실조회는 `GITHUB_APP_TOKEN` 설정 시 활성화
- 192.168.50.250 서버에서 P0 스모크 검증 완료 (`SERVER250_P0_SMOKE_OK`)

## 2026-02-26 — OAuth/GitHub 실연동 강화

### Added
- Google OAuth redirect GET callback (`GET /oauth/google/callback`)
- Google OAuth 계정 disconnect API (`DELETE /oauth/google/account/{user_email}`)
- GitHub App redirect GET callback (`GET /github/app/callback`)
- GitHub 설치별 repo 조회 API (`GET /github/app/installations/{installation_id}/repos`)

### Changed
- Google OAuth callback 시 userinfo(email) 검증 추가
- Workspace execute에서 mock 토큰이 아니면 Google Calendar/Drive 실 API 호출
- GitHub 연동에서 `GITHUB_APP_ID + GITHUB_APP_PRIVATE_KEY`를 통한 installation token 발급 지원

### Validation
- 192.168.50.250에서 회귀 API 테스트 성공 (`SERVER250_API_FULL_TEST_OK`, 51 calls)
- 192.168.50.250에서 OAuth/GitHub 실연동 경로 테스트 성공 (`SERVER250_REAL_OAUTH_GITHUB_PATH_TEST_OK`)

## 2026-02-26 — 운영 템플릿/체크리스트 추가

### Added
- 운영용 환경변수 템플릿 `.env.production.template`
- 실연동 필수 환경변수 점검 스크립트 `scripts/check_real_integration_env.py`
- 250 서버 기준 실 OAuth/GitHub E2E 문서 `docs/E2E_REAL_OAUTH_GITHUB_CHECKLIST.md`

### Changed
- README에 운영 준비 절차(`cp .env.production.template .env` + env 점검) 반영

## 2026-02-26 — 운영 배포 경로(250 + Traefik) 연결

### Added
- 250 서버 user systemd 서비스 `gws-deepagent-workspace.service`로 API 상시 실행(포트 `18090`)
- Traefik 동적 라우트 `nexus.ddok.ai -> http://192.168.50.250:18090`

### Validation
- 내부 헬스체크: `http://127.0.0.1:18090/health` → `{\"ok\":true}`
- 외부 도메인 헬스체크: `https://nexus.ddok.ai/health` → `200`, `{\"ok\":true}`

## 2026-02-26 — Google OAuth 우선 실연동 전환

### Changed
- 250 서버 `.env`에 Google OAuth 실값 반영
- Google Redirect URI를 `https://nexus.ddok.ai/oauth/google/callback`으로 고정
- `ALLOW_MOCK_AUTH=false`로 전환하여 mock fallback 비활성화

### Validation
- `POST /oauth/google/connect` 응답 auth_url에서 실제 `client_id`/redirect 확인
- `GET /oauth/google/callback?code=bogus&state=...` 호출 시 Google 토큰 엔드포인트 실호출 후 `invalid_grant`(400) 확인
- 도메인 경유(`https://nexus.ddok.ai`)에서도 동일 connect 경로 정상 확인
