from conftest import create_workspace


def test_github_app_install_link_and_webhook(client) -> None:
    workspace_id = create_workspace(client)

    install = client.post(
        "/github/app/install-url",
        json={"workspace_id": workspace_id, "actor_email": "owner@example.com"},
    )
    assert install.status_code == 200
    state = install.json()["state"]

    callback = client.post(
        "/github/app/callback",
        json={"state": state, "installation_id": 12345, "account_login": "BAEM1N"},
    )
    assert callback.status_code == 200

    linked = client.post(
        "/github/repos/link",
        json={
            "workspace_id": workspace_id,
            "actor_email": "owner@example.com",
            "installation_id": 12345,
            "repo_full_name": "BAEM1N/gws-deepagent-workspace",
        },
    )
    assert linked.status_code == 200

    webhook = client.post(
        "/github/webhook",
        headers={"x-github-event": "push"},
        json={
            "installation": {"id": 12345},
            "repository": {"full_name": "BAEM1N/gws-deepagent-workspace"},
            "sender": {"login": "baem1n"},
        },
    )
    assert webhook.status_code == 200
    assert webhook.json()["workspace_id"] == workspace_id

    events = client.get(
        "/github/events",
        params={"workspace_id": workspace_id, "actor_email": "owner@example.com"},
    )
    assert events.status_code == 200
    assert len(events.json()["events"]) == 1
