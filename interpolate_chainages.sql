drop view if exists im;

create view IF NOT EXISTS im as

select file
,image_id*5 as ch
--,image_id*5+5 as e_ch
--,start_chainage
--,end_chainage
--,(select pk from corrections where start_chainage<=image_id*5 and corrections.run = images.run order by start_chainage desc limit 1) as left_correction

,(select start_chainage from corrections where start_chainage<=image_id*5 and corrections.run = images.run order by start_chainage desc limit 1) as last_x
,(select end_chainage-start_chainage from corrections where start_chainage<=image_id*5 and corrections.run = images.run order by start_chainage desc limit 1) as last_y
,(select end_offset-start_offset from corrections where start_chainage<=image_id*5 and corrections.run = images.run order by start_chainage desc limit 1) as last_z

,(select start_chainage from corrections where end_chainage>=image_id*5 and corrections.run = images.run order by start_chainage asc limit 1) as next_x
,(select end_chainage-start_chainage from corrections where end_chainage>=image_id*5 and corrections.run = images.run order by start_chainage asc limit 1) as next_y
,(select end_offset-start_offset from corrections where end_chainage>=image_id*5 and corrections.run = images.run order by start_chainage asc limit 1) as next_z

from images;







----f(x) = f(a) + (x - a) * ((f(b) - f(a))/(b-a))
create view IF NOT EXISTS corrected as

select file

,COALESCE(last_y + (ch-last_x) * (next_y-last_y)/(next_x-last_x)
, last_y
,next_y
,0)
as chainage_correction

,COALESCE(last_z + (ch-last_x) * (next_z-last_z)/(next_x-last_x)
, last_y
,next_y
,0)
as offset_correction
from im





select image_id,run,file,start_chainage,end_chainage,MakeLine(pt),min(m),max(m)
from images left join gps on start_chainage <= (select m from gps where pk = next) and end_chainage >= (select m from gps where pk = last)
group by images.pk
order by m








select image_id,run,file,start_chainage,end_chainage,min(m),max(m)
,st_asText(Line_Substring(MakeLine(pt),(start_chainage-min(m))/(max(m)-min(m)),(end_chainage-min(m))/(max(m)-min(m)))) as line
from 
images left join
(select pt,m,lead(m) over (order by m) as next_m,lag(m) over (order by m) as last_m from gps)g
on 
start_chainage<=next_m and end_chainage >= last_m

group by images.pk
order by m