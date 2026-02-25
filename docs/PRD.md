# PRD — GWS DeepAgent Workspace

## 1) 문제 정의
Google Workspace 중심으로 일하는 1인/소형 법인은 업무 도구가 분산되어 있어 반복 작업(일정/문서/보고/커밋/정산)이 비효율적이다.

## 2) 대상 사용자
- 1인 대표/프리랜서
- 2~30인 규모 소형 법인
- Google Workspace + GitHub 기반 지식 노동 팀

## 3) 핵심 가치
- 자연어 지시 한 번으로 여러 업무 도구를 연결 실행
- AI 개발 로그를 자동 문서화하여 R&D 가시성 확보
- 추후 전자세금계산서 자동화로 운영/회계 부담 감소

## 4) 핵심 기능(MVP)
1. Workspace Agent Hub
   - Calendar/Tasks/Drive/Docs/Sheets/Slides/Meet 액션 실행
2. GitHub Work Journal
   - 커밋/브랜치/PR 이벤트를 일일/주간 보고서로 변환
3. Team Collaboration
   - 내부 채팅, 프로젝트 보드, 문서 위키 통합 UI
4. Agent-accessible Knowledge Base
   - 에이전트가 프로젝트 문서/결정 로그를 읽고 작업 실행

## 5) 비기능 요구사항
- 감사 가능성: 누가 어떤 자연어 지시로 어떤 액션을 실행했는지 추적
- 권한 안전성: 민감 액션(HITL 승인)
- 확장성: 바로빌/회계 SaaS 등 외부 커넥터 확장 가능

## 6) 성공 지표(초기)
- 반복 업무 자동화 비율 40%+
- 보고서 작성 시간 70% 절감
- 프로젝트 문서화 누락률 10% 이하
