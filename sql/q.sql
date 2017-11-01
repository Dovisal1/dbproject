
-- Query to find the name of all content that is shared with David

select name
from content natural join share natural join member
where member = 'DD' or is_pub = true;
