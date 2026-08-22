"""HR Priority Queue — WHAT NEEDS YOUR ATTENTION TODAY."""

from __future__ import annotations

PRIORITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def generate_priority_queue(
    anomalies: list[dict],
    risk_signals: list[dict],
    leave_conflicts: list[dict],
    pending_actions: list[dict],
) -> list[dict]:
    """Generate ranked priority queue items."""
    items: list[dict] = []

    for anomaly in anomalies:
        severity = str(anomaly.get("severity", "MEDIUM")).upper()
        if severity not in PRIORITY_ORDER:
            severity = "MEDIUM"
        items.append(
            {
                "priority": severity if severity == "HIGH" else ("MEDIUM" if severity == "MEDIUM" else "LOW"),
                "title": "Attendance Anomaly Detected",
                "description": f"Unusual attendance pattern for {anomaly.get('employee_name', anomaly.get('employee_id'))}",
                "employee_id": anomaly.get("employee_id", "N/A"),
                "employee_name": anomaly.get("employee_name", "Unknown"),
                "reason": anomaly.get("reason", "Attendance pattern deviates from baseline"),
                "recommended_action": anomaly.get("recommendation", "Review attendance history with the employee"),
            }
        )

    for signal in risk_signals:
        level = str(signal.get("risk_level", "MEDIUM")).upper()
        if level not in PRIORITY_ORDER:
            level = "MEDIUM"
        reasons = signal.get("reasons", [])
        items.append(
            {
                "priority": level,
                "title": "Workplace Risk Signal",
                "description": f"Elevated workplace risk indicators for {signal.get('employee_name', signal.get('employee_id'))}",
                "employee_id": signal.get("employee_id", "N/A"),
                "employee_name": signal.get("employee_name", "Unknown"),
                "reason": reasons[0] if reasons else "Multiple risk factors above threshold",
                "recommended_action": (signal.get("recommendations") or ["Schedule supportive HR check-in"])[0],
            }
        )

    for conflict in leave_conflicts:
        level = str(conflict.get("conflict_level", "MEDIUM")).upper()
        items.append(
            {
                "priority": level if level in PRIORITY_ORDER else "MEDIUM",
                "title": "Leave Conflict",
                "description": conflict.get("description", "Scheduling conflict detected for leave request"),
                "employee_id": conflict.get("employee_id", "N/A"),
                "employee_name": conflict.get("employee_name", "Unknown"),
                "reason": (conflict.get("reasons") or ["Team availability impact"])[0],
                "recommended_action": conflict.get("recommendation", "Review team calendar before approving"),
            }
        )

    for action in pending_actions:
        items.append(
            {
                "priority": action.get("priority", "LOW"),
                "title": action.get("title", "Pending Administrative Action"),
                "description": action.get("description", "Action requires HR review"),
                "employee_id": action.get("employee_id", "N/A"),
                "employee_name": action.get("employee_name", "Multiple"),
                "reason": action.get("reason", "Administrative backlog"),
                "recommended_action": action.get("recommended_action", "Review and respond promptly"),
            }
        )

    items.sort(key=lambda x: PRIORITY_ORDER.get(x["priority"], 99))
    return items[:20]
