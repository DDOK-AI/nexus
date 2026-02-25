from __future__ import annotations

from typing import Optional

from app.db.database import db


class BillingService:
    def create_invoice(self, *, customer: str, business_no: str, supply_amount: float, vat_rate: float, metadata: dict) -> dict:
        tax_amount = round(supply_amount * vat_rate, 2)
        total_amount = round(supply_amount + tax_amount, 2)
        now = db.now_iso()
        status = "draft"

        db.execute(
            """
            INSERT INTO billing_invoices(customer, business_no, amount, tax_amount, status, metadata_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (customer, business_no, total_amount, tax_amount, status, db.to_json(metadata), now, now),
        )

        row = db.fetchone("SELECT * FROM billing_invoices ORDER BY id DESC LIMIT 1")
        assert row is not None
        return self._deserialize(row)

    def issue_invoice(self, invoice_id: int, approver: str) -> Optional[dict]:
        row = db.fetchone("SELECT * FROM billing_invoices WHERE id=?", (invoice_id,))
        if not row:
            return None

        metadata = db.from_json(row["metadata_json"])
        metadata["issued_by"] = approver
        metadata["issued_via"] = "barobill-ready-adapter"

        now = db.now_iso()
        db.execute(
            "UPDATE billing_invoices SET status=?, metadata_json=?, updated_at=? WHERE id=?",
            ("issued", db.to_json(metadata), now, invoice_id),
        )

        updated = db.fetchone("SELECT * FROM billing_invoices WHERE id=?", (invoice_id,))
        return self._deserialize(updated) if updated else None

    def list_invoices(self, limit: int = 100) -> list[dict]:
        rows = db.fetchall("SELECT * FROM billing_invoices ORDER BY id DESC LIMIT ?", (limit,))
        return [self._deserialize(row) for row in rows]

    @staticmethod
    def _deserialize(row: dict) -> dict:
        return {
            "id": row["id"],
            "customer": row["customer"],
            "business_no": row["business_no"],
            "amount": row["amount"],
            "tax_amount": row["tax_amount"],
            "status": row["status"],
            "metadata": db.from_json(row["metadata_json"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }


billing_service = BillingService()
