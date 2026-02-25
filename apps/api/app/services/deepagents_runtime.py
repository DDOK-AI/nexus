"""DeepAgents 오케스트레이터 기반 MVP 런타임.

실제 deepagents SDK/툴콜은 v0.2에서 연결하고,
현재는 동일한 입출력 계약으로 orchestrator 동작을 제공한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from app.services.billing_service import billing_service
from app.services.docs_service import docs_service
from app.services.github_service import github_service
from app.services.report_service import report_service
from app.services.workspace_service import workspace_service


@dataclass
class AgentCapabilityProfile:
    google_workspace: bool = True
    github_ops: bool = True
    reporting: bool = True
    billing_future: bool = True
    collab_hub: bool = True
    docs_base: bool = True


def build_capability_profile() -> AgentCapabilityProfile:
    return AgentCapabilityProfile()


def runtime_status() -> dict:
    profile = build_capability_profile()
    return {
        "status": "active",
        "runtime": "deepagents-orchestrator-mvp",
        "capabilities": profile.__dict__,
        "note": "v0.1은 Orchestrator 계약 우선 구현, v0.2에서 deepagents SDK 직접 연결",
    }


class DeepAgentOrchestrator:
    def execute(self, *, user_email: str, instruction: str, context: dict) -> dict:
        text = instruction.strip()
        lowered = text.lower()

        steps: list[dict] = []
        outputs: dict = {}

        if "주간" in text and ("보고" in text or "report" in lowered):
            end = date.today()
            start = end - timedelta(days=6)
            report = report_service.generate_report(report_type="weekly", period_start=start, period_end=end)
            steps.append({"module": "reporting", "action": "weekly_report", "ok": True})
            outputs["weekly_report"] = report

        if ("일일" in text or "daily" in lowered) and ("보고" in text or "report" in lowered):
            today = date.today()
            report = report_service.generate_report(report_type="daily", period_start=today, period_end=today)
            steps.append({"module": "reporting", "action": "daily_report", "ok": True})
            outputs["daily_report"] = report

        if "커밋" in text or "github" in lowered or "깃헙" in text:
            events = github_service.list_events(limit=20)
            steps.append({"module": "github", "action": "list_events", "ok": True, "count": len(events)})
            outputs["github_events"] = events

        if "일정" in text or "calendar" in lowered:
            calendar_payload = context.get("calendar", {"title": "AI 자동 생성 일정"})
            result = workspace_service.execute(
                user_email=user_email,
                service="calendar",
                action="create",
                payload=calendar_payload,
            )
            steps.append({"module": "workspace", "action": "calendar.create", "ok": True})
            outputs["calendar"] = result

        if "문서" in text or "docs" in lowered:
            new_doc = docs_service.create(
                space=context.get("space", "knowledge"),
                title=context.get("title", "에이전트 실행 메모"),
                content=f"지시문: {instruction}\n\n컨텍스트: {context}",
                tags=["agent", "automation"],
            )
            steps.append({"module": "docs", "action": "create", "ok": True, "doc_id": new_doc["id"]})
            outputs["doc"] = new_doc

        if "세금" in text or "invoice" in lowered or "바로빌" in text:
            invoice_ctx = context.get("invoice", {})
            if invoice_ctx.get("customer") and invoice_ctx.get("supply_amount"):
                invoice = billing_service.create_invoice(
                    customer=invoice_ctx["customer"],
                    business_no=invoice_ctx.get("business_no", ""),
                    supply_amount=float(invoice_ctx["supply_amount"]),
                    vat_rate=float(invoice_ctx.get("vat_rate", 0.1)),
                    metadata=invoice_ctx.get("metadata", {}),
                )
                steps.append({"module": "billing", "action": "create_invoice", "ok": True})
                outputs["invoice"] = invoice
            else:
                steps.append(
                    {
                        "module": "billing",
                        "action": "create_invoice",
                        "ok": False,
                        "reason": "context.invoice.customer/supply_amount 필요",
                    }
                )

        if not steps:
            steps.append({"module": "orchestrator", "action": "analyze_only", "ok": True})
            outputs["hint"] = "현재 지시문은 실행 모듈과 직접 매핑되지 않아 분석 결과만 반환합니다."

        summary = f"{len(steps)}개 단계 실행(또는 계획) 완료"
        return {"summary": summary, "steps": steps, "outputs": outputs}


orchestrator = DeepAgentOrchestrator()
