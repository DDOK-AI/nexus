from datetime import date


def _connect_google(client, email: str = "ceo@example.com") -> None:
    resp = client.post(
        "/oauth/google/callback",
        json={"code": "demo-auth-code", "state": "local", "user_email": email},
    )
    assert resp.status_code == 200


def test_github_webhook_and_weekly_report(client) -> None:
    webhook = client.post(
        "/github/webhook",
        headers={"x-github-event": "push"},
        json={
            "repository": {"full_name": "BAEM1N/gws-deepagent-workspace"},
            "sender": {"login": "baem1n"},
            "commits": [{"id": "abc123", "message": "feat: add report pipeline"}],
        },
    )
    assert webhook.status_code == 200
    assert webhook.json()["saved"] is True

    report = client.post(
        "/reports/weekly",
        json={"period_start": date.today().isoformat(), "period_end": date.today().isoformat()},
    )
    assert report.status_code == 200
    assert report.json()["report_type"] == "weekly"


def test_agent_execute_end_to_end(client) -> None:
    _connect_google(client)

    client.post(
        "/github/webhook",
        headers={"x-github-event": "pull_request"},
        json={
            "repository": {"full_name": "BAEM1N/gws-deepagent-workspace"},
            "sender": {"login": "baem1n"},
            "action": "opened",
        },
    )

    run = client.post(
        "/agent/execute",
        json={
            "user_email": "ceo@example.com",
            "instruction": "이번 주 커밋 기반으로 주간 보고 만들고 문서 저장하고 일정 생성해",
            "context": {
                "calendar": {"title": "주간 R&D 리뷰", "start": "2026-02-26T10:00:00", "end": "2026-02-26T11:00:00"},
                "title": "주간 R&D 자동 보고",
            },
        },
    )

    assert run.status_code == 200
    body = run.json()
    assert "weekly_report" in body["outputs"]
    assert "doc" in body["outputs"]
    assert "calendar" in body["outputs"]
