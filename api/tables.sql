CREATE TABLE record (
    id INTEGER PRIMARY KEY,
    subsidiary VARCHAR(2),
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    currency_iso VARCHAR(3),
    total_mrr FLOAT,
    data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT current_timestamp
)