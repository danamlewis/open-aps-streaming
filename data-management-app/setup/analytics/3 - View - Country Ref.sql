-----------------------------------------

--Create View: Country Ref

-----------------------------------------
-----------------------------------------

--Last Modified: 11/7/2019
--Written By: Matthew Taylor
--Create a view to make corrections to country entries

--Parent tables/views:
--openaps.member_demographics (table)
-----------------------------------------
-----------------------------------------

create view openaps.country_ref
as(
select 
	replace(lower(country),'the ','') as country_original
	,case
		when replace(lower(country),'the ','') = 'uk' then 'united kingdom'
		when replace(lower(country),'the ','') = 'us' then 'united states of america'
		when replace(lower(country),'the ','') like 'u.s.a%' then 'united states of america'
		when replace(lower(country),'the ','') = 'usa' then 'united states of america'
		when replace(lower(country),'the ','') = 'united states' then 'united states of america'
		when replace(lower(country),'the ','') = 'espa�a' then 'spain'
		when replace(lower(country),'the ','') = 'italia' then 'italy'
		when replace(lower(country),'the ','') = '' then 'not available'
		else replace(lower(country),'the ','')
	end as country_corrected

from openaps.member_demographics

group by 1,2
)
;

GRANT SELECT ON openaps.country_ref TO viewer;
GRANT SELECT ON openaps.country_ref TO admin_viewer;