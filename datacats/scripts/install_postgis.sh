#!/bin/bash

set -e

export PGHOST=db
export PGDATABASE=ckan
export PGUSER=postgres
export PGPASSWORD=${DB_ENV_POSTGRES_PASSWORD}

psql -c 'SELECT * FROM geometry_columns LIMIT 1;' 2> /dev/null && exit 0

psql -f /usr/share/postgresql/9.3/contrib/postgis-2.1/postgis.sql
psql -f /usr/share/postgresql/9.3/contrib/postgis-2.1/spatial_ref_sys.sql
psql -c 'ALTER VIEW geometry_columns OWNER TO ckan;'
psql -c 'ALTER TABLE spatial_ref_sys OWNER TO ckan;'
