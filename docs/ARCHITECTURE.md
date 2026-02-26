# Architecture — GWS DeepAgent Workspace

## P0 아키텍처
1. FastAPI Router Layer
   - workspaces, oauth, approvals, agent, github, docs, chat, reports, billing
2. Service Layer
   - workspace_service (RBAC)
   - oauth_service (Google token exchange/refresh)
   - approval_service (HITL)
   - deepagents_runtime (orchestrator + streaming)
   - github_integration/github_service
3. Data Layer
   - SQLite (`apps/api/data/app.db`)
   - 핵심 테이블: users/workspaces/workspace_members, approvals, agent_execution_logs

## P0 핵심 설계 포인트
- 멀티테넌시: workspace_id 기반 분리
- RBAC: owner/admin/member/viewer
- 승인 게이트: `agent_execute`, `invoice_issue`
- OAuth: 실교환 지원 + `ALLOW_MOCK_AUTH=true` 개발 fallback
- 실행 추적: 에이전트 실행별 로그 저장

## 다음 단계
- P1: 실 Google Workspace 액션 API 연결(현재 execute는 contract-ready)
- P1: GitHub App installation token 기반 실 sync
- P1: DeepAgents SDK 직접 연결 + subagent stream
