from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


LEAK_TYPES = ["memory", "data", "security", "infrastructure", "chemical", "other"]
SEVERITY_LEVELS = ["critical", "high", "medium", "low"]
REMEDIATION_STATUSES = ["pending", "in-progress", "completed", "deferred"]


@dataclass
class LeakIncident:
    incident_id: str
    title: str
    leak_type: str
    severity: str
    detected_at: datetime
    reported_by: str
    location: str
    description: str
    affected_systems: List[str] = field(default_factory=list)


@dataclass
class TimelineEvent:
    timestamp: datetime
    event: str
    actor: str = ""


@dataclass
class Finding:
    category: str
    description: str
    evidence: str
    severity: str


@dataclass
class RemediationStep:
    priority: int
    action: str
    owner: str
    deadline: str
    status: str = "pending"


@dataclass
class LeakReport:
    incident: LeakIncident
    executive_summary: str
    timeline: List[TimelineEvent]
    root_cause: str
    impact_assessment: str
    findings: List[Finding]
    remediation_steps: List[RemediationStep]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.now)
    generated_by: str = "Leak Investigation Report Generator"
