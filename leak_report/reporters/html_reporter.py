import html as html_lib
from ..models import LeakReport

_SEVERITY_COLORS = {
    "critical": "#dc3545",
    "high":     "#fd7e14",
    "medium":   "#ffc107",
    "low":      "#28a745",
}

_STATUS_COLORS = {
    "pending":     "#6c757d",
    "in-progress": "#007bff",
    "completed":   "#28a745",
    "deferred":    "#adb5bd",
}

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; color: #333; }
.container { max-width: 960px; margin: 40px auto; background: #fff; border-radius: 8px;
             box-shadow: 0 2px 12px rgba(0,0,0,.1); overflow: hidden; }
.header { background: #1a2b4a; color: #fff; padding: 32px 40px; }
.header h1 { font-size: 1.8rem; font-weight: 700; }
.header .meta { margin-top: 8px; font-size: .9rem; opacity: .8; }
.body { padding: 32px 40px; }
h2 { font-size: 1.2rem; font-weight: 600; color: #1a2b4a; margin: 32px 0 12px;
     padding-bottom: 6px; border-bottom: 2px solid #e0e6ef; }
h3 { font-size: 1rem; font-weight: 600; margin: 16px 0 6px; }
table { width: 100%; border-collapse: collapse; margin-bottom: 16px; font-size: .9rem; }
th { background: #f0f3f8; text-align: left; padding: 8px 12px; font-weight: 600; }
td { padding: 8px 12px; border-bottom: 1px solid #e8ecf2; }
tr:last-child td { border-bottom: none; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: .78rem;
         font-weight: 600; color: #fff; }
.finding-card { border: 1px solid #e0e6ef; border-radius: 6px; padding: 16px; margin-bottom: 12px; }
.finding-card .label { font-size: .78rem; color: #888; text-transform: uppercase;
                        font-weight: 600; letter-spacing: .05em; }
.finding-card p { margin-top: 4px; }
ul { padding-left: 20px; }
li { margin: 6px 0; }
.footer { background: #f0f3f8; padding: 16px 40px; font-size: .82rem; color: #666;
          text-align: center; border-top: 1px solid #e0e6ef; }
"""


def _e(text: str) -> str:
    return html_lib.escape(str(text))


def _badge(text: str, color: str) -> str:
    return f'<span class="badge" style="background:{color}">{_e(text.upper())}</span>'


def generate_html(report: LeakReport) -> str:
    inc = report.incident
    sev_color = _SEVERITY_COLORS.get(inc.severity, "#6c757d")

    parts: list[str] = []

    parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Leak Investigation Report – {_e(inc.incident_id)}</title>
<style>{_CSS}</style>
</head>
<body>
<div class="container">
<div class="header">
  <h1>Leak Investigation Report</h1>
  <div class="meta">
    {_e(inc.incident_id)} &nbsp;|&nbsp; Generated: {_e(report.generated_at.strftime('%Y-%m-%d %H:%M:%S'))}
    &nbsp;|&nbsp; Prepared by: {_e(report.generated_by)}
  </div>
</div>
<div class="body">""")

    # Section 1: Incident Overview
    parts.append("<h2>1. Incident Overview</h2>")
    parts.append("<table>")
    rows = [
        ("Incident ID", f"<code>{_e(inc.incident_id)}</code>"),
        ("Title", _e(inc.title)),
        ("Leak Type", _e(inc.leak_type.title())),
        ("Severity", _badge(inc.severity, sev_color)),
        ("Detected", _e(inc.detected_at.strftime("%Y-%m-%d %H:%M"))),
        ("Reported By", _e(inc.reported_by)),
        ("Location", _e(inc.location)),
    ]
    for label, value in rows:
        parts.append(f"<tr><th style='width:160px'>{label}</th><td>{value}</td></tr>")
    parts.append("</table>")
    parts.append(f"<p><strong>Description:</strong> {_e(inc.description)}</p>")
    if inc.affected_systems:
        parts.append("<p><strong>Affected Systems:</strong></p><ul>")
        for s in inc.affected_systems:
            parts.append(f"<li>{_e(s)}</li>")
        parts.append("</ul>")

    # Section 2: Executive Summary
    parts.append("<h2>2. Executive Summary</h2>")
    parts.append(f"<p>{_e(report.executive_summary)}</p>")

    # Section 3: Timeline
    parts.append("<h2>3. Timeline of Events</h2>")
    if report.timeline:
        parts.append("<table><tr><th>Timestamp</th><th>Event</th><th>Actor</th></tr>")
        for evt in sorted(report.timeline, key=lambda e: e.timestamp):
            parts.append(
                f"<tr><td>{_e(evt.timestamp.strftime('%Y-%m-%d %H:%M'))}</td>"
                f"<td>{_e(evt.event)}</td><td>{_e(evt.actor)}</td></tr>"
            )
        parts.append("</table>")
    else:
        parts.append("<p><em>No timeline events recorded.</em></p>")

    # Section 4: Root Cause
    parts.append("<h2>4. Root Cause Analysis</h2>")
    parts.append(f"<p>{_e(report.root_cause)}</p>")

    # Section 5: Impact
    parts.append("<h2>5. Impact Assessment</h2>")
    parts.append(f"<p>{_e(report.impact_assessment)}</p>")

    # Section 6: Findings
    parts.append("<h2>6. Findings</h2>")
    if report.findings:
        for i, f in enumerate(report.findings, 1):
            fc = _SEVERITY_COLORS.get(f.severity, "#6c757d")
            parts.append(f'<div class="finding-card">')
            parts.append(
                f"<div><strong>Finding #{i}: {_e(f.category)}</strong> &nbsp; "
                f"{_badge(f.severity, fc)}</div>"
            )
            parts.append(f'<p class="label" style="margin-top:10px">Description</p>')
            parts.append(f"<p>{_e(f.description)}</p>")
            parts.append(f'<p class="label" style="margin-top:8px">Evidence</p>')
            parts.append(f"<p>{_e(f.evidence)}</p>")
            parts.append("</div>")
    else:
        parts.append("<p><em>No findings recorded.</em></p>")

    # Section 7: Remediation
    parts.append("<h2>7. Remediation Steps</h2>")
    if report.remediation_steps:
        parts.append("<table><tr><th>#</th><th>Action</th><th>Owner</th><th>Deadline</th><th>Status</th></tr>")
        for step in sorted(report.remediation_steps, key=lambda s: s.priority):
            sc = _STATUS_COLORS.get(step.status, "#6c757d")
            parts.append(
                f"<tr><td>{step.priority}</td><td>{_e(step.action)}</td>"
                f"<td>{_e(step.owner)}</td><td>{_e(step.deadline)}</td>"
                f"<td>{_badge(step.status, sc)}</td></tr>"
            )
        parts.append("</table>")
    else:
        parts.append("<p><em>No remediation steps recorded.</em></p>")

    # Section 8: Recommendations
    parts.append("<h2>8. Recommendations</h2>")
    if report.recommendations:
        parts.append("<ul>")
        for rec in report.recommendations:
            parts.append(f"<li>{_e(rec)}</li>")
        parts.append("</ul>")
    else:
        parts.append("<p><em>No recommendations recorded.</em></p>")

    parts.append("</div>")  # .body
    parts.append(
        f'<div class="footer">Report generated by {_e(report.generated_by)} '
        f"on {_e(report.generated_at.strftime('%Y-%m-%d %H:%M:%S'))}</div>"
    )
    parts.append("</div></body></html>")

    return "\n".join(parts)
