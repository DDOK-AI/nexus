def test_invoice_create_and_issue(client) -> None:
    draft = client.post(
        "/billing/invoices",
        json={
            "customer": "테스트고객",
            "business_no": "123-45-67890",
            "supply_amount": 100000,
            "vat_rate": 0.1,
            "metadata": {"project": "R&D 자동화"},
        },
    )
    assert draft.status_code == 200
    invoice_id = draft.json()["id"]
    assert draft.json()["status"] == "draft"

    issued = client.post(f"/billing/invoices/{invoice_id}/issue", json={"approver": "ceo"})
    assert issued.status_code == 200
    assert issued.json()["status"] == "issued"
