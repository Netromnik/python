create table task_q (
    user_id   integer PRIMARY KEY,
    body_text text,
    photo varchar(512),
    locate varchar(512),
    state varchar(64)
);