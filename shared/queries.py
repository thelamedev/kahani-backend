CREATE_USER_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS users (
    id int primary_key not null,
    username text not null,
    password_hash text not null,
    created_at datetime default current_timestamp,
    deleted_at datetime default null
)
"""
