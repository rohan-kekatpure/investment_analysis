-- -- --- Create performance table
-- drop table if exists performance;
-- create table performance(
-- 	ticker varchar(5),
-- 	R1 float,
-- 	R3 float,
-- 	R5 float,
-- 	R10 float
-- );

-- --- copy performance
-- from '/Users/rkekatpure/work/code/investing/csv/fund_performance.csv'
-- with csv header delimiter as '|';
--
-- -- --- Create profiles table
-- drop table if exists profiles;
--
-- create table profiles (
-- 	ticker varchar(5),
-- 	family varchar(100),
-- 	sales_load float,
-- 	net_assets float,
-- 	prospectus_net_expense_ratio float,
-- 	gross_expense_ratio float,
-- 	ar_expense_ratio float,
-- 	inception date,
-- 	fees_12b1 float,
-- 	turnover float,
-- 	turnover_cat float
-- );
--
-- copy profiles
-- from '/Users/rkekatpure/work/code/investing/csv/fund_profiles_std.csv'
-- with csv header delimiter as '|';
--
-- -- --- Create risk table
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
-- from '/Users/rkekatpure/work/code/investing/csv/fund_risk_std.csv'
-- with csv header delimiter as '|';


---------------------------------------------------------------------------
-- Load google finance mutual fund data
---------------------------------------------------------------------------

---------------------------------------------------------------------------
-- profiles
---------------------------------------------------------------------------
drop table if exists gfnc_profiles;
create table gfnc_profiles (
  ticker varchar(5),
  total_assets float,
  front_load float,
  deferred_load float,
  expense_ratio float,
  management_fees float,
  fund_family varchar(50),
  pct_cash float,
  pct_stocks float,
  pct_bonds float,
  pct_preferred float ,
  pct_convertible float,
  pct_other float
);
copy gfnc_profiles
from '/Users/rkekatpure/work/code/investing/csv/gfnc_profile.csv'
with csv header delimiter as '|';

---------------------------------------------------------------------------
-- performance
---------------------------------------------------------------------------
drop table if exists gfnc_performance;
create table gfnc_performance (
  ticker varchar(5),
  r1d float,
  r1w float,
  r4w float,
  r3m float,
  rytd float,
  r1y float,
  r3y float,
  r5y float
);
copy gfnc_performance
from '/Users/rkekatpure/work/code/investing/csv/gfnc_performance.csv'
with csv header delimiter as '|';

---------------------------------------------------------------------------
-- performance
---------------------------------------------------------------------------
drop table if exists gfnc_risk;
create table gfnc_risk (
  ticker varchar(5),
  alpha1 float,
  alpha3 float,
  alpha5 float,
  alpha10 float,
  beta1 float,
  beta3 float,
  beta5 float,
  beta10 float,
  MAR1 float,
  MAR3 float,
  MAR5 float,
  MAR10 float,
  R2_1 float,
  R2_3 float,
  R2_5 float,
  R2_10 float,
  SD1 float,
  SD3 float,
  SD5 float,
  SD10 float,
  sharpe1 float,
  sharpe3 float,
  sharpe5 float,
  sharpe10 float
);
copy gfnc_risk
from '/Users/rkekatpure/work/code/investing/csv/gfnc_risk.csv'
with csv header delimiter as '|';


-- Start analysis
-- drop table if exists temp1;
-- create table temp1 as
-- select A.*,
-- B.sharpe3, B.sharpe5, B.sharpe10, C.r1, C.r3, C.r5, C.r10
-- from profiles A
-- inner join risk B on A.ticker=B.ticker
-- inner join performance C on A.ticker=C.ticker;












