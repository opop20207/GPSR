create table if not exists user (
  	user_id integer primary key autoincrement,
  	user_name string not null,
  	user_email string not null,
  	user_pw_hash string not null,
  	user_development bool
);

create table if not exists problem{
	problem_id integer primary key autoincrement 
	problem_name string not null,
	problem_correct integer,
	problem_text string not null,
	problem_pub_data integer
};

create table if not exists follow (
  	follow_who_id integer,
  	follow_whom_id integer
);

create table if not exists board{ 
	board_id integer primary key autoincrement,
	board_name string not null,
	board_text string not null
};