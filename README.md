# GWS DeepAgent Workspace

Google Workspace를 사용하는 1인/소형 법인을 위한 **DeepAgents 기반 업무 자동화 SaaS** 프로젝트입니다.

- 유형: 제품(Product)
- 경로: `~/Dev/company/gws-deepagent-workspace`
- 생성일: 2026-02-25

## MVP 구현 범위 (v0.1)
- Google OAuth 연결 흐름(연결 URL/콜백/연결 상태)
- Workspace 액션 실행 API (Calendar/Tasks/Drive/Docs/Sheets/Slides/Meet)
- GitHub Webhook 수집 + 이벤트 저널 저장
- 일일/주간 R&D 보고서 자동 생성 및 문서베이스 저장
- 프로젝트 문서베이스 CRUD + 검색
- 내부 팀 채팅(채널/메시지)
- 바로빌 연계 준비용 세금계산서 Draft/Issue 워크플로
- DeepAgent Orchestrator 자연어 실행 엔드포인트

## 디렉터리
```
apps/
  api/
    app/
      api/routes/
      core/
      db/
      schemas/
      services/
    tests/
    data/
docs/
```

## 실행
```bash
cd ~/Dev/company/gws-deepagent-workspace
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --app-dir apps/api --reload --port 8090
```

> DeepAgents SDK까지 설치하려면
```bash
pip install -e '.[deepagents]'
```

## 주요 API
- `GET /health`
- `GET /oauth/google/connect`
- `POST /oauth/google/callback`
- `POST /workspace/execute`
- `POST /github/webhook`
- `POST /reports/daily`, `POST /reports/weekly`
- `POST /docs`, `GET /docs/search/query`
- `POST /chat/channels`, `POST /chat/channels/{id}/messages`
- `POST /billing/invoices`, `POST /billing/invoices/{id}/issue`
- `POST /agent/execute`

## 문서
- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
