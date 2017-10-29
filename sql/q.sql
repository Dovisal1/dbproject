

select name
from content natural join share natural join member
where uname_member = 'DD' or is_pub = true;
