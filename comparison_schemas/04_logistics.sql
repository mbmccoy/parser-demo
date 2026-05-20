CREATE TABLE warehouses (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL CHECK (code <> ''),
    capacity INTEGER CHECK (capacity > 0),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
);

-- Multiline and mixed capitalization on purpose.
CrEaTe TaBlE shipments (
    id INTEGER PRIMARY KEY,
    origin_warehouse INTEGER NOT NULL,
    destination_warehouse INTEGER NOT NULL,
    weight_kg NUMERIC NOT NULL,
    fragile INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'queued',

    CHECK (
        origin_warehouse <> destination_warehouse
    ),
    constraint positive_weight CHECK (weight_kg > 0),
    CHECK (fragile IN (0, 1)),
    CHECK (
        status IN (
            'queued',
            'in_transit',
            'delivered',
            'returned'
        )
    )
);
