

insert into person values
('AA', md5('AA'), 'Ann', 'Anderson'),
('BB', md5('BB'), 'Bob', 'Baker'),
('CC', md5('CC'), 'Cathy', 'Chang'),
('DD', md5('DD'), 'David', 'Davidson'),
('EE', md5('EE'), 'Ellen', 'Ellenberg'),
('FF', md5('FF'), 'Fred', 'Fox'),
('GG', md5('GG'), 'Gina', 'Gupta'),
('HH', md5('HH'), 'Helen', 'Harper');

insert  into friendgroup(uname, gname) values
('AA', 'family'),
('BB', 'family'),
('AA', 'besties');

insert into member values
('AA', 'family', 'AA'),
('AA', 'family', 'CC'),
('AA', 'family', 'DD'),
('AA', 'family', 'EE'),
('BB', 'family', 'BB'),
('BB', 'family', 'FF'),
('BB', 'family', 'EE'),
('AA', 'besties', 'AA'),
('AA', 'besties', 'GG'),
('AA', 'besties', 'HH');

insert into content(cid, name) values
(1, 'Whiskers'),
(2, 'My birthday party'),
(3, 'Rover');

insert into post(cid, uname) values
(1, 'AA'),
(2, 'AA'),
(3, 'BB');

insert into share values
(1, 'AA', 'family'),
(2, 'AA', 'besties'),
(3, 'BB', 'family');
