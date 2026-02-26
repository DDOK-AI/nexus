# WORK SUMMARY (2026-02-26)

## 1) 제품/아키텍처
- DeepAgent 기반 Google Workspace SaaS 백엔드 골격 구축
- Workspace 멀티테넌시 + RBAC(owner/admin/member/viewer) 적용
- Docs/Chat/Reports/Billing/Agent 기능을 workspace 스코프로 정렬

## 2) P0 구현
- Google OAuth 연결/콜백/계정 조회/해제
- GitHub App 설치 URL/콜백/리포 링크/웹훅 이벤트 저널
- HITL 승인(Agent 실행, Billing 발행)
- Agent 실행 + 스트리밍 + 실행 로그

## 3) 운영 준비
- 운영용 env 템플릿 추가: `.env.production.template`
- 실연동 env 점검 스크립트: `scripts/check_real_integration_env.py`
- 실연동 E2E 체크리스트: `docs/E2E_REAL_OAUTH_GITHUB_CHECKLIST.md`

## 4) 인프라 반영
- 192.168.50.250: systemd user 서비스로 API 상시 실행 (`:18090`)
- 192.168.50.253 Traefik: `nexus.ddok.ai -> 192.168.50.250:18090`
- 외부 도메인 헬스체크 통과: `https://nexus.ddok.ai/health`

## 5) Google 우선 실연동
- Google Redirect URI: `https://nexus.ddok.ai/oauth/google/callback`
- `ALLOW_MOCK_AUTH=false` 전환
- 실토큰 경로 검증(잘못된 code로 Google `invalid_grant` 400 확인)

## 6) 현재 상태
- Google 실연동 경로: 준비 완료
- GitHub App: 조직 단위 앱 생성 후 시크릿 반영 단계 대기
