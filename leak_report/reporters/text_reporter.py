from ..models import LeakReport

_SEVERITY_LABELS = {
    "critical": "[CRITICAL]",
    "high":     "[HIGH]    ",
    "medium":   "[MEDIUM]  ",
    "low":      "[LOW]     ",
}

_STATUS_LABELS = {
    "pending":     "[ ]",
    "in-progress": "[~]",
    "completed":   "[x]",
    "deferred":    "[-]",
}


def _section(title: str) -> str:
    border = "=" * 60
    return f"\n{border}\n  {title.upper()}\n{border}\n"


def _subsection(title: str) -> str:
    return f"\n  --- {title} ---\n"


def generate_text(report: LeakReport) -> str:
    inc = report.incident
    lines: list[str] = []

    lines.append("=" * 60)
    lines.append("  LEAK INVESTIGATION REPORT")
    lines.append("=" * 60)
    lines.append(f"  Generated : {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  Prepared by: {report.generated_by}")

    lines.append(_section("1. Incident Overview"))
    lines.append(f"  ID         : {inc.incident_id}")
    lines.append(f"  Title      : {inc.title}")
    lines.append(f"  Type       : {inc.leak_type.upper()}")
    lines.append(f"  Severity   : {inc.severity.upper()}")
    lines.append(f"  Detected   : {inc.detected_at.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"  Reported by: {inc.reported_by}")
    lines.append(f"  Location   : {inc.location}")
    lines.append(f"\n  Description:\n  {inc.description}")
    if inc.affected_systems:
        lines.append("\n  Affected Systems:")
        for s in inc.affected_systems:
            lines.append(f"    - {s}")

    lines.append(_section("2. Executive Summary"))
    lines.append(f"  {report.executive_summary}")

    lines.append(_section("3. Timeline of Events"))
    if report.timeline:
        for evt in sorted(report.timeline, key=lambda e: e.timestamp):
            actor = f" ({evt.actor})" if evt.actor else ""
            lines.append(f"  {evt.timestamp.strftime('%Y-%m-%d %H:%M')}  {evt.event}{actor}")
    else:
        lines.append("  No timeline events recorded.")

    lines.append(_section("4. Root Cause Analysis"))
    lines.append(f"  {report.root_cause}")

    lines.append(_section("5. Impact Assessment"))
    lines.append(f"  {report.impact_assessment}")

    lines.append(_section("6. Findings"))
    if report.findings:
        for i, f in enumerate(report.findings, 1):
            sev = _SEVERITY_LABELS.get(f.severity, f"[{f.severity}]")
            lines.append(f"\n  Finding #{i} {sev}")
            lines.append(f"  Category   : {f.category}")
            lines.append(f"  Description: {f.description}")
            lines.append(f"  Evidence   : {f.evidence}")
    else:
        lines.append("  No findings recorded.")

    lines.append(_section("7. Remediation Steps"))
    if report.remediation_steps:
        for step in sorted(report.remediation_steps, key=lambda s: s.priority):
            status = _STATUS_LABELS.get(step.status, f"[{step.status}]")
            lines.append(f"\n  {status} #{step.priority}. {step.action}")
            lines.append(f"       Owner   : {step.owner}")
            lines.append(f"       Deadline: {step.deadline}")
            lines.append(f"       Status  : {step.status}")
    else:
        lines.append("  No remediation steps recorded.")

    lines.append(_section("8. Recommendations"))
    if report.recommendations:
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"  {i}. {rec}")
    else:
        lines.append("  No recommendations recorded.")

    lines.append("\n" + "=" * 60)
    lines.append("  END OF REPORT")
    lines.append("=" * 60 + "\n")

    return "\n".join(lines)
