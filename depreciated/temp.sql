# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 14:00:35 2023

@author: Drew.Bennett
"""


create view if not exists lines_view as
select points.m as start_m
,points2.m as end_m
,makeline(makePointM(points.x,points.y,points.m),makePointM(points2.x,points2.y,points2.m)) as line
,makeline(makePointM(points.corrected_x,points.corrected_y,points.m),makePointM(points2.corrected_x,points2.corrected_y,points2.m)) as corrected_line
,points.corrected_x as corrected_start_x
,points.corrected_y as corrected_start_y
from points inner join points as points2
on points2.pk = points.next_pk;

create view if not exists corrections_view as
select pk,run,chainage,new_x,new_y,x_offset,y_offset
,st_x(Line_Interpolate_Point(corrected_line,(chainage-start_m)/(end_m-start_m))) + x_offset as current_x
,st_y(Line_Interpolate_Point(corrected_line,(chainage-start_m)/(end_m-start_m))) + y_offset as current_y
,new_x-st_x(Line_Interpolate_Point(line,(chainage-start_m)/(end_m-start_m))) - x_offset as x_shift
,new_y - st_y(Line_Interpolate_Point(line,(chainage-start_m)/(end_m-start_m))) - y_offset as y_shift
from corrections left join lines_view on start_m <= chainage and chainage < end_m;

create view if not exists cv as
select chainage,x_shift,y_shift 
,lead(chainage) over (order by chainage) as next_ch
,lag(chainage) over (order by chainage) as last_ch
,lead(x_shift) over (order by chainage) as next_xs
,lead(y_shift) over (order by chainage) as next_ys
from corrections_view;

create view if not exists points_view as
select pk
,m
,COALESCE(x+x_shift+(next_xs-x_shift)*(m-chainage)/(next_ch-chainage),x+x_shift,x) as corrected_x
,COALESCE(y+y_shift+(next_ys-y_shift)*(m-chainage)/(next_ch-chainage),y+y_shift,y) as corrected_y
from points left join cv on chainage<m and m<next_ch
or next_ch is null and m>=chainage
or last_ch is null and m<=chainage
;

create view if not exists images_view as
select original_file,
image_id,
makeLine(MakePointM(corrected_x,corrected_y,m)) as center_line
from images
inner join points_view on marked and image_id*5<=m and m<=image_id*5+5
group by original_file
order by m;

create view if not exists center_lines as
select image_id,MakeLine(makePoint(corrected_x,corrected_y)) as center_line from
(select cast(floor(m/5) as int) as image_id from points group by cast(floor(m/5) as int) order by m)
inner join points on image_id*5 <= cast(m as int) and cast(m as int) <= image_id *5 +5
group by image_id order by m;

