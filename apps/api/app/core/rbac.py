from __future__ import annotations

from typing import Optional

ROLE_RANK = {
    "viewer": 1,
    "member": 2,
    "admin": 3,
    "owner": 4,
}

PERMISSIONS = {
    "workspace.read": "viewer",
    "workspace.manage_members": "admin",
    "workspace.execute": "member",
    "agent.execute": "member",
    "approval.decide": "admin",
    "invoice.issue": "admin",
    "invoice.create": "member",
    "docs.write": "member",
    "chat.write": "member",
    "github.link": "admin",
}


def normalize_role(role: str) -> str:
    role_name = (role or "").strip().lower()
    if role_name not in ROLE_RANK:
        raise ValueError(f"지원하지 않는 역할입니다: {role}")
    return role_name


def has_permission(role: Optional[str], permission: str) -> bool:
    if not role:
        return False
    required = PERMISSIONS.get(permission)
    if not required:
        return False
    return ROLE_RANK.get(role, 0) >= ROLE_RANK[required]
