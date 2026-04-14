import json
import os
import psycopg2

SCHEMA = "t_p73609521_led_control_automati"

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])


def log_event(conn, event_type: str, description: str):
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO {SCHEMA}.event_log (event_type, description) VALUES (%s, %s)",
            (event_type, description),
        )


def handler(event: dict, context) -> dict:
    """Управление состоянием системы: получение и обновление состояния, логирование событий."""
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}

    method = event.get("httpMethod", "GET")
    conn = get_conn()

    try:
        if method == "GET":
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT motion_sensor, led_enabled, led_on, delay_seconds, updated_at FROM {SCHEMA}.system_state ORDER BY id DESC LIMIT 1"
                )
                row = cur.fetchone()
            if not row:
                return {"statusCode": 404, "headers": CORS_HEADERS, "body": json.dumps({"error": "No state found"})}
            return {
                "statusCode": 200,
                "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
                "body": json.dumps({
                    "motion_sensor": row[0],
                    "led_enabled": row[1],
                    "led_on": row[2],
                    "delay_seconds": row[3],
                    "updated_at": row[4].isoformat(),
                }),
            }

        elif method == "POST":
            body = json.loads(event.get("body") or "{}")
            action = body.get("action")
            conn.autocommit = False

            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT motion_sensor, led_enabled, led_on, delay_seconds FROM {SCHEMA}.system_state ORDER BY id DESC LIMIT 1"
                )
                row = cur.fetchone()
                motion_sensor, led_enabled, led_on, delay_seconds = row

                if action == "set_led_enabled":
                    led_enabled = body["value"]
                    desc = "Светодиод включён" if led_enabled else "Светодиод отключён"
                    cur.execute(
                        f"UPDATE {SCHEMA}.system_state SET led_enabled=%s, updated_at=NOW()",
                        (led_enabled,),
                    )
                    log_event(conn, "LED_TOGGLE", desc)

                elif action == "set_led_on":
                    led_on = body["value"]
                    desc = "Светодиод активирован вручную" if led_on else "Светодиод деактивирован вручную"
                    cur.execute(
                        f"UPDATE {SCHEMA}.system_state SET led_on=%s, updated_at=NOW()",
                        (led_on,),
                    )
                    log_event(conn, "LED_MANUAL", desc)

                elif action == "set_motion":
                    motion_sensor = body["value"]
                    desc = "Датчик движения сработал" if motion_sensor else "Датчик движения сброшен"
                    cur.execute(
                        f"UPDATE {SCHEMA}.system_state SET motion_sensor=%s, updated_at=NOW()",
                        (motion_sensor,),
                    )
                    log_event(conn, "MOTION", desc)

                elif action == "set_delay":
                    delay_seconds = int(body["value"])
                    cur.execute(
                        f"UPDATE {SCHEMA}.system_state SET delay_seconds=%s, updated_at=NOW()",
                        (delay_seconds,),
                    )
                    log_event(conn, "DELAY_CHANGE", f"Задержка изменена на {delay_seconds} сек.")

                elif action == "activate":
                    led_on = True
                    cur.execute(
                        f"UPDATE {SCHEMA}.system_state SET led_on=TRUE, updated_at=NOW()"
                    )
                    log_event(conn, "ACTIVATE", "Кнопка активации нажата — светодиод включён")

            conn.commit()
            return {
                "statusCode": 200,
                "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
                "body": json.dumps({"ok": True}),
            }

    finally:
        conn.close()

    return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"error": "Bad request"})}
