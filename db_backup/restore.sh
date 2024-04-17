#!/bin/bash
BACKUP_DIR="db_backup"  # Update this with the path outside the containers

# Find the most recent backup file
LATEST_BACKUP=$(ls -t ${BACKUP_DIR}/db_backup_*.sql | head -n 1)


echo "Restoring database from ${LATEST_BACKUP}"


# # Restoring the database into the db container
docker exec -i iac_xbs-db-1 /bin/bash -c "PGPASSWORD=binaries psql --username iac_xbs xbdb" <  "$LATEST_BACKUP"

