from conftest import connect_google, create_workspace


def test_agent_hitl_and_logs(client) -> None:
    workspace_id = create_workspace(client)
    connect_google(client, workspace_id)

    requested = client.post(
        "/agent/execute",
        json={
            "workspace_id": workspace_id,
            "actor_email": "owner@example.com",
            "user_email": "owner@example.com",
            "instruction": "문서 저장하고 일정 생성",
            "context": {"title": "테스트 문서"},
        },
    )
    assert requested.status_code == 200
    assert requested.json()["outputs"]["approval_required"] is True
    request_id = requested.json()["outputs"]["approval_request"]["id"]

    approved = client.post(
        f"/approvals/requests/{request_id}/approve",
        json={"workspace_id": workspace_id, "actor_email": "owner@example.com", "note": "ok"},
    )
    assert approved.status_code == 200

    executed = client.post(
        "/agent/execute",
        json={
            "workspace_id": workspace_id,
            "actor_email": "owner@example.com",
            "user_email": "owner@example.com",
            "instruction": "문서 저장하고 일정 생성",
            "context": {"title": "테스트 문서", "calendar": {"title": "캘린더 일정"}},
            "approval_request_id": request_id,
        },
    )
    assert executed.status_code == 200
    assert executed.json()["execution_log_id"] > 0

    logs = client.get(
        "/agent/logs",
        params={"workspace_id": workspace_id, "actor_email": "owner@example.com"},
    )
    assert logs.status_code == 200
    assert len(logs.json()["logs"]) == 1


def test_agent_stream_requires_approval(client) -> None:
    workspace_id = create_workspace(client)
    connect_google(client, workspace_id)

    requested = client.post(
        "/agent/execute",
        json={
            "workspace_id": workspace_id,
            "actor_email": "owner@example.com",
            "user_email": "owner@example.com",
            "instruction": "일정 생성",
            "context": {"calendar": {"title": "스트림 일정"}},
        },
    )
    request_id = requested.json()["outputs"]["approval_request"]["id"]

    client.post(
        f"/approvals/requests/{request_id}/approve",
        json={"workspace_id": workspace_id, "actor_email": "owner@example.com", "note": "ok"},
    )

    stream = client.post(
        "/agent/execute/stream",
        json={
            "workspace_id": workspace_id,
            "actor_email": "owner@example.com",
            "user_email": "owner@example.com",
            "instruction": "일정 생성",
            "context": {"calendar": {"title": "스트림 일정"}},
            "approval_request_id": request_id,
        },
    )
    assert stream.status_code == 200
    assert "event: final" in stream.text
