/* Clinic scheduling. Some constraints are intentionally table-level. */
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    clinician_id INTEGER NOT NULL,
    starts_at TEXT NOT NULL,
    ends_at TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'office' CHECK (
        kind IN ('office', 'telehealth', 'lab')
    ),
    cancelled_at TEXT,
    cancellation_reason TEXT,

    CHECK (ends_at > starts_at),
    CONSTRAINT cancellation_pair CHECK (
        (cancelled_at IS NULL AND cancellation_reason IS NULL)
        OR
        (cancelled_at IS NOT NULL AND cancellation_reason IS NOT NULL)
    )
);

CREATE TABLE lab_results (
    appointment_id INTEGER NOT NULL,
    test_code TEXT NOT NULL,
    numeric_value NUMERIC,
    unit TEXT,
    abnormal_flag TEXT CHECK (abnormal_flag IN ('L', 'H', 'N') OR abnormal_flag IS NULL),
    CHECK (numeric_value IS NULL OR unit IS NOT NULL)
);
