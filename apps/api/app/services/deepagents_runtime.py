"""DeepAgents 런타임 연결을 위한 최소 인터페이스.

실제 DeepAgents SDK wiring은 Sprint 1에서 구현한다.
"""

from dataclasses import dataclass


@dataclass
class AgentCapabilityProfile:
    google_workspace: bool = True
    github_ops: bool = True
    reporting: bool = True
    billing_future: bool = True
    collab_hub: bool = True


def build_capability_profile() -> AgentCapabilityProfile:
    return AgentCapabilityProfile()


def runtime_status() -> dict:
    profile = build_capability_profile()
    return {
        "status": "bootstrapped",
        "runtime": "deepagents-sdk",
        "capabilities": profile.__dict__,
        "note": "DeepAgents 툴/서브에이전트/HITL 설정은 추후 구현",
    }
