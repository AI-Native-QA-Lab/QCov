import json
from pathlib import Path

from qcov.adapters.playwright import PlaywrightAdapter


def test_playwright_scan_collects_nested_spec_outcomes(tmp_path: Path) -> None:
    path = tmp_path / "playwright.json"
    path.write_text(json.dumps({
        "suites": [{
            "title": "checkout",
            "file": "tests/checkout.spec.ts",
            "specs": [
                {"title": "pays", "tests": [{"projectName": "chromium", "status": "expected"}]},
                {"title": "refund", "tests": [{"projectName": "firefox", "status": "unexpected"}]},
            ],
            "suites": [{
                "title": "retry",
                "file": "tests/checkout.spec.ts",
                "specs": [{"title": "recovers", "tests": [
                    {"projectName": "webkit", "status": "flaky"},
                    {"projectName": "webkit", "status": "skipped"},
                ]}],
            }],
        }]
    }))

    result = PlaywrightAdapter().scan(path)

    assert [(record.identity, record.status) for record in result.records] == [
        ("tests/checkout.spec.ts::checkout > pays [chromium]", "expected"),
        ("tests/checkout.spec.ts::checkout > refund [firefox]", "unexpected"),
        ("tests/checkout.spec.ts::checkout > retry > recovers [webkit]", "flaky"),
        ("tests/checkout.spec.ts::checkout > retry > recovers [webkit]", "skipped"),
    ]


def test_playwright_scan_reports_malformed_json(tmp_path: Path) -> None:
    path = tmp_path / "playwright.json"
    path.write_text("{")

    result = PlaywrightAdapter().scan(path)

    assert result.records == ()
    assert result.diagnostics[0].code == "QCOV-SCAN-001"
