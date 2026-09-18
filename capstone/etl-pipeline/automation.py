# Import libraries required for connecting to mysql

# Import libraries required for connecting to DB2 or PostgreSql

# Connect to MySQL
import mysql.connector

# connect to database
# You can get the Hostname and Password from the connection information section of Mysql 
connection = mysql.connector.connect(user='root', password='',host='localhost',database='sales')

# create cursor




# Connect to DB2 or PostgreSql
import psycopg2



# psql -d postgres -c "CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD '123';"
# connectction details

dsn_hostname = 'localhost'
dsn_user='postgres'        # e.g. "abc12345"
dsn_pwd ='123'      # e.g. "7dBZ3wWt9XN6$o0J"
dsn_port ="5432"                # e.g. "50000" 
dsn_database ="sales"           # i.e. "BLUDB"


# create connection

conn = psycopg2.connect(
   database=dsn_database, 
   user=dsn_user,
   password=dsn_pwd,
   host=dsn_hostname, 
   port= dsn_port
)

#Crreate a cursor onject using cursor() method




# Find out the last rowid from DB2 data warehouse or PostgreSql data warehouse
# The function get_last_rowid must return the last rowid of the table sales_data on the IBM DB2 database or PostgreSql.

def get_last_rowid():
    SQL = "SELECT MAX(rowid) FROM sales_data"
    cursor = conn.cursor()
    cursor.execute(SQL)
    res = cursor.fetchone()
    print(res)
    
    return int(res[0])


last_row_id = get_last_rowid()
print("Last row id on production datawarehouse = ", last_row_id)

# List out all records in MySQL database with rowid greater than the one on the Data warehouse
# The function get_latest_records must return a list of all records that have a rowid greater than the last_row_id in the sales_data table in the sales database on the MySQL staging data warehouse.

def get_latest_records(rowid):
    SQL = "SELECT * FROM sales_data WHERE rowid > %s"
    cursor = connection.cursor()

    cursor.execute(SQL, [rowid])
    new_records = cursor.fetchall()
    return new_records

new_records = get_latest_records(last_row_id)

print("New rows on staging datawarehouse = ", len(new_records))

# Insert the additional records from MySQL into DB2 or PostgreSql data warehouse.
# The function insert_records must insert all the records passed to it into the sales_data table in IBM DB2 database or PostgreSql.

def insert_records(records):
    SQL = "INSERT INTO sales_data (rowid, product_id, customer_id, quantity) VALUES (%s, %s, %s, %s);"
    cursor = conn.cursor()

    for rec in records:
        cursor.execute(SQL, rec)

    conn.commit()

insert_records(new_records)
print("New rows inserted into production datawarehouse = ", len(new_records))

# disconnect from mysql warehouse
connection.close()

# disconnect from PostgreSQL data warehouse
conn.close()

# End of program