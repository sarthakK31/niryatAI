#!/bin/bash

# Container and DB config
CONTAINER_NAME=niryat-db   # change if different
DB_NAME=testdb                    # change if needed
DB_USER=postgres

CONTAINER_FILE=/tmp/hs_codes.csv
HOST_FILE=./hs_codes.csv

echo "Exporting HS codes from PostgreSQL..."

docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME <<'SQL'
COPY (
    SELECT hs_code
    FROM hs_code_reference
) TO '/tmp/hs_codes.csv' CSV HEADER;
SQL

echo "Copying file from container to host..."

docker cp $CONTAINER_NAME:$CONTAINER_FILE $HOST_FILE

echo "Verifying export..."

cat $HOST_FILE

echo "Done."