# GWS DeepAgent Workspace

Google Workspace 기반 1인/소형 법인을 위한 **DeepAgent SaaS 백엔드**.

## 현재 상태
- P0 구현 완료 (RBAC/OAuth/HITL/GitHub App 연결/API 스트리밍/실행로그)
- 경로: `~/Dev/company/gws-deepagent-workspace`

## 핵심 기능
- **Workspace + RBAC**: owner/admin/member/viewer
- **Google OAuth**: 실제 토큰 교환/갱신 준비 + mock fallback
- **HITL 승인**: Agent 실행, Invoice 발행 승인 게이트
- **GitHub App**: 설치 URL, callback, repo link, webhook 저널
- **Agent 실행**: 일반 실행 + SSE 스트리밍 + 실행 로그
- **Docs/Chat/Reports/Billing**: workspace 단위 데이터

## 실행
```bash
cd ~/Dev/company/gws-deepagent-workspace
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --app-dir apps/api --reload --port 8090
```

## 주요 API
- Workspace/RBAC: `/workspaces`, `/workspaces/{id}/members`, `/workspaces/{id}/permissions/me`
- OAuth: `/oauth/google/connect`, `/oauth/google/callback`, `/oauth/google/account/{email}`
- Approvals: `/approvals/inbox`, `/approvals/requests/{id}/approve|reject`
- Agent: `/agent/execute`, `/agent/execute/stream`, `/agent/logs`
- GitHub: `/github/app/install-url`, `/github/app/callback`, `/github/repos/link`, `/github/webhook`
- Billing: `/billing/invoices`, `/billing/invoices/{id}/issue`

## 문서
- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/API_EXAMPLES.md`
- `docs/CHANGELOG.md`
- `docs/VALIDATION_LOG.md`
