#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

# Check if POSTGRES_USER is set; if not, set a default value
# if [ -z "${POSTGRES_USER:-}" ]; then
#     base_postgres_image_default_user='postgres'
#     export POSTGRES_USER="${base_postgres_image_default_user}"
# fi

# # Correctly format the DATABASE_URL
# export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"

python << END
import sys
import time
import psycopg

MAX_WAIT_SECOND=30
RETRY_INTERVAL=5
start = time.time()

def check_database():
    try:
        psycopg.connect(
            dbname="${POSTGRES_DB}",
            user="${POSTGRES_USER}",
            password="${POSTGRES_PASSWORD}",
            host="${POSTGRES_HOST}",
            port="${POSTGRES_PORT}",
        )
        return True
    except psycopg2.OperationalError as error:
        elapsed = int(time.time() - start_time())
        sys.stderr.write("Database connection attempt failed after {elapsed} second:{error}\n")  
        return False



while True:
    if check_database():
        break
    if time.time() - start_time > MAX_WAIT_SECOND:
        sys.stderr.write("Error: Database connection could not to be established after 30 second \n")  
        sys.exit(1)
    sys.stderr.write(f"Waiting {RETRY_INTERVAL} second before retrying...\n")
    time.sleep(RETRY_INTERVAL)
    
END


>&2 echo "PostgreSQL is available to accept connection"

exec "$@"