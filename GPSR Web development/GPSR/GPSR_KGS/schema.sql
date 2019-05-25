create table if not exists user (
  user_num integer primary key autoincrement,
  user_id string not null,
  user_nickname string not null,
  user_email string not null,
  user_pw_hash string not null
);

create table if not exists problem (
  problem_num integer primary key autoincrement, 
  problem_name string not null,
  problem_correct integer,
  problem_text string not null
);

create table if not exists follow (
  follow_who_id integer,
  follow_whom_id integer
);

create table if not exists board (
  board_num integer primary key autoincrement,
  board_name string not null,
  board_text string not null
);

create table if not exists answer (
  answer_num integer primary key autoincrement, 
  answer_user string not null,
  answer_text string not null,
  answer_correct integer not null
);