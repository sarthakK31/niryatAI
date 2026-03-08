"""Export readiness tracking service."""

from app.database import get_cursor


def get_all_steps_with_progress(user_id: str):
    """Get all export steps with user's completion status."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                es.id AS step_id,
                es.step_number,
                es.title AS step_title,
                es.description AS step_desc,
                es.category,
                sub.id AS substep_id,
                sub.substep_number,
                sub.title AS substep_title,
                sub.description AS substep_desc,
                COALESCE(ur.completed, false) AS completed,
                ur.completed_at,
                ur.notes
            FROM export_steps es
            JOIN export_substeps sub ON sub.step_id = es.id
            LEFT JOIN user_readiness ur ON ur.substep_id = sub.id AND ur.user_id = %s
            ORDER BY es.step_number, sub.substep_number
        """, (user_id,))
        rows = cur.fetchall()

    steps = {}
    for r in rows:
        step_id = r[0]
        if step_id not in steps:
            steps[step_id] = {
                "step_number": r[1],
                "title": r[2],
                "description": r[3],
                "category": r[4],
                "substeps": [],
                "completed_count": 0,
                "total_count": 0,
            }
        substep = {
            "id": r[5],
            "substep_number": r[6],
            "title": r[7],
            "description": r[8],
            "completed": r[9],
            "completed_at": r[10],
            "notes": r[11],
        }
        steps[step_id]["substeps"].append(substep)
        steps[step_id]["total_count"] += 1
        if substep["completed"]:
            steps[step_id]["completed_count"] += 1

    return sorted(steps.values(), key=lambda s: s["step_number"])


def mark_substep(user_id: str, substep_id: int, completed: bool, notes: str = None):
    """Mark a substep as completed or incomplete."""
    with get_cursor(commit=True) as cur:
        if completed:
            cur.execute("""
                INSERT INTO user_readiness (user_id, substep_id, completed, completed_at, notes)
                VALUES (%s, %s, true, NOW(), %s)
                ON CONFLICT (user_id, substep_id)
                DO UPDATE SET completed = true, completed_at = NOW(), notes = COALESCE(%s, user_readiness.notes)
            """, (user_id, substep_id, notes, notes))
        else:
            cur.execute("""
                INSERT INTO user_readiness (user_id, substep_id, completed, completed_at, notes)
                VALUES (%s, %s, false, NULL, %s)
                ON CONFLICT (user_id, substep_id)
                DO UPDATE SET completed = false, completed_at = NULL
            """, (user_id, substep_id, notes))


def get_readiness_summary(user_id: str):
    """Get overall readiness percentage and next step."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM export_substeps
        """)
        total = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM user_readiness
            WHERE user_id = %s AND completed = true
        """, (user_id,))
        done = cur.fetchone()[0]

        # Find next incomplete substep
        cur.execute("""
            SELECT es.title, sub.title
            FROM export_substeps sub
            JOIN export_steps es ON es.id = sub.step_id
            LEFT JOIN user_readiness ur ON ur.substep_id = sub.id AND ur.user_id = %s
            WHERE COALESCE(ur.completed, false) = false
            ORDER BY es.step_number, sub.substep_number
            LIMIT 1
        """, (user_id,))
        next_step = cur.fetchone()

    pct = round((done / total * 100), 1) if total > 0 else 0
    return {
        "total_substeps": total,
        "completed_substeps": done,
        "percentage": pct,
        "next_step": f"{next_step[0]} → {next_step[1]}" if next_step else "All complete!",
    }
