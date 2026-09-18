


CREATE DATABASE sales;

USE sales;

CREATE TABLE sales_data(product_id INT,
customer_id INT,
price FLOAT,
quantity INT,
timestamp DATETIME);

SELECT count(*) from sales_data;


CREATE INDEX ts ON sales_data (timestamp);

SHOW INDEX FROM sales_data;