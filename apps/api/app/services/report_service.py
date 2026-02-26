from __future__ import annotations

from collections import Counter
from datetime import date, datetime, time, timezone
from typing import Optional

from app.db.database import db
from app.services.docs_service import docs_service
from app.services.github_service import github_service


class ReportService:
    def generate_report(
        self,
        *,
        workspace_id: int,
        actor_email: str,
        report_type: str,
        period_start: date,
        period_end: date,
    ) -> dict:
        start = datetime.combine(period_start, time.min).replace(tzinfo=timezone.utc)
        end = datetime.combine(period_end, time.max).replace(tzinfo=timezone.utc)
        events = github_service.events_between(workspace_id, start, end)

        counter = Counter([event["event_type"] for event in events])
        repo_counter = Counter([event["repo"] for event in events if event["repo"]])

        lines: list[str] = []
        lines.append(f"# {report_type.upper()} Report")
        lines.append(f"- 기간: {period_start.isoformat()} ~ {period_end.isoformat()}")
        lines.append(f"- 수집 이벤트 수: {len(events)}")
        lines.append("")

        if counter:
            lines.append("## 이벤트 타입 요약")
            for event_type, count in counter.items():
                lines.append(f"- {event_type}: {count}건")
            lines.append("")

        if repo_counter:
            lines.append("## 저장소 활동 요약")
            for repo, count in repo_counter.items():
                lines.append(f"- {repo}: {count}건")
            lines.append("")

        if events:
            lines.append("## 주요 이벤트")
            for event in events[:30]:
                lines.append(
                    f"- [{event['created_at']}] {event['event_type']} / {event['repo'] or '-'} / {event['actor'] or '-'}"
                )
        else:
            lines.append("## 주요 이벤트")
            lines.append("- 해당 기간 GitHub 이벤트가 없습니다.")

        content = "\n".join(lines)
        now = db.now_iso()
        title = f"{report_type}-{period_start.isoformat()}-{period_end.isoformat()}"

        db.execute(
            """
            INSERT INTO reports(workspace_id, report_type, period_start, period_end, title, content, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (workspace_id, report_type, period_start.isoformat(), period_end.isoformat(), title, content, actor_email, now),
        )

        report = db.fetchone("SELECT * FROM reports ORDER BY id DESC LIMIT 1")
        assert report is not None

        docs_service.create(
            workspace_id=workspace_id,
            created_by=actor_email,
            space="reports",
            title=title,
            content=content,
            tags=["report", report_type, period_start.isoformat(), period_end.isoformat()],
        )

        return report

    def list_reports(self, *, workspace_id: int, report_type: Optional[str] = None, limit: int = 100) -> list[dict]:
        if report_type:
            rows = db.fetchall(
                "SELECT * FROM reports WHERE workspace_id=? AND report_type=? ORDER BY id DESC LIMIT ?",
                (workspace_id, report_type, limit),
            )
        else:
            rows = db.fetchall(
                "SELECT * FROM reports WHERE workspace_id=? ORDER BY id DESC LIMIT ?",
                (workspace_id, limit),
            )
        return rows


report_service = ReportService()
