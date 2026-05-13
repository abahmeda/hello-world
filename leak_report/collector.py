"""Interactive CLI data collection for leak incidents."""

import json
import sys
from datetime import datetime
from typing import List

from .models import (
    LEAK_TYPES, SEVERITY_LEVELS, REMEDIATION_STATUSES,
    Finding, LeakIncident, LeakReport, RemediationStep, TimelineEvent,
)


def _prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"  {label}{suffix}: ").strip()
    return value if value else default


def _prompt_list(label: str) -> List[str]:
    print(f"  {label} (enter each on a new line, blank line to finish):")
    items = []
    while True:
        val = input("    > ").strip()
        if not val:
            break
        items.append(val)
    return items


def _prompt_choice(label: str, choices: List[str]) -> str:
    options = ", ".join(f"{i+1}={c}" for i, c in enumerate(choices))
    while True:
        raw = input(f"  {label} ({options}): ").strip().lower()
        if raw in choices:
            return raw
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass
        print(f"  Please enter one of: {', '.join(choices)}")


def _parse_datetime(raw: str) -> datetime:
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {raw!r}. Use YYYY-MM-DD HH:MM format.")


def collect_incident() -> LeakIncident:
    print("\n--- Incident Details ---")
    incident_id = _prompt("Incident ID", f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    title = _prompt("Incident title")
    leak_type = _prompt_choice("Leak type", LEAK_TYPES)
    severity = _prompt_choice("Severity", SEVERITY_LEVELS)

    while True:
        raw_dt = _prompt("Detected at (YYYY-MM-DD HH:MM)", datetime.now().strftime("%Y-%m-%d %H:%M"))
        try:
            detected_at = _parse_datetime(raw_dt)
            break
        except ValueError as e:
            print(f"  Error: {e}")

    reported_by = _prompt("Reported by")
    location = _prompt("Location / system name")
    description = _prompt("Brief description")
    affected_systems = _prompt_list("Affected systems/components")

    return LeakIncident(
        incident_id=incident_id,
        title=title,
        leak_type=leak_type,
        severity=severity,
        detected_at=detected_at,
        reported_by=reported_by,
        location=location,
        description=description,
        affected_systems=affected_systems,
    )


def collect_timeline() -> List[TimelineEvent]:
    print("\n--- Timeline of Events ---")
    print("  (Enter chronological events; blank line to finish)")
    events: List[TimelineEvent] = []
    while True:
        raw_dt = input("  Timestamp (YYYY-MM-DD HH:MM) or blank to finish: ").strip()
        if not raw_dt:
            break
        try:
            ts = _parse_datetime(raw_dt)
        except ValueError as e:
            print(f"  Error: {e}")
            continue
        event = _prompt("  Event description")
        actor = _prompt("  Actor / team")
        events.append(TimelineEvent(timestamp=ts, event=event, actor=actor))
    return events


def collect_findings() -> List[Finding]:
    print("\n--- Findings ---")
    print("  (Describe each finding; blank line to finish)")
    findings: List[Finding] = []
    idx = 1
    while True:
        print(f"\n  Finding #{idx}:")
        category = input("  Category (or blank to finish): ").strip()
        if not category:
            break
        description = _prompt("  Description")
        evidence = _prompt("  Evidence / source")
        severity = _prompt_choice("  Severity", SEVERITY_LEVELS)
        findings.append(Finding(category=category, description=description,
                                evidence=evidence, severity=severity))
        idx += 1
    return findings


def collect_remediation() -> List[RemediationStep]:
    print("\n--- Remediation Steps ---")
    steps: List[RemediationStep] = []
    idx = 1
    while True:
        print(f"\n  Step #{idx}:")
        action = input("  Action (or blank to finish): ").strip()
        if not action:
            break
        owner = _prompt("  Owner / responsible team")
        deadline = _prompt("  Deadline (e.g. 2026-05-20)")
        status = _prompt_choice("  Status", REMEDIATION_STATUSES)
        steps.append(RemediationStep(priority=idx, action=action,
                                     owner=owner, deadline=deadline, status=status))
        idx += 1
    return steps


def collect_interactive() -> LeakReport:
    print("=" * 60)
    print("  LEAK INVESTIGATION REPORT GENERATOR")
    print("=" * 60)

    incident = collect_incident()

    print("\n--- Executive Summary ---")
    executive_summary = _prompt("Executive summary")

    timeline = collect_timeline()

    print("\n--- Root Cause Analysis ---")
    root_cause = _prompt("Root cause")

    print("\n--- Impact Assessment ---")
    impact_assessment = _prompt("Impact assessment")

    findings = collect_findings()
    remediation_steps = collect_remediation()

    print("\n--- Recommendations ---")
    recommendations = _prompt_list("Recommendations")

    print("\n--- Report Metadata ---")
    generated_by = _prompt("Report prepared by", "Leak Investigation Team")

    return LeakReport(
        incident=incident,
        executive_summary=executive_summary,
        timeline=timeline,
        root_cause=root_cause,
        impact_assessment=impact_assessment,
        findings=findings,
        remediation_steps=remediation_steps,
        recommendations=recommendations,
        generated_by=generated_by,
    )


def collect_from_json(path: str) -> LeakReport:
    with open(path) as f:
        data = json.load(f)

    inc_data = data["incident"]
    incident = LeakIncident(
        incident_id=inc_data["incident_id"],
        title=inc_data["title"],
        leak_type=inc_data["leak_type"],
        severity=inc_data["severity"],
        detected_at=_parse_datetime(inc_data["detected_at"]),
        reported_by=inc_data["reported_by"],
        location=inc_data.get("location", ""),
        description=inc_data["description"],
        affected_systems=inc_data.get("affected_systems", []),
    )

    timeline = [
        TimelineEvent(
            timestamp=_parse_datetime(e["timestamp"]),
            event=e["event"],
            actor=e.get("actor", ""),
        )
        for e in data.get("timeline", [])
    ]

    findings = [
        Finding(
            category=f["category"],
            description=f["description"],
            evidence=f.get("evidence", ""),
            severity=f["severity"],
        )
        for f in data.get("findings", [])
    ]

    remediation_steps = [
        RemediationStep(
            priority=i + 1,
            action=s["action"],
            owner=s.get("owner", ""),
            deadline=s.get("deadline", "TBD"),
            status=s.get("status", "pending"),
        )
        for i, s in enumerate(data.get("remediation_steps", []))
    ]

    return LeakReport(
        incident=incident,
        executive_summary=data.get("executive_summary", ""),
        timeline=timeline,
        root_cause=data.get("root_cause", ""),
        impact_assessment=data.get("impact_assessment", ""),
        findings=findings,
        remediation_steps=remediation_steps,
        recommendations=data.get("recommendations", []),
        generated_by=data.get("generated_by", "Leak Investigation Report Generator"),
    )
