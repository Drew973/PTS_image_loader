create view if not exists corrected_lines as
    select c.id,c.m as start_m,next.m as end_m,makeLine(makePointz(st_x(c.pt),st_y(c.pt),c.m),makePointz(st_x(next.pt),st_y(next.pt),next.m)) as line from corrected_points as c
    inner join corrected_points as next 
    on next.id = c.id+1;
	
	
	
	create view if not exists corrected_points as
select id,m,next_id,next_m
,makePoint(
st_x(pt)*t00 + t01*st_y(pt) + t02
,st_x(pt)*t10 + t11*st_y(pt) + t12
,27700) as pt
 from original_points inner join transforms on m >= start_m and m < end_m;




create view if not exists original_lines as
    select c.id,c.m as start_m,next.m as end_m,makeLine(makePointz(st_x(c.pt),st_y(c.pt),c.m),makePointz(st_x(next.pt),st_y(next.pt),next.m)) as line from original_points as c
    inner join original_points as next 
    on next.id = c.id+1;
    
	
	
create view if not exists lines_5 as
    select s,e,makeLine(pt) as line from
    (select cast(id/5.0 as int)*5 as s,cast(id/5.0 as int)*5+5 as e from original_points as e group by s,e)
    inner join original_points on s<=id and id<=e
    group by s
    order by m;




CREATE VIEW if not exists corrected_view as select id,p.m,p.next_m,p.next_id
,makePoint(
st_x(pt) + x_shift + (p.m-c.m)*(next_x_shift-x_shift)/(c.next_m-c.m)
,st_y(pt) + y_shift + (p.m-c.m)*(next_y_shift-y_shift)/(c.next_m-c.m)
,27700) as point
from original_points as p inner join interpolate_corrections as c on c.m < p.m and p.m < c.next_m
union
select id,p.m,p.next_m,p.next_id
,makePoint(st_x(pt)+x_shift,
st_y(pt) + y_shift
,27700)
from 
(select m,x_shift,y_shift from interpolate_corrections order by m limit 1) mi
inner join original_points as p on p.m <= mi.m
union
select id,p.m,p.next_m,p.next_id
,makePoint(st_x(pt)+next_x_shift,
st_y(pt) + next_y_shift
,27700)
from 
(select next_m,next_x_shift,next_y_shift from interpolate_corrections order by m desc limit 1) mi
inner join original_points as p on p.m >= mi.next_m;



create view if not exists interpolate_corrections as
select m,5*(frame_id-line/1250) as next_m
,c.x_shift,c.y_shift
,n.x_shift as next_x_shift,n.y_shift as next_y_shift from
(select 5*(frame_id-line/1250) as m
,lead(pk) over (order by 5*(frame_id-line/1250)) as next
,x_shift
,y_shift
from corrections) c
inner join corrections as n
on n.pk = c.next;


create view if not exists lines_5m as
select frame
,frame * 5 -5 as start_m
,frame * 5 as end_m
,MakeLine(pt) as geom
 from original_points inner join frames
on m >= frame * 5 - 5 and m <= frame * 5
group by frame;


create table if not exists corrections
( 
	pk INTEGER PRIMARY KEY
	,frame_id int not null
	,line int default 0
	,pixel int default 0
	,new_x float
	,new_y float
	,x_shift float
	,y_shift float
);
create index if not exists corrections_frame on corrections(frame_id);


create view if not exists corrections_m as select pk,5.0*(frame_id-line/1250) as m,
4.0*0.5-pixel*4.0/1038 as left_offset,makePoint(new_x,new_y) as pt from corrections;
