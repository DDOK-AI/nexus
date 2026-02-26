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
