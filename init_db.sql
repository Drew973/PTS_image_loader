    SELECT InitSpatialMetaData();
    
  create table if not exists runs
    (
    	pk INTEGER PRIMARY KEY
    	,start_frame int default 0
    	,end_frame int default 0
        ,correction_start_m float default 0.0
        ,correction_end_m float default 0.0
        ,correction_start_offset float default 0.0
        ,correction_end_offset float default 0.0
    );
	
    create view if not exists runs_view as select ROW_NUMBER() over (order by start_frame,end_frame) as number,pk
    ,start_frame,end_frame,correction_start_m,correction_end_m,correction_start_offset,correction_end_offset
    ,correction_end_m - correction_start_m as chainage_shift,correction_end_offset - correction_start_offset as offset
    from runs;
    
   create table if not exists images
            ( 
                pk INTEGER PRIMARY KEY
                ,frame_id INTEGER
                ,original_file text unique
                ,image_type text
             );
      
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

create view if not exists images_view as
select pk,original_file,image_type,frame_id
,(select number from runs_view where start_frame<=frame_id and end_frame >= frame_id order by number limit 1) as run
from images;
            
create table if not exists original_points(
    		id INTEGER PRIMARY KEY
            ,m INTEGER UNIQUE
            ,next_id int
            ,next_m float
            );
 
SELECT AddGeometryColumn('original_points' , 'pt', 27700, 'POINT', 'XY');
create index if not exists original_points_m on original_points(m);


create view if not exists corrected_points as
select id,m,next_id,next_m
,makePoint(
st_x(pt)*t00 + t01*st_y(pt) + t02
,st_x(pt)*t10 + t11*st_y(pt) + t12
,27700) as pt
 from original_points inner join transforms on m >= start_m and m < end_m;


drop table if exists pos;
create table if not exists pos (pixel float,line float);
insert into pos (pixel,line) values (519,0),(519,625),(519,1250),(516,200),(525,400);

   create view if not exists original_lines as
    select c.id,c.m as start_m,next.m as end_m,makeLine(makePointz(st_x(c.pt),st_y(c.pt),c.m),makePointz(st_x(next.pt),st_y(next.pt),next.m)) as line from original_points as c
    inner join original_points as next 
    on next.id = c.id+1;
    
   create view if not exists corrected_lines as
    select c.id,c.m as start_m,next.m as end_m,makeLine(makePointz(st_x(c.pt),st_y(c.pt),c.m),makePointz(st_x(next.pt),st_y(next.pt),next.m)) as line from corrected_points as c
    inner join corrected_points as next 
    on next.id = c.id+1;
    
    create view if not exists lines_5 as
    select s,e,makeLine(pt) as line from
    (select cast(id/5.0 as int)*5 as s,cast(id/5.0 as int)*5+5 as e from original_points as e group by s,e)
    inner join original_points on s<=id and id<=e
    group by s
    order by m;
    
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

create view if not exists frames as
select cast(m/5 as int) as frame from original_points 
group by cast(m/5 as int);


create view if not exists lines_5m as
select frame
,frame * 5 -5 as start_m
,frame * 5 as end_m
,MakeLine(pt) as geom
 from original_points inner join frames
on m >= frame * 5 - 5 and m <= frame * 5
group by frame;



create table if not exists cracks(
section_id int
,crack_id int
,len float
,depth float
,width float
,unique(section_id,crack_id)
);

create index if not exists section_id_ind on cracks(section_id);

SELECT AddGeometryColumn('cracks' , 'geom', 0, 'Linestring', 'XY');
--x coord is chainage , y is offset.

create view if not exists cracks_view as
select section_id,crack_id,len,depth,width,geom,chainage_shift,offset
from cracks inner join runs_view on start_frame <= section_id and end_frame >= section_id;


create table if not exists rut(
pk INTEGER primary key
,frame int
,chainage float
,wheelpath text
,depth float
,width float
,x_section float
,type INT
,deform float
,mo_wkb blob
,unique(frame,chainage,wheelpath)
);
create index if not exists frame_ind on rut(frame);

SELECT AddGeometryColumn('rut' , 'geom', 27700, 'POLYGON', 'XY');


drop view if exists rut_view;
create view if not exists rut_view as
select rut.pk as pk,frame,chainage,wheelpath,depth,width,type,deform,x_section,mo_wkb,geom,chainage_shift,offset
from rut inner join runs_view on start_frame <= frame and end_frame >= frame;





create table if not exists joints(
frame int
,joint_id int
,off float
,faulting int
,width float
,mo_wkb blob
,unique(frame,joint_id)
);

create index if not exists section_id_ind on joints(joint_id);

SELECT AddGeometryColumn('joints' , 'geom', 0, 'POLYGON', 'XY');
--x coord is chainage , y is offset.



create table if not exists transverse_joints(
frame int
,joint_id int
,length float
,average_depth_bad_seal float
,average_depth_good_seal float
,min_depth_seal float
,max_depth_seal float
,mo_wkb blob
,unique(frame,joint_id)
);


SELECT AddGeometryColumn('transverse_joints' , 'geom', 0, 'Linestring', 'XY');
--x coord is chainage , y is offset.




create table if not exists transverse_joint_faulting(
frame int
,joint_id int
,joint_offset int
,faulting float
,width float
,mo_wkb blob
,PRIMARY KEY (frame,joint_id,joint_offset)
);


SELECT AddGeometryColumn('transverse_joint_faulting' , 'geom', 27700, 'POLYGON', 'XY');
--x coord is chainage , y is offset.

create view if not exists faulting_view as
select frame,joint_id,joint_offset,faulting,width,geom,mo_wkb,chainage_shift,runs_view.offset as left_offset from transverse_joint_faulting
inner join runs_view on start_frame <= frame and end_frame >= frame;