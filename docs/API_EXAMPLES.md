# API Examples

## 1) Google 연결
```bash
curl -s http://localhost:8090/oauth/google/connect

curl -s -X POST http://localhost:8090/oauth/google/callback \
  -H 'Content-Type: application/json' \
  -d '{"code":"demo-code","state":"local","user_email":"ceo@example.com"}'
```

## 2) GitHub Webhook 이벤트 저장
```bash
curl -s -X POST http://localhost:8090/github/webhook \
  -H 'Content-Type: application/json' \
  -H 'x-github-event: push' \
  -d '{"repository":{"full_name":"BAEM1N/gws-deepagent-workspace"},"sender":{"login":"baem1n"}}'
```

## 3) 주간 보고 생성
```bash
curl -s -X POST http://localhost:8090/reports/weekly \
  -H 'Content-Type: application/json' \
  -d '{"period_start":"2026-02-20","period_end":"2026-02-26"}'
```

## 4) 자연어 에이전트 실행
```bash
curl -s -X POST http://localhost:8090/agent/execute \
  -H 'Content-Type: application/json' \
  -d '{
    "user_email":"ceo@example.com",
    "instruction":"이번 주 커밋 요약해 주간 보고 만들고 문서 저장해",
    "context":{"title":"주간 R&D 보고"}
  }'
```
