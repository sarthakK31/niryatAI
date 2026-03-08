"""Market intelligence query service."""

from app.database import get_cursor


def get_top_markets(hs_code: str = None, limit: int = 20):
    """Get top markets by opportunity score, optionally filtered by HS code."""
    with get_cursor() as cur:
        if hs_code:
            cur.execute("""
                SELECT mi.country, mi.hs_code, mi.avg_growth_5y, mi.volatility,
                       mi.total_import, mi.opportunity_score, mi.ai_summary,
                       cr.stability_index, cr.risk_score
                FROM market_intelligence mi
                LEFT JOIN country_risk cr ON cr.country = mi.country
                WHERE mi.hs_code = %s
                ORDER BY mi.opportunity_score DESC
                LIMIT %s
            """, (hs_code, limit))
        else:
            cur.execute("""
                SELECT mi.country, mi.hs_code, mi.avg_growth_5y, mi.volatility,
                       mi.total_import, mi.opportunity_score, mi.ai_summary,
                       cr.stability_index, cr.risk_score
                FROM market_intelligence mi
                LEFT JOIN country_risk cr ON cr.country = mi.country
                ORDER BY mi.opportunity_score DESC
                LIMIT %s
            """, (limit,))
        rows = cur.fetchall()

    return [
        {
            "country": r[0], "hs_code": r[1], "avg_growth_5y": float(r[2]) if r[2] else None,
            "volatility": float(r[3]) if r[3] else None,
            "total_import": float(r[4]) if r[4] else None,
            "opportunity_score": float(r[5]) if r[5] else None,
            "ai_summary": r[6],
            "stability_index": float(r[7]) if r[7] else None,
            "risk_score": float(r[8]) if r[8] else None,
        }
        for r in rows
    ]


def get_country_risks(limit: int = 50):
    """Get all countries with risk scores."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT country, stability_index, risk_score
            FROM country_risk
            ORDER BY risk_score DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
    return [
        {"country": r[0], "stability_index": float(r[1]) if r[1] else None,
         "risk_score": float(r[2]) if r[2] else None}
        for r in rows
    ]


def get_available_hs_codes():
    """Get distinct HS codes in the database."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT DISTINCT hs_code FROM market_intelligence ORDER BY hs_code
        """)
        return [r[0] for r in cur.fetchall()]


def get_market_summary_for_user(hs_codes: list[str]):
    """Get a summary of best markets for a user's product codes."""
    if not hs_codes:
        return []
    with get_cursor() as cur:
        cur.execute("""
            SELECT mi.country, mi.hs_code, mi.opportunity_score, mi.ai_summary,
                   cr.risk_score
            FROM market_intelligence mi
            LEFT JOIN country_risk cr ON cr.country = mi.country
            WHERE mi.hs_code = ANY(%s)
            ORDER BY mi.opportunity_score DESC
            LIMIT 10
        """, (hs_codes,))
        rows = cur.fetchall()
    return [
        {"country": r[0], "hs_code": r[1], "opportunity_score": float(r[2]) if r[2] else None,
         "ai_summary": r[3], "risk_score": float(r[4]) if r[4] else None}
        for r in rows
    ]
