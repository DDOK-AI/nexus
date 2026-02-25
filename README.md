# GWS DeepAgent Workspace

Google Workspace를 사용하는 1인/소형 법인을 위한 **DeepAgents 기반 업무 자동화 SaaS** 프로젝트입니다.

## 프로젝트 유형
- 유형: 제품(Product)
- 경로: `~/Dev/company/gws-deepagent-workspace`
- 생성일: 2026-02-25

## 핵심 목표
- Google Calendar/Tasks/Drive/Docs/Sheets/Slides/Meet 통합 에이전트
- GitHub 연동으로 AI 코딩 작업(Claude Code, Codex, OpenCode) 자동 기록/커밋/리포트화
- 일일 R&D 보고서 / 주간 보고 자동 생성
- 향후 바로빌 API 연계로 세금계산서 자동 발행
- 내부 팀 채팅 + Notion/Confluence/Jira 통합형 프로젝트/문서 베이스
- 위 지식베이스에 DeepAgents가 직접 접근해 자연어 지시 실행

## 초기 구조
```
apps/
  api/
    app/
      api/routes/
      core/
      services/
    tests/
docs/
```

## 문서
- `docs/PRD.md` : 제품 요구사항
- `docs/ARCHITECTURE.md` : 시스템 아키텍처
- `docs/ROADMAP.md` : 단계별 구현 계획

## 로컬 실행(스캐폴드)
```bash
cd ~/Dev/company/gws-deepagent-workspace
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --app-dir apps/api --reload --port 8090
```

## 다음 우선 작업
1. Google OAuth 및 Workspace API 인증 레이어 구축
2. DeepAgents 런타임 + 툴 권한 정책(HITL) 연결
3. GitHub App 설치형 연동(커밋/PR/이슈/릴리즈 로그)
4. 보고서 생성 파이프라인(일/주간)
5. 협업 허브(채팅 + 문서/업무) MVP
