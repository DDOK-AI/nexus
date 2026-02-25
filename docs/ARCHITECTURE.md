# Architecture — GWS DeepAgent Workspace

## 전체 구성
1. Web App (사용자 UI)
2. API Gateway (인증/인가, 라우팅)
3. DeepAgent Orchestrator (플래닝/툴호출/서브에이전트)
4. Connector Layer
   - Google Workspace Connectors
   - GitHub Connector
   - Billing Connector(Barobill, future)
5. Collaboration Core
   - Team Chat
   - Project Management
   - Docs Base (Notion+Confluence+Jira 성격)
6. Storage
   - PostgreSQL (업무 데이터)
   - Vector Store (문서 임베딩 검색)
   - Blob Storage (첨부파일)

## DeepAgents 적용 전략 (SDK 모드)
- 메인 오케스트레이터: 사용자 지시 해석 + 계획 수립
- 서브에이전트 분리:
  - calendar-agent
  - docs-agent
  - github-agent
  - reporting-agent
  - finance-agent(future)
- HITL 정책:
  - 외부 공유, 삭제, 결제/세금 발행 등 고위험 액션은 승인 필요

## 이벤트 흐름 예시
1) 사용자가 자연어로 "이번 주 커밋 요약해서 주간보고 작성" 요청
2) orchestrator가 github-agent + reporting-agent에 작업 위임
3) GitHub 이벤트 수집 → 요약 생성 → docs-base에 보고서 저장
4) 필요 시 슬랙/이메일/채팅방으로 공유

## 보안/권한
- OAuth 2.0 (Google/GitHub)
- 조직/프로젝트 단위 RBAC
- 감사 로그 + 실행 리플레이
