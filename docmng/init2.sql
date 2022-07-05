CREATE TABLE config(
    _table_name varchar(150),
    _column_name varchar(150)
);


CREATE UNIQUE INDEX IF NOT EXISTS config_by_table_name ON config (_table_name);
