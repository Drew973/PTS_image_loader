
create table if not exists transforms
(
	start_m float
	,end_m float
	,t00 float default 1.0-- x scale
	,t01 float default 0.0 --rotation
	,t02 float-- x shift
	,t10 float default 0.0 -- rotation
	,t11 float default 1.0 -- y scale
	,t12 float -- y shift
	);
	
create index if not exists start_m_ind on transforms(start_m);
create index if not exists end_m_ind on transforms(end_m);



/*

create view if not exists corrected_points as 
select 
,m
,st_x(pt)*t00 + t01*st_y(pt) + t02
,st_x(pt)*t10 + t11*st_y(pt) + t12
from transforms inner join original_points on m >= start_m and end_m > m
;
*/


