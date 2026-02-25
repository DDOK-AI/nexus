# Architecture — GWS DeepAgent Workspace

## 1) 컴포넌트
1. **API Layer (FastAPI)**
   - OAuth, Workspace, GitHub, Reports, Docs, Chat, Billing, Agent 라우터
2. **DeepAgent Orchestrator (MVP)**
   - 자연어 지시를 모듈 호출 단계로 분해
3. **Domain Services**
   - `oauth_service`, `workspace_service`, `github_service`, `report_service`, `docs_service`, `chat_service`, `billing_service`
4. **Storage**
   - SQLite (`apps/api/data/app.db`) 기반 영속 저장
5. **Future Connectors**
   - 실제 Google API, GitHub App, Barobill API 어댑터

## 2) 데이터 흐름
- GitHub Webhook → `github_events` 저장
- 보고서 생성 요청 → 기간 이벤트 집계 → `reports` 저장 → `docs` 동시 저장
- 자연어 지시 → Orchestrator → Workspace/Docs/Reports/Billing 서비스 호출

## 3) 보안/권한 전략
- OAuth 2.0(Google/GitHub) 토큰 스토리지 분리 예정
- 고위험 액션(삭제/외부공유/발행)은 HITL 승인 게이트 적용 예정
- 감사 로그(지시문, 실행 스텝, 결과) 확장 예정

## 4) DeepAgents 적용 전략
- v0.1: SDK 계약에 맞춘 orchestrator MVP 구현
- v0.2: `deepagents` 실제 런타임 연결 + 서브에이전트 분리
  - calendar-agent
  - docs-agent
  - github-agent
  - reporting-agent
  - finance-agent

## 5) 확장 포인트
- 문서베이스 벡터 검색(Qdrant 등)
- 실시간 채팅(WebSocket)
- 바로빌 실 발행 API + 회계 시스템 연동
