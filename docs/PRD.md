# PRD — GWS DeepAgent Workspace

## 1) 문제 정의
Google Workspace 중심으로 일하는 1인/소형 법인은 업무 도구가 분산되어 반복 작업(일정/문서/보고/커밋/정산)에 시간이 많이 든다.

## 2) 대상 사용자
- 1인 대표/프리랜서
- 2~30인 규모 소형 법인
- Google Workspace + GitHub 중심 팀

## 3) 제품 가치
- 자연어 지시로 멀티 도구 실행
- AI 작업 로그 자동 문서화 (일일/주간 R&D 보고)
- 팀 협업(채팅+문서+프로젝트 관리) 단일 허브
- 향후 세금계산서 자동 발행(Barobill)

## 4) 기능 요구사항
### 4.1 Workspace Agent Hub
- Calendar/Tasks/Drive/Docs/Sheets/Slides/Meet 액션 실행
- 사용자 계정 연결 상태 확인

### 4.2 GitHub Work Journal
- Webhook 기반 이벤트 수집
- 기간별 활동 요약

### 4.3 보고 자동화
- 일일/주간 보고서 생성
- 문서베이스 자동 저장

### 4.4 Collaboration Hub
- 채널 생성/메시지 기록
- 프로젝트 문서 CRUD + 검색

### 4.5 Billing Automation (준비)
- 세금계산서 Draft 생성
- 승인 후 Issue 상태 전환

### 4.6 DeepAgent Natural Language Execution
- `/agent/execute` 입력 지시문을 실행 단계로 분해
- 결과를 구조화된 출력으로 반환

## 5) 비기능 요구사항
- 감사 가능성(실행 기록)
- 권한 안전성(HITL 확장)
- 커넥터 확장성

## 6) 초기 성공 지표
- 보고서 작성 시간 70% 절감
- 반복 업무 자동화율 40%+
- 문서화 누락률 10% 이하
