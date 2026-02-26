# VALIDATION LOG

## 2026-02-26 Local
- 명령:
  - `python3 -m compileall apps/api/app apps/api/tests`
  - inline smoke script (TestClient 기반 end-to-end)
- 결과:
  - `LOCAL_P0_SMOKE_OK`
- 검증 범위:
  - Workspace/RBAC 생성·멤버·권한
  - Google OAuth connect/callback (mock fallback)
  - GitHub App install-url/callback/repo-link/webhook/event 조회
  - HITL 승인 후 Agent 실행/스트리밍/로그
  - HITL 승인 후 Invoice issue

## 2026-02-26 Server(192.168.50.250)
- 예정: 코드 동기화 후 원격 실행 검증
