drop table if exists worker_history;
create table worker_history (
    history_id integer primary key autoincrement,
    start_work integer NOT NULL,
    end_work integer NOT NULL,
    hours_worked integer NOT NULL,
    worker_id integer NOT NULL,
        FOREIGN KEY (worker_id) REFERENCES workers(worker_id)
);
