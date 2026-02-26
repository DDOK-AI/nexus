# E2E 체크리스트 (Real OAuth + GitHub App)

## A. 250 서버 환경 준비
1. 템플릿 복사
   - `.env.production.template` → `.env`
2. 실값 입력
   - Google: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`
   - GitHub: `GITHUB_APP_ID`, `GITHUB_APP_SLUG`, `GITHUB_APP_PRIVATE_KEY`, `GITHUB_WEBHOOK_SECRET`
3. 강제 실모드
   - `ALLOW_MOCK_AUTH=false`
4. 점검 스크립트
   - `python3 scripts/check_real_integration_env.py`

## B. Google OAuth 실연동
1. Google Cloud Console OAuth Client 설정
2. Authorized redirect URI에 다음 포함
   - `https://YOUR_DOMAIN/oauth/google/callback` (또는 운영 엔드포인트)
3. API 호출 순서
   - `POST /workspaces`
   - `POST /oauth/google/connect`
   - 브라우저 로그인 후 `GET /oauth/google/callback?code=...&state=...`
   - `GET /oauth/google/account/{email}` 확인
4. 실행 검증
   - `POST /workspaces/{id}/execute` with `calendar.create`
   - `drive.list` 또는 `drive.search`

## C. GitHub App 실연동
1. GitHub App 생성/설치
2. Webhook URL 설정
   - `https://YOUR_DOMAIN/github/webhook`
3. App 권한 확인 (Repo metadata/read 권장)
4. API 호출 순서
   - `POST /github/app/install-url`
   - 설치 후 `GET /github/app/callback?state=...&installation_id=...`
   - `GET /github/app/installations/{installation_id}/repos`
   - `POST /github/repos/link`
5. Webhook 검증
   - push 이벤트 발생
   - `GET /github/events`에 이벤트 적재 확인

## D. HITL 포함 업무 플로우
1. Agent
   - `POST /agent/execute` → approval_required
   - `POST /approvals/requests/{id}/approve`
   - `POST /agent/execute` with `approval_request_id`
   - `POST /agent/execute/stream`
2. Billing
   - `POST /billing/invoices`
   - `POST /billing/invoices/{id}/issue` (승인 요청 생성)
   - 승인 후 재실행

## E. 완료 판정
- OAuth 계정 연결 상태 `connected=true`
- GitHub 설치 리포 조회/링크 성공
- Webhook 서명 검증 통과 + 이벤트 저장
- Agent/Billing 승인 게이트 정상 동작
- 실패 없이 end-to-end 시나리오 1회 완료
