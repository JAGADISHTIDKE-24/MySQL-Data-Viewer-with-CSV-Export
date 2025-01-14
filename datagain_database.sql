create database data_gain;
use data_gain;

drop table sample_base;
create table sample_base (
employee_id int(10) primary key,
Employee_name varchar(20),
salary decimal(10,2),
date_of_joining date);

drop table world_population;
drop table sample_base;
drop table countries; 

