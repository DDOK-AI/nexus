from conftest import create_workspace


def test_oauth_get_callback_and_disconnect(client) -> None:
    workspace_id = create_workspace(client)

    connect = client.post(
        "/oauth/google/connect",
        json={"workspace_id": workspace_id, "user_email": "owner@example.com"},
    )
    assert connect.status_code == 200
    state = connect.json()["state"]

    callback = client.get(
        "/oauth/google/callback",
        params={"code": "demo-code", "state": state},
    )
    assert callback.status_code == 200
    assert callback.json()["connected"] is True

    disconnected = client.delete(
        "/oauth/google/account/owner@example.com",
        params={"workspace_id": workspace_id, "actor_email": "owner@example.com"},
    )
    assert disconnected.status_code == 200
    assert disconnected.json()["disconnected"] is True


def test_github_installation_repo_list_without_token(client) -> None:
    workspace_id = create_workspace(client)

    install = client.post(
        "/github/app/install-url",
        json={"workspace_id": workspace_id, "actor_email": "owner@example.com"},
    )
    assert install.status_code == 200
    state = install.json()["state"]

    callback = client.get(
        "/github/app/callback",
        params={"state": state, "installation_id": 2026, "setup_action": "install"},
    )
    assert callback.status_code == 200

    repos = client.get(
        "/github/app/installations/2026/repos",
        params={"workspace_id": workspace_id, "actor_email": "owner@example.com"},
    )
    assert repos.status_code == 200
    assert repos.json()["mode"] == "no-github-token"
