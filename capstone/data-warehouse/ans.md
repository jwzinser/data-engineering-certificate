brew services start postgresql

psql -d postgres

-- 1. Create the database (run this while connected to any other db, e.g. postgres)
CREATE DATABASE "Test1";

psql -d Test1;

DROP TABLE IF EXISTS FactSales;
DROP TABLE IF EXISTS DimDate;
DROP TABLE IF EXISTS DimCategory;
DROP TABLE IF EXISTS DimCountry;

CREATE TABLE DimDate (
    DateKey         INT PRIMARY KEY,
    FullDate        DATE NOT NULL,
    Year            SMALLINT NOT NULL,
    QuarterNum      SMALLINT NOT NULL,
    QuarterLabel    VARCHAR(5) NOT NULL,
    Month           SMALLINT NOT NULL,
    MonthName       VARCHAR(20) NOT NULL,
    Day             SMALLINT NOT NULL,
    WeekdayNum      SMALLINT NOT NULL,
    WeekdayName     VARCHAR(20) NOT NULL
);

CREATE TABLE DimCategory (
    CategoryKey     INT PRIMARY KEY,
    CategoryName    VARCHAR(100) NOT NULL
);

CREATE TABLE DimCountry (
    CountryKey      INT PRIMARY KEY,
    CountryName     VARCHAR(100) NOT NULL
);

CREATE TABLE FactSales (
    SalesKey        INT PRIMARY KEY,
    DateKey         INT NOT NULL REFERENCES DimDate(DateKey),
    CountryKey      INT NOT NULL REFERENCES DimCountry(CountryKey),
    CategoryKey     INT NOT NULL REFERENCES DimCategory(CategoryKey),
    SalesAmount     NUMERIC(12,2) NOT NULL
);


psql -d Test1 -c "\copy DimDate FROM '/Users/juanzinser/Documents/projects/data-engineering-certificate/capstone/data-warehouse/DimDate.csv' WITH (FORMAT csv, HEADER true)"
psql -d Test1 -c "\copy DimCategory FROM '/Users/juanzinser/Documents/projects/data-engineering-certificate/capstone/data-warehouse/DimCategory.csv' WITH (FORMAT csv, HEADER true)"
psql -d Test1 -c "\copy DimCountry FROM '/Users/juanzinser/Documents/projects/data-engineering-certificate/capstone/data-warehouse/DimCountry.csv' WITH (FORMAT csv, HEADER true)"
psql -d Test1 -c "\copy FactSales FROM '/Users/juanzinser/Documents/projects/data-engineering-certificate/capstone/data-warehouse/FactSales.csv' WITH (FORMAT csv, HEADER true)"


SELECT
    co.CountryName  AS country,
    ca.CategoryName AS category,
    SUM(f.SalesAmount) AS totalsales
FROM FactSales f
JOIN DimCountry  co ON f.CountryKey  = co.CountryKey
JOIN DimCategory ca ON f.CategoryKey = ca.CategoryKey
GROUP BY GROUPING SETS (
    (co.CountryName, ca.CategoryName),
    (co.CountryName),
    (ca.CategoryName),
    ()
)
ORDER BY country NULLS LAST, category NULLS LAST;

SELECT
    d.Year AS year,
    c.CountryName AS country,
    SUM(f.SalesAmount) AS totalsales
FROM FactSales f
JOIN DimDate d ON f.DateKey = d.DateKey
JOIN DimCountry c ON f.CountryKey = c.CountryKey
GROUP BY ROLLUP (d.Year, c.CountryName)
ORDER BY d.Year, c.CountryName;

SELECT
    d.Year AS year,
    c.CountryName AS country,
    AVG(f.SalesAmount) AS avgsales
FROM FactSales f
JOIN DimDate d ON f.DateKey = d.DateKey
JOIN DimCountry c ON f.CountryKey = c.CountryKey
GROUP BY CUBE (d.Year, c.CountryName)
ORDER BY d.Year, c.CountryName;

CREATE MATERIALIZED VIEW total_sales_per_country AS
SELECT
    c.CountryName AS country,
    SUM(f.SalesAmount) AS total_sales
FROM FactSales f
JOIN DimCountry c ON f.CountryKey = c.CountryKey
GROUP BY c.CountryName;