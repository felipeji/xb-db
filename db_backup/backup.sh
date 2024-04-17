#!/bin/bash

# Backup PostgreSQL database

# Tables to backup in the database
# data_ingestion_object
# data_ingestion_spect



# Timestamp for file uniqueness
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
BACKUP_DIR="db_backup"  # Update this with the path outside the containers

# Ensure backup directory exists
mkdir -p ${BACKUP_DIR}

# Dump the database
docker exec -i iac_xbs-db-1 /bin/bash -c "PGPASSWORD=binarias pg_dump --username iac_xbs xbdb" > ${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql
