psql -d postgres

Task 1: MyDimDate
dateid
fulldate
day
dayname
weekday
dayofweek
week
month
monthname
quarter
year
isweekend
isholiday

weekday/dayofweek covers the "weekday basis" reporting requirement; month/monthname/year cover monthly and yearly rollups.

Task 2: MyDimWaste
wasteid
wastetype
wastecategory
wastedescription
isrecyclable
unitofmeasure

Task 3: MyDimZone
zoneid
zonename
borough
district
communityboard
zipcode
region
Task 4: MyFactTrips
tripid
dateid
wasteid
zoneid
truckid
numberoftrips
tonscollected
distancetraveled
tripduration


CREATE DATABASE "Project";
\c Project

CREATE TABLE MyDimDate (
    dateid INT PRIMARY KEY,
    date DATE,
    Year INT,
    Quarter INT,
    QuarterName VARCHAR(10),
    Month INT,
    Monthname VARCHAR(20),
    Day INT,
    Weekday INT,
    WeekdayName VARCHAR(20)
);

CREATE TABLE MyDimTruck (
    Truckid INT PRIMARY KEY,
    TruckType VARCHAR(50)
);

CREATE TABLE MyDimStation (
    Stationid INT PRIMARY KEY,
    City VARCHAR(100)
);

CREATE TABLE MyFactTrips (
    Tripid INT PRIMARY KEY,
    Dateid INT REFERENCES MyDimDate(dateid),
    Stationid INT REFERENCES MyDimStation(Stationid),
    Truckid INT REFERENCES MyDimTruck(Truckid),
    Wastecollected NUMERIC(6,2)
);

COPY MyDimDate FROM '/tmp/DimDate.csv' WITH (FORMAT csv, HEADER true);
COPY MyDimTruck FROM '/tmp/DimTruck.csv' WITH (FORMAT csv, HEADER true);
COPY MyDimStation FROM '/tmp/DimStation.csv' WITH (FORMAT csv, HEADER true);
COPY MyFactTrips FROM '/tmp/FactTrips.csv' WITH (FORMAT csv, HEADER true);




SELECT
    ft.stationid,
    dt.trucktype,
    SUM(ft.wastecollected) AS total_waste_collected
FROM MyFactTrips ft
JOIN MyDimTruck dt ON ft.truckid = dt.truckid
GROUP BY GROUPING SETS (
    (ft.stationid),
    (dt.trucktype),
    (ft.stationid, dt.trucktype),
    ()
)
ORDER BY ft.stationid, dt.trucktype;


SELECT
    dd.year,
    ds.city,
    ft.stationid,
    SUM(ft.wastecollected) AS total_waste_collected
FROM MyFactTrips ft
JOIN MyDimDate dd ON ft.dateid = dd.dateid
JOIN MyDimStation ds ON ft.stationid = ds.stationid
GROUP BY ROLLUP (dd.year, ds.city, ft.stationid)
ORDER BY dd.year, ds.city, ft.stationid;

SELECT
    dd.year,
    ds.city,
    ft.stationid,
    AVG(ft.wastecollected) AS avg_waste_collected
FROM MyFactTrips ft
JOIN MyDimDate dd ON ft.dateid = dd.dateid
JOIN MyDimStation ds ON ft.stationid = ds.stationid
GROUP BY CUBE (dd.year, ds.city, ft.stationid)
ORDER BY dd.year, ds.city, ft.stationid;

CREATE MATERIALIZED VIEW max_waste_stats AS
SELECT
    ds.city,
    ft.stationid,
    dt.trucktype,
    MAX(ft.wastecollected) AS max_waste_collected
FROM MyFactTrips ft
JOIN MyDimStation ds ON ft.stationid = ds.stationid
JOIN MyDimTruck dt ON ft.truckid = dt.truckid
GROUP BY ds.city, ft.stationid, dt.trucktype;