"""Market intelligence query service."""

from app.database import get_cursor


def get_top_markets(user_hs_codes: list[str], hs_code: str = None, limit: int = 20):
    """Get top markets filtered to user's HS codes, optionally narrowed to one."""
    if not user_hs_codes:
        return []
    with get_cursor() as cur:
        if hs_code:
            # Single HS code filter — still must belong to user
            if hs_code not in user_hs_codes:
                return []
            cur.execute("""
                SELECT mi.country, mi.hs_code, mi.avg_growth_5y, mi.volatility,
                       mi.total_import, mi.opportunity_score, mi.ai_summary,
                       cr.stability_index, cr.risk_score,
                       hr.product_description
                FROM market_intelligence mi
                LEFT JOIN country_risk cr ON cr.country = mi.country
                LEFT JOIN hs_code_reference hr ON hr.hs_code = mi.hs_code
                WHERE mi.hs_code = %s
                ORDER BY mi.opportunity_score DESC
                LIMIT %s
            """, (hs_code, limit))
        else:
            cur.execute("""
                SELECT mi.country, mi.hs_code, mi.avg_growth_5y, mi.volatility,
                       mi.total_import, mi.opportunity_score, mi.ai_summary,
                       cr.stability_index, cr.risk_score,
                       hr.product_description
                FROM market_intelligence mi
                LEFT JOIN country_risk cr ON cr.country = mi.country
                LEFT JOIN hs_code_reference hr ON hr.hs_code = mi.hs_code
                WHERE mi.hs_code = ANY(%s)
                ORDER BY mi.opportunity_score DESC
                LIMIT %s
            """, (user_hs_codes, limit))
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
            "product_description": r[9],
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


def get_user_hs_codes(user_hs_codes: list[str]):
    """Get user's HS codes that exist in market_intelligence, with descriptions."""
    if not user_hs_codes:
        return []
    with get_cursor() as cur:
        cur.execute("""
            SELECT DISTINCT mi.hs_code, hr.product_description
            FROM market_intelligence mi
            LEFT JOIN hs_code_reference hr ON hr.hs_code = mi.hs_code
            WHERE mi.hs_code = ANY(%s)
            ORDER BY mi.hs_code
        """, (user_hs_codes,))
        return [
            {"hs_code": r[0], "product_description": r[1]}
            for r in cur.fetchall()
        ]


def get_map_data(user_hs_codes: list[str]):
    """Get top 10 countries per HS code for the map visualization."""
    if not user_hs_codes:
        return []
    with get_cursor() as cur:
        cur.execute("""
            SELECT country, hs_code, opportunity_score, total_import, avg_growth_5y, product_description
            FROM (
                SELECT mi.country, mi.hs_code, mi.opportunity_score,
                       mi.total_import, mi.avg_growth_5y,
                       hr.product_description,
                       ROW_NUMBER() OVER (PARTITION BY mi.hs_code ORDER BY mi.opportunity_score DESC) AS rn
                FROM market_intelligence mi
                LEFT JOIN hs_code_reference hr ON hr.hs_code = mi.hs_code
                WHERE mi.hs_code = ANY(%s)
            ) ranked
            WHERE rn <= 10
            ORDER BY hs_code, opportunity_score DESC
        """, (user_hs_codes,))
        rows = cur.fetchall()
    return [
        {
            "country": r[0], "hs_code": r[1],
            "opportunity_score": float(r[2]) if r[2] else None,
            "total_import": float(r[3]) if r[3] else None,
            "avg_growth_5y": float(r[4]) if r[4] else None,
            "product_description": r[5],
        }
        for r in rows
    ]


def get_market_summary_for_user(hs_codes: list[str]):
    """Get the top market (by opportunity score) for each of the user's HS codes."""
    if not hs_codes:
        return []
    with get_cursor() as cur:
        cur.execute("""
            SELECT country, hs_code, opportunity_score, ai_summary, risk_score, product_description
            FROM (
                SELECT mi.country, mi.hs_code, mi.opportunity_score, mi.ai_summary,
                       cr.risk_score, hr.product_description,
                       ROW_NUMBER() OVER (PARTITION BY mi.hs_code ORDER BY mi.opportunity_score DESC) AS rn
                FROM market_intelligence mi
                LEFT JOIN country_risk cr ON cr.country = mi.country
                LEFT JOIN hs_code_reference hr ON hr.hs_code = mi.hs_code
                WHERE mi.hs_code = ANY(%s)
            ) ranked
            WHERE rn = 1
            ORDER BY opportunity_score DESC
        """, (hs_codes,))
        rows = cur.fetchall()
    return [
        {"country": r[0], "hs_code": r[1], "opportunity_score": float(r[2]) if r[2] else None,
         "ai_summary": r[3], "risk_score": float(r[4]) if r[4] else None,
         "product_description": r[5]}
        for r in rows
    ]
