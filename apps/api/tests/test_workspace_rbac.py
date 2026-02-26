from conftest import connect_google, create_workspace


def test_workspace_rbac_and_execute(client) -> None:
    workspace_id = create_workspace(client)

    add_member = client.post(
        f"/workspaces/{workspace_id}/members",
        json={
            "actor_email": "owner@example.com",
            "target_email": "viewer@example.com",
            "role": "viewer",
        },
    )
    assert add_member.status_code == 200

    perms_owner = client.get(
        f"/workspaces/{workspace_id}/permissions/me",
        params={"user_email": "owner@example.com"},
    )
    assert perms_owner.status_code == 200
    assert perms_owner.json()["permissions"]["workspace.manage_members"] is True

    connect_google(client, workspace_id)

    execute_ok = client.post(
        f"/workspaces/{workspace_id}/execute",
        json={
            "workspace_id": workspace_id,
            "actor_email": "owner@example.com",
            "user_email": "owner@example.com",
            "service": "calendar",
            "action": "create",
            "payload": {"title": "주간 리뷰"},
        },
    )
    assert execute_ok.status_code == 200

    execute_forbidden = client.post(
        f"/workspaces/{workspace_id}/execute",
        json={
            "workspace_id": workspace_id,
            "actor_email": "viewer@example.com",
            "user_email": "viewer@example.com",
            "service": "calendar",
            "action": "create",
            "payload": {"title": "권한없음"},
        },
    )
    assert execute_forbidden.status_code == 400
