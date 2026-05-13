"""Tests for the Leak Investigation Report Generator."""

import os
import sys
import tempfile
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from leak_report.collector import collect_from_json
from leak_report.models import Finding, LeakIncident, LeakReport, RemediationStep, TimelineEvent
from leak_report.reporters import generate_html, generate_markdown, generate_text


SAMPLE_JSON = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_incident.json")


def _make_report() -> LeakReport:
    return LeakReport(
        incident=LeakIncident(
            incident_id="INC-TEST-001",
            title="Test Memory Leak",
            leak_type="memory",
            severity="high",
            detected_at=datetime(2026, 5, 1, 10, 0),
            reported_by="Test User",
            location="service-alpha",
            description="Heap memory grows unbounded under load.",
            affected_systems=["service-alpha", "load-balancer"],
        ),
        executive_summary="Memory leak detected in service-alpha causing OOM crashes.",
        timeline=[
            TimelineEvent(datetime(2026, 5, 1, 9, 0), "First OOM restart observed", "Monitoring"),
            TimelineEvent(datetime(2026, 5, 1, 10, 0), "Issue escalated to engineering", "On-call"),
        ],
        root_cause="EventEmitter listeners not removed on request teardown.",
        impact_assessment="Service restarts every ~3 hours under normal load.",
        findings=[
            Finding("Memory Management", "Listeners accumulate per request", "heap dump #42", "high"),
            Finding("Logging", "No memory metrics exported", "Grafana dashboard", "low"),
        ],
        remediation_steps=[
            RemediationStep(1, "Remove listeners in teardown handler", "Backend Team", "2026-05-05", "completed"),
            RemediationStep(2, "Add heap metrics to Prometheus", "SRE Team", "2026-05-10", "pending"),
        ],
        recommendations=["Add memory leak regression tests.", "Set up heap dump alerting."],
        generated_by="Test Suite",
    )


class TestCollectFromJson(unittest.TestCase):
    def test_loads_sample_file(self):
        report = collect_from_json(SAMPLE_JSON)
        assert report.incident.incident_id == "INC-2026-0042"
        assert report.incident.severity == "critical"
        assert len(report.timeline) == 7
        assert len(report.findings) == 4
        assert len(report.remediation_steps) == 6

    def test_affected_systems_parsed(self):
        report = collect_from_json(SAMPLE_JSON)
        assert "prod-db-01 (PostgreSQL RDS)" in report.incident.affected_systems

    def test_timeline_sorted_correctly(self):
        report = collect_from_json(SAMPLE_JSON)
        timestamps = [e.timestamp for e in report.timeline]
        assert timestamps == sorted(timestamps)


class TestTextReporter(unittest.TestCase):
    def test_contains_incident_id(self):
        report = _make_report()
        output = generate_text(report)
        assert "INC-TEST-001" in output

    def test_contains_section_headers(self):
        output = generate_text(_make_report())
        for header in ["INCIDENT OVERVIEW", "EXECUTIVE SUMMARY", "TIMELINE",
                       "ROOT CAUSE", "IMPACT ASSESSMENT", "FINDINGS",
                       "REMEDIATION", "RECOMMENDATIONS"]:
            assert header in output

    def test_severity_label_present(self):
        output = generate_text(_make_report())
        assert "[HIGH]" in output

    def test_completed_status_marked(self):
        output = generate_text(_make_report())
        assert "[x]" in output


class TestMarkdownReporter(unittest.TestCase):
    def test_contains_heading(self):
        output = generate_markdown(_make_report())
        assert "# Leak Investigation Report" in output

    def test_incident_id_in_table(self):
        output = generate_markdown(_make_report())
        assert "INC-TEST-001" in output

    def test_severity_badge(self):
        output = generate_markdown(_make_report())
        assert "High" in output

    def test_timeline_table(self):
        output = generate_markdown(_make_report())
        assert "| Timestamp | Event | Actor |" in output

    def test_remediation_table(self):
        output = generate_markdown(_make_report())
        assert "Completed" in output or "completed" in output.lower()


class TestHtmlReporter(unittest.TestCase):
    def test_valid_html_structure(self):
        output = generate_html(_make_report())
        assert "<!DOCTYPE html>" in output
        assert "</html>" in output

    def test_incident_id_present(self):
        output = generate_html(_make_report())
        assert "INC-TEST-001" in output

    def test_xss_escaping(self):
        report = _make_report()
        report.incident.description = '<script>alert("xss")</script>'
        output = generate_html(report)
        assert "<script>" not in output
        assert "&lt;script&gt;" in output

    def test_severity_color_applied(self):
        output = generate_html(_make_report())
        assert "#fd7e14" in output  # high severity colour


class TestRoundTrip(unittest.TestCase):
    def test_json_to_html(self):
        report = collect_from_json(SAMPLE_JSON)
        html = generate_html(report)
        assert "INC-2026-0042" in html
        assert "critical" in html.lower()

    def test_json_to_markdown(self):
        report = collect_from_json(SAMPLE_JSON)
        md = generate_markdown(report)
        assert "INC-2026-0042" in md

    def test_output_written_to_file(self):
        report = _make_report()
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            path = f.name
        try:
            from pathlib import Path
            Path(path).write_text(generate_text(report), encoding="utf-8")
            content = Path(path).read_text(encoding="utf-8")
            assert "INC-TEST-001" in content
        finally:
            os.unlink(path)


if __name__ == "__main__":
    import unittest
    unittest.main()
