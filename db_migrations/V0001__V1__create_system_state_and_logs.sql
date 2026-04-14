
CREATE TABLE IF NOT EXISTS t_p73609521_led_control_automati.system_state (
    id SERIAL PRIMARY KEY,
    motion_sensor BOOLEAN NOT NULL DEFAULT FALSE,
    led_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    led_on BOOLEAN NOT NULL DEFAULT FALSE,
    delay_seconds INTEGER NOT NULL DEFAULT 30,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO t_p73609521_led_control_automati.system_state (motion_sensor, led_enabled, led_on, delay_seconds)
VALUES (FALSE, TRUE, FALSE, 30);

CREATE TABLE IF NOT EXISTS t_p73609521_led_control_automati.event_log (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
