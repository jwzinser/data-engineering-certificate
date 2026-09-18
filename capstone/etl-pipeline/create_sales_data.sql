DROP TABLE IF EXISTS sales_data;

CREATE TABLE sales_data (
    rowid           INT PRIMARY KEY,
    product_id      INT NOT NULL,
    customer_id     INT NOT NULL,
    price           DECIMAL DEFAULT 0.0 NOT NULL,
    quantity         INT NOT NULL,
    timeestamp       TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
