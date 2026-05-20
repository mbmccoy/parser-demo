-- Auth tables: note quoted identifiers and CHECK text inside string literals.
CREATE TABLE users (
    "user-id" INTEGER PRIMARY KEY,
    username TEXT NOT NULL CHECK (length(username) BETWEEN 3 AND 40),
    "user-status" TEXT NOT NULL
        CONSTRAINT user_status_known CHECK (
            "user-status" IN ('invited', 'active', 'locked', 'deleted')
        ),
    password_hash TEXT NOT NULL,
    note TEXT CHECK (note IS NULL OR note <> 'CHECK (not really a constraint)'),

    CHECK (
        "user-status" <> 'active' OR password_hash <> ''
    )
);

create table sessions (
    session_id text primary key,
    "user-id" integer not null,
    created_at text not null,
    expires_at text not null,
    revoked_at text,
    CHECK (expires_at > created_at),
    CONSTRAINT revoked_before_expiry CHECK (
        revoked_at IS NULL OR revoked_at <= expires_at
    )
);
