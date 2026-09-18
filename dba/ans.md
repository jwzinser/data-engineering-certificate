SHOW max_connections;



\c tolladata
CREATE USER backup_operator WITH PASSWORD 'your_chosen_password';

CREATE ROLE backup;

GRANT CONNECT ON DATABASE tolldata TO backup;

GRANT SELECT ON ALL TABLES IN SCHEMA toll TO backup;

GRANT backup TO backup_operator;


mysql -h localhost -u root -p -e "CREATE DATABASE billing;"

mysql -h localhost -u root -p  < billingdata.sql

mysql -h localhost -u root -p billing -e "SHOW TABLES;"

SELECT
    table_name AS 'Table',
    ROUND((data_length / 1024 / 1024), 2) AS 'Data Size (MB)'
FROM information_schema.tables
WHERE table_schema = 'billing'
AND table_name = 'billdata';


SELECT * FROM billing.billdata WHERE billedamount > 19999;

CREATE INDEX idx_billedamount ON billing.billdata (billedamount);

SELECT * FROM billing.billdata WHERE billedamount > 19999;

SHOW TABLE STATUS FROM billing LIKE 'billdata';

CREATE VIEW basicbilldetails AS
SELECT customerid, month, billedamount
FROM billing.billdata;