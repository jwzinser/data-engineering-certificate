## Section 1 — Entities & Business Rules
### Entities Modeled
This covers all six required areas (transactions, line items, products, category/type, staff, locations), split as seven physical tables since category and type are kept separate for proper normalization.
### Business Rules
Each sales transaction is processed by exactly one staff member, at exactly one location.
Each transaction has one or more line items (sales_detail rows); every line item belongs to exactly one transaction.
Each line item references exactly one product; a product may appear on many line items across many transactions.
Each product belongs to exactly one product type, and each product type belongs to exactly one category (no product is left uncategorized).
Each staff member is assigned to exactly one home location; a location may have many staff members.
Quantity and unit price on a line item must be positive values, and a transaction's total amount must be non-negative — invalid/negative sales data is rejected at the database level.

## Section 2 — Normalized Logical Schema (3NF)


### `location`
| Column | Type | Constraint |
|---|---|---|
| `location_id` | INT | **PK** |
| `location_name` | VARCHAR(100) | NOT NULL |
| `address` | VARCHAR(150) | NOT NULL |
| `city` | VARCHAR(50) | NOT NULL |
| `state` | VARCHAR(20) | NOT NULL |


### `staff`
| Column | Type | Constraint |
|---|---|---|
| `staff_id` | INT | **PK** |
| `staff_name` | VARCHAR(100) | NOT NULL |
| `position` | VARCHAR(50) | |
| `location_id` | INT | **FK** → `location.location_id`, NOT NULL |


### `product_category`
| Column | Type | Constraint |
|---|---|---|
| `category_id` | INT | **PK** |
| `category_name` | VARCHAR(50) | NOT NULL, UNIQUE |


### `product_type`
| Column | Type | Constraint |
|---|---|---|
| `type_id` | INT | **PK** |
| `type_name` | VARCHAR(50) | NOT NULL |
| `category_id` | INT | **FK** → `product_category.category_id`, NOT NULL |


### `product`
| Column | Type | Constraint |
|---|---|---|
| `product_id` | INT | **PK** |
| `product` | VARCHAR(100) | NOT NULL |
| `description` | TEXT | |
| `price` | DECIMAL(10,2) | NOT NULL, CHECK (price >= 0) |
| `type_id` | INT | **FK** → `product_type.type_id`, NOT NULL |


### `sales_transaction`
| Column | Type | Constraint |
|---|---|---|
| `transaction_id` | INT | **PK** |
| `transaction_timestamp` | TIMESTAMP | NOT NULL |
| `staff_id` | INT | **FK** → `staff.staff_id`, NOT NULL |
| `location_id` | INT | **FK** → `location.location_id`, NOT NULL |
| `payment_method` | VARCHAR(20) | NOT NULL, CHECK (payment_method IN ('cash','credit','debit','mobile')) |
| `total_amount` | DECIMAL(10,2) | NOT NULL, CHECK (total_amount >= 0) |


### `sales_detail`
| Column | Type | Constraint |
|---|---|---|
| `sales_detail_id` | INT | **PK** |
| `transaction_id` | INT | **FK** → `sales_transaction.transaction_id`, NOT NULL |
| `product_id` | INT | **FK** → `product.product_id`, NOT NULL |
| `line_number` | INT | NOT NULL |
| `quantity` | INT | NOT NULL, CHECK (quantity > 0) |
| `unit_price` | DECIMAL(10,2) | NOT NULL, CHECK (unit_price >= 0) |
| | | UNIQUE (`transaction_id`, `line_number`) |




## Section 3 — Relationship Definitions
- sales_detail ↔ sales_transaction — One-to-many. One sales_transaction has one or more sales_detail rows. The FK lives on the "many" side: sales_detail.transaction_id references sales_transaction.transaction_id. NOT NULL on this FK guarantees no orphan line items; guaranteeing "at least one" line item per transaction is a rule enforced at the application/insert-transaction level, since standard FK constraints can't require a minimum child-row count.
- sales_detail ↔ product — Many-to-one. Many line items across many transactions can reference the same product. FK: sales_detail.product_id → product.product_id. unit_price is stored on sales_detail (not just looked up from product.price) intentionally, to preserve the historical price at time of sale even if the product's list price later changes.
- product ↔ product_type (and product_type ↔ product_category) — Many-to-one at each level. Many products share one type; many types share one category. FKs: product.type_id → product_type.type_id, and product_type.category_id → product_category.category_id. This is a two-level normalized hierarchy rather than storing category/type text directly on product.
- Staff-locations report relationship — staff ↔ location is many-to-one: many staff share one home location. FK: staff.location_id → location.location_id. This single relationship is sufficient to answer "which staff work at which location" via a simple join, which is exactly what staff_locations_view implements below.


## Section 4 SQL Implementation
```sql
CREATE TABLE location (
    location_id   INT PRIMARY KEY,
    location_name VARCHAR(100) NOT NULL,
    address       VARCHAR(150) NOT NULL,
    city          VARCHAR(50) NOT NULL,
    state         VARCHAR(20) NOT NULL
);


CREATE TABLE staff (
    staff_id    INT PRIMARY KEY,
    staff_name  VARCHAR(100) NOT NULL,
    position    VARCHAR(50),
    location_id INT NOT NULL REFERENCES location(location_id)
);


CREATE TABLE product_category (
    category_id   INT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE
);


CREATE TABLE product_type (
    type_id     INT PRIMARY KEY,
    type_name   VARCHAR(50) NOT NULL,
    category_id INT NOT NULL REFERENCES product_category(category_id)
);


CREATE TABLE product (
    product_id  INT PRIMARY KEY,
    product     VARCHAR(100) NOT NULL,
    description TEXT,
    price       DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    type_id     INT NOT NULL REFERENCES product_type(type_id)
);


CREATE TABLE sales_transaction (
    transaction_id         INT PRIMARY KEY,
    transaction_timestamp  TIMESTAMP NOT NULL,
    staff_id               INT NOT NULL REFERENCES staff(staff_id),
    location_id            INT NOT NULL REFERENCES location(location_id),
    payment_method         VARCHAR(20) NOT NULL
        CHECK (payment_method IN ('cash','credit','debit','mobile')),
    total_amount           DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0)
);


CREATE TABLE sales_detail (
    sales_detail_id INT PRIMARY KEY,
    transaction_id  INT NOT NULL REFERENCES sales_transaction(transaction_id),
    product_id      INT NOT NULL REFERENCES product(product_id),
    line_number     INT NOT NULL,
    quantity        INT NOT NULL CHECK (quantity > 0),
    unit_price      DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    UNIQUE (transaction_id, line_number)
);


CREATE VIEW staff_locations_view AS
SELECT
    s.staff_id,
    s.staff_name,
    l.location_name,
    l.address,
    l.city,
    l.state
FROM staff s
JOIN location l ON s.location_id = l.location_id;

CREATE MATERIALIZED VIEW product_info_mview AS
SELECT
    p.product_id,
    p.product AS product_name,
    pc.category_name,
    pt.type_name,
    p.price
FROM product p
JOIN product_type pt ON p.type_id = pt.type_id
JOIN product_category pc ON pt.category_id = pc.category_id;
```


### 4. Explanation
- Normalization choice: splitting product_category and product_type into their own tables, rather than storing category/type as free-text columns on product, eliminates update anomalies — renaming a category (e.g., "Coffee beans" → "Coffee Beans") now requires changing one row instead of every product row that used that text, and it prevents inconsistent spellings from creeping into the data over time.
- Integrity constraint: the CHECK (quantity > 0) and CHECK (unit_price >= 0) constraints on sales_detail matter because they stop invalid sales data (a zero/negative quantity, or a negative price from a data-entry error) from ever being persisted, catching a whole class of bad input at the database layer rather than relying on every application/reporting query to filter it out after the fact.
                     


     







Section 1 — Entities & Business Rules
Entities ModeledThis covers all six required areas (transactions, line items, products, category/type, staff, locations), split as seven physical tables since category and type are kept separate for proper normalization.
Business Rules
Each sales transaction is processed by exactly one staff member, at exactly one location.Each transaction has one or more line items (sales_detail rows); every line item belongs to exactly one transaction.
Each line item references exactly one product; a product may appear on many line items across many transactions.Each product belongs to exactly one product type, and each product type belongs to exactly one category (no product is left uncategorized).
Each staff member is assigned to exactly one home location; a location may have many staff members.
Quantity and unit price on a line item must be positive values, and a transaction's total amount must be non-negative — invalid/negative sales data is rejected at the database level.



Section 2 — Normalized Logical Schema (3NF)
`location`| Column | Type | Constraint ||---|---|---|| `location_id` | INT | **PK** || `location_name` | VARCHAR(100) | NOT NULL || `address` | VARCHAR(150) | NOT NULL || `city` | VARCHAR(50) | NOT NULL || `state` | VARCHAR(20) | NOT NULL |
 `staff`| Column | Type | Constraint ||---|---|---|| `staff_id` | INT | **PK** || `staff_name` | VARCHAR(100) | NOT NULL || `position` | VARCHAR(50) | || `location_id` | INT | **FK** → `location.location_id`, NOT NULL |### `product_category`| Column | Type | Constraint ||---|---|---|| `category_id` | INT | **PK** || `category_name` | VARCHAR(50) | NOT NULL, UNIQUE |
 `product_type`| Column | Type | Constraint ||---|---|---|| `type_id` | INT | **PK** || `type_name` | VARCHAR(50) | NOT NULL || `category_id` | INT | **FK** → `product_category.category_id`, NOT NULL |### `product`| Column | Type | Constraint ||---|---|---|| `product_id` | INT | **PK** || `product` | VARCHAR(100) | NOT NULL || `description` | TEXT | || `price` | DECIMAL(10,2) | NOT NULL, CHECK (price >= 0) || `type_id` | INT | **FK** → `product_type.type_id`, NOT NULL |
 `sales_transaction`| Column | Type | Constraint ||---|---|---|| `transaction_id` | INT | **PK** || `transaction_timestamp` | TIMESTAMP | NOT NULL || `staff_id` | INT | **FK** → `staff.staff_id`, NOT NULL || `location_id` | INT | **FK** → `location.location_id`, NOT NULL || `payment_method` | VARCHAR(20) | NOT NULL, CHECK (payment_method IN ('cash','credit','debit','mobile')) || `total_amount` | DECIMAL(10,2) | NOT NULL, CHECK (total_amount >= 0) |
`sales_detail`| Column | Type | Constraint ||---|---|---|| `sales_detail_id` | INT | **PK** || `transaction_id` | INT | **FK** → `sales_transaction.transaction_id`, NOT NULL || `product_id` | INT | **FK** → `product.product_id`, NOT NULL || `line_number` | INT | NOT NULL || `quantity` | INT | NOT NULL, CHECK (quantity > 0) || `unit_price` | DECIMAL(10,2) | NOT NULL, CHECK (unit_price >= 0) || | | UNIQUE (`transaction_id`, `line_number`) |



Section 3 — Relationship Definitions
sales_detail  - sales_transaction: One-to-many. One sales_transaction has one or more sales_detail rows. The FK lives on the many side: sales_detail.transaction_id references sales_transaction.transaction_id. NOT NULL on this FK guarantees no orphan line items; guaranteeing "at least one" line item per transaction is a rule enforced at the application/insert-transaction level, since standard FK constraints can't require a minimum child-row count.
sales_detail - product: Many-to-one. Many line items across many transactions can reference the same product. FK: sales_detail.product_id -> product.product_id. unit_price is stored on sales_detail (not just looked up from product.price) intentionally, to preserve the historical price at time of sale even if the product's list price later changes.- 
product - product_type (and product_type - product_category): Many-to-one at each level. Many products share one type; many types share one category. FKs: product.type_id -> product_type.type_id, and product_type.category_id -> product_category.category_id. This is a two-level normalized hierarchy rather than storing category/type text directly on product.
staff - location is many-to-one: many staff share one home location. 



Section 4 SQL Implementation
CREATE TABLE location (    location_id   INT PRIMARY KEY,    location_name VARCHAR(100) NOT NULL,    address       VARCHAR(150) NOT NULL,    city          VARCHAR(50) NOT NULL,    state         VARCHAR(20) NOT NULL);CREATE TABLE staff (    staff_id    INT PRIMARY KEY,    staff_name  VARCHAR(100) NOT NULL,    position    VARCHAR(50),    location_id INT NOT NULL REFERENCES location(location_id));CREATE TABLE product_category (    category_id   INT PRIMARY KEY,    category_name VARCHAR(50) NOT NULL UNIQUE);
CREATE TABLE product_type (    type_id     INT PRIMARY KEY,    type_name   VARCHAR(50) NOT NULL,    category_id INT NOT NULL REFERENCES product_category(category_id));CREATE TABLE product (    product_id  INT PRIMARY KEY,    product     VARCHAR(100) NOT NULL,    description TEXT,    price       DECIMAL(10,2) NOT NULL CHECK (price >= 0),    type_id     INT NOT NULL REFERENCES product_type(type_id));
CREATE TABLE sales_transaction (    transaction_id         INT PRIMARY KEY,    transaction_timestamp  TIMESTAMP NOT NULL,    staff_id               INT NOT NULL REFERENCES staff(staff_id),    location_id            INT NOT NULL REFERENCES location(location_id),    payment_method         VARCHAR(20) NOT NULL        CHECK (payment_method IN ('cash','credit','debit','mobile')),    total_amount           DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0));
CREATE TABLE sales_detail (    sales_detail_id INT PRIMARY KEY,    transaction_id  INT NOT NULL REFERENCES sales_transaction(transaction_id),    product_id      INT NOT NULL REFERENCES product(product_id),    line_number     INT NOT NULL,    quantity        INT NOT NULL CHECK (quantity > 0),    unit_price      DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),    UNIQUE (transaction_id, line_number));
CREATE VIEW staff_locations_view ASSELECT    s.staff_id,    s.staff_name,    l.location_name,    l.address,    l.city,    l.stateFROM staff sJOIN location l ON s.location_id = l.location_id;
CREATE MATERIALIZED VIEW product_info_mview ASSELECT    p.product_id,    p.product AS product_name,    pc.category_name,    pt.type_name,    p.priceFROM product pJOIN product_type pt ON p.type_id = pt.type_idJOIN product_category pc ON pt.category_id = pc.category_id;


 Explanation- Normalization choice: splitting product_category and product_type into their own tables, rather than storing category/type as free-text columns on product, eliminates update errors. 
Integrity constraint: the CHECK (quantity > 0) and CHECK (unit_price >= 0) constraints on sales_detail matter because they stop invalid sales data.       



