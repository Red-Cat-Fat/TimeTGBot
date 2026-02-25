CREATE TABLE IF NOT EXISTS chat_user_timezones (
    id INTEGER PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    utc_offset_minutes INTEGER NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_chat_user_timezones_chat_id_user_id
    ON chat_user_timezones (chat_id, user_id);
