SELECT * 
FROM parks_and_recreation.employee_demographics;


select first_name, last_name, birth_date, age, (age + 10) * 10
from parks_and_recreation.employee_demographics;

select distinct gender, first_name 
from parks_and_recreation.employee_demographics;


select first_name,gender
from parks_and_recreation.employee_demographics
where first_name = 'leslie';

select *
from employee_salary
where salary >= 50000;


select *
from employee_demographics
where gender != "female";


select *
from employee_demographics
where birth_date > "1985-01-01" AND gender = 'male';


select *
from employee_demographics
where first_name like "a___";


select gender, avg(age), count(age)
from employee_demographics
group by gender
;


select *
from employee_demographics
order by gender, age desc
;


select gender, avg(age)
from employee_demographics
group by gender
having avg(age) > 40

;
select occupation, avg(salary)
from employee_salary
where occupation like '%manager%'
group by occupation
having avg(salary) > 70000

;


select *
from employee_demographics
order by age desc
limit 2,1
;

select gender, avg(age) as avg_age
from employee_demographics
group by gender
having avg_age > 40

;


select *
from employee_demographics;

select *
from employee_salary;


select dem.employee_id, age, occupation
from employee_demographics as dem
inner join employee_salary as sal
	on dem.employee_id = sal.employee_id
;

select *
from employee_demographics as dem
right join employee_salary as sal
	on dem.employee_id = sal.employee_id
;

select emp1.employee_id as emp_santa,
emp1.first_name as first_name_santa,
emp1.last_name as last_name_santa,
emp2.employee_id as emp_santa,
emp2.first_name as first_name_santa,
emp2.last_name as last_name_santa
from employee_salary as emp1
join employee_salary as emp2
	on emp1.employee_id  + 1 = emp2.employee_id

;

select *
from employee_demographics;
select *
from employee_salary;

select dem.first_name , dem.last_name, sal.first_name, sal.last_name
from employee_demographics as dem
join employee_salary as sal
	on dem.employee_id + 1 = sal.employee_id

;
select *
from parks_departments

;


select dem.first_name, dem.last_name, sal.occupation, sal.salary, pd.department_name
from employee_demographics as dem
join employee_salary as sal
	on dem.employee_id = sal.employee_id
join parks_departments as pd
	on sal.dept_id = pd.department_id
    
;
    
    
select first_name, last_name, 'old_man' as Label
from employee_demographics
where age > 40 and gender = 'Male'
union
select first_name, last_name, 'old_lady' as Label
from employee_demographics
where age > 40 and gender = 'female'
union 
select first_name, last_name, 'Highly Paid Empolyees' as label
from employee_salary
where salary > 70000

order by first_name, last_name
;


select length('skyline')
;
select first_name, length(first_name)
from employee_demographics
order by 2
;
select lower('SKY')

;

select first_name, upper(first_name)
from employee_demographics

;
select ltrim('      hello       ')

;

select first_name, substring(first_name, 2,3)
from employee_demographics

;

select birth_date, substring(birth_date,6,2) as birth_month
from employee_demographics;
;

select first_name, replace(first_name, 'e', 'a')
from employee_demographics

;

select first_name, last_name, birth_date,
concat(first_name,' ', last_name, 'and the birht date is', birth_date) as full_name
from employee_demographics

;

case statement

select first_name, last_name,
case
	when age <= 30 then 'Young'
    when age between 31 and 50 then 'old'
    when age >=50 then 'death'
end as age_bracket
from employee_demographics
;
pay increase and bounes


select *,
case
	when salary < 50000 then salary + salary*0.05
    when salary > 50000 then salary + salary*0.07
    
end as pay_increase_bounes,
case 
	when department_name = 'Finance' then salary*0.1
end as bounes
from employee_salary
inner join(parks_departments)
on dept_id = department_id
;


subquries

select *
from employee_demographics
where employee_id in 
				(select employee_id 
                 from employee_salary
                 where dept_id = 1)
                 
;

select first_name, salary,
(select avg(salary)
from employee_salary)
from employee_salary


;

select gender, avg(age), max(age), min(age), count(age)
from employee_demographics
group by gender

;

select gender, avg(`max(age)`)
from 
(select gender, avg(age), max(age), min(age), count(age)
from employee_demographics
group by gender) as aggregated_table
group by gender;

window functions

select gender, avg(salary) as avg_salary
from employee_demographics dem
join employee_salary sal
	on dem.employee_id = sal.employee_id
group by gender
;

select dem.first_name, dem.last_name, gender, avg(salary) over(partition by gender)
from employee_demographics dem
join employee_salary sal
	on dem.employee_id = sal.employee_id

;


select dem.first_name, dem.last_name, gender, salary, sum(salary) over(partition by gender order by dem.employee_id) as rolling_total
from employee_demographics dem
join employee_salary sal
	on dem.employee_id = sal.employee_id

;

select dem.employee_id, dem.first_name, dem.last_name, gender, salary, 
row_number() over(partition by gender order by salary desc),

rank () over(partition by gender order by salary desc),
dense_rank () over(partition by gender order by salary desc)
from employee_demographics dem
join employee_salary sal
	on dem.employee_id = sal.employee_id

;

advance --

CTE --

with CTE_example (Gender, avg_sal, max_sal, min_sal, count_sal) as
(
select gender, avg(salary) avg_sal, max(salary) max_sal, min(salary) min_sal, count(salary) count_sal
from employee_demographics dem
join employee_salary sal
	on dem.employee_id = sal.employee_id
group by gender
)
select *
from CTE_example

;


with CTE_example as
(
select employee_id, gender, birth_date
from employee_demographics
where birth_date > '1985-01-01'
),
CTE_example2 as
(
select employee_id, salary
from employee_salary
where salary > 50000
)
select *
from CTE_example
join cte_example2
	on CTE_example.employee_id = cte_example2.employee_id
;


Temporary Tables 

create temporary table temp_table
(
first_name varchar(50),
last_name varchar(50),
favorite_movie varchar (100)

);
select * 
from temp_table;

insert into temp_table
values ('alex', 'freberg', 'lord of the rings');


select *
from employee_salary;

create temporary table salary_over_50k

select *
from employee_salary
where salary >= 50000;

select *
from salary_over_50k;
Stored Procedures


select *
from employee_salary
where salary >= 50000 ;


create procedure large_salaries ()
select *
from employee_salary
where salary >= 50000 ;


call large_salaries();



DELIMITER $$
create procedure large_salaries5 (employee_id_param INT)
begin 
	select salary
    from employee_salary
    where employee_id = employee_id_param
    
    ;
    
end $$
DELIMITER ;

call large_salaries5(1)

;
-- Trigers and Events

select *
from employee_demographics;

select *
from employee_salary;

-- IMPORTAAAANTTTTTTT
DELIMITER $$
create trigger employee_insert
	after insert on employee_salary
    for each row 
    
begin
	 insert into employee_demographics(employee_id, first_name, last_name)
     values (new.employee_id, new.first_name, new.last_name);
     
end $$
DELIMITER ;

insert into employee_salary (employee_id, first_name, last_name, occupation, 
salary, dept_id)
values(13,'Jeanemployee_salaryemployee_salary-Ralphio', 'Saperstein', 'Entertainment 720 CEO', 1000000,null);

select *
from employee_demographics;
select *
from employee_salary;

-- Events (Schedule Automated)
Select *
from employee_demographics;

DELIMITER $$
create event delete_retirees
on schedule every 30 second
DO
begin
	delete
    from employee_demographics
    where age >= 60;



end $$
DELIMITER ;

show variables like 'event%' ;







