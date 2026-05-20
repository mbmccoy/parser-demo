-- E-commerce checkout schema.
PRAGMA foreign_keys = ON;

CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'paused', 'closed')),
    created_at TEXT NOT NULL,

    CONSTRAINT email_shape CHECK (
        email LIKE '%@%' AND email NOT LIKE '% %'
    )
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    subtotal NUMERIC NOT NULL CHECK (subtotal >= 0),
    tax NUMERIC NOT NULL DEFAULT 0 CHECK (tax >= 0),
    discount NUMERIC DEFAULT 0,
    total NUMERIC NOT NULL,
    state TEXT NOT NULL DEFAULT 'draft',

    -- old rule kept for product discussion:
    -- CHECK (state IN ('cart', 'submitted')),

    CONSTRAINT valid_state CHECK (
        state IN ('draft', 'submitted', 'paid', 'cancelled', 'refunded')
    ),
    CHECK (total = subtotal + tax - COALESCE(discount, 0)),
    CHECK (discount IS NULL OR discount BETWEEN 0 AND subtotal)
);
