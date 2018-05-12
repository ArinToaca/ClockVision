drop table if exists workers;
create table workers (
    worker_id integer primary key autoincrement,
    at_work integer NOT NULL,
    name text NOT NULL
);
