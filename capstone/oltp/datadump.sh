#! /bin/sh

if mysqldump --user=root sales sales_data > sales_data.sql
then
    echo "Success create dump.";
else
    echo "Something went wrong. Dump not created";
fi