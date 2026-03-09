"""HS code reference lookup service."""

from app.database import get_cursor


def search_hs_codes(query: str, limit: int = 20):
    """Search HS codes by code prefix or product description keyword."""
    if not query or not query.strip():
        return []
    query = query.strip()
    with get_cursor() as cur:
        cur.execute("""
            SELECT hs_code, product_description
            FROM hs_code_reference
            WHERE hs_code ILIKE %s OR product_description ILIKE %s
            ORDER BY
                CASE WHEN hs_code ILIKE %s THEN 0 ELSE 1 END,
                hs_code
            LIMIT %s
        """, (f"{query}%", f"%{query}%", f"{query}%", limit))
        return [
            {"hs_code": r[0], "product_description": r[1]}
            for r in cur.fetchall()
        ]


def get_descriptions_for_codes(hs_codes: list[str]) -> dict[str, str]:
    """Get product descriptions for a list of HS codes. Returns {hs_code: description}."""
    if not hs_codes:
        return {}
    with get_cursor() as cur:
        cur.execute("""
            SELECT hs_code, product_description
            FROM hs_code_reference
            WHERE hs_code = ANY(%s)
        """, (hs_codes,))
        return {r[0]: r[1] for r in cur.fetchall() if r[1]}
