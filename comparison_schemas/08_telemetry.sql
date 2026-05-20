-- Device telemetry with bracketed identifiers and commented-out experiments.
CREATE TABLE devices (
    [device id] TEXT PRIMARY KEY,
    model TEXT NOT NULL,
    firmware TEXT CHECK (firmware NOT LIKE '% beta %'),
    enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1))
);

CREATE TABLE readings (
    [device id] TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    metric TEXT NOT NULL,
    value NUMERIC NOT NULL,
    quality TEXT DEFAULT 'ok',
    payload TEXT,
    -- CHECK (payload <> 'this code is commented out')
    CHECK (metric IN ('temperature', 'humidity', 'battery')),
    CHECK (
        metric <> 'battery' OR (value >= 0 AND value <= 100)
    ),
    CONSTRAINT quality_known CHECK (
        quality IN ('ok', 'estimated', 'bad')
    )
);
