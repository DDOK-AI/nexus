from conftest import create_workspace


def test_invoice_create_and_issue_hitl(client) -> None:
    workspace_id = create_workspace(client)

    draft = client.post(
        "/billing/invoices",
        json={
            "workspace_id": workspace_id,
            "actor_email": "owner@example.com",
            "customer": "테스트고객",
            "business_no": "123-45-67890",
            "supply_amount": 100000,
            "vat_rate": 0.1,
            "metadata": {"project": "R&D 자동화"},
        },
    )
    assert draft.status_code == 200
    invoice_id = draft.json()["id"]

    req = client.post(
        f"/billing/invoices/{invoice_id}/issue",
        json={
            "workspace_id": workspace_id,
            "actor_email": "owner@example.com",
            "approver": "owner@example.com",
            "approval_request_id": 0,
        },
    )
    assert req.status_code == 200
    assert req.json()["approval_required"] is True
    request_id = req.json()["approval_request"]["id"]

    appv = client.post(
        f"/approvals/requests/{request_id}/approve",
        json={"workspace_id": workspace_id, "actor_email": "owner@example.com", "note": "issue"},
    )
    assert appv.status_code == 200

    issued = client.post(
        f"/billing/invoices/{invoice_id}/issue",
        json={
            "workspace_id": workspace_id,
            "actor_email": "owner@example.com",
            "approver": "owner@example.com",
            "approval_request_id": request_id,
        },
    )
    assert issued.status_code == 200
    assert issued.json()["status"] == "issued"
