CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL CHECK (slug GLOB '[a-z0-9-]*'),
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    visibility TEXT NOT NULL DEFAULT 'draft',
    published_at TEXT,

    CONSTRAINT visibility_allowed CHECK (
        visibility in ('draft', 'private', 'public', 'archived')
    ),
    CHECK (
        visibility <> 'public' OR published_at IS NOT NULL
    )
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL,
    author_name TEXT CHECK (author_name IS NULL OR author_name <> ''),
    body TEXT NOT NULL CHECK (body <> ''),
    moderation_state TEXT DEFAULT 'pending',
    CHECK (moderation_state IN ('pending', 'approved', 'rejected')),
    -- CREATE TABLE fake (x INTEGER CHECK (x > 0));
    CHECK (body NOT LIKE '%unbalanced ) example%')
);
