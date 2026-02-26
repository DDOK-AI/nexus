# API Examples (OAuth/GitHub 실연동 우선)

## 0) Workspace 생성
```bash
curl -s -X POST http://localhost:8090/workspaces \
  -H 'Content-Type: application/json' \
  -d '{"actor_email":"owner@example.com","name":"BaeumAI"}'
```

## 1) Google OAuth 연결 URL 발급
```bash
curl -s -X POST http://localhost:8090/oauth/google/connect \
  -H 'Content-Type: application/json' \
  -d '{"workspace_id":1,"user_email":"owner@example.com"}'
```

## 2) Google OAuth 콜백 처리
```bash
# 프론트/브라우저 redirect 시 GET /oauth/google/callback?code=...&state=...
# 서버 내부 처리나 테스트 시 POST 사용 가능
curl -s -X POST http://localhost:8090/oauth/google/callback \
  -H 'Content-Type: application/json' \
  -d '{"code":"oauth-code","state":"signed-state"}'
```

## 3) GitHub App 설치 URL 생성
```bash
curl -s -X POST http://localhost:8090/github/app/install-url \
  -H 'Content-Type: application/json' \
  -d '{"workspace_id":1,"actor_email":"owner@example.com"}'
```

## 4) GitHub 설치 콜백 저장
```bash
curl -s -X POST http://localhost:8090/github/app/callback \
  -H 'Content-Type: application/json' \
  -d '{"state":"signed-state","installation_id":12345,"account_login":"BAEM1N"}'
```

## 5) 설치 리포 조회 (실토큰 설정 시)
```bash
curl -s "http://localhost:8090/github/app/installations/12345/repos?workspace_id=1&actor_email=owner@example.com"
```

## 6) Agent 실행(승인 필요)
```bash
curl -s -X POST http://localhost:8090/agent/execute \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_id":1,
    "actor_email":"owner@example.com",
    "user_email":"owner@example.com",
    "instruction":"이번 주 커밋 요약해서 주간보고 만들어줘",
    "context":{}
  }'
```
