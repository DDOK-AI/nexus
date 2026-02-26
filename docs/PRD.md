# PRD — GWS DeepAgent Workspace

## 목표
Google Workspace + GitHub 기반 소형 조직 업무를 자연어 에이전트로 통합 자동화한다.

## P0 범위 (완료)
1. Workspace 생성 및 RBAC(owner/admin/member/viewer)
2. Google OAuth 연결 및 토큰 갱신
3. Agent/Invoice 실행 전 승인(HITL)
4. GitHub App 설치 연결 및 레포 링크
5. Agent 실행 스트리밍/로그 저장

## 핵심 요구사항
- 권한 안전성: role + approval gate
- 감사 가능성: 실행로그/승인이력 저장
- 확장성: 실제 Google/GitHub/Barobill API로 교체 가능

## 비포함(P1+)
- Taskboard/위키 링크그래프/유틸리티툴
- 문서 임베딩 검색(RAG)
- 실시간 웹소켓 채팅
