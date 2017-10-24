
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
	date timestamp not null default current_timestamp,
	primary key(id)
);
