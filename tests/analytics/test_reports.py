"""Analytics reports tests."""

from reports import build_attendance_report, build_department_report, build_leave_report, build_payroll_summary, build_risk_summary


def test_attendance_report(sample_employees, sample_attendance):
    report = build_attendance_report(sample_attendance, sample_employees)
    assert report["report_type"] == "attendance"
    assert len(report["rows"]) >= 1
    assert "attendance_rate" in report["rows"][0]


def test_leave_report(sample_employees, sample_leaves):
    report = build_leave_report(sample_leaves, sample_employees)
    assert report["report_type"] == "leave"
    assert report["rows"][0]["status"] == "PENDING"


def test_department_report(sample_employees, sample_attendance):
    report = build_department_report(sample_employees, sample_attendance)
    assert report["report_type"] == "department"
    depts = {row["department"] for row in report["rows"]}
    assert "Engineering" in depts


def test_payroll_and_risk_reports():
    payroll = build_payroll_summary([{"base_salary": 90000, "net_salary": 85000}])
    assert payroll["total_monthly"] == 85000

    risk = build_risk_summary(
        [{"employee_id": "EMP002", "risk_level": "HIGH"}],
        [{"employee_id": "EMP002", "severity": "HIGH"}],
    )
    assert risk["risk_distribution"]["HIGH"] == 1
    assert risk["flagged_employees"] == 1
