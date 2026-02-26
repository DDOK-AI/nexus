# API Examples (P0)

## 0) Workspace 생성
```bash
curl -s -X POST http://localhost:8090/workspaces \
  -H 'Content-Type: application/json' \
  -d '{"actor_email":"owner@example.com","name":"BaeumAI"}'
```

## 1) Google OAuth 연결 URL
```bash
curl -s -X POST http://localhost:8090/oauth/google/connect \
  -H 'Content-Type: application/json' \
  -d '{"workspace_id":1,"user_email":"owner@example.com"}'
```

## 2) 승인 요청 조회/승인
```bash
curl -s "http://localhost:8090/approvals/inbox?workspace_id=1&actor_email=owner@example.com"

curl -s -X POST http://localhost:8090/approvals/requests/1/approve \
  -H 'Content-Type: application/json' \
  -d '{"workspace_id":1,"actor_email":"owner@example.com","note":"ok"}'
```

## 3) Agent 실행 (승인 요구)
```bash
curl -s -X POST http://localhost:8090/agent/execute \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_id":1,
    "actor_email":"owner@example.com",
    "user_email":"owner@example.com",
    "instruction":"이번 주 커밋 요약해서 주간 보고 만들어줘",
    "context":{}
  }'
```

## 4) GitHub App 설치 URL 생성
```bash
curl -s -X POST http://localhost:8090/github/app/install-url \
  -H 'Content-Type: application/json' \
  -d '{"workspace_id":1,"actor_email":"owner@example.com"}'
```

## 5) Workspace 실행
```bash
curl -s -X POST http://localhost:8090/workspaces/1/execute \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_id":1,
    "actor_email":"owner@example.com",
    "user_email":"owner@example.com",
    "service":"calendar",
    "action":"create",
    "payload":{"title":"주간 리뷰"}
  }'
```
