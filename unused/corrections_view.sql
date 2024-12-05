
drop view if exists corrections_view;

create view if not exists corrections_view as
select m
,a.run

,coalesce(
--prev.y + (x-prev.x)*(next.y-prev.y)/(next.x - prev.x)
prev.new_offset - prev.original_offset + (m-prev.original_chainage)*(next.offset_shift - prev.offset_shift)/(next.original_chainage-prev.original_chainage)
,next.offset_shift
,prev.offset_shift
,0) as offset_diff

,coalesce(
--prev.y + (x-prev.x)*(next.y-prev.y)/(next.x - prev.x)
prev.chainage_shift + (m-prev.original_chainage)*(next.chainage_shift - prev.chainage_shift)/(next.original_chainage-prev.original_chainage)
,next.chainage_shift
,prev.chainage_shift
,0) as chainage_diff


from
(
select run,image_id*5 as m from images where marked
union select run,image_id*5+5 from images where marked
) a

left join corrections as prev on prev.pk = (select pk from corrections where corrections.run=a.run and original_chainage<=m order by original_chainage desc limit 1)
left join corrections as next on next.pk = (select pk from corrections where corrections.run=a.run and original_chainage>=m order by original_chainage asc limit 1)

;



drop view if exists images2;

create view if not exists images2 as
select origonal_file as original_file
,image_id*5
,image_id*5+s.chainage_diff as start_m
,image_id*5+5+e.chainage_diff as end_m
,s.offset_diff as left_offset
 from images 
inner join corrections_view as s
on marked and images.run = s.run and image_id*5 = s.m
inner join corrections_view as e
on marked and images.run = e.run and image_id*5+5 = e.m
;

drop view if exists images_view;


--line from min(gps.start_m to max(gps.end_m)
create view images_view as
select original_file,
ST_OffsetCurve(ST_Line_Substring(ST_LineMerge(ST_Collect(line))
,case when images2.start_m > min(gps.start_m) then (images2.start_m - min(gps.start_m))/abs(max(gps.end_m)-min(gps.start_m)) else 0
end
,case when max(gps.end_m)>images2.end_m then (images2.end_m - min(gps.start_m))/abs(max(gps.end_m)-min(gps.start_m)) else 1 end
),left_offset
)
 as line

from images2 left join gps on gps.end_m>images2.start_m and gps.start_m<images2.end_m group by original_file order by gps.start_m

;
	


select original_file,st_length(line),* from images_view