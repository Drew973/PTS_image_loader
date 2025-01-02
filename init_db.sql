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


create view if not exists images_view as
select pk,original_file,image_type,frame_id
,(select number from runs_view where start_frame<=frame_id and end_frame >= frame_id order by number limit 1) as run
from images;


create table if not exists original_points
(
	id INTEGER PRIMARY KEY
	,m INTEGER UNIQUE
	,next_id int
	,next_m float
);
--SELECT AddGeometryColumn('original_points' , 'pt', 4326, 'POINT', 'XY');--wgs84
SELECT AddGeometryColumn('original_points' , 'pt', 4326, 'POINT', 'XYZ');--wgs84
create index if not exists original_points_m on original_points(m);


create table if not exists frames
(
	id int primary key
);
create view load_gps_view as select id,GROUP_CONCAT(number) as runs from frames left join runs_view on start_frame <= id and id <= end_frame group by id;

drop table if exists pos;
create table if not exists pos (pixel float,line float);
insert into pos (pixel,line) values (519,0),(519,625),(519,1250),(516,200),(525,400);


create table if not exists cracks
(
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


--SELECT AddGeometryColumn('transverse_joints' , 'geom', 0, 'Linestring', 'XY');
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


--SELECT AddGeometryColumn('transverse_joint_faulting' , 'geom', 4326, 'POLYGON', 'XY');
--x coord is chainage , y is offset.

create view if not exists faulting_view as
select frame,joint_id,joint_offset,faulting,width,geom,mo_wkb,chainage_shift,runs_view.offset as left_offset from transverse_joint_faulting
inner join runs_view on start_frame <= frame and end_frame >= frame;