import json
import os
import psycopg2

SCHEMA = "t_p73609521_led_control_automati"

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def handler(event: dict, context) -> dict:
    """Получение журнала событий системы управления освещением."""
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}

    params = event.get("queryStringParameters") or {}
    limit = min(int(params.get("limit", 50)), 200)

    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT id, event_type, description, created_at
                FROM {SCHEMA}.event_log
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    logs = [
        {
            "id": r[0],
            "event_type": r[1],
            "description": r[2],
            "created_at": r[3].isoformat(),
        }
        for r in rows
    ]

    return {
        "statusCode": 200,
        "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
        "body": json.dumps({"logs": logs}),
    }
