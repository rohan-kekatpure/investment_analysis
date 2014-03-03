drop table if exists profiles;

create table profiles (
	ticker varchar(5),
	family varchar(100),
	sales_load float, 
	net_assets varchar(10),
	prospectus_net_expense_ratio float, 
	gross_expense_ratio float,
	ar_expense_ratio float, 
	inception date, 
	fees_12b1 float,
	turnover float, 
	turnover_cat float
);

copy profiles
from '/Users/rkekatpure/work/code/investing/fund_profiles.csv' 
with csv header delimiter as '|';

-- drop table if exists risk;
-- 
-- create table risk (
-- 	"ticker" varchar(5),
--     "sharpe3" float, 
--     "sharpe5" float,
--     "sharpe10" float,
--     "sharpe3_cat" float, 
--     "sharpe5_cat" float, 
--     "sharpe10_cat" float,
--     "treynor3" float, 
--     "treynor5" float, 
--     "treynor10" float,
--     "treynor3_cat" float, 
--     "treynor5_cat" float, 
--     "treynor10_cat" float,
--     "alpha3" float, 
--     "alpha5" float, 
--     "alpha10" float,
--     "alpha3_cat" float, 
--     "alpha5_cat" float, 
--     "alpha10_cat" float,
-- 	"beta3" float, 
-- 	"beta5" float, 
-- 	"beta10" float,
--     "beta3_cat" float, 
--     "beta5_cat" float, 
--     "beta10_cat" float,
--     "sd3" float, 
--     "sd5" float, 
--     "sd10" float,
--     "sd3_cat" float, 
--     "sd5_cat" float, 
--     "sd10_cat" float
-- );
-- 
-- copy risk
-- from '/Users/rkekatpure/work/code/investing/fund_risk.csv' 
-- with csv header delimiter as '|';
-- 
drop table if exists performance;
create table performance(
	ticker varchar(5), 
	R1 float, 
	R3 float, 
	R5 float, 
	R10 float
);

copy performance
from '/Users/rkekatpure/work/code/investing/fund_performance.csv' 
with csv header delimiter as '|';

-- Start analysis
drop table if exists temp1;
create table temp1 as
select A.net_assets, A.sales_load, A.gross_expense_Ratio, A.turnover,
B.sharpe3, B.sharpe5, B.sharpe10, C.*
from profiles A inner join risk B on A.ticker=B.ticker 
inner join performance C on A.ticker=C.ticker;












