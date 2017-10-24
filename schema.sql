
-- Tables:
-- Content
-- Person
-- Post
-- Comment
-- Tag
-- FriendGroup
-- Member
-- Share

create table content (
	id integer not null auto increment,
	date timestamp default current_timestamp,
	is_pub boolean, -- default? not null?
	primary key(id)
);

create table person (
	uname varchar not null,
	password varchar,
	fname varchar,
	lname varchar,
	primary key(uname)
);

create table post (
	uname varchar not null,
	id integer not null,
	primary key(uname, id),
	foreign key(uname) references person(uname),
	foreign key(id) references content(id)
);

create table comment (
	uname varchar not null,
	id integer not null,
	timestamp date not null default current_timestamp,
	text,
	primary key(uname, id, timestamp),
	foreign key(uname) references person(uname),
	foreign key(id) references content(id)
);

create table tag (
	tagger varchar not null,
	taggee varchar not null,
	id integer not null,
	timestamp date default current_timestamp,
	status varchar, --default?
	primary key(tagger, taggee, id),
	foreign key(tagger) references person(uname),
	foreign key(tagger) references person(uname),
	foreign key(id) references content(id)
);

create table friendgroup (
	uname varchar not null,
	name not null,
	description varchar,
	primary key(uname, name),
	foreign key(uname) references person(uname)
);

create table member (
	owner varchar not null,
	group_name varchar not null,
	group_member varchar not null,
	primary key(owner, group_name, group_member),
	foreign key(owner, group_name) references friendgroup(uname, name),
	foreign key(group_member) references person(uname)
);

create table share (
	owner varchar not null,
	group_name varchar not null,
	c_id integer not null,
	primary key(owner, group_name, c_id),
	foreign key(owner, group_name) references friendgroup(uname, name),
	foreign key(c_id) references content(id)
);



