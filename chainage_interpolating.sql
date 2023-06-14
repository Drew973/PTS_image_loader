update images set 

start_chainage =
COALESCE
(last_y + (next_y-last_y) * (x-last_x) / (next_x-last_x),
last_y,
next_y,
x)
,

offset = COALESCE
(last_z + (next_z-last_z) * (x-last_x) / (next_x-last_x),
last_z,
next_z,
0)


from 
(
select pk,
image_id*5 as x,
(select original_chainage from corrections where original_chainage<=image_id*5 and corrections.run=images.run order by original_chainage desc  limit 1 ) as last_x,
(select new_chainage from corrections where original_chainage<=image_id*5 and corrections.run=images.run order by original_chainage desc  limit 1 ) as last_y,
(select offset from corrections where original_chainage<=image_id*5 and corrections.run=images.run order by original_chainage desc  limit 1 ) as last_z,
(select original_chainage from corrections where original_chainage>=image_id*5 and corrections.run=images.run order by original_chainage asc  limit 1 ) as next_x,
(select new_chainage from corrections where original_chainage>=image_id*5 and corrections.run=images.run order by original_chainage asc  limit 1 ) as next_y,
(select offset from corrections where original_chainage>=image_id*5 and corrections.run=images.run order by original_chainage asc  limit 1 ) as next_z
from images
) a

where a.pk=images.pk;



update images set 

end_chainage =
COALESCE
(last_y + (next_y-last_y) * (x-last_x) / (next_x-last_x),
last_y,
next_y,
x)

from 
(
select pk,
image_id*5+5 as x,
(select original_chainage from corrections where original_chainage<=image_id*5+5 and corrections.run=images.run order by original_chainage desc  limit 1 ) as last_x,
(select new_chainage from corrections where original_chainage<=image_id*5+5 and corrections.run=images.run order by original_chainage desc  limit 1 ) as last_y,
(select original_chainage from corrections where original_chainage>=image_id*5+5 and corrections.run=images.run order by original_chainage asc  limit 1 ) as next_x,
(select new_chainage from corrections where original_chainage>=image_id*5+5 and corrections.run=images.run order by original_chainage asc  limit 1 ) as next_y
from images
) a

where a.pk=images.pk;