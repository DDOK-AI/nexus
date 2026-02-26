# VALIDATION LOG

## 2026-02-26 Local
- 명령:
  - `python3 -m compileall apps/api/app apps/api/tests`
  - TestClient 기반 inline smoke script
- 결과:
  - `LOCAL_P0_SMOKE_OK`
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
