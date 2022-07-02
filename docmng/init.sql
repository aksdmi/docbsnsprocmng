CREATE TABLE documents(
    _idrref BYTEA NOT NULL,
    _code varchar(50),
    _description varchar(150),
    _create_date timestamp,
    _content text,
    _sum numeric(5, 2)
);

CREATE UNIQUE INDEX IF NOT EXISTS documents_by_id ON documents (_idrref);
CREATE UNIQUE INDEX IF NOT EXISTS documents_by_code ON documents (_code);
CREATE UNIQUE INDEX IF NOT EXISTS documents_by_description ON documents (_description);
CREATE UNIQUE INDEX IF NOT EXISTS documents_by_dims ON documents (_idrref, _code, _description);