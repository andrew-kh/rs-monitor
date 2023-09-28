-- Active: 1672421927448@@localhost@5432
select
	(split_part(ad_json->>'property_price', ',',1)::float)*1000 price,
	((split_part(ad_json->>'property_price', ',',1)::float)*1000)
	/
	replace(ad_json->'property_info'->>'Kvadratura', 'm2', '')::float price_per_sq_m
from dev.ads_demo
where 1=1
	and source_directory_id is not null



select
	ad_json->>'property_district',
	sum(split_part(ad_json->>'property_price', ',',1)::float)/count(ad_json->>'property_district') av_price,
	sum(((split_part(ad_json->>'property_price', ',',1)::float)*1000)
	/
	replace(ad_json->'property_info'->>'Kvadratura', 'm2', '')::float)/count(ad_json->>'property_district') av_price_per_sq_m
from dev.ads_demo
where 1=1
	and source_directory_id is not null
group by 1
order by 3 desc