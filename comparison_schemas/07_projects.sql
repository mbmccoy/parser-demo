CREATE TABLE projects (
    project_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (trim(name) <> ''),
    start_date TEXT,
    end_date TEXT,
    budget NUMERIC DEFAULT 0,
    archived INTEGER DEFAULT 0 CHECK (archived IN (0, 1)),
    CHECK (budget >= 0),
    CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date)
);

CREATE TABLE tasks (
    task_id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL CHECK (title <> ''),
    estimate_hours NUMERIC,
    actual_hours NUMERIC,
    priority TEXT DEFAULT 'normal',
    CONSTRAINT known_priority CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    CHECK (
        (estimate_hours IS NULL OR estimate_hours >= 0)
        AND
        (actual_hours IS NULL OR actual_hours >= 0)
    )
);
