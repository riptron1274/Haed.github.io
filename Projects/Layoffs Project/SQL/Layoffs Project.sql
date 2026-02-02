-- Data Cleaning

select *
from layoffs;

-- 1. remove duplicates
-- 2. standardize the data
-- 3. null values and black values
-- 4. remove any rows and columns


-- remove duplicates

create table layoffs_staging
like layoffs;

select * 
from layoffs_staging;

insert layoffs_staging
select *
from layoffs;

select *,
row_number() over(
partition by company, industry, total_laid_off, percentage_laid_off, `date`
) as num_row
from layoffs_staging;


with duplicate_cte as 
(
select *,
row_number() over(
partition by company, location, industry, total_laid_off, percentage_laid_off,
`date`, stage, country, funds_raised_millions
) as num_row
from layoffs_staging
)
select *
from duplicate_cte
where num_row > 1;

select *
from layoffs_staging
where company = 'casper';

-- removing
with duplicate_cte as 
(
select *,
row_number() over(
partition by company, location, industry, total_laid_off, percentage_laid_off,
`date`, stage, country, funds_raised_millions
) as num_row
from layoffs_staging
)
delete
from duplicate_cte
where num_row > 1;

CREATE TABLE `layoffs_staging2` (
  `company` text,
  `location` text,
  `industry` text,
  `total_laid_off` int DEFAULT NULL,
  `percentage_laid_off` text,
  `date` text,
  `stage` text,
  `country` text,
  `funds_raised_millions` int DEFAULT NULL,
  `row_num` INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

select *
from layoffs_staging2;

insert into layoffs_staging2
select *,
row_number() over(
partition by company, location, industry, total_laid_off,
percentage_laid_off, `date`, stage, country, funds_raised_millions
) as num_row
from layoffs_staging;

select *
from layoffs_staging2;

-- Standardizing data

select company, trim(company)
from layoffs_staging2
;

update layoffs_staging2
set company = trim(company);

select *
from layoffs_staging2
where industry like 'crypto%'
;

update layoffs_staging2
set industry = 'Crypto'
where industry like 'crypto%';

select distinct industry
from layoffs_staging2;

select distinct country
from layoffs_staging2
order by 1;

UPDATE layoffs_staging2
SET country = 'United State'
WHERE trim(country) like 'United State.';

select distinct country
from layoffs_staging2
order by 1;

select distinct country, length(country)
from layoffs_staging2
where country like 'United State%';

UPDATE layoffs_staging2
SET country = TRIM(REPLACE(country, '.', ''))
WHERE TRIM(country) LIKE 'United State%';



update layoffs_staging2
set country = trim(replace(country, '.', ''))
where trim(country) like 'United State%';

SELECT DISTINCT country
FROM layoffs_staging2
WHERE country LIKE 'United State%';


select `date`,
str_to_date(`date`, '%m/%d/%Y') as date_changed
from layoffs_staging2;

update layoffs_staging2
set `date` = str_to_date(`date`, '%m/%d/%Y');

alter table layoffs_staging2
modify column `date` date;

select * 
from layoffs_staging2
where total_laid_off is null 
and percentage_laid_off is null;



select *
from layoffs_staging2
where industry is null
or industry = '';

select *
from layoffs_staging2
where company = 'Airbnb';


select t1.industry, t2.industry
from layoffs_staging2 t1
join layoffs_staging2 t2
	on t1.company = t2.company
    and t1.location = t2.location
		
where (t1.industry is null or t1.industry = '')
and t2.industry is not null;

update layoffs_staging2
set industry = null
where industry = '';


update layoffs_staging2 t1
join layoffs_staging2 t2
	on t1.company = t2.company
set t1.industry = t2.industry
where t1.industry is null
and t2.industry is not null;


select *
from layoffs_staging2
where industry is null
or industry = '';



select *
from layoffs_staging2
where total_laid_off is null
and percentage_laid_off is null
;


delete 
from layoffs_staging2
where total_laid_off is null
and percentage_laid_off is null
;


select *
from layoffs_staging2;

alter table layoffs_staging2
drop column row_num;


-- Data Cleaned

-- Exploratiry Data Analysis

Select *
from layoffs_staging2
where percentage_laid_off = 1
order by funds_raised_millions desc;


Select max(total_laid_off), max(percentage_laid_off)
from layoffs_staging2;

Select company, sum(total_laid_off)
from layoffs_staging2
group by company
order by 2 desc;

select min(`date`), max(`date`)
from layoffs_staging2;

Select industry, sum(total_laid_off)
from layoffs_staging2
group by industry
order by 2 desc;


--

select substring(`date`, 1 ,7) as `month`, sum(total_laid_off)
from layoffs_staging2
where substring(`date`, 1 ,7)  is not null
group by 1
order by 1 
;

with rolling_total as 
(
select substring(`date`, 1 ,7) as `MONTH`, sum(total_laid_off) as total_off
from layoffs_staging2
where substring(`date`, 1 ,7)  is not null
group by `MONTH`
order by 1 asc 
)
select `MONTH`, total_off,
sum(total_off) over (order by `month`) as rolling_total
from rolling_total;



Select company, sum(total_laid_off)
from layoffs_staging2
group by company
order by 2 desc;

Select company, year(`date`), sum(total_laid_off)
from layoffs_staging2
group by company, year(`date`)
order by 3 desc
;

with Company_year (company, years, total_laid_off) as
(
Select company, year(`date`), sum(total_laid_off)
from layoffs_staging2
group by company, year(`date`)
), Company_year_rank as 
(select *, 
dense_rank() over (partition by  years order by total_laid_off desc) as ranking
from Company_year
where years is not null
)
select *
from Company_year_rank
where ranking <=5
;



























