
-- Tables:
-- Content
-- Person
-- Post
-- Comment
-- Tag
-- FriendGroup
-- Member
-- Share


create table if not exists content (
	cid int(10) unsigned not null auto_increment,
	date timestamp default current_timestamp,
	file_path varchar(255) default null,
	name varchar(255) not null,
	is_pub boolean default false, -- default? not null?
	primary key(cid)
);

create table if not exists person (
	uname varchar(64) not null,
	password varchar(255) not null,
	fname varchar(60),
	lname varchar(60),
	primary key(uname)
);

create table if not exists post (
	uname varchar(64) not null,
	cid int(10) unsigned not null,
	primary key(uname, cid),
	foreign key(uname) references person(uname),
	foreign key(cid) references content(cid)
);

create table if not exists comment (
	uname varchar(64) not null,
	cid int(10) unsigned not null,
	timestamp timestamp not null default current_timestamp,
	text longtext default null,
	primary key(uname, cid, timestamp),
	foreign key(uname) references person(uname),
	foreign key(cid) references content(cid)
);

create table if not exists tag (
	uname_tagger varchar(64) not null,
	uname_taggee varchar(64) not null,
	cid int(10) unsigned not null,
	timestamp timestamp default current_timestamp,
	status varchar(64),
	primary key(uname_tagger, uname_taggee, cid),
	foreign key(uname_tagger) references person(uname),
	foreign key(uname_tagger) references person(uname),
	foreign key(cid) references content(cid)
);

create table if not exists friendgroup (
	uname varchar(64) not null,
	gname varchar(64) not null,
	description longtext default null,
	primary key(uname, gname),
	foreign key(uname) references person(uname)
);

create table if not exists member (
	uname_owner varchar(64) not null,
	gname varchar(64) not null,
	uname_member varchar(64) not null,
	primary key(uname_owner, gname, uname_member),
	foreign key(uname_owner, gname) references friendgroup(uname, gname),
	foreign key(uname_member) references person(uname)
);

create table if not exists share (
	cid int(10) unsigned not null,
	uname_owner varchar(64) not null,
	gname varchar(64) not null,
	primary key(cid, uname_owner, gname),
	foreign key(cid) references content(cid),
	foreign key(uname_owner, gname) references friendgroup(uname, gname)
);



