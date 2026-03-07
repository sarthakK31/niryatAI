from strands import tool
import psycopg2
import pandas as pd
import re

conn = psycopg2.connect(
    host="localhost", port=5432, database="testdb", user="postgres", password="password"
)


ALLOWED_TABLES = {"market_intelligence", "country_risk"}


@tool
def list_tables():
    """
    List all tables the agent is allowed to access.
    """

    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema='public';
    """

    df = pd.read_sql(query, conn)

    tables = df["table_name"].tolist()

    # Filter allowed tables
    visible_tables = [t for t in tables if t in ALLOWED_TABLES]

    return visible_tables

@tool
def describe_table(table_name: str):
    """
    Show columns and types for an allowed table.
    """

    if table_name not in ALLOWED_TABLES:
        return f"Access denied for table {table_name}"

    query = f"""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = %s;
    """

    df = pd.read_sql(query, conn, params=(table_name,))

    return df.to_dict(orient="records")


@tool
def preview_table(table_name: str, limit: int = 10):
    """
    Preview rows from a table.
    """
    
    if table_name not in ALLOWED_TABLES:
        return f"Access denied for table {table_name}"
    
    query = f"SELECT * FROM {table_name} LIMIT %s"

    df = pd.read_sql(query, conn, params=(limit,))

    return df.to_dict(orient="records")


@tool
def run_query(sql_query: str):
    """
    Execute a safe read-only SQL query for data analysis.
    Only SELECT queries should be used.
    """

    blocked = ["insert", "update", "delete", "drop", "alter", "truncate"]

    lower = sql_query.lower()

    if not lower.strip().startswith("select"):
        return "Only SELECT queries allowed."

    if any(word in lower for word in blocked):
        return "Dangerous query blocked."

    # Extract table names from query
    tables = re.findall(
        r'(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        sql_query.lower()
    )    
    
    for table in tables:
        if table not in ALLOWED_TABLES:
            return f"Access denied for table {table}"
        
    df = pd.read_sql(sql_query, conn)
    return df.head(50).to_dict(orient="records")


@tool
def get_schema():
    """
    Return schema overview for allowed tables only.
    """

    query = """
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema='public'
    """

    df = pd.read_sql(query, conn)

    df = df[df["table_name"].isin(ALLOWED_TABLES)]

    return df.to_dict(orient="records")
