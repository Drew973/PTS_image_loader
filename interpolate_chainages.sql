

create view corrections_view as
select corrections.original_chainage as last_original_chainage
,corrections.new_chainage as last_new_chainage
,corrections.new_offset as last_offset
,next_correction.original_chainage as next_original_chainage
,next_correction.new_chainage as next_new_chainage
,next_correction.new_offset as next_offset
from corrections inner join corrections as next_correction on (select pk from corrections as c where c.original_chainage>corrections.original_chainage) = next_correction.pk



select *
,last_new_chainage+(next_new_chainage-last_new_chainage) * (image_id*5 - last_original_chainage) / abs(next_original_chainage-last_original_chainage) as chainage
,last_offset+(next_offset-last_offset) * (image_id*5 - last_original_chainage) / abs(next_original_chainage-last_original_chainage) as offset

from images left join corrections_view on last_original_chainage <= image_id*5 and image_id*5 <= next_original_chainage
order by image_id



--select * from gps

--set line = where start_chainage,end_chainage

--select * from images;
/*
update images set end_chainage = last_new_chainage+(next_new_chainage-last_new_chainage) * (image_id*5+5 - last_original_chainage) / abs(next_original_chainage-last_original_chainage)
    from corrections_view where last_original_chainage <= image_id*5+5 and image_id*5+5 <= next_original_chainage;
	
	
update images set start_chainage = last_new_chainage+(next_new_chainage-last_new_chainage) * (image_id*5 - last_original_chainage) / abs(next_original_chainage-last_original_chainage),
    offset = last_offset+(next_offset-last_offset) * (image_id*5 - last_original_chainage) / abs(next_original_chainage-last_original_chainage)
    from corrections_view where last_original_chainage <= image_id*5 and image_id*5 <= next_original_chainage;

*/
update images set line = ST_OffsetCurve(Line_Substring(ST_LineMerge(gps.line),(start_chainage-min(start_m))/(max(end_m)-min(start_m)),(end_chainage-min(start_m))/(max(end_m)-min(start_m))),offset)
from gps where end_m >= start_chainage and start_m <= end_chainage;


select * from images