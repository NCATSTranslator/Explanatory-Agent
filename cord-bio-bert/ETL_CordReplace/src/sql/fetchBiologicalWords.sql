with distinct_proteins as (
	select distinct name, type from biological_words
    where type = 'protein'
), distinct_chemicals as (
	select distinct name, type from biological_words
    where type = 'chemical'
), distinct_diseases as (
	select distinct name, type from biological_words
    where type = 'disease'
), distinct_words as (

	select name, type from distinct_proteins
	where name not in (select name from distinct_chemicals) and name not in (select name from distinct_diseases)
	union
	select name, type from distinct_chemicals
	where name not in (select name from distinct_proteins) and name not in (select name from distinct_diseases)
	union
	select name, type from distinct_diseases
	where name not in (select name from distinct_chemicals) and name not in (select name from distinct_proteins)
)

select name, reverse(type) as type_reversed from distinct_words
where length(name) > 2;